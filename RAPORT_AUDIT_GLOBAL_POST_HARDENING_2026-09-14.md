# RAPORT DE AUDIT GLOBAL — iConta, după închiderea P0…P7

**Snapshot auditat:** `iconta_STARE_COMPLETA_2026-09-14.zip`, construit din `git archive` la
**`cf13d201`** (SHA-256 `e971798abbb015938b03a4263899531b5e710b3d245f74e003e163e4778ba868`).
**Data:** 14.09.2026. **Cine:** audit de ansamblu, pornit de la zero.

---

## CUM S-A FĂCUT AUDITUL, ȘI CE ÎNSEAMNĂ ASTA PENTRU CIFRE

Nu s-a pornit de la concluzia că P0…P7 au găsit tot. Fiecare afirmație de mai jos vine dintr-o
**măsurătoare rulată pe snapshot**, nu din registre. Unde am folosit un registru al proiectului, o
spun — și îl tratez ca pe o afirmație de verificat, nu ca pe o dovadă.

Ce **nu** acoperă auditul ăsta, și se scrie ca să nu fie citit ca „tot": n-am rulat aplicația sub
sarcină, n-am testat penetrare, n-am citit cele 65 de generatoare de declarații linie cu linie
contra legii, și n-am verificat corectitudinea fiscală a rezultatelor pe date reale. E un audit al
**formei codului, al gărzilor și al suprafețelor**, nu al cifrelor fiscale produse.

**Inventarul:** `main.py` 6557 linii · `core/` 953 fișiere (521 probe, 51 depozite, 27 use-case,
27 instrumente de scanare, ~327 module de producție) · `scripts/` 69 · 421 de rute · 5840 de teste.

---

# 1. DEFECTE REALE

*Lucruri care nu funcționează cum spune codul despre ele. Fiecare are dovada și consecința.*

## D1 — Limitarea de ritm e per-proces, iar producția rulează două procese (IMPACT MARE)

> **ÎNCHIS la E1 (14.09.2026).** Cele trei dicționare au trecut în `public.cereri_ritm`;
> `RATE_LIMIT_IN_PROCES` 6 → 0, gardat de `core/test_ritm_partajat.py`. Constatarea rămâne
> scrisă aici cu măsurătoarea ei — un raport de audit consemnează ce a găsit, nu se rescrie.

Trei limitatoare anti-abuz țin starea în memoria procesului:

| unde | ce apără |
|---|---|
| `main.py:1545` `_reset_rate` | „Am uitat parola" — trimite e-mail |
| `main.py:1557` `_cui_rate` | `/public/verifica-cui/{cui}` — **cheia ANAF**, rută publică |
| `core/uc_comun.py:507` `_magic_rate` | magic-link — trimite e-mail |

Implementarea, `main.py:1558-1566`, își scrie premisa în docstring: *„Anti-spam per IP (in-memory,
**single worker**)"*. Premisa a murit la **P6 valul 3**, când unitatea systemd a primit
`Environment=WEB_CONCURRENCY=2`. Cu două procese, fiecare cu dicționarul lui, **pragul efectiv e
dublu** (10 cereri/15 min în loc de 5), iar la fiecare repornire — deci la fiecare publicare —
contoarele se golesc.

**Ce arată că e un defect, nu o alegere:** aceeași problemă a fost deja recunoscută și reparată în
vecinătate. `main.py:1274` scrie, despre blocarea la autentificare: *„un proces n-o vedea (măsurat:
cinci eșecuri pe A, `blocat=False` pe B)"* — și blocarea a fost mutată în baza de date. Cele trei
limitatoare au rămas în urmă.

**Consecință:** `/public/verifica-cui` e rută **publică**, fără `Depends`, care cheamă ANAF
(`main.py:2661-2666`). Pragul dublat înseamnă dublu consum pe cheia ANAF, iar golirea la repornire
înseamnă că un atacant obține o fereastră curată ori de câte ori publicăm.

