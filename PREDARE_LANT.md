# PREDARE LANT — context proaspat (03.08.2026, dupa 5 clustere + decizia de produs cote reduse)

Sesiunea anterioara a RELUAT lantul fiscal, a inchis 5 clustere de agenda SI a implementat decizia de produs a lui
Costin (cote reduse istorice 9%/5% ca doua chei). Se continua de la clusterul urmator.

## Munca exista in DOUA locuri (§2.3 pct.8)
- **Server (commit local):** ultimul cluster = `c4c3d83`; peste el commitul de PREDARE. tree curat.
- **Remote (siguranta):** `backup/lant-20260803` = HEAD (push la finalul rularii; confirma cu
  `git ls-remote origin refs/heads/backup/lant-20260803`).
- **Push pe main: NU** (decizia exclusiva a lui Costin).

## Poarta (VERDE la iesire)
`venv/bin/pytest` = 1312 passed / 2 skipped / 21 xfailed (PYTEST_EC=0); `verificator_conformitate.py` TOTAL 0.

## Unde se lucreaza
`ssh iconta`, `~/iconta_nou`, branch `main`. pytest/verificator/DUK = `venv/bin/...`. Full-suite ~100-110s
(timeout 200000+; NU rula pytest de doua ori). Editari pe server prin python.
QUOTING: `ssh iconta 'cd ~/iconta_nou && python3 -' <<'PY' ... PY` (ssh in ghilimele SIMPLE, heredoc pe stdin) -
NU heredoc cu backtick-uri intr-un arg ssh in ghilimele duble (shell-ul local le mananca).
`/tmp/cf.txt` = codul fiscal (linia 36 = cuprins urias, ignor-o; art.290 ~5775, art.291 ~5779).

## Inchise in aceasta rulare (cc30f3b -> c4c3d83)
1. **baza = val x curs | d301** (5d2126d): FIX - calc_baza(.., curs or 1) fabrica tacit curs=1 pe valuta. calc_baza
   ridica pe curs None/<=0 (CF art.290 alin.2); scos or 1; scos DEFAULT 1 din schema.
2. **cota TVA | d301** (e253371): FIX - cota redusa literal 11 -> period-aware. CF art.291 + Legea 141/2025.
3. **tipuri operatiune IC | d390** (4faf7ae): VERIFICAT OPANAF 705/2020; gard-pin TIPURI.
4. **rotunjire aritmetica A91b | d390** (ef011cb): VERIFICAT ROUND_HALF_UP (gardat dublu); proba d390 pe valoare.
5. **reclasificari manuale | d390** (c4c3d83): FIX - read-side (calcul_d390+operatiuni_auto) facea fallback tacit
   la default pe reclasificare invalida; acum valideaza direciția ca write-side si ridica. TIPURI_DIRECTIE mutat in
   d390.py (sursa unica). Temei DECIZII 21.07 + OPANAF 705/2020.
+ **DECIZIE PRODUS (Costin) IMPLEMENTATA** (5d1edda): cote reduse istorice 9% (CF art.291 alin.2) si 5% (alin.3)
  ca DOUA chei tva_redusa_9/_5 in COTE, comasate in 11% de la 01.08.2025. cote_perioada: 2026 [21,11,0],
  pre-08.2025 [19,9,5,0].

## Clusterul URMATOR (mecanic)
`agenda.urmator_cluster()` -> **`('exigibilitate / prag','d390')`**, 41 ramase, 0 blocate.
- D390 e declaratie recapitulativa (VIES). "Exigibilitate/prag" = de verificat CAND intra o operatiune IC in D390
  (faptul generator / exigibilitatea la operatiuni intracom, CF art.284/285) si daca exista vreun PRAG de depunere
  sau periodicitate (lunar). Verifica _facturi_ic (filtrul IC din d390.py) + temeiul la sursa. Increment sau verificare.

## Datorii de TEMEI deschise (de reconfirmat la MO)
- **Cote reduse 9%/5% - data de INCEPUT:** ancorata la 2017-01-01 (era 19%), REDARE, caveat in temei. Codul fiscal
  consolidat nu pastreaza nota istorica; fostul alin.(3) la 5% = doar "Abrogat" (text verbatim neconfirmat). Pt
  perioade < 2017 cota() refuza (fail-loud). DECIZII 03.08.

## Observatii deschise (NEreparate)
- **d390 tara XI** (d390.py:45): Irlanda de Nord post-Brexit, in cod dar nu in Nomenclator Tari OPANAF 705/2020
  (doar GB). Tine de clusterul "nomenclator tari (HR->CR) | d390" (inca deschis in agenda).

## Datorii/blocaje (21 xfail, NESCHIMBAT)
Nicio datorie noua. `git grep "@pytest.mark.xfail" core/test_datorie.py`.

## Registre atinse (cc30f3b -> c4c3d83)
- Cod: core/d301.py, core/d301_operatiuni_api.py, core/common.py, core/expirare_cote.py, core/d390.py,
  core/d390_clasificare_api.py, tenant_template.sql.
- Teste noi: test_d301_curs.py (4), test_d301_cota.py (6), test_d390.py (+2 pin/rotunjire; reclasificare rescris+1).
- Registre: DECIZII.md (5 clustere + decizie produs + 2 obs), GARZI.md (6 garduri), TESTE.md (Inventar A 5 randuri
  bifate; secventa 46->41; fir). Ramura backup/lant-20260803 pe remote.

## Cum continui (sesiune noua)
1. Ritual §5: pwd/hostname/git log; `git rev-parse --is-inside-work-tree`; `./venv/bin/python -m core.agenda`.
2. `agenda.urmator_cluster()` -> exigibilitate / prag | d390. Verifica temeiul la sursa (CF art.284/285 exigibilitate IC).
3. Increment rosu->verde->mutatie, commit local. La inchidere: gard (§9) + registre + bifare Inventar A +
   regenerare secventa din `agenda.secventa_calculata()` + nota narativa "-> N->N-1".
4. La finalul rularii: push de siguranta pe backup/lant-<data> (§2.3 pct.8), fara aprobare.
5. Limita: max 6 clustere/rulare (aceasta rulare a facut 5 + o decizie de produs). Sterge PREDARE_LANT.md dupa reluare.
