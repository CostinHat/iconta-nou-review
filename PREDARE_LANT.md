# PREDARE LANT — context proaspat (03.08.2026, oprire pct.6 dupa 7 clustere in aceasta rulare)

Oprire la §2.3 pct.6 (context substantial). Rulare precedenta: A1 + campania B + zilieri. Rulare aceasta: 7 clustere.

## Munca in DOUA locuri (§2.3 pct.8)
- Server: ultimul cluster = `f26be10`; peste el commitul de PREDARE. tree curat.
- Remote: `backup/lant-20260803` = HEAD (push la finalul rularii; confirma cu git ls-remote).
- Push pe main: NU.

## Poarta (VERDE)
`venv/bin/pytest` = 1325 passed / 2 skipped / 21 xfailed (EC=0); verificator TOTAL 0.

## Unde se lucreaza
`ssh iconta`, `~/iconta_nou`, main. venv/bin/... Full-suite ~115s (timeout 200000+; NU de doua ori; commit-urile
d100 depasesc 2 min -> foloseste run_in_background la commit). Editari prin python:
`ssh iconta 'cd ~/iconta_nou && python3 -' <<'PY' ... PY` (ghilimele SIMPLE la ssh; in SQL scrie '1012%%' direct,
NU escapa la '''; comentariile din cod pastreaza prefixul #). `/tmp/cf.txt` = codul fiscal. FISIER de test NOU ->
bifa Inventar A in commit SEPARAT (gard anti-stale). Cand referi in Inventar A o functie dintr-un fisier, adaug-o
la coloana fisiere (altfel gardul anti-stale n-o gaseste).

## Inchise in aceasta rulare (0f8aaed -> f26be10)
1. regim marja second-hand|tva_marja - VERIFICAT (suta marita cota/(100+cota), CF art.312 alin.4) + gard golden.
2. regim marja turism|tva_marja_turism - VERIFICAT (suta marita + scutire non-UE proportionala, art.311) + gard.
3. impozit dividend|decontari_asociati - FIX cote istorice: 10% (petic) era gresit -> 5% (2016-2022), 8% (2023-2025,
   OG 16/2022), 16% (2026, Legea 141/2025). Verificat la sursa (anaf_surse/). Teste care cimentau 10% actualizate.
4. contributii PFA|d212 - VERIFICAT calcul conform (CAS art.148, CASS art.170 alin.1 liniar) + FIX citare temei
   (plafon 72 sm: Legea 141/2025 -> Legea 239/2025 art.XII pct.19). Obs: calea 2026 dormanta (poarta an=2025).
5. nomenclator cod_oblig<->cod_bugetar|d100 - FIX cont bugetar obsolet 20470101 -> 5503XXXXXX (d100_struct:562,
   coroborat d101/d112); gard anti-drop pe cod nemapat. Sursa unica (d710 importa din d100).
6. cota micro 121 (flag)|d100 - VERIFICAT (121->cota=1, 103->fara cota) + gard bidirectional in build_xml.
7. checksum totalPlata_A (R11b)|d100 - VERIFICAT valoarea emisa (2x sum, DUK R11b) + FIX divergenta res.total_plata_a
   (1x) vs emis (2x) -> aliniat la sursa unica (res.total_plata_a=checksum, emis de build_xml, ca celelalte declaratii).

## Clusterul URMATOR (mecanic)
`agenda.urmator_cluster()` -> **`('scadente/nr_evidenta','d100')`**, 26 ramase, 1 blocat.

## CAMPANIA DATORII - ce RAMANE (blocaje motivate, DECIZII 03.08)
A2 (D390 ziua-15 schema), A3 (D177 formular), C1/C2 (tichete cresa/culturale research MO), C3 (amortizare MF xfail),
C4 (D112 sectiunea 8.3), C5 (migrare tichete culturale). A1 LIVRAT, C6 inchis, B completa.

## Datorii xfail ramase (21) - motivele in test_datorie.py
Pre-existente in afara campaniei + C3 (mf_metode_amortizare).

## Registre atinse (0f8aaed -> f26be10)
Cod: tva_marja.py, tva_marja_turism.py, common.py, d212_engine.py, d100.py, d101/d205/decontari_asociati/lichidare
(teste dividend). anaf_surse/: impozit_dividende_istoric_cote.txt (sha256). DECIZII/GARZI/TESTE la zi.

## Cum continui (sesiune noua)
1. Ritual §5. agenda.urmator_cluster() -> scadente/nr_evidenta | d100 (scadenta platii D100 + nr_evidenta 23 poz;
   deja exista teste nr_evid - probabil verificare). Verifica temeiul.
2. Increment rosu->verde->mutatie, commit local (background la d100). La inchidere: gard (§9) + registre + bifare
   Inventar A + regenerare secventa + nota narativa.
3. Fara limita de clustere (pct.5 eliminat) - continua pana la un criteriu de oprire.
4. La finalul rularii: push de siguranta pe backup/lant-<data>. Sterge PREDARE_LANT.md dupa reluare.
