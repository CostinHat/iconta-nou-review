# TESTE.md — planul de testare

**29.07.2026.** Registrul campaniei de testare a aplicației.

Campania are **două sesiuni distincte** (A, B), precedate de o **Faza 0** de pregătire — în ordine:

- **Faza 0 — decuplarea suitei de firmele persistente (GATA, 29.07).** Niciun test nu mai
  depinde de o firmă din baza (`tenant_001/002/003`): cine atinge baza își construiește
  subiectul pe schemă efemeră din `tenant_template` (comisă + DROP pentru scriitori, ROLLBACK
  pentru cititori) sau pe fake cursor. Prerechizit pentru B — firmele F1–F7 se **construiesc**,
  nu se presupun. Gardă permanentă: `core/test_teste_decuplate.py`. Vezi DECIZII 29.07.
- **Sesiunea A — alinierea la legislație.** Fiecare test fiscal se rescrie ca să afirme
  **regula de drept**, nu implementarea. Un test o dată; se validează, apoi următorul. Nu
  are nevoie de date; e pură.
- **Sesiunea B — testarea pe flux.** Cele 7 firme de test, cele 11 etape ale muncii unui
  contabil, cu regula cascadei.

**A înaintea lui B, și nu invers.** În A verifici legea o dată; în B o folosești. Fișierul
de așteptări al firmelor de test (B) se scrie din temeiurile deja verificate în A, nu de la
zero. Invers ar însemna să verifici de două ori — sau, mai probabil, a doua oară din memorie.

---

## Infrastructură de testare vizuală (permanentă, 17.08.2026 — cerută de Costin)

Trei unelte care rulează pe pagina **randată** (Playwright autentificat via `w_auth`), pe cele 5 ecrane
problematice numite de Costin (`frontend_test/vizual/nav_ecrane.py::ECRANE`: import_mijloace_fixe,
vector_fiscal, plan_conturi, stat_plata, declaratii). Rulate **pe server** (`~/iconta_nou`, serviciul la
127.0.0.1:8010). **Nu repară — măsoară și marchează.**

| Unealtă | Fișier | Ce acoperă | Ieșire |
|---|---|---|---|
| axe-core (v4.10.2, vandorizat offline) | `frontend_test/vizual/axe_scan.py` | contrast (`color-contrast`), fără-etichetă (`label`/`*-name`), `title` în 3 categorii: strict / glif / extra (title cară info absentă din etichetă) | `raport_axe.txt`+`.json` |
| emulare mobil (Pixel 5: touch, fără hover, 393px) | `frontend_test/vizual/mobil_scan.py` | ce dispare pe touch: tooltip `title` cu info unică, reguli CSS `:hover`, ținte de atingere <44px, overflow orizontal | `raport_mobil.txt`+`.json` + `mobil_*.png` |
| baseline capturi (echiv. `toHaveScreenshot`) | `frontend_test/vizual/baseline_scan.py` | fără arg = stabilește `baseline/*.png` + self-diff (flakiness); `--compare` = diff pixel vs baseline (prag 0.05%) | `raport_baseline.txt`+`.json` |

Rulare: `set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; export PYTHONPATH=$HOME/iconta_nou:$HOME/iconta_nou/frontend_test:$HOME/iconta_nou/frontend_test/vizual; ./venv/bin/python frontend_test/vizual/<unealtă>.py`

Gardă: `core/test_infra_vizuala.py` (infra nu poate dispărea — Regula 6). Poartă verde vizuală: **CLAUDE.md §2.3 pct.11** (cele trei rulate pe ecranele atinse înainte de poarta verde). Detalii: `frontend_test/vizual/README.md`.

## În lucru acum
- fir: TURA IMPORT CUBUS — cele 11 defecte ramase din PREDARE_LANT (16.08.2026). Ordine ceruta: intai
  cifre gresite pe ecran, apoi blocaje, apoi restul. LOT 1 [GATA]: amortizare pe metoda (Q6+Q15).
- ultim: 3 loturi PUBLICATE 16.08: L1 amortizare (5a610dc), L2 preview=salvare (74a655c), L3 COR (0ae8baf).
  Garzi RED-probate: test_amortizare_ecran_metoda.py (15), test_preview_salvare_poarta.py (6), test_q16_cor.py (2).
  Randat autentificat (frontend_test/render_lant.py): ecran MF (L1), Solduri Q10, Date firma Q1. verificator 0.
- urmator: cod mort skip salariati [GATA 16.08, audit tenant_003]. RAMAS in PREDARE_LANT.md: Q9 coerenta
  blocanta parteneri, Q18 XSD auto-select, Q7 mesaj confirmare, Q8 badge per-strat (blocat: semnal prezenta
  plan_conturi), Q12 avertisment PE RAND accesibil, Q14 CSV model x5. + traseul tenant_003 neparcurs integral
  (operare/semafor/control/declaratii->XML->DUK). Tura separata: triaj mesaje generatoare.

- fir: C-4 TRANȘA 2 (coerență + TVA) [ACTIV 06.08.2026 — predare ★★; supersedează firele de mai jos] — seed 11 firme + T-1…T-7 coerente + documente D300/D394/D390/D301 pt M1/M2/P1/P2/N1/S1/S2/S3 + limite TVA L1/L2/L3/L4/L10/L12 ×3 cazuri. Metodologie identică tranșei 1: divergență = bug până la proba contrarie → vânătoare de clasă → temei la sursă → gard + RED/GREEN → DUK.
- ultim: C-5 CATALOG COMPLET (P1-P7) în date_test/C5_catalog.md — P1 (blocari: izolare gard structural test_izolare_structurala.py 243 rute×metoda + marcaje mutat; clase 1-4 catalog), P6 (cens .oblig 34 ecrane: 10 goluri dir.1 + 5 dir.2), P2 (date lipsa: stopuri fiscale exemplare; bug B17 d406 UM tacut), P3 (~140 raise-uri core/: ~55% explicit reconciliere+cota-TVA model, ~25% telegrafic; ZERO tacere fiscala), P4 (401/403/404/409/423 grupat pe sir: ~142 izolare terse-corect + goluri rol telegrafice), P5 (400/422: 208 situri, tinte rescriere email/cabinet/r.get(cod)), P7 (mecanism validare: gol cap.6 sistemic eroare-nu-langa-camp + non-enumerabil complet 34 cu motiv). Commituri 412d5df→ea1ff90, backup/lant-2026-08-06.
- urmator: C-5 CATALOG ÎNCHIS (inventar de goluri, nu rescriere - decizia Costin). Actionabil rescriere/fix = CAMPANII SEPARATE cu decizia lui Costin: (a) rescriere mesaje telegrafice (P4 rol: Nu-ai-acces/Doar-Admin/rol-insuficient prin dep central+_cer_admin_cabinet+_pachet_schema; P5: fara-cabinet-asociat x5/familia-email/r.get(cod) x12; P3: input-guards ~25% + constrangerea); (b) fix bug-uri tacere B1-B17 + info-leak operatiuni:381 (B7 cod rupt, B8 cm-sfarsit NULL, B14 urcaPoze pierde atasamente, B17 d406 UM); (c) markeri literali ' *'→.oblig; (d) mecanism eroare-langa-camp (A) in loc de zona generica (B). NU se atinge: izolare terse (corect), entity-not-found. C-4 INCHISA.
- pasi:
  T2-1. [GATA] [seed firme] date_test/seed/transa2_coerenta_tva.py: provizionare idempotentă M1,M2,P1,P2,N1,S1,S2,S3,NR1,T1,T2 sub Cabinet Prisma (fid 1968; S4=tenant_001 există deja). firma_profil per C-4 sect.D: platitor_tva, tip_decont (L/T), regim_fiscal (micro/profit), operatiuni_ic, tva_la_incasare, caen. CUI-uri C-2 (re-verificate ANAF la seed).
  T2-2. [GATA] [coerență T-1…T-7] clienti/furnizori nomenclator + facturi: la emitent directie='emisa', la primitor directie='primita', cu numar/serie, data_emitere, total, tva, tert_cui IDENTICE pe ambele laturi; factura_linii cota_tva=21. Cazuri speciale: T-6 taxare_inversa (art.331); T-3 furnizor neplătitor (tert_platitor_tva=False, tva=0); T-5 forfetar 8%. T-7 (P1→S4) folosește tenant_001.
  T2-3. [GATA] [probă coerență] → 7/7 identice, 0 divergențe (script coerenta_check) pt fiecare T-k: latura emisa(emitent) == latura primita(primitor) pe CUI/sumă/dată — raport per pereche (D394 vânzări↔cumpărări se reconciliază din date, nu prin check cross-firmă în app).
  T2-4. [PARȚIAL] [generare + DUK] P1 LUNAR D300+D394 (luni 2-6) = 10/10 DUK-VALID ✓. M2/P2 TRIMESTRIAL = BUG confirmat (perioada neagregată) → Cluster 3. D390 P1 / D301 N1 / marjă S1,S2 = neîncepute (cer seed IC extern + d301_operatiuni + marjă).
  T2-5. [limite TVA] L1/L2/L3/L4/L10/L12 ×3 cazuri (exact/−1/+1), cu lecția tranșei 1: prag−1 poate fi C-5 (date defecte), nu C-4 — verifică per prag.
  STARE = ÎNCHISĂ 06.08 tura 2. Livrate verzi: seed 11 firme + T-1…T-7; fix trimestrial D300/D394; T-6 taxare inversă; (e) T-5 forfetar orfan D300 (commit d1a2e4d, gard+RED+mutație+DUK); (b)+(c) acoperire D390 P1 / D301 N1 (test 4/4 DUK-valid + seed extins). Decizii produs consemnate GARZI: (d) marjă + (f) praguri L1/L2/L3/L10. L4 rămâne în C-4 (enforced+testat).

--- FIRELE DE MAI JOS = istoric campanii anterioare; superseate de firul C-4 activ (EXTINDEREA 05.08 punct 1 → tranșa 1 închisă; punctele 2-4 EXTINDEREA = tranșa 3 anuale). Păstrate ca traseu. ---
- fir: EXTINDEREA ACOPERIRII (campanie noua 05.08) - 4 puncte: 1.D112 cazuri complexe, 2.D101 impozabil, 3.amortizare MF neliniara, 4.tip_document 2-5 D394
- ultim: Punctul 1 sub-caz 1c-PT LIVRAT - PART-TIME suprataxare: CAS+CASS reconciliate pe baza ridicata. Acoperire ~35-50%->~40-55% est.
- urmator: Punctul 1 sub-caz 1c-CM BLOCAT: decizie de produs (poarta cale2 OARBA pe CM + candidat bug baza salariala CM). Vezi GARZI 05.08 "DESCOPERIRE 1c-CM". Urmatorul actionabil FARA decizie = Punctul 2 (D101 ajustari computed).
- pasi:
  P1a. [GATA] facilitate la minim stabila toata luna: baza=sm-fac, CAS+CASS; _stabil_la_minim SQL propriu; rotunjire la intreg ca _d112int. Prorata ramane sarita.
  P1b. [GATA] TICHETE DE MASA (angajat peste minim, luna intreaga, fara CM/part-time/scutire/alte beneficii). CAS reconciliat, CASS numit-afara.
       Proba: 6000+tichet40, pontaj confirmat -> cas=1500/cass=600(salarial)/cass_tichete=84; reconciliat_cas_doar; mutatie cas PICA; mutatie cass NU pica.
       RED probat pe codul vechi (tichete inca sarite / cheia reconciliati_cas_doar inexistenta). test_d112_reconciliere.py 8->10.
  P1c-PT. [GATA] PART-TIME suprataxare (art.146 alin.5^6). Emis = max(brut, sm-fac) x cota; sub prag -> cas_min_pt/cass_min_pt. Proba: id10 brut2025->cas_min_pt938/cass375 reconciliat; id11 brut8000->cas2000; mutatie pica. RED probat. test 10->12.
    c1. core/d112_reconciliere.py: skip part_time (l.139) -> flag este_pt (pastreaza skip scutit_contrib_minim = si scutit_pt).
    c2. Dupa filtrele cm/ben/luna-intreaga, ramura part-time INAINTE de brut==sm: prag=sm-fac_val (full month, fara CM -> fara proratare);
        baza_pt=max(brut, prag); emis = cas_min_pt/cass_min_pt daca pt_aplica altfel cas/cass; confrunta emis vs _q(baza_pt x cota).
    c3. part-time + tichete = combo ulterior -> sarit. Reconciliaza CAS+CASS complet (emis pe baza ridicata).
    c4. test: part-time SUB prag (brut 2025 -> emis cas_min_pt=938/cass_min_pt=375) reconciliat; part-time PESTE prag (brut 8000 -> cas=2000) reconciliat; mutatie pica.
  P1c-CM. CONCEDII MEDICALE (OUG 158/2005): baze/procente proprii (CAS 25% uniform, CASS doar 01/07/10). NEINCEPUT - sub-caz separat, mai mare.
    b1. core/d112_reconciliere.py: skip-ul neconditionat pe tichet_masa_valoare (l.141-142) -> flag are_tichete_masa.
        Skip ben_ids RAMANE (garanteaza fara vacanta/cultural/cresa in beneficii_lunare -> exces_vac=0 -> DOAR tichete de masa).
    b2. branch caz-simplu (brut>sm) + are_tichete_masa: confrunta DOAR cas (=_q(brut x cota_cas)); sid -> reconciliati_cas_doar.
        CASS numit-AFARA: d112.py:239 cass += cass_tichete -> baza CASS emisa (brut x cota_cass + cass_tichete) != brut x cota_cass.
    b3. branch facilitate (brut==sm) + are_tichete_masa: SARIT (combo facilitate+tichete = sub-caz ulterior, numit).
    b4. return: cheie noua reconciliati_cas_doar; docstring/header: 1b acopera CAS, CASS numit-afara. Non-tautologie AST neatinsa (fara importuri noi).
    b5. test: salariat tichete>minim + pontaj confirmat (perioada.confirma "pontaj"); pull emite cass>brut x cota_cass (cass_tichete>0);
        reconciliaza pass pe CAS; mutatie cas -> PICA; mutatie cass -> NU pica (proba ca limita CASS-afara e reala).
  STARE = BLOCAT: decizie de produs pe 1c-CM (vezi GARZI 05.08 DESCOPERIRE 1c-CM). Punctul 2 (D101) e urmatorul actionabil.


Firul curent — de aici derivă URMATORUL PAS al agendei. Se ține la ZI (regula de
redirecționare: ce se lucrează intră aici ÎNAINTE de a începe).

> **Stare:** site în mentenanță (46507b5) — allowlist pe IP-ul lui Costin; revenire cu `mentenanta.sh off`.

- fir: GARDUL DE CONTINUT — a doua cale D300 (campanie noua 05.08.2026; golden full-decl BLOCAT la sursa, vezi mai jos)
- ultim: ritual pornire + agenda_drift curat; inventar anaf_surse CONFIRMA: niciun exemplu ANAF completat cu cifre (ebb834a).
- urmator: [GATA 05.08] CAMPANIA GARDUL DE CONTINUT COMPLETA 6/6 (D300 3096812, D394 6f19ebe, D112 06dc9df+69f83f3, D406 661d6ae, D101+D205 93e4a2c). Fiecare: recalcul independent + non-tautologie AST + mutatie + hard-block + limita declarata. Directia (a) golden full-decl ramane blocata la sursa. Firul e INCHIS.
- CONTEXT CAMPANIE: DUK valideaza STRUCTURA, nu semantica. Directia (a) "golden din exemplu oficial ANAF" e BLOCATA LA SURSA — anaf_surse/ NU contine nicio declaratie completata cu cifre (verificat 05.08, grep/find pe tot repo-ul); ANAF publica structura+instructiuni, nu declaratii-model. Gardul de continut real = directia (b): A DOUA CALE de reconciliere pe totaluri. Ordine confirmata Costin: D300 -> D394(vs D300) -> D112 -> D406 -> D101/D205.
- pasi:
  C1. [core/d300_reconciliere.py NOU] Calea 2: pull SQL PROPRIU al liniilor brute (independent de d300.pull), agregare proprie pe cote (independenta de calcul_d300/_segmente), Sigma(baza)xcota, rotunjire aritmetica ROUND_HALF_UP. Confrunta cu randurile AUTOMATE ale generatorului (R9/R10/R11 colectat, R22/R23 deductibil). Divergenta = EROARE VIZIBILA care numeste ambele valori; NU repara tacit. Sare randurile atinse manual + tva_la_incasare (NEACOPERIT, nu alarma falsa). Wire in d300.genereaza (poarta inainte de return). NON-TAUTOLOGIE probata static (test) + MUTATIE (factura pierduta / cota in bucket gresit / semn inversat -> reconcilierea pica). Proba functionala pe schema efemera, ROLLBACK. Limita in GARZI cat.4 la DESCHIDERE.
  STARE = GATA (C1 comis 3096812; suita 1391 passed +7, verificator 0; non-tautologie+mutatie probate)
  C2. [core/d394_reconciliere.py NOU] D394: recalcul PROPRIU al rezumat2 pe cota (bazaL/tvaL/bazaA/tvaA, C->A) din liniile brute; poarta HARD-BLOCK in d394.genereaza. NU cross-recon vs D300 (paritatea existenta e tautologica; D300>=D394 nu e egalitate). Acoperire: tot traficul auto (taxare-inversa/N incluse); manual= nealimentat azi = reziduu. Non-tautologie AST + mutatie. Comis 6f19ebe.
  STARE = GATA (C2 comis 6f19ebe; suita 1397 passed +6, verificator 0)
  C3. [core/d112_reconciliere.py NOU] D112 CAZUL SIMPLU: CAS/CASS = brut x cota per angajat (brut peste minim, fara CM/part-time/scutire/tichete, luna intreaga), din brut+SQL propriu, cotele din registrul de lege. Poarta HARD-BLOCK in d112.genereaza. Facilitati/CM/impozit/CAM = AFARA (declarat, nu 'acoperit'). Non-tautologie pe lant TRANZITIV + mutatie. Comis 06dc9df.
  STARE = GATA (C3 comis 06dc9df; suita 1402 passed +5, verificator 0; cazul simplu, restul declarat afara)
  C4. [core/d406_reconciliere.py NOU] D406/SAF-T: balanta de rulaje per cont INDEPENDENTA din inregistrari_linii, legata de SAF-T emis (res.note) + invariant Sdebit=Scredit. Poarta HARD-BLOCK. Prinde GL gol (bug istoric)/drop/mapare gresita. Acopera GeneralLedgerEntries, NU facturi/plati/active. Non-tautologie AST + mutatie. Comis 661d6ae.
  STARE = GATA (C4 comis 661d6ae; suita 1409 passed +5, verificator 0)
  C5. [core/d101_reconciliere.py NOU] D101 PROFIT CONTABIL: recalcul independent P1/P2/P4/P5 (venituri/cheltuieli clasele 7/6) din inregistrari_linii vs res.P. NU impozabilul (ajustari manuale §8 + golden). Poarta HARD-BLOCK. Non-tautologie AST + mutatie. Comis 93e4a2c.
  C6. [core/d205_reconciliere.py NOU] D205 DIVIDENDE: recalcul independent baza+impozit per beneficiar (Σ457 x cota asociat x cota lege) vs res.beneficiari. NU cross-check D100 (same-source trap, probat AST). Poarta HARD-BLOCK. Mutatie. Comis 93e4a2c.
  STARE = GATA (C5+C6 comise 93e4a2c; CAMPANIE COMPLETA 6/6; suita 1417 passed, verificator 0)

- fir: motor cluster "rezerva legala" — formula contabila CONFORMA (gard) + deductibilitate fiscala art.26(1)a = decizie produs (lant)
- ultim: credit sponsorizare|sponsorizari profit conform + datorie micro (5d1f5e8).
- urmator: cluster inchis (formula contabila gardata + deductibilitate fiscala = decizie produs). Ruleaza urmator_cluster(). GATA.
- pasi:
  RL1. [verificare + decizie] Formula rezervei legale CONTABILE (motor.py: 5% profit, plafon cumulat 20% capital - rezerva existenta) = CORECTA structural (Legea 31/1990 art.183, OMFP 1802/2014 pct.421), period-aware. Lipsea test NUMERIC (doar tautologic). Gard golden adaugat. NECONFORMITATE: deductibilitatea FISCALA CF art.26(1)a (baza = profit contabil + cheltuiala cu impozitul, plafon 20% capital subscris/varsat) LIPSESTE complet - nu se calculeaza nicaieri; d101 P6 "Deduceri fiscale" e input manual. = DECIZIE DE PRODUS (implementare + legare in d101 schimba declaratia de profit). motor.py e cod MORT (niciun apelant productie) - observatie. Commit.
  STARE = GATA (RL1 comis)

- fir: SWEEP DUK toate declaratiile (redirectionare Costin 31.07: inainte de reconstructii, mapez cate sunt sparte pe validatorul CURENT)
- ultim: sweep rulat pe schema efemera + profil complet + date minime adecvate (salariat/factura UE/dividende). Rezultat initial: 7 VALID + 2 sparte (d101, d406). d406 REZOLVAT 01.08 (bug de CALE, o linie): plan_oficial cauta d406_nomenclatoare_anaf.properties in radacina, dar fisierul e in anaf_surse/ -> set gol -> filtrarea pe norma (adaugata 15.07 tocmai pt 731 ONG) nu rula -> conturi ONG scapau in SAF-T comercial -> DUK respingea. Fix cale -> plan_oficial(A)=635, 731 exclus, d406 DUK VALID. RAMANE 1/9 SPART: d101 (reconstructie). Claim 16.07 infirmat.
- urmator: gard smoke-sweep DUK livrat (8 valide asertate incl d406 reparat + d101 xfail). d406 REPARAT (fix cale). RAMANE 1 reconstructie: d101 - cere greenlight temei OPANAF 206/2025. Posibil edge d394 (luna doar UE -> R112.3) de confirmat separat. BLOCAT: cere decizie d101.
- pasi:
  1. [GATA] sweep no-data + sweep cu date (salariat/factura UE) -> 7 valid / 2 sparte.
  2. reconstructie d101 (temei OPANAF 206/2025 validat) - cand Costin da drumul.
  3. [GATA 01.08] d406 reparat (fix cale plan_oficial -> anaf_surse/); gard test_d406.test_plan_oficial_citeste_nomenclatorul.
  4. [GATA 01.08] gard smoke-sweep DUK permanent: core/test_smoke_duk.py.
  STARE = BLOCAT: sweep+gard+d406 reparat; ramane d101 (reconstructie) - cere greenlight temei


- fir: REZOLVAT 03.08.2026 - D101 RECONSTRUIT si DUK-VALID. Clusterul structura-P1-P53|d101 bifat 03.08 (test_d101_reconstructie_proba_duk_valid + test_imca_d101_duk_valid TREC azi). Blocul de mai jos e ISTORIC (starea pre-reconstructie 31.07: D101 respins de DUK, nu poate fi depusa) - pastrat ca traseu, NU mai e valabil. test_datorie_d101_build_xml_respins_de_duk a fost SCOS la reconstructie. [citare-istorica: scos la reconstructia D101 03.08]
- ultim: descoperit la C2 - DUK respinge 'sectiune necunoscuta (P1)' (P-values ca elemente <P1>) + cod_bug=5503XXXXXX placeholder literal. Consemnat test_datorie_d101_build_xml_respins_de_duk. [citare-istorica: scos la reconstructia D101 03.08]
- urmator: INVESTIGARE (metoda D1xx CLAUDE.md): extrag structura reala din D101Validator.jar (ultima versiune, constant pool), gasesc forma corecta P/cod_bug, construiesc XML minim valid pe DUK (o corectie/runda), PROPUN cu temei -> Costin valideaza -> implementez. IN LUCRU.
- pasi:
  1. localizeaza D101Validator.jar, versiunea maxima; unzip + strings pe clasele declaratiei; citeste TOATE atributele/elementele reale (P1..P16: element vs atribut? container?).
  2. cod_bug real pentru cod_obligatie 103 (impozit profit) - din nomenclator/validator, nu placeholder.
  3. XML minim construit manual, validat pe DUK sectiune cu sectiune pana la 'valid'.
  4. verifica clasa: d112 emite si el cod_bug=5503XXXXXX (add_oblig) - aceeasi problema? generalizare.
  5. PROPUNERE cu temei -> validare Costin -> implementare d101.py + test proba DUK + mutatie + gard.
  --- INVESTIGARE GATA 31.07 (metoda D1xx aplicata) ---
  CAUZA + SCOP REAL: D101 nu e fix mic, e RECONSTRUCTIE. (1) build_xml emite P ca ELEMENTE <P1> -> validatorul le respinge ca sectiune; corect = ATRIBUTE pe <declaratie101> (probat pe DUK: eroarea P1 dispare). (2) calcul_d101 a INVENTAT o numerotare proprie (cod: p11=impozit, p9=baza) care NU corespunde formularului oficial. Oficial (OPANAF 206/2025, D101_A600 v9/v10, anaf_surse/d101_struct_anaf.txt): ~53 campuri P cu lant de formule - P3=P1-P2, P6=P4-P5, P7=P3+P6, P8>=SUM(P081..P084), P10=P7+P8-P9, P16=P11+..+P15, P21=P17+..+P20, P22=P10-P16-P21, P34=SUM(P23..P33), P35=P22+P34, P38a=P35+P36+P37-P38, P40, P41=P411+P412 (=IMPOZIT PE PROFIT), P42=P421+P422+P423, P43, P48, P52, P53; totalPlata_A=SUM(P1..P53). Reguli: R17.1 scadenta (an_S>2025 => LL+3, cod foloseste LL+6 gresit + inconsistent cu nr_evid), R38 rezultat brut, R41 P41=P411+P412, grup (d_grup) etc. cod_bug=5503XXXXXX pare FORMAT ACCEPTAT (d112 il emite si trece) - nu e problema.
  DECIZIE CERUTA COSTIN: reconstructie D101 (rescrie calcul_d101 pe P-urile oficiale + build_xml cu P atribute, validat iterativ pe DUK pana la valid, gard test DUK) - GREENLIGHT temeiul (OPANAF 206/2025 + structura oficiala)? Campanie coheziva (un formular nu se face pe jumatate), mare. Alternativ: bounded first step sau amanat.
  COLATERAL: claim-ul 16.07 "toate 9 valide pe DUK" e nesigur - D101 clar nu e; d100/d205 confirmate azi (probele mele), d112/d390/d301/d406 NEREVALIDATE azi pe DUK curent (posibila deriva de versiune validator).
  STARE = BLOCAT: investigare gata, cere decizie temei/scop (reconstructie D101)

- fir: Contract uniform A1 - conversia generatoarelor ramase la contractul {pull, erori_generare, calcul_dNNN, build_xml, genereaza(conn,schema,perioada,...)} (Sesiunea A - arhitectura). Baseline verificator CONTRACT 6, coboara cu 1 la fiecare modul convertit.
- ultim: modul 7/10 d205 la contract (pull+genereaza(perioada); adaptor _d205; manual strict cheie_manual; DUK d205 valid; baseline 4->3). Convertite: d300,d301,d394,d710,d100,d101,d205. C (d100/d101/d205) GATA. DE DECIS (Costin): D101 build_xml respins de DUK (nu poate fi depusa) - campanie separata structura D101? Consemnat test_datorie_d101_build_xml_respins_de_duk. [citare-istorica: scos la reconstructia D101 03.08]
- urmator: D1 - d112 (modul 8/10). RISC STRUCTURAL real (SCOPAT 31.07): d112 are DEJA pull+erori_generare; lipsesc calcul_d112+build_xml, ambele inghesuite in _d112_genereaza(prof,salariati,an,luna) ~250 linii unde calculul si XML-ul sunt IMPLETITE in aceeasi bucla per-salariat (fiecare <asigurat> emite XML imediat dupa ce-si calculeaza zecile de valori B1/B2/B3/B4/D/E1/E3 + part-time/CM/tichete; agregatele sum_imp/cas/cass/cam + C1/C2 se acumuleaza in bucla si intra in antet). Fara cusatura curata. Extragerea fidela cere Rezultat care poarta FIECARE valoare din XML (inclusiv randurile B3/D structurate) + proba golden-XML byte-identica pe fixturi ce ating toate ramurile. NEINCEPUT - cere greenlight (vezi DE DECIS).
- pasi:
  C1. [d100] pull(conn,schema,perioada)->(prof,venituri); genereaza(conn,schema,perioada,manual=None): cota din manual (cheie_manual(manual,"cota")), an=perioada.an, luna=perioada.trim*3, guard trim 1-4; adaptor _d100 -> Perioada(an,trim=), manual={"cota":..}. RED contract + mutatie + proba efemera. Baseline 6->5.
  C2. [d101] pull(conn,schema,perioada)->(prof,r{venituri,cheltuieli}); genereaza(perioada,manual); adaptor _d101 -> Perioada(an). Baseline 5->4.
  C3. [d205] pull(conn,schema,perioada)->(prof,asoc,total_div); genereaza(perioada,manual) override manual castiga; adaptor _d205 -> Perioada(an). Baseline 4->3.
  D1. [d112] extragere structurala calcul_d112/build_xml din genereaza (RISC - OPRIRE la regresie). Baseline 3->2.
  D2. [d406] idem (RISC). Baseline 2->1.
  d390-LA-URMA. 3 pull-uri impletite cu override + 2 consumatori -> 1 pull public + reclasificari->manual. Baseline 1->0.
  A2. except goale (7 codebase: d406=3 + tenant_provisioning/observare/gdpr_sterge/cron): tratat+documentat ori eliminat, niciunul gol; gard.
  A3. mutant zero sistematic: fiecare din 11 generatoare cu sursa->[] => suita PICA (test permanent, garzi cat.9).
  STARE = REFACTOR OPTIONAL, NEINCEPUT (D1 d112: extragere structurala calcul_d112/build_xml din genereaza = ARHITECTURA/contract uniform, NU blocaj fiscal - d112 e verificat + DUK-valid in clusterele bifate. Se ia doar daca se reia conversia la contractul uniform; nu blocheaza nimic fiscal.)

- fir: Granite API — cota TVA lipsa = intrare incompleta -> eroare, nu default 21 (Sesiunea A · TVA, sub-fir temeiuri)
- ultim: masurare livrata — 80 cote "fara temei" = 79 TVA reale (1 fals-poz), 3 valori (21/11/19), cluster TVA verificat, 0 de cercetat / ~20 granite de reparat, rest ACCEPTATE (etaloane/fixtures/parametri). Directie confirmata Costin: default ELIMINAT, nu inlocuit; nedeterminat != 21; scutit 0 pastrat.
- urmator: GATA (31.07.2026, commit-uri 4ef863c..c11a1d4). 6 teme comise, fiecare rosu->verde->mutatie: (A) 16 endpoint-uri; (B) emitere nedeterminat; (C) cota 0 + date stocate; (D) registru GRI (80->2 baseline); (E) proba D300 scutit -> DUK VALID. Ramas descoperit: 2 GRI de agregare (main:4045/4046, temei cunoscut) + auto-match AI propune cota cu incredere mica la produs nou ambiguu (transparent, corectabil - NU tacut).
- pasi:
  1. [tema A] cota_ceruta(corp) helper (HTTPException 422 la None, 0 valid) + cele 16 endpoint-uri main.py + RED + mutatie.
  2. [tema B] potriveste_cota: 4 fallback-uri -> NEDETERMINAT (nu 21); produse_api.creeaza + _potriveste_linii ridica; dead ,21 eliminat; LinieIn->Optional=None; storno cota. RED: AI picat + linie fara cota -> emitere blocata.
  3. [tema C] produse_api:46 bug cota-0 (or 21 -> distinge None/0) + granite date stocate (main:6291, reconciliere:177, stocuri adauga_nir). RED: cota 0 ramane 0.
  4. [tema D] verificator: gard GRI cota (verde/gri/rosu, listat) + baseline recompute + ACCEPTATE.
  5. [tema E] proba D300 + factura scutita (cota 0) -> DUK VALID (lectia D3).