## D2 — Aceleași trei dicționare nu uită niciodată un IP (IMPACT MEDIU)

> **ÎNCHIS la E1.** Orice scriere șterge TOATE rândurile ieșite din fereastră, ca la
> `login_esec`; probat pe 20 de IP-uri expirate + o scriere → un singur rând rămas.

`main.py:1563-1566`:

```
q = [t for t in store.get(ip, []) if acum - t < fereastra]
if len(q) >= maxreq: raise HTTPException(429, ...)
q.append(acum); store[ip] = q
```

Curățarea se face **numai pentru IP-ul care cere acum**. Un IP care a cerut o dată rămâne în
dicționar cât trăiește procesul. Cheia e controlată de client (antetul `X-Real-Ip`, pus de nginx din
`$remote_addr`), deci creșterea e nemărginită și direct proporțională cu numărul de IP-uri distincte
care ating trei rute publice.

## D3 — `uvicorn.log` crește nemărginit; nu există rotație (IMPACT MEDIU)

> **PARȚIAL la E1.** `config/iconta-logrotate.conf` e scris și verificat; **instalarea cere
> root**, deci constatarea rămâne DESCHISĂ până când fișierul ajunge în `/etc/logrotate.d/`.

Unitatea scrie cu `append` în arborele aplicației — `config_referinta_iconta-nou.service:22-23`
(și `/etc/systemd/system/iconta-nou.service:15` pe server). **Măsurat pe snapshot: 63,7 MB**, plus
`alerta_acces.log` 1,0 MB și `firma_rezumat.log` 0,55 MB. `/etc/logrotate.d/` **nu conține nicio
intrare pentru iConta**. Discul e la 15% (11 G din 75 G), deci nu e urgent — dar e o resursă fără
plafon pe partiția aplicației, iar jurnalele de pornire sunt chiar locul unde se citesc incidentele.

## D4 — Inversare de strat: un modul din `core/` importă `main` (IMPACT MEDIU)

> **ÎNCHIS la E6 (14.09.2026).** `CORE_IMPORTA_MAIN` 2 → 0, gardat de
> `core/test_core_fara_main.py`. Constatarea rămâne scrisă aici cu măsurătoarea ei.

`core/firma_rezumat.py:1009` și `:1024` — lucrătorul modelului de citire face `import main as _main`
și cheamă `_main._construieste_contabil(...)`, `_main.pastila_firma(...)`, `_main._termene_una_firma(...)`.
Stratul de sub HTTP depinde de stratul HTTP.

**Nu e teoretic:** în valul use-case, o curățenie automată de importuri a scos din `main.py`
re-exportul `pastila_firma` — nefolosit *acolo* — și **șase firme au ajuns cu `control_fiscal` în
stare de eroare**. Repararea a fost să se pună importul la loc cu `# noqa`, adică să se păstreze
inversarea. Cele patru criterii canonice ale lui P7 nu se uită la muchia asta: ele întreabă despre
SQL în rută, `db` în motorul fiscal, module mixte și proprietatea tranzacției.

---

# 2. RISCURI

*Nu s-a întâmplat nimic rău; suprafața există și nimic nu o păzește.*

## R1 — 59 de rute (14%) nu sunt numite de niciun test; 21 dintre ele SCRIU (IMPACT MARE)

Măsurat pe cele 421 de rute, căutând în toate probele (`core/`, `frontend_test/`, `scripts/`) atât
numele funcției, cât și calea. Dintre cele 21 care schimbă date:

```
POST   /cabinet/api-chei              DELETE /cabinet/api-chei/{kid}
POST   /admin/cabinete/{id}/suspenda  POST   /admin/cabinete/{id}/reactiveaza
POST   /portal/bon                    POST   /portal/bon/{bon_id}/confirma
DELETE /portal/bon/{bon_id}           POST   /migrare/incarca
POST   /eu/schimba-parola             POST   /eu/cabinet
POST   /raportari/mesaj/{mid}/imagine POST   /portal/recomanda
```

