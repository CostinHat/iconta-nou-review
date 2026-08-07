# E1E12_GASITE.md — parcurgere cap-coadă (PLAN_B) ca un contabil real

> Registru al parcurgerii E1–E12. **NU se repară aici** — doar se consemnează.
> Stări: **DEFECT** | **SUSPICIUNE** | **INFIRMAT-OK** | **DESCHIS-cunoscut**.
> Un defect = divergență pe FLUX REAL, cu repro (declarație datorată lipsă / declarație greșită tăcută &
> depozabilă / blocaj tăcut sau prost plasat / izolare spartă / te obligă să ghicești).

---

## Sesiunea 07.08.2026 (tura 1) — firma F2 (micro + salariați + TVA trimestrial), E1→E11 via HTTP

**Mediu:** parcurgere ca client HTTP (FastAPI). **ATENȚIE metodologică (vezi DEFECT-1):** serverul de
producție `:8010` rulează cod STALE de 6 zile → parcurgerea validă s-a făcut pe un uvicorn PROASPĂT din HEAD,
pornit pe `:8011` (`venv/bin/uvicorn main:app --port 8011`). Rezultatele „OK/DEFECT" de mai jos sunt de pe `:8011`
(cod curent), cu excepția DEFECT-1 care e chiar despre `:8010`.

**Firmă de test:** F2 = micro, plătitor TVA, tip_decont trimestrial, cu salariați. Creată prin flux HTTP real
(register/login cabinet Prisma → POST /tenants → POST /vector). tenant_014, cui 97701002.

**SOLD:** 2 DEFECT (1 blocant pe flux real) · 3 INFIRMAT-OK · izolare + TVA + facturare OK · restul = vizual
(tura 2 headless).

---

### DEFECT-1 — [E-transversal / E6] Serverul de PRODUCȚIE rulează cod stale de 6 zile; D112 crapă 500 pe el. **BLOCANT pe flux real.**

**Clasă:** disciplină de deploy — procesul care servește utilizatorii ≠ HEAD. D112 e doar *instanța* găsită;
orice cod schimbat după 01.08 e neservit.

**Repro (server live):**
- `systemctl show iconta-nou` → MainPID 298512, `uvicorn main:app --port 8010`, pornit **Sat 2026-08-01 06:09:08**,
  nerestartat de atunci. nginx (`/etc/nginx/sites-available/iconta`) proxează TOT traficul → `127.0.0.1:8010`.
- HEAD la 07.08 = `b369ba3` — **45+ commituri** peste codul care rulează (corpus legislativ, model episod CM etc.).
- `POST /declaratii/d112/valideaza` pe `:8010` → **500 Internal Server Error**. Traceback (uvicorn.log):
  `core/salarizare.py:99 → c.Temei("CF", art="77", ..., nivel_sursa="MO", ...)` →
  `TypeError: Temei.__new__() got an unexpected keyword argument 'nivel_sursa'`.
  Cauza: `core/common.py` (clasa `Temei`) e în memoria procesului în forma DE DINAINTE ca `Temei` să capete
  parametrul `nivel_sursa`; `salarizare` se importă LAZY abia la primul D112 → crapă pe `common` stale.
- **Dovadă că e DOAR stale (nu defect în HEAD):** aceeași generare `d112.genereaza(conn,"tenant_014",2026,1)`
  într-un proces `venv/bin/python3` PROASPĂT = OK (xml 3576B); și pe uvicorn `:8011` din HEAD = OK (xml 2754B).
  `common.py` modificat 07.08 17:13 (commit 9b3e88f), la 6 zile după pornirea serverului.

**Ar fi prins-o suita existentă?** NU. `pytest` + `verificator_conformitate.py` rulează pe sursa de pe DISC,
niciodată pe procesul care rulează. `scripts/githooks/post-commit` (cablat 07.08) publică pe `origin/main` +
`backup` dar **NU restartează serviciul** și nu verifică „running == HEAD". Nu există gard care să compare
codul din memoria procesului live cu HEAD. De aceea D112 poate fi rupt în producție cât timp suita e verde.

