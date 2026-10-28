import hashlib
import hmac
import logging
import os
import re
import time

import requests
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request

from sop_bot import FALLBACK, query_sop_bot

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("gateway")

app = FastAPI(title="H-CORP Slack RAG Gateway")

# Nincs alapértelmezett érték: titok nélkül a szolgáltatás nem indulhat el
# (egy ismert alapértelmezett aláíró kulccsal bárki hamisíthatna kéréseket).
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

MENTION_RE = re.compile(r"<@[A-Z0-9]+>")

# Slack event_id deduplikálás (memóriában, egy folyamaton belül).
# Több worker / több példány esetén megosztott tár (pl. Redis) kell; a Dockerfile 1 workert indít.
DEDUPE_TTL_SECONDS = 600
_seen_events: dict[str, float] = {}


def already_seen(event_id: str | None) -> bool:
    """True, ha ezt az eseményt már feldolgoztuk. Közben a lejárt bejegyzéseket törli."""
    now = time.time()
    for key in [k for k, t in _seen_events.items() if now - t > DEDUPE_TTL_SECONDS]:
        del _seen_events[key]
    if not event_id:
        return False
    if event_id in _seen_events:
        return True
    _seen_events[event_id] = now
    return False


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


def extract_question(event: dict) -> str | None:
    """A kérdés szövege, ha az eseményre válaszolni kell; különben None.

    - csatornában: @megemlítés (app_mention)
    - privát üzenetben: message esemény im csatornatípussal (message.im)
    A bot saját és más botok üzeneteit, valamint a módosított/törölt/speciális
    (subtype-os) üzeneteket figyelmen kívül hagyjuk, hogy ne legyen önmagára válaszoló hurok.
    """
    if event.get("bot_id") or event.get("subtype"):
        return None
    etype = event.get("type")
    if etype == "app_mention":
        question = clean_mention(event.get("text", ""))
    elif etype == "message" and event.get("channel_type") == "im":
        question = event.get("text", "").strip()
    else:
        return None
    return question or None


def answer_in_slack(channel: str, question: str) -> None:
    started = time.time()
    failed = False
    try:
        resp = query_sop_bot(question)
    except Exception:
        log.exception("LLM hívás sikertelen")
        resp = FALLBACK
        failed = True
    try:
        requests.post(
            "https://slack.com/api/chat.postMessage",
            json={"channel": channel, "text": resp},
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
            timeout=10,
        ).raise_for_status()
    except requests.RequestException:
        log.exception("Slack üzenet küldése sikertelen")
    # Szándékosan nem naplózzuk a kérdés/válasz szövegét (személyes adat lehet benne).
    log.info(
        "answered channel=%s q_len=%d a_len=%d llm_failed=%s fallback=%s ms=%d",
        channel, len(question), len(resp), failed, resp.strip() == FALLBACK, int((time.time() - started) * 1000),
    )


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


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
    if already_seen(data.get("event_id")):
        return {"status": "ok"}
    event = data.get("event", {})
    question = extract_question(event)
    if question:
        background.add_task(answer_in_slack, event.get("channel"), question)
    return {"status": "ok"}