**Nuanța, ca să nu fie citit mai rău decât e:** rutele *sunt* acoperite structural — sweep-urile
generice (`core/test_rute_autentificate.py`, `core/test_rute_model_body.py`) le trec pe toate, deci
nimeni nu poate adăuga o rută fără gardă sau fără model de corp. Ce lipsește e **comportamentul**:
nicio probă nu spune ce se întâmplă când chei API se creează și se revocă, când un cabinet se
suspendă, sau când un client încarcă un bon.

Cele mai grele două: `POST/DELETE /cabinet/api-chei` e **suprafață de autentificare** (creează și
revocă chei care ocolesc parola), iar `/admin/cabinete/{id}/suspenda` schimbă accesul unui cabinet
întreg.

> **URMARE (14.09.2026).** Cele două rute au acum probe de comportament în suită —
> `core/test_comportament_chei_suspendare.py`, 10 probe. Ele au scos o constatare pe care raportul
> n-o avea: **suspendarea unui cabinet nu invalidează cheile lui de API**. Constatarea a fost
> reparată în aceeași zi, pe decizia lui Costin: suspendarea închide și cheile, iar reactivarea le
> redă fără regenerare. Vezi DECIZII.md (43) pentru constatare și (44) pentru decizie.
>
> **CORECȚIE (14.09.2026), la o cifră a acestui raport.** Căutarea a numărat doar fișiere
> `test_*.py`. Pentru `POST /cabinet/api-chei` **există** o probă cap-coadă —
> `frontend_test/proba_verificare_functionalitati.py:1232` chiar cheamă ruta prin HTTP —, dar ea
> **nu e în suită**: fișierul nu se numește `test_*`, iar `pytest --collect-only` pe el întoarce
> *„no tests collected"*. Deci cifra **59** rămâne corectă pentru SUITĂ, iar formularea „nicio
> probă" era prea tare pentru ruta aceea: există una, doar că nu rulează la poartă. Pentru
> `DELETE /cabinet/api-chei/{kid}` și cele două rute de suspendare/reactivare nu există nimic.

## R2 — Trei reparații fiscale aplicate, dar niciodată exercitate (IMPACT MEDIU-MARE)

Din chiar registrul de datorii al proiectului, `core/test_datorie.py:126,132,138`: trunchierea
denumirii/adresei a fost reparată în **d205**, **d390** și **d710**, dar *„NEEXERCITAT — sare «nu se
datorează» pe firma fără beneficiari / fără operațiuni IC"*. Pentru d710 e mai rău: *„niciun test nu-i
verifică trunchierea"*.

**De ce contează:** o reparație pe care n-a văzut-o rulând nimeni e o intenție, nu un fapt. Aici
efectul e o declarație respinsă la ANAF pe un câmp prea lung — vizibil, dar la depunere.

## R3 — Opt coduri de regulă DUK/eFactura canonizate fără verificare la sursă (IMPACT MEDIU)

`core/test_datorie.py:159`: *„cele 8 mențiuni canonizate la DUK/eFactura n-au fost re-verificate la
sursă — s-a schimbat doar markerul. Dacă vreuna cita o regulă GREȘITĂ înainte, canonizarea a
făcut-o să arate corect și să rămână greșită"* (A91b, R28, R17, R11b, R15, F10_68, BR-RO-100,
BR-RO-110). Plus `:167`: R17/R28/R32 din D300/D394 au fost tratate drept **rânduri** de declarație,
dedus din context, nu verificat în structura oficială.

E clasa cea mai insidioasă din tot auditul: **o citare greșită care arată corect**.

## R4 — Un fapt contabil înghețat nu spune de unde știe (IMPACT MIC-MEDIU)

