Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — audit vizual tenant_005 (Constructii Profit Trim SRL / P2, cabinet 1968); clusterele 1-5 LIVRATE

## REPORNIRE (comanda exacta, gata de dat)
Continua auditul vizual tenant_005 (P2, Constructii Profit Trim SRL) cap-coada cu Playwright (captura PRIVITA +
axe-core + mobil pe fiecare ecran atins - Regula 14 integral), REPARAND ce gasesti; ce gasesti pe o firma cauta pe
toate (Regula 13). Valorile fiscale se verifica la sursa (anaf_surse/*_struct + XSD + DUK), NU se cer de la Costin.
Fiecare gard nou: mutatie probata RED pe cod vechi, prin rulare. DS inainte de orice cod de interfata, cu capitolul
citat. DUPA ORICE editare static/js: venv/bin/python versioneaza_assets.py --scrie INAINTE de commit (altfel poarta
rosie). Commit pe iconta_nou = poarta pre-commit (~9min: suita + verificator); post-commit publica origin/main +
backup + restart iconta-nou automat. Probele Playwright: helper w_auth (tenant_005 id=4840); scripturi in ~/probe_t005.

PUNCTUL LA CARE AM RAMAS: stratul VECTOR FISCAL (nr.2) parcurs cap-coada si reparat (clusterele 4+5). RAMAS, in
ordinea straturilor de migrare (meniuMigrarePerFirma), NEparcurse vizual cap-coada:
- **Solduri initiale (nr.3)**: import balanta. Preview POST /tenants/{id}/solduri/incarca ; salvare POST /solduri ;
  registru GET /solduri. Validator core/solduri_api (extrage_balanta:68 + verifica_echilibru + balanta_valida).
  Blocaje de provocat la preview: format neacceptat (doar .csv/.xlsx); "nu gasesc coloane debit/credit"; balanta
  DEZECHILIBRATA (debit != credit); balanta GOALA (toate 0).
- **Solduri parteneri (nr.4)**: POST /tenants/{id}/parteneri/incarca -> /parteneri. Validator solduri_parteneri_api
  (extrage + coerenta + verifica_randuri:185): respinge conturi non-partener + CUI invalid.
- **Asociati (nr.6)**: POST /tenants/{id}/asociati-import/incarca -> /asociati-import. Validator
  asociati_import_api.verifica_randuri:126: CNP/CUI valid + cotele insumeaza EXACT 100%. Consumat de D205/dividende.
- **Mijloace fixe (nr.7)**: POST /tenants/{id}/mijloace-fixe-import/incarca -> import. Registru GET /mijloace-fixe
  (ecran mijloace_ecran.js). Validator mijloace_fixe_import_api.verifica_randuri:158. Obligatoriu: denumire.
- **Istoric declaratii (nr.8)**: POST /tenants/{id}/istoric-declaratii-import/incarca -> import. Validator
  verifica_randuri:138: tip in nomenclator ANAF, an 2000..anul+1, luna 1-12, data depunerii >= perioada.
- **Plan de conturi (nr.9)**: FARA fisier - cautare + adaugare cont manual (simbol+denumire), POST /plan-conturi.
- (Vector nr.2, Salariati nr.5, Articole = deja parcurse cap-coada.)

## FRONTURI RAMASE DESCHISE (din turele anterioare)
- FRONT D - declaratii: D112 (VERIFICA la sursa daca art.60 pct.5 constructii e in vigoare 2026 inainte de a decide
  daca lipsa scutirii e defect), D101/D205 anuale, Bilant S1005 (blocat CORECT de reg.com. lipsa). Wizard pas 3 neatins.
- FRONT E (mic) - editarea nume/CNP/data_angajare/norma salariat din UI (azi doar IBAN/COR/incetare/salariu).

## REZIDUU (in GARZI, neridicat aceasta tura)
- (a) Eroarea de la formularul Vector NU marcheaza campul vinovat cu contur (doar cutie generica jos; mesajul il
  numeste acum). Pattern app-wide de field-level error marking (Regula 14 pct.4 "eroarea care nu marcheaza campul") -
  cluster a11y separat.
- (b) axe pe ecranul Vector: 15 noduri color-contrast (serious) + 17 tinte <44px + 2 info livrata EXCLUSIV prin
  `title` (pierduta pe touch, Pixel 5). Pre-existent, app-wide.
- (c) Seed: 12/20 tenanti au tip_decont 'L'/'T' legacy - INTENTIONAT (test ca motoarele accepta legacy, vezi ruptura
  seed<->control 14.08). Normalizat la granita UI (common.tip_decont_lung); seed-ul NU se atinge.

## FOUR-WAY (de confirmat de urmatoarea tura)
HEAD = origin/main = backup/lant-2026-08-17 (remote) = 3a3b3f2. Comituri aceasta tura: 53ca370 (cluster 4), 3a3b3f2
(cluster 5), + acest PREDARE. Poarta verde pe fiecare (2281->2284 passed, verificator TOTAL 0). RUNNING confirmat
BEHAVIORAL: formularul Vector arata profit/TVA-Da/Trimestrial/IC-Nu/CUI-populat (captura privita, iconta-nou restart
17:24 > commit). Sentinele PUSH_*_ESUAT absente.

## LIVRAT aceasta tura (clustere 4+5)
4. **Mesaje user-facing fara nume intern de camp** (53ca370, DS v2.35). 13 instante (vector_fiscal x3,
   facturi_recurente, stocuri_cv, main.py x6, perioada, control_fiscal, d112/d205/d300_reconciliere) reparate + gard
   core/test_mesaje_fara_camp_intern.py (RED-probat) + 2 baseline temei-diagnostic (bug de cod) cu motiv.
5. **Vector fiscal per-firma reflecta vectorul salvat** (3a3b3f2, DS v2.36). B1: formularVectorFirma incarca
   /tenants/{id}/vector (era gol pe traseul per-firma - plator TVA aparea "Nu", risc suprascriere vector real; CUI gol
   in antet). B2: common.tip_decont_lung normalizeaza 'L'/'T' legacy la granita UI (citeste + portal_api.date_firma;
   date_firma.js citeste vectorul din /vector). Garduri core/test_tip_decont_lung.py (2, RED-probate). Motoarele
   fiscale NEATINSE (parseaza raw prin perioada_tva_tip).