**Efect pe contabil:** un contabil care validează/depune D112 pe iconta.eu ACUM primește 500 (declarație
lunară de salarii = nedepozabilă pe firmele F2/F6). Toată munca celor 45 de commituri nu ajunge la utilizator.

**Reparație (candidat, cu decizia lui Costin):** restart `systemctl restart iconta-nou` după deploy + gard/hook
care (a) restartează serviciul la avans de HEAD SAU (b) refuză raportul „încheiat" cât timp procesul live nu e
pe HEAD (endpoint `/versiune` care întoarce `git rev-parse HEAD` de la pornire, comparat cu HEAD curent).

**REMEDIERE 07.08 (tura 2, aprobat de Costin) — DEFECT-1 REPARAT ȘI PROBAT pe prod:**
- `sudo systemctl restart iconta-nou` → MainPID 298512 (pornit 01.08) → 2518402 (pornit 07.08 21:38), pe cod HEAD.
- PROBAT (nu presupus), pe `:8010` prod, cod nou:
  - (a) `POST /declaratii/d112/valideaza` pe firmă REALĂ (tenant_001/S4, 2026/1) → **HTTP 200** (stare=erori din
    atenționare DUK, NU 500). D112 nu mai crapă.
  - (b) firmă NOUĂ creată pe `:8010` → **schemă LA ZI**: `perioada_confirmata` prezentă, toate 8 coloane
    `concedii_medicale` (cnp_ingrijit, cod_urgenta, data_certificat_initial, este_continuare, numar_initial,
    serie_initiala, venituri_6_luni, zile_6_luni) + 2 coloane `facturi` (data_faptului_generator,
    tert_platitor_tva). Provizionarea produce acum tenanți conformi. Firma de probă ștearsă după verificare.