`core/anaf_api.py:97-106` — `platitor_tva_freeze(cui, fallback)`: dacă ANAF e jos sau CUI-ul nu e
găsit, întoarce `fallback`, tăcut. La `core/uc_tenants.py:3519`, fallback-ul e **`True`** codificat,
iar valoarea se scrie pe factură (`tert_platitor_tva=_tert_pl`) ca fapt imutabil.

**Argumentul contrar, care e real:** ruta e o achiziție cu TVA deductibilă, iar semantica operațiunii
implică un furnizor plătitor — comentariul de la `core/uc_tenants.py:3559` o spune. Deci valoarea nu e o invenție.

**Ce rămâne totuși:** faptul stocat **nu poartă proveniența**. Nu se poate distinge „confirmat de
ANAF" de „presupus din operațiune", iar doctrina proiectului cere exact opusul — *„un necunoscut nu
se rotunjește la «știu că nu»"* (interdicția 32, gardată în `core/test_document_ref_necunoscut.py`
pentru `note_ciorna`). Aceeași regulă nu se aplică aici.

## R5 — Restaurarea din backup a fost probată o singură dată, acum două luni (IMPACT MEDIU)

`GARZI.md:413` și `DECIZII.md:2632`: restaurare cap-coadă pe **18.07.2026** — `pg_restore` exit 0,
scheme identice, `tenants 2=2`. Corect făcută. Dar de atunci schema a crescut (19 fișiere DDL,
44 de migrări unice), iar proba **nu se repetă**: nu există timer, script sau probă care s-o reia.
Un backup neprobat periodic e o afirmație despre trecut.

---

# 3. DATORII TEHNICE

*Costuri cunoscute, măsurate, fără urgență — dar care cresc.*

| # | ce | cifra de azi | dovada |
|---|---|---|---|
| T1 | constante fiscale fără temei scris, în producție | **139** în 54 fișiere | clichet în `core/test_constante_nesursate.py`; vârf: `salarizare.py` 18, `d212_engine.py` 11, `common.py` 8, `d101.py` 7, `d406_active.py` 7 |
| T2 | funcții peste 120 de linii | **25** | `core/d300.py:147 calcul_d300` **546** · `core/d112.py:229 _d112_genereaza` **465** · `core/d394.py:416 calcul_d394` **379** · `core/control_fiscal_api.py:172 obligatii_datorate` **358** |
| T3 | modulul-sac al stratului use-case | `core/uc_tenants.py` **5440 linii / 254 funcții** | valul use-case a mutat forma lui `main.py` cu un strat mai jos, nu a desfăcut-o |
| T4 | aserțiuni ancorate pe TEXT, nu pe structură | **1221** | clichet 50, `core/clichet_garzi_pe_text.json`; METODA §23 |
| T5 | `except ... : pass` în producție | **25** (+ 229 `except Exception` largi) | ex. `core/agenda.py:195`, `core/amef_import.py:32`, `core/anaf_api.py:105`. Garda existentă (`core/test_masti.py`) acoperă **JS și SQL**, nu Python |
| T6 | funcții care se întind pe mai mult de o tranzacție | **104** | `core/uc_coada.py:26 coada_adauga` (4 blocuri), `core/uc_tenants.py:541 vector_salveaza` (3), `core/uc_coada.py:200 coada_depune` (3) |

**Despre T6, ca să nu fie citit greșit:** P4 a clasificat **căile** și a păzit cele 7 critice cu
injecție de defect, iar clasificarea e vie și verde azi (43 de probe, `core/p4_clasificare.py`).
Cifra 104 e la nivel de **funcție**, e mai largă, și nu contrazice P4 — dar arată suprafața pe care
o judecată viitoare o are de reluat.

---

# 4. LIMITĂRI DE DOVEZI

*Ce NU dovedesc cifrele publicate. Partea cea mai importantă a acestui audit.*

