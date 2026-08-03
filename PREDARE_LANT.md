# PREDARE LANT — context proaspat (03.08.2026, dupa 3 clustere fiscale)

Predare pentru o sesiune NOUA cu context GOL (§2.3 pct.6). Sesiunea anterioara a RELUAT lantul fiscal si a
inchis 3 clustere (baza=valxcurs, cota TVA, tipuri operatiune d390). Se continua de la clusterul urmator.

## Munca exista in DOUA locuri (§2.3 pct.8)
- **Server (commit local):** ultimul cluster = `4faf7ae`; peste el commitul de PREDARE. tree curat · ahead ~53.
- **Remote (ramura de siguranta):** `backup/lant-20260803` = HEAD (push de siguranta facut la finalul rularii;
  confirma cu `git ls-remote origin refs/heads/backup/lant-20260803`).
- **Push pe main: NU** (decizia exclusiva a lui Costin).

## Poarta (VERDE la iesire)
`venv/bin/pytest` = 1307 passed / 2 skipped / 21 xfailed (PYTEST_EC=0); `verificator_conformitate.py` TOTAL 0.

## Unde se lucreaza
`ssh iconta`, `~/iconta_nou`, branch `main`. pytest/verificator/DUK = `venv/bin/...`. Full-suite ~100-110s
(timeout 200000+; NU rula pytest de doua ori intr-o comanda). Editari pe server prin python.
CAPCANA DE QUOTING (platita): NU pune heredoc python/cat intr-un argument ssh in GHILIMELE DUBLE daca textul
contine backtick-uri sau `...` - shell-ul LOCAL le interpreteaza si goleste bucatile. Foloseste
`ssh iconta 'cd ~/iconta_nou && python3 -' <<'PY' ... PY` (ssh in ghilimele simple, heredoc pe stdin).
`/tmp/cf.txt` = codul fiscal strip-uit (linia 36 = cuprins urias, ignor-o; corpul art. e mai jos).

## Clustere inchise in aceasta rulare (cc30f3b -> 4faf7ae)
1. **baza = val x curs | d301** (5d2126d): NECONFORMITATE reparata - generator+reader faceau `calc_baza(.., curs or 1)`,
   deci curs absent pe EUR devenea tacit 1 -> baza subevaluata la ANAF fara eroare. Fix: calc_baza ridica pe
   curs None/<=0 (CF art.290 alin.(2)); scos "or 1"; scos `DEFAULT 1` de pe coloana curs in tenant_template.
2. **cota TVA | d301** (e253371): NECONFORMITATE reparata - cota redusa era literal 11 in cote_perioada,
   period-aware doar standardul. Pt perioade < 01.08.2025 oferea 11% gresit (atunci 9%/5%). Fix: redusa din
   `common.cota("tva_redusa")`, omisa cand neconfigurata. CF art.291 + Legea 141/2025.
3. **tipuri operatiune IC (L/A/P/S) | d390** (4faf7ae): VERIFICAT conform OPANAF 705/2020 (fara fix); gard-pin
   nou pe nomenclatorul TIPURI=(L,T,A,P,S,R).

## Clusterul URMATOR (mecanic)
`venv/bin/python3 -c "from core import agenda; print(agenda.urmator_cluster())"` ->
**`('rotunjire aritmetica (A91b)','d390')`**, 43 ramase, 0 blocate.
- Probabil VERIFICARE: rotunjirea aritmetica ROUND_HALF_UP (regula DUK A91b) e deja gardata cross-generator
  (`test_rotunjirea_e_identica_intre_generatoare`). Confirma pe d390, adauga proba d390-specifica daca lipseste.

## DECIZIE DE PRODUS DESCHISA (cere raspunsul lui Costin, §2.3 pct.2)
- **Cote reduse TVA istorice (9%/5% pre-01.08.2025).** Clusterul "cota TVA" a scos oferirea gresita a lui 11%
  pentru perioade < 08.2025, DAR pt a oferi CORECT cota redusa pe acele perioade, `COTE` trebuie remodelat:
  doua cote reduse COEXISTENTE (9% SI 5%); modelul actual tine o singura valoare/moment. Optiuni: doua chei
  `tva_redusa_9`/`tva_redusa_5`, sau valoare-lista. Schimba ce optiuni vede contabilul -> decizia lui Costin.
  Pana la decizie: pre-08.2025 ramane fara optiune de redusa (fail-loud). Detalii in DECIZII.md 03.08.

## Observatii deschise (raportate, NEreparate)
- **d390 reclasificare (d390.py:151-152):** tip invalid din tabela d390_reclasificare -> fallback TACIT la L/A
  (misclasificare posibila, NU drop - operatiunea ramane declarata). De decis daca se uniformizeaza cu calea
  manuala (raise pe tip invalid). DECIZII 03.08.
- **d390 tara XI (d390.py:45):** Irlanda de Nord post-Brexit (VIES) e in cod dar NU in Nomenclator Tari 2020
  (doar GB). Tine de clusterul "nomenclator tari (HR->CR) | d390" (inca deschis in agenda), nu de cel inchis.

## Datorii/blocaje (21 xfail, NESCHIMBAT)
Nicio datorie noua deschisa in aceasta rulare. `git grep "@pytest.mark.xfail" core/test_datorie.py`.

## Registre atinse (cc30f3b -> 4faf7ae)
- Cod: core/d301.py, core/d301_operatiuni_api.py, tenant_template.sql.
- Teste noi: core/test_d301_curs.py (4), core/test_d301_cota.py (3), core/test_d390.py (+1 pin).
- Registre: DECIZII.md (3 clustere + decizia de produs + 2 obs), GARZI.md (3 garduri cu mutatie probata),
  TESTE.md (Inventar A: 3 randuri bifate √ 03.08; secventa persistata 46->43; fir la zi). CLAUDE.md necitit-modificat.
- Ramura de siguranta: backup/lant-20260803 pe remote.

## Cum continui (sesiune noua)
1. Ritual §5: `pwd; hostname; git log --oneline -1; git rev-parse --is-inside-work-tree; ./venv/bin/python -m core.agenda`.
   Trebuie /home/costin/iconta_nou, iconta-prod, arbore valid. Daca nu - OPRIRE.
2. `agenda.urmator_cluster()` -> rotunjire aritmetica (A91b) | d390. Verifica temeiul la sursa.
3. Increment rosu->verde->mutatie, commit local. La inchidere: gard (§9) + registre + bifare Inventar A +
   regenerare secventa numerotata din `agenda.secventa_calculata()` + nota narativa "-> N->N-1" (altfel
   `test_secventa_persistata_e_actuala` cade).
4. La finalul rularii: push de siguranta pe backup/lant-<data> (§2.3 pct.8), fara aprobare.
5. Limita: max 6 clustere/rulare. Sterge PREDARE_LANT.md dupa ce ai reluat lantul.
