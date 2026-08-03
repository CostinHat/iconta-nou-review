# PREDARE LANT — context proaspat (03.08.2026, LIMITA DE 6 clustere atinsa)

Rulare oprita la LIMITA §2.3 pct.5 (max 6 clustere/rulare), nu premature. Sesiunea a inchis 6 clustere de agenda
+ a implementat decizia de produs a lui Costin (cote reduse 9%/5%). Sesiunea NOUA reia de la clusterul urmator.

## Munca in DOUA locuri (§2.3 pct.8)
- **Server:** ultimul cluster = `e4a25ee`; peste el commitul de PREDARE. tree curat.
- **Remote:** `backup/lant-20260803` = HEAD (push la finalul rularii; confirma cu
  `git ls-remote origin refs/heads/backup/lant-20260803`).
- **Push pe main: NU** (decizia lui Costin).

## Poarta (VERDE)
`venv/bin/pytest` = 1313 passed / 2 skipped / 21 xfailed (PYTEST_EC=0); `verificator_conformitate.py` TOTAL 0.

## Unde se lucreaza
`ssh iconta`, `~/iconta_nou`, branch `main`. venv/bin/... Full-suite ~100-110s (timeout 200000+; NU de doua ori).
Editari prin python: `ssh iconta 'cd ~/iconta_nou && python3 -' <<'PY' ... PY` (ghilimele SIMPLE la ssh, heredoc pe
stdin) - NU heredoc cu backtick-uri intr-un arg ssh in ghilimele duble. `/tmp/cf.txt` = codul fiscal (linia 36 =
cuprins, ignor-o; art.283/284 ~5730, art.290 ~5775, art.291 ~5779, art.325 ~6386).

## Inchise in aceasta rulare (cc30f3b -> e4a25ee)
1. **baza = val x curs | d301** (5d2126d): FIX - calc_baza(.., curs or 1) fabrica tacit curs=1. calc_baza ridica pe
   None/<=0 (CF art.290 alin.2); scos or 1 + DEFAULT 1.
2. **cota TVA | d301** (e253371): FIX - cota redusa literal 11 -> period-aware (CF art.291 + Legea 141/2025).
3. **tipuri operatiune IC | d390** (4faf7ae): VERIFICAT OPANAF 705/2020; gard-pin TIPURI.
4. **rotunjire aritmetica A91b | d390** (ef011cb): VERIFICAT ROUND_HALF_UP; proba d390 pe valoare.
5. **reclasificari manuale | d390** (c4c3d83): FIX - read-side valideaza direciția (fail-loud) ca write-side;
   TIPURI_DIRECTIE mutat in d390.py.
6. **exigibilitate / prag | d390** (e4a25ee): VERIFICAT - incadrare pe data_emitere = exigibilitate (CF art.283/284),
   fara prag (art.325); gard temporal pe pull.
+ **DECIZIE PRODUS (Costin) IMPLEMENTATA** (5d1edda): cote reduse istorice 9%/5% ca doua chei tva_redusa_9/_5.

## Clusterul URMATOR (mecanic)
`agenda.urmator_cluster()` -> **`('cote acceptate','d394')`**, 40 ramase, 0 blocate.
- D394 = declaratia informativa a livrarilor/achizitiilor pe teritoriul national. "Cote acceptate" = de verificat
  ce cote TVA accepta/valideaza D394 pe operatiuni, period-aware (21/11 acum; 19/9/5 istoric). Legatura cu clusterul
  "cota TVA" (d301, deja inchis) si cu common.COTE (tva_standard/tva_redusa/_9/_5 acum populate). Verifica d394.py.

## DECIZII DE PRODUS / SCHEMA deschise (cer raspunsul lui Costin)
1. **Cote reduse 9%/5% - data de INCEPUT** ancorata la 2017-01-01 (REDARE, de reconfirmat la MO; codul consolidat
   nu pastreaza nota istorica). Pt perioade < 2017 cota() refuza (fail-loud). DECIZII 03.08.
2. **D390 plafon "ziua 15" (exigibilitate intarziata):** art.284 cere exigibilitatea la ziua 15 a lunii urmatoare
   faptului generator cand factura intarzie; NEimplementabil - tabela facturi nu are data faptului generator. Fix
   cere camp nou in schema facturi + ce introduce contabilul = decizie de schema/produs. DECIZII 03.08.

## Observatii deschise (NEreparate)
- **d390 tara XI** (d390.py:45): Irlanda de Nord post-Brexit, in cod dar nu in Nomenclator Tari 2020. Tine de
  clusterul "nomenclator tari (HR->CR) | d390" (inca deschis).

## Datorii/blocaje (21 xfail, NESCHIMBAT)
Nicio datorie noua. `git grep "@pytest.mark.xfail" core/test_datorie.py`.

## Registre atinse (cc30f3b -> e4a25ee)
- Cod: d301.py, d301_operatiuni_api.py, common.py, expirare_cote.py, d390.py, d390_clasificare_api.py, tenant_template.sql.
- Teste noi: test_d301_curs.py (4), test_d301_cota.py (6), test_d390.py (pin+rotunjire+reclasificare rescris/dir),
  test_pull_declaratii.py (+1 gard temporal d390).
- Registre: DECIZII.md (6 clustere + decizie produs + 2 decizii deschise), GARZI.md (7 garduri), TESTE.md (Inventar A
  6 randuri bifate; secventa 46->40; fir). Ramura backup/lant-20260803 pe remote.

## Cum continui (sesiune noua)
1. Ritual §5: pwd/hostname/git log; `git rev-parse --is-inside-work-tree`; `./venv/bin/python -m core.agenda`.
2. `agenda.urmator_cluster()` -> cote acceptate | d394. Verifica temeiul (cote D394 vs common.COTE period-aware).
3. Increment rosu->verde->mutatie, commit local. La inchidere: gard (§9) + registre + bifare Inventar A +
   regenerare secventa din `agenda.secventa_calculata()` + nota narativa "-> N->N-1".
4. La finalul rularii: push de siguranta pe backup/lant-<data> (§2.3 pct.8).
5. Limita: max 6 clustere/rulare. Sterge PREDARE_LANT.md dupa reluare.
