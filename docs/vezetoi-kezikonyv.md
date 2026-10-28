# H-CORP VEZETŐI KÉZIKÖNYV
## A vállalkozói elengedéstől az AI LLMOps immunrendszeréig

---

### Bevezetés: A Vállalkozás mint Rendszer és Önismereti Eszköz

A modern cégépítés nem a mikromenedzsmentről, a végtelen tűzoltásról vagy a zárt ajtók mögött csiszolt üzleti tervekről szól. Balogh Petya gondolatiságát és a H-CORP determinisztikus mérnöki logikáját ötvözve a vállalkozás egy radikális felismeréssel kezdődik: **a kudarc nem kivétel, hanem a szándékos edzésterv.**

Ez a kézikönyv összefoglalja azt az ötlépcsős architekturális utat, amelyen keresztül egy egyszemélyes hősködésből épülő, törékeny vállalkozás átalakul egy önmagát fegyelmező, skálázható és AI-alapú immunrendszerrel védekező szervezetté.

---

### I. Fejezet: A Vezetői Identitás Válsága és az Elengedés Törvénye

#### 1. A kudarc mint edzésterv
A kezdő vállalkozó legnagyobb tévképzése, hogy elvárja az élettől a sima utat. A valóságban a piac folyamatos terhelést (stressz-tesztet) mér ránk. 
* **A kudarc átmeneti:** Aki a padlón marad, abból nem lesz cégvezető. Aki felporolja magát, az tudatosan edzi magát a következő iterációra.
* **A tőke illúziója:** Ha egy termék nem működik tőke nélkül, pénzzel sem fog. A gyors piacra lépés és a valóság-validáció mindent felülír.

#### 2. A cégvezető mint szűk keresztmetszet
Amíg a cég minden döntése, számlája és ügyféligénye rajtad áramlik keresztül, addig nem cégvezető vagy, hanem egy túlhajszolt alkalmazott a saját vállalkozásodban.
* **A valódi KPI:** A vezető elsődleges mérőszáma az, hogy **mennyire tudja magát feleslegessé tenni** az operatív munkában. Te vagy a jégtörő hajó: feltérképezed az ismeretlent, majd delegálsz.
* **Az identitás védelme:** Ha a cég eladásakor vagy egy válságban megszűnsz létezni, mert a cég te magad vagy, akkor az egész építmény összedől. Új célok, új bakancslista kell.

---

### II. Fejezet: A Delegálás Mérnöki Protokollja

A delegálás nem hitkérdés és nem is érzelmi döntés, hanem egy ötlépcsős determinisztikus folyamat:

1. **A fekete doboz dokumentálása:** Írd le lépésről lépésre, hogyan hajtod végre a feladatot. Ha nem írható le SOP-ként, még nem érett az átadásra.
2. **Árnyékolási fázis („Én csinálom, te nézed”):** Hangosan kimondott belső monológ mellett végzed el a feladatot, átadva a kontextust és a mintafelismerést.
3. **Fordított árnyékolás („Te csinálod, én figyelek”):** A kolléga ül a székben; te csak vészhelyzetben avatkozol közbe, hogy a logikát teszteld.
4. **Felügyelt autonómia:** A napi önálló munkavégzés utáni utólagos, szúrópróbaszerű kalibrálás.
5. **Teljes Ownership:** A feladat végleg elszakad a személyedtől; bekerül a cég SOP-rendszerébe.

---

### III. Fejezet: Az SOP mint a Vállalkozás Operációs Rendszere

A tudás nem maradhat a vezető fejében. A szervezet alapköve az élő, faék egyszerűségű ellenőrzőlistákra épülő SOP (Standard Operating Procedure).

* **A 4 részes sablon:** Cél és előfeltételek $\rightarrow$ Lépésről lépésre checklist $\rightarrow$ Döntési elágazások (Ha-Akkor logika) $\rightarrow$ Hibaelhárítás.
* **A Tudásbázis hierarchiája:** A strukturált mapparendszertől (Notion / Wiki) a szigorú elnevezési konvenciókig (`SOP-OPS-012`), ahol minden dokumentumnak van felelőse és frissítési naplója (Changelog).

---

### IV. Fejezet: A RAG Alapú Céges Idegrendszer (AI Botok)

Hogy a kollégáknak ne kelljen mappákban keresgélniük, a tudásbázisra épített **RAG (Retrieval-Augmented Generation)** architektúra felelős. Egy belső Slack vagy Teams csatornán elhelyezett AI-asszisztens természetes nyelven, kizárólag a hivatalos SOP-kból ad ki választ.

* **Szerep-alapú megosztás (RBAC):** Külön bot felel az operációért (`SOP-Bot`), az új belépők támogatásáért (`Onboard-Bot`) és a technikai hibaelhárításért (`IT-Fixer`).
* **Zéró halucináció:** A System Prompt szigorúan tiltja a külső piaci tudás használatát; ha valami nincs a dokumentumokban, kötelező fallback választ adni és a terület felelőséhez irányítani.

---

### V. Fejezet: Az LLMOps mint a Szervezet Immunrendszere

Egy belső AI botot nem szabad "bemondásra" használni. SOP frissítés után a modell haluzálhat vagy érzékeny adatot (PII) szivárogtathat ki. Ezért kötelező a CI/CD pipeline alapú tesztelés.

1. **Test Dataset (50+ kérdés):** Red-Teaming (jailbreak, PII-lopás, rosszindulatú kérések) és napi rutin tesztek kombinációja.
2. **Assertions ($temperature: 0.0$):** 
   * Deklaratív (`icontains`, `not-icontains`) és LLM-rubric (AI bíró általi biztonsági értékelés) szabályok.
   * Imperatív Python/Regex szűrők (pl. `\d{6,}` tiltása, hogy ne szivárogjon ki bérsáv vagy jelszó).
3. **Automated CI/CD Immune Pipeline (GitHub Actions):** 
   * Nemcsak push és PR alkalmával fut le, hanem **minden reggel 8:00-kor**, biztosítva, hogy a reggeli órákra ne ébredjen a cég egy elavult SOP miatt haluzáló bottal.

---

### Konklúzió

A vállalkozás végül egy önmagát tökéletesítő ökoszisztémává áll össze:
> **Delegálás** (emberi szint) $\rightarrow$ **SOP** (folyamat szint) $\rightarrow$ **Tudásbázis** (memória szint) $\rightarrow$ **RAG Bot** (kommunikációs szint) $\rightarrow$ **LLMOps Pipeline** (biztonsági immunrendszer).

Ha ez a lánc zárt, a cég nélküled is pontosabban teker, a vezető pedig megkapja a legfőbb ajándékot: a szabadságot és a rendszerszintű békét.