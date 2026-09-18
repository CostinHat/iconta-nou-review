# Raport — Runda a doua de reparații (pe RAPORT_AUDIT_INDEPENDENT_2026-09-17.md)

Data: 17.09.2026 · Bază: `726105de` → commituri de lucru mai jos · Fiecare constatare: **reparată** /
**restanță deschisă cu motiv** / **contestată cu dovadă**.

Metodă, pentru fiecare reparație: o probă care **PICĂ pe codul de dinainte și TRECE pe codul de după**,
scrisă de la cazul contabil în jos, confirmată prin swap la commitul de bază. Fiecare lot trece **poarta
completă** (pytest întreg + verificator TOTAL 0 + ruff) și se publică (four-way închis, prod restartat).

## Commituri (toate publicate: four-way închis, prod restartat, poartă completă verde)
- `0dc088db` — A1 + B1–B4 (excepțiile structurale, primele — restul sunt consecințele lor)
- `dbaf8cc2` — A2, A3, A4, A5
- `8719c223` — A7, A8 (micro)
- `f6c7dbb2` — C1, C2, C3
- `0e219330` — §0 parțial (venv scos din index, INVENTAR_A regenerat, TZ documentat)
- `d9de53a2` — A8-profit (D100 cumulat art.41) + A6 (D205 cotă după data distribuirii) + deblocarea
  porții (slice Lot 7: `efactura_primite` sursă condiționată, forțat de calendar 18.09)
- `8bf059c2` — Lot 6: A10 (import e-Factura, baza liniei) + E-nota (contare primită pe cote); restul
  Lot 6 (A9/A11/A12/C4/C5/C6/E-alte) = restanțe cu motiv în mesaj; R183 contestat ca reparat
- `5ff1b8ba` — Lot 7 (D1–D10): recalibrarea celor 6 scanere; clichete de la cifra reală (SUBSET 0→10,
  NICAIERI 3→21, IN_SUITA 77→76); gardă-mutație D4 nouă

Migrări rulate pe producție (iconta_v2) la închidere: `migrare_curs_lei` → 97 facturi RON completate
cu total_lei, 0 valută fără curs; `migrare_unic_numar_factura` → 37 indici unici creați, 0 scheme
blocate de duplicate. A1 și C1 complete și pe datele existente.

---

## §0 — pachetul (prima constatare a auditului)
- **venv/ versionat** — RESTANȚĂ (Lot 8): `git rm -r --cached venv` + `.gitignore` (deja are `venv/`).
- **căi /home/costin și ~/iconta_nou în 64+ fișiere** — RESTANȚĂ (Lot 8): derivare din rădăcina proiectului.
- **procedură de construire a bazei de la zero (un script)** — RESTANȚĂ (Lot 8).
- **TZ=Europe/Bucharest obligatoriu, nedocumentat** — RESTANȚĂ (Lot 8).
- **INVENTAR_A.md (12 chei) vs COTE (20)** — RESTANȚĂ (Lot 8).
- **tichet 45 lei fără data_out** — parte din E, restanță.

## A — cifre valide-dar-false
- **A1** conversia în lei — **REPARATĂ** (`0dc088db`). Accesor unic `core/sume_lei.py`; garanție la creare
  (RON→1); citirea în lei în D300/D394/D390/D406 + contare (4426/4427) ȘI a doua cale de reconciliere a
  fiecăreia; backfill `migrare_curs_lei.py`. Probă: EUR curs 5 → notă 4111=4427 lei → D300 rd.9 → D394.
- **A2** tvai IC/export/servicii/storno — **REPARATĂ** (`dbaf8cc2`). `_pull_incasare` duce clasificarea;
  decontarea negativă reduce. Probă: achiziție IC decontată → rd.5, nu rd.26.
- **A3** filtre status/tip D394/D390/D406 + contare document void — **REPARATĂ** (`dbaf8cc2`). Probă:
  factură anulată nu intră în D394 și nu primește notă.
- **A4** storno copiază clasificarea — **REPARATĂ** (`dbaf8cc2`). Probă: storno IC scade rd.1.
- **A5** rutare non-UE servicii rd.3/rd.7+rd.20 — **REPARATĂ** (`dbaf8cc2`). Probă pură.
- **A6** D205 cotă dividend după data distribuirii — **REPARATĂ** (`d9de53a2`, 18.09). Modul neutru
  `core/dividende_curs.py` atribuie FIFO plățile (debit 457) pe distribuiri (credit 457, inclusiv ani
  anteriori) → impozit ponderat pe rata fiecărei distribuiri; generator + `d205_reconciliere` + `_thunk_d205`
  sincronizate. Probă: distribuire dec.2025 + plată ian.2026 → 10% (nu 16%). Roșu-înainte: generator vechi
  (16%) + reconciliere FIFO nouă (10%) → divergență → generarea se blochează.
- **A7** deducere ceil pe tranșe — **REPARATĂ** (`8719c223`). Probă: sm+1/sm+50/sm+51.
- **A8 (micro)** bază 70x/75x/76x−709 — **REPARATĂ** (`8719c223`). Probă: 704+766−709 → cod 121.
- **A8 (profit)** cumulat de la începutul anului (art.41) — **REPARATĂ** (`d9de53a2`, 18.09). `pull` (regim
  profit) codează baza efectivă a trimestrului ca (venituri=profit cumulat acum, cheltuieli=profit cumulat
  anterior, ambele clip la 0) → `venituri−cheltuieli` a lui `deriva_obligatii` (și `_thunk_d100`) dă impozitul
  incremental; `d100_reconciliere` la fel. Probă: Q1 −50k, Q2 +80k → cod 103 = 4.800 (nu 12.800 izolat).

