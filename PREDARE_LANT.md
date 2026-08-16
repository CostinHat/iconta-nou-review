Marca de referință: 0ae8baf. Citește CLAUDE.md §2.2 (structura raportului) și §2.3 (lanț, siguranță, limbă) și ARHITECT.md „FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, înainte de a începe. Sunt 7 defecte nereparate din campania import CUBUS (Q9, Q18, Q7, Q8, Q12, Q14, cod mort Q10-skip). Punctele de aici sunt harta, nu perimetrul (regula 13). Repară tot ce e defect pe traseul importului/migrării, inclusiv dincolo de ce e scris. Ordinea: cifre greșite → blocante → restul.

# PREDARE LANT — import CUBUS: loturile amortizare + preview=salvare + COR LIVRATE

## FOUR-WAY (ultima execuție, 16.08.2026)
HEAD = origin/main = backup/lant-2026-08-16 = RUNNING = 0ae8baf
(post-commit restartează automat iconta-nou pe portul 8010; confirmă cu `versiune.stare()` running==head, divergent=False.)

## LIVRAT în această tură (RED probat pe cod vechi, GREEN după; randat unde e ecran)
- **Lot 1 amortizare (Q6+Q15) — 5a610dc.** Ecranul /mijloace-fixe + notele lunară/casare/reevaluare calculau
  MEREU liniar ignorând `metoda`; TREI înscriau cifra greșită în jurnal/notă (ajunge la ANAF), una o afișa.
  Motorul cu 4 metode (core/d406_active.py, CF art.28) exista, nechemat. 2 funcții noi (amortizat_la_data,
  amortizare_luna, coerente cu calc_asset la granița de an); 4 situri cablate. Metodă nepermisă pe categorie
  → eroare pe rând / 422, nu liniar tacit (DS cap.17). Casat → amortizat/ramas None (regula 4). Ultima lună
  absoarbe rotunjirea → suma pe viață = amortizabil exact. Gardă core/test_amortizare_ecran_metoda.py (15).
  Randat autentificat: ecranul afișează Metodă + amortizat pe motor (1.200/3.600, 1.100/4.900 pe ALFA MICRO).
- **Lot 2 preview=salvare (Q5) — 74a655c.** Cele 5 endpoint-uri de preview (parteneri/salariați/asociați/
  mijloace/istoric) luau verdictul din flagurile lui extrage (cnp_valid/ok) — a DOUA validare care drifta de
  verifica_randuri (poarta pe care SALVAREA, importa, o ridică). Acum întorc `erori = verifica_randuri(...)`
  prin migrare_api.erori_verifica (normalizează tuplu parteneri/listă); frontend `gateazaPreview()` blochează
  Salvarea pe rândurile respinse + le arată (DS cap.5/6/24). Gardă core/test_preview_salvare_poarta.py (6),
  același fișier prin ambele capete. Randat: Solduri (Q10) + Date firmă (Q1).
- **Lot 3 COR (Q16) — 0ae8baf.** Preview salariați arăta codul COR ca „Funcție"; acum denumirea ocupației
  (cor_api.denumire din public.cor_ocupatii), fallback la cod, cod în title. Gardă core/test_q16_cor.py (2).

## RĂMAS DE FĂCUT (neînceput) — cifre/blocante întâi
1. **Q9 parteneri — coerență pierdută (BLOCANT).** Diferența `coerenta()` (solduri_parteneri_api.py:148) se
   arată la preview dar NU se persistă și NU blochează salvarea (spre deosebire de solduri). Fix: blochează
   salvarea pe incoerență (ca la solduri) SAU persistă+propagă la controlul fiscal. Datele incoerente intră
   acum tăcut în evidență.
2. **Q18 XSD — nomenclator înghețat (SISTEMIC).** d112.py:16 hardcodează `d112_06082026.xsd`. Fix: alege automat
   cel mai nou `d112_*.xsd` din anaf_surse/ (glob pe data din nume) — adăugarea fișierului să fie de ajuns, fără
   editare de cod. Toate declarațiile fixate la XSD datat (grep clasa).
3. **Q7 solduri — confirmare după salvare (UX).** După salvare, `arataMesaj(..., "ok")` de confirmare (DS cap.6),
   nu revenire tăcută la formular gol.
4. **Q8 badge de stare per strat.** `meniuMigrarePerFirma` (migrare.js:1477): badge per strat citind
   /migrare/status (ca `meniuMigrare` la nivel cabinet). Semafor prin tokeni (DS cap.8).
5. **Q12 avertisment pe rând — doar `title=` (inaccesibil pe touch).** Fix: `.caseta-atentie`/arataMesaj vizibil
   (DS cap.5). NOTĂ: gateazaPreview (Lot 2) a introdus deja `.caseta-atentie` pentru erorile de preview la nivel
   de fișier; Q12 rămâne pentru avertismentele PE RÂND din tabelele de preview (r.ok / CNP), încă pe `title=`.
6. **Q14 „Descarcă model (CSV)" — există doar la solduri (1/9, confirmat la randarea Q10).** Adaugă la parteneri,
   salariați, asociați, mijloace, istoric, fiecare cu model corect.
7. **Cod mort Q10-skip.** Salariații NU sar peste invalizi — ambele parsere blochează tot importul; calea „skip"
   (salariati_import_api bucla din `importa` + banda UI „X cu CNP greșit (vor fi sărite)" din migrare.js) e COD
   MORT + text care promite un comportament inexistent (dinainte de 15.07.2026). De ELIMINAT codul mort + textul.

## TURĂ SEPARATĂ (NU se începe din predarea asta)
- Triaj mesaje generatoare (~150 raise ValueError în d100/d112/d205/d300/d390/...): afișat-vs-intern, judecată
  per-mesaj, diacriticizat cele afișate + gardă scopată ca la import (extinderea Q2/Q17).

## LECȚII METODĂ (tura 16.08)
- **JS: NU calcula manual tokenul `?v=`** — rulează `./venv/bin/python versioneaza_assets.py --scrie` (content-hash;
  bumpează TOATE siturile de import, DS cap.19). Un token greșit pică `test_versionare_assets` → poartă roșie.
- **Editare pe server prin patch scripts Python via scp** (Edit/Write locale ating checkout-ul Windows, nu ~/iconta_nou).
- **post-commit restartează automat iconta-nou (port 8010)** → four-way automat după poarta verde; nu e nevoie de restart manual.
- **Randare autentificată**: frontend_test/render_lant.py (login din ~/.iconta/fe_test.env, token în sessionStorage,
  BAZA=127.0.0.1:8010 = iconta-nou, ocolește allowlist-ul de mentenanță). Firma cu MF = ALFA MICRO (tenant_013, doar liniar).
- **DB din shell**: `set -a; . ~/.iconta/db.env; set +a` înainte de pytest/scripturi ad-hoc.
- **Cuplaj testat**: o schimbare care adaugă `db.get_conn` într-un endpoint fără DB (ex. Q16 pe salariați) cere fake_conn în gărzile care apelau acel endpoint (Q5).