## L1 — `D4_STRAT_MIXT = 0` are un domeniu pe care cifra nu-l arată (IMPACT MARE)

Universul registrului de straturi se derivă, la `scripts/scan_p7_straturi.py:351-360`, ca:

> generatoare de declarații **∪** module cu valori fiscale **∪** module care poartă rute

Măsurat pe snapshot: **195 de module declarate din 405 de producție**. Cele **211 nedeclarate** n-au
fost niciodată clasificate — iar **138 dintre ele conțin SQL**, în total **685 de instrucțiuni**:

```
core/stocuri_cv_api.py      31        core/auth_api.py            24
core/tenant_provisioning.py 28        core/reconciliere_api.py    18
core/raportari_api.py       24        core/coada_api.py           18
```

Deci propoziția adevărată nu e *„niciun modul nu face două straturi deodată"*, ci **„niciun modul
din universul declarat nu face două straturi deodată"**. Module ca `coada_api.py` (mașina de stări a
cozii **plus** 18 instrucțiuni SQL) sunt exact forma pe care D4 o caută, și stau în afara lui.

*Nu e o acuzație de cifră falsă: `p7_criterii` măsoară ce spune că măsoară. E o citire care lipsește
de lângă cifră.*

## L2 — Defectul D1 stă într-un punct orb DECLARAT al lui P6 (IMPACT MARE)

Detectorul de stare de proces (`scripts/scan_stare_proces.py`) raportează el însuși:

```
nume_mutabile (clasificate)      13
orbire_prin_apel                640
excluse  E3_nume_importat      1430 · E4_immutable 4730
```

Cele trei dicționare de la D1 **apar în `raw`** (`core/uc_comun.py:507`, `main.py:1545`, `main.py:1557`)
dar **nu apar între cele 13 clasificate**: mutația lor (`store[ip] = q`) se face pe un dicționar
primit ca **parametru**, iar detectorul își declară orbirea exact acolo — `main.py:1567
_rate_limit_reset` și `main.py:2662 public_verifica_cui` sunt în lista `orbire_prin_apel`.

`core/test_stare_proces.py` cere ca **numele detectate** să fie clasificate. Cerința e satisfăcută.
Dar „P6 închis, starea business în PostgreSQL" se citește ca o afirmație despre **toată** starea de
proces, iar ea e despre cele 13 pe care detectorul le vede.

## L3 — Șapte rute despre care detectorul de apelanți nu poate afirma nimic

`scripts/scan_ancore_rute.py`: `421 rute = ACCEPTAT 382 + GRI 7 + ROSU 0 + EXCLUS 32`. GRI **nu e
verde** — e „nu se poate ști", iar verdictul o scrie. Clichet R80 = 7, poate doar să scadă.

## L4 — Portalul clientului nu are acoperire de comportament

Toate cele cinci rute `/portal/bon*` sunt în lista R1 (fără test care să le numească), iar fluxul
bon → AI → ciornă → confirmare e singurul din aplicație în care **un client**, nu contabilul, scrie
date care ajung în contabilitate.

---

# 5. CE E DEJA ACOPERIT CORECT

*Verificat în auditul ăsta, nu preluat din registre.*

