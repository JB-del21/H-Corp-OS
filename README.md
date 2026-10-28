# H-CORP AI Engine: LLMOps immunrendszer

Teszt nélkül nincs bizalom. Pipeline nélkül nincs rendszer.

Belső SOP-bot (Slack), amelyhez automatizált biztonsági és regressziós tesztelés tartozik. A vezetői háttér: [docs/vezetoi-kezikonyv.md](docs/vezetoi-kezikonyv.md).

## Szerkezet

| Útvonal | Szerep |
|---|---|
| `prompts/` | A botok system promptjai (`sop_bot`, `onboard`, `it_helpdesk`, `hr_admin`) |
| `prompts/sop_bot_chat.json` | Chat sablon a promptfoo-hoz (system + kontextus + kérdés) |
| `knowledge/sop_knowledge_base.md` | SOP tudásbázis. **Minta**, élesben a cég valódi SOP-jaira cserélendő |
| `sop_bot.py` | Közös bot-réteg, ezt használja a gateway és a tesztek is |
| `main.py` | Slack gateway (FastAPI) |
| `promptfooconfig.yaml` | Deklaratív tesztek (`icontains`, `not-regex`, `llm-rubric`) |
| `tests/` | `test_gateway.py` (kulcs nélkül fut), `test_ai_guardrails.py` (valódi modell, kulcs kell) |
| `.github/workflows/ai-tests.yml` | CI: push, PR, napi ütemezés |

## Beállítás

1. Cseréld ki a `[CÉGNÉV]` és egyéb `[PLACEHOLDER]` értékeket a `prompts/` mappában.
2. Cseréld le a `knowledge/sop_knowledge_base.md` mintatartalmát a valódi SOP-kra.
3. GitHub → Settings → Secrets and variables → Actions → `OPENAI_API_KEY`.
   Kulcs nélkül a gateway tesztek lefutnak, az LLM tesztek kimaradnak, és a CI figyelmeztetést ír.
4. A Slack-hez szükséges `SLACK_SIGNING_SECRET` és `SLACK_BOT_TOKEN` **futtatási környezeti változó** a szerveren (lásd `.env.example`), a CI-nak nem kell.

## Futtatás helyben

```bash
pip install -r requirements.txt
pytest tests/test_gateway.py                 # kulcs nélkül
export OPENAI_API_KEY=...
pytest                                       # minden teszt
npx promptfoo@0.125.1 eval -c promptfooconfig.yaml -o output.html

export SLACK_SIGNING_SECRET=... SLACK_BOT_TOKEN=...
uvicorn main:app --host 0.0.0.0 --port 8000
```

Slack Request URL: `https://<a-te-domained>/slack/events`

## Ütemezés

A napi futás `0 7 * * *` UTC-kor indul, ez téli időben 8:00, nyári időben 9:00 magyar idő. Nyárra `0 6 * * *`-ra kell átírni. A GitHub ütemezett futásai terhelés miatt késhetnek is.

## Mit nem garantál

A `temperature: 0` csökkenti a válaszok szórását, de nem garantálja az azonos kimenetet. A tesztek ezért **mintavételes védelmet** adnak: egy zöld futás azt jelenti, hogy a tesztelt esetek átmentek, nem azt, hogy a bot soha nem hibázik. A tesztkészletet (jelenleg 8 eset) bővíteni kell a kézikönyvben célzott 50+ kérdésig.
