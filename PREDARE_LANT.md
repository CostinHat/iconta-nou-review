Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — masurarea clasei de constante fiscale (tura 20.08, seara)

## REPORNIRE (comanda exacta, gata de dat) — TURA 20.08(c): scan constante + R5

LIVRAT, comis si impins (`e188018`, `feddfd0`; HEAD = origin/main; backup/lant-2026-08-20; RUNNING 21:21 > commit 21:12; :8010 -> 200):
- **Clasa de constante fiscale s-a MASURAT**, la comanda lui Costin, INAINTE de a repara fragmente din
  ea. `core/scan_constante.py` + clichet per fisier `core/test_constante_nesursate.py`.
  **A=48 sursate / B=308 nomenclator / C=126 NESURSATE / D=37 precizie.** Partea invizibila (126) e mai
  mare decat cea vazuta in inventarul pe teste de pe 31.07 (85). Termenele sunt 4 din 126.
- **R5**: `temei_legal` despartit de `regula_produs` in harta casetelor + garda
  `core/test_harta_temei.py` (citare rezolvabila in `anaf_surse/`, `None` asumat, sau `DATORIE`
  explicita; regula de produs poarta decizia si data). Toate cele 6 intrari trimiteau la COD, zero la un
  act, si `TEMEI` n-avea niciun consumator.

**FRONT NOU DESCHIS de masuratoare — cele mai grele din C, in ordinea in care ajung la contabil:**
1. ~~`cote_tva.COTA_STANDARD = 21`~~ **CORECTAT, vezi mai jos: e FALS POZITIV.** Modulul isi citeaza
   temeiul in antet (art. 291 CF, Legea 141/2025) si per categorie, si e pe `_TVA_EXCLUSE` in verificator.
2. `cota=21` / `procent=8` ca **default de parametru** in `tva_marja`, `tva_marja_turism`,
   `tva_agricultori` — supravietuiesc TACUT unei schimbari de cota. Nu pica niciun test.
3. `Decimal("16")` duplicat in `d101.py:40` si `d101g.py:62` — aceeasi cota, doua locuri.
4. `d216.COTA_IMPOZIT = 0.3` — cota fiscala in **float**, nu Decimal.
5. `d212_engine.py:148-174` — 11 `assert` cu valori asteptate hardcodate intr-un modul de PRODUCTIE.
6. `salarizare.py` 19 valori (deduceri 0.20-0.45, `PCT_TINERI` 0.15, `PRAG_VENIT_DEDUCERE` 2000, concediu
   medical 0.55/0.65/0.75/0.85) si `common.py` ferestrele 220/450, 240/470, 250/490 — fara `Temei`, chiar
   langa `COTE` care are.

**COMANDA DE REPORNIRE:** „Sursarea per tip a termenelor (R4, `core/test_temei_termene.py` e xfail
strict pana atunci), apoi arderea clichetului de la 126 in jos, in ordinea 1-6 de mai sus. Dupa:
`semafor.js` — griul e in afara modelului lui, iar un cabinet numai cu firme gri arata un rand verde
linistitor. Si R6: o declaratie depusa rezolva `neclar`?”

**CORECTIE la frontul de mai sus + a PATRA clasa a scanului (gasita privind fisierul, nu scanandu-l):**

`cote_tva.py` NU e nesursat. Antetul citeaza *art. 291 Cod fiscal, modificat prin Legea 141/2025, in
vigoare de la 01.08.2025*, fiecare categorie poarta `"lege": "art. 291 (2) a)"`, iar
`verificator_conformitate.py:594` il are pe `_TVA_EXCLUSE` — exclus DELIBERAT, fiindca el e modulul care
reproduce legea. Mutarea in `COTE` ar fi stricat structura injectata in promptul AI.

Deci scanul are o a patra clasa nedistinsa: **temei PREZENT, dar in PROZA, nu ca obiect `Temei`**. E
masurabila — verificatorul face deja exact asta prin `_TVA_TEMEI`. **Pasul urmator decis (20.08c):**
rafinez scanul cu clasa asta, recalculez cele 126, cobor clichetul cu falsele pozitive scoase. Abia dupa
aia lista de ardere e reala. Acelasi principiu ca masurarea inaintea fragmentelor, aplicat propriei
masuratori.

