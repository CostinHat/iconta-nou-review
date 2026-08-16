Marca de referință: dd25c3e. Citește CLAUDE.md §2.2 (structura raportului) și §2.3 (lanț, siguranță, limbă) și ARHITECT.md „FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, înainte de a începe. Stare: audit vizual tenant_003, reparație C1–C4. LIVRAT: C1, C2, C4 (four-way, gărzi RED→GREEN, randat before/after cu captură privită). RĂMAS: C3 (schimbare de schemă pe 28 tenanturi — merită sesiune focalizată, scop complet mai jos).

# PREDARE LANT — reparație constatări audit tenant_003 (C1/C2/C4 livrate, C3 rămas)

## FOUR-WAY (ultima execuție, 16.08.2026)
HEAD = origin/main = backup/lant-2026-08-16 = RUNNING = dd25c3e.

## PARCURGERE tenant_003 (auth cross-cabinet, reutilizabil)
- tenant_003 (Comert Micro TVA SRL) sub cabinetul 1968 (Prisma). Token mințuit fără parolă via
  `auth_api.emite_token(<user patron@prisma-cont.test>)` + inject sessionStorage. Helper: frontend_test/w_auth.py
  (new_page, deschide_firma, shot). Probe scrise în această tură: proba_c1_t003.py, proba_c2.py, proba_c4.py.
- Rulare: `set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=~/iconta_nou:~/iconta_nou/frontend_test ./venv/bin/python frontend_test/<script>.py`. Serviciul = 127.0.0.1:8010.

## LIVRAT (C1, C2, C4 — RED probat pe cod vechi, GREEN după; randat înainte/după)
- **C1 [349cc5b]** — Stat de plată (#fa-salariati): „pontaj neconfirmat" era o stare de PERIOADĂ (an,luna,domeniu=pontaj)
  afișată ROȘU ca atribut per-salariat (cheiat pe tichete>0), implicând fals că un salariat fără marcaj ar avea
  pontaj confirmat. Fix (DS cap.23): banner `.caseta-info` + semafor gri o dată pe lună; per-rând „tichete blocate"
  gri (consecința reală) doar la cei cu tichete. Gard core/test_c1_pontaj_neconfirmat_gri.py (2). Randat pe tenant_003
  (Ana tichet=40 marcată vs Radu tichet=0 nemarcată). Cauză confirmată la sursă: stat_plata_api.py:67.
- **C2 [2b710bb]** — import per firmă (migrare.js): după salvare `nav.deschide(<wizard cabinet>)` → fereastră nouă cu
  TOATE firmele, în afara firmei; fără mesaj de succes. Fix: `nav.inapoiPas()` (revine pe traseu la meniul firmei) +
  mesaj verde care supraviețuiește revenirea (`_migMesaj`/`_consumaMigMesaj`, arataMesaj „ok"). CLASA (Regula 13):
  7 handlere reparate (solduri/parteneri/salariati/asociati/mijloace/istoric + vector fiscal). Gard
  core/test_c2_migrare_revenire_firma.py (2). Randat before/after pe tenant_003 (salariati).
- **C4 [dd25c3e]** — „Descarcă model (CSV)" exista doar la solduri (1/9). Adăugat la celelalte 8 straturi de import cu
  fișier (parteneri/salariati/asociati/mijloace/istoric/articole/retete/rip), format citit din PARSER
  (core/*_import_api.py), model comun `_descarcaModelCSV`+`MODELE`. Intro mijloace (bug numit) + articole completate
  cu conturile citite dar omise. Gard core/test_c4_model_csv.py (3). Probat round-trip pe mijloace (model
  descărcat → reîncărcat → parserul îl recunoaște, 2 mijloace corecte). plan_conturi = căutare/adăugare (fără upload),
  exclus.

## RĂMAS: C3 — badge stare per strat + flag plan_conturi (SCOP COMPLET DESCOPERIT, decizie DATĂ de Costin)
Constatare: `meniuMigrarePerFirma` (static/js/ecrane/migrare.js:1435) NU are badge de stare per strat, deși wizardurile
de cabinet au („✓ gata / de încărcat"). Planul de conturi n-are semnal de prezență: 185 conturi standard fără flag →
count>0 ar fi FABRICAT; analiticele venite din balanță NU se disting azi de planul standard.

**Decizia lui Costin (DATĂ, NU se re-cere): adaugi flagul.** C3 e CUPLAT — badge-ul pentru plan_conturi cere flagul
(altfel count=185 = prezență fabricată). E schimbare de schemă pe 28 tenanturi (§2.3 pct.2/5 — categorie de grijă;
de-aia predat separat, nu grăbit ca al 4-lea cluster).

Scop (verificat la sursă în această tură):
1. **SCHEMA**: `plan_conturi` are simbol/denumire/tip/sold_debitor/sold_creditor — FĂRĂ coloană de sursă. 28 scheme au
   tabela; tenant_003 are exact 185 conturi (toate standard). Adaugă coloană `sursa` (varchar: 'standard'/'balanta'/
   'manual') în `tenant_template.sql`, cu seed-ul celor 185 marcat 'standard'.
2. **MIGRARE**: `core/migrare_plan_conturi_sursa.py` (tiparul migrare_*.py, ex. migrare_cont_venit_linie.py) — ALTER
   TABLE plan_conturi ADD COLUMN sursa IF NOT EXISTS pe toate schemele; backfill: simbolurile care coincid cu cele 185
   standard din template → 'standard', restul → 'balanta'. Rulează pe 28 scheme (deploy).
3. **IMPORT**: `solduri_api.py` (balanța adaugă conturi analitice în plan — vezi docstring: „conturile analitice
   intră automat în plan") → marchează noile conturi `sursa='balanta'`; backendul importPlanConturiFirma (adăugare
   manuală) → `sursa='manual'`.
4. **UI**: (a) `meniuMigrarePerFirma` — badge per strat. Pentru plan_conturi semnalul de prezență = are conturi
   ADĂUGATE (sursa≠'standard'), nu count total. Pentru status per firmă al celorlalte straturi: wizardurile de cabinet
   iau `are_X` din `/migrare/<strat>`; verifică dacă există endpoint de status PER FIRMĂ sau agregă. (b) ecranul
   plan_conturi (importPlanConturiFirma) — distinge vizual conturile standard de cele adăugate.
5. **GĂRZI**: `test_schema_coloane.py` + `test_audit_schema.py` (poartă HARD template→tenant) TREBUIE actualizate
   pentru noua coloană — altfel pică. Gard nou: plan_conturi.sursa există + backfill corect + importul marchează sursa.
6. **PROBĂ (Regula 14)**: Playwright pe tenant_003 — badge în meniul firmei; plan_conturi cu standard vs balanță
   distincte; pe date reale (185 standard + analiticele din balanța importată).

ATENȚIE: `test_audit_schema` PICĂ dacă template și tenanții diverg → template + migrare + rulare pe 28 scheme se fac
ÎMPREUNĂ, într-un singur cluster. Fără backfill corect, badge-ul plan_conturi rămâne fabricat (exact ce blochează).

## LECȚII METODĂ (16.08, tura C1/C2/C4)
- Editare pe server prin scripturi Python cu `assert count==1/2` pe ancore + `rfind` când textul apare de două ori
  (dispecer + handler). Ancore encoding-stabile (fără diacritice) când intro-urile mixează diacritice literale și `\u`.
- Proba cea mai tare la un model de import = round-trip: descarcă modelul → reîncarcă-l → parserul îl recunoaște.
- `versioneaza_assets.py --scrie` după fiecare editare JS; ES-check prin copie `.mjs`.
