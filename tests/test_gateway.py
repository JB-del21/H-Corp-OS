"""Kulcs nélkül futó tesztek a Slack gateway-re (aláírás, mention-tisztítás, challenge)."""
import hashlib
import hmac
import json
import os
import time

os.environ["SLACK_SIGNING_SECRET"] = "test-secret"
os.environ["SLACK_BOT_TOKEN"] = "xoxb-test"

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402

client = TestClient(main.app)


def signed_headers(body: bytes, ts: int | None = None, secret: str = "test-secret") -> dict:
    ts = str(ts if ts is not None else int(time.time()))
    base = b"v0:" + ts.encode() + b":" + body
    sig = "v0=" + hmac.new(secret.encode(), base, hashlib.sha256).hexdigest()
    return {"X-Slack-Signature": sig, "X-Slack-Request-Timestamp": ts, "Content-Type": "application/json"}


def test_clean_mention():
    assert main.clean_mention("<@U123ABC> Mi a teendő?") == "Mi a teendő?"
    assert main.clean_mention("Szia <@U123ABC>, kérdés") == "Szia , kérdés"


def test_rejects_missing_signature():
    r = client.post("/slack/events", content=b"{}")
    assert r.status_code == 403


def test_rejects_wrong_secret():
    body = b"{}"
    r = client.post("/slack/events", content=body, headers=signed_headers(body, secret="rossz"))
    assert r.status_code == 403


def test_rejects_old_timestamp():
    body = b"{}"
    r = client.post("/slack/events", content=body, headers=signed_headers(body, ts=int(time.time()) - 3600))
    assert r.status_code == 403


def test_url_verification_challenge():
    body = json.dumps({"challenge": "abc123"}).encode()
    r = client.post("/slack/events", content=body, headers=signed_headers(body))
    assert r.status_code == 200
    assert r.json() == {"challenge": "abc123"}


def test_app_mention_schedules_answer(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "answer_in_slack", lambda channel, q: calls.append((channel, q)))
    body = json.dumps(
        {"event": {"type": "app_mention", "channel": "C1", "text": "<@UBOT> Mi a teendő?"}}
    ).encode()
    r = client.post("/slack/events", content=body, headers=signed_headers(body))
    assert r.status_code == 200
    assert calls == [("C1", "Mi a teendő?")]


def test_bot_messages_are_ignored(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "answer_in_slack", lambda channel, q: calls.append((channel, q)))
    body = json.dumps(
        {"event": {"type": "app_mention", "channel": "C1", "text": "<@UBOT> hello", "bot_id": "B1"}}
    ).encode()
    client.post("/slack/events", content=body, headers=signed_headers(body))
    assert calls == []
