# PREDARE LANT — context proaspat (03.08.2026, oprire pct.6 dupa A1 + campania B + 14 clustere)

Oprire la §2.3 pct.6 (context se apropie efectiv de epuizare). A1 (prioritatea) LIVRAT; campania B (temeiuri) COMPLETA.

## Munca in DOUA locuri (§2.3 pct.8)
- Server: ultimul cluster = `d738ba9`; peste el commitul de PREDARE. tree curat.
- Remote: `backup/lant-20260803` = HEAD (push la finalul rularii; confirma cu git ls-remote).
- Push pe main: NU (decizia lui Costin).

## Poarta (VERDE)
`venv/bin/pytest` = 1322 passed / 2 skipped / 21 xfailed (EC=0); verificator TOTAL 0. collect: 1343.

## Unde se lucreaza
`ssh iconta`, `~/iconta_nou`, main. venv/bin/... Full-suite ~110s (timeout 200000+; NU de doua ori). Editari prin
python: `ssh iconta 'cd ~/iconta_nou && python3 -' <<'PY' ... PY` (ghilimele SIMPLE la ssh; NU escapa ghilimelele
SQL - scrie '1012%%' direct, nu '''1012%%''' - lectie A1). `/tmp/cf.txt` = codul fiscal. FISIER de test NOU ->
bifa Inventar A in commit SEPARAT (gardul anti-stale citeste git HEAD).

## LIVRAT in aceasta rulare (peste ce era)
- **A1 (rezerva legala fiscala art.26(1)a in d101)** IMPLEMENTAT (43fe525): P13 auto = min(5% x (P7+691); 20% x
  capital 1012 - rezerva 1061), sursat din contabilitate; dependenta circulara rezolvata (baza = cifra contabila
  691, nu impozitul D101). Gard + proba pe date reale. DUK D101 = GRI (validator neinstalat).
- **Campania B (temeiuri istorice) COMPLETA** (6675f19): cote reduse 2016, diurna 20/23, micro 20% 2019-2023, gaze
  codPR=36. 3 xfail inchise; 5 fisiere anaf_surse/ cu sha256.
- **zilieri | contracte_speciale** (d738ba9): FIX CAS period-aware (CAS pe zilieri doar de la 01.05.2019 OUG 26/2019).

## Clusterul URMATOR (mecanic)
`agenda.urmator_cluster()` -> **`('regim marja second-hand','tva_marja')`**, 33 ramase, 1 blocat.

## CAMPANIA DATORII - ce RAMANE (blocaje motivate, DECIZII 03.08)
- A2. D390 "ziua 15" (schema data_faptului_generator + migrare tenanti) - context propriu (schema pe date reale).
- A3. D177 formular - structura oficiala de descarcat intai de la ANAF (nu inventa campuri).
- C1/C2. Tichete cresa 740 / culturale 240-470 - research la MO (metoda B dovedita).
- C3. Metode amortizare MF (xfail test_datorie_mf_metode_amortizare) - subsistem de construit.
- C4. D112 sectiunea 8.3 avantaje toate biletele - implementare generator D112.
- C5. Migrare tichete culturale pe tenanti - deployment (precautii ca A2).
- C6. Tara XI - INCHIS (verificat corect, VIES post-Brexit).

## Datorii xfail ramase (21) - motivele in test_datorie.py
Pre-existente in afara campaniei (trunchiere d205/d390/d710, d101_imca, d300_9pct/exigibilitate/reverse-charge-MO,
concedii medicale cm_*, deduceri personale, tichete masa, probe DUK/PDF, verificator) + C3 (mf_metode_amortizare).

## Registre atinse
Cod: d101.py (A1), common.py/deconturi.py/sponsorizari.py/taxare_inversa.py/d394.py (campania B),
contracte_speciale.py (zilieri). Teste: +functii in test_d101/pull_declaratii/versionare_formule/d394; sterse 3
xfail (gaze/diurna/micro). anaf_surse/: 5 fisiere noi cu sha256. DECIZII/GARZI/TESTE la zi.

## Cum continui (sesiune noua)
1. Ritual §5. agenda.urmator_cluster() -> regim marja second-hand | tva_marja (CF art.312-315 regim marja bunuri
   second-hand: TVA pe marja, nu pe pret). Verifica temeiul la sursa.
2. Increment rosu->verde->mutatie, commit local. La inchidere: gard (§9) + registre + bifare Inventar A + regenerare
   secventa + nota narativa.
3. Fara limita de clustere (pct.5 eliminat) - continua pana la un criteriu de oprire.
4. La finalul rularii: push de siguranta pe backup/lant-<data>. Sterge PREDARE_LANT.md dupa reluare.