**Doua constatari in `cote_tva.py`, de reparat cu gard:**
- `potriveste_cota` — docstring-ul spune *"Daca AI indisponibil -> fallback: cota standard 21%
  (sursa='fallback'), ca sa nu blocheze fluxul"*, iar codul returneaza `_nedeterminat(...)`. A cincea
  instanta doc-contra-cod in aceeasi zi. Aici codul are dreptate si poarta rationamentul explicit ("un 21
  marcat fallback ajunge in decont exact ca unul tacit daca factura se emite oricum"), deci docstring-ul
  se corecteaza la decizia scrisa si se LEAGA — nu se inmoaie ca sa se potriveasca.
- `cote_valide()` — **zero consumatori**, cod mort. Intoarce `[21, 11, 0]` fara data; chemat pe o factura
  din iunie 2025 ar respinge 19% ca invalid. Reparatie reala = se sterge sau se face period-aware.

**Metoda e acum SCRISA:** `METODA_VERIFICARE.md` (cele trei acte, cele patru surse, precondiția-harta,
temei legal vs regula de produs, cum se construieste un instrument de masura cu formele de orbire prin
constructie, clichet vs xfail, doc-contra-cod, verde-e-o-afirmatie, ce NU acopera). Pana acum traia doar
in docstring-uri si in practica. Gardata de `core/test_metoda_vie.py`: fiecare fisier pe care metoda il
numeste trebuie sa existe, altfel metoda descrie un instrument disparut.

RAMAS deschis din turele anterioare, nemiscat tura asta: FK pe `salariu_istoric`/`pontaj` + 24 orfani pe
t001 · cele 8 CNP-uri plauzibile pe t013-t016 · `etransport_ecran.js` etTimp gri -> „—” ·
citirea celor 9 diff-uri verificator/verificat co-comise · marcarea celor 85 de teste · cele trei stari ca
fixturi · scanerul multi-firma (garda hartii citeste artefactul unei singure firme).

---

# ARHIVA — PREDARE LANT — audit tenant_001 (Panificatie Salarii Speciale SRL / S4, cabinet Prisma 1968)

## REPORNIRE (comanda exacta, gata de dat) — TURA 20.08: audit t001, 10 defecte, 4 garzi

LIVRAT (necomis la scrierea asta; poarta verde inainte de commit):
- **6 rute** care lasau un refuz motivat sa devina 500 gol -> 422 cu mesajul care exista deja
  (`bilant_api`, `factura_pdf`). Doua dintre ele gasite de GARDA, nu de mine.
- **14 mesaje publicate** rescrise in limba contabilului: nume interne in canal **4 -> 0**, fara
  diacritice **89 -> 82** (clichet cu baseline 84, burn-down declarat).
- **GET care comitea** (`GET /stat-plata` -> INSERT+commit): scos; media CM pe 6 luni se calculeaza
  acum din sursa. Poarta de stergere trecuta pe `perioada_confirmata`. Datoria din `test_datorie.py`
  corectata (cauta si in radacina, formularea nu mai afirma un fals).
- **Contrast** `.cf-galben`/`.cf-termen-galben` inapoi pe tokenul DS `#92500a` (4.02 -> 5.30).
- **`sterge_salariat`** curata tabelele-copil fara FK (`salariu_istoric`, `pontaj`).
- **`audit_tenant.py`** decide pe `severitate`, nu pe `stare` — F2 pe t001 a trecut de la ROSU fals la VERDE.
- **Vector t001** completat conform C-2/S4. Reziduul sondelor (24 `state_plata` + 2 `nir`) sters tintit.

GARZI NOI: `test_refuz_generator_422`, `test_mesaje_valueerror_publicat`, `test_get_fara_scriere`,
`test_stergere_salariat_completa`; `test_a11y_contrast_tokens` extins. Toate RED-probate din backup-copie.
Fiecare are aserțiune anti-vacuu — cea de la stergere s-a declansat chiar la nastere (schema traieste in
`tenant_template.sql` PLUS `NN_ddl_*.sql`).

**COMANDA DE REPORNIRE:** „Continua pe t001. Doua lucruri DECISE si NEIMPLEMENTATE, in ordinea asta:
(1) gardul pe FIXTURES — un fixture care contine iesire de validator nu poate exista fara verdict
(«verificata la sursa, iata temeiul» sau «bug cunoscut, iata datoria»); ala ar fi prins fixture-ul B4_5P
in ziua in care a fost scris (08.08). (2) D1 — scade cei 300 lei din pragul part-time (CF art.146(5^6) /
art.168(6^1), `structura_D112` l.3128/3157, arbitrul da 3750); D2 — Nomenclatorul 9 (20 coduri) devine
sursa unica pentru D_9 in toate cele patru straturi, XSD-ul ramane al doilea semnal; verifica intai
`caen_in_nomenclator` la arbitru, e aceeasi expunere. Odata cu D2, cele TREI etichete inversate din
`flux_concediu.js`: `02`/`03` sunt schimbate intre ele (surse de plata diferite!), `16` scrie «boala
infectocontagioasa» in loc de «unele tipuri de arsuri», `17` scrie «reducere cu 1/4» in loc de «ingrijire
pacient oncologic». Apoi: marcajul celor 85 de teste care aserteaza o constanta fiscala FARA temei
(inventar 31.07, `test_datorie.py:234`) — comentariu injectat mecanic + clichet, si in aceeasi trecere
numara cate difera de registrul `common.COTE`. Abia dupa astea, cele trei stari ca fixturi
(galben randat / vector incomplet / generator care refuza) — D2 schimba a treia, altfel o construiesti
de doua ori."

NEDECIS, pe masa lui Costin: orfanii `salariu_istoric` (24 pe t001) + FK-ul pe `salariu_istoric`/`pontaj`
(migrare pe 19 scheme, cere intai stergerea orfanilor). `reg_com`/`banca`/`iban` pe t001 raman NULL
deliberat — sunt cazurile de test care au scos refuzul de bilant si cel de D300.

---

# ARHIVA — PREDARE LANT — audit tenant_006 (Achizitii IC Neplatitor SRL / N1, cabinet Prisma 1968)

## REPORNIRE (comanda exacta, gata de dat) — TURA 20.08: I1 (patru-ochi) + I2 (checksum manual) INCHISE

LIVRAT (un singur commit, bundle I1+I2, o singura repornire):
- **I1 — patru-ochi pe cabinet solo.** Patru-ochi are DOUA axe: POLITICA (`activ`, explicita, a patronului,
  persistenta) x APLICABILITATE (`posibil`, aritmetica, live). `efectiv = activ ∧ posibil`, dintr-o SURSA
  UNICA (`coada_api.patru_ochi_stare`) consumata si de `aproba` si de `GET /eu/patru-ochi`. Defectul
  PRINCIPAL reparat = INDICATORUL MINCINOS (subbara zicea „Validarea in doi ✓" pe un cabinet cu un singur
  validator, in timp ce cardul de pe acelasi ecran zicea „De depus"). Trei stari, nu doua; bifa doar pe
  `efectiv`; suspendat = `var(--ardezie)`, fara verde.
- **I1b — FUNDATURA gasita si inchisa (corectie fata de propunerea initiala).** Formula veche a lui `posibil`
  („>=1 pregatitor + >=1 validator + >=2 oameni") devenea `true` cand un cabinet solo angaja un asistent DOAR
  cu `poate_pregati` -> cele 3 declaratii pregatite de unicul validator deveneau NEAPROBABILE DE NIMENI.
  Acum `posibil` ⇔ >=2 VALIDATORI activi. Nu se pierde nicio protectie (un om fara drept de validare nu putea
  oricum aproba nimic).
- **I1c — trecerea granitei NU e tacuta**, in trei locuri: subbara (crom persistent = STAREA), dialogul
  „Acorzi dreptul de validare lui X?" din Asistenti (= MOMENTUL, prin `patru_ochi_intra_in_vigoare`), textul
  cozii (trei variante: in vigoare / suspendat / oprit — „dezactivat" pe o politica suspendata era o a doua
  minciuna).
- **I2 — checksum VIES pe liniile manuale/D301** in `calcul_d390` (era doar pe latura din facturi). Neblocant,
  simetric cu latura auto. `salveaza_reclasificare` verificat CURAT (nu creeaza cod nou de partener).
- Reparatie reala: „cine poate aproba in acest cabinet" era intrebat in TREI locuri cu trei interogari
  proprii -> `coada_api.validatori_activi`, sursa unica.

GARZI: `core/test_patru_ochi_efectiv.py` (14), `core/test_d390_checksum_manual.py` (5),
`core/test_a11y_contrast_tokens.py` extins. RED-probate (8/14 + 2/5 pica pe HEAD; mutatii prinse pe prag,
pe notificari si pe culoare). DECIZII 20.08 (doua intrari, regula GARDATA). DS v2.60.
PROBA: `frontend_test/proba_patru_ochi.py` pe cabinetul 1968 — trei stari, capturi privite
(`po_0_inainte_*` / `po_1_suspendat_*` / `po_2_efectiv_*`), axe 0 desktop + Pixel 5 (body=393).
IGIENA DE DATE: asistentul 6248 activat TEMPORAR pentru starea 2 si restaurat exact (activ=f, competente
f/f/f) — verificat in proba. Flagul `patru_ochi_activ` pe 1968 = ON (vezi mai jos).

IGIENA DE DATE (facuta, 20.08 dupa reparatie): flagul patru_ochi_activ pe cabinetul 1968 a fost STINS
(era ON doar ca proba vizibila a defectului). Cabinetul 1968 e din nou in starea lui naturala: un singur
validator (patronul), politica oprita, cele 3 declaratii din coada raman la_senior si depozabile de el.
Asistentul 6248 restaurat exact (activ=f, competente f/f/f) dupa starea 2 a probei. Ramura „suspendat" a
indicatorului ramane acoperita de gard (core/test_patru_ochi_efectiv.py) si de capturile comise, nu de o
stare lasata in baza. Ca s-o reaprinzi oricand: butonul din subbara, sau
`UPDATE public.accounting_firms SET patru_ochi_activ=true WHERE id=1968;`.

RAMAS NUMIT din I2 (nu tacut, NU e gaura de corectitudine): formularul de linie MANUALA D390
(`d390_clasificare_api.manual_adauga`) valideaza tip/tara/cod-obligatoriu/baza, dar NU da inca avertismentul
de checksum LA INTRODUCERE, asa cum face ecranul D301 din 19.08. Corectitudinea e inchisa (avertismentul apare
la generare, cu partenerul NUMIT), dar simetria „contabilul afla DEVREME, in limba lui" nu. De adaugat cand se
atinge ecranul: backend `avertisment` (5 linii, copia exacta din `d301_operatiuni_api.salveaza`) + afisarea lui
in `declaratii.js:371` (azi raspunsul e aruncat — deci fara UI ar fi cod mort).

COMANDA DE REPORNIRE (gata de dat): "Continua auditul cabinetului 1968. I1 (patru-ochi) + I2 (checksum manual
D390) = INCHISE. Reia campania colectii date valide+invalide de la urmatoarea firma din matrice: t001
(D112 erori DUK 'asigurat idAsig=4' + cod boala '91') sau t009 (D406 factura COER-T5 nereconciliata).
Instrument: audit_tenant.py <id> --user=patron@prisma-cont.test. Metoda Regula 13+14 (captura PRIVITA)."


## INCHIS — MISDIAGNOSTIC: „D394/003 perioada septembrie + cifre necorespunzatoare" (NU redeschide)

Constatarea din tura precedenta („D394 pe tenant_003 emite septembrie in loc de trimestru, plus cifre care
nu corespund") a fost investigata read-only si inchisa ca **MISDIAGNOSTIC** — codul de produs e CORECT, nu s-a
reparat nimic. Eticheta simptomului confunda CODIFICAREA ANAF cu o eroare de perioada. Verificat la sursa:

1. **Codificarea ANAF.** OPANAF 2194/2025 lit. c: campul `luna` pentru declarantul trimestrial = ultima luna a
   trimestrului (01 pt lunar; **03 pt T1, 06 pt T2, 09 pt T3, 12 pt T4**; 12 si pt anual). Deci `luna=09` pe T3 e
   marcajul corect al trimestrului III, NU „septembrie" ca luna izolata. Wizard-ul trimite `trim`; conversia
   `declaratii_api.py` face `luna = trim * 3` → ancora canonica 3/6/9/12.
2. **Fereastra reala T3.** `fereastra_tva(perioada, "T")` returneaza empiric pe T3 intervalul
   **[2026-07-01, 2026-10-01)** — TRIMESTRUL INTREG (3 luni), nu doar luna-ancora. Iulie si august NU se pierd.
   Decupleaza ETICHETA (luna pusa in XML = 9) de FEREASTRA DE DATE (tot trimestrul) — vezi docstring `fereastra_tva`.
3. **Cifrele.** „Cifrele necorespunzatoare" = singura factura din **august** a lui 003, culeasa corect de fereastra T3:
   bazaL 3500 (11%) + 2400 (21%) = **5900 baza**, TVA 889 → **5900 + 889 = 6789** = totalul facturii din august.
   Nu lipseste si nu se dubleaza nimic; cifrele corespund exact facturii, doar ca nu au fost recunoscute la triaj.

**GARD care ingheata corectitudinea:** `core/test_d394_trimestrial_perioada.py` (4 teste) — freeze pe AMBELE laturi:
eticheta (`trim*3 ∈ {3,6,9,12}`) + fereastra (`fereastra_tva(·,"T")` = trimestrul intreg, augustul inauntru,
span 3 luni, orice luna din trimestru → aceeasi fereastra). RED-probat: mutand fereastra T la doar luna-ancora
(regresia care ar pierde iulie/august) → 3 teste pica. Daca simptomul reapare, citeste intai gardul si punctele
1–3 de mai sus INAINTE de a-l reclasa ca bug.


## REPORNIRE (comanda exacta, gata de dat) — TURA 18.08(b): straturi import 006 provocate + corectate

STARE (tura curenta, 3 comituri): straturile de import ale campaniei "colectii valide+invalide" (F5/Regula 14.4)
provocate INDIVIDUAL pe tenant_006, cap-coada cu Playwright (captura privita). LIVRAT:
- **firme** (fd224d2): intrarea ne-CUI (typo/antet, ex. "ABC") disparea TACUT inainte de ANAF (Regula 4 - drop
  tacut) -> anaf_api.separa_cui() intoarce (curatate, ignorate); ruta /migrare/valideaza intoarce "ignorate";
  banner VIZIBIL .mig-avert (role=status, nu title-only). Gard RED (7 aserții) + Playwright (axe 0, mobil 393).
- **plan_conturi** (a651fec): adaugarea manuala facea INSERT ON CONFLICT DO UPDATE -> simbol duplicat (101)
  REDENUMEA TACUT contul OMFP standard "Capital". Calea bulk (solduri_api) folosea corect DO NOTHING. -> refuz
  409 in limba contabilului ("Contul X exista deja: «denumire»…"), cont neatins. Gard RED + Playwright (axe 0, mobil 393).
- **solduri_parteneri**: MESAJ conform by-design (poarta Q5 preview=salvare: per-rand DE CE nu se salveaza + Salvare
  blocata) - probat live cu conturi ne-partener (5121/101 -> "nu tine solduri pe parteneri (doar 4111,401,409,419)").
  Fara fix de mesaj.
- **a11y contrast P3** (2bdac14): axe pe preview parteneri a scos .mig-sold-cont #347ab8 = 3.86 < 4.5 pe panoul #e9edf3
  (fix-ul Control fiscal asumase "migrare = pe alb", gresit) -> baza .mig-sold-cont -> #2f6fa6 (toate instantele,
  tiparul P3) + gard ancorat la regula de BAZA. Re-probat: axe color-contrast 0 pe preview parteneri.
- **vector_fiscal** (73522f5): provocat pe tenant_001 (firma FARA vector) - platitor TVA fara periodicitate decont ->
  salvare RESPINSA (400, nicio scriere), mesaj corect DAR grupul vinovat nu era marcat (Regula 14.4 pct.4). Fix:
  salveaza() intoarce 'camp' -> ruta expune erori_campuri -> migrare.js marcheaza grupul (.camp-invalid + aria-invalid).
  Gard RED (5) + Playwright (contur rosu privit, axe 0). CELE 4 STRATURI DE IMPORT 006 = INCHISE.
- **plan_conturi field-marking** (ebd05c6): ultima datorie de field-marking DIN perimetru inchisa (asterisc
  obligativitate inainte de buton + campul gol marcat). §5 (ce ramane) pe straturile de import 006 = GOL de
  neverificat/nereparat IN perimetru; ce ramane e DOAR tiparul in ALTE formulare neatinse (pattern app-wide,
  nu datoria firmei curente). Regula noua (Costin 19.08): la finalizarea unei firme, §5 gol de perimetru.
- **DS + F6 (mobil/axe)** (b94fcf2 + 6683623): DS citit si citat. cap.6 pct.4 (fail-fast INTERZIS pe formular
  multi-camp) a scos ca vector marca doar PRIMUL camp lipsa -> acum COLECTEAZA toate campurile lipsa si le
  marcheaza odata (b94fcf2). Changelog DESIGN_SYSTEM v2.56/v2.57 (Regula 6). F6: axe-pe-mobil (Pixel 5) pe
  firme/vector/plan/parteneri = 0 DUPA fix .fereastra-corp `tabindex=0` (axe scrollable-region-focusable,
  WCAG 2.1.1, 6683623); tinte >=24 AA, title-unic 0, fara h-scroll (393). §5 perimetru import 006 = GOL
  (F6 + DS incluse). Lectie infra (OUT-of-perimeter, nu datoria firmei): axe_scan e desktop-only + mobil_scan
  nu ruleaza axe -> de adaugat un pas axe-pe-mobil in infra vizuala.

COMANDA DE REPORNIRE (gata de dat): "Cele 4 straturi de import ale tenant_006 (firme/plan_conturi/solduri_parteneri/
vector_fiscal) + a11y contrast = INCHISE (fd224d2, a651fec, 2bdac14, 73522f5). Continua campania colectii valide+invalide
la URMATOAREA firma din matricea 1968: t001 (Panificatie Salarii Speciale - D112 erori DUK 'asigurat idAsig=4' + cod
boala '91' pe concediu medical) sau t009 (D406 factura COER-T5 nereconciliata: antet net/tva != suma liniilor).
Instrument: audit_tenant.py <id> --user=patron@prisma-cont.test (F2 DUK + F7 semafor + F6 axe/mobil). Metoda Regula 13+14
(captura privita). Cluster RAMAS app-wide: field-level marking in ALTE formulare cu grupuri de butoane/selecturi care nu
folosesc erori_campuri - de maturat form cu form (mecanism: api.js marcheazaCampInvalid + detail.erori_campuri)."


## REPORNIRE (comanda exacta, gata de dat) — CAMPANIE ACTIVA: colectii date valide+invalide per firma + corectitudine (F5)
Costin (18.08): pentru FIECARE firma din matrice (cabinet 1968: t001-t012 + t017; + demo 8396-99) construieste o
colectie de date VALIDE (genereaza toate declaratiile aplicabile DUK-valid) + una INVALIDE (provoaca fiecare blocaj/
refuz/camp obligatoriu). La cele INVALIDE conteaza ca MESAJUL de pe ecran sa-l ajute pe contabil sa inteleaga si sa
remedieze intrarea - "nu facem economie de vorbe" (F5/Regula 14.4: ce lipseste + unde se corecteaza + consecinta;
FARA nume interne; motiv VIZIBIL nu title-only; obligativitate inainte de buton). NU vanez defect/firma - verific
CORECTITUDINEA aplicatiei, holistic. Instrument: frontend_test/audit_tenant.py <id> --user=<email> (F2 DUK + F7
semafor + F6 axe/mobil; F3/F5 manuale). Metoda = MODEL_AUDIT_TENANT.md (8 fatete, extensibile). Fiecare firma cap-
coada -> rand in ISTORIC_TENANTI.md; roșurile de corectitudine reparate cu tiparul P3 (app-wide) + gard RED-probat.
Criteriu "gata de productie" (AGREAT Costin): fiecare functionalitate a trecut fatetele aplicabile pe >=1 firma cu
date valide+invalide, roșurile de corectitudine reparate, restul documentat ca decizie de produs (NU "zero bug").

COMANDA DE REPORNIRE (gata de dat): "Continua campania colectii date valide+invalide + corectitudine. Instrument:
audit_tenant.py pe matricea 1968 (--user=patron@prisma-cont.test). Reia de la 006. PRIORITATI din re-testul 006 (18.08):
(A) F5 - mesajul D301 'nr_doc gol' EXPUNE numele intern -> rescrie in limba contabilului ('Operatiunea N: completeaza
numarul documentului'); cauta TIPARUL 'nume intern in paranteza' in TOATE mesajele de generare (grep pe erori_generare/
valideaza) si repara app-wide. (B) a11y APP-WIDE (P3, iesit pe 006 SI ALFA): campuri fara eticheta pe fa-stocuri(4)/
fa-registratura(2)/fa-banca(1)/fa-rapoarte(1); contrast pe fa-control(2)/fa-etransport(1)/fa-centrecost(2); mobil
tinte<24px pe fa-casa/fa-banca - reparate cu tiparul + gard test_a11y_touch_target/contrast_tokens extins. (C) apoi
colectii INVALIDE per firma (CSV-uri bad per strat + valori la limita), provocate cu F5, mesaj util. Toate: poarta
verde + rand ISTORIC_TENANTI."

STARE MATRICE (harta F2/F7 pe cabinet 1968, 18.08): DEFECTE REALE = t001 (D112 erori DUK 'asigurat idAsig=4' + cod
boala '91' pe concediu medical), t006 (D301 operatiune fara nr_doc), t009 (D406 factura COER-T5 nereconciliata:
antet net/tva != suma liniilor). SUB-EXERCITATE (fara date de validat) = t005/t011/t012 (au nevoie de DATE, nu de
stergere - regimuri valoroase: profit-trim/startup-partial/tranzitie). REFUZ CORECT by-design (D100 pe zero) =
t002/t009/t017. CURAT F2 = t004/t007/t008/t010. Concluzie firme (agreat): cele 13 ≈ set minim de REGIMURI; nu se
reduc - se umplu cu date. audit_tenant.py: --user mint server-side + F6 + XSD pre-check + user sanitizat (18.08).


## REPORNIRE (comanda exacta, gata de dat) — CAMPANIE: 6 formulare manuale pt declaratiile _DOAR_API
Costin a cerut formulare de introducere manuala pentru 6 declaratii (din cele 41 _DOAR_API care au generator+DUK dar
n-au ecran), in ordinea frecventei la un cabinet SRL: **d710, d311, d307, d107, d177, d207**. Cap-coada fiecare:
(1) parametri cititi din SEMNATURA generatorului (nu presupusi); (2) formular UI pe modelul panoului D301 (clase DS
cap.6, ZERO clase noi, regula 0 citata in cap; identitate intre situatii similare); (3) scos din declaratii_api._DOAR_API
-> apare in GET /declaratii/tipuri; (4) traseu live probat pe firma demo: formular->generare->XML->DUK valid, CAPTURA
PRIVITA. GARDA per declaratie: formular gol nu produce declaratie (refuz backend cu mesaj de CONTABIL, nu nume de camp),
mutatie-probata RED. CSV FUNCTIONALITATI (Stare AMANAT->LIVE) odata cu codul; test_registru_functionalitati verde.

CAMPANIE INCHISA (18.08.2026): GATA toate 6 - d710+d311+d307+d107+d177+d207. Fiecare LIVE, scos din _DOAR_API,
formular UI + gard formular-gol (mesaj de contabil) + DUK valid + Playwright (axe 0/0 + mobil 393). Commit d207: 89c3a26.

GATA (18.08.2026, commit 0392b3b): (1) axe region/landmarks app-wide -> 0 - fix STRUCTURAL in navigator.js
(<header class="bara-antet"> banner peste bara+subbara+bara3; role="dialog"+aria-modal pe ferestre; role="status"
pe toast); scan_region_all.py = 0 pe dashboard + 5 ECRANE; gard core/test_a11y_landmarks.py (RED-probat din
backup-copie). (2) D406 731-738 verificat la sursa (nomenclatorul ANAF) = excludere CORECTA din norma A
(731-738 sunt in planul ONG, nu in bal_soc_com); gard test_conturi_ong_731_738_norma_specifica (ambele laturi).

GATA (18.08.2026, commit dc1ee22): (3) mobil/touch-target AA 2.5.8 pe cele 5 ecrane -> 0 tinte <24px
(.fir-veriga 19->24, .ajutor-btn 20->24, flex-shrink:0 pe controale copil-direct in .fer-larg; bug #pc-cauta
40->20px reparat); gard test_a11y_touch_target. (4) IMPORT: tiparul "motiv de refuz livrat DOAR prin title"
(pierdut pe touch) reparat pe 4 straturi (salariati/asociati CNP, mijloace fixe, istoric) -> motiv VIZIBIL
(span.mig-motiv); probat live tenant_006 (salariati bad_sal.csv); gard test_import_motiv_vizibil.

COMANDA DE REPORNIRE (SUPERSEDAT de blocul REPORNIRE TURA 18.08(b) de la inceputul fisierului): din cele 4 straturi
de import, firme/plan_conturi/solduri_parteneri/contrast = LIVRATE tura asta (fd224d2, a651fec, 2bdac14). RAMAS pe
straturi = DOAR vector_fiscal (refuz camp obligatoriu lipsa pe o firma FARA vector complet)."

**GATA: d710** - formular "Obligatii corectate" (cod 121 micro/103 profit, suma initiala/corecta, cota la micro),
obligatii in memorie -> body, refuz-pe-gol, gard test_d710_formular, CSV F192->LIVE. Model: declaratii.js::randeazaFormularD710.

**GATA: d311** (TVA cod anulat, commit aceasta tura) - PANOU-CAMP (nu lista): data anularii + motiv (oficiu/cerere) +
3 situatii oficiale baze/TVA (livrari / achizitii cu taxare inversa / livrari cu TVA la incasare exigibila dupa anulare),
subtotaluri+total CALCULATE, total de plata LIVE la tastare. Model complet: declaratii.js::randeazaFormularD311 +
_d311Manual + S.d311 (in memorie) + hook-urile pas2 (S.tip==="d311", DOUA locuri: eroare + succes, indentare diferita).
Backend: erori_generare d311.py rescrise in limba contabilului (fara Data_A/d_anul1/OB_51); test_d311 re-ancorat;
gard core/test_d311_formular.py (RED-probat prin sed pe mesaj). Scos din _DOAR_API (ATENTIE: nu sterge si vecinul -
am scos din greseala d307, prins de test_live_accesibil). CSV F207->LIVE + login.js GRUPE_FUNC regenerat
(`python3 genereaza_grupe_functii.py --scrie`, ALTFEL verificatorul RESPINGE commitul: CSV live-count != pagina).
Proba: frontend_test/proba_d311_formular.py (ALFA MICRO 8396; declarant setat via API /firma-profil/date; DUK valid,
axe 0, mobil Pixel5). CUI-uri demo sintetice (301111003) TREC DUK.

**GATA: d307** (ajustare/corectie TVA, commit aceasta tura) - LISTA de operatiuni (model d710): fiecare operatiune tip
(A=transfer active/cedent, L=leasing/finantator, C=anulare cod TVA/beneficiar) + cod fiscal + denumire operator + TVA
(poate fi <=0 la regularizare); tvaA/L/C + total de ajustare CALCULATE (total afisat, recalculat la randare). Model:
declaratii.js::randeazaFormularD307 + _d307Manual + S.d307 (operatiuni in memorie) + hook pas2 (S.tip==="d307", DOUA locuri).
Backend: erori_generare d307.py rescrise in limba contabilului; valideaza_cerere prietenos; gard core/test_d307_formular.py
(RED-probat sed pe denO). Scos DOAR d307 din _DOAR_API. CSV F217->LIVE + GRUPE_FUNC regenerat + registre IN ACELASI commit
(lectia d311). Proba: frontend_test/proba_d307_formular.py (ALFA MICRO, 2 operatiuni tip A+C cu TVA negativ, DUK valid, axe 0, mobil body=393).

**GATA: d107** (informativa sponsorizari/mecenat/burse, commit aceasta tura) - LISTA de beneficiari (model d307):
fiecare beneficiar cu denumire + cod fiscal (CUI/CNP) + adresa + trei sume (acordata Val1 / reportata Val2 / dedusa Val3);
TVal1/TVal2/TVal3 + totalPlata_A (suma de control) CALCULATE si afisate (coincid cu serverul). Anexa neindividualizati
(entit1) intr-un `<details>` colapsat, mini-lista conditionata de Val2_NI>0 (regula validatorului). Model complet:
declaratii.js::randeazaFormularD107 + _d107Manual + S.d107 (in memorie) + hook pas2 (S.tip==="d107", DOUA locuri:
div placeholder + render, indentari diferite 6/4 si 4/2 sp) + id #d107-totaluri. Backend: erori_generare d107.py rescrise
in limba contabilului + valideaza_cerere d107 rescris (NU mai expune `manual.beneficiari` - prins de proba Playwright,
nu de unit); test_d107 re-ancorat; gard core/test_d107_formular.py (RED-probat sed pe Val2_NI). Scos DOAR d107 din
_DOAR_API. CSV F211->LIVE + GRUPE_FUNC regenerat (148) + registre IN ACELASI commit. Proba:
frontend_test/proba_d107_formular.py (ALFA MICRO an 2024, 2 beneficiari, DUK valid, axe 0, mobil body=393).

**GATA: d177** (redirectionare impozit profit -> ONG/cult, commit aceasta tura) - cea mai bogata forma: ANTET (plafoane
suma_max/ant/rest + perioada fiscala) + LISTA de beneficiari, fiecare cu tip (1 cult / 2 alte / 3 mecenat / 5 UNICEF;
4 nepermis), cod fiscal (CUI, CNP la mecenat - eticheta se schimba), denumire, IBAN, suma, acord, contract (obligatoriu
la tip<5, ascuns la UNICEF). Total alocat vs. ramas afisat; suma de control = 0. Model complet: declaratii.js::
randeazaFormularD177 + _d177Manual + _D177_TIPB + S.d177 (in memorie) + hook pas2 (DOUA locuri) + id #d177-totaluri.
Backend: erori_generare + valideaza_cerere rescrise (fara tipB/cuiB/sumaRest/etc); test_d177 re-ancorat; gard
core/test_d177_formular.py (RED-probat sed pe sumaRest). BUG REAL reparat: luna XML derivata din dataSfarsit (dispatch
trimitea luna=6 -> R4.1 respins), aserție regresie in gard. Scos DOAR d177 din _DOAR_API. CSV F210->LIVE + GRUPE_FUNC
(149) + registre IN ACELASI commit. Proba: frontend_test/proba_d177_formular.py (ALFA MICRO an 2025, DUK valid, axe 0, mobil body=393).

**GATA: d207** (LIVRAT 18.08, commit 89c3a26 - ULTIMA, CAMPANIA INCHISA; DUK valid + axe 0/0 + mobil body=393;
nomenclator tip venit SURSAT din structura_D207_2025 cap.III - 25 coduri, impozabile+scutite; suma control 10801
JS=server; scutit->impozit dezactivat+0. LECTIE: RED-proof pe fisier needitat-committed NU cu git checkout -
sterge si editarile necommitate; re-aplica editarea sau foloseste o copie). Istoric metoda: informativa nerezidenti, ULTIMA din
campanie, MANUALA). Citeste core/d207.py (semnatura genereaza + calcul + erori_generare + build_xml) si valideaza_cerere
d207 (linia "d207 cere `manual.beneficiari` (lista de beneficiari nerezidenți)" - de rescris in limba contabilului).
Model LISTA de beneficiari nerezidenti, grupati pe tip_venit (verifica structura la sursa in anaf_surse). DE FACUT identic
cu d177/d107: (1) mesaje contabil in erori_generare SI valideaza_cerere; (2) formular-lista + hook pas2 AMBELE locuri;
(3) scoate DOAR d207 din _DOAR_API; (4) ajutor d207 (F-number in CSV, rand existent); (5) gard test_d207_formular RED;
(6) CSV ->LIVE + GRUPE_FUNC + registre IN ACELASI commit; (7) proba Playwright ALFA MICRO -> DUK valid + axe + mobil.
RESTART OBLIGATORIU dupa scoaterea din _DOAR_API. ATENTIE (lectia d177): ruleaza proba pe traseul REAL, cu default-urile
dispatchului - bug-urile de parametru (ex. luna/perioada) trec de unit-teste dar cad la DUK pe traseu. Cu d207 campania de 6 e INCHISA.
RESTART OBLIGATORIU dupa scoaterea din _DOAR_API (modificare backend, altfel tipul nu apare in selectorul live - prins la d307).

