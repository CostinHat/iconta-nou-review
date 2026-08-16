Marca de referință: 76e6bb1. Citește CLAUDE.md §2.2 (structura raportului) și §2.3 (lanț, siguranță, limbă) și ARHITECT.md „FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, înainte de a începe. Stare: reparația celor 8 constatări C1–C8 din auditul tenant_003. LIVRAT: C7, C6, C5 (+ C8 verificat fals). RĂMAS: C1, C2, C3, C4 (mai jos, cu ecranul exact). Regula 13 (clasă), regula 14 (randare înainte/după).

# PREDARE LANT — reparație constatări audit tenant_003 (C7/C6/C5 livrate, C1-C4 rămase)

## FOUR-WAY (ultima execuție, 16.08.2026)
HEAD = origin/main = backup/lant-2026-08-16 = RUNNING = 76e6bb1 (post-commit restartează iconta-nou pe 8010).

## PARCURGERE tenant_003 (auth cross-cabinet, reutilizabil)
- tenant_003 (Comert Micro TVA SRL) e sub cabinetul 1968 (Prisma). Token mintuit fără parolă:
  `auth_api.emite_token(<user patron@prisma-cont.test>)` + inject sessionStorage. Scripturi în frontend_test/:
  w_auth.py (helper), w_salariati/w_operare/w_straturi/w_date_vector/w_declaratii/w_decl_gen3/w_c8.py.
- Rulare: `set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; PYTHONPATH=~/iconta_nou:~/iconta_nou/frontend_test ./venv/bin/python frontend_test/<script>.py`. Serviciul = 127.0.0.1:8010.

## LIVRAT în această tură (RED probat pe cod vechi, GREEN după; randat înainte/după)
- **C7 [corectitudine, SISTEMIC] — 76e6bb1.** D300/D394/D406 pe firmă TRIMESTRIALĂ picau cu „luna invalidă:
  None (aștept 1-12)" (BLOCATE). Cauza: `/declaratii/tipuri`+wizardul folosesc periodicitatea EFECTIVĂ
  (tip_decont), dar `valideaza_cerere` folosea cea STATICĂ (d300=lunar); frontendul trimite `trim`, validatorul
  cerea `luna`. Fix într-un singur loc (dispecerul `genereaza`+`valideaza_cerere`): periodicitate efectivă la
  validare + conversie trim→lună-ancoră (T1→3,T2→6,T3→9,T4→12; DUK R18). Clasa = {d300,d394,d406}. Gard
  core/test_c7_periodicitate_trimestriala.py (6).
- **C6 [text fals]** — selectorul de declarații afișa hardcodat „nu se aplică (partidă simplă)" (declaratii.js:89)
  pentru orice neaplicabilă; motivul real (neaplicabile_selector) era în title. Fix: afișează motivul real.
- **C5 [acord]** — „Profil incomplet — 1 câmpuri obligatorii lipsesc" → singular/plural. Gard core/test_c6_c5_motiv_acord.py (2).
- **C8 [VERIFICAT FALS, NEreparat]** — „mm/dd/yyyy" la Casă = randarea nativă a `<input type=date>` în browser
  (en-US), NU defect (app nu setează placeholder — verificat null; `<html lang=ro>`). Regula 2 a răsturnat constatarea.

## RĂMAS DE REPARAT (constatări, cu ECRANUL exact)
- **C1** [Stat de plată, #fa-salariati] Pontaj neconfirmat afișat INCONSISTENT: Popescu Ana „⚠ pontaj
  neconfirmat", Ionescu Radu (la fel de nou pe 08/2026) NU. Cauză de căutat: probabil legat de prezența
  tichetelor de masă (mesajul „Tichetele de masă sunt blocate" apare doar la Ana). De verificat unde se decide
  marcajul „pontaj neconfirmat" pe salariat (fluturaș/stat de plată) și de ce diferă între cei doi.
- **C2** [Salariați migrare, după salvare] Fără mesaj de succes explicit (doar badge „✓ gata"); navigarea duce
  la wizardul CABINET (toate firmele), nu la firma curentă. Handler: migrare.js `previzualizeazaSalariati` →
  `nav.deschide("Salariați", wizardSalariati)`. Fix: arataMesaj „ok" (DS cap.6) + revenire la firmă. CLASA:
  toate cele ~9 straturi navighează la fel după salvare (Q7 din campania veche — verifică toate).
- **C3** [Import date per firmă, meniuMigrarePerFirma] Fără badge de stare per strat. BLOCAT pe un semnal de
  prezență corect pentru `plan_conturi` (185 conturi standard, fără flag standard/adăugat → count>0 ar fi
  FABRICAT). Restul straturilor au sursă clară (rezumat/count). Decizie de model necesară pentru plan_conturi.
- **C4** [Straturi import] „Descarcă model (CSV)" doar la Solduri (1/9). De adăugat la parteneri/asociați/
  mijloace/istoric/articole/rețete, fiecare cu modelul corect (coloanele din intro-ul fiecărui strat).

## RĂMAS DE PARCURS (din tura de audit anterioară, netraversat)
- Declarații pasul 3 (XML + DUK) — acum DEBLOCAT de C7 pe D300 trimestrial; de reluat până la Descarcă XML +
  Validează DUK. Celelalte declarații (D100/D112/D205/D394/D406). Bancă (#fa-banca). Salvarea reală pe
  straturile solduri/parteneri/asociați/mijloace/istoric/plan/articole/rețete.

## LECȚII METODĂ (16.08)
- **Regula 2 pe constatările de parcurgere**: verifică la sursă înainte de a repara (C8 era artefact de browser).
- Periodicitatea declarațiilor TVA e EFECTIVĂ (tip_decont), nu statică — o singură sursă (dispecerul).
- JS: `versioneaza_assets.py --scrie` pentru tokeni. Auth cross-cabinet: `auth_api.emite_token`.