- fir: Temeiuri citabile mecanic + reverificarea locurilor fără temei (Sesiunea A · transversal)
- ultim: runda 4 comisă — (B) gardă bump-motiv: o bifă din Inventar A mutată înainte cere motivul scris în coloană, altfel garda anti-stale devine ornament (105ef50); (C/FIX5) salariu minim 2025 corectat 4050 → HG 1506/2024 (era 3700 = valoarea 2024 H2, act greșit), datorie xfail închisă și consemnată în DECIZII.md (cf31ddb); (A) confirmat că plafonul deducerii e DERIVAT (salarizare.py: sm+2000), zero literal 6050/6325 → niciun bug activ (semestrul 2: sm=4325 → prag=6325 automat). Fiecare fix: roșu→verde→mutație, commit separat.
- urmator: CORECTIE REGULA temei 01.08 GATA (3 etape). (1) corectie DECIZII (ab0f359); (2) data_out ESTIMAT pe 7 valori + gard nicio-cota-fara-data_out (4c23994); (3) 2 GRI atasate (tva_redusa in COTE + main.py period-aware) + GRI_BASELINE 2->0 PRAG. Temei structurat=0, GRI=0. Ambele garzi in PRAG. GATA markeri TEMEI functie 01.08: criteriu structural EVALUAT (57 prinse, 5/7, ~18 fals-poz rotunjire) si RESPINS -> lista EXPLICITA (salarizare 6 functii salariu/CM), toate 6 marcate ACUM, gard verificator PRAG 0. DECIZII 01.08. Limita: nu auto-detecteaza (alte clustere se adauga la confirmare).
- pasi:
  · [GATA] §3.1 format · inventar (60 clustere, 4 √) · core/temeiuri.py (CLI) · gard validator-regulă · garda anti-stale per funcție.
  · [ÎN CURS] 2b — locuri fără temei, pe CLUSTER, cu validarea ta: deducere personală [√ 31.07] → tichete → concedii medicale → apoi celelalte 10 module.
  · [GATA 31.07] Temei STRUCTURAT (etapele 1-4): common.Temei(act/.../data_out) pe toate cotele COTE; cota() ridica la expirare (data_out = mecanism principal de deriva, nu proxy); gard ratchet in verificator; Inventar A generat partial + overlay persistent; GARZI cat.3 = limita reala (schimbare de lege intre data_in si data_out nu e detectabila). Commit-uri 3c37bfa..9ed8899.
  · [RĂMAS] cele 113 citări normative (decizia #1) · datoriile xfail deschise.

- fir (în așteptare): Modelarea contractului în timp (Sesiunea A · salarizare)
- ultim: 2b-scrieri comis — creare/editare/import scriu pe salariu_istoric, citiri pe salariu_curent (reparat si bug-ul activ din import, PASUL 1)
- urmator: 2b-coloană — DROP salariati.salariu_brut din tabel + migrare, UI schimbare salariu (valabil_din), scoaterea bridge-ului salariu_la. NEÎNCEPUT.

---

## Implementarea modelului de temei (01.08)
- ETAPA 1 [GATA]: data_out=None pe curente + derivare din succesor + verificat_la/de_cine + EXPIRA_DUPA_LUNI scos + cota() ridica doar pe gol real + gard inversat + raport cote_neconfirmate (expirare_cote reformulat). Alerta email aliniata (fara expira/REFUZA pe curente).
- ETAPA 2 [NEINCEPUT]: text_citat + nivel_sursa + lant_acte pe cele 12 COTE + 6 functii; gard nivel_sursa obligatoriu.
- ETAPA 3 [GATA]: core/graf_temei.py - analizor AST cota("x") + inchidere tranzitiva. Proba: depinde_de("salariu_minim")=12 functii (deducere_personala+calcul_salariu DIRECT; sub-conceptele facilitate/plafon12sm/suprataxare/prag-tineri traiesc IN ele, vazute prin ele). Limita: literal hardcodat ocoleste graful (gardul GRI la 0 = conditia). Pct.7 nedecis (masurare, alta tura).

# SESIUNEA A — alinierea la legislație

## Problema

Un test poate fi corect tehnic — izolat, curat, cu mutație dovedită — și complet inutil,
dacă afirmă **ce face codul** în loc de **ce cere legea**.

Trei cazuri, toate cu suita verde luni de zile:

- **D301** — regula că secțiunea 4.1 se preia DIN secțiunea 4 (OPANAF 592/2016) nu era
  scrisă nicăieri. Generatorul o încălca, ANAF respingea declarația pe cazul cel mai
  frecvent (servicii UE). Nu exista **niciun** test pe D301.
- **D390** — rotunjirea era bancară (`round()`), deși D112 documenta în cod că ANAF cere
  aritmetică și că cea bancară fusese RESPINSĂ de validator (regula A91b). Ambele treceau.
- **Limita de 75 de caractere** — respectată în 6 din 11 locuri unde se emitea numele
  declarantului. Niciun test n-o afirma; jumătatea nerespectată a trăit până când ANAF a
  respins declarația unei firme cu denumire lungă.

Cauza e aceeași: testele reproduceau implementarea. Un test scris din citirea codului
**încremenește codul, inclusiv greșelile lui**.

**Observație de metodă (29.07.2026).** Verificarea la sursă a unui singur test (facilitatea la
salariul minim) a scos trei fațete ale aceleiași lipse de model — contractul n-are dimensiune
temporală. Nu s-ar fi văzut din cod: fiecare fațetă arată ca un caz izolat până când se citește
articolul întreg, care le enumeră pe toate patru într-un singur alineat.

## Regula

**Orice test care afirmă o valoare, o cotă, un prag, o rotunjire sau o structură fiscală
citează temeiul lângă assert.** Nu într-un document separat — pe linie, unde se vede când
cineva îl modifică.

```python
# FĂRĂ sursă — reproduce formula din cod, nu apără nimic:
assert calcul_tva(1000, 21) == 210

# CU sursă — afirmă regula, pică dacă cineva „optimizează" implementarea:
assert _int(112.5) == 113   # ANAF cere rotunjire ARITMETICĂ, nu bancară.
                            # D112 regula A91b: CAM calculat 112, cerut 113 (respins de validator).
```

## Ce se face când temeiul lipsește

**Dacă regula nu e verificată la sursă, testul NU se scrie.** Se pune `xfail(strict=True)`
în `core/test_datorie.py`, cu motivul „temei neverificat: <ce anume>".

Un test scris pe presupunere e mai periculos decât absența lui: dă siguranță falsă, iar
când cineva îl vede roșu repară **codul** ca să se potrivească cu presupunerea.

Pe 27.07 era să se întâmple: cerusem ca `total_plata_A` la D301 să se calculeze din
secțiunile 1–4. Verificarea empirică la DUK a arătat că ANAF impune altceva (regula R28,
checksum peste toate cinci). Dacă testul se scria pe acea presupunere, generatorul ar fi
fost „reparat" ca să producă o declarație pe care ANAF o respinge.

## Cum se lucrează în sesiunea A

**Un test o dată. Se validează, apoi următorul.** Fără fragmentare pe alte subiecte: în
sesiunea A se aliniază produsul cu specificațiile legale, atât.

Pentru fiecare test:

1. **Ce afirmă azi** — se citește testul existent, nu se presupune.
2. **Ce cere legea** — se verifică la sursă oficială (Cod fiscal, OMFP, OPANAF, OUG,
   instrucțiunile formularului). Se notează temeiul exact: act, articol, alineat.
3. **Se compară.** Trei rezultate posibile:
   - **coincide** → testul se rescrie cu temeiul citat pe linie;
   - **diferă** → **e reparație fiscală, nu rescriere de test.** Se repară codul, cu
     dovadă (validator, zero regresie), apoi testul;
   - **legea nu spune** → nu se scrie test. `xfail` în `test_datorie.py` cu „temei
     neverificat".
4. **Se validează** înainte de a trece mai departe.

Rezultatul sesiunii A: o suită care afirmă legea, nu implementarea.

## PREDARE PART II (02.08.2026) — mecanismul de localizare act -> clustere (PART I livrat, PART II ramas)

PART I LIVRAT (condiile, in ordine): V1 inventar complet + criteriu (43b2f5c), V2 graful vede doar prin cota()
(609cc6b), V3 resetarea propagata pe graf + ratchet stale (a8889b8). Fundament pe care se sprijina PART II:
- core/temeiuri.py: gaseste(act) -> locurile din core/*.py care CITEAZA actul (substring, forme partiale).
- core/agenda.py: cote_cluster(rand) -> cotele de care depinde un cluster (test->sursa->graf). stare_sesiune_a()
  -> randurile inventarului (cluster, modul, Temeiuri, Functie(test)).
- core/graf_temei.py: depinde_de(cota) -> functiile care depind de o cota (direct/tranzitiv).
- common.COTE: fiecare valoare cu Temei (act/nr/an/art + lant_acte).

PART II - de construit (core/localizare.py + test cu probele):
1. INDEX act -> clustere, din temeiuri atasate:
   - cote_lovite(act) = cheile COTE al caror Temei (str + lant_acte) contine actul.
   - clustere_direct(act) = randuri din inventar a caror coloana Temeiuri contine actul.
   - functii(act) = temeiuri.gaseste(act) (markeri TEMEI + obiecte Temei in cod).
   - clustere_indirect(act) = randuri cu cote_cluster(rand) ∩ cote_lovite(act) != {}, MINUS clustere_direct
     (lovite prin VALOARE din graf - marcate DISTINCT de cele lovite direct prin citare).
   - declaratii(act) = modulele clusterelor lovite (d100..d710, salarizare, + orfanele V1).
2. INTEROGARE(act) -> {clustere_direct, clustere_indirect, cote, functii, teste=Functie(test) ale clusterelor
   lovite, declaratii}.

PROBE (de rulat, output brut):
- Legea 141/2025 -> TVA (tva_standard/tva_redusa citeaza) SI concedii (Temeiuri: 'Legea 141/2025 si 136/2020';
  modifica art.17 OUG 158/2005). Daca lista e INCOMPLETA -> granita intre clustere e trasata gresit: repara
  GRANITA, nu interogarea (ramificatie: tichete culturale/cresa vs masa/vacanta - Legea 165/2018 le da pe toate 4).
- OUG 158/2005 si art.77 CF -> verificat MANUAL ca listele sunt complete.
- salariu_minim (COTA, nu act) -> reverse-graf: deducere, facilitate, plafon 12 sm, suprataxare part-time, prag
  tineri, tichete vacanta. RISC CUNOSCUT (V2): 'tichete vacanta' (plafon 6 sm, beneficii_api) poate sa NU apara
  daca plafonul e hardcodat, nu cota() - atunci graful nu vede dependenta -> spune care si de ce (blind spot V2).

RAMIFICATII PART II: (a) act cu lista incompleta -> repara GRANITA de cluster; (b) daca repararea granitei ar
CADEA vreo bifa -> OPRESTE, raporteaza (nu reseta singur - vezi si cele 3 stale de la V3); (c) daca lista testelor
fara cluster trece de ~20, gard pe ratchet.

DE DECIS COSTIN (din V3, deschis): 3 bife 29.07 (suprataxare part-time, proratare, suprataxare prag) sunt STALE -
stau pe salariu_minim 2025 corectat 3700->4050 dupa √. De reverificat la sursa. Ratchet baseline=3 in test_agenda
le tine vizibile fara sa le reseteze; la reverificare, coboara baseline-ul.

## PAS 1 (02.08.2026) — forma grafului de dependente intre clustere (masurat inainte de secventa)

Edge A->B (A dupa B) = o functie a lui A (testele lui -> functii-sursa -> inchidere pe graf_temei) atinge o
functie DETINUTA de B, fara co-locatie (functie partajata = fatete, nu dependenta). Cifre:
- TOTAL clustere: 70. RADACINI (zero dependente): 63. Cu functii mapate (via teste): 8.
- ADANCIME MAX a lanturilor: 2 (facilitate -> deducere). Muchii: 7, TOATE in familia salarizare.
- CICLURI: 1 -> `facilitate salariu minim <-> deducere personala` (co-locatie in calcul_salariu: calculul net
  foloseste deducerea; deducerea si facilitatea traiesc in aceeasi functie). NU il tai singur (decizie Costin).
- COMPONENTE cu >1 nod: 1 (7 clustere: facilitate, deducere, suprataxare part-time, proratare, suprataxare prag,
  contributii PFA, impozit dividend). Restul 63 = izolate.

Muchii reale: facilitate->deducere; suprataxare part-time->{deducere,facilitate}; proratare->{deducere,facilitate};
deducere->facilitate; suprataxare prag->facilitate; impozit dividend->facilitate; contributii PFA->facilitate.

CONSECINTE:
- Ordinea CONTEAZA PUTIN: adancime 2, 63/70 radacini -> campania e aproape LINIARA (departajare, nu lant lung).
- Ciclul e INTRE CLUSTERE BIFATE (facilitate+deducere = √) -> NU blocheaza secventa celor NEBIFATE. Cele 2 nebifate
  din componenta (contributii PFA, impozit dividend) depind doar de facilitate (bifat) -> LIBERE. Deci toate
  clusterele nebifate sunt libere: secventa = departajare determinista, nu sortare pe lant.
- Cele 63 izolate: structura/declaratii care depind doar de cote de BAZA (deja verificate cu temei), nu de alte
  clustere. Dependentele ascunse cunoscute (d100/d212) au fost rutate prin cota() (campania anterioara) -> graful
  le vede acum. Nu s-au gasit alte clustere invizibile grafului la aceasta masurare.

## Secventa de verificare (persistata 02.08.2026 - NU se recalculeaza la fiecare rulare)

Ordine DETERMINISTA a celor 64 clustere nebifate+neblocate, sortare topologica pe graf_clustere + departajare
(a) FISCAL>STRUCTURA (b) deblocari desc (c) ordinea inventarului. Rescrisa 02.08: tichete masa/vacanta BIFAT ->
iesit din secventa (65->64); concedii medicale (salarizare+d112) INCHISE 02.08 -> 64->62; tichete culturale (functionalitate noua livrata) INCHIS 02.08 -> 62->61. tichete cresa (functionalitate noua livrata) INCHIS 02.08 -> 61->60. cota profit 16% + IMCA (cota verificata + IMCA implementat art.18^1) INCHIS 02.08 -> 60->59. amortizare|d101 (tratament art.28 aliniat; datorie MF metode) INCHIS 03.08 -> 59->58. baze contributii|d112 (cotele CAS/CASS/imp/CAM rutate period-aware prin COTE, value-preserving, aliniere Sesiunea A) INCHIS 03.08 -> 58->57. rotunjire aritmetica (A91b)|d112 (contributii aritmetice verificate; REPARAT minimul part-time care rotunjea bancar in B4_*P declarat) INCHIS 03.08 -> 57->56. sect_II tip_venit|d205 (structura OPANAF 102/2025 verificata; REPARAT impozit dividende hardcodat 10% -> period-aware 16%/2026 Legea 141/2025) INCHIS 03.08 -> 56->55. rotunjire|d205 (sumele fiscale rotunjesc aritmetic - verificat, deja corect prin _i ROUND_HALF_UP; gardat cross-generator + proba) INCHIS 03.08 -> 55->54. cote TVA->randuri|d300 (livrari 21/11/9 corecte; REPARAT achizitii deductibile 11% R74->R23 si 9% R76->manual, proba DUK; datorie 9% auto) INCHIS 03.08 -> 54->53. exigibilitate/TVA la incasare|d300 (IMPLEMENTAT art.282/297 OUG 8/2026: exigibilitate din decontari, suta marita, proportional, proba DUK) INCHIS 03.08 -> 53->52. taxare inversa|d300 (rd.12 reparat - R12_ lipsea din allow-list; GRI reverse-charge reconfirmat la sursa art.331+structuri) INCHIS 03.08 -> 52->51. pro-rata deducere|d300 (verificat corect art.300 - R31 ajustare Rd.33, net R28xpro_rata; gap de acoperire inchis + proba DUK) INCHIS 03.08 -> 51->50. rotunjire aritmetica|d300 (verificat aritmetic ROUND_HALF_UP, deja in gardul de identitate; proba d300-specifica) INCHIS 03.08 -> 50->49. ajustari|d300 (REPARAT R29/R30/R35/R36 aruncate din allow-list - ajustari/regularizari nedeclarate; proba DUK) INCHIS 03.08 -> 49->48. tipuri operatiune 1-5|d301 (verificat maparea tip->sectiune OPANAF 592/2016; gard tipuri 1/2/3 + proba DUK toate 5) INCHIS 03.08 -> 48->47. rollup S4.1->S4|d301 (verificat COMPLET - S4.1 subset din S4 OPANAF 592/2016, TVA nedublat, checksum, proba DUK; test_d301_rollup.py dedicat) INCHIS 03.08 -> 47->46. baza=val x curs|d301 (verificat CF art.290 alin.(2): baza=elemente_valuta x curs BNR/BCE la exigibilitate, rotunjire ROUND_HALF_UP corecta; REPARAT fabricare tacita curs=1 pe valuta - gard calc_baza pe None/<=0 + scos or 1 din generator+reader + scos DEFAULT 1 din schema; proba 1000x4.977=4977 / EUR fara curs->ValueError / RON=1->1234) INCHIS 03.08 -> 46->45. cota TVA|d301 (standard period-aware corect; REPARAT cota redusa literal 11 -> period-aware din common.cota, omisa pt perioade < 08.2025 unde reducerile erau 9%/5%; 2026 neschimbat [21,11,0]; decizie de produs deschisa: modelare 9%/5% coexistente) INCHIS 03.08 -> 45->44. tipuri operatiune IC (L/A/P/S)|d390 (VERIFICAT - mapare tip->simbol = nomenclator OPANAF 705/2020 L/T/A/P/S/R; codO/totalPlata_A/anti-drop conforme; gard-pin TIPURI==oficial adaugat) INCHIS 03.08 -> 44->43. rotunjire aritmetica (A91b)|d390 (VERIFICAT - _int ROUND_HALF_UP, gardat dublu identitate+scan; proba d390 pe valoare adaugata) INCHIS 03.08 -> 43->42. reclasificari manuale|d390 (FIX asimetrie: read-side facea fallback tacit la default pe reclasificare invalida; acum valideaza direciția ca write-side si ridica, TIPURI_DIRECTIE sursa unica in d390.py) INCHIS 03.08 -> 42->41. exigibilitate / prag|d390 (VERIFICAT - incadrare pe data_emitere = exigibilitate art.283/284, fara prag art.325; gard temporal pe pull adaugat; edge-case ziua-15 consemnat = decizie schema) INCHIS 03.08 -> 41->40. cote acceptate|d394 (VERIFICAT - d394 e modelul period-aware; cota_standard din common.cota, set fix = validator v5, fara literal hardcodat; garduri pin + cross-modul common⊆d394 adaugate) INCHIS 03.08 -> 40->39. taxare inversa|d394 (11/12 conform; NECONFORMITATE lit.l gaze naturale gasita, CORECTARE blocata pe codPR D394 neconfirmat la sursa - gard anti-regresie + datorie xfail(strict); input cerut: codPR gaze post-2021) INCHIS 03.08 -> 39->38. SourceDocuments|d406 (FIX period-awareness TaxCode livrari - TAXCODE_LIVRARI_PRE era definit dar nefolosit, factura veche emitea coduri post gresite; helper _taxcode_livrari pe data + gard. Payments/achizitii/adrese = observatii documentate) INCHIS 03.08 -> 38->37. plafon diurna neimpozabila|deconturi (calcul curent CONFORM art.76 alin.4^1 + gard golden; NECONFORMITATE period-awareness istorica - varianta unica aplica valorile de azi retroactiv, fix blocat pe HG diurna lipsa; datorie xfail strict) INCHIS 03.08 -> 37->36. credit sponsorizare / D177|sponsorizari (PROFIT conform art.25 alin.4 lit.i + gard existent; micro NU period-aware=datorie xfail (blocat pe text istoric art.56 alin.1^5 abrogat); D177 formular absent=decizie produs; endpoint neperiodizat=observatie) INCHIS 03.08 -> 36->35. rezerva legala|motor (formula CONTABILA conforma Legea 31 art.183 + gard golden adaugat; deductibilitatea FISCALA art.26(1)a - add-back impozit + plafon capital subscris - LIPSESTE = decizie produs; motor.py cod mort fara apelant) INCHIS 03.08 -> 35->34. zilieri (impozit+CAS)|contracte_speciale (FIX period-awareness: CAS 25%% aplicat din 2018-01-01, dar exista legal doar de la 01.05.2019 OUG 26/2019; 2 variante datate - 2018 doar impozit 10%%, 2019 CAS+impozit; impozit/CASS conforme) INCHIS 03.08 -> 34->33. regim marja second-hand|tva_marja (VERIFICAT - TVA pe marja = marja x cota/(100+cota) suta marita conform CF art.312 alin.(4), marja negativa->0; gard golden adaugat (lipsea test numeric); observatii main.py: cota neperiodica + la_data nepasat) INCHIS 03.08 -> 33->32. regim marja turism|tva_marja_turism (VERIFICAT - suta marita CF art.311 alin.4 + scutire proportionala non-UE alin.5, marja negativa->0; gard golden adaugat; neintegrat in datorie.py = observatie) INCHIS 03.08 -> 32->31. impozit dividend|decontari_asociati (FIX cote istorice: intrarea pre-2026 era 10%% fals (10%% = impozit pe venit art.78, nu pe dividende) -> 2023-2025 supra-impozitate; 3 intrari verificate la sursa 5%%/8%%/16%% (OUG 50/2015, OG 16/2022, Legea 141/2025); teste care cimentau 10%% actualizate) INCHIS 03.08 -> 31->30. contributii PFA (praguri CAS/CASS pe sm)|d212 (VERIFICAT calcul conform - CAS art.148, CASS art.170 alin.1 liniar, sm period-aware; REPARAT citare temei plafon 72 sm: Legea 141/2025 -> Legea 239/2025 art.XII pct.19; obs: calea 2026 dormanta) INCHIS 03.08 -> 30->29. nomenclator cod_oblig<->cod_bugetar|d100 (FIX cont bugetar obsolet: 20470101 (pre-2018) -> 5503XXXXXX, coroborat cu d101/d112; sursa unica d100.COD_BUGETAR importata si de d710; gard anti-drop pe cod nemapat; teste actualizate) INCHIS 03.08 -> 29->28. cota micro 121 (flag)|d100 (VERIFICAT - generator conform struct poz.17a (121->cota=1, 103->fara cota); gard bidirectional in build_xml: 121-fara-cota si cota-pe-alt-cod ridica ValueError, imposibil XML respins) INCHIS 03.08 -> 28->27. checksum totalPlata_A (R11b)|d100 (VERIFICAT valoarea emisa corecta 2x sum DUK R11b; REPARAT divergenta res.total_plata_a (1x) vs emis (2x) - aliniat la sursa unica res.total_plata_a=checksum emis de build_xml, ca celelalte declaratii) INCHIS 03.08 -> 27->26. scadente/nr_evidenta|d100 (VERIFICAT - nr_evidenta 23 poz conform struct (fix R16 poz.18), scadenta 25 luna urmatoare (poz.15) format ZZ.LL.AAAA; gard scadenta adaugat (lipsea); obs alte reguli scadenta pt obligatii nengerate) INCHIS 03.08 -> 26->25. structura P1-P53|d101 (VERIFICAT conform si complet OPANAF 206/2025 - toate formulele P3-P53 rand-cu-rand, totalPlata_A sum P1..P53, P13 rezerva legala corect, d_grup tratat; deja gardat golden+DUK, fara fix) INCHIS 03.08 -> 25->24. R17 Data_S/termen|d101 (neconformitate aparenta REZOLVATA: scadenta D101 parea inversata fata de lege dar valoarea validatorului 2022-2025=iunie e legal corecta via OUG 153/2020 art.I alin.13 lit.a - act ratat de prima cercetare; 2026=martie baza=jar-ul DUK, OUG 8/2026->iunie cand jar-ul se actualizeaza; decizie Costin: urmeaza validatorul pe ambele ramuri; temeiuri corectate) INCHIS 03.08 -> 24->23. limita text 75|d112 (2 neconformitati trunchiere reparate: numeAsig/prenAsig salariat (C75) erau netrunchiate -> nume >75 respins; functie_declar are C(50) nu 75, se trunchia la 74; reparat _t pe nume salariat + _t(...,50) pe functie) INCHIS 03.08 -> 23->22. nomenclator cod_oblig|d112 (VERIFICAT conform - toate 6 codurile cod_oblig<->cod_bugetar coincid cu nomenclatorul ANAF: 602/412/432->5503XXXXXX, 480 CAM->20470300XX distinct, 458/459->5503XXXXXX; lipsea gardul pe cod_bugetar, adaugat) INCHIS 03.08 -> 22->21. checksum totalPlata_A|d205 (VERIFICAT valoarea emisa CONFORMA - totalPlata_A=nrben+Tcastig+Tpierd+T_VB+T_GAR+Tbaza+Timp exact ca ANAF struct D205 OPANAF 102/2025 l.80-85, DUK-valid; REPARAT capcana latenta clasa-d100: res.total_plata_a tinea DOAR Timp, build_xml recalcula checksum-ul INDEPENDENT - d205 outlier de la conventia tuturor declaratiilor; aliniat sursa unica: calcul_d205->res.total_plata_a=checksum, build_xml il emite) INCHIS 03.08 -> 21->20. INCHIS 03.08 -> 21->20. trunchiere den/adresa|d205 (NECONFORMITATE reparata probata DUK: campurile text se trunchiau la 75 default, dar struct D205 OPANAF 102/2025 + DUK dau den C200/adresa C1000/functie_declar C50/den1 C100; den/adresa over-trunchiate=pierdere date, functie 51-75 si den1 >100 respinse de ANAF; fix limite explicite in build_xml, proba DUK pe inputuri lungi=valid) INCHIS 03.08 -> 20->19. INCHIS 03.08 -> 20->19. randuri / checksum|d300 (VERIFICAT CONFORM - totalPlata_A=suma camp 27..124 except 62/63(rd14.1/14.2=R67/R68); res.total_plata_a=sum(res.R) sursa unica; R67/R68 nu-s in allow-list -> excluse prin constructie; probat total==sum==7810==DUK-valid + R67/R68 manual->ValueError; gard golden+pin adaugat. OBS datorie: adresa/den d300 _t default 75 = over-trunchiere latenta ca d205) INCHIS 03.08 -> 19->18. INCHIS 03.08 -> 19->18. checksum totalPlata_A (R28)|d301 (VERIFICAT CONFORM - totalPlata_A=INT(sum baza1..5+tva1..5) toate 5 tipurile, struct poz.28, DUK R28; res.total_plata_a=sum(tot), build_xml emite res (sursa unica); deja gardat golden 12044+DUK in rollup, adaugat gardul de legatura res==emis==suma; fara fix, era conform) INCHIS 03.08 -> 18->17. INCHIS 03.08 -> 18->17. nomenclator tari (HR->CR)|d390 (NECONFORMITATE reparata, probata DUK: maparea HR->CR era GRESITA - DUK respinge tara=CR, accepta HR; _TARA_XML golit, Croatia emite HR. Restul nomenclatorului conform: TARI_UE complet, GB/XI DUK-valide) INCHIS 03.08 -> 17->16. INCHIS 03.08 -> 16->15. tipuri operatiune (pct.215)|d394 (VERIFICAT - TIPURI = exact setul din struct pdf (pin adaugat), derivarea testata; DATORIE: ASI e in TIPURI dar D394Validator instalat il RESPINGE ca enum (pdf-vs-jar), corectare blocata pe decizie produs remove/remap - gard anti-regresie adaugat) INCHIS 03.08 -> 15->14. INCHIS 04.08 -> 15->14. tip_partener|d394 (VERIFICAT CONFORM - clasifica_partener = cele 4 categorii pct.216 OPANAF 77/2022 (RO+CUI->1, fara/ne-numeric->2, UE->3, non-UE->4); cui_ro e normalizare, validitatea cuiP enforced de validator R218.2 fail-fast; sprijinit pe _TARI_UE verificat; gard consolidat adaugat) INCHIS 04.08 -> 14->13. INCHIS 04.08 -> 14->13. rezumat1 campuri complete|d394 (VERIFICAT cazurile comune - rezumat1 pt tp1(RO)/tp3(UE)/tp4 e complet si J8-valid, probat DUK; NECONFORMITATE ACTIVA: operatiunile N (neinreg tip2, auto din achizitii fara CUI) respinse de J8 - codul nu emite tip_document/tip_N/document_N; corectare = decizie produs, gard anti-regresie + datorie) INCHIS 04.08 -> 13->12. INCHIS 04.08 -> 13->12. nomenclator codPR (art.331)|d394 (VERIFICAT CONFORM pe J8 - toate codurile CODPR (categorii 22-31, gaze 36, subcoduri cereale) acceptate de validator, probat DUK cod-cu-cod; sursa comentata Ghid 2016 invechita dar codurile validator-confirmate; gaze codPR 36 = fostul blocaj lit.l, acum confirmat (lit.l rezolvat in 6675f19); gard DUK nou) INCHIS 04.08 -> 12->11. INCHIS 04.08 -> 12->11. totalPlata_A (R17)|d394 (VERIFICAT CONFORM - totalPlata_A=Suma(nrCui1..4)+Suma(rezumat2.baza[L+A+AI]) = formula R17 validator; res.total_plata_a==emis (sursa unica, clasa d100); probat pe J8: corect valid / gresit respins R17; gard sursa-unica+DUK adaugat) INCHIS 04.08 -> 11->10. ULTIMUL cluster d394 din secventa - urmeaza d406/d710. INCHIS 04.08 -> 11->10. plan conturi pe norma|d406 (VERIFICAT - planul SAF-T filtrat pe nomenclatorul oficial al normei (plan_oficial), conturi ne-norma excluse (ANAF le respinge), AccountID sintetic; REPARAT drop tacit: conturile excluse (strain) nu erau surfaced - acum pull le returneaza si genereaza le SEMNALEAZA in avertisment (numite), ca N in d394; gard DB adaugat) INCHIS 04.08 -> 10->9. INCHIS 04.08 -> 10->9. UoM UN/ECE|d406 (VERIFICAT CONFORM - UOM_UNECE = coduri UN/ECE Rec.20 (nu unitati RO), validator-confirmate (proba 15.07 BUC respins + extractie jar: H87/KGM/.../MWH prezente, BUC absent); default H87 + semnalare la necunoscut; XSD = SAFcodeType (lista in validator); gard nou) INCHIS 04.08 -> 9->8. MovementType nomenclator|d406 (VERIFICAT + COMPLETAT nomenclatorul - MISCARI_STOC/MOVEMENT_IMPLICIT dormante (MovementType se emite doar in raportarea de stocuri, sectiunile <MovementTypeTable/>/<MovementOfGoods/> goale lunar); cele 3 coduri (10/20/30) erau corecte dar nomenclatorul INCOMPLET - oficial 19 coduri (xlsx foaia 'Nomenclator stocuri', nota 5 = out-of-list respins fatal); completat la 19, MOVEMENT_IMPLICIT=10 cod valid; gard pin pe setul oficial complet) INCHIS 04.08 -> 9->8. BaseRate (encoding pro-rata)|d406 (VERIFICAT CONFORM - BaseRate=FRACTIE [0.0000-1.0000], 1.0000=100%, tip SAFBaseRate decimal(5,4); foaia '2.MasterFiles' contradictorie (proza '100/60' vs restrictie obligatorie [0-1]) - restrictia castiga, deci BASE_RATE=1 corect pt livrari; comentariul vechi cita gresit doc-ul, corectat; sursa unica: linia 582 hardcoda literal, acum emite BASE_RATE; datorie 50% pro-rata dormanta; gard nou + RED cu BASE_RATE=100) INCHIS 04.08 -> 8->7. registration_number (00+CUI)|d406 (VERIFICAT + NECONFORMITATE reparata: _UE_NON_RO avea 'GR' (ISO) nu 'EL' (prefix VAT/VIES); partener grec 'EL...' cadea pe 02=non-UE, schema cere 01EL123456789. Reparat EL + normalizare GR->EL; generalizat - d390/d394/intracomunitar deja corect EL, d406 singurul outlier. Firma proprie RO+CIF conform. Datorii: tip 03 CNP, XI, validare control-digit. Gard nou + RED) INCHIS 04.08 -> 7->6. structura XSD (Header/MasterFiles/GLE)|d406 (VERIFICAT CONFORM prin validare XSD mecanica contra saft.xsd: D406 complet = XSD-valid zero erori pe toata structura SAF-T; lunar omite sub-sectiunile goale (DUK-confirmat) -> exact o abatere asteptata (PurchaseInvoices) pe schema d406t. Namespace aliniat d406->d406t. Complementar DUK xfail (semantic). Gard nou + RED. ULTIMUL cluster d406 - urmeaza doar d710) INCHIS 04.08 -> 6->5. structura declaratie710|d710 (VERIFICAT + NECONFORMITATE reparata: cota pe <obligatie> nepazita bidirectional (spre deosebire de d100); DUK 04.08: 121 fara cota respins 'R17 cota lipsa', cota pe cod!=121 respins 'R17 cota nu se completeaza'. Reparat gard bidirectional in build_xml. Structura DUK-valida (5 cazuri + gunoi respins). Generalizat: doar d100+d710 au tiparul. Gard nou + RED) INCHIS 04.08 -> 5->4. nomenclator COD_BUGETAR|d710 (VERIFICAT pe DUK R14a: 5503XXXXXX acceptat pt 121/103 - mesajul releva inca vechiul 20470101 dar forma curenta 5503 e valida; sursa unica d100. NECONFORMITATE: lipsea gardul anti-drop pe cod_bugetar gol (d100 il are) - reparat in calcul_d710. Datorie: 130/131/132 nemapate, in afara LIMITEI. Gard nou + RED) INCHIS 04.08 -> 4->3. checksum R11b|d710 (VERIFICAT CONFORM pe DUK: totalPlata_A = Suma(dat_I+plata_I+dat_C+plata_C) pe obligatii = 2*(dat_I+dat_C); multi-obligatie 1500 valid, gresit respins R11b; sursa unica res.total_plata_a. Fara fix. Gard nou multi-obligatie+DUK) INCHIS 04.08 -> 3->2. R15 termen definitivare|d710 (VERIFICAT CONFORM pe DUK: cod 121 trim4 -> scadenta 25.06 an urmator (definitivare micro), valoare unica ceruta de DUK regula R15 (gresita respinsa EROARE cu 25.06 revelat); codul produce exact, stabil pe an. Fara fix. Gard nou + DUK) INCHIS 04.08 -> 2->1. scadente|d710 (VERIFICAT pe DUK R15 (25 luna urmatoare + micro trim4 25.06) + NECONFORMITATE reparata: nr_evid EMBEDA scadenta (R16) dar folosea scadenta calculata la override manual -> cod 103 scadenta alternativa valida 25.12 respinsa R16. Reparat nr_evid urmeaza scadenta emisa; GENERALIZAT la d100 (acelasi footgun). Gard nou + RED. ULTIMUL cluster din secventa - SECVENTA EPUIZATA) INCHIS 04.08 -> 1->0. Identitate = cluster | modul (nume duplicate intre module).

**REGULA DE ORDONARE.** Clusterul A vine dupa B daca o functie din A foloseste o valoare care APARTINE lui B (dependenta din graf_clustere). Sortare topologica pe aceste dependente. Departajare cand mai multe sunt libere simultan, in ordinea: (a) intra intr-o declaratie DEPUSA la ANAF - proxy Risc=FISCAL, aproximatie DECLARATA, nu echivalenta; (b) cate clustere deblocheaza; (c) ordinea din inventar. Secventa se PERSISTA, nu se recalculeaza la fiecare rulare - altfel pozitia 7 de azi nu e pozitia 7 de maine. Se rescrie DOAR cand se schimba graful sau se adauga clustere, cu motivul consemnat (vezi randul 'Rescrisa 02.08' de mai sus).
(SECVENTA EPUIZATA 04.08.2026 - toate clusterele nebifate-neblocate din Inventarul A au fost verificate. `core.agenda.urmator_cluster()` intoarce (None, 0, 1); ramane blocajul preexistent 'plafon diurna' (datorie xfail, HG istoric lipsa - nu e in secventa). Reintroducerea de clustere noi rescrie lista numerotata aici, cu motivul consemnat.)
## Inventarul de acoperit în A

Per CLUSTER de reguli, nu per fișier (30.07.2026) — un √ pe fișier ascundea că doar o parte din
reguli era verificată (vezi salarizare 29.07). `Verificat la sursă`: `√ DD.MM` = testele afirmă
LEGEA la data aceea (garda anti-stale pică `√`-ul dacă codul se schimbă substanțial după). `Risc`:
**FISCAL** = produce o cifră într-o declarație, greșeala e INVIZIBILĂ (validatorul acceptă) și ajunge
la ANAF; **STRUCTURA** = mapare/nomenclator/checksum/XML, greșeala e VIZIBILĂ (validatorul respinge).
Estimare de structură — se rafinează la citirea fiecărui modul.

### Criteriul de apartenenta la cluster (V1, 01.08.2026)

Un CLUSTER = o regula fiscala/structurala distincta (sau un grup strans cuplat) care produce o valoare
intr-o declaratie sau un modul de calcul, sprijinita pe un set coerent de temeiuri, verificata de un set de
functii de test (coloana Functie(test)). Granita e REGULA, nu fisierul: un fisier de test acopera mai multe
clustere.

- CO-LOCATIE: o regula partajata intre doua clustere apare in Functie(test) al AMBELOR (ex. proratarea se
  aplica SI facilitatii SI suprataxarii). Garda anti-stale reseteaza clusterele co-locate IMPREUNA (mesajul
  le numeste). Nu se duplica regula intr-un cluster nou.
- ORFAN: o regula fiscala in cod (functie cu marker TEMEI SAU care citeste o cota SAU un rate literal) fara
  NICIUN rand in inventar. Un orfan nu e verificat de nimeni si nu va fi -> se ADAUGA ca rand. Detectia e
  MARGINITA de markeri+graf: o regula cu rate hardcodat, fara marker si fara cota, e INVIZIBILA (cazul
  bilant_api) - se inchide doar cu gardul GRI de literale la 0 (GARZI cat.3, LIPSA).
- TEST DE MECANISM vs DE VALOARE: un test care verifica MASINARIA (graf de dependente, temei structurat,
  dispecer de versionare, cota() period-aware, generarea inventarului, blocaj motivat) NU asertaza o valoare
  fiscala a unui cluster - nu apartine niciunui cluster, prin design. Doar testele care asertaza o CIFRA/
  structura ceruta de lege intra in Functie(test).

| Cluster | Modul | Teste | Verificat la sursă | Risc | Temeiuri | Funcție(test) |
|---|---|---|---|---|---|---|
| facilitate salariu minim | salarizare | test_salarizare.py | √ 31.07 (bump: FIX3 a mutat net-ul asertat in test_minim_4325_are_facilitate_sem2; facilitatea reconfirmata la sursa OUG 89/2025 art.III + HG 146/2026, neschimbata) | FISCAL | OUG 156/2024 art.LXVI; OUG 89/2025 art.III; HG 146/2026 | test_minim_4325_are_facilitate_sem2 test_facilitatea_ramane_conditionata_de_norma_intreaga test_facilitate_pe_minim_cu_cm_ramane_intreaga test_facilitate_prorata_luna_angajare |
| suprataxare part-time | salarizare | test_salarizare.py | √ 02.08 (bump: V3 salariu_minim 2025 corectat 3700->4050 HG 1506/2024 FIX5 dupa √ 29.07; praguri COTA-DERIVATE nu literal - salarizare.py:129 sm=cota, d112 _sal_minim=cota; recalculat sm 2025/2026H1=4050 2026H2=4325 identic cu codul: (4050-300-2000)*25%=437.50, (4325-200-2000)*25%=531.25) | FISCAL | CF art.146 alin.(5^6)-(5^7); art.168 alin.(6^1) | test_part_time_2000_suprataxa_pe_angajator test_part_time_exceptat_fara_suprataxa test_norma_intreaga_sub_minim_este_suprataxata test_part_time_sub_minim_ramane_suprataxat test_exceptatul_nu_e_suprataxat_indiferent_de_norma test_peste_minim_nu_se_suprataxeaza test_suprataxa_baza_pe_minimul_diminuat_ambele_semestre |
| proratare angajare/incetare | salarizare | test_salarizare.py | √ 02.08 (bump: V3 salariu_minim 2025 corectat 3700->4050 HG 1506/2024 FIX5 dupa √ 29.07; praguri COTA-DERIVATE nu literal - salarizare.py:129 sm=cota, d112 _sal_minim=cota; recalculat sm 2025/2026H1=4050 2026H2=4325 identic cu codul: (4050-300-2000)*25%=437.50, (4325-200-2000)*25%=531.25) | FISCAL | OUG 156/2024 art.LXVI alin.(4); OMF 1855/2022 pct.2 | test_suprataxa_prag_prorata_luna_angajare test_facilitate_prorata_luna_angajare test_suprataxa_si_facilitate_prorata_la_incetare |
| deducere personala | salarizare | test_salarizare.py | √ 06.08 bump: #11 gard art.77(12)-(13) - deducerea 100 lei/copil conditionata pe declaratie_copii; testul trece flag-ul | FISCAL | Cod fiscal art.77 alin.(4)/(10)(a); pliant ANAF AJFP Vrancea (deducere personala) | test_deducere_degresiva_pe_trepte test_deducere_copil_scoala test_deducere_zero_fara_functie_baza test_deducere_4plus_persoane_45pct test_tanar_sub26_brut_mic_primeste_deducere test_deducere_la_data_obligatoriu |
| tichete masa/vacanta | salarizare | test_salarizare.py test_tichete_pontaj.py test_exces_vacanta_d112.py | √ 15.08 (bump: 15.08 reverificat test_tichete_blocheaza_daca_pontaj_neconfirmat dupa rescrierea pt noul contract stat-plata (#1/#3 plimbarea M2): pontaj neconfirmat -> tichete=0 + flag pontaj_neconfirmat, statul se randeaza (nu mai arunca pt tot statul); tichetele raman blocate pana la confirmarea pontajului, HG 1045/2018 art.10(3). Anterior 02.08: D2 nr tichete = zile efectiv lucrate din pontaj CONFIRMAT cap.23 - fe99cc2/5a5b63c/f83da8a/61c0260; D3 exces vacanta in brut declarat DUK-valid 9a82748; fond 31.07 valoare45/cote/plafon6sm/cadou; #3 baza CASS ramane GRI - verbatim art.78 neconfirmabil, fond prin derivare art.157->78. Teste D2 in test_tichete_pontaj, D3 in test_exces_vacanta_d112) | FISCAL | Legea 201/2025; HG 1045/2018 art.10(3); CF art.76(3)h/78/142(r)/157(2); OUG 8/2009 art.1; L296/2023 | test_exces_vacanta_intra_in_baza_salariala test_cass_doar_pe_01_07_10 test_tichete_scad_cu_zilele_de_co test_tichete_blocheaza_daca_pontaj_neconfirmat test_d112_cu_exces_vacanta_valid_duk |
| concedii medicale | salarizare | test_salarizare.py | √ 02.08 (bump: PARTIAL 31.07 -> inchis 02.08 - cod 02 GRI + unificare taxe_cm confirmata + D-field cod 06/08 DUK-valid pe clusterul d112; CM1 GRI, CM4/cod05 datorii) — procente pe cod (01=55/65/75 progresiv, 02/03/04 FAAMBP 80/100, 05/06/07/12/14/51=100, 08/09=85, 13/15/rest=75, 10 art.19), split 1-5/FNUASS, diminuare 1 zi, CAS 25% uniform + CASS 01/07/10 UNIFICAT (taxe_cm canonic, apelat si de d112.py:186 - fara divergenta, cautat clasa nu instanta); cod 02 accident traseu GRI (FAAMBP corect; nerecunoscut ITM -> recodificare la 01, nu ramura pe cod 02); DUK cod 01 valid. GRI: CM1 verbatim art.139(1)(o) neobtinut la MO. DATORII declarate (test_datorie): CM4 plafon 12sm in calcul_cm neaplicat, cod 05 sub-randuri infectocontagioase | FISCAL | OUG 158/2005 art.10/12/17/20; Legea 141/2025 si 136/2020; CF art.139(1)o+140 (CAS salariat activ; art.144=alte categorii)/142/155(1)i; OUG 34/2024 | test_cass_doar_pe_01_07_10 test_cm_cas_25pct_uniform test_cm_split_angajator_max_5 test_carantina_cod07_este_100pct |
| tichete culturale | salarizare | test_tichet_cultural.py test_salarizare.py | √ 04.08 (bump: 02.08->04.08 fereastra oct2025-mar2026 reverificata la sursa (Ordin MF/MC 1.574/3.246/2025, MO 900) + test plafon redenumit la confirmare; FUNCTIONALITATE NOUA livrata; temeiuri VERDE anaf_surse/RAPORT_verificare_temeiuri.md: impozit 10% art.76(3)h/v13, CAS nu art.142r/v10, CASS nu art.157(2)/v11 [DIVERGENTA vs masa], CAM nu 220^4(2)/v12, nu in plafon 33% v14, nominal 10-multiplu-50 art.22(2)/v15; plafon semestrial plafon_cultural() 220/450 si 250/490 confirmate primar, fereastra oct2025-mar2026 CONFIRMATA 240/470 (04.08, Ordin MF/MC 1.574/3.246/2025, MO 900/01.10.2025); D112 camp E3_74 emis la nivel etalon prin impozit). Gard BILETE_VALOARE_TRATAMENT. | FISCAL | Legea 165/2018 art.21/22; CF art.76(3)h/142(r)/157(2)/220^4(2)/25(3)b3; ordine MF/MC 361/2680-2025 si 369/2624-2026 | test_plafon_cultural_ferestre_confirmate test_plafon_cultural_oct2025_mar2026_confirmat_240_470 test_cultural_impozit_fara_cass test_cultural_diferit_de_masa_pe_cass test_bilete_valoare_declara_toate_tratamentele |
| tichete cresa | salarizare | test_tichet_cresa.py test_salarizare.py | √ 02.08 (FUNCTIONALITATE NOUA livrata; tratament fiscal = ca CULTURAL: impozit 10% art.76(3)h, CAS nu 142r, CASS nu 157(2) [DIVERGENTA vs masa], CAM nu 220^4(2); nominal 10-multiplu-100 art.19(2); plafon 450/luna/copil art.19(1) baza confirmata, indexare 740 GRI verdict 17 BLOCATA cf regula de lant; D112 camp E3_72 etalon prin impozit). Gard BILETE_VALOARE_TRATAMENT + plafon_cresa. | FISCAL | Legea 165/2018 art.19; CF art.76(3)h/142(r)/157(2)/220^4(2) | test_plafon_cresa_450_per_copil test_cresa_impozit_fara_cass test_cresa_in_registru_fara_cass test_cresa_seteaza_peste_plafon_1_copil_blocheaza_indexarea test_cresa_db_roundtrip_baza_450 |
| randuri dinamice facturi-recurente (cap.24) | facturi recurente UI (formSablon) | test_facturi_recurente_randuri_dinamice.py | √ 08.08 (GARD headless comis a771f25: 5 scenarii DOM + no-op, chromium + backend real interceptat facturi_api.linii_campuri_lipsa prefix fr-l; mutatie filtru->rosu, revert->verde) | STRUCTURA | DESIGN_SYSTEM cap.24 (randuri dinamice) + cap.6 (eroareCamp) | test_rand_incomplet_in_mijloc_nu_dispare test_noop_lista_nefiltrata_si_hash |
| randuri dinamice retete (cap.24) | retete UI (sectiuneaCV) | test_retete_randuri_dinamice.py | √ 08.08 (GARD headless comis a771f25: 5 scenarii DOM + no-op; retete_api._ingrediente_campuri_lipsa; mutatie filtru->rosu, revert->verde) | STRUCTURA | DESIGN_SYSTEM cap.24 + cap.6 | test_ingredient_incomplet_in_mijloc_nu_dispare test_noop_lista_nefiltrata_si_hash |
| randuri dinamice NIR (cap.24 regula 1+2) | NIR UI (ecranStocuri) | test_nir_randuri_dinamice.py | √ 08.08 (GARD headless comis 332e10b: 5 scenarii DOM + no-op; regula 1 appendChild/remove -> re-randare integrala din model; stocuri_api._nir_campuri_lipsa; ruta /stocuri/nir 422 field-keyed; mutatie filtru->rosu, revert->verde) | STRUCTURA | DESIGN_SYSTEM cap.24 (regula 1+2) + cap.6 | test_rand_incomplet_in_mijloc_nu_dispare test_noop_lista_nefiltrata_si_hash |
| filtrare-inainte-validare cablat (cap.24 regula 2) | inventar UI + verificator | test_inventar_randuri_dinamice.py verificator_conformitate.py | √ 08.08 (GARD headless comis 332e10b + regula 2 CABLATA in verificator FILTRARE_INAINTE_VALIDARE fara exceptii; inventar lista fixa -> doar regula 2, backend autoritar sare faptic gol; mutatie filtru reintrodus -> FILTRARE=2/TOTAL=2 + garduri headless rosii, revert->verde) | STRUCTURA | DESIGN_SYSTEM cap.24 regula 2 (lista randata = lista validata, fara filtrare tacita) | test_noop_toate_articolele_trimise_nefiltrat test_eroare_per_linie_langa_camp |
| running == HEAD (detector) | app/versiune + superadmin | test_running_head.py | √ 08.08 (GARD comis 38101bc: detector VIZIBIL in app - stampila commitul de pornire in memoria procesului (core/versiune.py, lifespan) vs HEAD de pe disc, NU dedus din mtime; /admin/versiune superadmin-only; caseta-atentie DOAR la divergenta; divergenta->aprins/egalitate->stins/necunoscut->tacut; RBAC superadmin 200 / alte roluri 403 / fara token 401; mutatie != -> == rosu) | STRUCTURA | DECIZII/GARZI iulie (running==HEAD: detector vizibil, NU auto-restart) + DESIGN_SYSTEM cap.6 (caseta-atentie) | test_divergenta_aprinde_semnalul test_endpoint_alte_roluri_403 |
| edge canonic www/HEAD (crawler) | app (_edge_canonic_head, main.py) | test_edge_canonic_head.py | √ 15.08 (GARD comis 02869c0: middleware _edge_canonic_head in main.py, doua cereri Costin. #1 www.iconta.eu -> 301 PERMANENT catre forma canonica FARA www, PASTRAND calea+query (duplicat SEO evitat; canonic = _GHID_BAZA, baza sitemap+rel=canonical); non-www ramane 200. #2 HEAD pe rutele GET -> 200 nu 405 (FastAPI NU adauga HEAD la @app.get -> era 405; Googlebot foloseste HEAD ca sa verifice schimbarea, 405 irosea buget crawl), Content-Length HEAD == GET, redirect si pe HEAD. In-process TestClient (/,/ghid nu ating DB), aserturi ASCII; probat HEAD 200 CL 1919/26147/7885 + www 301 Location canonic. MUTATIE: scoti middleware-ul -> HEAD 405 / www 200 rosu) | STRUCTURA | decizie crawler/SEO Costin (commit 02869c0): canonic fara www (301 permanent, _GHID_BAZA pe care se genereaza sitemap+rel=canonical) + HEAD ca GET (RFC 7231 sect.4.3.2: HEAD identic cu GET fara corp, aceleasi headere incl Content-Length); nginx trece Host la upstream -> rezolvat in app, versionat/testabil | test_head_pe_rute_get_da_200_nu_405 test_head_are_content_length_ca_get test_www_redirect_301_catre_canonic test_www_redirect_pastreaza_calea_si_query test_non_www_ramane_200_fara_redirect test_www_redirect_si_pe_head |
| randuri dinamice e-Transport (cap.24 3a) | e-Transport UI | test_etransport_randuri_dinamice.py | √ 08.08 (GARD headless comis c0be1cf: 5 scenarii DOM + no-op sha256, chromium + backend real interceptat; mutatie filtru->rosu, revert->verde) | STRUCTURA | DESIGN_SYSTEM cap.24 (randuri dinamice) + cap.6 (eroareCamp) | test_rand_incomplet_in_mijloc_nu_dispare test_noop_lista_nefiltrata_si_sha256 |
| nomenclator cod_oblig<->cod_bugetar | d100 | test_d100.py (+test_d710.py) | √ 03.08 (FIX cont bugetar obsolet. D100 mapa cod_oblig 121/103 la 20470101 - OBSOLET, inlocuit oficial cu 5503 din 26.07.2018 (d100_struct_anaf.txt:562), fara X-padare C(10). Coroborare: d101 (acelasi cod 103) si d112 emit deja 5503XXXXXX. FIX: COD_BUGETAR -> "5503XXXXXX" (sursa unica, d710 importa din d100). GARD anti-drop: cod_oblig nemapat -> ValueError (nu omite tacit atributul obligatoriu). Teste care cimentau 20470101 actualizate) | STRUCTURA | nomenclator ANAF D100 (cont unic 5503 din 26.07.2018, d100_struct_anaf.txt; cod_bugetar C(10) X-padat) | test_cod_bugetar_din_nomenclator |
| cota micro 121 (flag) | d100 | test_d100.py | √ 03.08 (VERIFICARE + gard. Generator CONFORM struct D100 poz.17a: micro (cod_oblig 121) emite cota="1", profit (103) fara cota (daca 121 atunci cota=1 altfel null). Rata micro pt suma = period-aware din registru (impozit_micro 1%%), separata de flag-ul structura cota="1". GARD bidirectional in build_xml: 121 fara cota="1" -> ValueError; cota pe alt cod -> ValueError (face imposibil XML respins, inclusiv apel direct)) | STRUCTURA | struct D100 poz.17a (cota N(1): daca cod_oblig=121 atunci cota=1 altfel null) | test_cota_micro_121_gard_bidirectional test_micro_are_cota_1_pe_obligatie |
| checksum totalPlata_A (R11b) | d100 | test_d100.py | √ 03.08 (VERIFICAT + aliniere sursa unica. Valoarea emisa (totalPlata_A = 2x sum(suma_dat), DUK R11b) era CORECTA. DAR divergenta: res.total_plata_a era 1x sum, iar build_xml recalcula 2x INDEPENDENT (nu din res) - d100 exceptia de la conventia tuturor declaratiilor (d101/d390/d710 emit res.total_plata_a). FIX: res.total_plata_a = checksum (2x sum) + build_xml il emite (o sursa). Gard: res==XML==2x sum) | STRUCTURA | DUK regula R11b (totalPlata_A = suma_dat+suma_ded+suma_plata+suma_rest = 2x sum la obligatia simpla) | test_totalplata_a_checksum_r11b_din_res |
| scadente/nr_evidenta | d100 | test_d100.py | √ 03.08 (VERIFICARE + gard scadenta. nr_evidenta CONFORM struct (23 poz: 10+cod_oblig+01+LLAA+ZZLLAA+0+0+00+control; poz.18="0" dupa fix R16), gardat de 3 teste. scadenta = 25 a lunii urmatoare perioadei (struct poz.15), format ZZ.LL.AAAA - conform pt 121/103 trimestrial (Q1-Q3 25 apr/jul/oct, Q4 25 ian). Lipsea test scadenta -> gard adaugat. Obs: alte reguli scadenta (25/12, 28-29/07) sunt pt obligatii nengerate de d100; Q4 profit definitivare = D101) | STRUCTURA | struct D100 poz.15 (scadenta 25 luna urmatoare, ZZ.LL.AAAA) + poz.20 (nr_evid 23 poz + suma control) | test_scadenta_25_luna_urmatoare_perioadei test_nr_evid_cifra_de_control |
| structura P1-P53 | d101 | test_d101.py | √ 03.08 (VERIFICAT CONFORM SI COMPLET fata de OPANAF 206/2025. Toate formulele derivate P3-P53 coincid rand-cu-rand (P3=P1-P2, P7=P3+P6, P10=P7+P8-P9, P16=SP11..15, P22=P10-P16-P21, P34=SP23..33, P38a, P40 profit impozabil, P41=P411+P412, P48 dispecerat P46/P47, P52/P53, totalPlata_A=sum P1..P53 fara sub-randuri din care). P13 rezerva legala (A1) corect. d_grup tratat. FARA fix - deja gardat de golden lant formule + proba DUK (§9 acoperit)) | STRUCTURA | OPANAF 206/2025 (D101_A600 v10, structura P1-P53 + totalPlata_A poz.20) | test_golden_lant_formule_oficiale test_d101_reconstructie_proba_duk_valid |
| cota profit 16% + IMCA | d101 | test_d101.py | √ 03.08 (cota 16% verificata CF art.17 + COTE impozit_profit, test cu temei; IMCA CF art.18^1 IMPLEMENTAT: formula 1%x(VT-Vs-I-A) negativ->0 + prag 50mil euro + wiring P47/comparatie P48 + PROBA DUK. Gap minor: cota din COTA_STANDARD literal, nu cota() - rutare follow-up) | FISCAL | CF art.17 (cota 16%); CF art.18^1 (IMCA); OUG 8/2026 | test_golden_lant_formule_oficiale test_cota_profit_16pct_din_cota_cu_temei test_imca_formula_1pct_din_vt_vs_i_a test_datoreaza_imca_prag_50mil_euro test_imca_wiring_p47_si_comparatie_p48 test_imca_d101_duk_valid |
| R17 Data_S / termen | d101 | test_d101.py | √ 03.08 (neconformitate aparenta -> REZOLVATA cu decizie Costin + act gasit. Scadenta D101 e period-aware; parea inversata fata de lege, dar valoarea validatorului (2022-2025 -> 25 iunie) e LEGAL CORECTA via OUG 153/2020 art.I alin.(13) lit.a (derogare art.42, aplicabil 2021-2025, MO 817/04.09.2020) - prima cercetare ratase actul. 2026 -> 25 martie baza art.42 = ce cere jar-ul DUK; OUG 8/2026 il muta la iunie de la fiscal 2026 cand validatorul se actualizeaza (depunere in 2027; proba DUK pe 2026 va semnala). Decizie: tool-ul urmeaza validatorul pe ambele ramuri. Temeiuri corectate OPANAF->OUG 153/2020 + Legea 227/2015 art.42) | STRUCTURA | OUG 153/2020 art.I alin.(13) lit.a (2022-2025 iunie) + Legea 227/2015 art.42(1) baza + OUG 8/2026 art.6 pct.12 (2026 iunie viitor) | test_scadenta_LL_plus_3_pentru_an_peste_2025 |
| amortizare | d101 | test_d101.py | √ 03.08 (tratamentul amortizarii in d101 aliniat CF art.28: amortizare FISCALA P11 dedusa in P16, amortizare CONTABILA P28 adaugata inapoi in P34; prag MF amortizabil 5000 lei art.28 alin.2b/OUG8-2026. Golden cu temei. DATORIE separata MF/D406: degresiva/accelerata necalculate - xfail test_datorie_mf_metode_amortizare, impact pe contabil/SAF-T nu pe d101) | FISCAL | CF art.28 (amortizarea fiscala); OUG 8/2026 (prag 5000) | test_amortizare_ajustare_fiscala_art28 test_mf_prag_amortizabil_5000_art28 |
| baze contributii (CAS/CASS/imp/CAM) | d112 | test_d112.py | √ 03.08 (cotele salariale rutate PERIOD-AWARE prin cota() din COTE, nu literale: CAS 25% CF art.138 lit.a, CASS 10% CF art.156, impozit 10% CF art.78 alin.2, CAM 2.25% CF art.220^3 alin.1 - toate verificate VERBATIM la sursa. Value-preserving: golden D112 + DUK neschimbate. Gard anti-hardcode pe sursa functiilor) | FISCAL | CF art.138 (CAS 25%); CF art.156 (CASS 10%); CF art.78 (impozit 10%); CF art.220^3 (CAM 2.25%) | test_cotele_contributii_din_cote_cu_temei test_d112_ruteaza_cotele_prin_cote_nu_literale test_d112_cas_cass_valori_neschimbate_dupa_rutare |
| concedii medicale (asiguratB3/D) | d112 | test_exces_vacanta_d112.py test_pull_declaratii.py | √ 10.08 (bump: fixtures test_pull_declaratii reparate tura 26 - serie/numar/data asiguratD obligatorii, D_1/D_2/D_5/D_6/D_7; re-verificat DUK cod 06/08 valid + suita verde) — D-field per cod: D_9/D_10/D_11(cod 06 urgenta, HG 423/2020, C(3) obligatoriu daca D_9=06)/D_23; cod 08 maternitate Rd.3 (C2_31/32/34/36) 100% FNUASS; taxe CM prin taxe_cm canonic. DUK VALID: cod 01/06/08 (raw, 02.08). DATORIE declarata (test_datorie): cod 05 sub-randuri infectocontagioase Rd.1.1-1.4 nedefalcate (emise 0, corect cat timp nu exista cod 05 in luna) | FISCAL | OUG 158/2005; structura D112 (D_11 cf HG 423/2020) | test_d112_cod06_urgenta_valid_duk test_d112_maternitate_cod08_c2_rd3 test_d112_urgenta_cod06_emite_d11 |
| suprataxare prag | d112 | test_d112.py | √ 02.08 (bump: V3 salariu_minim 2025 corectat 3700->4050 HG 1506/2024 FIX5 dupa √ 29.07; praguri COTA-DERIVATE nu literal - salarizare.py:129 sm=cota, d112 _sal_minim=cota; recalculat sm 2025/2026H1=4050 2026H2=4325 identic cu codul: (4050-300-2000)*25%=437.50, (4325-200-2000)*25%=531.25) | FISCAL | CF art.146 alin.(5^6) | test_sub_minim_nescutit_emite_asigexc2_fara_motivexc test_peste_minim_asigexc_zero |
| rotunjire aritmetica (A91b) | d112 | test_d112.py test_limita_text_anaf.py | √ 03.08 (rotunjirea contributiilor = ARITMETICA/half-up, nu bancara - ANAF structura D112 'Contributiile se rotunjesc aritmetic', DUK regula A91b CAM 112->113. _d112int (ROUND_HALF_UP) pe toate contributiile. REPARAT: minimul part-time (prag_zile, cas_min_pt, cass_min_pt) folosea round() BANCAR - _d112int ulterior era no-op pe valoarea deja intreaga, deci bancarul ajungea in B4_*P declarat; prag_zile=1226 -> CAS 306 in loc de 307. Rutat prin _d112int, proba pe valori reale) | FISCAL | ANAF structura D112 0126_030226 (rotunjire aritmetica); DUK regula A91b | test_rotunjire_aritmetica_nu_bancara test_partime_minim_rotunjeste_aritmetic_nu_bancar test_partime_minim_foloseste_d112int_nu_round_bancar test_toate_generatoarele_rotunjesc_aritmetic |
| limita text 75 | d112 | test_d112.py | √ 03.08 (2 neconformitati de trunchiere reparate fata de structura D112 0126_030226. (A) numeAsig/prenAsig (nume/prenume salariat C75) erau doar escapate, NEtrunchiate -> nume >75 respins; (B) functie_declar are C(50) nu C(75), se trunchia la 74 in loc de 50. Reparat: _d112esc(_t(...)) pe nume salariat + _t(...,50) pe functie. Restul campurilor (nume_declar/prenume_declar C75, den) erau deja corecte) | STRUCTURA | structura ANAF D112 0126_030226: numeAsig/prenAsig C(75), functie_declar C(50) | test_limita_75_asigurat_si_functie_declar_50 |
| nomenclator cod_oblig | d112 | test_d112.py | √ 03.08 (VERIFICAT CONFORM. Toate 6 codurile cod_oblig<->cod_bugetar din add_oblig coincid cu nomenclatorul oficial ANAF (structura D112 Nomenclator 3): 602/412/432 -> 5503XXXXXX, 480 CAM -> 20470300XX (distinct), 458/459 suportat angajator -> 5503XXXXXX. Fara neconformitate. Testul vechi verifica doar codOblig ca substring - lipsea gardul pe cod_bugetar; adaugat) | STRUCTURA | structura ANAF D112 Nomenclator 3 (Obligatii de plata BS/BASFS): 602/412/432/480/458/459 + coduri bugetare | test_cod_oblig_pereche_cu_cod_bugetar_corect test_codurile_de_obligatie_corecte |
| sect_II tip_venit (impozit retinut) | d205 | test_d205.py | √ 16.08 (bump: test_impozit_dividend_period_aware_cf_art97 actualizat - cota dividende 2025 corectata la 10%% (OUG 156/2024 art.LXIV, de la 01.01.2025; registrul lipsea intrarea 2025), reverificat la sursa. structura sect_II + tip_venit verificate la sursa anaf_surse/d205_struct_anaf.txt = OPANAF 102/2025: tip_venit=08 '1.a venituri din dividende' cu tip_plata=2 + divid_D/divid_P + baza1/imp1; sect_II frate cu benef; totalPlata_A = suma tuturor campurilor. REPARAT impozit retinut pe dividende: era hardcodat 10%, acum PERIOD-AWARE prin cota('impozit_dividend') - 16% de la 01.01.2026 CF art.97/Legea 141/2025 (era 10% pana in 2025). Proba DB reala: 50000 div 2026 -> 8000, nu 5000; proba DUK valida) | FISCAL | OPANAF 102/2025 (structura D205); CF art.97 + Legea 141/2025 (impozit dividende 16% de la 2026) | test_d205_contract_pull_genereaza_perioada test_impozit_dividend_period_aware_cf_art97 test_d205_rata_dividend_din_cota_nu_hardcodat test_d205_contract_proba_duk_valid |
| checksum totalPlata_A | d205 | test_d205.py | √ 03.08 (VERIFICAT valoarea emisa CONFORMA + aliniere sursa unica. totalPlata_A emis = nrben+Tcastig+Tpierd+T_VB+T_GAR+Tbaza+Timp (formula EXACTA ANAF struct D205, OPANAF 102/2025, l.80-85) - corect, DUK-valid. DAR capcana latenta clasa-d100: res.total_plata_a tinea DOAR Timp, iar build_xml recalcula checksum-ul INDEPENDENT - d205 outlier de la conventia tuturor declaratiilor (d100/d101/d300/d390/d710 emit res.total_plata_a). FIX red->green: calcul_d205 calculeaza checksum-ul -> res.total_plata_a; build_xml il EMITE din res (o sursa). Gard: res==header emis==suma sect_II din XML) | STRUCTURA | ANAF struct D205 OPANAF 102/2025 l.80-85 (totalPlata_A=suma nrben+Tcastig+Tpierd+T_VB+T_GAR+Tbaza+Timp); DUK proba | test_total_plata_a_res_egal_checksum_emis test_totalPlata_A_e_suma_tuturor_campurilor_sect_II test_d205_contract_proba_duk_valid |
| trunchiere den/adresa | d205 | test_d205.py | √ 03.08 (NECONFORMITATE reparata, probata DUK. Campurile text D205 se trunchiau la 75 (default text_anaf), dar struct ANAF OPANAF 102/2025 + validatorul DUK dau: den C(200), adresa C(1000), functie_declar C(50), den1 beneficiar C(100). den/adresa OVER-trunchiate 76-200/76-1000 = pierdere de date (D205 absent din lista 27.07 de respingere >75); functie 51-75 si den1 >100 emiteau si ANAF le RESPINGEA. Probe DUK: den 200 valid/201 erori, adresa 1000/1001, functie 50/51, den1 100/101. FIX: limite explicite _t(...,200/1000/50/100) in build_xml. Proba DUK pe inputuri lungi trunchiate = valid) | STRUCTURA | ANAF struct D205 OPANAF 102/2025 (den C200, adresa C1000, functie_declar C50, den1 C100); probat direct pe validatorul DUK (boundary 200/201, 1000/1001, 50/51, 100/101) | test_trunchiere_den_adresa_functie_den1_la_limitele_anaf test_trunchiere_lunga_ramane_duk_valida |
| rotunjire | d205 | test_d205.py test_limita_text_anaf.py | √ 03.08 (sumele fiscale D205 - baza1/imp1/dividende/parte - se rotunjesc ARITMETIC prin _i = Decimal.quantize(ROUND_HALF_UP), aceeasi regula ANAF ca la D112 (validator A91b). Deja corect prin constructie; GARDAT acum: _i adaugat in gardul cross-generator de identitate + proba d205-specifica _i(2.5)=3/_i(0.5)=1 aritmetic nu bancar. Fara schimbare de comportament) | FISCAL | ANAF structura D205 (OPANAF 102/2025) + regula A91b (rotunjire aritmetica) | test_d205_rotunjeste_aritmetic_nu_bancar test_rotunjirea_e_identica_intre_generatoare |
| cote TVA -> randuri | d300 | test_d300.py | √ 03.08 (maparea cotelor pe randuri verificata la sursa structura_D300_v12.0.0 + proba DUK: LIVRARI 21->Rd.9, 11->Rd.10, 9(art.III L141/2025)->Rd.11 - corecte. REPARAT ACHIZITII DEDUCTIBILE: 11% era la R74 (=Rd.24.1 cota 19% legacy, marja 18-20% - respins DUK) -> mutat la R23 (Rd.25, DUK valid); 9% era la R76 (=taxare inversa Rd.27.4, respins DUK + pierdut din R27) -> scos din auto, semnalat pentru declarare MANUALA (validatorul instalat respinge si R75 din v12). DATORIE: 9% deductibil auto - xfail test_datorie_d300_9pct_deductibil_auto) | FISCAL | structura_D300_v12.0.0 (marja randuri) + Legea 141/2025 (cote 21/11/9) | test_cote_tva_maparea_pe_randuri_d300 test_9pct_deductibil_nu_emite_rand_invalid_si_avertizeaza test_cote_tva_d300_proba_duk_valid |
| exigibilitate / TVA la incasare | d300 | test_d300.py (+test_tva_incasare.py) | √ 03.08 (IMPLEMENTAT: firma pe sistem -> D300 calculeaza exigibilitatea din DECONTARI - incasari cont 4111 / plati cont 401 validate in perioada, suta marita art.282(8), proportional pe plati partiale art.282(3); deducere amanata la plata art.297(2-3); taxare inversa exclusa art.282(6). Sursa = note contabile legate de factura, nu emiterea/platita_la. Fara cap 90 zile - eliminat de OUG 8/2026. Proba DB reala + DUK) | FISCAL | CF art.282 + art.297 (OUG 8/2026); plafon 5M COTE | test_tva_la_incasare_exigibilitate_pe_decontari_suta_marita test_tva_la_incasare_partial_proportional test_tva_incasare_exigibil_la_decontare_nu_la_emitere test_tva_incasare_d300_proba_duk_valid |
| taxare inversa | d300 | test_d300.py | √ 17.08 (bump: diacriticizare mesaje afisate (09010f7), comportament si verificare NESCHIMBATE; era 03.08: CF art.331: beneficiarul auto-taxeaza; se declara MANUAL in rd.12 colectata + rd.27/R25 deductibila = net zero. REPARAT: R12_ lipsea din allow-list-ul manual -> rd.12 era silentios ignorat (sub-declarare); adaugat. Proba DUK pe decont echilibrat rd.12=rd.27 + gard anti-drop. GRI reverse-charge D300/D394 inchis - reconfirmat la sursa art.331 + structuri D300 Rd.12 / D394 tip bun) | FISCAL | CF art.331; structura D300 Rd.12; structura D394 (bun/defalcare) | test_taxare_inversa_rd12_se_declara_manual test_taxare_inversa_r12_fara_fix_ar_fi_dropped test_taxare_inversa_d300_proba_duk_valid |
| pro-rata deducere | d300 | test_d300.py | √ 03.08 (CF art.300, regim mixt: deducere pro-rata cand nu se tin evidente separate. D300 CORECT prin constructie: R31_2 = Ajustari conform pro-rata (Rd.33 struct v12) = -(taxa dedusa x fractia nedeductibila); total dedus R32 = R28 x pro_rata/100 - NU scalare directa. Verificat + GARDAT: pro_rata=80% -> R28=210, R31=-42, R32=168; pro_rata=100 fara ajustare; proba DUK) | FISCAL | CF art.300 (deducere regim mixt); structura D300 Rd.33 (ajustari pro-rata) | test_pro_rata_ajustare_deductibila_art300 test_pro_rata_100_fara_ajustare test_pro_rata_d300_proba_duk_valid |
| randuri / checksum | d300 | test_d300.py | √ 17.08 (bump: diacriticizare mesaje afisate (09010f7), comportament si verificare NESCHIMBATE; era 03.08: VERIFICAT CONFORM + gard golden. totalPlata_A = suma(camp 27..124) EXCEPT 62(rd14.1=R67)/63(rd14.2=R68), struct D300. Codul: res.total_plata_a=sum(res.R) (sursa unica, build_xml emite res, ca celelalte declaratii); R67/R68 nu-s in nicio allow-list -> gardul-clasa le respinge, deci nu pot intra in checksum (excludere prin constructie). Probat: total_plata_a==sum(R)==7810==DUK-valid; R67_1/R68_1 manual->ValueError. Lipsea gardul explicit - adaugat. OBS: adresa/den d300 emise cu _t default 75 - DUK accepta 152 (over-trunchiere latenta ca d205, in afara scopului) = datorie deschisa) | STRUCTURA | struct D300 (totalPlata_A=suma camp 27..124 except 62/63); probat pe validatorul DUK (checksum + excludere 14.1/14.2) | test_checksum_totalplata_a_egal_suma_randuri_emise_duk_valid test_randuri_14_1_14_2_eliminate_nu_intra_in_checksum |
| rotunjire aritmetica | d300 | test_d300.py test_limita_text_anaf.py | √ 03.08 (sumele fiscale D300 se rotunjesc ARITMETIC prin _int = numar_fiscal.quantize(ROUND_HALF_UP), regula A91b ANAF. Deja in gardul de identitate cross-generator (a==b==c==d cu d390/d112/d205); adaugat proba d300-specifica _int(2.5)=3/_int(0.5)=1 aritmetic nu bancar. Fara schimbare de comportament) | FISCAL | regula A91b (rotunjire aritmetica ANAF) | test_d300_rotunjeste_aritmetic_nu_bancar test_rotunjirea_e_identica_intre_generatoare |
| ajustari | d300 | test_d300.py | √ 17.08 (bump: diacriticizare mesaje afisate (09010f7), comportament si verificare NESCHIMBATE; era 03.08: CF art.304 regularizari + art.305 ajustari. REPARAT: randurile de ajustare/regularizare R29 (restituiri cumparatori straini Rd.31), R30 (regularizari taxa dedusa Rd.32), R35 (sold reportat), R36 (diferente inspectie Rd.38) lipseau din allow-list-ul manual -> erau silentios aruncate (ajustari nedeclarate). Adaugate: R29/R30 intra in total dedusa R32, R35/R36 in R37 cumulat. Proba DUK + gard anti-drop) | FISCAL | CF art.304 (regularizari) + art.305 (ajustari); structura D300 Rd.31/32/37/38 | test_ajustari_regularizari_deductibila_se_declara test_regularizari_rezultat_r36_intra_in_cumulat test_ajustari_r30_fara_fix_ar_fi_dropped test_ajustari_d300_proba_duk_valid |
| tipuri operatiune 1-5 | d301 | test_d301_rollup.py | √ 03.08 (OPANAF 592/2016: maparea tip->sectiune verificata la sursa struct - 1=S1 achizitii intracom bunuri, 2=S2 mijloace transport noi (bifa mij), 3=S3 produse accizabile, 4=S4 servicii, 5=S4.1 servicii art.150 subset din S4. Rollup S4.1->S4 deja testat; adaugat gard tipuri 1/2/3 pe sectiuni proprii + proba DUK cu TOATE cele 5 tipuri) | FISCAL | OPANAF 592/2016 (structura D301, sectiuni 1-4.1) | test_tipuri_1_2_3_pe_sectiuni_proprii test_toate_tipurile_1_5_proba_duk_valid test_tip5_se_preia_in_sectiunea_4 |
| rollup S4.1->S4 | d301 | test_d301_rollup.py | √ 03.08 (OPANAF 592/2016: in Sectiunea 4.1 se preiau DIN Sectiunea 4 serviciile intracom art.150 - S4.1 e SUBSET al S4, deci fiecare op tip 5 se preia si in S4. Verificat COMPLET de test_d301_rollup.py: S4 contine S4.1, S4=S4.2+S4.1, TVA datorat o singura data (nu se dubleaza), checksum totalPlata_A include 4.1 prin definitie, fara tip5 nu se inventeaza rollup. Proba DUK cu toate tipurile - validatorul impune rollup-ul) | FISCAL | OPANAF 592/2016 (instructiuni formular 301, S4.1 preluat din S4) | test_tip5_se_preia_in_sectiunea_4 test_tip5_plus_tip4_cumuleaza_in_sectiunea_4 test_tva_datorat_o_singura_data_desi_checksum_include_4_1 test_toate_tipurile_1_5_proba_duk_valid |
| checksum totalPlata_A (R28) | d301 | test_d301_rollup.py | √ 03.08 (VERIFICAT CONFORM + gard de legatura. totalPlata_A = INT(sum baza1..5 + tva1..5) pe toate 5 tipurile (struct d301 poz.28, impus de DUK R28); res.total_plata_a=sum(tot) si build_xml emite res (sursa unica, clasa d100). Deja gardat golden (12044 pe XML si pe res) + proba DUK R28 in clusterul rollup; lipsea legatura EXPLICITA res==emis==suma toate tipurile - adaugata. Checksum include 4.1 prin definitie (nu e dubla impozitare: TVA datorat=tva4 o data). Fara fix de cod - era conform) | STRUCTURA | struct d301 poz.28 (totalPlata_A=INT sum baza1..5+tva1..5); DUK regula R28 (respinge orice alt total) | test_checksum_r28_res_egal_emis_egal_suma_toate_tipurile test_tva_datorat_o_singura_data_desi_checksum_include_4_1 test_tip5_emite_sectiune_4_si_4_1_in_xml |
| baza = val x curs | d301 | test_d301_rollup.py (+test_d301_curs.py) | √ 03.08 (CF art.290 alin.(2): baza in valuta = elemente_valuta x curs BNR/BCE valabil la exigibilitate; rotunjire ROUND_HALF_UP la leu intreg = struct ANAF baza integer. Formula+rotunjire CORECTE. REPARAT clasa "valoare gresita tacuta": generatorul (d301.py) + reader-ul grilei (d301_operatiuni_api.lista) faceau calc_baza(..., curs or 1) -> curs absent/0 pe EUR (moneda default) devenea tacit 1 -> baza subevaluata la ANAF fara eroare. calc_baza ridica acum pe curs None/<=0 (chokepoint); scos or 1 din generator+reader; scos DEFAULT 1 din schema (tenant nou fail-loud). Proba: 1000x4.9770=4977, EUR fara curs->ValueError, RON=1->1234. Poarta adauga() valida deja curs>0) | FISCAL | CF art.290 alin.(2) (curs de schimb pt baza in valuta) + OPANAF 592/2016 (structura D301) | test_calc_baza_refuza_curs_absent_sau_nul test_generator_d301_refuza_curs_lipsa_pe_valuta test_lista_api_refuza_curs_nul_nu_fabrica_1 test_calc_baza_corect_pe_curs_valid |
| cota TVA | d301 | test_d301_rollup.py (+test_d301_cota.py) | √ 03.08 (CF art.291: standard alin.(1) 21%% de la 01.08.2025 / 19%% inainte = period-aware CORECT prin common.cota; redusa alin.(2) 11%% de la 01.08.2025; alin.(8) cota achizitiei intracom = cota livrarii interne, deci redusa se aplica in D301. REPARAT: cota redusa era literal 11 indiferent de perioada -> gresita pt luni < 08.2025 (atunci 9%%/5%%, comasate de Legea 141/2025). Fix: redusa din common.cota(tva_redusa), OMISA cand neconfigurata (nu se ofera 11%% fals; adauga o respinge -> nu se persista tva eronat). Proba: 2026 [21,11,0] neschimbat, 2025-06 [19,0]. DECIZIE DE PRODUS deschisa: 9%%/5%% istorice coexistente cer remodelare COTE) | FISCAL | CF art.291 alin.(1)(2)(8) + Legea 141/2025 (comasare cote reduse) | test_cote_2026_standard_21_redusa_11_scutit_0 test_cote_redusa_period_aware_nu_ofera_11_pe_perioada_veche test_adauga_respinge_cota_11_pe_perioada_veche |
| tipuri operatiune IC (L/A/P/S) | d390 | test_d390.py | √ 03.08 (VERIFICARE - fara fix necesar. TIPURI=(L,T,A,P,S,R) d390.py:50 = EXACT nomenclatorul OPANAF 705/2020 (anaf_surse/d390_struct_anaf.txt): L livrari IC bunuri, T triunghiulare, A achizitii IC bunuri, P prestari IC servicii, S achizitii IC servicii, R livrari IC regim special agricultori. codO obligatoriu L/T/P/R (:206), totalPlata_A (:177), gard anti-drop manual (:159 raise) - conforme. GARD-PIN nou: TIPURI==lista oficiala, mutant probat. Obs tangentiale: reclasificare fallback tacit L/A pe tip invalid din DB (misclasif, nu drop); XI tara post-Brexit tine de clusterul nomenclator tari) | FISCAL | OPANAF 705/2020 (nomenclator tip operatiune D390) | test_tipuri_operatiune_sunt_exact_nomenclatorul_oficial_opanaf_705_2020 test_d390_manual_tip_necunoscut_ridica_nu_dispare |
| nomenclator tari (HR->CR) | d390 | test_d390.py | √ 03.08 (NECONFORMITATE reparata, probata DUK. Maparea HR->CR (crezuta corecta: 'prefixul TVA HR se scrie CR') era GRESITA - DUK respinge tara="CR" ('nu se afla in lista', nomenclatorul ANAF D390 nu are CR) si accepta tara="HR". Un partener croat real facea D390 respins de ANAF. FIX: _TARA_XML golit (HR ramane HR, = prefixul TVA = codul ISO). Restul nomenclatorului verificat: setul TARI_UE complet (26 UE non-RO + GB/XI post-Brexit), GB si XI DUK-valide pt 2026 (validatorul le accepta - nu-s bug). EL=Grecia corect. Singura remapare era HR->CR, eliminata) | STRUCTURA | nomenclator tari ANAF D390 (OPANAF 705/2020) - prefix TVA = cod ISO; probat DUK boundary (CR respins, HR valid; GB/XI valide) | test_croatia_emite_HR_nu_CR test_croatia_HR_trece_duk |
| rotunjire aritmetica (A91b) | d390 | test_d390.py test_limita_text_anaf.py | √ 03.08 (VERIFICARE - fara fix. d390._int (d390.py:59) = ROUND_HALF_UP (schimbat de la round() bancar 27.07). ANAF cere half-up nu bancar (DUK regula A91b - referinta validator, nu act normativ §3.1). Deja gardat dublu: identitate cross-generator (test_rotunjirea_e_identica_intre_generatoare importa d390._int) + scan anti-round() bancar (test_toate_generatoarele_rotunjesc_aritmetic). Adaugat proba d390 pe valoare: _int(0.5)=1/2.5=3/112.5=113 (mutant bancar 0/2/112)) | FISCAL | DUK regula A91b (rotunjire aritmetica ANAF - referinta validator) | test_d390_rotunjeste_aritmetic_nu_bancar_A91b test_rotunjirea_e_identica_intre_generatoare test_toate_generatoarele_rotunjesc_aritmetic |
| reclasificari manuale | d390 | test_d390.py | √ 03.08 (FIX asimetrie read-side. Scrierea (salveaza_reclasificare) valida tip+DIRECTIE (emisa:L/T/P/R, primita:A/S); citirea (calcul_d390+operatiuni_auto) facea fallback TACIT la default pe tip invalid, fara verif directie -> misclasificare tacuta daca un override ocolea API (migrare/DB). Contrazicea gardul liniilor manuale (:159). Fix: TIPURI_DIRECTIE mutat in d390.py (sursa unica, import in API fara ciclu) + helper _reclasificare_tip valideaza direciția si RIDICA in ambele cai citire. Pe date valide 0 schimbare. Proba: recl "Z"/"A-pe-emisa" -> ValueError) | FISCAL | DECIZII 21.07 (tranzitie directie: achizitia nu devine livrare) + OPANAF 705/2020 (semantica L/A/P/S/T/R) | test_reclasificare_tip_invalid_ridica_nu_revine_tacit test_reclasificare_directie_gresita_ridica test_reclasificare_muta_tipul_fara_dubla_numarare |
| exigibilitate / prag | d390 | test_d390.py (+test_pull_declaratii.py) | √ 03.08 (VERIFICARE - conform in cazul normal. D390 incadreaza pe data_emitere (pull, fereastra [M-01,(M+1)-01)); CF art.283/284: exigibilitatea intracom = DATA EMITERII facturii, deci data_emitere = exigibilitate -> corect. CF art.325 alin.(4): fara prag valoric, doar lunile cu exigibilitate; d390_are_operatiuni + refuz pe zero = conform. Gard temporal nou pe fereastra pull (golul: testele calcul ocoleau pull). EDGE-CASE consemnat (decizie schema): plafonul "ziua 15 a lunii urmatoare faptului generator cand factura intarzie" (art.284) neimplementabil - facturi n-are data faptului generator) | FISCAL | CF art.283 (exigibilitate livrari IC) + art.284 (achizitii IC) + art.325 (recapitulativa, fara prag) | test_d390_pull_incadreaza_pe_data_emitere_exigibilitate |
| tipuri operatiune (pct.215) | d394 | test_d394.py | √ 04.08 (bump: 03.08->04.08 reverificat la rezolvarea ASI - testele pct.215 rescrise (pin mutat pe validator, datorie->gard invers, ASI scos). VERIFICAT + 1 DATORIE. TIPURI=(A,L,C,V,AI,LS,AS,ASI,N) = EXACT setul de tipuri op1 din structura oficiala D394 (formulele op1(tip)=X din d394_struct_anaf.txt) - pin adaugat. Derivarea tip_operatiune (pct.215) testata. DAR probat izolat pe DUK (substitutie doar a valorii tip pe o baza identica): 8 tipuri (L/V/A/C/N/LS/AS/AI) sunt acceptate ca enum, iar **ASI e RESPINS** ('tip: valoarea ASI nu se afla in lista', la fel ca un tip inventat). Discrepanta pdf-vs-jar: structura pdf are ASI, D394Validator instalat NU. Un contabil care introduce manual tip=ASI face D394 respins. CORECTARE blocata pe DECIZIE DE PRODUS (scoate ASI vs remapare AI/AS vs versiune validator) - schimba ce poate declara contabilul. Gard anti-regresie: test_asi_respins_de_validatorul_instalat_DATORIE. REZOLVAT 03.08 cu greenlight Costin: ASI SCOS din cod (aliniere validator J8); OPANAF 77/2022 confirma AS=achizitii regim special, fost-ASI->AS; fara date ASI de migrat (op1.tip nepersistat); gard devenit INVERS; d394_struct 2020 marcat INVECHIT, OPANAF 77/2022 salvat cu sha256; audit: d301/d390 struct vechi = datorie follow-up) | STRUCTURA | structura D394 pct.215 (formulele op1(tip)=X) + probat pe D394Validator instalat (enum tip: ASI respins, restul 8 acceptate) | test_TIPURI_e_setul_validatorului_curent test_asi_ramane_scos_gard_invers test_tip_respecta_compatibilitatea_cu_partenerul | [citare-istorica: ASI scos din cod 03.08 (redenumit test_asi_ramane_scos_gard_invers)]
| tip_partener | d394 | test_d394.py | √ 04.08 (VERIFICAT CONFORM. clasifica_partener mapeaza exact cele 4 categorii pct.216 (OPANAF 77/2022): 1=inregistrat RO (prefix RO/numeric), 2=neinregistrat (fara CUI/ne-numeric), 3=UE (prefix stat membru), 4=non-UE. Probat: 5 cazuri clasificare corecte (incl HR->3 dupa fix nomenclator) + DUK accepta tip_partener UE/non-UE. Design conform: cui_ro e NORMALIZARE, nu validare - un CUI RO invalid da tip 1 iar validatorul il respinge (R218.2 cuiP invalid), fail-fast; reclasificarea la 2 ar declara gresit un inregistrat ca neinregistrat. Ramura UE/non-UE se sprijina pe _TARI_UE (verificat DUK, cluster HR->CR). Gard consolidat adaugat) | STRUCTURA | pct.216 (OPANAF 77/2022, anaf_surse/opanaf_77_2022): 4 categorii tip_partener; validitate cuiP enforced de validator R218.2 | test_tip_partener_clasificare_pct216 test_partener_ro_valid_e_tip_1 test_partener_ue_e_tip_3_nu_se_exclude test_partener_non_ue_e_tip_4 |
| cote acceptate | d394 | test_d394.py | √ 03.08 (VERIFICARE - conform, d394 e modelul-tinta al lui d301. cota_standard (d394.py:258) period-aware din common.cota (evita int(0.21)=0); cotele operatiunilor validate contra set fix d394.COTE=(0,5,9,11,19,20,21,24) = validator ANAF v5 OPANAF 2194/2025 (21/11 de la 01.08.2025) peste structura 2020; agregare pe cota reala (rectificative vechi -> 19/9/5). Fara literal hardcodat. Garduri: pin set v5 + CROSS-MODUL common.COTE tva_* subseteaza d394.COTE (cota noua in common neacoperita -> cade)) | FISCAL | OPANAF 2194/2025 (validator v5 cote) + structura D394 (cota in 0,5,9,11,19,20,21,24) | test_d394_cote_acceptate_sunt_setul_validatorului_v5 test_d394_cote_acopera_toate_cotele_tva_din_common test_cota_standard_vine_din_sursa_unica |
| rezumat1 campuri complete | d394 | test_d394.py | √ 04.08 (VERIFICAT cazurile comune + 1 NECONFORMITATE ACTIVA. Pentru parteneri INREGISTRATI (RO tip1) si STRAINI (UE tip3/non-UE tip4) setul de campuri rezumat1 (facturi/baza pe fiecare tip cerut de rez1_tipuri, tva doar A/L/C/AI, 0-umplut) e COMPLET si J8-VALID - probat DUK (test_rezumat1_campuri_complete_tp1_tp3_valide_pe_validator). NECONFORMITATE: operatiunile N (tip_partener=2, neinreg) sunt produse AUTOMAT din orice factura de achizitie fara CUI, DAR J8 le RESPINGE - codul nu emite op1.tip_document (pct.228) / op1.tip_N (pct.229) / rezumat1.document_N (pct.60), iar facturiLS e interzis cand document_N<>1 (R41.2). Bug ACTIV (tenanti cu achizitii de la neinregistrati -> D394 respins). CORECTARE = decizie de produs (sourcing tip_N bunuri/servicii; suport document_N 2-5 manual) - vezi DECIZII 04.08. REZOLVAT 04.08 approach (b) Costin: operatiunile N se EXCLUD cu avertisment vizibil care numeste furnizorii+sumele (res.avertismente->UI); restul D394 ramane valid. Gard anti-regresie pastrat (test_N_ar_fi_respins_de_validator_daca_emis_GARD_INVERS). Datorie GARZI: tip_document 2-5 + tip_N UI = implementarea completa (a), campanie proprie) | STRUCTURA | structura D394 (pct.60 document_N, 228 tip_document, 229 tip_N) + reguli validator J8 (R38/R41/R42/R49/R53/R56/R60/R228); probat DUK boundary | test_rezumat1_campuri_complete_tp1_tp3_valide_pe_validator test_operatiuni_N_excluse_cu_avertisment_vizibil test_N_ar_fi_respins_de_validator_daca_emis_GARD_INVERS |
| nomenclator codPR (art.331) | d394 | test_d394.py | √ 04.08 (VERIFICAT CONFORM pe validatorul CURENT. Nomenclatorul d394.CODPR (categorii art.331 -> cod op11: deseuri 22, masa_lemnoasa 23, certificate_emisii 24, energie 25, certificate_verzi 26, cladiri 27, aur 28, telefoane 29, circuite 30, console 31, GAZE_NATURALE 36) + subcodurile NC cereale (1001..121291) sunt TOATE acceptate de D394Validator J8 - probat DUK cod-cu-cod. Comentariul citeaza Ghid_D394_2016 (INVECHIT), dar codurile-s validator-confirmate (ca ASI: sursa veche, cod verificat pe validator). IMPORTANT: gaze_naturale codPR 36 - fostul blocaj al datoriei lit.l (art.331 alin.2 lit.l, Legea 296/2020) - e acum CONFIRMAT valid pe J8; lit.l a fost rezolvat in commit 6675f19 (campanie datorii B: gaze in motor taxare_inversa.CATEGORII lit.l + CODPR 36, xfail inchis). Gard nou: test_codpr_valide_pe_validatorul_curent. OBS: bifa 'taxare inversa|d394' e STALE - inca zice gaze lipseste+datorie xfail (nu mai exista); follow-up cleanup) | STRUCTURA | d394.CODPR (art.331 alin.2 lit.a-l -> cod op11) + subcod NC cereale; sursa comentata Ghid_D394_2016 INVECHITA - AUTORITATE = validatorul J8 (probat cod-cu-cod) | test_codpr_valide_pe_validatorul_curent test_codpr_din_nomenclatorul_oficial test_toate_categoriile_taxare_inversa_au_codpr_d394 test_cereale_codPR_e_subcodul_NC_iar_detaliu_bun_e_categoria |
| taxare inversa | d394 | test_d394.py | √ 04.08 (bump: 03.08->04.08 - datoria gaze naturale (lit.l) INCHISA. 12/12 CONFORM acum: gaze in motor taxare_inversa.CATEGORII (lit.l) + d394.CODPR 36, probat DUK cod-cu-cod (commit 6675f19). Fostul xfail(strict) test_datorie_gaze_naturale_... SCOS la inchidere - bifa il mai cita (citare moarta), curatat aici. Descoperit scriind capitolul de metoda despre clustere. Vezi bifa 'nomenclator codPR (art.331)|d394' care detine proba DUK a gazelor) | FISCAL | CF art.331 alin.(2) lit.a-l (12 categorii) + alin.(6) expirare + structura D394 op11 (codPR) | test_toate_categoriile_taxare_inversa_au_codpr_d394 | [citare-istorica: scos la inchiderea datoriei gaze 6675f19]
| totalPlata_A (R17) | d394 | test_d394.py | √ 04.08 (VERIFICAT CONFORM + gard sursa-unica/DUK. totalPlata_A D394 = Suma(informatii.nrCui1..4) + Suma(rezumat2.baza[L+A+AI]) - formula R17 din validator (comentariul d394.py:18 nota ca formula VECHE era inventata; asta e cea corecta). res.total_plata_a (calculat in calcul_d394) == valoarea EMISA in XML - sursa unica (build_xml emite res, clasa d100). Probat pe validatorul CURENT J8: valoarea corecta (3002) e VALIDA; o valoare gresita (+999) e RESPINSA cu regula R17 (totalPlata_A trebuie egal cu Suma...). Testul vechi test_total_plata_a_dupa_formula_oficiala era tautologic (recalcula formula); gard nou leaga res==emis + probeaza R17 pe validator) | STRUCTURA | R17 validator D394 (totalPlata_A = Suma nrCui1..4 + Suma rezumat2.baza[L+A+AI]); probat pe validatorul curent (valoare corecta valida / gresita respinsa R17) | test_totalPlata_A_R17_sursa_unica_si_probat_pe_validator test_total_plata_a_dupa_formula_oficiala test_nrCui1_e_distinct_pe_cui test_nrCui2_e_numar_de_inregistrari_nu_distinct |
| plan conturi pe norma | d406 | test_d406.py | √ 17.08 (bump: diacriticizare mesaje afisate (09010f7), comportament si verificare NESCHIMBATE; era 04.08: VERIFICAT + REPARAT drop tacit. Planul de conturi emis in SAF-T (MasterFiles/GeneralLedgerAccounts) e FILTRAT pe nomenclatorul OFICIAL al normei firmei (baza_contabila -> plan_oficial din anaf_surse/d406_nomenclatoare_anaf.properties): conturile care nu apartin normei se EXCLUD (ANAF le respinge 'contul trebuie sa se gaseasca in planul de conturi'). AccountID = sintetic (401.05->401). NECONFORMITATE (drop tacit): conturile excluse (strain) erau colectate dar NICIODATA surfaced - pull nici nu le returna. REPARAT: pull returneaza strain, genereaza SEMNALEAZA in avertisment (insert la pozitia 0) numind conturile excluse + norma - ca la N in d394 (decizie Costin: exclus dar VIZIBIL, nu tacit). Fisiere corectate (erau test_limita_text_anaf, sunt test_d406). Garduri: DB strain + plan_oficial) | STRUCTURA | SAF-T MasterFiles/Account: plan filtrat pe nomenclatorul normei (d406_nomenclatoare_anaf.properties); AccountID sintetic (validator: numar intreg); conturi ne-norma respinse de ANAF | test_conturi_straine_de_norma_sunt_semnalate_nu_excluse_tacit test_plan_oficial_citeste_nomenclatorul_norma_A |
| UoM UN/ECE | d406 | test_d406.py | √ 17.08 (bump: diacriticizare mesaje afisate (09010f7), comportament si verificare NESCHIMBATE; era 04.08: VERIFICAT CONFORM pe validatorul SAF-T. UOM_UNECE mapeaza unitatile RO in coduri UN/ECE Recommendation 20 (nu unitatile romanesti). Codurile-tinta (H87 bucata, KGM, GRM, TNE, LTR, MLT, MTR, CMT, KMT, MTK mp, MTQ mc, HUR, DAY, MON, ANN, SET, PR, KWH, MWH) sunt validator-confirmate: probate pe validatorul oficial 15.07.2026 (BUC respins 'nu se afla in lista') SI verificate acum prin EXTRACTIE din D406Validator.jar (/opt/duk/saft/...) - codurile distinctive H87/KGM/.../MWH prezente, BUC=0 (absent). Default H87 (bucata) + semnalare la necunoscut (uom_unece intoarce (cod, False) - mai bine implicit DECLARAT decat XML respins). XSD saft.xsd: UnitOfMeasure=SAFcodeType (cod generic, nu enumerare - lista e in validator). Fisiere corectate (test_limita_text -> test_d406). Gard nou: test_uom_unece_mapare_coduri_valide) | STRUCTURA | UN/ECE Recommendation 20 (nomenclator UoM SAF-T); XSD saft.xsd UnitOfMeasure=SAFcodeType; codurile validator-confirmate (proba 15.07.2026 + extractie D406Validator.jar) | test_uom_unece_mapare_coduri_valide |
| MovementType nomenclator | d406 | test_d406.py | √ 17.08 (bump: diacriticizare mesaje afisate (09010f7), comportament si verificare NESCHIMBATE; era 04.08: VERIFICAT + COMPLETAT nomenclatorul. MISCARI_STOC/MOVEMENT_IMPLICIT sunt DORMANTE - MovementType se emite DOAR in raportarea de STOCURI, iar sectiunile <MovementTypeTable/> si <MovementOfGoods/> se emit GOALE lunar (nimic nu foloseste constanta la generare azi). Cele 3 coduri prezente (10 Achizitie/20 Productie/30 Vanzare) erau CORECTE, dar nomenclatorul era INCOMPLET: oficial are 19 coduri (anaf_surse/d406_schema_anaf.xlsx, foaia 'Nomenclator stocuri'). Nota 5 a foii: o valoare din AFARA listei -> eroare FATALA, D406 respins - deci completitudinea conteaza cand se cableaza raportarea de stocuri (o miscare reala ca 40 'Retur produse vandute' altfel nereprezentabila). COMPLETAT MISCARI_STOC la cele 19 coduri oficiale (40...180); MOVEMENT_IMPLICIT='10' ramane cod valid. XSD saft.xsd: MovementType=SAFcodeType (format, nu enumerare) - lista inchisa e impusa de validator + nota 5. Sursa = foaia oficiala, nu comentariul (LECTIE: comentariul nu e proba). Gard nou test_movementtype_nomenclator_oficial pin pe setul oficial complet. Fisier corectat test_limita_text_anaf->test_d406) | STRUCTURA | ANAF nomenclator 'Nomenclator stocuri' (d406_schema_anaf.xlsx, 19 coduri; nota 5 = out-of-list respins fatal); XSD saft.xsd MovementType=SAFcodeType | test_movementtype_nomenclator_oficial |
| BaseRate (encoding pro-rata) | d406 | test_d406.py | √ 17.08 (bump: diacriticizare mesaje afisate (09010f7), comportament si verificare NESCHIMBATE; era 04.08: VERIFICAT CONFORM + sursa unica. BaseRate (MF.TT.11 din TaxCodeDetails) = pro-rata de DEDUCERE per cod de taxa, encodata ca FRACTIE in [0.0000, 1.0000] unde 1.0000=100.00% (tip SAFBaseRate = decimal 5,4). NECONFORMITATE DE DOCUMENTATIE (a 3-a comentariu-capcana din campanie): foaia oficiala '2. MasterFiles' e INTERN CONTRADICTORIE - proza spune 'Standard is 100 (whole amount) / 60 if 60%' (text OECD-legacy pe procente) DAR restrictia obligatorie din ACEEASI celula e '[0,0000 - 1,0000] (unde 1,0000=100%)'. Restrictia CASTIGA: 100 sau 60 ar viola [0-1] -> D406 respins. Deci BASE_RATE=1 (=1.0000=100%) e CORECT pentru livrari (singurele coduri emise azi; livrarile n-au pro-rata de deducere). Comentariul VECHI cita GRESIT doc-ul ca 'standard 1' - concluzia corecta dar din restrictie, nu din proza; corectat sa citeze contradictia si sa avertizeze 'NU schimba in 100'. REPARAT sursa unica: linia 582 hardcoda literal '1' (BASE_RATE dormant, ca MISCARI_STOC) -> acum emite BASE_RATE (output identic '1'). DATORIE: cote_tva emite doar coduri LIVRARI; un cod achizitie ded. 50% ar cere BaseRate=0.5, nu 1 (dormant azi - nu se emit coduri de achizitie in TaxTable). Gard nou test_baserate_encoding_pro_rata_fractie: encoding fractie [0,1] + SAFBaseRate(5,4) + DINTI (100/60 respinse) + sursa unica emis==BASE_RATE; RED probat cu BASE_RATE=100. Fisier corectat test_limita_text_anaf->test_d406) | STRUCTURA | SAF-T D406 schema MF.TT.11 BaseRate=SAFBaseRate decimal(5,4), restrictie [0,0000-1,0000] unde 1,0000=100% (d406_schema_anaf.xlsx foaia '2. MasterFiles'; proza '100/60' contrazisa de restrictie) | test_baserate_encoding_pro_rata_fractie |
| registration_number (00+CUI) | d406 | test_d406.py | √ 19.08 (bump: re-ancorare dupa garda #2 (campania gardare) care a schimbat un CUI de test (checksum) in test_d406.py; logica registration_number=00+CUI VERIFICATA neschimbata la sursa. 04.08: VERIFICAT + NECONFORMITATE reparata (Grecia EL). Doua reguli oficiale (foaia '5. Structures'): PARTENER (S.C.1) = tip(2 cifre)+cod: 00+CUI (RO, FARA prefix 'RO'), 01+tara+VAT (UE, VIES), 02+tara+VAT (non-UE); FIRMA PROPRIE (5.5 S.CMH.1) = RO+CIF daca platitor TVA, altfel CIF. Ambele forme = conforme. NECONFORMITATE: _UE_NON_RO avea 'GR' (ISO) in loc de 'EL' (prefix VAT/VIES) - schema exemplifica LITERAL '01EL123456789'; un partener grec 'EL...' cadea pe 02 (non-UE) = partener UE raportat GRESIT ca non-UE (bug latent, ca HR->CR la d390). REPARAT: EL in setul UE + normalizare ISO 'GR'->'EL' (_ISO_TO_VAT) ca output-ul sa iasa cum cere ANAF indiferent de sursa. Generalizare pe clasa: d390/d394/intracomunitar folosesc deja corect 'EL'; d406 era singurul outlier (GR din d394 = judetul GIURGIU, nu Grecia). N-am putut proba pe DUK (d406 DUK = xfail preexistent 'cont referit absent'); sursa = exemplul oficial explicit + conventia VIES verificata la d390 (GB/XI). DATORII (dormante/observatii): tip 03 (CNP persoane fizice RO) neimplementat - un CNP ar iesi '00'+CNP nu '03'; validarea cifrei de control/lungime CUI (max 10) lasata validatorului (fail-fast); XI (Irlanda de Nord) -> 02, neexemplificat de ANAF. Gard nou test_registration_number_partener_si_firma_proprie pe exemplele oficiale + Grecia EL; RED probat. Fisier corectat test_limita_text_anaf->test_d406) | STRUCTURA | SAF-T D406 schema '5. Structures' S.C.1 (00/01/02+cod; RO fara prefix; UE VIES cu EL pt Grecia - exemplu '01EL123456789') + 5.5 S.CMH.1 (RO+CIF platitor / CIF neplatitor) | test_registration_number_partener_si_firma_proprie |
| SourceDocuments (facturi reale, PARTIAL) | d406 | test_d406.py | √ 03.08 (FIX period-awareness. Partea solida (27.07): SalesInvoices/PurchaseInvoices cu linii reale pe produs, reconciliate, DUK-valid. REPARAT: TAXCODE_LIVRARI_PRE_2025_08 era DEFINIT dar nefolosit -> pull() emitea mereu codurile post indiferent de data (19%@luna veche -> 310312 taxare inversa gresit). Helper _taxcode_livrari period-aware pe data_emitere la ambele situri livrari; gard. Docstring stale actualizat. OBSERVATII (DECIZII 03.08): Payments gol=datorie pe date, TaxCode achizitii grosier, adresa placeholder, lipsa golden) | FISCAL | Legea 141/2025 (coduri TaxCode livrari 01.08.2025) + structura D406/SAF-T | test_taxcode_livrari_period_aware |
| structura XSD (Header/MasterFiles/GLE) | d406 | test_d406.py | √ 04.08 (VERIFICAT CONFORM prin validare XSD MECANICA contra schemei oficiale SAF-T (/opt/duk/saft/saft.xsd). Schema are targetNamespace 'd406t' (varianta pe cerere) dar structura SAF-T (AuditFile/Header/MasterFiles/GeneralLedgerEntries/SourceDocuments, tipuri, ordine, elemente obligatorii) e IDENTICA cu d406 lunar - se aliniaza namespace-ul pt validare. Cu TOATE sub-sectiunile SourceDocuments populate (SalesInvoices+PurchaseInvoices+Payments+MovementOfGoods) -> XSD-valid ZERO erori: intreaga structura conforma. Raportarea LUNARA omite sub-sectiunile de liste goale (DUK-confirmat 16.07.2026: emise vide -> respinse 'minimum 1 ori'), ceea ce fata de schema d406t produce EXACT O abatere (PurchaseInvoices absent inainte de MovementOfGoods) = comportament lunar corect, nu eroare de structura; gardul confirma ca e SINGURA abatere. Validarea XSD e complementara celei DUK (d406 DUK = xfail preexistent 'cont referit absent' = validare SEMANTICA; aici = STRUCTURA). Gard nou test_structura_xsd_conforma_saft (skip daca saft.xsd lipseste); RED probat cu element injectat in Header. Fisier corectat test_limita_text_anaf->test_d406) | STRUCTURA | Schema oficiala SAF-T saft.xsd (structura AuditFile/Header/MasterFiles/GLE/SourceDocuments); validare XSD mecanica cu lxml, namespace aliniat d406->d406t | test_structura_xsd_conforma_saft |
| structura declaratie710 | d710 | test_d710.py | √ 04.08 (VERIFICAT + NECONFORMITATE reparata (cota bidirectional). Structura declaratie710 (namespace propriu mfp:anaf:dgti:d710:declaratie:v2, atribute header, <obligatie> repetabil cu perechi Initial_I/Corectat_C, d_recN period-aware de la 12.2025) e DUK-VALIDA: 5 cazuri parametrizate trec pe validatorul instalat (test_valid_pe_duk_fara_erori) + gunoi respins (test_duk_respinge_gunoi) - reconfirmat pe DUK 04.08. NECONFORMITATE gasita+reparata: atributul `cota` pe <obligatie> nu era pazit bidirectional (spre deosebire de d100). Dovedit pe DUK 04.08: cod 121 FARA cota -> respins 'R17: cota (lipsa) - Cota impozitare eronata'; cota pe cod != 121 -> respins 'R17: cota nu se completeaza'. Codul putea genera XML respins in ambele directii. REPARAT: gard bidirectional in build_xml (121 fara cota / cota pe alt cod -> ValueError), ca la d100. Valoarea = rata micro period-aware (DUK accepta 1 si 3, respinge 16 'in afara intervalului') - range-check ramane la validator, gardul pazeste regula STRUCTURALA (prezenta/absenta). Generalizat: tiparul obligatie-cota-121 apare doar in d100 (deja pazit) si d710 (acum) - acoperire completa. Gard nou test_structura_cota_bidirectional_gard; RED probat (121 fara cota nu ridica inainte)) | STRUCTURA | Structura D710Validator.jar (parameters v10) + reguli DUK: namespace d710:v2, obligatie Initial/Corectat, d_recN de la 12.2025, cota OBLIGATORIU+NUMAI cod 121 (R17, probat DUK 04.08); validare pe validatorul instalat | test_structura_cota_bidirectional_gard test_namespace_e_d710_nu_d100 test_xml_are_perechea_initial_corectat test_d_recN_doar_de_la_perioada_12_2025 test_valid_pe_duk_fara_erori test_duk_respinge_gunoi |
| nomenclator COD_BUGETAR | d710 | test_d710.py | √ 10.08 (bump: assertions test_cod_bugetar reparate TURA 3 tura 29 - escape-hatch buggy 'permite extinderi' inlocuit cu blocaj nomenclator + R14a PRE-DUK; DUK-backed R14a pastrat, re-verificat valid. VERIFICAT pe DUK + gard anti-drop. cod_bugetar per cod_oblig, SURSA UNICA d100.COD_BUGETAR (cluster d100 verificat 03.08). Codurile dominante 121/103 -> 5503XXXXXX. Confirmat pe DUK 04.08 (regula R14a): validatorul D710 accepta 5503XXXXXX pentru 121 SI 103; mesajul la valoare gresita releva inca vechiul cont 20470101 (validator tolerant/invechit in text) DAR 5503XXXXXX (forma curenta, cont unic 5503 din 26.07.2018) e VALID - codul emite forma curenta. NECONFORMITATE (gard lipsa, ca la cota): d710 nu avea gardul anti-drop pe cod_bugetar gol (d100 il are). Un cod nemapat fara valoare manuala emitea XML fara atributul cod_bugetar -> respins de DUK (R14a). REPARAT: gard anti-drop in calcul_d710 (cod fara cont bugetar -> ValueError, eroare clara in aplicatie, nu mesaj criptic DUK). DATORIE: coduri D710 valide dar nemapate (130/131/132 din StatusTable) sunt in afara LIMITEI motorului (cer data_I / modele suma diferite). Gard nou test_cod_bugetar_nomenclator_duk_si_antidrop (DUK-backed R14a + anti-drop); RED probat. Ramane si test_cod_bugetar_din_nomenclator) | STRUCTURA | DUK regula R14a (cod bugetar = X pt cod_oblig; 5503XXXXXX acceptat pt 121/103, probat DUK 04.08); sursa unica d100.COD_BUGETAR (cont unic 5503, 26.07.2018) | test_cod_bugetar_nomenclator_duk_si_antidrop test_cod_bugetar_din_nomenclator |
| checksum R11b | d710 | test_d710.py | √ 04.08 (VERIFICAT CONFORM pe DUK. totalPlata_A = suma de control R11b = SUMA pe TOATE obligatiile a (suma_dat_I + suma_plata_I + suma_dat_C + suma_plata_C); cum suma_plata=suma_dat pe fiecare latura, = 2*(dat_I+dat_C) pe obligatie. Confirmat pe DUK 04.08: multi-obligatie 121(100->150)+103(200->300) -> totalPlata_A=1500 VALID; valoare gresita (9999) -> respinsa 'R11b: Suma de control totalPlata_A(9999)= ...calculata cf. regulii(1500)'. Sursa unica: build_xml emite res.total_plata_a direct (clasa d100/d394), fara recalcul divergent. Cod CONFORM, fara fix. Gard nou test_checksum_r11b_multi_obligatie_si_duk (multi-obligatie + sursa unica + DUK-backed corect/gresit); ramane si test_totalPlata_A_suma_dat_plus_plata_ambele_laturi) | STRUCTURA | DUK regula R11b (totalPlata_A = Suma(suma_dat_I+suma_plata_I+suma_dat_C+suma_plata_C) pe obligatii; probat DUK 04.08 corect valid / gresit respins) | test_checksum_r11b_multi_obligatie_si_duk test_totalPlata_A_suma_dat_plus_plata_ambele_laturi |
| R15 termen definitivare | d710 | test_d710.py | √ 04.08 (VERIFICAT CONFORM pe DUK. Cod 121 (micro), trimestrul 4 (luna 12): scadenta = 25.06 an urmator = termenul de DEFINITIVARE, NU 25.01. Confirmat pe DUK 04.08 (DUK regula R15): pentru cod_oblig=121 luna=12, o scadenta gresita e respinsa cu EROARE 'R15: scadenta (X) ar fi trebuit sa fie 25.06.2026' (valoare UNICA, eroare - nu avertisment). Codul produce exact (25,6,an+1), stabil pe an. Alt trimestru 121 -> 25 a lunii urmatoare. (Contrast: cod 103 profit trim4 -> 25.01 sau 25.12, doar avertisment.) Cod CONFORM, fara fix. Gard nou test_r15_termen_definitivare_micro_trim4_duk (unit + DUK-backed cu 25.06 revelat); ramane si test_scadenta_micro_trim4_e_25_iunie_an_urmator) | STRUCTURA | DUK regula R15 (cod 121 trim4 -> scadenta 25.06 an urmator, definitivare micro; probat DUK 04.08 valoarea unica ceruta) | test_r15_termen_definitivare_micro_trim4_duk test_scadenta_micro_trim4_e_25_iunie_an_urmator |
| scadente | d710 | test_d710.py | √ 04.08 (VERIFICAT pe DUK + NECONFORMITATE reparata (nr_evid urmeaza scadenta). Scadenta calculata: 25 a lunii urmatoare (standard, _scadenta_zile) + exceptia micro trim4 (cod 121 luna 12 -> 25.06 an urmator, cluster R15). Confirmat pe DUK 04.08 (DUK regula R15): cod 121 toate trimestrele (25.04/25.07/25.10 + 25.06 trim4, EROARE strict); cod 103 (25.01 SAU 25.12 trim4, avertisment). NECONFORMITATE (footgun pe override): nr_evid EMBEDA scadenta (poz.12-17) si DUK regula R16 o verifica fata de atributul scadenta; codul folosea scadenta CALCULATA pentru nr_evid chiar cand atributul era override manual -> mismatch. Dovedit pe DUK 04.08: cod 103 trim4 cu scadenta alternativa VALIDA (25.12.2025, acceptata de R15) primea nr_evid pe 25.01 -> respins R16. REPARAT: nr_evid derivat din ACEEASI data ca scadenta emisa (override parsat ZZ.LL.AAAA, format gresit -> ValueError). GENERALIZAT PE CLASA: acelasi footgun in d100 (linia 142-144, scadente|d100 cluster inchis 03.08) - reparat identic in d100.py (clasa d100/d710). Gard nou test_scadente_nr_evid_urmeaza_scadenta_emisa (unit + nr_evid poz.12-17 urmeaza override + format invalid ridica + DUK fara R16); RED probat. Ramane si test_scadenta_micro_trim4_e_25_iunie_an_urmator) | STRUCTURA | DUK regula R15 (scadenta 25 luna urmatoare + micro trim4 25.06) si DUK regula R16 (nr_evid embeda scadenta, verificat fata de atribut); probat DUK 04.08 | test_scadente_nr_evid_urmeaza_scadenta_emisa test_scadenta_micro_trim4_e_25_iunie_an_urmator |
| plafon diurna neimpozabila | deconturi | test_deconturi.py test_versionare_formule.py | √ 04.08 (bump: 03.08->04.08 datoria period-awareness istorica REZOLVATA in 6675f19. calcul CURENT CONFORM + istoric REZOLVAT. Plafon = min(2,5x diurna bugetara; 3 salarii/zile lucratoare) x zile = conform CF art.76 alin.(4^1) pt 2023+ (verificat la sursa). Adaugat gard golden (lipsea). REZOLVAT period-awareness: valorile HG istorice confirmate la sursa (HG 714/2018 intern 20 lei + HG 518/1995 extern, salvate in anaf_surse/), Ordin MF 1235/2023 -> 23 lei din 01.04.2023; diurna e period-aware in deconturi.py (plafon 2020 < 2026 crescator, pre-1995 ridica). xfail-ul test_datorie_plafon_diurna_period_aware_istoric inchis in 6675f19) | FISCAL | CF art.76(2) lit.k + alin.(4^1); HG 714/2018; HG 518/1995; Legea 72/2022 (cap 3-salarii) | test_plafon_diurna_curent_conform_art76 test_plafon_diurna_capul_3_salarii_musca_pe_salariu_mic test_plafon_diurna_dispecer_versionat | [citare-istorica: scos la inchiderea datoriei diurna 6675f19]
| credit sponsorizare / D177 | sponsorizari | test_operatiuni_speciale.py (+test_datorie.py) | √ 03.08 (PROFIT CONFORM + observatii. Credit profit = min(0,75%% CA; 20%% impozit) + registru = conform CF art.25 alin.(4) lit.i (verificat la sursa); report 7 ani corect eliminat (2022). Gardat de test_operatiuni_speciale.py. NECONFORMITATE micro: credit=0 la orice data desi 2019-2023 avea credit (fostul art.56 alin.1^5 abrogat OUG 115/2023) - fix blocat pe text istoric neconsolidat, DATORIE xfail strict. D177 formular ABSENT = decizie de produs (Ordin 3562/2024). Endpoint neperiodizat = observatie) | FISCAL | CF art.25(4) lit.i (profit) + fostul art.56 alin.1^5 (micro, abrogat OUG 115/2023) + Ordin ANAF 3562/2024 (D177) | test_plafon_dublu_min_ca_impozit test_credit_sub_plafon_lasa_redirectionabil test_micro_fara_credit test_beneficiar_neinscris_fara_credit |
| rezerva legala | motor | test_operatiuni_speciale.py | √ 03.08 (formula CONTABILA conforma + deductibilitate fiscala = decizie produs. Rezerva contabila (motor.py: 5% profit, plafon cumulat 20% capital - rezerva existenta) = corecta structural (Legea 31/1990 art.183, OMFP 1802/2014 pct.421), period-aware. Adaugat gard golden pe valoare (lipsea). NECONFORMITATE: deductibilitatea FISCALA CF art.26(1)a (baza = profit + cheltuiala impozit, plafon 20% capital subscris/varsat) LIPSESTE - d101 P6 e input manual; = DECIZIE DE PRODUS (schimba declaratia profit). motor.py e cod mort (niciun apelant productie)) | FISCAL | Legea 31/1990 art.183; OMFP 1802/2014 pct.421 (rezerva contabila); CF art.26 alin.(1) lit.a (deducere fiscala) | test_rezerva_legala_5pct_plafon_20pct_capital |
| zilieri (impozit+CAS) | contracte_speciale | test_versionare_formule.py | √ 03.08 (FIX period-awareness CAS. Impozit 10%% (CF art.76(2) lit.r) + CASS 0 (nu-s in art.157) = CONFORME. REPARAT: codul aplica CAS 25%% din 2018-01-01, dar CAS pe zilieri exista legal doar de la 01.05.2019 (OUG 26/2019: adauga CF art.139(1) lit.s + Legea 52/2011 art.9^1; abroga exceptarea art.142 lit.t). 2 variante datate: 2018 doar impozit 10%% (net 90); 2019 CAS 25%% + impozit pe brut-CAS (net 67,5). Verificat /tmp/cf.txt. Obs: plafon zile 90/an doar in docstring, neaplicat) | FISCAL | CF art.76(2) lit.r (impozit) + art.139(1) lit.s (CAS, OUG 26/2019) + Legea 52/2011 art.9^1; CF art.142 lit.t (fosta exceptare) | test_calcul_zilier_dispecer_versionat |
| regim marja second-hand | tva_marja | test_versionare_formule.py | √ 03.08 (VERIFICARE - motor CONFORM. TVA pe marja = marja x cota/(100+cota) (suta MARITA, TVA extras din marja), conform CF art.312 alin.(4) (baza=marja EXCLUSIV taxa); marja negativa -> TVA 0. NU cota/100. (art.313=aur, codul citeaza corect 312). Lipsea test numeric -> gard golden (marja 400 cota 21 -> 69,42; negativa -> 0; cota 19 -> 63,87). OBSERVATII main.py: cota_ceruta nu valideaza period-aware; la_data nu se paseaza la motor) | FISCAL | CF art.312 alin.(4) (baza=marja exclusiv taxa; norme pct.86) | test_tva_marja_formula_suta_marita_art312 |
| regim marja turism | tva_marja_turism | test_versionare_formule.py | √ 03.08 (VERIFICARE - motor CONFORM. TVA = marja_taxabila x cota/(100+cota) suta marita (CF art.311 alin.4); scutire PROPORTIONALA non-UE (alin.5, coef cost_non_ue/cost_total) tratata; marja negativa -> 0; cota period-aware (param). Consistent cu art.312. Lipsea test numeric -> gard golden (tot UE 69,42; 50%% non-UE scutita 200/TVA 34,71; negativa 0). OBSERVATII: neintegrat in datorie.py (fara apelant); cota din default la integrare de luat period-aware) | FISCAL | CF art.311 alin.(4) (marja exclusiv taxa) + alin.(5) (scutire non-UE) | test_marja_turism_formula_suta_marita_si_scutire_non_ue_art311 |
| impozit dividend | decontari_asociati | test_impozit_dividend.py | √ 16.08 (bump: cota 2025 corectata 8%%->10%% (OUG 156/2024 art.LXIV+LXV, de la 01.01.2025; confirmat d205_struct_anaf.txt:6 "8%%/2024,10%%/2025,16%%/2026") - reverificat la sursa, concluzia 03.08 ca "2023-2025=8%%" era gresita pe 2025. FIX cote istorice. Mecanism period-aware corect (common.cota), DAR datele gresite: intrarea pre-2026 era 10%% (petic "else 10") - 10%% NU a fost niciodata cota pe dividende (e impozit pe VENIT art.78) -> 2023-2025 primeau 10%% in loc de 8%%. REPARAT: 3 intrari verificate la sursa - 5%% (2016-2022, Legea 227/2015+OUG 50/2015), 8%% (2023-2024, OG 16/2022), 10%% (2025, OUG 156/2024), 16%% (2026, Legea 141/2025). Teste care cimentau 10%% actualizate la 8%%. Proba 2020->5%%, 2024->8%%, 2026->16%%) | FISCAL | CF art.97 alin.(7); OUG 50/2015 (5%% din 2016); OG 16/2022 (8%% din 2023); Legea 141/2025 (16%% din 2026) | test_impozit_dividend_period_aware_din_cote test_cota_dividend_si_lichidare_sursa_din_cote |
| contributii PFA (praguri CAS/CASS pe sm) | d212 | test_d212_reper.py | √ 03.08 (VERIFICARE - calcul CONFORM. CAS 25%% praguri 12/24 sm (CF art.148), CASS 10%% LINIAR 6 sm..plafon 60/72 sm (CF art.170 alin.1 - treptele doar pt venituri pasive, nu PFA), impozit 10%% pe net-CAS-CASS. sm period-aware. REPARAT citare temei: plafonul 72 sm 2026 era atribuit gresit "Legea 141/2025" -> corect Legea 239/2025 art.XII pct.19 (valoarea 72 sm corecta). Obs: calea 2026 dormanta in productie (poarta an=2025), de ridicat la 2027) | FISCAL | CF art.148-149 (CAS), art.170 alin.(1) (CASS PFA liniar), art.68-69 (venit net); Legea 239/2025 art.XII pct.19 (plafon CASS 72 sm 2026) | test_d212_reper_din_cota_nu_literal test_d212_apare_in_graful_salariu_minim |
| rutare D300 (IC/export/avans/furnizor/rand manual) + F125 reclasificare bun->serviciu + reconciliere D300<->D390 | d300 | test_d300_b1_rutare.py | √ 17.08 (bump: diacriticizare mesaje afisate (09010f7), comportament si verificare NESCHIMBATE; era 15.08: c8d3947 - fisier nou intrat in git la c8d3947 = HEAD; ancoreaza comportamentele B1-B4: achizitie IC -> R5 + oglinda R18 nu R26, livrare IC -> R1, export non-UE -> R14, RO/zero nu autoclasifica, anti-dubla-numarare la rand manual peste IC, fereastra avans pe emitere, deducere amanata furnizor cu TVA la incasare, paritate preview<->depunere pe randul manual persistat. EXTINS 15.08: F125 reclasificare bun->serviciu pe sursa unica d390_reclasificare - MUTA nu adauga (emisa P->R3, primita S->R7+R20 oglinda), teste reclas_* comise la HEAD 0b132c3. Lotul curent (NEcomis) adauga si gardul de reconciliere cross-declaratie D300<->D390 (R3_1==bazaP, R7_1==bazaS) prin 3 teste noi [recon_P_emisa/recon_S_primita/recon_sursa_unica] - NU sunt inca citate mai jos pentru ca gardul A citeste starea COMISA (git HEAD); intra in coloana de citare la commitul lotului, fara re-ancorare (niciun test citat nu e redenumit). Adaugarea de teste NU cere re-ancorare) | FISCAL | OPANAF 174/2026 (structura D300 v12); Legea 141/2025 (cote); CF art.282 (exigibilitate - avans/TVA la incasare), art.294 (scutiri export/livrari IC); OPANAF 705/2020 (D390, tipuri L/T/A/P/S/R) | test_livrare_ic_bunuri_ruteaza_R1 test_achizitie_ic_bunuri_R5_oglinda_R18 test_export_non_ue_ruteaza_R14 test_discriminare_pe_tara_RO_zero_nu_autoclasifica test_antidubla_numarare_ic_livrare_manual_ridica test_avans_fereastra_pe_emitere_nu_reapare test_deducere_amanata_furnizor_la_incasare test_persistenta_manual_paritate_preview_depunere test_reclas_emisa_serviciu_P_muta_R1_la_R3 test_reclas_primita_serviciu_S_muta_R5R18_la_R7R20_oglinda test_reclas_tip_nelegal_pt_directie_ridica test_reclas_antidubla_serviciu_S_plus_manual_R7_ridica test_reclas_absenta_pastreaza_L_A_actual test_reclas_T_emisa_ramane_bunuri_dar_semnaleaza test_reclas_cheie_per_luna_5tuple |
| versionare asseturi (cache-bust ?v= = hash de continut, anti-cascada) | asseturi | test_versionare_assets.py | √ 15.08 (087b33a - fisier nou intrat in git la 087b33a = HEAD; ancoreaza disciplina ?v=: tokenul e hash de CONTINUT nu contor manual - un modul JS/CSS schimbat fara re-stampilare are referinta cu token vechi = gard rosu; o referinta catre un asset inexistent = rosu; generatorul e versioneaza_assets.py. Cauza constatarii #1, selectoare Clasificare TVA invizibile din cache, = ?v=6 neincrementat la emitere_ecran.js -> acum staleness-ul e gardat) | INFRA | disciplina cache-bust ?v= (Design System - asseturi versionate); anti-cascada prin hash de continut | test_generator_prezent test_hash_stabil_fata_de_versiuni test_nicio_referinta_catre_asset_inexistent test_fiecare_referinta_are_tokenul_hashului_curent test_acelasi_asset_are_acelasi_token test_gardul_vede_referinte |

Numărul nu e ținta. Ținta: fiecare cluster FISCAL să aibă cifra afirmată cu temei citat la sursă.

### V1 (01.08.2026) — inventar completat: reguli si teste care erau fara cluster

INAINTE: 62 clustere. DUPA: 69 (+7 orfane adaugate mai sus). Cifra corecta > cifra stabila.

(A) REGULI FISCALE ORFANE (marker TEMEI, modul absent din inventar) - ADAUGATE ca randuri: deconturi.plafon_diurna,
sponsorizari.plafon_credit+credit_sponsorizare, motor.rezerva_legala, contracte_speciale.calcul_zilier,
tva_marja.vanzare_marja, tva_marja_turism.marja_turism_special, decontari_asociati.cota_dividend. Toate produceau
o valoare fiscala fara sa apara in inventar. GOL: 5 au DOAR test de dispecer (versionare), niciun golden de
VALOARE la sursa (plafon_diurna, rezerva_legala, calcul_zilier, vanzare_marja, marja_turism_special) - regula
exista, nimic nu-i verifica cifra contra legii. De scris la reverificarea clusterului.

(B) TESTE care asertaza o valoare fiscala, absente din Functie(test) - clasificate (scan pe core/test_*.py):
- MECANISM (legitim fara cluster, verifica masinaria): test_graf_temei(4), test_temei_structurat(7),
  test_versionare_formule(13), test_expirare_cote_de_baza(5), test_inventar_a(3), test_perioada_indisponibila(3),
  test_impozit_dividend period-aware, test_tva_incasare plafon_pe_data.
- DE VALOARE, apartin unui cluster EXISTENT dar NELISTATE (test_salarizare, ~10): deducere
  (test_peste_plafon_deducere_zero, test_minim_difera_pe_semestru, test_brut_6000_fara_dependenti_sem2),
  concedii (test_cass_doar_pe_01_07_10, test_cm_cas_25pct_uniform, test_cm_prima_zi_diminuata_boala ...).
  NU le-am adaugat la clusterele BIFATE (√ deducere/concedii): garda anti-stale le-ar compara cu commitul √ si,
  daca vreuna s-a schimbat dupa, √-ul ar CADEA. HELD - de adaugat la reverificarea clusterului, cu proba ca nu
  cad √-urile (ramificatie: nu resetez singur).
- DE VALOARE, acum acoperite de orfanele adaugate: test_operatiuni_speciale(4 -> sponsorizari),
  test_cota_dividend (-> decontari_asociati).

### PAS 6 (02.08.2026) — au temei cele 7 orfane adaugate la V1?

Verificat mecanic (marker TEMEI in docstring + Temeiuri in inventar):
- AU marker TEMEI (6): deconturi.plafon_diurna, sponsorizari.plafon_credit+credit_sponsorizare, motor.rezerva_legala,
  contracte_speciale.calcul_zilier, tva_marja.vanzare_marja, tva_marja_turism.marja_turism_special.
- decontari_asociati.cota_dividend: FARA marker de functie - dar e CITITOR SUBTIRE (intoarce cota(impozit_dividend)),
  temeiul traieste in COTE (CF art.97 / Legea 141/2025) + Temeiuri in inventar. Nu e regula de formula -> nu cere marker.
CONCLUZIE: toate 7 clusterele orfane AU temei; niciunul fara. NU se bifeaza inca: 5 au DOAR test de dispecer
(versionare), fara golden de VALOARE la sursa (plafon_diurna, rezerva_legala, calcul_zilier, vanzare_marja,
marja_turism_special) -> in secventa de verificat. sponsorizari + decontari au teste de valoare (test_operatiuni_speciale
/ test_impozit_dividend), dar nebifate pana la reverificare la sursa cu golden calculat de mana.

LIMITA declarata (bilant_api): detectia vede doar reguli cu marker TEMEI sau cota(). O regula cu rate hardcodat
fara marker e invizibila - se inchide cu gardul GRI de literale la 0 (GARZI cat.3, LIPSA). De construit separat.

### V2 (01.08.2026) — graful vede tot? NU. Vede doar dependentele rutate prin cota()

Graful (`graf_temei`) leaga functie -> cota DOAR prin apeluri `cota("x")` in corp. Numarul de clustere cu
ZERO dependente in graf e MARE: cele 29 structurale (nomenclator/checksum/XML) - fundamental zero; iar dintre
cele 40 fiscale, majoritatea iau rata ca INPUT contabil (`manual`) sau o hardcodeaza -> tot zero in graf.
Dependenta e vizibila azi doar in familia salarizare (calcul_salariu/deducere/taxe_cm cheama cota). Deci
"graful vede tot" e FALS: e complet doar unde se foloseste cota().

3 clustere verificate MANUAL (citit codul):
1. checksum totalPlata_A (d100, STRUCTURA) - suma campurilor de obligatie, nicio valoare fiscala.
   VERDICT: FUNDAMENTAL (zero dependenta reala).
2. cota micro 121 (d100) - rata vine ca input (`manual`); DEFAULT hardcodat `Decimal("1")` (micro) /
   `Decimal("16")` (profit), ocoleste cota() (d100.py:239-247). VERDICT: DEPENDENTA ASCUNSA - cotele
   micro 1%/3% + profit 16% nu-s in COTE, graful e orb. Vizibil prin: mutare in COTE + cota(), sau gardul GRI.
3. d212_engine (PFA/D212 - modul ORFAN, absent din inventar, dar LIVE prin rip_api/control_fiscal_api) -
   hardcodeaza `PlafoaneD212(salariu_minim=4050)` ca reper anual (d212_engine.py:28-34). Toate pragurile
   CAS/CASS (12/24/60/72 sm) = multipli de acest 4050 literal. VERDICT: DEPENDENTA ASCUNSA pe salariu_minim -
   graful nu vede D212 depinzand de salariul minim. Valoarea e SURSA-VERIFICATA (11.07: reperul D212 = sm la
   1 ian, FIX pe an, deliberat neschimbat de majorarea 4325) - corecta azi, dar LINK-ul e invizibil.
   Vizibil prin: `cota("salariu_minim", date(an,1,1))` in loc de literalul 4050 (pastreaza semantica "fix pe an").

DEPENDENTE NEVAZUTE enumerate: (a) micro/profit rate default (d100); (b) d212 salariu_minim reper (+ toate
pragurile sm). CE LE FACE VIZIBILE: rutarea literalului prin cota()/COTE (specific) + gardul GRI de literale
fiscale la 0 (general, GARZI cat.3 LIPSA - inca de construit). Niciuna nu produce azi o cifra GRESITA (default pe
cale manuala; d212 sursa-verificat) - sunt goluri de VIZIBILITATE, nu buguri active. REPARATIE = gardul GRI
(campanie separata) + reroute; d212 e si orfan de inventar (de adaugat ca rand la fel ca V1).

## Estimare de efort pe clusterele nebifate (ESTIMARE, 01.08.2026 — NU angajament)

**Estimarea NU e criteriu de prioritizare.** Departajarea in secventa se face pe RISC (intra intr-o declaratie depusa la ANAF), nu pe efort - un cluster MIC si riscant se face inaintea unuia MARE si izolat. Estimarea serveste doar la a sti ORIZONTUL campaniei, nu ordinea. (Regula de ordonare: la sectiunea Secventa de verificare.)

Cerută de două ori, neapărută în raport. Estimare din COD + inventar, clusterele **NU** sunt verificate
aici — doar clasate pe efort. Calibrare din cele 7 atinse: **MARE** (o zi sau mai mult — multe reguli,
surse contradictorii, ca *deducere personală* √31.07) · **MEDIU** (câteva ore — mai multe valori/coduri,
ca *tichete* / *concedii medicale* PARTIAL 31.07) · **MIC** (sub o oră — puține valori, sursă clară:
nomenclatoare, checksum-uri, trunchieri, rotunjiri).

Nebifate: **55** din 62 (7 atinse: 5 √ + 2 PARTIAL). Repartiție efort × risc:

| Efort | FISCAL | STRUCTURA | Total | Interval/buc | Sub-total |
|---|---|---|---|---|---|
| MARE  | 6  | 0  | **6**  | 1–1,5 zile | 6–9 zile |
| MEDIU | 12 | 4  | **16** | 2–4 h       | ~4–8 zile |
| MIC   | 8  | 25 | **33** | 0,3–1 h     | ~1,5–4 zile |
| **Total** | **26** | **29** | **55** | | **≈ 12–21 zile** |

Centru realist: **~15 zile-om** de lucru focalizat (RED→verde→mutație→sursă per cluster), reductibil vezi caveat.

**MARE (6, toate FISCAL):** cota profit 16%+IMCA (d101) · amortizare (d101) · exigibilitate/TVA la încasare
(d300) · pro-rata deducere (d300) · ajustări (d300) · SourceDocuments facturi reale (d406).

**MEDIU (16):** *FISCAL(12)* tichete culturale · tichete creșă · baze contribuții CAS/CASS/imp/CAM (d112) ·
concedii medicale asiguratB3/D (d112) · sect_II tip_venit (d205) · cote TVA→rânduri (d300) · taxare inversă
(d300) · tipuri operațiune 1-5 (d301) · tipuri operațiune IC L/A/P/S (d390) · reclasificări manuale (d390) ·
exigibilitate/prag (d390) · taxare inversă (d394). *STRUCTURA(4)* tipuri operațiune pct.215 (d394) · rezumat1
câmpuri complete (d394) · plan conturi pe normă (d406) · structură XSD Header/MasterFiles/GLE (d406).

**MIC (33):** *FISCAL(8)* rotunjire A91b (d112) · rotunjire (d205) · rotunjire aritmetică (d300) · rollup
S4.1→S4 (d301) · bază=val×curs (d301) · cotă TVA (d301) · rotunjire aritmetică (d390) · cote acceptate (d394).
*STRUCTURA(25)* d100 ×4 (nomenclator cod_oblig↔bugetar, cotă micro 121, checksum R11b, scadențe/nr_evidența) ·
d101 ×2 (structură P1-P53, R17 Data_S) · d112 ×2 (limită text 75, nomenclator cod_oblig) · d205 ×2 (checksum
totalPlata_A, trunchiere den/adresă) · d300 (rânduri/checksum) · d301 (checksum R28) · d390 (nomenclator țări
HR→CR) · d394 ×3 (tip_partener, nomenclator codPR art.331, totalPlata_A R17) · d406 ×4 (UoM UN/ECE,
MovementType, BaseRate, registration_number) · d710 ×5 (structură decl710, nomenclator COD_BUGETAR, checksum
R11b, R15 termen, scadențe).

**Caveat — reduce totalul (nu reflectat în cifra brută):**
- **structura P1-P53 (d101) + R17 Data_S** sunt de facto ACOPERITE de reconstrucția d101 din 01.08 (golden
  lanț formule + DUK valid, DECIZII 01.08); rămâne doar bump de inventar, nu muncă. −2 MIC efectiv.
- Clusterele de **cotă TVA** (d300 cote→rânduri, d301 cotă TVA, d394 cote acceptate) se sprijină pe clusterul
  TVA DEJA verificat (Legea 141/2025 în common.COTE, period-aware, golden test_d394) — efort real spre capătul
  de jos al intervalului.
- **d112 baze/concedii** se sprijină pe salarizare deja verificată (taxe_cm canonic, apelat și de d112).
Cu discount-urile, banda efectivă coboară spre **~10–16 zile**.



---

# SESIUNEA B — testarea pe flux

## Starea sesiunii B

| Fază | Stare | Când |
|---|---|---|
| Faza 0 — decuplarea suitei de firmele persistente | închisă | 29.07 |
| Faza 1 — cele 7 firme (F1–F7) pe flux | neîncepută | |

Etapele fluxului (Faza 1), `√ DD.MM` = etapa are teste cap-coadă pe o firmă:
| Etapă | Stare |
|---|---|
| 1. Migrare / preluare | |
| 2. Configurare firmă | |
| 3. Intrare documente primare | |
| 4. Salarizare | |
| 5. Contabilizare | |
| 6. Sfârșit de lună | |
| 7. Verificări interne | |
| 8. Declarații — generare | |
| 9. Declarații — depunere | |
| 10. Ieșiri externe | |
| 11. Transversal | |


## De ce pe flux, nu pe zone

Campania din iunie a testat pe **zone** (ecrane, module): 17 zone, ~190 de teste, verde.
N-a fost destul — D101 a trecut testele de zonă pentru că nimeni n-a verificat că registrul
*de sub el* avea rânduri. Zonele ascund **propagarea**; un test pe flux o urmărește.

## Regula cascadei

**Un eșec la etapa N invalidează toate rezultatele de la N+1 în jos.** Nu ai voie să declari
„D300 verde" dacă etapa 5 (contabilizare) n-a fost dovedită pe aceleași date.

## Regula bazei nule

**Orice declarație cu bază 0, zero linii sau total 0 e EROARE până la proba contrară.**
„Fără activitate" se declară EXPLICIT (firma F7), nu se deduce din tăcere.

DUKIntegrator validează STRUCTURA, nu conținutul. Dovedit de trei ori: D101 (bază zero din
query rupt), D406 (registru gol sub mască), D112 (salarii zero din coloană dispărută) —
toate treceau validatorul.

## Firmele de test

Setul e derivat din **legislație**, nu din ce s-a construit. Dimensiunile care produc
comportament diferit:

| Dimensiune | Valori | Temei |
|---|---|---|
| Sistem contabil | partidă dublă / simplă | L 82/1991; OMFP 1802/2014; OMFP 170/2015 |
| Regim TVA | neplătitor · lunar · trimestrial · la încasare · art. 317 | CF art. 310, 316, 317, 322, 282(5) |
| Impozit | micro 1%/3% · profit 16% · PFA real · PFA normă | CF Titlul II, III, IV |
| Operațiuni | achiziții IC · servicii UE · taxare inversă · salariați · fără activitate | CF art. 307, 331; OUG 158/2005 |

| ID | Formă | TVA | Impozit | Ce testează UNIC |
|---|---|---|---|---|
| **F1** | SRL | lunar | micro 1% | comerț cu stoc, 3 salariați, descărcare de gestiune, D300 lunar, D394, D112, D101, D406 |
| **F2** | SRL | trimestrial | profit 16% | D300 **trimestrial**, D100, amortizare, mijloace fixe, registru de casă |
| **F3** | SRL | neplătitor + **art. 317** | micro 3% | **D301** (achiziții IC + servicii UE tip 5), **D390**, taxare inversă |
| **F4** | SRL | **TVA la încasare** | micro | exigibilitate la încasare — logică complet separată |
| **F5** | PFA | plătitor | **sistem real** | partidă simplă, RIP, **D212**, D710, contribuții PFA |
| **F6** | PFA | neplătitor | **normă de venit** | fără evidență de venituri, doar D212 pe normă |
| **F7** | SRL | plătitor | micro | **fără nicio operațiune** — singura care are voie să dea bază 0 |

**Două cabinete**, ca să se testeze și izolarea între cabinete:
Cabinetul A — F1, F2, F3, F7 · Cabinetul B — F4, F5, F6

**Fiecare firmă are un an fiscal complet (2026)**, cu cifrele așteptate calculate din
temeiurile verificate în sesiunea A, înghețate într-un fișier de așteptări **scris înainte
de a rula aplicația pe date**. Altfel copiezi output-ul și testezi că 1 = 1.

## Cele 11 etape

Pentru fiecare: **invariantul** și **capcana** (modul cunoscut de eșec, din cele întâlnite).

### 1. Migrare / preluare firmă
Sold inițial, plan de conturi, parteneri, stocuri, mijloace fixe, RIP (PFA), pre-fill ANAF v9.
**Invariant:** Σdebit = Σcredit pe soldul preluat; nr. rânduri importate = nr. din fișier −
duplicate raportate explicit.
**Capcană:** import „reușit" cu 0 rânduri; dedup care înghite tot; schema tenantului ≠ template.

### 2. Configurare firmă
`tip_firma`, regim TVA și perioadă fiscală, vector fiscal, an fiscal, utilizatori, roluri.
**Invariant:** fiecare regim produce exact setul de straturi și declarații așteptat.
**Capcană:** regim schimbat retroactiv care rescrie tăcut trecutul.
**Firme:** toate șapte produc vectori fiscali diferiți — etapa care le distinge.

### 3. Intrare documente primare
Facturi emise/primite, e-Factura, extras bancar, casă, Raport Z, NIR, documente fotografiate.
**Invariant:** fiecare document → exact o intrare în registru; total documente = total listă
= total raport.
**Capcană:** parser care întoarce 0 linii tratat ca „lună fără documente"; semn inversat;
document dublat la reimport.

### 4. Salarizare
Contracte, stat de plată, concedii medicale, part-time, fluturași, tichete.
**Invariant:** brut − reținute = net pe fiecare salariat; Σ stat = Σ rulaj 421/4315/4316/444/436.
**Capcană:** salariat exclus tăcut din stat; **sau coloană dispărută din schemă → salarii
ZERO** (dovedit 27.07; acoperit acum de `common.cere_coloane_cursor`).

### 5. Contabilizare
Motor, note automate, note manuale, patru-ochi, stornare.
**Invariant:** Σdebit = Σcredit per notă și per perioadă; nicio notă validată fără
document-sursă; storno = oglinda exactă.
**Capcană:** notă rămasă ciornă → nu intră în rulaj → **exact mecanismul bazei zero**.

### 6. Operațiuni de sfârșit de lună
Închidere TVA, amortizare, descărcare de gestiune, diferențe de curs, închidere de an.
**Invariant:** după închidere, 4426/4427 sold 0; stoc cantitativ ↔ valoric coerent.
**Capcană:** operațiune rulată de două ori; rulată pe lună închisă.

### 7. Verificări interne
Semafor, control încrucișat, alerte, monitor fiscal.
**Invariant:** pe firmă cu eroare **injectată deliberat**, verificatorul o GĂSEȘTE; pe firmă
curată, verde cu motiv explicit.
**Capcană:** gri raportat ca verde; verificator care compară o funcție cu ea însăși.

### 8. Declarații — generare
Toate declarațiile datorate, pe toate cele 7 firme, toate lunile.
**Invariant:** fiecare cifră din XML = cifra din fișierul de așteptări. **Bază 0 doar la F7.**
**Capcană:** query rupt → generator gol → XML valid. Ramură scrisă și niciodată executată
(D301 tip 5).

### 9. Declarații — depunere
DUKIntegrator, SPV, D710 rectificativă.
**Invariant:** declarația depusă se stochează cu hash; regenerarea produce același hash sau
se raportează diferența.
**Capcană:** DUK tratat ca dovadă de conținut. **Nu e.** Plus validare care nu rulează deloc
și raportează gri permanent (D406, 27.07 — `an`/`luna` nepasate).

### 10. Ieșiri externe
SAGA, WinMentor, D406, rapoarte, portal client, export GDPR.
**Invariant:** totalurile din export = totalurile din aplicație, calculate pe **a doua cale**.
**Capcană:** rută inaccesibilă (a mușcat la SAGA); encoding; denumire de fișier.

### 11. Transversal (la FIECARE etapă, nu la sfârșit)
Izolare tenanți, acces/roluri, integritate în timp, backup + **restaurare**.
**Invariant:** două firme cu date identice, citire încrucișată → 0 rânduri; apel
neautentificat → 401; obiect din alt tenant → 404.
**Capcană:** `search_path` nesetat; constrângere nescopată la `current_schema()`; job de
fundal pe tenantul greșit.

## Cele trei niveluri de test

| Nivel | Ce dovedește | Regula |
|---|---|---|
| **N1 — calcul pur** | formula fiscală | fără DB, fără fake; cifre din exemplul oficial |
| **N2 — integrare pe DB reală** | granița cod ↔ bază | Postgres real; **fake interzis pe `core.d*`** |
| **N3 — cap-coadă pe firmă de test** | că fluxul întreg produce adevărul | de la import până la XML validat |

Cele ~1049 de teste actuale sunt aproape toate N1. N2 a apărut pe 27.07
(`test_pull_declaratii.py`). **N3 nu există** — e ce construiește sesiunea B.

### Izolarea unui test de integrare

Depinde de **cine deține conexiunea** (stabilit 29.07):

- funcție **cititoare** care primește `conn` → trăiește în tranzacția fixturii → **ROLLBACK**
  curăță (tiparul din `test_pull_declaratii`);
- funcție **scriitoare** care își deschide propria conexiune și comite → ROLLBACK-ul
  fixturii n-are ce anula → **schemă efemeră comisă + DROP la teardown**, cu `DROP IF EXISTS`
  la setup pentru siguranță la crash.

**Nu se refactorizează cod de producție ca să servească un test.**

Și: **niciun test de integrare nu depinde de o firmă persistentă din bază.** Un test legat
de o firmă anume trece pentru că firma există, nu pentru că logica e corectă — și devine
roșu când cineva îi schimbă datele, fără să se fi modificat cod.

---

# Ordinea de execuție

## Sesiunea A
Testele fiscale, unul câte unul, până la epuizarea inventarului. Nu are nevoie de date.

## Sesiunea B

**Faza 0 — curățenie (blocantă).** Ștergerea completă a datelor actuale: firme, cabinete,
utilizatori. Tot ce e acum e de test, nimic real.

**Faza 1 — cele 7 firme.** Creare prin **interfață**, ca un contabil care intră prima dată,
nu prin script. Așa se testează etapele 1–2 și se prind problemele pe care le vede omul.
Fișierul de așteptări se scrie **înainte**, din temeiurile verificate în sesiunea A.

**Faza 2 — etapele 3→11**, în ordine, cu regula cascadei.

**Faza 3 — gardurile** care împiedică regresia. Vezi `GARZI.md`.

---

# Cum se consemnează

- **Rezultatul fiecărei etape** — în „Starea sesiunii B" (Faza 1) și „Inventarul de acoperit în A" de mai sus, cu data.
- **Defectele găsite** — în `DECIZII.md`, cu **cauza**, nu doar cu simptomul.
- **Ce nu se repară imediat** — `xfail(strict=True)` în `core/test_datorie.py`, NU notă
  într-un fișier. Un registru pe care trebuie să ți-l amintești nu funcționează.
- **Gardurile noi** — în `GARZI.md`, în aceeași zi.

---

# Reguli de lucru

1. **Verificare la sursă înainte de orice afirmație.** Valorile fiscale se verifică la
   ANAF/lege, nu din memorie. Trigger: „lipsește", „nu există", „e greșit".
2. **Proba pe date reale.** Nicio etapă nu e „gata" pentru că trece validatorul sau pentru
   că testele sunt verzi. Un test care rămâne verde când generatorul întoarce `[]` nu
   testează nimic.
3. **Ancorele se citesc din fișier, nu se scriu din memorie.**
4. **Nicio comandă de commit fără poartă** — pe suită ȘI pe proba funcțională.
5. **Nu se repară pe suspiciune.** Se măsoară întâi. Pe 27.07, „float pe bani e greșit" era
   adevărat ca principiu și fals ca diagnostic: 0 din 5000 de valori pierdeau precizie.
6. **Un test nu se scrie fără temei verificat.** Vezi sesiunea A.

## PREDARE §6 (01.08.2026) — Campania versionare formule pe la_data: CAMPANIE COMPLETA (pas 0-5)

OPRIRE §6 (limita de context, NU fragmentare-pentru-confirmare): pas 3-5 sunt DECISE in comanda aprobata,
nu se re-decid. Se continua fara sa se intrebe nimic. Predare la granita de commit (26fe9ca), tot ce e
comis e functional (suita 1195 verde, verificator 0).

GATA (5 commit-uri):
- PAS 0 (19faad6): cota_dividend + lichidare -> COTE["impozit_dividend"]. FLAG: 10% pre-2026 neverificat la
  sursa (posibil 8% 2023-2025), REDARE, de reconfirmat la MO.
- PAS 1 (3ee3ad7): TIPARUL. common.alege_varianta(variante, la_data) = cota() pe COD. deducere_personala ->
  _deducere_personala_2018 (varianta) + _VARIANTE_DEDUCERE (registru cu temei) + dispecer public.
  graf_temei EXTINS sa lege dispecerul de variantele din _VARIANTE_* (module-var -> functii).
- PAS 2a (ff8fd84): plafon_la (valoare) -> COTE["plafon_tva_incasare"].
- PAS 2b (35b4732): d101._scadenta + d710 d_recN (structura) -> variante datate.
- PAS 2c (26fe9ca): calcul_cm (fereastra diminuare) -> _calcul_cm_core(diminuare_activa) + 3 variante.

TIPARUL de aplicat (mecanic) la PAS 3 - functii STABILE (o singura versiune azi):
  Pentru fiecare functie F(args, la_data):
    1. redenumeste corpul: def F -> def _F_2018 (sau anul in vigoare al regulii).
    2. registru: _VARIANTE_F = [("<data_in>", _F_2018, c.Temei(<act>, ..., nivel_sursa="REDARE",
       de_cine="Code/Costin", verificat_la="2026-07-31"))].
    3. dispecer public F: docstring cu markerul TEMEI (daca F e in _TEMEI_FUNCTII), apoi
       fn,_ = c.alege_varianta(_VARIANTE_F, la_data or date.today()); return fn(args...).
    Import in modul daca lipseste: from core.common import alege_varianta as _av, Temei as _Tm (sau c.*);
    from datetime import date. Foloseste STRING pt data_in ("2018-01-01") - _ca_data o converteste.
  Roșu->verde->mutatie->commit, un MODUL per commit.

PAS 3 - lista (11 functii, cu modul; toate SINGLE BODY azi):
  salarizare.py: procent_cm, taxe_cm, calcul_cm_cod10, calcul_salariu  (calcul_salariu e mare: dispecer
     subtire care forwardeaza; NU duplica corpul - redenumeste in _calcul_salariu_2018).
  deconturi.py: plafon_diurna
  sponsorizari.py: plafon_credit, credit_sponsorizare
  motor.py: rezerva_legala
  contracte_speciale.py: calcul_zilier
  tva_marja.py: vanzare_marja  -> RAMIFICATIE: verifica intai daca doar CITESTE cota (base x cota) fara
     regula proprie; daca da, RECLASIFICA (nu e functie de regula), scoate-o din lista, spune, lista scade la 10.
  tva_marja_turism.py: marja_turism_special (prorata scutire non-UE = regula, ramane)
  ATENTIE (ramificatie Costin): daca vreo functie se dovedeste ca ARE puncte de schimbare (nu stabila),
  trateaz-o ca la pas 2 (variante datate reale, nu 1 versiune).

PAS 4 - GARD (ratchet -> PRAG 0 in aceeasi campanie): in verificator, pt fiecare functie din _TEMEI_FUNCTII
  (+ eventual lista extinsa a celor 11+), verifica AST ca are un dispecer pe la_data (corpul cheama
  alege_varianta pe un registru _VARIANTE_*). Baseline = cate NU au inca; coboara la 0 cand toate convertite;
  la 0, PRAG (orice regula fiscala noua fara dispecer BLOCHEAZA). Nota: procent_cm nu ia la_data direct (ia
  cod/zile) - decide daca intra in gard sau are exceptie declarata (apelat de calcul_cm care e versionat).

PAS 5 - CONSUMATORI (proba pe cifra, cerinta finala): verifica adeverinta:50, d112.py:443 (rectificativa),
  stat_plata_api.py:60/145, salarii_contare.py:55 - toate paseaza la_data pana la capat.
  PROBA CERUTA: genereaza o adeverinta pentru o luna din 2025 si arata ca foloseste regulile 2025 (nu 2026).
  Ramificatie Costin: daca vreun consumator NU paseaza la_data -> repara-l (e chiar bugul campaniei).

La final: Raport §2 etapa 5 pentru TOATA campania (pas 0-5).

---
CAMPANIE COMPLETA (01.08.2026) — pas 3-5 livrate:
- PAS 3 (7 commit-uri, un modul fiecare): cele 11 functii de regula ramase -> dispecer pe la_data.
  salarizare 783cca4 (procent_cm/taxe_cm/calcul_cm_cod10/calcul_salariu; procent_cm primeste la_data din
  _calcul_cm_core; calcul_salariu = dispecer subtire; graf_temei test actualizat variant-aware). deconturi
  4fa6ffd (plafon_diurna). sponsorizari 0f423e5 (plafon_credit + credit_sponsorizare, paseaza la_data intern).
  motor 3822edd (rezerva_legala). contracte_speciale 3c3611c (calcul_zilier). tva_marja 126e9b9 (vanzare_marja).
  tva_marja_turism 1606d61 (marja_turism_special). RAMIFICATIE rezolvata: vanzare_marja NU e simplu cititor de
  cota (aplica regula regimului marjei) -> RAMANE in lista (11, nu 10). Fiecare: rosu->verde->mutatie.
- PAS 4 (8c0ea86): GARD verificator - fiecare din cele 13 functii de regula (_VERSIONARE_FUNCTII) trebuie sa
  fie dispecer pe la_data (AST: corpul cheama alege_varianta(_VARIANTE_*, ...)). Ratchet la PRAG 0 in aceeasi
  campanie (toate 13 convertite). Mutatie: rezerva_legala single-body -> TOTAL 1 BLOCHEAZA.
- PAS 5 (ee8a717): consumatorii. adeverinta:50, d112:443, stat_plata_api:60/145, salarii_contare:55 paseaza
  DEJA la_data. Reparat salariati_api:334 (calcul_cm_cod10 nu pasa la_data). Proba schema efemera: adeverinta
  2026-06 (era 2025: sm 4050+facilitate 300) net 2574.75 vs 2026-08 (sm 4325+facilitate 0) net 2455.75.
- GOL PRE-EXISTENT descoperit (NU al campaniei; cota, nu formula): calcul_salariu pre-2026 RIDICA fiindca
  plafon_facilitate_salariu_minim (COTE) incepe 2026-01-01 - nicio valoare 2025. Adeverinta pentru o luna
  2025 crapa. DE DECIS (Costin): backfill plafon 2025 la sursa SAU ramane limita declarata (app n-are date
  reale pre-2026). NU s-a inventat o valoare.
  REZOLVAT (01.08.2026, blocaj motivat): NU backfill - LIMITA DECLARATA. cota() ridica PerioadaIndisponibila
  (tag PERIOADA_BLOCATA -> UI 423, nu 500) cu cele 4 elemente. Gard verificator GARD BLOCAJ MOTIVAT PRAG 0.
  Cote late-start care rup un calcul: plafon_facilitate_salariu_minim + tichet_masa_plafon (ambele 2026-01-01,
  calcul_salariu). Restul cotelor de regula: cas/cass/impozit/cam (2018), salariu_minim/facilitate (2025-01-01
  =podea) - nu rup in [2025, azi]. Nota (nu regula): tva_redusa (2025-08-01) rupe calcul_tva pt facturi
  pre-08.2025 (cititor subtire, acelasi mecanism central). Commit-uri 1d37d3a + 1de6ac9. Backfill 2025 = de decis Costin.


## Clustere — metoda (referință permanentă, 04.08.2026)

Capitol de METODĂ, nu jurnal. Se ACTUALIZEAZĂ când se adaugă/modifică un cluster, nu se rescrie. Regula sursei
unice: ce există deja în Inventarul A (nume, modul, √, funcții) și în GARZI.md (limita fiecărei bife) se REFERĂ
de aici, nu se copiază. Aici stă doar ce NU e deja scris: definiția operațională, criteriul de apartenență, și
clasificarea pe expunere la extindere.

### 1. Ce e un cluster (definiție operațională)

Un cluster = **un RÂND din tabelul „## Inventarul de acoperit în A"** din acest fișier. Identitatea lui e perechea
**(nume, modul)** — nu doar numele: același nume se repetă între module (ex. `taxare inversa` la d300 ȘI d394;
`rotunjire aritmetica` la d112/d300/d390), iar cheia pe nume le-ar colapsa (dovadă: `core/agenda.py::secventa_calculata`,
funcția `_id(r) = (cluster, modul)`). Un rând poartă: nume | modul | fișiere de test | „Verificat la sursă" (bifa √ +
data + eventualul `bump:`) | risc (FISCAL/STRUCTURA) | temeiuri | funcțiile de test care îl probează.

Un cluster e o **unitate de verificare la sursă**: o felie de comportament fiscal a unui modul, verificată contra
sursei oficiale (act normativ + validatorul DUK instalat), bifată cu data verificării, și păzită de funcții de test
nominalizate. Bifa √ nu spune „codul e testat" — spune „la data D, felia asta a fost confruntată cu sursa".

### 2. Criteriul de apartenență: IMPLICIT (judecată la momentul verificării), nu explicit

**Nu există regulă în cod care să ia o funcționalitate nouă și s-o clasifice într-un cluster.** `agenda.py` doar
PARSEAZĂ tabelul scris de mână (`stare_sesiune_a()` → `_randuri_tabel(text, "## Inventarul de acoperit în A")`).
Apartenența unei bucăți de cod la un cluster e o **decizie umană**, luată când se scrie rândul în Inventar A. Nu e
derivabilă mecanic dintr-un fișier/funcție/temei.

Ce ESTE derivat mecanic (dar NU e apartenență — e ordine și reset):
- **`graf_clustere()`** — muchiile de DEPENDENȚĂ între clustere EXISTENTE: prin analiză statică (test → funcții-sursă
  apelate → închidere pe `graf_temei`), un cluster A depinde de B dacă o funcție a lui A atinge o funcție DEȚINUTĂ de
  B. Servește doar sortarea topologică din `secventa_calculata()` (o dependență se verifică înaintea celui ce depinde
  de ea). LIMITA declarată în cod: vede doar prin `cota()`/apeluri; un literal ascuns rămâne invizibil. În practică
  DOAR familia `salarizare` are muchii; restul sunt rădăcini.
- **`cote_cluster()`** — ce chei din `COTE` (cote/plafoane) atinge un cluster, pentru RESETUL propagat: dacă o cotă de
  care depinde clusterul s-a schimbat în `common.py` după data √, bifa e stale (garda V3 din `test_agenda`).
- **`secventa_calculata()` / `urmator_cluster()`** — ordinea deterministă a clusterelor NEbifate și NEblocate
  (departajare: FISCAL înaintea STRUCTURA, apoi câte deblochează, apoi ordinea din inventar). Sursa listei =
  `secventa_persistata()` (scrisă în „## Secvența de verificare"); un cluster BLOCAT (`_e_blocat`, marcaj `BLOCAT:` în
  coloana bifă) iese din secvență până se deblochează.

Concluzie pentru sesiuni viitoare: **când apare o funcționalitate nouă, TU decizi cărui cluster aparține (sau că e
cluster nou) — nu există clasificator automat.** Regula practică folosită până acum: gruparea pe (felie de comportament
fiscal × modul de declarație), la nivelul la care sursa se verifică o dată (un act/o structură/un set din validator).

### 3. Inventarul clusterelor tratate

Sursa canonică a listei complete (nume | modul | √ data | funcții) e **tabelul „## Inventarul de acoperit în A"** de
mai sus; limita fiecărei bife (ce NU a acoperit) e în **GARZI.md**, la intrarea gardului corespunzător („Limita
declarată"). Nu se recopiază aici (sursă unică). Ce adaugă acest capitol e clasificarea pe TIP DE CRITERIU al bifei —
fiindcă tipul criteriului determină dacă bifa devine incompletă la extindere (secțiunea 4):

- **A. Pin pe SET (enum/nomenclator/cote):** bifa asertă `SET == {enumerare înghețată}` sau `valoare = lookup(perioadă)`.
  Extensibil: legea poate adăuga un membru/o fereastră. → secțiunea 4.
- **B. Golden pe FORMULĂ:** bifa fixează o formulă cu cifre calculate de mână (ex. `rezerva legala` 5%/plafon 20%;
  `TVA marja` cota/(100+cota); `checksum totalPlata_A` = sum(componente); lanțul P1-P53 D101). Stabilă: nu crește cu
  instanțe noi — se strică doar dacă se schimbă FORMULA (derivă legislativă generală, nu extindere de set).
- **C. Structură/prezență:** bifa verifică forma XML/XSD sau prezența unei chei (ex. `structura XSD d406`;
  `cere_coloane`; anti-drop pe allow-list). Se strică la schimbare de structură oficială.
- **D. Fereastră period-aware:** bifa fixează o valoare pe o fereastră de date (plafoane, cote istorice). Hibrid A/B:
  formulă stabilă, dar SETUL de ferestre crește cu fiecare ordin nou. → secțiunea 4.

### 4. CLUSTERE EXPUSE LA EXTINDERE (partea cea mai utilă)

Bifele de tip **A (pin pe set)** și **D (fereastră)** devin **incomplete în tăcere** când apare o instanță nouă: pin-ul
rămâne VERDE contra setului vechi (codul nu s-a schimbat, deci nici garda anti-stale nu se aprinde), dar setul din
lume a crescut. Enumerate explicit (fiecare cu limita în GARZI — se referă, nu se copiază):

| cluster | modul | setul care poate crește | intrare GARZI (limita) |
|---|---|---|---|
| tipuri operatiune (pct.215) | d394 | TIPURI op1 (A,L,C,V,AI,LS,AS,N) | „Gard tipuri operatiune D394 + datorie ASI" |
| tipuri operatiune IC | d390 | (L,T,A,P,S,R) OPANAF 705/2020 | „Gard-pin nomenclator tipuri operatiune D390" |
| cote acceptate | d394 | (0,5,9,11,19,20,21,24) validator v5 | „Garduri cote acceptate D394" |
| taxare inversa / codPR (art.331) | d394 | CATEGORII→CODPR (12 litere art.331) | „Gard anti-regresie taxare inversa", „Gard nomenclator codPR" |
| CODPR_N / categorie_331 | d394 | nomenclator lit.D (21-23/32-35) | „Gard rezumat1 campuri + datorie N" |
| tip_partener (pct.216) | d394 | 4 categorii + _TARI_UE | „Gard clasificare tip_partener D394" |
| nomenclator tari | d390 | prefixe TVA țări (HR...) | „Gard nomenclator tari Croatia HR" |
| nomenclator cod_oblig↔cod_bugetar | d100/d112/d710 | coduri obligații BS/BASFS | „Gard cod_oblig <-> cod_bugetar", „Fix cont bugetar D100" |
| UoM UN/ECE | d406 | UOM_UNECE (coduri Rec.20) | „Gard UoM UN/ECE D406" |
| MovementType | d406 | 19 coduri nomenclator stocuri | (Inventar A d406; GARZI d406) |
| SourceDocuments/TaxCode | d406 | coduri TaxCode livrări period-aware | „Gard TaxCode livrari period-aware D406" |
| randuri / checksum (allow-list) | d300 (+d390/d394) | rânduri manuale acceptate (R12/R29...) | „Gard checksum + excludere 14.1/14.2 D300", „Gard de CLASA allow-list manual" |
| limita text per-câmp | toate | LIMITE_TEXT_ANAF (C(n) per câmp) | „Gard de CLASA limita text per-camp" |
| cote period-aware (COTE) | common/toate | fiecare cotă + fereastra ei | GARZI cat.3 „derivă legislativă" (gaura structurală) |
| impozit dividend istoric | d205/decontari | 5%/8%/16% pe perioade | „Fix cote istorice impozit dividend" |
| plafoane (cultural/creșă/diurnă/CM/masă) | salarizare/deconturi | ferestre pe ordine MF/MMSS | „tichete culturale/cresa", „plafon diurna", CM plafon |

**Regula de citit tabelul:** oriunde codul are un `== (tuple)`, un `in SET`, un `dict[categorie]`, sau un `lookup(perioadă)`
peste un nomenclator/cotă ANAF, bifa e expusă. Un pin ținut la zi PRIN CONSTRUCȚIE nu ajunge — el prinde driftul
codului (cineva editează setul fără reverificare), NU creșterea lumii (ANAF adaugă un membru și nimeni nu atinge codul).

### 5. Confruntare cu FUNCTIONALITATI.csv

Stări în CSV (04.08): 172 LIVE · 3 PARTIAL · 3 PLANIFICAT · 6 AMANAT · 7 RESPINS · 10 ELIMINAT. Funcționalitățile
NEabordate încă (relevante întrebării „cad sub criteriul unui cluster închis?"):

- **PARTIAL: F035/F036/F037 (D406 SAF-T lunar/active/stocuri)** — CAD sub clustere d406 deja ÎNCHISE (SourceDocuments,
  UoM, MovementType, plan conturi, TaxCode, registration_number, structura XSD). PARTIAL fiindcă validarea DUK
  SEMANTICĂ e xfail (doar structura e verificată). Extinderea D406 (mai multe secțiuni SAF-T) va atinge aceste bife →
  fiecare secțiune nouă cere reverificarea pin-urilor d406 corespunzătoare.
- **PLANIFICAT: F123 (provider plată), F130 (Open Banking PSD2), F148 (arhivare cloud)** — sunt INTEGRĂRI/infrastructură,
  NU declarații fiscale. NU cad sub niciun cluster fiscal (modelul de clustere acoperă generarea de declarații). Nu
  amenință nicio bifă.

Concluzie #5: printre funcționalitățile CSV neabordate, NICIUNA nu răstoarnă o bifă fiscală închisă (D406 e deja
clusterizat; restul sunt integrări în afara modelului). **Riscul real de „bifă incompletă la implementare" NU vine din
CSV** — vine din instanțele LAW-DRIVEN ale seturilor de la secțiunea 4 (o cotă TVA nouă, un tip de operațiune nou, un
tichet nou, o categorie taxare-inversă nouă), care nu sunt „funcționalități" în CSV, ci apar când se schimbă legea.

### 6. Ce se întâmplă când o instanță nouă satisface criteriul unui cluster închis: BUMP

Procedura (dovedită de precedente): (1) se extinde pin-ul/garda ca să includă instanța nouă + PROBĂ la sursă (DUK sau
MO); (2) bifa √ se **bumpează** la data reverificării, cu `bump: <motiv>` OBLIGATORIU în coloana Verificat
(garda `test_agenda::test_bifa_bumpuita_are_motiv` respinge o bifă mutată înainte fără motiv — altfel bump-ul devine
ornament); (3) dacă funcția de test s-a schimbat substanțial, garda anti-stale `test_verificarile_A` cere ca √ să fie
≥ data commitului de schimbare (re-ancorare). Un cluster BLOCAT se REDESCHIDE (scoate marcajul `BLOCAT:`) când sursa
devine disponibilă.

**Tiparul bump-urilor** (cele 8 din Inventar A, `grep -in "bump:" TESTE.md`) — trei cauze distincte:
- **(R1) o dependență s-a schimbat sub bifă** — o cotă (`salariu_minim` 3700→4050, HG 1506/2024, FIX5) sau o funcție-sursă
  partajată (FIX3: net-ul asertat mutat în alt test). 5 bife: `facilitate salariu minim`, `suprataxare part-time`,
  `proratare angajare/incetare` (salarizare), `suprataxare prag` (d112) — toate reset-ate de corecția `salariu_minim`;
  exact ce urmărește `cote_cluster()`/graful.
- **(R2) blocaj ridicat / acoperire extinsă** — PARTIAL→închis, sub-cluster adăugat: `concedii medicale` (PARTIAL 31.07 →
  02.08), `tichete masa/vacanta` (sub-clustere D2/D3 adăugate).
- **(R3) o instanță dintr-un SET extensibil, re-verificată la sursă** — `tipuri operatiune (pct.215)|d394` (03.08→04.08:
  ASI scos din cod la greenlight Costin, pin mutat pe validatorul J8, datorie→gard invers) și `tichete culturale`
  (02.08→04.08: fereastra oct2025-mar2026 confirmată la MO 240/470). ← EXACT cazul secțiunii 4.

Tipar: bump-urile se grupează pe (R1) schimbări de dependență partajată (mai ales `salariu_minim`, propagat mecanic) și
(R3) reverificarea unui set extensibil (declanșată de o DECIZIE umană, nu de un detector). ASI a stat pin-VERDE deși era
greșit în pdf; discrepanța a fost prinsă de un gard-datorie (probă DUK izolată), dar rezolvarea a cerut greenlight Costin.

### 7. Ce mecanism LIPSEȘTE pentru detectare automată

**Nu există niciun mecanism care să detecteze automat că un SET EXTERN (nomenclator/cotă ANAF) a crescut un membru pe
care pin-ul nu-l are.** Ambele garde existente operează pe starea CODULUI, nu a LUMII:
- pin-ul (`SET == {...}`) prinde editarea setului în cod fără reverificare, NU adăugarea unui membru în lume (setul stă
  neatins → pin verde);
- garda anti-stale `test_agenda` prinde schimbarea CODULUI funcției de test după data √, NU schimbarea legii sub un cod
  care stă (e UNIDIRECȚIONALĂ — vezi GARZI cat.3 „derivă legislativă", gaura structurală deschisă 31.07).

E aceeași gaură ca la derivă legislativă: **nu există feed legislativ/nomenclator RO citibil mecanic** (dovedit repetat:
WebFetch eșuează pe PDF-uri ANAF, MO se citește manual). Un detector automat ar cere, per set expus (secțiunea 4): o
sursă externă a nomenclatorului oficial curent + o comparație periodică `SET_cod ⊆ SET_oficial` care semnalează membrii
noi. Fără el, se DEGRADEAZĂ la **revizuire manuală periodică ghidată de registru**: pin-urile marchează UNDE să te uiți
(cele 16 din secțiunea 4), data √ marchează CÂND s-a verificat ultima dată, iar `bump:` lasă urma reverificării.
Substitutul parțial care există deja: `data_out` pe cote (refuză o valoare expirată — dar semnalează doar la CALCUL,
nu la depunere, și nu vede schimbarea din interiorul ferestrei).

**A doua gaură, în garda anti-stale însăși (nu doar în lume):** garda `test_agenda::test_verificarile_A` prinde
schimbarea CODULUI unei funcții citate, DAR are un punct orb — un test ȘTERS, încă citat în coloana `functie` a unui
cluster cu MAI MULTE fișiere, scapă. `_fisier_functie` caută funcția în fișierele clusterului la HEAD; dacă nu o
găsește în niciunul (test șters), cade pe `fișier[0]`, iar `_functie_schimbata` compară `<ABSENT>` (la commitul √) cu
`<ABSENT>` (la HEAD) în acel fișier unde funcția n-a existat niciodată → egal → NEstale. Dovadă empirică (04.08): bifa
`taxare inversa|d394` a citat `test_datorie_gaze_naturale_taxare_inversa_art331_lit_l` mult după ce testul fusese scos [citare-istorica: scos la inchiderea datoriei gaze 6675f19]
(datoria gaze închisă în 6675f19), iar suita a rămas VERDE — garda n-a semnalat. REPARAT (04.08, aceeasi zi): `_functie_schimbata` a fost refacut sa caute functia in TOATE
fisierele clusterului la ambele commituri (nu doar fisier[0]) — stergere = schimbat, mutare neschimbata = NU stale
(fara fals-pozitiv), absent la ambele = citare moarta semnalata. Rulat pe tot inventarul (70 clustere), fixul a mai
scos 5 bife ascunse de acelasi punct orb: `plafon diurna` (datoria period-awareness istorica REZOLVATA in 6675f19,
nereflectata in bifa -> bump) + 4 citari gresite / coloane `fisiere` incomplete (testele cross-generator de rotunjire
traiesc in `test_limita_text_anaf.py` nelistat; IMCA nume trunchiat; reclasificare citata gresit). Toate reparate;
regresia e gardata de `test_functie_schimbata_cauta_toate_fisierele_punct_orb_04_08`. Integritatea coloanei `fisiere` (un test citat sa traiasca intr-un fisier listat) e gardata acum separat de `test_fisiere_coloana_completa` (+ mutatie), care prinde golul la CREAREA clusterului - acolo unde `test_verificarile_A` e oarba (lucreaza doar pe clustere bifate). Driftul DUS-INTORS (capete egale, mijloc diferit) NU e gardat per-commit (ar reciti istoricul) - e o rulare PERIODICA: `python3 -m core.agenda_drift`, declansata de o bifa >3 luni sau o repornire de campanie (vezi GARZI cat.9).


---

## Metode de verificare — clasele oarbe (referință permanentă, 05.08.2026)

Capitol de METODĂ (frate cu „Clustere — metoda"). Întrebare (Costin, 05.08): din TOATE limitele scrise (clustere +
GARZI cat.0-11 + xfail-uri, nu doar campania de conținut), ce CLASE de eroare nu le atinge nicio metodă, ce metodă
concretă le-ar prinde, cost/valoare/tautologie, și dacă „același fapt calculat diferit în două documente" e clasă
proprie. Sursa unică: limitele per-clasă trăiesc în GARZI cat.0-11; aici stă doar maparea metodă→clasă și golurile.

### 0. Cele 4 metode existente și AXA fiecăreia

| # | metodă | compară ce cu ce | axă | ratează STRUCTURAL |
|---|--------|------------------|-----|--------------------|
| 1 | Cod vs lege (cluster A→B) | constantă/regulă/formulă din cod ↔ text act oficial | logică statică, un modul | dacă calea e atinsă; date runtime; consistență între documente; citirea greșită a legii în A |
| 2 | Validator DUK | XML emis ↔ structura + aritmetica intra-câmp ANAF | structura unui document | valoare validă-dar-greșită care trece checkurile; consistență între documente; vs realitate |
| 3 | Reconciliere cale2 | valoarea generată ↔ recalcul independent din date PRIMARE, intra-document | valoare, un document | intrare partajată greșită (§8); ce nu recalculează; layerul de EMISIE (descoperit azi) |
| 4 | Garduri de registru | bifă/documentație ↔ starea reală (git HEAD, drift dus-întors) | meta-documentație | orice despre corectitudinea calculului |

Toate patru operează pe UN document/modul și DOWNSTREAM de intrarea primară. Niciuna n-are: (a) axă între documente,
(b) axă în timp, (c) confruntare cu un adevăr EXTERN firmei.

### 1. CLASELE fără nicio metodă (clase, nu instanțe)

- **C1. Integritatea INTRĂRII** (GARZI cat.1, LIPSĂ). Data primară e greșită înainte de orice calcul: câmp→NULL→0,
  import dublat, „1.234,56"→0 (virgulă), cotă inexistentă la dată. Toate 4 metodele sunt downstream; reconciliere
  citește ACEEAȘI intrare (tautologie §8). Nimeni nu confruntă intrarea cu un adevăr extern (document-sursă, extras).
- **C2. Consistența ÎNTRE DOCUMENTE** (clasă nouă, Q4). Același fapt, două documente ale firmei, căi de calcul
  diferite → divergență. Reconciliere e INTRA-document. Descoperit azi accidental (baza salarială CM: fluturaș
  1047.62 vs D112 emis 2000). Detaliu §4.
- **C3. Integritatea în TIMP** (GARZI cat.7, LIPSĂ). Valoarea era corectă la depunere dar DERIVĂ: editare retroactivă
  în lună închisă, declarație depusă regenerată cu alt rezultat, balanță ≠ Σînregistrări, backdating. Nicio metodă
  n-are axă temporală — toate sunt point-in-time.
- **C4. Eroarea de INTERPRETARE a sursei** (meta pe metoda 1). Citirea legii în pasul A e ea însăși greșită; metoda 1
  o CIMENTEAZĂ într-un golden (cazul real D101 R17 scadență — act ratat de prima cercetare, √ pe interpretare
  greșită). O prinde DOAR DUK (întruchipează interpretarea ANAF) sau o a doua citire independentă — unde există.
- **C5. Mascarea erorii / zero tăcut** (GARZI cat.0, rădăcină transversală). `except: return 0` / câmp gol produce 0
  care trece downstream (0 = „absență legitimă"). Mutant-zero ar prinde generatoarele, dar e LIPSĂ și nu acoperă
  căile non-generator (readere, API, contare).

(În afara scopului fiscal, tot fără metodă între cele 4: izolare tenant cat.5, acces/IDOR cat.6 — domeniu security,
garduri LIPSĂ proprii.)

### 2. Metodă concretă per clasă + tautologie

- **C1 → (a) invarianți DB pe intrare:** NOT NULL pe fiecare coloană de bani + cheie naturală unică (anti-dublare
  import) + parser care RIDICĂ pe „virgulă→0" (nu tace). **(b) reconciliere intrare↔document-sursă:** Σ(linii
  importate) == totalul de pe documentul fizic (extras bancar deja parsat, factură PDF). Tautologie: NU — (a) sunt
  axiome, nu recalcul; (b) sursa NU e intrarea (adevăr extern). Cost: (a) MIC; (b) MARE (parsing surse).
- **C2 → reconciliere ÎNTRE documente** (vezi §4). Tautologie: PARȚIALĂ — scapă doar pe perechi cu căi INDEPENDENTE.
- **C3 → snapshot+hash la depunere apoi REGENERARE și diff** (prezent ↔ sinele trecut al aceleiași căi) + job nocturn
  Σdebit=Σcredit per perioadă/tenant + orfani. Tautologie: NU — axa e timpul, nu calea. Cost: MEDIU (snapshot+hash =
  deja DECIS pt state_plata, GARZI INVENTAR A).
- **C4 → confruntare cu DUK unde are regulă + a doua citire OARBĂ a sursei** (al doilea cititor nu vede interpretarea
  din A). Tautologie: reconciliere NU ajută (aceeași interpretare); DUK/a-doua-lectură scapă. Cost: DUK = marginal
  MIC (rulat pe fixturi); a doua lectură umană = scump, unde DUK n-are regulă (xfail temeiuri_toate_redare).
- **C5 → mutant zero sistematic** (fiecare generator forțat →[] ⇒ suita roșie) + **gard AST anti-`except: return 0/pass`**
  pe căile de bani. Tautologie: NU — probă de sensibilitate, nu recalcul. Cost: MIC-MEDIU.

### 3. Cost × valoare (sinteză)

| clasă | metodă | prinde | cost construcție | tautologie §8 |
|-------|--------|--------|------------------|---------------|
| C5 | mutant-zero + gard anti-except | cauza rădăcină (maschează restul) | MIC-MEDIU | nu |
| C2 | reconciliere între documente | bani reali divergenți la ANAF | MEDIU | parțială (evitabilă pe perechi bune) |
| C3 | snapshot+hash + job balanță | derivă temporală, „regenerat altfel" | MEDIU (parțial decis) | nu |
| C1a | invarianți DB | intrare coruptă (NULL/dublu/virgulă) | MIC | nu |
| C1b | reconciliere intrare↔sursă | intrare ≠ document fizic | MARE | nu |
| C4 | DUK + a doua lectură | interpretare greșită cimentată | MIC (DUK) / MARE (uman) | nu |

### 4. Q4 — „același fapt, două documente" ca CLASĂ PROPRIE (C2) + unde apare (verificat în cod)

DA, clasă proprie, distinctă de reconciliere (care e generator-vs-recalcul INTRA-un-document). Mecanism: două
documente ale firmei declară/afișează ACELAȘI fapt, calculat pe căi de cod SEPARATE, fără punte de confruntare.
Descoperirea de azi (baza salarială CM: fluturaș proratat 4190→1047.62 vs D112 emis brut întreg 8000→2000) e prima
instanță, ieșită ACCIDENTAL fiindcă reconciliere cale2 a pus alături pull (fluturaș) și emisia.

Perechile (verificat în cod care există și care NU-s controlate):

| pereche | fapt partajat | control existent (verificat în cod) | verdict |
|---------|---------------|-------------------------------------|---------|
| fluturaș (stat_plata) ↔ D112 | CAS/CASS/impozit per salariat | test_cm_arbori_paraleli DOAR tratament indemnizație cod-08; baza salarială NEcontrolată | **NECONTROLAT** (azi: divergență activă) |
| D100 ↔ D112 | total CAS/CASS/impozit/CAM lunar | `calcul_d100(prof,an,luna,obligatii)` primește `obligatii` ca INPUT; nu importă d112, nu recalculează | **NECONTROLAT** (sursă comună=tautologie SAU manual=nesincronizat) |
| D205 ↔ D112 | impozit reținut per persoană (anual↔lunar) | niciun cross-check găsit | **NECONTROLAT** |
| balanță ↔ D101 | profit contabil (clase 6/7) | d101_reconciliere RECALCULEAZĂ profitul din 6/7 (=balanță) | **CONTROLAT parțial** (profit computat; ajustările §8 nu) |
| SAF-T D406 ↔ balanță | Σ înregistrări GL ↔ solduri balanță | d406_reconciliere e intra-doc; niciun tie GL↔balanță găsit | **NECONTROLAT** |
| D300 ↔ jurnale/balanță TVA | TVA colectată/deductibilă | verificatoare.py `decont TVA` = coerență internă parțială | **PARȚIAL** |
| D300 ↔ D394 | livrări/achiziții pe partener | control încrucișat menționat (GARZI F163) dar nu ca gard | **NECONTROLAT ca gard** |

**CORECȚIE 05.08 tura 6 (onestitate — analiza C2 inițială a ratat `core/control_incrucisat.py`):** acest modul
ESTE deja o metodă C2, pe principiul „reconciliază emisul" (citește totalurile DECLARATE din XML-ul GENERAT, nu o
reagregare). Compară declarația vs EVIDENȚA CONTABILĂ (a treia sursă, cale independentă):
- **D112 ↔ contabilitate** (`compara_d112`): CAS cod 412+458 ↔ rulaj 4315; CASS 432+459 ↔ 4316; CAM 480 ↔ 436;
  impozit 602 ↔ 444. Limită AUTO-declarată: brut (421) NEVERIFICAT pe luni cu CM. → pereche `D112 ↔ contabilitate`
  = **CONTROLAT PARȚIAL** (semafor runtime F162, TREI stări verde/roșu/GRI; NU test blocant; `test_control_incrucisat`
  NU exercită CM → de aici bug-ul A a scăpat suitei).
- **D300 ↔ contabilitate** (`compara_tva`): D300 R17_2 ↔ 4427, R27_2 ↔ 4426. → rândul D300↔jurnale de mai sus =
  PARȚIAL prin control_incrucisat (nu doar verificatoare.py).
COROBORARE A: `salarii_contare.py` bookează contribuțiile pe `brut_lucrat` (proratat, l.56) și recalculează CM
independent → ÎNAINTE de fix-ul A, D112 (brut întreg) diverga de 4315/4316/436, deci `compara_d112` ar fi dat ROȘU
pe lunile cu CM; DUPĂ fix, D112 se aliniază cu evidența. Fix-ul A e confirmat de o sursă independentă (contabilitatea
firmei), nu doar de citirea legii. Corecție pe pereche: `fluturaș ↔ D112` DIRECT rămâne necontrolat, dar contabilitatea
e un al treilea punct comun — dacă și fluturașul și D112 se leagă de 4315, se leagă și între ele (design mai robust).

Metoda C2: modul care ia ACELAȘI fapt din două generatoare și compară valoarea EMISĂ (nu intermediarul), pe cheia
comună. Ex.: `Σ(D112.B4_8 lunar pe an) == D205.impozit per persoană`; `D100.CAS_dat == Σ(D112.B4_8)`;
`stat_plata.cas == D112.B4_8 pe salariat`.
- **Tautologie parțială, decisivă pentru unde merită:** dacă ambele documente derivă din ACEEAȘI funcție de calcul
  (ex. D100 primește exact totalul D112 ca input), e tautologie PURĂ — coincid mereu, nu prind nimic. Metoda are
  valoare DOAR pe perechi cu CĂI DE CALCUL INDEPENDENTE (fluturaș↔D112, balanță↔D101), care e exact unde trăiesc
  bug-urile. Deci: aplic-o pe perechi cu căi independente; pe perechile pass-through (D100↔D112) întâi trebuie făcute
  independente, altfel gardul e ornament.
- **Precondiție critică:** compară valorile EMISE ale ambelor documente (nu intermediarele) — exact lecția de azi
  (poarta cale2 valida pre-emisia și rata emisia). Fără asta, metoda repetă orbirea de azi.

### 5. Ordinea propusă (efect × cost)

1. **C5 (mutant-zero + gard anti-except)** — cost MIC, efect MARE transversal, zero tautologie. Demască clasa care
   ascunde toate celelalte (un 0 tăcut face orice altă verificare să pară verde). Primul.
2. **C2 (reconciliere între documente, pe perechile cu căi INDEPENDENTE)** — întâi fluturaș↔D112 (are deja divergență
   activă dovedită azi), apoi Σ D112↔D205; balanță↔D101 e deja parțial acoperit. Cost MEDIU, bani reali la ANAF,
   tautologie evitabilă prin alegerea perechilor. Precondiție: valorile EMISE (Decizia 2 de azi = pilonul ei).
3. **C3 (snapshot+hash + job balanță nocturn)** — cost MEDIU (parțial DECIS pt state_plata), prinde „depus apoi
   regenerat altfel" și deriva retroactivă.
4. **C1a (invarianți DB pe intrare)** — cost MIC dar necesită migrare pe toți tenanții (risc), iar o parte din efect
   e prinsă reactiv de C2/reconciliere; de aceea al patrulea, nu primul.
5. **C1b (reconciliere intrare↔document-sursă)** — cost MARE (parsing surse), doar unde sursa e digitală; ultima.
6. **C4 (a doua lectură / extindere DUK)** — nu e proiect separat: se face continuu, per cluster nou.

Argument de ordine: întâi ce DEMASCĂ restul (C5), apoi ce prinde bani reali cu tautologie evitabilă (C2), apoi TIMPUL
(C3), apoi INTRAREA (C1) — o intrare greșită e prinsă parțial reactiv aval, dar o eroare mascată (C5) ascunde TOT.

### 6. C4 (interpretarea sursei) - cum se aplica, CONTINUU per cluster (nu campanie separata)

C4 din clasele oarbe: citirea legii in pasul A poate fi ea insasi gresita, iar metoda 1 (cod-vs-lege) o CIMENTEAZA
intr-un golden (cazul trait: D101 R17 scadenta - un act ratat de prima cercetare, √ pe interpretare gresita).
NU e o campanie cu un modul propriu - e o REGULA DE PROCEDURA aplicata la FIECARE cluster/verificare la sursa:

- **A doua lectura sau validatorul.** O bifa √ pe interpretare (nivel_sursa REDARE/INTERPRETARE_OFICIALA, nu MO
  verbatim) NU se declara definitiva pana cand interpretarea e confruntata cu o A DOUA cale independenta de citire:
  (a) validatorul DUK, unde intruchipeaza regula ANAF (asa s-a rezolvat D101 R17 - DUK a transat contra primei lecturi);
  (b) o a doua lectura oarba a actului (al doilea cititor nu vede interpretarea din A); (c) un exemplu numeric oficial.
- **Marcajul nivel_sursa e semnalul.** Fiecare Temei poarta nivel_sursa (MO / REDARE / INTERPRETARE_OFICIALA /
  PRACTICA). Clusterele pe REDARE/INTERPRETARE (nu MO verbatim) sunt candidatii C4 - lista lor traieste in
  test_datorie (xfail temeiuri_toate_redare: 12 COTE + 6 functii pe REDARE fara MO verbatim) + in bifele √ cu
  nivel_sursa != MO. Aia e coada de C4: fiecare, cand se atinge, primeste a doua cale de lectura la sursa.
- **Ce NU e C4:** o formula deja pazita de golden + DUK (a doua cale exista) e acoperita; C4 vizeaza DOAR feliile
  unde interpretarea sta pe o singura citire umana, necontrolata.

Operational: la orice reverificare de cluster, daca bifa e pe REDARE/INTERPRETARE si nu exista DUK/golden numeric care
sa intruchipeze regula independent, se ADAUGA a doua cale (DUK sau a doua lectura) INAINTE de a declara √ definitiv.
Non-tautologie: a doua cale trebuie sa fie o SURSA DIFERITA de prima lectura (DUK/MO verbatim/al doilea om), nu aceeasi.

Notă de legătură: descoperirea (Finding 2 CM) e prima instanță C2; Decizia 2 (poarta cale2 pe valori EMISE) e
precondiția tehnică a clasei C2 — LIVRATA pt D112 (05.08 tura 6, GARZI): poarta reconciliaza acum ce PLEACA la ANAF, nu
pre-emisia. Restul 5 declaratii = res==emis (poarta lor vede deja emisul). Ramane de construit reconcilierea CM (1c-CM)
si perechile cross-document (C2 propriu-zis).

**CORECȚIE 05.08 tura 7 (proba mecanică — B era supra-afirmat):** afirmația „Decizia 2 LIVRATA pt D112, restul res==emis
(poarta lor vede deja emisul)" e MECANIC FALSĂ. Mutație pe `totalPlata_A` în artefactul emis (după build_xml) pt d100/
d101/d205/d300/d394/d406 → genereaza TRECE la toate 6: **toate porțile reconciliază `res` ÎNAINTE de build_xml și NU
re-validează artefactul**. B a mutat DOAR poarta d112 după calculul de emisie (prinde bug-uri de calcul-emisie, ex.
divergența CM); celelalte 5 rămân pre-emisie. Promisiunea „un total greșit nu ajunge la ANAF" nu e enforced mecanic
împotriva bug-urilor de layer-emisie pt niciuna (2b = res≠emis prin construcție). Fix complet C2: reconciliază valoarea
PARSATĂ din XML (assert res==parse(emis)), nemfăcut.



### 7. Campania C - STARE FINALA pe cele 5 clase oarbe (05.08.2026, inchidere)

Fiecare unitate cu cod: modul + gard AST/proba + MUTATIE. Unde a doua cale NU exista (tautologie/schema o impune),
se scrie ca LIMITA, nu gard fals.

- **C5 (mascare / zero tacut)** - LIVRAT:
  - gard AST anti-except-masca (test_gard_masca_zero.py): niciun `except: pass/return-zero-gol` in modulele de bani;
    mutatie sintetica dovedeste ca prinde; None/False excluse (parsere/validatori).
  - mutant-zero (test_mutant_zero.py): un generator care INGHITE datele (gol cand ele exista) e prins de markerul de
    continut - d112 (<asigurat + mutatie pull-gol), d205 (ridica pe zero beneficiari). LIMITA: extinderea la
    d100/d101/d300/d394/d406 cu acelasi tipar ramasa (un generator nou isi adauga markerul).

- **C2 (intre documente)** - LIVRAT partial, TAUTOLOGII numite:
  - fluturas<->D112: a doua cale = ARTEFACT contabil (D112-XML emis vs ledger rulaje), control_incrucisat.compara_d112
    extins+gardat+mutatie (test_control_incrucisat.py). Direct fluturas-vs-D112 = TAUTOLOGIE (ambele=calcul_salariu).
  - balanta<->D101: DEJA COMPLET (d101_reconciliere, recalcul independent din balanta clase 7/6 + mutatie-probat).
  - D100<->D112: PASS-THROUGH pur (calcul_d100 formateaza obligatii dat) = tautologie, sarita numita.
  - Sum(D112)<->D205: D205 formatter, aceeasi sursa salariala = tautologie pe valori; doar agregarea anuala ar fi
    independenta (fixtura cross-an) - numita, nefacuta.

- **C3 (integritate in timp)** - LIVRAT partial:
  - snapshot+hash regenerare-diff (amprenta_declaratie.py + test): amprenta deterministica; editare retroactiva ->
    amprenta difera -> hard-block. A doua cale reala (prezent vs sinele trecut).
  - orfani (echilibru_perioada.orfani): referinta rupta inregistrare_id -> prins.
  - Sigma debit = Sigma credit per perioada: TAUTOLOGIC pe schema curenta - inregistrari_linii are cont_debit SI
    cont_credit NOT NULL -> fiecare linie e echilibrata prin constructie, Sigma-le mereu egale. Functia exista ca
    monitor (defense-in-depth daca schema relaxeaza NOT NULL) dar NU poate pica azi = LIMITA scrisa.
  - LIMITA: jobul nocturn (echilibru_perioada_db per tenant) + persistarea amprentei la depunere (tabel) = wiring
    produs ramas (state_plata snapshot deja DECIS).

- **C4 (interpretarea sursei)** - SCRIS (sectiunea 6), nu executat: procedura per cluster (a doua lectura/DUK inainte
  de √ definitiv pe REDARE/INTERPRETARE). Coada reverificata: 19 chei COTE toate REDARE; upgrade-ul FUNCTIILOR a
  inceput (d101 scadenta MO). xfail temeiuri_toate_redare actualizat sa reflecte coada reala.

- **C1 (integritatea intrarii)** - LIMITA (nu gard fals, nu migrare riscanta la buget epuizat):
  - Goluri REALE gasite: (a) facturi NU are cheie unica pe cheia naturala (numar+directie+tert) -> import dublat
    posibil (doar salariati are UNIQUE(cnp)); (b) coloanele de bani sunt `numeric DEFAULT 0`, nu NOT NULL (exceptie
    inregistrari_linii.suma NOT NULL - ledgerul e protejat).
  - DE CE nu s-a facut acum: migrarea enforce (ADD UNIQUE / SET NOT NULL) pe date EXISTENTE multi-tenant e RISCANTA -
    pica pe duplicate/NULL-uri curente; cere intai un pas de DEDUP/BACKFILL scopat. A o forta la buget epuizat ar
    lasa tree murdar sau ar strica date. Follow-up scopat (dedup facturi -> UNIQUE; audit NULL -> SET NOT NULL).
  - intrare<->document-sursa: reconcilierea BANCARA exista (reconciliere.py: extras<->facturi); Σ(linii)==total
    document nescris explicit ca gard - felie separata unde sursa e digitala.

## 06.08.2026 (tura 5) — RECONCILIERE registre (campania de reparatie)

- Firul "urmator" cu 4 follow-up-uri (rescriere mesaje / fix B1-B17 / markeri .oblig / eroare-langa-camp)
  era STALE: toate facute in sesiunile G1-G10 anterioare.
- Campanie tura 5: LIVRAT D1a (skip vizibil import salariati), A6 (D394 L->LS + proba DUK, DATORIE 31.07
  INCHISA), B3 (owner cabinet deblocat la depunere). STALE (nu erau vii): A1 (D406 rezolvat 27.07),
  D1b (NOT NULL retras - base-null e semantic), D1c (idempotenta deja exista pe 9 module).
- FLAGGED cer decizie Costin: A5 (amortizare degresiva/accelerata - modelare fiscala + fara golden),
  D3 (state_plata - build-new, niciun eveniment de emitere). xfail-uri raman deschise (21->20: A6 inchis).
- DEFERATE (garzi preventive pt defecte inexistente): D2, D5, D7.
- PLAN_B.md rescris (contabil = test user, F1-F8 matrice legala, E1-E12).
- PRODUS separat in GARZI ("PRODUS - de abordat la final"): marja, regim dual, D207, praguri,
  rezerva legala, coada DUK, D406-Payments, 50%-deductibil (d406.py:122), IMCA-DB, GDPR ROPA, tot §F.

## 06.08.2026 (tura 6) — METODOLOGIE: verifica anaf_surse/ INAINTE de a declara "blocat pe sursa"
Premisa "sursa nu e disponibila" trebuie VERIFICATA in anaf_surse/ inainte de a fi scrisa intr-un xfail.
Doua xfail-uri purtau note despre absenta unei surse care era, partial sau total, prezenta local:
- #10 (art.77(4) 45%): nota zicea "sursele oficiale blocheaza accesul" - FALS, cod_fiscal_227_2015_consolidat.html
  e in anaf_surse/ si confirma 45% verbatim -> INCHIS.
- #16 (OUG 158 art.17 pre-141): nota zicea "nu-s in anaf_surse/" - PARTIAL fals; oug_158_2005_consolidat.html
  EXISTA, doar forma PRE-141 lipseste verbatim (fisierul are doar forma consolidata curenta) -> ramane blocat,
  nota corectata.
Regula: inainte de a marca "blocat pe sursa" -> grep in anaf_surse/, apoi declara EXACT ce lipseste.

## 06.08.2026 (tura 6) — CONVENTIE: date istorice (acte normative) vs vechime de datorie in reason-uri xfail

Garda `test_datoria_nu_imbatraneste_nelimitat` (core/test_datorie.py) citeste ORICE `dd.mm.yyyy` dintr-un
reason de xfail si pica pe >90 zile. Problema: orice act normativ citat CORECT are o data -> "01.08.2025"
(data Legii 141) era citita ca vechime a datoriei si pica garda. Va reaparea la fiecare temei legal cu data.

CONVENTIE:
- **Vechimea datoriei** ramane `DATORIE dd.mm.yyyy` (cu puncte). Garda o citeste - ASTA e scopul ei.
- **Datele istorice din temeiuri legale** (data de intrare in vigoare / publicare a unui act) se scriu cu
  **LUNA IN LITERE**: "25 iulie 2025", "1 august 2025", "1 ianuarie 2023". Regexul garzii
  `\d{2}\.\d{2}\.\d{4}` NU prinde forma cu litere -> nu o confunda cu o vechime de datorie.
- **Numarul actului** ramane `nr/an` (Legea 141/2025, OUG 158/2005) - nu contine `dd.mm.yyyy`, deja sigur.

AUTO-ENFORCING: daca cineva scrie o data de act ca `dd.mm.yyyy` si e istorica (>90 zile), garda PICA si-l
forteaza sa aplice conventia. Mesajul garzii trimite explicit la aceasta sectiune. Nu s-a schimbat
comportamentul garzii (citeste tot dd.mm.yyyy) - doar mesajul indruma.

DOMENIU (verificat 06.08): ambiguitatea mecanica e DOAR aici - singura garda de vechime care citeste
`dd.mm.yyyy` din text liber e `test_datorie.py:94`. `test_datorie.py:81` doar verifica ca EXISTA o data
(nu vechime). Nicio alta garda nu citeste mecanic date de vechime din GARZI.md/DECIZII.md/markeri. DECIZII.md
contine date de acte cu puncte (01.08.2025 x14 etc.) dar NICIO garda nu le age-check-uie -> fara confuzie
acolo (spelling-ul e incurajat pt consistenta, nu obligatoriu).

## 07.08.2026 — CM model de episod: gard nou
core/test_cm_episod.py: procent pe zile_episod (nu pe certificat), diminuare+portie-angajator o data/episod,
episod 20 zile=2850, plumbing art.XI, gard-sursa ca salveaza_concediu paseaza zile_episod. xfail #16 (forma
pre-141) ramane deschis - sursa verbatim inca lipseste.

## 07.08.2026 — #16 inchis + teste art.XI
core/test_cm_episod.py: test_art_xi_granita_pre_post_141 (31 iulie=75% uniform / 1 august=55-65-75) +
test_coduri_speciale_neatinse_de_l141 (alin.2 100% identic in ambele regimuri). xfail #16 -> INCHIS.

## 07.08.2026 — B1 partial: plafon 2025 adaugat, tichet 2025 ramas
common.py plafon_facilitate_salariu_minim @2025=4300 (OUG 156/2024 art.LXVI, MO+verbatim). calcul_salariu(2025)
inca ridica pe tichet_masa_plafon @2025 - urmatorul rand, cere sursa. B1 reincadrat din "un rand" in "clasa".

## 07.08.2026 — B1 tichet 2025: gard nou + meta-teste mutate
core/test_tichet_2025.py: valorile (40,04/40,18/45), golul octombrie motivat (nu 40,18 tacit), corectia 45 de la
noiembrie. Cele 3 meta-teste perioada_indisponibila mutate de pe "2025 blocat" (acum reparat) pe sub-podea (2024,
stabil) + golul octombrie 2025.


## 08.08.2026 — DEFECT-2 CNP (cifra de control pe calea directa): gard nou
core/test_cnp_control.py (8 teste): CNP cu cifra de control gresita refuzat pe TOATE caile de intrare (create +
edit salariat prin valideaza_salariat->valideaza_cnp; import; asociati; cnp_ingrijit) + anti-cale-noua (orice
modul care INSERT-eaza CNP fara a referi valideaza_cnp pica) + anti-regresie valideaza_salariat la format-only.
Mutatie: git checkout pre-fix -> 5 rosii cu motivul corect. No-op: sha256 D112 tenant_001 identic (45e3b486).
Fisierul e in git HEAD (commit 2ad7af4) inainte de aceasta bifa.

## 08.08.2026 — DEFECT-3 (stat-plata 500 + catch care minte): gard nou
core/test_catch_vizibil.py (4 teste): (A) RATCHET catch-gol-langa-api pe frontend, baseline 54 — o cale noua pica;
repararea din restul hartii coboara baseline. (B) anti-regresie pe cele 4 ecrane reparate (flag de eroare + textul
vizibil "Nu am putut incarca"). (C) backend perioada.py califica tabela cu schema (fara `FROM perioada_confirmata`
necalificat). (D) cele 5 rute payroll/documente au marcajul search_path_tenant_v1 (get_conn(schema)). Mutatie:
git checkout pre-fix -> toate 4 rosii; restore -> verzi. Proba comportamentala (headless, interceptare 500 -> UI
arata eroare vizibila, NU stare goala) = evidenta manuala; in suita ramane gardul de sursa (B). Fisierul e in git
HEAD (commit b660534) inainte de aceasta bifa.


## Gard headless e-Transport randuri dinamice (cap.24 batch 3a) — 08.08.2026

`core/test_etransport_randuri_dinamice.py` re-ruleaza IN POARTA (chromium headless, modulul real montat +
backendul real `core.etransport` interceptat) cele 5 scenarii DOM de la 3a + proba no-op sha256:
rand adaugat / rand sters din mijloc (valori pastrate + reindexare) / doua randuri cu erori simultan (fiecare
langa campul ei) / re-validare dupa corectarea unuia singur / rand incomplet in mijloc care NU mai dispare +
lista nefiltrata cu XML identic corpului canonical complet. Reproductibil de pe repo curat FARA pasi manuali:
fixture-ul auto-instaleaza pachetul playwright si browserul chromium daca lipsesc; daca tot nu poate rula ->
`pytest.fail` (niciodata skip verde-fals). Infra (driver/browser >100MB) ramane gitignored, se provizioneaza automat.
MUTATIE probata: reintroducerea filtrului in construiesteCorp -> 3 teste ROSII (doua erori / re-validare /
rand incomplet mijloc); revenit la original -> verde. Vezi GARZI 08.08 + commit batch 3a.
Nota anti-stale: bifa √ in inventarul sesiunii A vine intr-un commit SEPARAT (test_agenda cere fisierul in HEAD).

## 09.08.2026 — D112 v1.03-072026 (zile prestatii) — 2 garduri
- test_d112_zile_prestatii_072026_emise_si_verbatim: asiguratD (07/2026, CM cod 01) poarta D_14a=za, D_15a=zf,
  D_16a=D_14a+D_15a; reguli D_14<=D_14a, D_15<=D_15a, D_16a<=NZL. Mutatie: gate (an,luna)>=(2026,7) -> False =>
  D_14a=None -> rosu.
- test_d112_zile_prestatii_absente_inainte_072026: luna 06/2026 NU emite D_14a/D_15a/D_16a (structura veche).
  Mutatie: emisie neconditionata -> rosu.
Fixtura noua _sal_cm (certificat CM inline: cod, zile_ang/fnuass, brut_ang/fnuass, serie/numar/date). PROBA J27:
XML 07/2026 -> DUK VALID (fara fix -> 3 erori "D_1xa: atributul trebuie sa existe").

## 09.08.2026 (tura 3) — Regula publicare four-way: comportamentala, neguardabila mecanic
Regula "patru pasi dupa poarta verde" (CLAUDE.md §2.3 pct.10) e comportamentala (executorul restarteaza), ca regula
de push INAINTE de cablarea post-commit. NU se adauga gard nou: restartul are stop point uman (comportament vizibil)
-> nu se poate cabla orb intr-un hook (ar reporni prod peste utilizatori activi). Confirmarea ramane four-way in
raport (§2.2 sect.11), verificata la executie prin versiune.stare() + start-time systemd. Gardul existent
core/test_running_head.py (detectorul running==HEAD) ramane neatins si suficient pentru semnalul de divergenta.

## 09.08.2026 (tura 4) — Garduri OUG 91/2025 (diminuare CM) verbatim — 3 garduri (test_cm_episod.py)
- test_diminuare_o_zi_lucratoare_exemplul_ordin_506: reproduce exemplul VERBATIM din Ordin 506 art.78^4(4)
  (5 zile lucr, media 200,82, 55%% -> 442 lei); pineaza NZLCM-1 = o zi LUCRATOARE.
- test_diminuare_fereastra_certificat_01022026_31122027: frontierele ferestrei OUG 91 art.II(1) (31.01.2026 nu,
  01.02.2026 da, 31.12.2027 da, 01.01.2028 nu).
- test_diminuare_exceptii_verbatim_art2_lit_c_d1_e: 08(c)/15(e)/17(d^1) NEdiminuate; 09(lit d)/01 diminuate.
Gardeaza NUMAI aspectele CLARE verbatim (nu 02/51 - sub intrebare). Ancorate la actele din corpus (oug_91_2025.html,
lege_64_2026.html, ordin_506_1030_2026_norme_oug158.html). test_cm_episod.py + test_salarizare.py: 46 passed.

## 09.08.2026 (tura 5) — Garduri CM decizii Costin (izolare/faza/cod02/gating) — 4 garduri (test_cm_episod.py)
- test_izolare_51_se_diminueaza: cod 51 in fereastra -> diminuare=1.
- test_exceptii_de_la_01062026_nu_de_la_01022026: 08 + spitalizare eliberate 03.2026 -> diminuate; 07.2026 -> exceptate.
- test_cod_02_03_04_raman_nediminuate: 02/03/04 diminuare=0 (ambele faze). [citare-istorica: redenumit test_cod_02_03_04_se_diminueaza in tura 8]
- test_gating_pe_data_eliberarii_nu_pe_data_inceput: inceput in fereastra dar eliberat < 01.02.2026 -> nediminuat.
Cluster CM+D112: 100 passed.

## 09.08.2026 (tura 6) — Corpus pasul 3: garduri existente acopera noile MO
Cele 4 temeiuri COTE ridicate la MO intra sub G1 (test_corpus_surse.test_temei_mo_are_sursa_locala): MO => fisier
local existent. Mutatie probata azi: sters og_16_2022_consolidat.html -> G1 ROSU; restaurat -> verde. G2/G3
neschimbate (noile fisiere = forma_la_data, exceptate de G2). INDEX.json regenerat coerent cu COTE.

## 09.08.2026 (tura 7) — 5 temeiuri COTE ridicate la MO (garduri existente)
Cele 5 valori (facilitate 300, tva_redusa_5, tva 19%, dividend 5%, mijloc fix 2.500) intra sub G1
(test_corpus_surse): MO => fisier local. Mutatie probata: sters cf_2015_forma_initiala.html -> G1 ROSU; restaurat
-> verde. G3 (set volatil-fara-MO) actualizat la [] (toate legate). Valorile confirmate NEschimbate (sanity rulat).

## 09.08.2026 (tura 8) — Cod 02/03/04 se diminueaza (garduri actualizate)
- core/test_cm_episod.py: test_cod_02_03_04_se_diminueaza (diminuare=1, ambele faze; fost gardul 'raman
  nediminuate'). Mutatie: re-exceptarea 02/03/04 -> rosu.
- Setul de exceptii de la diminuare (suita de salarizare CM de la radacina, nc28): 02/03/04 mutate din exceptat
  in diminuat.
Cluster CM+pull: 56 passed.

## 09.08.2026 (tura 9) — D_9a: 3 garduri
- core/test_migrare_program_national_cm.py: fiecare tenant are concedii_medicale.program_national.
- core/test_cm_episod.py::test_program_national_exceptat_de_la_diminuare: program_national -> diminuare=0 (fazat 01.06.2026).
- core/test_d112.py::test_d112_d9a_program_national_emis: asiguratD emite D_9a="1" cand marcaj (07/2026); absent altfel.

## 09.08.2026 (tura 12) — Gard proba de login prin endpoint (gaura de metoda)
- core/test_login_proba_metoda.py::test_proba_login_e_prin_endpoint_nu_prin_hash: cont cu hash VALID + activ=false
  -> verifica_parola=True dar auth_api.login()=ok:False; activ=true -> login() ok:True + token. Cont efemer
  @invalid, cleanup. Mutatie: login() fara verificarea activ -> assert (2) pica.

## 09.08.2026 (tura 13) — Gard izolare pe cheie API
- core/test_izolare_api_key.py::test_control_pozitiv_cheia_A_isi_vede_tenantul: cheia firmei A pe tenantul A -> 200 + factura A (APIKA-100).
- core/test_izolare_api_key.py::test_cheia_A_nu_atinge_tenantul_B: pe TOATE (ruta,metoda) /api/v1/firme/{tenant_id}, cheia A pe tenantul B -> niciodata 2xx, niciodata sentinela B. Mutatie: o ruta /api/v1 fara _api_schema -> pica.
- core/test_izolare_api_key.py::test_fara_cheie_401: fara X-Api-Key -> 401.

## 09.08.2026 (tura 14) — Gard cablaj verifica_tva (bug cross-check D300)
- core/test_control_incrucisat_wiring.py::test_verifica_tva_prinde_factura_necontabilizata_end_to_end:
  factura emisa TVA 210 fara nota validata -> verifica_tva ROSU (constatare "TVA colectata"). Mutatie:
  d300.genereaza(conn, schema, an, luna) [semnatura veche] -> gri -> pica.

## 09.08.2026 (tura 16) — Garduri "forma": balanta valida + cu_intarziere
- core/test_solduri_api.py: +4 teste (balanta_valida strain/gol/real + importa refuza strain inainte de DB).
- core/test_control_fiscal.py::test_clasifica_depusa_dupa_termen_iese_din_la_zi: depusa dupa termen -> cu_intarziere.
- test_matrice_control_fiscal + test_control_fiscal: re-ancorate la _clasifica cu 4 cosuri (depunere on-time = termen).

## 09.08.2026 (tura 17) — Mesaje solduri cu diacritice
- core/test_solduri_api.py::test_mesajele_balanta_valida_au_diacritice: cele 3 motive balanta_valida au diacritice RO.

## 09.08.2026 (tura 19) — Gard izolare /raportari (aparare de date)
- core/test_izolare_raportari.py::test_fir_alt_cabinet_da_404_nu_403: sesiune A pe fir B -> 404 (nu 403). Mutatie: firul_complet nefiltrat -> 403.
- core/test_izolare_raportari.py::test_citit_alt_cabinet_da_404: /citit pe fir B -> 404. Mutatie: fara check proprietar -> 200.
- core/test_izolare_raportari.py::test_autorul_isi_vede_firul: control pozitiv, autorul vede firul (200).

## 10.08.2026 (tura 20) — Proba browser antet wizard (in afara portii verzi)
- frontend_test/proba_wizard_antet.py: calea 'Migrare cabinet' - back revine la meniu + antet fara acumulare.
  Mutatie: cod vechi exit 1, cod nou exit 0. Rulare manuala (nu in pre-commit; pytest nu colecteaza frontend_test/).
- frontend_test/observa_*.py: unelte de observatie per-wizard (back-destinatie/acumulare), fara verdict.

## 10.08.2026 (tura 22) — Gard ZERO-BASE D100/D300
- core/test_zero_base_declaratii.py::test_zero_base_d100_d300: D100/D300 pe zero cu facturi -> avertisment; [citare-istorica: redenumit tura 23 -> test_d100_pe_zero_refuza + test_d300_pe_zero_cu_facturi_avertizeaza/nil_legal]
  nil legal (fara facturi) -> fara avertisment. Mutatie: cod vechi avertismente=[] -> pica.

## 10.08.2026 (tura 23) — Gard D100 refuz pe zero (DUK-dovedit invalid)
- core/test_zero_base_declaratii.py::test_d100_pe_zero_refuza: D100 fara obligatie -> ValueError. Mutatie: cod vechi nu ridica.
- ::test_d300_pe_zero_cu_facturi_avertizeaza / ::test_d300_nil_legal_fara_avertisment: D300 avertisment vs nil legal.

## 10.08.2026 (tura 24) — Garzi declaratii refacute la spec oficial (DUK)
- core/test_d394_codpr_cereale.py: op11 nu emite centralizatorul '21' (spec poz.68-70); subcod NC recunoscut. 3 teste.
- core/test_d301_data_doc.py: data_doc normalizat la ZZ.LL.AAAA (spec poz.35) din ISO/date/canonic. 3 teste.
- core/test_d406_supplierid.py: SupplierID PF fara CUI -> tip 04, nu "0" (SAF-T SD.P.22/23). 1 test (fixture efemera).
- core/test_pull_declaratii.py::test_d112_cm_suma_lipsa_din_stocare_recalc_din_media: indemnizatie CM completata din
  media x procent x zile (OUG158 art.17) cand lipseste din stocare.

## 10.08.2026 (tura 25) — Garzi din auditul field-by-field al tuturor declaratiilor (DUK)
- core/test_d100_scadenta_trimiv.py: scadenta pe cod (micro 121 trim IV 25.06.an+1; profit 103 sfarsit-an 25.12.an). 3 teste.
- core/test_d101_nr_evid_poz12.py: nr_evid poz.1-2 = "11" (OPANAF 206/2025). 3 teste.
- core/test_d205_cifr_obligatoriu.py: cifR/den1 obligatorii goale -> refuz. 3 teste.
- core/test_d300_drop_taxabil.py: linii taxabile la cota fara rand DUK-valid -> avertisment cuantificat. 4 teste.
- core/test_d390_rotunjire_coerenta.py: coerenta rotunjire baza per-op vs rezumat (R16). 3 teste.
- core/test_d394_v_taxare_inversa_cota0.py: V (taxare inversa) emisa la cota 0 (R217.2).
- core/test_d394_pull_ti_fara_linii.py: pull() pe taxare-inversa fara linii nu crapa (NameError latent).
- core/test_d406_payment_method.py: PaymentMethod = cod ANAF 01/02/03 (nu "VIR"/"NUM"). 3 teste.
- core/test_d112_carantina_c2.py: carantina cod 07 emite C2_213/C2_215 (angajator).

## 10.08.2026 (tura 26) — Garzi din repararea deciziilor §6 (Costin)
- core/test_d112_asiguratd_zerobase.py: asiguratD obligatorii goale -> refuz. + 4 fixtures reparate in test_pull_declaratii.py.
- core/test_d205_divid_platit.py: divid_D (distribuit) vs divid_P (platit) din cont 457.
- core/test_d205_rezid_derivat.py: Rezid derivat din CNP; nerezident dividende refuzat (R32).
- core/test_d300_taxare_inversa_beneficiar.py: achizitie taxare inversa -> R12/R25 net-zero, anti-dubla-numarare.
- core/test_d300_zero_rate.py: achizitie 0% -> R26_1; livrare 0% -> avertisment per-linie.
- core/test_d301_pers_inreg.py: pers_inreg 1/2 din inreg_art317 (nu hardcodat).
- core/test_d394_manual_codpr.py: op11/codPR pt operatiuni manuale C/V.
- core/test_d394_prsafiliat.py: prsAfiliat din are_operatiuni_afiliate.
- core/test_d406_taxcode_nota.py: GL/Payment TaxCode 380304 (nu "300").
- core/test_d406_master_pf.py: PF tip-04 prezent in master Customers/Suppliers.

## 10.08.2026 (tura 29) — Garzi TURA 3 (mesajul exact pre-DUK): validator identitate partajat + per declaratie
- core/test_identitate.py: valideaza_cui/valideaza_cnp/valideaza_cif ancorat pe valori DUK (valid+invalid).
- D100: test_d100_cui_checksum, test_d100_trunchiere.
- D101: test_d101_cui_checksum, test_d101_cod_obligatie_caen, test_d101_valori_pre_duk.
- D112: test_d112_cnp_angajat, test_d112_nume_dataang, test_d112_caen_codboala, test_d112_cert_overflow.
- D205: test_d205_cnp_checksum, test_d205_cui_checksum, test_d205_cnp_duplicat.
- D300: test_d300_valideaza_wired, test_d300_profil_identitate.
- D301: test_d301_valideaza_wired, test_d301_cif_checksum, test_d301_an_guard, test_d301_nr_doc_c20, test_d301_coercitie_tacita.
- D390: test_d390_diagnostic_partener.
- D394: test_d394_partener_cui_litere, test_d394_cuip_checksum, test_d394_op1_fara_op11.
- D406: test_d406_cui_checksum, test_d406_cnp_tert, test_d406_coercitie_t3, test_d406_accounttype_wired.
- D710: test_d710_t9_parsare, test_d710_t1_cui, test_d710_nomenclator_manual, test_d710_cod131_132, test_d710_sume_negative.

## 10.08.2026 (tura 30) — Garzi TURA 4 (reconciliere sursa-vs-declaratie + meta-gard)
- core/test_reconciliere_vie.py: meta-gard "nicio reconciliere nu moare tacit" (9/9, AST).
- core/test_d100_reconciliere.py: D100 baza din cont 70x vs suma_dat (aggregation-loss).
- core/test_d301_reconciliere.py: D301 baza din d301_operatiuni (RON curs 1) vs res.
- core/test_d390_reconciliere.py: D390 baza+nrOPI din facturi IC vs res (Layer-1 gen-gate).
- core/test_d205_imp_manual.py: D205 imp1 manual = rate×baza (d1).
- core/test_d300_r25_r12.py: D300 R25=R12 (V19/V20 neimpus de DUK).
- core/test_d710_suma_ded.py: D710 suma_ded (121 aplicat / 103 blocat).
- core/test_control_reconciliere_vizibila.py: reconciliere vizibila in Control fiscal (acelasi mecanism, anti-mort).


## 10.08.2026 — Lot 0 (adevarul registrului)
Gard nou: core/test_registru_functionalitati.py::test_sursa_cod_refera_fisiere_care_exista
- ce face imposibil: o intrare LIVE/PARTIAL care citeaza in coloana Sursa cod un fisier inexistent la calea EXACTA (modul mutat/redenumit/eliminat fara update de registru). Registrul e harta de cod a AI-ului F152; checkul vechi (numar campuri/ID) nu prinde asta - campurile pot fi aliniate si calea moarta.
- non-LIVE excluse (ELIMINAT/RESPINS/AMANAT/PLANIFICAT au codul legitim absent).
- proba ROSIE (registru nereparat): F117 admin_sanatate.js / F121 etransport_ecran.js / F152 raportari_api.py / F188 firme.js -> FAILED (4 intrari LIVE cu nume scurt/cale moarta); VERDE dupa normalizare la cale completa. "Un gard care nu pica pe codul vechi nu e gard" - probat.

Suita dupa Lot 0: 1886 passed / 3 skipped / 16 xfailed. Verificator DS TOTAL 0.
Verificat MANUAL (nu gard mecanic, notat): ELIMINAT (10) rute 404 pe app viu (127.0.0.1:8010) + cod absent; RESPINS/AMANAT/PLANIFICAT fara cod-fantoma; PARTIAL D406 registru exact (nedepunabil).

## 10.08.2026 — Lot 1 (transversal & infra) verificat
Fundatii PROBATE (erau fara proba): F008 (/auth/login live 200+401), F001 (apel real Claude 'OK'), F116 (partial: rate-limit/TLS/fail2ban OK, headere absente=gol).
Cronuri: crontab + timers systemd toate instalate/ruleaza (F083/F110/F111/F112/F060/F177/F178/F179/F170/F201/F202).
Migrari cablate (rute+importa): F007/F053/F059/F079/F084/F085/F150; proba functionala adanca = test-debt.
PWA F113: manifest+sw servite 200. Registru reparat: F150+F122 Sursa cod -> cod real. Gard test_sursa_cod verde (3/3).
Suita: 1886 passed/3 skipped/16 xfailed, verificator 0.
LIMITA gard: Sursa cod PROZA (fara path-token) nu e prinsa de test_sursa_cod (F150/F122/F124 treceau) - de intarit daca reapare.

## 11.08.2026 — Lot 2+3 verificate + gard CONCURENTA
Gard nou (al 4-lea de registru): test_sursa_cod_nu_e_referinta_de_concurenta - LIVE/PARTIAL nu poate avea Sursa cod care incepe cu "CONCURENTA". ROSU pe 10 (F126/F138-142/F144-147), verde dupa normalizare la cod real.
Lot 2: wizard Playwright TRECUT (exit 0); F004 ANAF live; F043 cod+ruta + suita e-Factura import verde (6 teste, fisier root-level); 21 cablate. F043 Testat gol->pytest.
Lot 3: 55 pytest tintit + suita; F118/F054/F144/F145 verificate; restul cu pytest verzi in suita.
Suita: 1886 passed/3 skipped/16 xfailed, verificator 0. Garduri registru: 4/4.

## 11.08.2026 — Lot 4-8 verificate (campania completa 9/9)
Lot 4: 55 pytest; drift F151 Sursa cod proza -> core/articole_import_api.py. Lot 5: 56 pytest (salarizare/pontaj/adeverinta). Lot 6: DUK pe 4163 - toate declaratiile generabile VALID; refuzurile = garduri pre-DUK corecte (zero/gol/corupt). Lot 7: F081 scadente probata (scadente.py + zile_lucratoare/scadentar); F051 cablat. Lot 8: FARA-PROBA toate cablate (rute confirmate).
Zero drift registru in Lot 5-8 (fixurile registry-wide din Lot 0-3 au curatat). Garduri registru: 4/4 verzi.
Suita: 1887 passed/3 skipped/16 xfailed, verificator 0.

## 11.08.2026 — Gard comportamental import migrare (certificare-comportament, cluster 1)
core/test_import_migrare_valideaza.py::test_parser_respinge_coloane_nerecunoscute (parametrizat pe 5 module):
un CSV cu structura valida dar coloane straine -> parserul (extrage/extrage_balanta) ridica ValueError, NU intoarce [] tacit (ZERO-BASE). ROSU pe cod vechi (5 failed), VERDE dupa fix. + non-regresie (fisier bun asociati acceptat).
Reparate: asociati/istoric_declaratii/mijloace_fixe/salariati/solduri_api - clasa "accepta orice fisier si declara succes".

## 11.08.2026 — Certificare pozitiva (populare + write-flows)
Certificat POZITIV pe ALFA populata (comportament exercitat, nu cod citit): produse/clienti/centre-cost/registratura/casa/stocuri/retete (creare 200 + citire nenula ZERO-BASE); emitere factura (TVA 21% corect), PDF (%PDF- valid), chitanta (serie CH 2 buc), contare extras (import 2 linii, nota 5121=4111). Formular emitere DS-curat in browser. README bug #6 (verifica_tva) confirmat reparat comportamental pe DELTA.
Gard import test_import_migrare_valideaza verde. Suita 1893 passed / verificator 0.

## 11.08.2026 — F116 headere securitate verificate (nginx enforcing)
Proba comportamentala: curl extern (5 headere), login prin formular sub CSP enforcing reusit (onsubmit OK, Enter nu navigheaza), walk 38 ecrane 0 violari, nginx 0 5xx. Unealta parcurgere CSP: cert_ds_browser/cert_ds_firma prin https://iconta.eu. Registru F116 corectat (NEDEPLOYATE->DEPLOYATE). Config sub versionare config_server/iconta-nginx.conf.

## 11.08.2026 — Certificare sub-ecrane adanci + bonuri portal
Crawl adanc pe 39 ecrane (fiecare sub-element deschis individual in browser prin nginx): render+DS+consola+CSP. ~130 pytest/DUK trecute prin aceeasi parcurgere. Covarsitor curat. Findings: clasa DS-input (.pr-input/.asi-per-sel vs .camp-input, browser>verificator static) + clasa console-400 (butoane cu precon­ditii, app se recupereaza) - raportate, nereparate (intentionate/benigne). Bonuri portal F017 certificat end-to-end (client->AI Claude vision->draft->confirm->cabinet). Fara schimbari de cod.

## 11.08.2026 — Gard INPUT_NECONFORM (verificator) + refactor DS-input
verificator_conformitate.py: regula INPUT_NECONFORM - input/select normal fara .camp-input pica (candidate). PROBAT rosu pe cod vechi = 27 (stash refactor JS/CSS), 0 dupa refactor. 28 inputuri refactorate la .camp-input (pr-input/asi-per-sel/asi-cauta/em-moneda-select/em-curs-input/dlg-input/fd-email-input/firme-q). Layout verificat vizual (screenshot Produse/Asistenti/emitere - nerupte). node --check ESM 0.

## 11.08.2026 — Decizia 2: butoane console-400 dezactivate cu motiv (verificat comportamental)
4 butoane firme.js disabled+title cand preconditia lipseste (Casa data/suma, REGES chei, SEPA IBAN, portal client) + backend /stat-plata reges_configurat. Verificat pe app viu: disabled+motiv cand lipseste, ENABLED cand precondtia e indeplinita (Casa dupa fill, portal ALFA cu client). 0 erori consola. Elimina clasa console-400 gasita la certificarea sub-ecranelor.

## 11.08.2026 — Gap INPUT_NECONFORM inchis: prinde si createElement (Costin)
Costin: extinde gardul sa prinda inputurile construite prin document.createElement, nu doar tag-urile literale.
verificator_conformitate.py (INPUT_NECONFORM) extins: detecteaza createElement("input"|"select") fara .camp-input in fereastra (linia curenta + 4 urmatoare, unde se seteaza className/classList/setAttribute).
PROBAT pe caz CONSTRUIT: _test_ce_rau.js (createElement fara camp-input) -> INPUT_NECONFORM=1 (PICA, tag "createElement"); _test_ce_bun.js (createElement cu className camp-input in fereastra) -> nu pica (control pozitiv). Sterse dupa, verificator 0. Zero createElement inputs in cod curent (gapul era teoretic; acum mecanizat pentru viitor). Limita ramasa: createElement(tag) cu tag dinamic (variabila) nu se prinde static.

## 11.08.2026 — Ajutor contextual: infrastructura + pipeline probat
core/ajutor.py + GET /ajutor/{fid} + api.js semnAjutor + .ajutor-btn (whitelist verificator). Endpoint: F031 -> 1587c ajutor, F001/F999 (fara ajutor) -> 404. Modal end-to-end pe Casa: 7 sectiuni, 0 erori consola, DS. Coloana `ajutor` (11 coloane), gard registru se adapteaza (4 passed). verificator 0.

## 11.08.2026 — Ajutor contextual: acoperire finala + garduri
Plasari finale (batch 6/7): F136 Adeverinta, F061 Registru jurnal, F077 RIP, F205 Cerere stergere, F016 Previziune bani, F118 Blocheaza luna. BILANT: 44 functionalitati cu "?" (20 statice + 24 dinamice), 47 ajutoare scrise.
Garduri active pe subsistem: GET /ajutor/{fid} declarat in PUBLICE (core/test_rute_autentificate.py) — altfel poarta pica pe ruta neautentificata nedeclarata; .ajutor-btn in CLASE_BUTON_OK (verificator, altfel BUTOANE il flag-uieste); coloana `ajutor` in test_registru_functionalitati (11 coloane, passed). Endpoint probat: F-cu-ajutor -> 200, F-fara-ajutor -> 404. ESM node --check pe toate ecranele atinse (declaratii/operatiuni/firme/setari/emitere/facturi/rip/portal). verificator TOTAL 0.

## 11.08.2026 — Ajutor de ansamblu: probe
Backend (TestClient, pe copie): login flag=False cand NULL / =True dupa marcare; GET /ansamblu 200 (7 grupe,
138 functii, 45 cu ajutor); POST /cont/bun-venit-vazut 200; fara auth 401/401.
Browser (playwright, 127.0.0.1:8010, cabinet 4163 test): prima logare -> .bun-venit-overlay (antet
"iConta.eu · bun venit", 9 pasi fir de intrare cu migrarea prima, 7 grupe, 45 "?" contextuale, buton "intru",
inchidere mentioneaza bara+ecrane), 0 erori consola; "intru" -> overlay dispare + flag DB setat; re-logare
(flag True) -> welcome NU reapare; ".nav-ghid" din bara -> modal "Prezentarea aplicatiei" (9 pasi, 7 grupe,
45 "?"); "?" contextual din ansamblu -> "Ajutor · Avansuri furnizori/clienti" cu 7 sectiuni (.aj-sec).
Garduri: rute autentificate (cere_context) -> test_rute_autentificate + test_registru passed (9); verificator 0
(.nav-ghid = buton bara-chrome, exceptat prin prefix "nav-"; BRAND_EU corectat "iConta.eu"; IMPORT_VERSIUNE
corectat migrare.js?v=6).

## 11.08.2026 — Restart neconditionat: gard + probe
Gard nou (poarta verde): core/test_publicare_restart_neconditionat.py - 3 aserturi: hook-ul de publicare exista;
restarteaza iconta-nou; NU inspecteaza tipul continutului (interzis: --name-only/--stat/git diff/git show/
diff-tree/diff-index/HEAD~/HEAD^/glob *.ext/regex ancorat .ext$). PROBAT pe mutatie reala: varianta conditionata
(git diff --name-only HEAD~ | grep pe extensie -> restart) PICA (1 failed, restul 2 passed); cea neconditionata
VERDE (3 passed). Proba comportamentala: commit de DOCS -> post-commit auto-restarteaza -> RUNNING==HEAD
(hash-uri in raport §3, /admin/versiune divergent=false).

## 11.08.2026 — tenant_013 apt DUK D406: proba pe date reale
Seed scripts/seed_alfa_d406.py (idempotent, hard-tintit tenant_013). Reconcilieri verificate: 2131 debit GL = valoare
MF activ = 10800 (INCHIS); stoc nenegativ pe toate articolele; 0 CUI invalid ramas. PROBA DUK: D406 periodic 2026-08 pe
date ALFA (6 InvoiceLine reale, Payments=0) -> DUKIntegrator_AnLunaUI -v D406 = **'valid' (0 erori)** CU fix-ul de
nomenclator (throwaway); FARA fix -> 4 erori format RegistrationNumber/CustomerID (Customer 1/2). F036: 2 <Asset>;
F037: 3 <PhysicalStockEntry>. DUK e LENIENT (nu verifica corespondenta cu contabilitatea) -> reconcilierea cu GL
verificata separat (mai sus), nu prin DUK.

## 11.08.2026 — Gard D406 identitate partener + reprobare DUK (fix real)
Gard nou: core/test_d406_partener_id_neconform.py - cade daca reapare Partener(id=str(r["id"])) pe identitatea
partenerului SAF-T. PROBAT: ROSU pe cod nereparat (test_fara_id_brut FAILED), VERDE dupa fix (2 passed). Reprobare DUK
FARA patch temporar: tenant_013 D406 2026-08 -> DUKIntegrator 'valid' (0 erori); id-uri brute suspecte: NICIUNUL.
Non-regresie: 30 teste d406 existente + smoke (strict-xfail) = passed. Stop-point: 014/016 (nomenclator gol) neschimbati.

## 11.08.2026 — Registru F035/F036/F037 la starea reala
FUNCTIONALITATI.csv: F035/F036/F037 Stare 27.07->11.08 + descrieri aduse la realitate; integritate 201 randuri x 11
coloane (test_registru_functionalitati 4 passed). DECIZII: PIVOT peste "27.07 NU e depunabil". Drift-check pe registru
(indicatori NEDEPUNABIL/pana la reparare/de reparat/sintetic/mock/stub): doar F035/F036/F037 aveau drift real.

## 11.08.2026 — Modal landing la zi (+3 LIVE), sync gardat
genereaza_grupe_functii.py: F083/F113/F199 mutate din EXCLUDE in EXPLICIT (Cabinet si portal client); login.js
regenerat (--scrie). Modal 138->141 (Cabinet si portal client 26->29; restul grupelor neschimbate). Gard
GRUPE_FUNC_STALE (verificator) VERDE (login.js in sync cu repartizeaza). ESM login.js OK. Doar functii LIVE adaugate.

## 12.08.2026 — 3 ghiduri noi + multi-slug
ghid/: diurna-interna-neimpozabila, diurna-externa-neimpozabila, impozit-dividende-2026. _ghid_lista extins multi-slug
(ghid_slug "|"). Verificat: 6 ghiduri in index+sitemap; pagina randeaza 200 cu title/meta description/canonical/OG/
JSON-LD/blocuri ghid-temei+ghid-exemplu. CSV integru 201x11 (test_registru passed). Toate pe functii LIVE, grounding
verbatim din anaf_surse (nicio valoare din memorie).

## 12.08.2026 — +9 ghiduri publice, legate + verificate
ghid/: salariu-minim-2026, cote-tva-2025, concediu-medical-cine-suporta, sponsorizare-credit-fiscal,
tva-la-incasare-exigibilitate, taxare-inversa-interna, control-incrucisat-d112, d394-ce-declari-reconciliere,
impozit-micro-2026. Legate in ghid_slug (F087/F023/F122/F086/F097/F091/F162/F034/F026, toate LIVE). Verificat: 15
ghiduri in index+sitemap; randare 200 + SEO complet (title/meta description/canonical/OG/JSON-LD/ghid-temei) pe
paginile noi; CSV integru 201x11. Temei verbatim din anaf_surse, nicio valoare din memorie.

## 12.08.2026 — +3 ghiduri finale (18 total)
ghid/: regim-marja-second-hand (F098), regim-special-agentii-turism (F099), decont-tva-d300-rezultat (F031). 18 ghiduri
in index+sitemap, randare 200+SEO. Toate verbatim din Cod fiscal art.311/312/323/303.


## 16.08.2026 — Onboarding CUBUS: garzi campanie regula 13
- `core/test_precompletare_anaf_unificata.py` — cele 3 cai de creare firma folosesc helperul unic de precompletare (Q9).
- `core/test_profil_blocaje.py` — CAEN out-of-enum + vector TVA lipsa la platitor blocheaza verdictul "complet" (Q1/Q8).
- `core/test_cauza_precisa_business.py` — ValueError business -> cauza precisa; RuntimeError -> generic (Q3).
- `core/test_d112_mesaje_afisate.py` — `raise ValueError` proza in d112 are diacritice (Q2).
- `core/test_onboarding_ux.py` — fereastra bun venit (ordine/nota/stivuire) + solduri (model/echilibru/transparenta) +
  descoperibilitate import firme (Q4-Q7, Q10).


## 16.08.2026 — Garzi import CUBUS (loturi 1-2)
- core/test_import_backend_corect.py — Q3/Q4/Q11/Q13 comportamental (cheama functiile), RED pe cod vechi.
- core/test_import_mesaje_afisate.py — rol raise ValueError pe fisierele de import are diacritice (Q2/Q17).
- test_import_migrare (_s cu tip_norma), test_solduri_parteneri (2 randuri), test_import_backend_corect
  (cnp_invalid) re-ancorate la comportamentul nou.

## 16.08.2026 - Gard C1 (pontaj neconfirmat gri)
- core/test_c1_pontaj_neconfirmat_gri.py (2) - interzice marcajul rosu per-salariat "pontaj neconfirmat" si
  banner-ul ecran-nota rosu; cere .caseta-info + semafor gri (DS cap.23). RED probat pe cod vechi
  (marcaj rosu + ecran-nota rosu prezente); GREEN dupa fix.

## 16.08.2026 - Gard C2 (revenire la firma dupa import)
- core/test_c2_migrare_revenire_firma.py (2) - fiecare nav.deschide("<Titlu>", wizard) apare O SINGURA data
  (dispecerul de straturi); a doua aparitie (handlerul de salvare) = nav.inapoiPas() + _migMesaj/_consumaMigMesaj.
  RED probat pe cod vechi (7 titluri de 2 ori, fara _migMesaj); GREEN dupa fix.

## 16.08.2026 - Gard C4 (model CSV per strat)
- core/test_c4_model_csv.py (3) - cele 8 straturi de import au butonul model cablat (_descarcaModelCSV(MODELE.X)),
  MODELE are toate cheile, intro-ul mijloacelor numeste cont imobilizare+amortizare. RED probat pe cod vechi; GREEN dupa.

## 17.08.2026 - Gard verdict control fiscal (diacritice + fara nume intern) [audit tenant_004]
- core/test_control_fiscal_diacritice.py (2 teste) - mesajele de verdict din control_fiscal_api.py (args la
  gri/neaplic/emite_tva, valori _NEAP_FORMA_SIMPLA, variabila cauza_r, return-uri _existenta_fapt) au >=1
  diacritica si zero identificator snake_case (nume intern). Reutilizeaza _DIAC din test_diacritice_afisate
  (sursa unica). RED probat pe cod vechi (13 mesaje fara diacritice + scurgere platitor_tva_anaf_inceput);
  GREEN dupa fix. Autotest-cu-dinti inclus (test_autotest_criteriu_are_dinti).

## 17.08.2026 - Gard reconciliere D100 pe semafor (thunk = generator) [audit tenant_002]
- core/test_reconciliere_d100_wiring.py (2 teste) - reconciliaza_declaratii pe scheme efemere micro (venituri
  10000 -> D100 121) si profit (venituri 10000 + cheltuieli 6000 -> D100 103 pe profit 4000) cere stare d100
  'verde', fara "too many values to unpack" in motiv. Prinde SI aritatea (pull 3) SI formula (baza profit).
  RED probat pe cod vechi (ambele gri, crash despachetare); GREEN dupa extragerea d100.deriva_obligatii.

## 17.08.2026 - Gard bilant refuza fara reg_com (S1005+S1003) [audit tenant_002]
- core/test_bilant_regcom_poarta.py (3 teste) - genereaza (S1005) si genereaza_s1003 ridica ValueError cu
  "registrul comertului" cand reg_com lipseste; control pozitiv: cu reg_com completat, S1005 se genereaza.
  RED probat pe cod vechi (ambele emiteau XML fara regCom, DID NOT RAISE); GREEN dupa adaugarea reg_com in
  bilant_api.erori_generare. Temei DUK: regCom "atributul trebuie sa existe".

## 17.08.2026 - Garzi default fabricat selecturi vector Date firma [audit tenant_001]
- core/test_vector_platitor_tva_oblig.py (2 teste) - vector_fiscal_api.salveaza cu platitor_tva=None (conn fals,
  fara DB) intoarce ok=False cod TVA_LIPSA si NU scrie; regresie operatiuni_ic=None ramane IC_LIPSA. RED pe cod
  vechi (bool(None)=False -> ok=True, platitor_tva=False persistat) -> GREEN.
- core/test_date_firma_alege_placeholder.py (4 teste) - source-scan pe date_firma.js: regim_fiscal/platitor_tva/
  operatiuni_ic marcate alege:true; placeholder randat la valoare lipsa (c.alege && !v, selected disabled hidden);
  salvarea NU coerce cu ===da (tri-stare triBool); regimul tine cont de partida_simpla. RED pe git
  HEAD:date_firma.js (rulat pe versiunea veche, cp temporar) -> GREEN.

## 17.08.2026 - Garzi IBAN import + blocaj vizibil SEPA/REGES [audit tenant_001]
- core/test_salariati_import_iban.py (4 teste) - parserul mapeaza coloana IBAN, verifica_randuri valideaza mod-97
  (un IBAN gresit trimite banii altcuiva), importa scrie iban in INSERT. RED pe cod vechi (importul stratul 4 nu
  avea IBAN deloc: parser/writer/model) -> GREEN.
- core/test_salariati_blocaj_vizibil.py (2 teste) - butoanele dezactivate SEPA / Raspunsuri REGES au motiv VIZIBIL
  (.caseta-info), NU doar prin title (invizibil pe touch). RED pe firme.js vechi (git HEAD, title="...") -> GREEN.

## 17.08.2026 - Garzi declarant obligatoriu + avertizat pe toate declaratiile [audit tenant_001, thread 3]
- core/test_declarant_oblig.py (3 teste) - declarant_nume + declarant_functie in firma_profil_api.OBLIGATORII;
  lipsuri le semnaleaza cu declaratiile blocate; prenume ramane optional. RED pe OBLIGATORII vechi -> GREEN.
- core/test_declarant_warn.py (1 test) - toate cele 8 declaratii care emit declarantul (d100/d101/d205/d112/
  d300/d301/d390/bilant) AVERTIZEAZA cand lipseste (nu fabrica tacit "ADMINISTRATOR"). RED pe d100 vechi -> GREEN.

## Bifa 17.08.2026 — audit tenant_005: import salariu_brut obligatoriu

`core/test_import_migrare.py`: adaugat `salariu_brut` la fixture-ul `_s()` (un salariat complet ARE baza > 0) + `test_salariu_brut_lipsa_e_respins`, `test_salariu_brut_negativ_e_respins`. RED probat pe cod vechi (stash salariati_import_api.py). GREEN: 21 passed in test_import_migrare.py; 33 passed pe suita de import salariati (iban/preview/d1/backend/cnp/valideaza). Gard in GARZI.

## Bifa 17.08.2026 — audit tenant_005: semnal baza lipsa + editare salariu

`core/test_salariu_scrieri.py`: `test_stat_plata_semnaleaza_baza_lipsa` (RED KeyError pe cod vechi) + `test_editarea_salariului_prin_put_dateaza_istoricul` (UPSERT pe data). GREEN: 33 passed (test_salariu_scrieri + test_import_migrare). Frontend cablat (buton „Salariu”), probat vizual pe Stat de plata. Gard in GARZI.

## Bifa 17.08.2026 — audit tenant_005: import articole stoc fara pret (Regula 13)

`core/test_import_migrare_valideaza.py::test_articole_stoc_fara_pret_e_invalid` (RED pe cod vechi). GREEN 7 passed. Generalizarea sweep-ului pe validatorii de import (subagent): singurul analog al salariu_brut = articole. Gard in GARZI.
## Bifa 17.08.2026 — audit tenant_005: mesaje user-facing fara nume intern de camp (cluster 4)

`core/test_mesaje_fara_camp_intern.py` (RED-probat: reintrodus `tip_decont` in mesaj -> pica). GREEN. 13 mesaje reparate in 8 fisiere. Refoloseste `_candidati()` din test_diacritice_afisate. Gard in GARZI. DS v2.35.

## Bifa 17.08.2026 — audit tenant_005: vector per-firma reflecta vectorul salvat (cluster 5)

`core/test_tip_decont_lung.py`: contract primitiva + integrare (tenant legacy L/T -> forma lunga prin citeste/portal) + clamp B1 (formularVectorFirma incarca /vector). Ambele RED-probate. GREEN 3 passed. versioneaza_assets --scrie (migrare.js). Gard in GARZI. DS v2.36.
## Bifa 17.08.2026 — audit tenant_005: diacritice mesaje validatori import (cluster 6)

`core/test_diacritice_afisate.py::test_validatori_import_cu_diacritice` (nou) + 14 triggere. RED-probat: avertisment fara diacritice -> pica. 21 mesaje reparate in 8 validatori + e-Factura. Aliniat test_mijloace_fixe_import_categorie. DS v2.37.

## Bifa 17.08.2026 — audit tenant_005: plan conturi adaugare reparata (cluster 7)

`core/test_rute_model_body.py` (nou): niciun param BaseModel clasificat ca query. RED-probat: PlanContIn dupa handler -> flagheaza param 'date'. Probat live: POST plan-conturi 200 (era 422). DS v2.38.
## Bifa 17.08.2026 — Front D: D205 diacritice + temei D112 (art.60 pct.5 abrogat)

`core/test_diacritice_afisate.py::test_generatoare_declaratii_cu_diacritice` (nou, _GEN_DECLARATII=[d205], RED-probat). 17 mesaje d205 diacriticizate. Aliniat test_d205_cui_checksum + test_declarant_warn. D112 verificat la sursa (OUG 156/2024). DS v2.39.

## Bifa 17.08.2026 — Front E: editare identitate salariat din UI

`core/test_front_e_editare_identitate.py` (nou): contract backend (SalariatEdit+_CAMPURI_API) + clamp UI (firme.js data-date/ed-cnp/cnpValid). RED-probat. Probat live: form pre-completat CNP/nume, validare CNP. DS v2.40.
## Bifa 17.08.2026 — backlog diacritice generatoare declaratii INCHIS

`test_generatoare_declaratii_cu_diacritice` (_GEN_DECLARATII = 58 fisiere). ~840 literale diacriticizate prin unealta; ~18 fisiere de test aliniate (aserari pe substring-uri de mesaj). Suita intreaga verde (1965 passed), verificator 0. DS v2.41.
## Bifa 17.08.2026 — a11y contrast WCAG AA (audit tenant_005)

`core/test_a11y_contrast_tokens.py` (nou, browser-free: recalcul contrast din sursa >= 4.5:1 pentru --albastru/camp-ajutor/CULORI_CARD). RED-probat (--albastru->#3d8fd6 pica). axe contrast=0 pe dashboard/vector/salariati. DS v2.42.
## Bifa 18.08.2026 — existenta_firma_an numara toata activitatea datata (audit tenant_006)

`core/test_existenta_activitate.py` (nou, 4 teste pe schema temporara: d301_operatiuni/casa_operatiuni/extras_linii = activitate; schema goala = False). RED-probat prin rulare (d301-only -> existenta 2026 False pe cod vechi). Suita control_incrucisat/premisa_restanta/matrice/control_fiscal: 198 passed.
## Bifa 18.08.2026 — D100 micro pe fapt (d100_fapt), audit tenant_006
`core/test_d100_fapt.py` (5 teste pure, mutatie-probata). Simetric d390_fapt/d112_fapt. Regresie matrice/premisa/termene/control/d100 = 232 passed.
## Bifa 18.08.2026 — a11y contrast Control fiscal (audit tenant_006)
`core/test_a11y_contrast_tokens.py` extins cu 2 teste (.cf-incr-temei #5c6675, coduri declaratii #2f6fa6, pe #e9edf3 >= 4.5). Mutatie-probat RED. axe contrast=0 pe Control fiscal. DS v2.43. Import blockages (salariati CNP / solduri dezechilibru) verificate curat vizual.
## Bifa 18.08.2026 — field-level error marking (audit tenant_006)
`core/test_fieldmark.py` (3 teste: eroareCamp marcheaza inputul + aria-invalid, curataEroriCamp scoate, CSS override invinge bordura globala). Mutatie-probat RED. Captura privita Date firma. DS v2.44.
## Bifa 18.08.2026 — D390 semnaleaza achizitiile din d301 (front 2)
`core/test_d390_d301_semnal.py` (2 teste: achizitii_d301 temp-schema + mesaj refuz tenant_006). Mutatie-probat RED. D390 producibil manual -> XML valid probat (rollback). 19 passed d390.
## Bifa 18.08.2026 — auto-derivare d301->D390 cod A/S (audit tenant_006, decizia Costin)
`core/test_d390_autoderivare.py` (mapare tip->cod + filtru tara; generator==reconciliere, mutatie-probat). Migrare `core/migrare_d301_partener` (19/19 scheme, test_audit_schema verde). D390 auto-derivat DUK valid probat. 103 passed regresie.
## Bifa 18.08.2026 — tip 3 -> cod A (sursa+DUK) + avertisment d301 rafinat
`test_d390_autoderivare.py` + fix schema temporara `test_d390_d301_semnal.py` (coloana partener_tara). tip 3 DUK valid (bazaA), tip 5 (bazaS). achizitii_d301 numara doar tip 1/3/5 fara tara. 116 passed d390.
## Bifa 18.08.2026 — tip 4 exclus din D390 verificat la sursa (CF art. 307)
Fara test nou (maparea neschimbata; test_mapare_tip_cod acopera deja tip 4 exclus). Comentariu temei precis in d390.py + nota UI grila D301. Captura privita.
## Bifa 18.08.2026 — indiciu mis-clasificare tip 4 -> tip 5
`core/test_d390_autoderivare.py::test_d390_posibil_serviciu...` (tip 4 cu cod -> True; tip 4 fara cod / tip 5 -> False). Mutatie-probat. Fixtura extinsa cu coloanele cerute de lista. 25 passed d390/d301. [citare-istorica: mecanism inlocuit de temei_307, 19.08.2026]
## Bifa 18.08.2026 — confirmare "nu e serviciu IC" (fals-pozitiv tip 4)
`core/test_d390_autoderivare.py::test_confirma_local_stinge_indiciul_reversibil` (True -> confirma -> False -> anuleaza -> True). Mutatie-probat. Migrare `core/migrare_d301_confirmat` (19/19, test_audit_schema verde). 37 passed. [citare-istorica: mecanism confirma_local/euristica inlocuit de temei_307, 19.08.2026]
## Bifa 18.08.2026 — confirmare persistenta per-furnizor
`core/test_d390_autoderivare.py::test_confirmare_per_furnizor_persista_intre_luni` (confirma iun -> iul acelasi furnizor mosteneste). Mutatie-probat. 25 passed. Fara migrare (derivat din confirmarile per-operatiune). [citare-istorica: mecanism confirma_local/euristica inlocuit de temei_307, 19.08.2026]
## Bifa 18.08.2026 — a11y contrast .btn-link + summary (axe pe grila D301)
`core/test_a11y_contrast_tokens.py` extins (2 teste: .btn-link pe alb+#e9edf3, .dec-xml summary pe #e9edf3, >= 4.5). Mutatie-probat. axe D301 contrast 8->0. Inchide RAMAS DS v2.42 (.btn-link #3d8fd6).
## Bifa 18.08.2026 — formular manual D710 in UI (declaratie 1/6)
`core/test_d710_formular.py` (3 teste, mutatie-probat). d710 scos din _DOAR_API -> GET /declaratii/tipuri (10). CSV F192->LIVE, test_registru_functionalitati verde. Backend refuz-gol + formular UI (model D301). DUK valid (cod 103 + cod 121 cu cota).

## Bifa 18.08.2026 — formular manual D311 in UI (declaratie 2/6)
`core/test_d311_formular.py` (3 teste, mutatie-probat prin sed pe mesaj) + `core/test_d311.py` re-ancorat (aserta formularea de contabil, nu numele intern Data_A/d_anul/OB_51, + asertie no-interne). d311 scos din _DOAR_API -> GET /declaratii/tipuri; d307 pus la loc (prins de test_live_accesibil). CSV F207->LIVE + login.js GRUPE_FUNC regenerat (145->146). Proba Playwright reala (ALFA MICRO): DUK valid, axe contrast/eticheta 0, mobil Pixel5 fara overflow.

## Bifa 18.08.2026 — formular manual D307 in UI (declaratie 3/6)
`core/test_d307_formular.py` (3 teste, mutatie-probat prin sed pe mesaj) + `core/test_d307.py` extins (asertie no-nume-interne). d307 scos din _DOAR_API -> GET /declaratii/tipuri; vecinii intacti (d107 ramane API). CSV F217->LIVE + login.js GRUPE_FUNC regenerat. Proba Playwright reala (ALFA MICRO): DUK valid (2 operatiuni tip A + C, TVA negativ la regularizare), axe 0, mobil Pixel5 body=393 (fara overflow).

## Bifa 19.08.2026 — GARD D394 trimestrial (perioada + fereastra) [audit 003]
`core/test_d394_trimestrial_perioada.py` (4 teste, RED-probat prin mutatia fereastra T -> luna-ancora). Inghetare a corectitudinii D394 trimestrial dupa inchiderea misdiagnosticului „003 septembrie + cifre necorespunzatoare": eticheta canonica (trim*3=3/6/9/12, OPANAF 2194/2025 lit. c) + fereastra = trimestrul intreg (augustul cules, 5900+889=6789). Test pur pe core.common.fereastra_tva/Perioada, fara DB. Fara reparatie in cod (produsul era corect). Inchidere in PREDARE_LANT.md.

## Gărzi adăugate la auditul tenant_001 (20.08.2026)

| gardă | ce face imposibil |
|---|---|
| `core/test_refuz_generator_422.py` | un refuz motivat de generator să ajungă la contabil ca 500 gol |
| `core/test_mesaje_valueerror_publicat.py` | un nume intern (0 admis) sau un mesaj fără diacritice (clichet, baseline 84) în canalul `ValueError` publicat |
| `core/test_get_fara_scriere.py` | o rută GET să scrie în starea de business (excepție mecanică: `public.audit_log`) |
| `core/test_stergere_salariat_completa.py` | ștergerea unui salariat să lase rânduri-copil orfane |
| `core/test_a11y_contrast_tokens.py` (extins) | o clasă `.cf-*` cu culoare literală sub 4.5:1 pe panoul Control fiscal |

Fiecare are un test anti-gard-mort: dacă euristica se rupe (regex, decorator, cale de schemă), gardul PICĂ în
loc să treacă pe gol. Cel de la `test_stergere_salariat_completa` s-a declanșat chiar la naștere — găsise 3
tabele în `tenant_template.sql` când baza are 5, fiindcă schema trăiește și în `NN_ddl_*.sql`.


## 20.08.2026 — două gărzi noi

| gardă | ce face imposibil |
|---|---|
| `core/test_constante_nesursate.py` | o constantă fiscală nouă în cod de producție fără `Temei` (clichet per fișier, baseline 93 — coborât de la 126 pe 21.08: clasa E, apoi temeiul din d300_reconciliere) |
| `core/test_harta_temei.py` | o intrare din harta casetelor care tace despre temeiul legal, citează un act inexistent în corpus, sau are regulă de produs fără decizie+dată |

Amândouă poartă anti-vacuu. Cel de la `test_constante_nesursate` e o calibrare în PATRU direcții (a patra adăugată 21.08), fiindcă
una singură lasă scanul să treacă pe gol în celelalte — și fiecare direcție a picat efectiv o dată în
construcție. Cel de la `test_harta_temei` cere ca harta să conțină toate cele trei feluri de temei
(citare / datorie declarată / produs curat), altfel ramurile gardului n-au fost exercitate.

Instrument nou, nu test: `core/scan_constante.py` — clasifică literalii numerici din modulele fiscale în
A=sursat (48) / B=nomenclator (308) / C=nesursat (93) / D=precizie (37) / E=temei în proză (33).
(126 → 98 pe 21.08 după distingerea clasei E; → 93 după ce `d300_reconciliere` și-a primit temeiul.)

## 21.08.2026 — clasa E și TEMA D

| gardă | ce face imposibil |
|---|---|
| `core/test_constante_nesursate.py` (extins) | ca o citare în proză să ȘTEARGĂ datorie reală: `25` din `_ZIUA`, `d216 0.3`, `d101 16` și cele unsprezece aserțiuni din `d212_engine` trebuie să RĂMÂNĂ în C; iar o respingere din `PROZA_RESPINSA` care nu mai corespunde unui candidat pică |
| `core/test_granite_cota.py` TEMA D | ca `cote_tva` să întoarcă din nou o cotă marcată `sursa='fallback'`, sau ca `cote_valide()` să reînvie |

Clichetul a coborât **126 → 98**, cu cele 28 de false pozitive scoase. `cote_tva.py` (2) și `d300.py`
(5) au ieșit complet — amândouă își citează actul lângă valoare, în antet.

## 21.08.2026 — R6 + clasa absenta_observatie + confruntarea instrumentelor

| gardă | ce face imposibil |
|---|---|
| `core/test_depunere_contrazice.py` | ca o depunere pe o perioadă declarată „nu se datorează" să treacă nevăzută; și ca una pe un `neclar` să sune a obligație stinsă |
| `core/test_absenta_nu_e_neaplicabil.py` | un motiv „nu se datorează" formulat ca absență de înregistrări, fără poartă de completitudine numită |
| `core/test_constante_nesursate.py` (confruntarea) | ca scanul și verificatorul să se contrazică în tăcere despre același fișier |

Măsurat înainte de reparație: 12 motive „nu se datorează", 5 formulate ca absență (2 cu poartă reală,
1 fără — D205, reîncadrat — 2 dintr-o bifă, reformulate). Trecerea inversă: 7 contraziceri + 1 opinie
pe 17 firme, zero semnale înainte. Confruntarea instrumentelor: 9 semnale retroactiv, 5 azi (clichet).

## 21.08.2026 — faptul bate vectorul + poarta D390 întărită

| gardă | ce face imposibil |
|---|---|
| `core/test_faptul_bate_vectorul.py` | ca selectorul să blocheze D390/D301 pe bifă când faptul o contrazice sau evidența e incompletă; și ca blocajul să dispară când faptul chiar lipsește (contra-direcția) |
| idem, partea D390 | să se afirme „nu se datorează pe luna X" când există e-Facturi primite de la ANAF, neînregistrate pe acea lună |

Cinci mutații RED-probate. Cele două `except` sunt marcate `# MASCA MOTIVATA` — direcția tăcerii
contează: un eșec de citire produce „nu pot ști", niciodată o afirmație despre lume.

## 21.08.2026 — actul de închidere a lunii (`facturi`)

| gardă | ce face imposibil |
|---|---|
| `core/test_inchidere_luna.py` | să se închidă o lună peste documente primite și neînregistrate; ca o factură nouă/ștearsă să lase luna închisă; ca punctul de adoptare să fie ultima lună în loc de prima |

14 teste pe schemă efemeră reală. 5 mutații — a patra a trecut prima dată (o singură lună închisă face
„prima" și „ultima" să coincidă); testul a fost întărit până a devenit falsificabil.

## 21.08.2026 — P2: proprietatea cojii

| gardă | ce face imposibil |
|---|---|
| `core/test_proprietate_coaja.py` | ca un ecran să scrie direct în `.bara` / `.subbara` / `.bara3` / `.bara-antet`; și ca proprietarul să nu-și mai declare locul (chiriașii ar dispărea tăcut) |

Contract: `static/js/coaja.js` — `inregistreazaLoc` (proprietarul declară) / `cereLoc` · `pune` ·
`scoate` (chiriașul cere). `pune` e idempotent.

## 21–22.08.2026 — P8: afirmațiile despre datele firmei, în toată aplicația

| gardă | ce face imposibil |
|---|---|
| `core/test_afirmatii_tipate.py` | ca un fișier să producă MAI MULTE afirmații netipate decât la instalare; ca un fișier NOU să intre tăcut; ca baseline-ul să rămână peste realitate după o conversie; ca scanul să orbească pe vocabular greșit; ca excluderea hărților de nomenclator să se lărgească |
| `core/test_respingeri_import.py` | ca o respingere de import să poarte un cod din afara nomenclatorului ÎNCHIS; ca un cod declarat să rămână nefolosit; ca `migrare.js` să clasifice iar după textul uman |
| `core/test_chei_duplicate.py` | ca o cheie să apară de două ori în același dicționar — Python o dedublează TĂCUT, ruff n-o prinde, iar într-un nomenclator fiscal ordinea din fișier ar decide ce regulă se aplică |
| `core/test_flag_constatare.py` | ca vreuna din cele trei stări ale semaforului de portofoliu să nu producă o afirmație validă; ca `an`/`luna` să redevină opționale în semnătură |
| `core/test_unde.py` | un fel de referent inventat pe loc; un referent fără identitate; **un fapt fără NICIUN domeniu** |
| `core/test_registru_exceptii.py` | ca registrul de excepții să crească; ca o excepție să rămână după ce situl a fost convertit; ca un motiv să fie scris în proză în loc să fie ales din setul închis |

### Instrumente
`core/scan_afirmatii.py` (inventarul, patru clase) · `core/scan_respingeri.py` (confruntarea
coduri-folosite ↔ nomenclator, ambele direcții) · `core/unde.py` (referința structurată) ·
`core/registru_exceptii.py` (excepțiile, cu rațiuni închise).

### Mutații
- clichetul de afirmații: **5 direcții**, toate roșii (fișier existent care crește · fișier nou ·
  baseline peste realitate · scanul orbit · clasificarea care înghite clasele excluse);
- felurile noi: **4 mutații** — și una a trecut prima dată, fiindcă `__pycache__` stale reciclase
  bytecode-ul mutației anterioare (aceeași dimensiune, aceeași secundă). Sonda curăță acum cache-ul
  între mutații; fără asta proba era falsă;
- cheia duplicată: RED-probat cu **exact duplicatul care mi-a scăpat** în `migrare_api.REGULI`;
- statul emis (lot anterior, aceeași tură): 7 mutații, toate roșii — și DOUĂ dintre gărzi treceau
  degeaba înainte (numărau pe o lună fără contradicții; apăsau butonul o singură dată).

### Ce NU probează gărzile astea
Că textul e bun, că `fel`-ul ales e cel potrivit, sau că referentul din `unde` există în bază. Prima
e a gărzilor de calitate-mesaj; a treia cere conexiune și e o gardă separată, neconstruită.
