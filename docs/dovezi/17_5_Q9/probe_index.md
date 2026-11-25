# 17.5-Q9 — indexul probelor (fiecare rulare: junit.xml, rc.txt, rulare.meta cu commitul și indexul, capturi/pytest.log cu liniile VERDICT)

Rulările pe 8019 trec prin `rulare_8019.sh` (lacătul oficial, portul eliberat, `baza_test.sh restaureaza` cu `--restaureaza`, rulatorul nativ `scripts/e2e_poarta.py` pe indexul git).

## Pe E_R2 (7d953658, worktree curat, numai testul REAL adăugat în index)
- `dovada_real_E/` — REAL izolat, baza restaurată: e.1 pică, e.2 trece, e.3 trece, e.4 pică; `cititor_E.out` (citeste_rezultat_Q7.py E, rc=0).
- `inainte/code/` — B4 prin `lanseaza_verificator.py --verificator code --parcurgere inainte`: f.1 trece, f.2 trece, a.1 pică (59).
- `probe_E/lot93a/` — `e2e_lot93a::test_def_c61_*` pică pe E (identic cu candidatul).
- `p2/7_diag_E_rep{1,2,3}/` — P2 izolat cu mutația de diagnostic: 3 din 3 trec (citirea tot în primul cadru al animației).

## P2 (decizia 13), pe candidatul P 751c21b5 înainte de reparația C238
- `p2/1_izolat` — izolat, restaurat: trece.
- `p2/2_N_P2` — e2e_ferestre_firma_17_5_N → P2, restaurat: trec.
- `p2/3_prefix_nativ` — fișierele 1–29 ale manifestului în ordine, apoi P2, restaurat: 91 trec, 2 pică (R021, R027); P2 trece (3,56 s).
- `p2/4_izolat_diag`, `p2/6_diag_cand_rep{1,2,3}` — izolat cu mutația de diagnostic (`p2/mutatie_diagnostic.json`, aplicată pe copia exportată): pică 2 din 4 (bloc None; `p2_diagnostic.json`: animațiile `aparitie-overlay` / `aparitie-fereastra` în curs, opacitatea suprapunerii 0,22 la ~17 ms, iar la momentul citirii 0).
- `p2/5_izolat_rep{1..4}` — izolat fără mutație: 4 din 4 trec (cursă de cadru).
- `p2/8_diag_reparat_rep{1..5}` — după reparația C238 (stil.css), cu diagnosticul: 5 din 5 trec, inclusiv citiri în cadrul 0 (opacitate 0,6).

## Pe candidat
- `probe_P/real_izolat` (P) — REAL izolat: patru «trece», cititorul C rc=0.
- `probe_P/f054_apoi_real` (P) — f054 → REAL: e.1 pică (C239: «Validează selectate» sub caseta de bun-venit), e.2–e.4 trec.
- `probe_P/f054_apoi_real_r2` (P + C239) — f054 → REAL: patru «trece», «De validat», «Note de validat (8)» = GET /coada; cititorul C pe `junit_numai_fundatie.xml` (extrasul nodului fundației din junit.xml) rc=0.
- `probe_P/fluxuri` (P) — F089 trece, F045 pică (corpul răspunsului gol pentru Playwright); `probe_P/fluxuri_r2` (P + api.descarca prin arrayBuffer): 4 din 4.
- `probe_P/lot93a` — 3 trec, c61 pică (identic pe E).
- `probe_P/toast_198` — `e2e_bloc_a::test_def_198` (caseta de bun-venit pe pagina principală) trece după C239.
- `probe_Pbis/` (P′ fa6436af) — REAL izolat patru «trece» (cititorul C rc=0), P2 izolat trece, P2 cu diagnosticul trece.
- Setul pytest al porții (nucleul + testele lotului, 240 de fișiere): pe P 1901 trec (`pytest_set_P.txt`), pe P′ 1901 trec (`pytest_set_Pbis.txt`).