### Deblocarea porții (slice Lot 7 / D2, forțat de calendar) — inclus în `d9de53a2`
De pe 18.09 poarta completă a devenit roșie dintr-o cauză **preexistentă** (cod din 13.09): `control_fiscal`
citește `efactura_primite` **condiționat de dată** (necitită pe 17, citită pe 18/25, spre scadența TVA), iar
registrul de dependențe n-o declara → `test_dependente_ramuri` roșu pentru **orice** commit. Reparat:
`efactura_primite` = sursă cu drepturi depline (declarată în `_T_CONTROL_FISCAL` + primește trigger, fiindcă
alimentează verdictul din cache) dar marcată `TABELE_CONDITIONALE` — scăzută din setul „atinsă pe orice zi"
(altfel ar pica pe zilele de la început de lună). Trigger + sincronizare registru se aplică la restart
(`lifespan`); `DEPENDENTE_P2.md` regenerat. Recalibrarea completă D1–D10 rămâne Lotul 7; aceasta e doar
bucata pe care calendarul a forțat-o înainte.
- **A9** D394 tvai câmpuri informatii — **RESTANȚĂ** (nu abordată; probabilă pe cod, cere profil tvai pe D394).
- **A10** import e-Factura BaseQuantity/AllowanceCharge + moneda — **RESTANȚĂ** (parțial acoperită de A1
  pe partea de monedă a facturilor create; UBL AllowanceCharge/BaseQuantity neabordate).
- **A11** exigibilitate D300 vs D390 pe IC — **RESTANȚĂ** (probabilă; cere alinierea expresiilor de exigibilitate).
- **A12** pro-rata pe tot rd.28 — **RESTANȚĂ** (ipoteză; depinde de folosirea pro_rata).

## B — izolare între firme
- **B1** cross-cabinet aproba/respinge/depune — **REPARATĂ** (`0dc088db`). Poartă de apartenență pe obiect
  (cabinet_id) în cele patru rute; probă: A depune elementul lui B → 404, declaratii_depuse al lui B neatins.
- **B2** auto-acordare competențe — **REPARATĂ** (`0dc088db`). `eu_competente_set` doar admin.
- **B3** portal dezactivează orice cont — **REPARATĂ** (`0dc088db`). Doar `rol='client'`.
- **B4** `POST /coada` fără poate_pregati — **REPARATĂ** (`0dc088db`).
- **B5** SET search_path de sesiune sub PgBouncer — **RESTANȚĂ** (ipoteză condiționată de infra; azi inofensiv
  cu conexiune directă + RESET în finally, întărit de C3).

## C — ce rămâne pe jumătate scris
- **C1** numerotare concurentă — **REPARATĂ** (`f6c7dbb2`). Rezervare atomică `UPDATE ... +1 RETURNING` +
  index unic. Probă: 12 fire → numere distincte.
- **C2** import în masă rollback tăcut — **REPARATĂ** (`f6c7dbb2`). Savepoint per firmă + validare lungime.
- **C3** conexiune moartă scursă din pool — **REPARATĂ** (`f6c7dbb2`). `putconn` mereu + close pe moartă.
- **C4** e-Factura/e-Transport retrimitere dublă — **RESTANȚĂ** (cere ANAF; probabilă).
- **C5** import extras bancar neidempotent — **RESTANȚĂ** (probabilă).
- **C6** minore (facturi_recurente search_path, woocommerce, portal_bon, R183) — **RESTANȚĂ**; R183 se poate
  închide ca reparată (audit a confirmat că `apel_anaf` nu mai ține tranzacția).

## D — instrumentele mint (clichetele)
- **D1–D10** — **RESTANȚĂ deschisă, cu design** (v. Anexa restanțe). Recalibrarea celor 6 scanere
  (call-graph multi-nivel D1; module d406_active/stocuri + helperi D2; „numită" pe AST D3; module de
  implementare excluse D5; anti-vacuum DUK D6) + rederivarea INVENTAR.txt/NEVERIFICAT.txt + rescrierea
  clichetului SUBSET_FISCAL de la cifra reală + garda-mutație D4 (cele trei clichete pică pe ea). Lotul e
  cohesiv (D4 depinde de recalibrarea D1/D3/D5) și mare; se implementează separat, cu clichetele reverificate.

## §7 — operațiunile rulate + durate măsurate

Operațiuni (per lot): probe roșu-înainte (swap la commitul de bază) → reparație → probe verde-după →
regresie țintită → gărzi de cascadă → **poarta completă** (pytest întreg + ruff + verificator) →
commit → post-commit (publicare + four-way + restart). Migrări (nerulate pe prod în această tură,
restanță de rulat la închidere): `migrare_curs_lei` (A1), `migrare_unic_numar_factura` (C1).

Durate măsurate ale porților complete (pytest, ~6.300 de teste):
- A1 (validare pre-commit A1-solo): 2.134 s (35:34)
- A1+B combinat: 2.116 s / 2.110 s / 2.127 s (rulări de verificare)
- A2–A5 (dbaf8cc2): pre-commit ~35 min; poartă de verificare 2.119 s
- A7+A8micro (8719c223): 2.127 s (35:27)
- C1–C3 (f6c7dbb2): 2.123 s / 2.124 s (35:24)
- §0: pre-commit în curs la scrierea raportului
Fiecare commit adaugă pre-commit-ul propriu (~36 min) + post-commit (publicare + restart, ~1 min).

## E — valori fiscale
- Cele conforme rămân conforme. **RESTANȚE**: plafon micro 100.000 EUR fără verificare; tichet 45 lei fără
  data_out (30.09.2026); CAM pe indemnizația CM; `salarizare.cam` include facilitatea (verifica_d112 roșu);
  nota facturii primite MAX(cota_tva) pe factură mixtă. Toate de tratat cu E/§0.
