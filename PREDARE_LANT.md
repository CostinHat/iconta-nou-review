# PREDARE LANT — context proaspat (03.08.2026, dupa campania de siguranta + hardening)

Predare pentru o sesiune NOUA cu context GOL (§2.3 pct.6). Ultima activitate NU a fost un cluster fiscal, ci
campanii NORMATIVE + de SIGURANTA cerute de Costin. Lantul fiscal se reia la clusterul urmator din agenda.

## Munca exista in DOUA locuri (§2.3 pct.8)
- **Server (commit local):** HEAD `da89b60` · tree curat (`git status --porcelain` gol) · ahead 45 fata de origin/main.
- **Remote (ramura de siguranta):** `backup/lant-20260803` = `da89b60` (identic cu HEAD, 45 commituri). Confirmat
  `git ls-remote origin refs/heads/backup/lant-20260803`.
- **Push pe main: NU** (decizia exclusiva a lui Costin, decizia c). Push de siguranta pe backup: OBLIGATORIU la
  finalul rularii, NU cere aprobare (§2.3 pct.8).

## Poarta (toate VERZI)
`venv/bin/pytest` = 1299 passed / 2 skipped / **21 xfailed** (PYTEST_EC=0); `verificator_conformitate.py` TOTAL 0.
1322 teste colectate. **Sold datorii: 21 xfail** in core/test_datorie.py.

## Unde se lucreaza
`ssh iconta`, `~/iconta_nou`, branch `main`. pytest/verificator/DUK = `venv/bin/...`. Full-suite ~100-110s
(foloseste timeout 200000+; NU rula pytest de doua ori intr-o comanda - depaseste 2 min). Editari pe server prin
scripturi python scp-uite din tmp (Edit local NU atinge serverul). `/tmp/cf.txt` = codul fiscal strip-uit (daca
lipseste, regenereaza din anaf_surse/cod_fiscal_227_2015_consolidat.html).

## REGULI NOI adaugate in aceasta sesiune (citeste-le, sunt active)
- **CLAUDE.md §2.3 pct.7 RAPORTUL IN LANT:** fiecare cluster inchis primeste raportul lui §2.2 sectiunile 1-10,
  inclusiv 8 (generalizare pe clasa), 9 (garduri), 10 (efect pe produs). Sinteza pe rulare NU inlocuieste
  rapoartele per cluster. Un cluster fara sectiunea 9 NU se declara inchis (daca nu s-a pus gard, §9 spune de ce
  reaparitia e deja imposibila).
- **CLAUDE.md §2.3 pct.8 SIGURANTA:** inainte de a raporta, verifica munca in doua locuri (server + backup). Daca
  e intr-unul singur, spune-o la PRIMA linie a raportului. Raportul se incheie cu `BACKUP: <ramura> — <n> commituri`.
- **CLAUDE.md §2.3 pct.9 WIP LA OPRIRE PE ROSU:** la oprire pe tree murdar/poarta rosie, INAINTE de raport, pune
  munca la adapost FARA s-o repari (`git stash create` + push pe `wip/<data>-<ora>`, sau commit pe ramura wip/).
  Tree-ul ramane in starea defecta. Raportul declara `WIP SALVAT: <ramura>`.
- **DECIZII.md decizia (c):** push de siguranta pe `backup/lant-<data>` la finalul FIECAREI rulari = obligatie,
  nu optiune. Push main ramane decizia lui Costin.

## Clusterul URMATOR (mecanic)
`venv/bin/python3 -c "from core import agenda; print(agenda.urmator_cluster())"` -> **`('baza = val x curs','d301')`,
46 ramase, 0 blocate.**
- Scop: in D301 baza impozabila = valoare_valuta x curs (achizitii intracom in valuta). Vezi `calc_baza` +
  `Operatiune` in core/d301.py. Verifica: cursul folosit (BNR la data faptului generator / a facturii?),
  rotunjirea bazei (`_r0`), moneda (EUR default). Temei: CF art.290 (cursul de schimb pt baza in valuta) + OPANAF
  592/2016. Proba pe date reale + DUK (PROF/_op in core/test_d301_rollup.py; CUI valid pt DUK = 14399840, nu
  RO12345678). Increment testat, commit local, gard + registru la inchidere.

## Pattern de tinut minte (descoperit + reparat pe clasa)
**Allow-list manual incompleta = drop tacit** in generatoarele de declaratii. Radacina bug-urilor R12 (taxare
inversa) + R29/R30/R35/R36 + R38/R39/R43/R44 (ajustari) din D300. GARD PE CLASA pus (commit 88915de): d300
"aplicate-sau-eroare" (cheie manual neaplicata -> ValueError), d390/d394 ridica pe tip necunoscut. Cand atingi un
rand manual intr-un generator, testeaza intai daca `calcul(..., {"RXX": val})` chiar il seteaza. d301 respinge tot
manual; d112/d406 n-au manual.

## Datorii/blocaje deschise (21 xfail; relevante D300/D301)
1. **9% deductibil auto | d300** (`test_datorie_d300_9pct_deductibil_auto`) - validatorul DUK instalat respinge R75.
2. **MF metode degresiva/accelerata** (`test_datorie_mf_metode_amortizare`) - subsistem mijloace fixe.
3. Restul: `git grep "@pytest.mark.xfail" core/test_datorie.py`.

## Observatii deschise (raportate, NEreparate - decizia lui Costin)
- **Gap pct.4<->pct.8** = INCHIS acum (pct.9 WIP). Nu mai e deschis.
- **Drift push-per-pas CLAUDE.md 328/358** = REZOLVAT (aliniat la commit local + backup). Nu mai e deschis.
- Ambele erau in raportul campaniei de siguranta; le-am inchis in aceasta sesiune.

## Registre atinse (ultimele sesiuni, dcbdc65 -> da89b60)
- Cod: d101/d112/d205/d300/d390/d394 + testele. CLAUDE.md (§2.3 pct.7/8/9, aliniere 328/358), DECIZII.md
  (14 clustere + gard clasa + decizia c siguranta), GARZI.md (contor 1294->1322 pe interval), TESTE.md (secventa
  ...->46). Ramura de siguranta backup/lant-20260803 pe remote.

## Cum continui (sesiune noua)
1. Citeste CLAUDE.md §2.2 (raport) + §2.3 (lant, incl. pct.7/8/9 noi). Ruleaza `agenda.urmator_cluster()`.
2. Verifica temeiul la sursa (CF art.290 + OPANAF 592/2016 pt d301). Increment rosu->verde->mutatie, commit local.
3. La inchidere: gard (§9) + registre. La finalul rularii: push de siguranta pe backup/lant-<data> (§2.3 pct.8) +
   raport care se incheie cu `SALVAT: <hash> + BACKUP: <ramura> — <n> commituri`.
4. Limita: max 6 clustere/rulare. Sterge PREDARE_LANT.md dupa ce ai reluat lantul.
