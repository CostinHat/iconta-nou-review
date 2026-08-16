Marca de referință: ed6ac35. Citește CLAUDE.md §2.2 (structura raportului) și §2.3 (lanț, siguranță, limbă) și ARHITECT.md „FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, înainte de a începe. În lucru: audit vizual cap-la-cap al tenant_003 (Comert Micro TVA SRL, cabinet 1968 Prisma) — parcurs până la ecranul de import salariați; restul traseului NEparcurs. Regula 13: perimetrul, nu numele. Regula 14: captură privită, nu selectoare.

# PREDARE LANT — audit vizual tenant_003 (parcurgere migrare, în curs)

## FOUR-WAY (ultima execuție, 16.08.2026)
HEAD = origin/main = backup/lant-2026-08-16 = RUNNING = ed6ac35
(post-commit restartează automat iconta-nou pe portul 8010.)

## CUM SE PARCURGE tenant_003 CU PLAYWRIGHT (auth cross-cabinet)
- tenant_003 e sub cabinetul 1968 (Prisma), NU sub cabinetul login-ului de test FE (4163). Deci NU folosi
  fe_test.env. Mintuiește un token direct pentru admin-ul cabinetului 1968, fără parolă:
  `from core import auth_api; tok = auth_api.emite_token(<rand user patron@prisma-cont.test din public.users>)`.
  Injectează în sessionStorage (iconta_token + iconta_user JSON), ca în frontend_test/walk_t003.py + provoke_t003.py.
- Env pt scripturi ad-hoc: `set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a` (JWT_SECRET e în api_keys.env),
  și `PYTHONPATH=~/iconta_nou`. Serviciul = iconta-nou pe 127.0.0.1:8010 (localhost ocolește allowlist-ul de mentenanță).
- Navigare: „/" → Firme → Firme existente → „Comert Micro TVA" → cardurile firmei (#fa-import Import date,
  #fa-datefirma Date firmă, #fa-facturi, #fa-banca, ...). Import date deschide meniuMigrarePerFirma (10 straturi).
- Starea datelor tenant_003 (mostly gol): salariati=1, plan_conturi=185 (standard), vector setat (platitor_tva=T,
  tip_decont='T', regim micro); solduri_initiale/parteneri/asociati/mijloace/istoric/produse/retete/rip = 0.

## LIVRAT în această tură (RED probat pe cod vechi, GREEN după; dovadă vizuală)
- **Cod mort skip salariați (Q10) — ed6ac35.** Provocând importul de salariați cu fișier stricat (2 CNP
  invalide), banda „2 cu CNP greșit (vor fi sărite)" contrazicea vizibil caseta „2 rânduri nu pot fi salvate"
  + butonul dezactivat. Adevărul: importa() BLOCHEAZĂ la primul CNP invalid (verifica_randuri = prima poartă);
  bucla de skip + `sarite_cnp` + textele „vor fi sărite"/„X săriți" erau cod mort/promisiune falsă. Eliminat
  (backend) + text aliniat (DS cap.6). Gardă core/test_d1_import_integritate.py REscrisă (block-not-skip,
  superseda test_salariați_skip_surfațat_in_ui). Clasa (regula 13): doar salariați; retete/articole „sărite" =
  skip REAL de duplicate (neatins).

## CONSTATĂRI din aceeași parcurgere (VĂZUTE, neatinse)
- **Q8 — meniuMigrarePerFirma nu are badge de stare per strat** (văzut: toate cele 10 rânduri identice, fără
  „importat/gol"). Contabilul nu vede ce e adus. Reparația e BLOCATĂ pe un semnal de prezență corect: `plan_conturi`
  are 185 conturi standard fără flag standard/adăugat → un badge count>0 acolo ar fi FABRICAT (exact capcana regulii
  14 pct.3). Cere decizie de model: flag „adăugat" pe plan_conturi SAU definirea „plan importat". Restul straturilor
  au sursă clară de prezență (rezumat/count: solduri_initiale, solduri_parteneri, salariati, asociati, mijloace_fixe,
  public.declaratii_depuse sursa='migrare', produse, retete, rip_operatiuni; vector = firma_profil.tip_decont).
- **Q12 — avertismentul CNP pe rând e doar în `title=`** (văzut: „1960101078911 ⚠", motivul „cifra de control"
  doar în title, inaccesibil pe touch). Fix: vizibil, nu tooltip nativ (DS cap.5).

## RĂMAS DE PARCURS pe tenant_003 (traseul, NEatins)
1. Migrare, fiecare strat cap-la-cap (import→preview→salvare→confirmare→ecran unde apar datele), cu blocaje
   provocate: solduri, parteneri, asociați, mijloace fixe, istoric, plan de conturi, articole, rețete. (Salariați
   parcurs parțial: preview + blocaj; salvarea reală + ecranul „unde apar" neparcurse.)
2. Date firmă și vectorul fiscal (#fa-datefirma; vector = primul rând din Import date).
3. Operarea curentă: facturi (#fa-facturi), bancă (#fa-banca), casă, salarii — Comert Micro TVA e micro+TVA, are 1 salariat.
4. Semaforul + controlul fiscal (dashboard: „7 alerte fiscale", „1 declarație de validat" — de deschis și citit).
5. Fiecare declarație datorată (micro+TVA: D300, D394, D100/D101 după caz, D112 dacă are salariați, D205, SAF-T)
   până la generarea XML + validarea DUK.

## DEFECTE din campania anterioară (încă NEatinse, cod-citit)
- Q9 parteneri — coerență pierdută (BLOCANT): coerenta() se arată la preview dar nu blochează salvarea; ALEGERE
  block-vs-persistă+propagă = posibilă decizie de produs (a se clarifica).
- Q18 XSD — d112.py:16 hardcodează d112_06082026.xsd; glob pe cel mai nou d112_*.xsd (sistemic).
- Q7 confirmare după salvare (arataMesaj „ok", DS cap.6) — pe toate straturile (salvarea navighează tăcut).
- Q14 „Descarcă model (CSV)" — doar la solduri (1/9); de adăugat la celelalte.
- Tură separată: triaj mesaje generatoare (~150 raise, afișat-vs-intern).

## LECȚII METODĂ (16.08)
- **Auth cross-cabinet fără parolă**: `auth_api.emite_token(user_row)` + inject sessionStorage (vezi mai sus).
- **JS: NU calcula manual `?v=`** — `./venv/bin/python versioneaza_assets.py --scrie` (bumpează toate siturile).
- **Ratchet pe cod mort**: nu pune în COMENTARIU tiparul pe care gardul îl interzice (`sarite += 1` în comentariu a
  picat propriul gard). Descrie mecanismul fără să scrii literalul interzis.
- **Editare pe server prin patch scripts Python via scp**; DB/JWT din `~/.iconta/db.env` + `api_keys.env`.
