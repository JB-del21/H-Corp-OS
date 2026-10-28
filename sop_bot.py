"""Közös SOP-bot réteg: a Slack gateway és a tesztek ugyanezt a kódot használják."""
import os
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).parent
PROMPT_PATH = ROOT / "prompts" / "system_prompt_sop_bot.txt"
KNOWLEDGE_PATH = ROOT / "knowledge" / "sop_knowledge_base.md"
# Rögzített (dátumozott) modellverzió: az alias ("gpt-4o") észrevétlenül változhat.
# FIGYELEM: az OpenAI bejelentése szerint ez a snapshot 2027-01-14-én kikerül az API-ból,
# addig át kell állni az utódra (a promptfooconfig.yaml provider-ét is át kell írni),
# és a teljes tesztkészletet le kell futtatni.
MODEL = os.environ.get("SOP_BOT_MODEL", "gpt-4o-2024-08-06")

FALLBACK = (
    "Sajnos erről a folyamatról nincs érvényes hivatalos SOP a tudásbázisunkban. "
    "Kérlek, keresd a terület felelősét!"
)


def build_messages(user_prompt: str) -> list[dict]:
    """System prompt + tudásbázis kontextus + felhasználói kérdés."""
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    knowledge = KNOWLEDGE_PATH.read_text(encoding="utf-8")
    system = f"{system_prompt}\n\n# KONTEXTUS (hivatalos SOP dokumentumok)\n{knowledge}"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_prompt},
    ]


def query_sop_bot(user_prompt: str) -> str:
    client = OpenAI(timeout=20, max_retries=2)  # OPENAI_API_KEY környezeti változóból
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.0,
        messages=build_messages(user_prompt),
    )
    return response.choices[0].message.content or ""
