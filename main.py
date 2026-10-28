import hashlib
import hmac
import os
import re
import time

import requests
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request

from sop_bot import FALLBACK, query_sop_bot

app = FastAPI(title="H-CORP Slack RAG Gateway")

# Nincs alapértelmezett érték: titok nélkül a szolgáltatás nem indulhat el
# (egy ismert alapértelmezett aláíró kulccsal bárki hamisíthatna kéréseket).
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

MENTION_RE = re.compile(r"<@[A-Z0-9]+>")


def verify_slack_signature(request: Request, body: bytes) -> bool:
    sig = request.headers.get("X-Slack-Signature", "")
    ts = request.headers.get("X-Slack-Request-Timestamp", "")
    try:
        if abs(time.time() - int(ts)) > 300:
            return False
    except ValueError:
        return False
    base = b"v0:" + ts.encode() + b":" + body
    my_sig = "v0=" + hmac.new(SLACK_SIGNING_SECRET.encode(), base, hashlib.sha256).hexdigest()
    return hmac.compare_digest(my_sig, sig)


def clean_mention(text: str) -> str:
    return MENTION_RE.sub("", text).strip()


def answer_in_slack(channel: str, question: str) -> None:
    try:
        resp = query_sop_bot(question)
    except Exception:
        resp = FALLBACK
    requests.post(
        "https://slack.com/api/chat.postMessage",
        json={"channel": channel, "text": resp},
        headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
        timeout=10,
    )


@app.post("/slack/events")
async def slack_events(request: Request, background: BackgroundTasks):
    body = await request.body()
    if not verify_slack_signature(request, body):
        raise HTTPException(status_code=403, detail="Invalid signature")
    # Slack újrapróbálkozásait nem dolgozzuk fel újra (az LLM-hívás lassabb lehet 3 mp-nél).
    if request.headers.get("X-Slack-Retry-Num"):
        return {"status": "ok"}
    data = await request.json()
    if "challenge" in data:
        return {"challenge": data["challenge"]}
    event = data.get("event", {})
    if event.get("type") == "app_mention" and not event.get("bot_id"):
        question = clean_mention(event.get("text", ""))
        if question:
            background.add_task(answer_in_slack, event.get("channel"), question)
    return {"status": "ok"}