## REPORNIRE (audit tenant_006 - context anterior)
Continua auditul cap-coada tenant_006 (N1, neplatitor micro cu achizitii intracomunitare; id 4841, schema tenant_006,
CUI 95451848). Livrat tura asta: fix de coerenta semafor (existenta_firma_an numara achizitiile IC + casa/banca),
commit 288f886. Livrat si: D100 pe fapt de venituri (b196943), a11y contrast Control fiscal + import blockages
verificate. Fronturi RAMASE: field-level error marking (front 3, formulare SAVE), D390 ignora d301 (front 2, decizie
ceruta), axe "region"/landmarks app-wide, D406 conturi 731-738. Metoda Regula 13+14: captura PRIVITA + axe/mobil pe
fiecare ecran atins, REPARAND, gard RED-probat prin
rulare; DS inainte de cod UI; versioneaza_assets --scrie dupa editare static/js|css; commit pe iconta_nou = poarta
~8min + post-commit publica+restart. Probe Playwright: helper ~/probe_t006/wt006.py (deschide_firma -> "Achizitii IC
Neplatitor"); scripturi in ~/probe_t006 (server). Env: `set -a && . ~/.iconta/db.env && . ~/.iconta/api_keys.env`.

## FOUR-WAY (de confirmat de urmatoarea tura)
Confirmat de raportul acestei ture (four-way pe commitul a11y). Comituri tura tenant_006: 288f886 (existenta_firma_an),
50c3ebf (registre+predare), b196943 (D100 pe fapt de venituri), c55308f (predare), + commitul a11y contrast +
import-verificat al acestei ture. Poarta verde pe fiecare, verificator 0.

## INCHIS tura asta — CLUSTER A11Y CONTRAST pe Control fiscal (LIVRAT)
17 violari color-contrast pe panoul #e9edf3, reduse la 2 tokeni, reparate SCOPED: `.cf-rand-decl/.cf-incr-cap
.mig-sold-cont` (coduri declaratii) #347ab8->#2f6fa6 (4.53); `.cf-incr-temei` (sub-text verdicte) #9aa3b2->#5c6675
(4.95). Token global neatins. axe contrast=0 dupa (captura privita, identitate pastrata). Gard test_a11y_contrast_tokens
extins (mutatie-probat). DS v2.43. versioneaza_assets --scrie. Import blockages verificate CURAT (salariati CNP /
solduri dezechilibru = model). RAMAS a11y: axe "region" (landmark) 8-19 noduri app-wide (moderat, structural);
D406 avertisment conturi 731-738 excluse din norma A (neverificat la sursa).

## INCHIS tura asta — FRONT 2 (D390<->d301) rezolvat pe corectitudine
INVESTIGAT: D390 SE POATE produce manual - UI-ul de clasificare intracomunitara are Tip A (achizitie bunuri IC cu
tara + cod TVA furnizor). Probat: linie manuala cod A -> d390.genereaza produce XML valid (nr_opi=1); DUK valideaza
algoritmul codului TVA. Deci NU e blocaj de corectitudine. FIX LIVRAT: refuzul D390 "pe zero" semnaleaza acum
operatiunile din d301_operatiuni si indruma spre adaugarea manuala (Tip A), in loc de mesajul generic fals "verifica
facturile UE". Mirror al refuzului D301<->facturi. Gard test_d390_d301_semnal (mutatie-probat).
RAMAS = DECIZIE (recomandare executor: NU construi): auto-derivarea d301->D390 cod A ar cere migrare DB (coloane
partener cod TVA+tara pe d301_operatiuni) + camp in ecranul D301, pentru un caz de margine (art.317). Calea manuala +
avertismentul acopera corect fluxul.

## INCHIS tura asta — D100 micro pe fapt de venituri (commit b196943)
Semaforul arata D100 micro restanta ignorand baza de venituri, DAR D100 pe zero e structural invalid la DUK
(generatorul refuza) -> restanta falsa. Reparat: d100_fapt (simetric d390_fapt/d112_fapt) gateaza D100 pe baza de
venituri; trimestru inchis fara venituri -> "nu se datoreaza", nu restanta. tenant_006 (achizitie IC, fara venituri):
D100 T1/T2 -> "Nu se datoreaza" (captura privita); restante ramase D406 T1/T2 + D301 iun (toate genereaza DUK-valid).
tenant_003 (venituri 0) corectat identic; tenant_002 T1 (are venituri) pastrat. Gard RED(mutatie)->GREEN test_d100_fapt.

## INCHIS tura asta — FIELD-LEVEL ERROR MARKING (front 3, LIVRAT)
eroareCamp (api.js) ancora mesajul rosu langa camp DAR nu marca inputul (fara contur). Reparat app-wide (7 ecrane):
eroareCamp adauga `.camp-invalid` + aria-invalid, curataEroriCamp o scoate la corectare; contur rosu #a3231c + glow.
Capcana: bordura globala `!important` (contrast_ferestre_v1, specificitate 0,6,1) - overrideul reproduce selectorul +
`.camp-invalid` (0,7,1). Captura privita Date firma (2 campuri goale -> contur rosu + mesaj, dispar la corectare).
Gard test_fieldmark.py mutatie-probat. DS v2.44.

## INCHIS tura asta — AUTO-DERIVARE d301->D390 cod A/S (CONSTRUITA, decizia Costin)
Costin a cerut construirea (peste recomandarea executorului). Livrat: migrare DB (furnizor pe d301_operatiuni, 19/19
scheme) + ecran D301 cu 3 campuri furnizor + indicator grila + generator d390.operatiuni_din_d301 (tip 1/3->A, 5->S;
2/4 excluse) + reconciliere a-doua-cale _pull_d301. Proba: tenant_006 op cu furnizor DE -> D390 auto-derivat DUK VALID
(cod A, baza 52261); captura privita ecran D301. Gard mutatie-probat (cele doua cai coincid). DS v2.45.
tip 3 (accizabile) -> cod A VERIFICAT la sursa (OPANAF 394/2017 anexa 2: cod A = achizitii IC de bunuri, fara
excludere accizabile) + DUK (bazaA); tip 5 -> cod S DUK (bazaS). tip 4 (art.307 alin.(3)(5)(6): gaz/energie +
bunuri din regim suspensiv + taxare inversa locala) VERIFICAT la sursa (CF art.307) = NEintracomunitar -> exclus
din D390 CORECT (serviciile IC art.307(2) = tip 5). Rafinare: achizitii_d301 numara doar tip 1/3/5 fara tara;
grila D301 clarifica tip 2/4 ("nu intra in D390 — ..."). Toate cele 5 tipuri D301 verificate la sursa.
Mis-clasificare: tip 4 cu cod TVA furnizor -> indiciu soft "poate e serviciu IC -> foloseste tip 5 (D390 cod S)"
(flag d390_posibil_serviciu), ca un serviciu IC ratacit pe tip 4 sa nu ramana absent din D390. Fals-pozitivul
benign (gaz/energie alin.3/5 cu furnizor inregistrat) -> buton "confirma (nu e serviciu)" (coloana
d390_confirmat_local + ruta PUT confirma-local) stinge indiciul reversibil. Confirmarea PERSISTA per-furnizor
(tara+cod): un furnizor confirmat pe orice operatiune stinge indiciul si pe viitoarele lui (alta luna),
marcate "✓ furnizor confirmat local" (derivat din confirmarile existente, fara tabel nou).

## RAMAS deschis (fronturi pt urmatoarea tura)
- [INCHIS 18.08 commit 0392b3b] axe region/landmarks app-wide -> 0 (fix structural navigator.js + gard test_a11y_landmarks).
- [INCHIS 18.08 commit 0392b3b] D406 731-738: verificat la sursa = excludere CORECTA din norma A (sunt in planul ONG); gard intarit.
- [PARTIAL 18.08 commit dc1ee22] Import: reparat tiparul motiv-title-only pe 4 straturi (salariati/asociati/mijloace/istoric)
  -> motiv vizibil, probat live salariati. RAMAS de provocat individual: firme (CUI ANAF), vector_fiscal,
  solduri_parteneri (cont nepartener/CUI), plan_conturi (adauga cont gol/duplicat).
- [INCHIS 18.08 commit dc1ee22] Vizual/mobil (Pixel5): 5 ecrane (import mf, vector, plan conturi, stat plata, declaratii)
  -> 0 tinte <24px (AA 2.5.8), fara revarsare/hover-loss. RAMAS: casa/banca, facturi, produse neanalizate pe telefon.

## LIVRAT (tura asta, commit 288f886)
existenta_firma_an (control_incrucisat.py) numara acum orice operatiune datata: d301_operatiuni (achizitii IC),
casa_operatiuni, extras_linii, bonuri, chitante, mijloace_fixe; nomenclatoare + solduri initiale EXCLUSE. Repara
contradictia de pe semafor (restanta D301 "operatiuni IC iun 2026" vs "nu pot demonstra ca firma era activa in 2026").
tenant_006 acum consistent cu tenant_002/003 (micro): D100/D406 2026 T1+T2 restante concrete; 2025 ramane necunoscut.
Gard RED->GREEN core/test_existenta_activitate.py (schema temporara, 4 teste). D301 verificat end-to-end: DUK valid,
cifre corecte (baza 52261, tva 10975 @21%, total 63236), avertisment art.317 (pers_inreg=1). Probe vizuale privite:
dashboard, import (10 straturi), declaratii (selector), Control fiscal (inainte+dupa), Vector fiscal (reflecta
micro/neplatitor/IC=Da), Date firma (art.317 editabil=nu). Declaratii la XML+DUK: D301 valid, D406 valid (68895B),
D101/D112 genereaza gol, D205/D390 refuza pe gol. D100 pe zero (semafor restanta vs generator refuza) REPARAT tura asta
(vezi INCHIS mai jos).