| # | ce | dovada măsurată |
|---|---|---|
| C1 | **Izolarea între firme și injecția SQL** | 328 de `execute()` cu f-string; interpolează **doar** `schema` (381 folosiri) și constante literale de coloană/tabel. **Zero rute primesc `schema` ca parametru**. Toate cele 6 fragmente dinamice rămase sunt **literale alese de cod**, cu valorile pe `%s`: liste construite din șiruri fixe (`core/jurnal_api.py:208`, `core/rip_api.py:91`), un ternar între două nume de coloană (`core/facturi_api.py:638`, `core/spv_conector.py:254`), un filtru fix (`core/export_saga.py:167`) și o pereche tabel/condiție luată dintr-un **tuplu literal** din apelant (`core/repo_control_incrucisat.py:105` ← `core/control_incrucisat.py:173-178`). Niciunul nu primește text din cerere. Numele de schemă nouă e generat `tenant_%03d` și validat înainte de DDL (`core/tenant_provisioning.py:106`) |
| C2 | **Autentificare și autorizare** | 402 din 421 de rute sunt în spatele a 5 dependențe (`cere_cabinet` 239, `cere_rol` 102, `cere_context` 37, `cere_client` 19, `cere_api_key` 5); cele 19 fără `Depends` sunt toate public-prin-natură (`/`, `/auth/login`, `/public/*`, `/ghid`, `/robots.txt`). Blocarea la autentificare e în baza de date, deci **traversează procesele** (`main.py:1274-1284`) |
| C3 | **Chei API** | `secrets.token_urlsafe(32)`, păstrate ca **SHA-256**, arătate o singură dată (`core/api_public.py:9-12`); revocarea caută tot pe hash (`:46-49`) |
| C4 | **Jetoane și parole** | HMAC-SHA256 cu `exp`+`iat`, comparat cu `hmac.compare_digest` (`core/nucleu.py:69,102-106`); parole scrypt pentru conturi noi, bcrypt pentru cele vechi cu rehash leneș (`core/auth_api.py:40-47`) |
| C5 | **Apeluri externe** | 7 locuri de apel HTTP; toate au `timeout`. Singurul fără termen literal e dispecerul `core/spv_conector.py:500`, iar toți apelanții îl dau prin `**kw` (`timeout=30/60/120`) |
| C6 | **Frontend ↔ backend** | **299** de căi distincte chemate din `static/js/**`; **0** fără rută potrivită |
| C7 | **Proprietatea tranzacției (P4)** | clasificarea e **vie**, nu un fișier: 43 de probe verzi, 7 căi critice, fiecare cu injecție de defect (`core/test_p4_fault_injection.py`) |
| C8 | **Backup** | local zilnic `pg_dump -Fc` (7 zile) + off-site rsync (30 zile), cu numărarea eșecurilor consecutive și alertă la prag (`config/iconta-backup.sh:1-17`); restaurare probată cap-coadă (v. R5 pentru limită) |
| C9 | **Registrul de datorii ca probe** | `core/test_datorie.py` ține datoriile ca `xfail(strict=True)` cu motiv și dată: apar în raportul fiecărei rulări și **devin roșii când se rezolvă** — exact invers decât un TODO |
| C10 | **Declarațiile** | toate cele **65** de generatoare sunt exercitate de cel puțin o probă; completitudinea golden-XSD e ea însăși gardată (`core/test_golden_xsd.py:33`) |
| C11 | **Rate de curse pe scriere** | 53 de `ON CONFLICT`, 5 `FOR UPDATE`, 6 blocaje consultative — cursele se apără în **bază**, nu doar în cod |

---

# 6. PRIORITIZARE

| rang | element | de ce acolo |
|---|---|---|
| 1 | **L1** — domeniul lui `D4=0` (138 module cu SQL neclasificate) | schimbă citirea celui mai vizibil rezultat al lui P7 |
| 2 | **D1** — ritm per-proces pe trei rute publice | defect viu, cu efect de securitate, pe o premisă moartă de la P6 |
| 3 | **R1** — 21 de rute care scriu, fără probă de comportament | include suprafața de chei API și suspendarea unui cabinet |
| 4 | **L2** — 640 de puncte oarbe declarate la P6 | e cauza lui D1 și poate ascunde altele ca el |
| 5 | **R2/R3** — reparații fiscale neexercitate, citări neverificate | corectitudine fiscală: efect direct asupra unei declarații depuse |
| 6 | **D4** — `core/` importă `main` | a produs deja un incident real |
| 7 | **D2, D3** — creștere nemărginită (memorie, jurnal) | fără termen apropiat, dar fără plafon |
| 8 | **T1…T6** | datorii care cresc încet |
| 9 | **R4, R5, L3, L4** | risc scăzut sau limită declarată |

