# PREDARE LANT — context proaspat (03.08.2026, dupa 4 clustere + decizia de produs cote reduse)

Sesiunea anterioara a RELUAT lantul fiscal, a inchis 4 clustere de agenda SI a implementat decizia de produs
aprobata de Costin (cote reduse TVA istorice 9%/5% ca doua chei). Se continua de la clusterul urmator.

## Munca exista in DOUA locuri (§2.3 pct.8)
- **Server (commit local):** ultimul cluster = `ef011cb`; peste el commitul de PREDARE. tree curat.
- **Remote (siguranta):** `backup/lant-20260803` = HEAD (push facut la finalul rularii; confirma cu
  `git ls-remote origin refs/heads/backup/lant-20260803`).
- **Push pe main: NU** (decizia exclusiva a lui Costin).

## Poarta (VERDE la iesire)
`venv/bin/pytest` = 1311 passed / 2 skipped / 21 xfailed (PYTEST_EC=0); `verificator_conformitate.py` TOTAL 0.

## Unde se lucreaza
`ssh iconta`, `~/iconta_nou`, branch `main`. pytest/verificator/DUK = `venv/bin/...`. Full-suite ~100-110s
(timeout 200000+; NU rula pytest de doua ori). Editari pe server prin python.
CAPCANA DE QUOTING (platita de doua ori): NU pune heredoc python/cat intr-un argument ssh in GHILIMELE DUBLE
daca textul contine backtick-uri - shell-ul LOCAL le interpreteaza si goleste bucatile. Foloseste
`ssh iconta 'cd ~/iconta_nou && python3 -' <<'PY' ... PY` (ssh in ghilimele SIMPLE, heredoc pe stdin).
`/tmp/cf.txt` = codul fiscal (linia 36 = cuprins urias, ignor-o; art.291 pe ~5779, art.290 pe ~5775).

## Inchise in aceasta rulare (cc30f3b -> ef011cb)
1. **baza = val x curs | d301** (5d2126d): FIX - `calc_baza(.., curs or 1)` fabrica tacit curs=1 pe valuta ->
   baza subevaluata la ANAF. calc_baza ridica pe curs None/<=0 (CF art.290 alin.(2)); scos or 1; scos DEFAULT 1.
2. **cota TVA | d301** (e253371): FIX - cota redusa era literal 11, gresita pt < 01.08.2025. Period-aware din
   common.cota. CF art.291 + Legea 141/2025.
3. **tipuri operatiune IC (L/A/P/S) | d390** (4faf7ae): VERIFICAT OPANAF 705/2020; gard-pin TIPURI.
4. **rotunjire aritmetica (A91b) | d390** (ef011cb): VERIFICAT ROUND_HALF_UP (gardat dublu); proba d390 pe valoare.
+ **DECIZIE PRODUS (Costin) IMPLEMENTATA** (5d1edda): cote reduse istorice 9% (CF art.291 alin.2) si 5% (alin.3)
  ca DOUA chei separate tva_redusa_9/_5 in COTE, comasate in 11% de la 01.08.2025. cote_perioada period-aware pe
  3 chei + dedup: 2026 [21,11,0], pre-08.2025 [19,9,5,0].

## Clusterul URMATOR (mecanic)
`agenda.urmator_cluster()` -> **`('reclasificari manuale','d390')`**, 42 ramase, 0 blocate.
- CAP DE PONT (observat deja in clusterul tipuri d390): `d390.py:151-152` - reclasificarea contabilului (P/S/T/R
  din tabela d390_reclasificare) face FALLBACK TACIT la L/A default cand tipul e invalid, in loc sa ridice ca
  la calea manuala (d390.py:159). NU e drop (operatiunea ramane declarata si numarata), dar e MISCLASIFICARE
  tacuta. Acoperit de `test_reclasificare_ignora_tip_invalid` (comportament INTENTIONAT). Cluster = decide daca
  se uniformizeaza cu calea manuala (raise/marcaj vizibil) sau se confirma ca acceptabil (dropdown UI controlat).

## Datorii de TEMEI deschise (de reconfirmat la MO)
- **Cote reduse 9%/5% - data de INCEPUT:** ancorata la 2017-01-01 (era standard 19%), REDARE, caveat in temei.
  Codul fiscal consolidat NU pastreaza nota istorica de introducere; fostul alin.(3) la 5% apare doar "Abrogat"
  (textul verbatim al operatiunilor la 5% neconfirmat). Pt perioade < 2017 cota() refuza (fail-loud). DECIZII 03.08.

## Observatii deschise (NEreparate)
- **d390 tara XI** (d390.py:45): Irlanda de Nord post-Brexit, in cod dar nu in Nomenclator Tari OPANAF 705/2020
  (doar GB). Tine de clusterul "nomenclator tari (HR->CR) | d390" (inca deschis in agenda).

## Datorii/blocaje (21 xfail, NESCHIMBAT)
Nicio datorie noua. `git grep "@pytest.mark.xfail" core/test_datorie.py`.

## Registre atinse (cc30f3b -> ef011cb)
- Cod: core/d301.py, core/d301_operatiuni_api.py, core/common.py (COTE += tva_redusa_9/_5),
  core/expirare_cote.py (ETICHETE), tenant_template.sql.
- Teste noi: core/test_d301_curs.py (4), core/test_d301_cota.py (6), core/test_d390.py (+2: pin + rotunjire).
- Registre: DECIZII.md (4 clustere + decizie produs rezolvata + 2 obs), GARZI.md (5 garduri), TESTE.md (Inventar A
  4 randuri bifate; secventa 46->42; fir). Ramura backup/lant-20260803 pe remote.

## Cum continui (sesiune noua)
1. Ritual §5: pwd/hostname/git log; `git rev-parse --is-inside-work-tree`; `./venv/bin/python -m core.agenda`.
2. `agenda.urmator_cluster()` -> reclasificari manuale | d390 (vezi CAP DE PONT). Verifica temeiul la sursa.
3. Increment rosu->verde->mutatie, commit local. La inchidere: gard (§9) + registre + bifare Inventar A +
   regenerare secventa din `agenda.secventa_calculata()` + nota narativa "-> N->N-1" (altfel
   `test_secventa_persistata_e_actuala` cade).
4. La finalul rularii: push de siguranta pe backup/lant-<data> (§2.3 pct.8), fara aprobare.
5. Limita: max 6 clustere/rulare. Sterge PREDARE_LANT.md dupa ce ai reluat lantul.
