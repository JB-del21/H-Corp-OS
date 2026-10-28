# Ügyfél-bevezetési checklist (SOP-bot, Slack)

Egy ügyfél = egy külön példány: saját Slack-app, saját OpenAI Project és kulcs, saját tudásbázis, saját szerver/konténer.

## 0. Szerződés és adatvédelem
- [ ] Szolgáltatási szerződés és SLA aláírva (hatókör, reakcióidő, díj).
- [ ] Adatfeldolgozói megállapodás az ügyféllel (milyen adatok kerülnek a tudásbázisba, ki a kezelő, ki a feldolgozó).
- [ ] Döntés: kerülhet-e személyes adat a SOP-kba? Ha igen, előbb anonimizálni kell, vagy ki kell hagyni.
- [ ] Az ügyfél tudja, hogy a kérdések és a SOP-kontextus külső modellszolgáltatóhoz (OpenAI) kerülnek.

## 1. SOP-anyag (az ügyféltől)
- [ ] 10-20 kulcsfolyamat SOP-ja a 4 részes sablonban (cél, lépések, döntési elágazás, hibaelhárítás).
- [ ] Minden SOP-nak van kódja (pl. `SOP-UGYF-003`), címe, verziója és felelőse.
- [ ] Az anyag bekerült a `knowledge/sop_knowledge_base.md`-be a minta helyére (a fejléc formátuma: `## KÓD: Cím vX.Y`).
- [ ] `[CÉGNÉV]` és az összes `[PLACEHOLDER]` kitöltve a `prompts/` mappában (pl. `[JELSZO_SELFSERVICE_LINK]`).
- [ ] Az ügyfél jóváhagyta, hogy a SOP-k aktuálisak (kinek a felelőssége a frissítés?).

## 2. OpenAI
- [ ] Külön Project az ügyfélnek, saját API-kulccsal és költségplafonnal.
- [ ] Ha az ügyfél kéri: EU-s adatrezidencia. Ez csak új Projectnél választható, és jogosult ügyfeleknek érhető el, ezt előre ellenőrizni kell.
- [ ] Modellverzió ellenőrizve (lásd README: a jelenlegi snapshot 2027-01-14-én kivezetésre kerül).

## 3. Slack-app (a workspace adminjával)
A kód jelenleg csak a csatornás @megemlítésre (`app_mention`) válaszol, privát üzenetre nem.
- [ ] Új app létrehozása a Slack API felületén (api.slack.com/apps) az ügyfél workspace-ében.
- [ ] Bot Token Scopes (OAuth & Permissions): `app_mentions:read` és `chat:write`. (A kód viselkedéséből következő minimum, ellenőrizd a Slack aktuális dokumentációjában.)
- [ ] Az app telepítése a workspace-be. A kapott `xoxb-` kezdetű **Bot User OAuth Token** lesz a `SLACK_BOT_TOKEN`.
- [ ] A **Signing Secret** (Basic Information → App Credentials) lesz a `SLACK_SIGNING_SECRET`.
- [ ] Event Subscriptions bekapcsolása, Request URL: `https://<ügyfél-domain>/slack/events`. A Slack ekkor `challenge` kérést küld, ehhez a szervernek már futnia kell (lásd 4. pont).
- [ ] Feliratkozás a bot eseményre: `app_mention`. Mentés után az app újratelepítése, ha a Slack kéri.
- [ ] A bot meghívása a használni kívánt csatornákba (`/invite @botnév`), különben nem látja a megemlítéseket.

## 4. Szerver
- [ ] EU-s szerver (VPS vagy felhő), nyilvános HTTPS végponttal és érvényes tanúsítvánnyal (reverse proxy).
- [ ] `.env` kitöltve (`OPENAI_API_KEY`, `SLACK_SIGNING_SECRET`, `SLACK_BOT_TOKEN`), nincs verziókezelésben.
- [ ] `docker compose up -d --build`, majd `curl https://<ügyfél-domain>/healthz` válasza `{"status":"ok"}`.
- [ ] Egyetlen példány fut (a deduplikálás memóriában él).
- [ ] Automatikus újraindítás és külső elérhetőség-figyelés beállítva.

## 5. Átvételi tesztek
- [ ] A repo CI-ban az ügyfél SOP-jaira írt 50+ magyar tesztkérdés zöld (folyamat-kérdések, hiányzó SOP, béradat, jelszó, jailbreak).
- [ ] Élő próba a Slackben: 10 valódi kérdés az ügyfél munkatársaitól, a válaszok SOP-kóddal jönnek, hiányzó SOP-nál a fix fallback-mondat.
- [ ] Ellenőrizve: a bot nem ad ki bért, jelszót, személyes adatot, és nem enged szabálymódosítást.
- [ ] Az ügyfél írásban átvette az eredményt.

## 6. Élesítés
- [ ] Rövid belső tájékoztató a munkatársaknak: mire jó a bot, mire nem, hogyan kell kérdezni, kinek jelezzék a hibát.
- [ ] Felelős kijelölve a SOP-frissítésre. Minden SOP-változás után a tesztek újrafuttatása a CI-ban.
- [ ] Napi ütemezett teszt aktív (lásd a workflow cron-ját, nyári időszámításra átírva).

## 7. Üzemeltetés
- [ ] Havi riport: kérdésszám, fallback-arány, hibák, tesztek eredménye.
- [ ] Negyedéves felülvizsgálat: SOP-k frissessége, új tesztesetek a valós kérdésekből.
- [ ] Modellváltás vagy kivezetés előtt teljes tesztfutás, csak zölden éles.
- [ ] Incidens esetén: kulcsok és tokenek cseréje, napló átnézése, ügyfél értesítése a szerződés szerint.