---

# 7. ROADMAP PROPUS — etapa următoare

Fiecare pas are **criteriul lui mecanic**, ca P0…P7: o cifră care se recalculează, nu o impresie.

### E1 — „Ritmul se numără o singură dată" *(1–2 zile)*
Cele trei limitatoare trec în baza de date, pe modelul deja folosit la blocarea autentificării
(`login_esecuri`), cu curățare periodică. Logrotate pentru `uvicorn.log` și celelalte.
**Criteriu:** `RATE_LIMIT_IN_PROCES=0`, probat cu două procese reale (ca la P6) — cinci cereri pe
lucrătorul A, a șasea refuzată pe B. Închide **D1, D2, D3**.

### E2 — „Universul, nu eșantionul" *(3–5 zile)*
Universul registrului de straturi se lărgește la **orice modul care conține SQL**. Cele 138 primesc
strat declarat; D1/D2/D4 se re-derivă pe universul real.
**Criteriu:** `MODULE_CU_SQL_FARA_STRAT=0` și cele trei detectoare recalculate pe universul nou —
cu cifra dinainte și cea de după, scrise amândouă. Închide **L1**; probabil deschide un val de
separare, care se planifică **după** ce se vede cifra.

### E3 — „Ce scrie, se probează" *(3–4 zile)*
Probă de comportament pentru cele 21 de rute care scriu și n-au niciuna, în ordinea: chei API →
suspendare cabinet → portal bon → restul.
**Criteriu:** `RUTE_CARE_SCRIU_FARA_PROBA=0`, cu clichet. Închide **R1**, reduce **L4**.

### E4 — „Reparația se vede rulând" *(2–3 zile, cere o firmă de probă cu profil potrivit)*
Cele trei trunchieri (d205/d390/d710) primesc firma care le declanșează; cele 8 coduri DUK/eFactura
se re-verifică la sursă, unul câte unul.
**Criteriu:** cele patru `xfail(strict=True)` din `core/test_datorie.py` devin verzi și se scot.
Închide **R2, R3**.

### E5 — „Motoarele fiscale se pot citi" *(continuu, nu o campanie)*
`calcul_d300` (546), `_d112_genereaza` (465), `calcul_d394` (379) se desfac pe secțiuni de formular,
fiecare cu probă proprie. Se face **numai** când se atinge oricum modulul, nu ca val separat.
**Criteriu:** clichet descrescător pe „funcții peste 200 de linii în motoarele fiscale".

### E6 — „Modelul de citire nu mai depinde de HTTP" *(1 zi)*
`core/firma_rezumat.py` primește cele trei funcții prin injecție, nu prin `import main`.
**Criteriu:** `CORE_IMPORTA_MAIN=0`, gardat. Închide **D4**.

---

## O SINGURĂ CONCLUZIE

Aplicația e, structural, într-o stare bună și neobișnuit de bine păzită: 5840 de probe, gărzi care
verifică gărzile, registre care nu pot îmbătrâni tăcut, și o disciplină de măsurare care a prins, în
chiar ultimul val, patru pierderi tăcute pe care nicio suită verde nu le-ar fi arătat.

Ce a găsit auditul ăsta nu contrazice P0…P7. **Aproape tot ce e mai grav stă în ce anume au măsurat
cifrele, nu în ce au măsurat greșit** — un univers definit mai îngust decât îl citește cineva care
vede rezultatul, și un punct orb declarat în care s-a așezat un defect viu. De-aia primele două
locuri din prioritizare sunt o *limitare de dovezi* și un defect care trăiește înăuntrul alteia.

*Un instrument care își declară orbirea e mai bun decât unul care tace. Dar orbirea declarată
rămâne orbire, iar cineva trebuie să se uite acolo cu mâna.*