- **Migrări prod (alt strat, aceeași clasă):** toți cei 12 tenanți reali conformi cu template → migrările de
  SCHEMĂ tenant sunt LA ZI pe prod (garda `test_toti_tenantii_conform_cu_template` verde = mecanismul „alt
  strat" există și trece). GOL rezidual: nicio gardă pentru drift de schemă PUBLIC (vezi GARZI, candidat nou).
- **Artefacte de test curățate:** tenant_013 (driftat), tenant_014, tenant_013-bis (proba), cabinet B — șterse
  strict-scoped; rămân 12 tenanți reali (001–012), neatinși. Poarta verde reconfirmată (2 gărzi passed).
- **Rămâne clasa neînchisă:** „running == HEAD" nu are încă gard (vezi GARZI candidat nou); restartul de azi e o
  reparație de INSTANȚĂ, nu de clasă.

---

### DEFECT-2 — [E2/E6] CNP la adăugarea DIRECTĂ a salariatului validează doar formatul (13 cifre), nu cifra de control. Confirmat cu probă în aval (DUK respinge D112).

**Clasă:** validare CNP inconsecventă între căile de intrare. = **instanța pe flux** a candidatului consemnat în
GARZI.md 07.08 (adus de Costin din auditul de reguli).

**Repro (pe :8011, cod HEAD):**
- `POST /tenants/6701/salariati` cu `cnp="6010101123458"` (13 cifre, dar cifra de control GREȘITĂ;
  `valideaza_cnp("6010101123458") = (False, "cifra de control")`) → **200, salariat acceptat TĂCUT**.
- Apoi `POST /declaratii/d112/valideaza` → DUK **stare=erori**:
  `E: asigurat (2) [idAsig = 2] eroare atribut: cnpAsig: CNP invalid ('6010101123458')`.
  Deci CNP-ul greșit intră în evidență și ajunge în D112, care devine NEDEPOZABIL — validatorul oficial ANAF îl
  respinge abia la depunere. Tiparul PLAN_B: „apare tăcut o declarație GREȘITĂ & depozabilă".
- Sursa: `core/salariati_api.py:85-87` — `_CNP = re.compile(r"^\d{13}$")`, doar format.

**Vânătoare de clasă (statică, pentru reparație):** singura cale NON-import de intrare CNP e adăugarea directă a
salariatului (`salariati_api`). Verificate și CURATE: calea de **import** (`salariati_import_api.valideaza_cnp` —
cheie de control 279146358279 + dată + județ) și câmpul **`cnp_ingrijit`** (CM cod 09/91/92/17,
`salariati_api.py:341` cheamă tot `valideaza_cnp`). `grep -rn cnp core/*_api.py main.py` (fără import) →
doar `salariati_api.py:86`. Clasă mărginită; reparația = refolosirea lui `valideaza_cnp` (nu cod nou).

**Ar fi prins-o suita existentă?** NU direct — nicio gardă nu compară cele două căi de validare CNP între ele.
DUK o prinde DOAR la validare/depunere (java; „erori"), nu în `pytest`. Candidatul stă în GARZI.md fără gard.

**Efect pe contabil:** salariat cu CNP tastat greșit (control) intră fără avertisment; se descoperă abia când
ANAF/DUK respinge D112.

---

### INFIRMAT-OK — verificate și corecte (nu sunt defecte)

- **[E1] D205 exclus din setul datorat al F2 — CORECT.** `obligatii_datorate(vector F2, cu salariați)` întoarce
  `{D100, D112, D300, D394, D406}`, FĂRĂ D205. Generatorul confirmă: `POST /declaratii/d205` →
  „D205 fara niciun beneficiar de venit". D205 e informativa pe impozit REȚINUT LA SURSĂ (dividende/chirii/etc.),
  nu pe salarii (acelea merg în D112). Rândul F2 din PLAN_B care listează D205 e imprecis pentru o firmă doar cu
  salariați; codul e corect că NU o datorează fără beneficiari.
- **[E1] D406 (SAF-T) inclus în setul F2 — plauzibil corect (nu defect).** SAF-T extins la plătitori; motorul îl
  datorează. `POST /declaratii/d406` generează (69KB, 0 furnizori pt că n-am pus achiziții). Temeiul exact al
  obligativității SAF-T pe micro se poate confirma separat dacă se dorește — nu în scopul walk-ului.
- **[E10] four-eyes NU blochează self-approval — PRIN DESIGN.** `POST /coada/{id}/aproba` de același user care a
  pregătit → 200. `coada_api.aproba`: patru-ochi se aplică DOAR dacă `patru_ochi_activ` (opt-in al patronului,
  default False) ȘI `patru_ochi_posibil` (≥2 useri competenți: pregătitor + validator distincți). Cabinet fără
  opt-in / cu un singur user → self-approval permis. Control intern opțional, nu defect.

### OK — verificat funcțional (flux real, :8011)

- **[E3] Facturare** cotă 21%: `POST /facturi/emite` (net 10000) → factura_id, total 12100, TVA 2100. Denumire
  beneficiar obligatorie (422 fără ea) — respectat.
- **[E4] D300 trimestrial** (luna-ancoră 3): op=7, DUK **stare=valid**, „Rezultat TVA de plată 2.100 lei".
  **D394**: op=1 partener TVA RO. Reconcilierea nu blochează fals.
- **[E11] Izolare tenant — ȚINE.** Al doilea cabinet (Cabinet B) → `GET /tenants/6701/{vector,salariati,
  firma-profil}` = **404**, `POST /declaratii/d300` pe tenantul A = **403**. Niciun 2xx cross-tenant.

---

## CE A RĂMAS NEVERIFICABIL FĂRĂ BROWSER (pentru tura 2 — playwright + chromium)

Parcurgerea HTTP + inspecția statică NU pot decide RANDAREA și temporalitatea. De verificat vizual în tura 2:

1. **[E2] Markeri obligatorii `*`** — apar VIZUAL lângă câmpul pe care backend-ul chiar îl cere (nu doar în DOM).
2. **[E2/D1a] Skip-uri la import** — numărul de rânduri sărite e VIZIBIL pe ecran (nu tăcut).
3. **[E11/G10] Mesajul de eroare apare LÂNGĂ câmpul-cauză** (nu doar existent în DOM). G10 e implementat DOAR pe
   `flux_concediu` (`#cm-cnp-ingrijit`, coduri 09/91/92/17); pe restul fluxurilor NU — de confirmat vizual.
4. **[E11] poarta_gol** — declarația cu op=0 (văzut: D100 op=0, D406 op=0, D300 Q4 op=0) trebuie să arate o
   POARTĂ vizuală „declarație goală", nu identic cu una golită de un query rupt. Neverificabil prin HTTP.
5. **[E11] Starea goală are cele 3 părți**; blocajul global rămâne vizibil (nu fundătură).
6. **[E8/A5] Metoda de amortizare AFIȘATĂ = cea calculată** (azi calc e liniar chiar dacă metoda zice
   degresiv/accelerat — DESCHIS-cunoscut). Divergență pur vizuală.
7. **[E12] Comportament la ÎNCĂRCARE** (întreg): flash de ecran gol confundabil cu „nu ai date", loading vizibil,
   latență, date parțiale, revenire din eroare de rețea. Nicio gardă de sursă nu-l acoperă.

## DESCHIS-cunoscut (nu re-raportate ca defecte — zgomot cunoscut din predare)

- A5 amortizare liniară indiferent de metodă (campanie proprie amânată).
- AUTO-legare episoade CM adiacente (decizie, nu defect).
- F8-produs (marjă/nerezidenți/forfetar) — oglindă de goluri de produs.
- `tva_redusa_5` 11%@2025 — decizie de produs.

## ARTEFACTE DE TEST lăsate (nu s-a reparat/curățat — „nu repari nimic")

- uvicorn `:8011` = instanță de test din HEAD (de OPRIT după walk; PID în `/tmp/uvicorn8011.log`).
- Sub cabinet Prisma: firme F2 `tenant_013` (cui 97700015, creată pe serverul stale) și `tenant_014`
  (cui 97701002, pe :8011), cu salariați de test — inclusiv un salariat cu CNP control-greșit (dovada DEFECT-2).
- Cabinet „Cabinet B Izolare SRL" (patronB@cabinetB.test) — creat pentru testul de izolare E11.
- Aceste date sunt în DB live sub cabinete de test; de curățat separat dacă deranjează (nu s-a atins, per regulă).

---

## REMEDIERE DEFECT-2 (07.08.2026, aprobat de Costin) — REPARAT + GARD

- **Fix (refolosire, nu cod nou):** `core/salariati_api.py:86` (`cnp_control_v1`) — `valideaza_salariat` cheama
  `valideaza_cnp` (format + data + judet + CIFRA DE CONTROL, cheia 279146358279), la fel ca import + cnp_ingrijit.
  Acopera CREATE (POST) si EDIT (PUT) intr-un singur loc (ambele trec prin `valideaza_salariat`).
- **Vanatoare de clasa (completa, CNP+CUI):** vezi harta in GARZI.md 07.08. CNP: singura cale nevalidata era
  salariat create/edit (reparata); restul (cnp_ingrijit, import, asociati) deja validau. CUI: control offline doar
  la provizionare + import parteneri; NEvalidat pe client/tert_cui (partial justificat: parteneri straini) si pe
  CUI PROPRIU firma la editare (candidat de reparat — GARZI 07.08).
- **Proba:** RED/GREEN + mutatie (git checkout la pre-fix -> 5 teste rosii cu motivul corect; re-aplicat -> 8
  passed). No-op pe date reale: sha256 D112 tenant_001 2026/1 IDENTIC pre/post (45e3b486…) — fix write-side,
  generarea neatinsa.
- **Gard:** `core/test_cnp_control.py` (8 teste): refuz control-gresit pe toate caile CNP + anti-cale-noua
  (INSERT CNP fara valideaza_cnp pica) + anti-regresie la format-only.
- **Nefacut intentionat (motiv):** bifa in TESTE.md a noului fisier de test = follow-up DUPA ce intra in HEAD
  (garda anti-stale `test_agenda` citeste `git show HEAD:` -> o citare in acelasi commit ar fi "citare moarta").

---

## TURA HEADLESS (07.08.2026, aprobat de Costin) — harness READY + primele constatari vizuale

**Harness:** playwright + chromium (headless-shell) + deps de sistem (apt) instalate pe server. Drive headless
al `:8010` (nginx SPA) merge end-to-end: landing -> modal acces -> login cabinet -> dashboard -> portofoliu firme
-> meniu firma -> formulare. Screenshot-uri in /tmp/shots (vazute de Code).

**E12 (baza) — OK:** ecranele parcurse RANDEAZA, fara ecran gol/mut: landing, modal login, dashboard
("Salut, Elena", 12 firme active — confirma curatarea teardown), portofoliu (12 firme listate), meniu firma
(Panificatie/S4), "Salariat nou". Nicio pagina goala confundabila cu "nu ai date" pe caile atinse.

**E2 — SUSPICIUNE (marker obligatoriu vs. ce cere aval-ul):** pe formularul REAL "Salariat nou" (firma S4),
DOAR **"Nume*"** e marcat cu `*`. **CNP** si **Data angajarii** NU au marker `*`, desi ambele sunt necesare in
aval: CNP = cnpAsig OBLIGATORIU in D112 (fara el declaratia lunara de salarii e incompleta/respinsa de DUK);
data_angajare = salariatii fara ea sunt FILTRATI la salarizare (constatare transa 1, 4 situri). In plus CNP e
backend-OPTIONAL (cnp=None -> 200, vazut in walk-ul HTTP). => formularul semnaleaza CNP ca optional in timp ce
D112 il cere -> cale TACUTA spre un D112 incomplet. Se leaga de zona DEFECT-2 (identitatea salariatului).
Recomandare (decizie Costin): marker `*` pe CNP + data_angajare + refuz backend la salariat ACTIV fara CNP
(sau macar avertisment vizibil ca D112 va fi incomplet). NU reparat (in afara scopului fix-ului CNP de azi).

**NEATINS inca in tura headless (nav mai adanca; harness + selectori acum cunoscuti -> continuare ieftina):**
- E11/G10: mesajul apare LANGA `#cm-cnp-ingrijit` pe `flux_concediu` (cod 09/91/92/17) — de deschis fisa CM.
- E11: poarta_gol pe o declaratie op=0 (D100/D406/D300-Q gol) — ecranul declaratii al firmei.
- E11: starea goala are cele 3 parti; blocaj global vizibil.
- E2/D1a: nr. de randuri sarite VIZIBIL la import.
- E8/A5: metoda de amortizare AFISATA vs. cea calculata.
- E12 (avansat): loading vizibil, latenta, date partiale, revenire din eroare de retea.

---

## TURA HEADLESS (2) 07.08 — DEFECT-3 (blocant) + verdict G10 pe flux_concediu

### DEFECT-3 — [E6, BLOCANT, LIVE] „Stat de plată" pe luna CURENTA da 500 -> tot payroll-ul dispare, ascuns ca „Niciun salariat activ"

**Clasa:** query necalificat pe schema + ruta fara search_path pe tenant; eroarea ascunsa de frontend.
**Repro (LIVE, :8010):** `GET /tenants/4784/stat-plata?an=2026&luna=8` -> **HTTP 500** (luna 1 -> 200 cu 12 salariati).
Root cause: `core/perioada.py:26 e_confirmat(conn, schema, an, luna, domeniu)` PRIMESTE `schema` dar NU-l
foloseste — `SELECT ... FROM perioada_confirmata` e NECALIFICAT, se bazeaza pe search_path. Ruta
`main.py:3708 tenant_stat_plata` cheama `stat_plata` pe `db.get_conn()` (FARA schema in search_path) ->
`UndefinedTable: relation "perioada_confirmata" does not exist` -> 500. Trigger: `stat_plata:60` cheama
`e_confirmat` DOAR cand un salariat are `tichet_val > 0` (tichete masa) -> luna 8 (S4 are tichete) crapa;
luna 1 (fara tichete pe acel path) merge. In-process cu `get_conn("tenant_001")` (search_path setat) merge
pe ambele -> de-aia unit-urile nu vad bug-ul.
**Frontend ASCUNDE eroarea (a doua fata):** `static/js/ecrane/firme.js:739` face `try{ api.get(stat-plata) }catch{}`
-> 500 inghitit -> `stat=[]` -> randeaza „**Niciun salariat activ încă.**". VIZUAL: contabilul deschide Stat de
plata August pentru S4 (12 salariati reali) si vede „niciun salariat" — payroll-ul intregii firme dispare TACUT
pe luna curenta. Exact tiparul PLAN_B: „la incarcare ecranul minte; gol confundabil cu eroare" (E11/E12) +
mascarea erorii (GARZI cat.0).
**Ar fi prins-o suita?** NU. `test_perioada`/`test_salarizare`/`test_tichete_pontaj` cheama e_confirmat/stat_plata
cu conn avand search_path pe tenant (get_conn(schema)) -> nu ating query-ul necalificat. Calea rutei
(get_conn() fara schema) + inghitirea din frontend `catch{}` sunt neacoperite. Aceeasi clasa ca DEFECT-1
(comportament de ruta/integrare neverificat de unit-uri). `perioada_confirmata` e tabela NOUA (cap.23, 15472f0);
integrarea in stat_plata nu a fost exersata pe calea reala a rutei.
**Efect pe contabil:** Stat de plata pe luna curenta = gol fals pentru orice firma cu salariati cu tichete de masa.
NEreparat (regula: nu repar). = defectul de clasa la care ma opresc din parcurgere.

### G10 — verdict vizual pe cele 5 puncte (ce VAD efectiv, nu ce ar trebui), flux_concediu, cod 09

Ajuns pe formularul „Certificat nou" (Concedii medicale) pe un salariat real (via luna 01/2026, ca sa ocolesc
DEFECT-3). Dupa „Calculează și salvează" cu campuri goale:
1. **Toate erorile deodata: DA.** La un singur Calc apar SIMULTAN toate erorile de camp (CNP-ingrijit, Data
   inceput, Data sfarsit, Zile lucratoare CM, Venituri 6 luni, Zile 6 luni), fiecare sub campul ei. Nu una cate una.
2. **Plasare sub camp: DA.** Fiecare mesaj rosu (bold) e direct SUB inputul lui. Sub CNP: mesaj rosu tranzitoriu
   „...completează CNP-ul persoanei îngrijite (13 cifre) — D112 îl cere obligatoriu." + un hint gri PERMANENT
   (regula DUK S97). Doua texte sub CNP -> usor redundant (ambele spun „D112 îl cere"), dar plasat corect.
3. **Conditionale pe cod: DA.** Cod 09 -> campul „CNP-ul persoanei îngrijite" + eroarea lui apar. Cod 01 -> TOATA
   zona CNP dispare (display:none). Campul si validarea lui sunt conditionate de cod (09/91/92/17).
4. **Re-validare fara stivuire: DA.** Dupa 3x Calc, mesajele raman SINGLE per camp (5, nu 15) — se inlocuiesc, nu
   se adauga. Fara duplicare vizuala.
5. **Aranjare: curata.** Grid de campuri, eroare rosie + hint gri sub fiecare, sectiuni clare (Certificat nou /
   Episod de boala / Baza de calcul). Singura observatie: redundanta eroare-rosie vs hint-gri sub CNP.

**Campuri certificat de CONTINUARE (noi, intrate ieri): OK.** La bifarea „Certificat de continuare (același episod
de boală)" apar corect „Seria certificatului inițial*" + „Numărul certificatului inițial*" (cu `*` + hint care
citeaza OUG 158/2005 art.17(1) si nota ca adaugarea continuarii poate ridica procentul certificatelor anterioare
la 75%). Reveal conditionat + randare corecte.

**Observatie G10 (SUSPICIUNE, FE/BE mismatch pe campul-pilot):** validarea FRONTEND a lui `#cm-cnp-ingrijit` e
DOAR format (`/^\d{13}$/`): am pus „6010101123458" (13 cifre, cifra de control GRESITA) si eroarea rosie a
DISPARUT (frontend multumit). Backend-ul (salariati_api:344 valideaza_cnp) verifica controlul -> ar bloca la
submit, dar mesajul inline G10 „langa camp" pentru control-gresit NU apare (vine doar din round-trip backend).
Mesajul FE zice chiar „13 cifre", nu „cifra de control valida". Pentru exact campul pe care e pilotat G10,
feedback-ul inline e mai slab decat backend-ul. (Nu e silent-wrong: backend blocheaza; e inconsecventa de UX.)

### NEATINS in aceasta tura (oprit la DEFECT-3, blocant): poarta_gol pe declaratii op=0, A5 metoda afisata, skip
import D1a, E12 avansat (loading/latenta/date partiale). Harness + selectori cunoscuti -> continuare ieftina.
