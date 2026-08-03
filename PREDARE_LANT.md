# PREDARE LANT — context proaspat (03.08.2026, oprire pct.6 dupa 12 clustere)

Oprire la §2.3 pct.6 (context se apropie efectiv de epuizare), la granita curata de commit - NU premature.
12 clustere inchise + decizia de produs cote 9%/5% implementata + limita de 6/rulare eliminata (CLAUDE.md).
S-au acumulat mai multe decizii care cer input de la Costin (vezi sectiunea dedicata).

## Munca in DOUA locuri (§2.3 pct.8)
- **Server:** ultimul cluster = `f34318a`; peste el commitul de PREDARE. tree curat.
- **Remote:** `backup/lant-20260803` = HEAD (push la finalul rularii; confirma cu git ls-remote).
- **Push pe main: NU** (decizia lui Costin).

## Poarta (VERDE)
`venv/bin/pytest` = 1320 passed / 2 skipped / 24 xfailed (PYTEST_EC=0); verificator TOTAL 0.
SOLD DATORII: 21 xfail la intrare -> 24 la iesire (+3 noi: gaze naturale d394, diurna istoric, micro sponsorizare).

## Unde se lucreaza
`ssh iconta`, `~/iconta_nou`, branch main. venv/bin/... Full-suite ~110s (timeout 200000+; NU de doua ori).
Editari prin python: `ssh iconta 'cd ~/iconta_nou && python3 -' <<'PY' ... PY` (ghilimele SIMPLE la ssh, heredoc
pe stdin; backtick-urile intr-un arg ssh dublu-quotat sunt mancate de shell-ul local). `/tmp/cf.txt` = codul fiscal.
ATENTIE (lectie 03.08): la un cluster care adauga un FISIER de test NOU, bifarea Inventar A merge in commit SEPARAT
dupa ce fisierul intra in git (gardul anti-stale test_agenda citeste git HEAD, nu working tree).

## Inchise in aceasta rulare (cc30f3b -> f34318a), 12 clustere
1. baza=val x curs|d301 — FIX fabricare tacita curs=1 (CF art.290).
2. cota TVA|d301 — FIX cota redusa period-aware (CF art.291 + Legea 141/2025).
3. tipuri operatiune IC|d390 — VERIFICAT OPANAF 705/2020 + gard-pin.
4. rotunjire A91b|d390 — VERIFICAT ROUND_HALF_UP + proba.
5. reclasificari manuale|d390 — FIX read-side valideaza direciția (fail-loud).
6. exigibilitate/prag|d390 — VERIFICAT incadrare pe data_emitere + gard temporal.
7. cote acceptate|d394 — VERIFICAT + gard cross-modul common.COTE subseteaza d394.COTE.
8. taxare inversa|d394 — 11/12 conform; DATORIE lit.l gaze naturale (codPR neconfirmat).
9. SourceDocuments|d406 — FIX TaxCode livrari period-aware.
10. plafon diurna|deconturi — calcul curent conform + DATORIE period-awareness istorica.
11. credit sponsorizare/D177|sponsorizari — profit conform; DATORIE micro + D177 decizie produs.
12. rezerva legala|motor — formula contabila conforma; deductibilitate fiscala art.26(1)a = decizie produs.
+ DECIZIE PRODUS cote 9%/5% IMPLEMENTATA (tva_redusa_9/_5 in common.COTE).
+ CLAUDE.md §2.3 pct.5: limita de 6 clustere/rulare ELIMINATA.

## Clusterul URMATOR (mecanic)
`agenda.urmator_cluster()` -> **`('zilieri (impozit+CAS)','contracte_speciale')`**, 34 ramase, 1 blocat.
- Zilieri (Legea 52/2011): impozit 10% pe remuneratie + posibil CAS/CASS. Verifica modulul contracte_speciale.

## DECIZII / INPUT CERUT DE LA COSTIN (acumulate in aceasta rulare)
1. **gaze naturale (D394 taxare inversa, art.331 alin.2 lit.l):** codPR-ul D394 nu e in sursele repo (Ghid 2016).
   Nevoie: structura/ghid D394 ANAF post-2021. Datorie xfail test_datorie_gaze_naturale_...
2. **cote reduse 9%/5% - data de INCEPUT:** ancorata la 2017-01-01 (REDARE); codul consolidat nu pastreaza nota
   istorica. De reconfirmat la MO pentru perioade < 2017.
3. **diurna - valorile istorice HG 714/2018 (+ succesoare) + data trecerii la 23 lei** + nomenclator HG 518/1995
   (extern). Datorie xfail test_datorie_plafon_diurna_...
4. **micro sponsorizare - textul istoric art.56 alin.1^5** (abrogat, rata 20% + start neconsolidate). Datorie xfail.
5. **D177 formular** (redirectionare sponsorizare) - ABSENT ca formular (doar scalar). Construire = scop nou.
6. **rezerva legala - deductibilitatea fiscala CF art.26(1)a** (add-back cheltuiala impozit + legare in d101 P6) -
   schimba declaratia de profit = decizie de produs. Regula E disponibila, doar de construit.
7. **D390 plafon "ziua 15"** (exigibilitate intarziata art.284) - cere camp data_faptului_generator in schema facturi.

## Observatii deschise (NEreparate)
- d390 tara XI (Irlanda de Nord) in cod dar nu in Nomenclator Tari 2020 - tine de clusterul "nomenclator tari|d390".
- d406: Payments gol (datorie pe date), TaxCode achizitii grosier, adresa placeholder, lipsa golden pe _factura_xml.
- credit sponsorizare endpoint main.py:7853 apeleaza fara la_data (neperiodizat); d101 nu cheama motorul.

## Registre atinse (cc30f3b -> f34318a)
- Cod: d301.py, d301_operatiuni_api.py, common.py, expirare_cote.py, d390.py, d390_clasificare_api.py,
  d406.py, deconturi.py (doar test), tenant_template.sql, CLAUDE.md (§2.3 pct.5).
- Teste noi: test_d301_curs.py, test_d301_cota.py, test_deconturi.py; +functii in test_d390/d406/d394/datorie/
  operatiuni_speciale/pull_declaratii.
- Registre: DECIZII.md, GARZI.md, TESTE.md (Inventar A 12 randuri bifate; secventa 46->34). backup/lant-20260803.

## Cum continui (sesiune noua)
1. Ritual §5: pwd/hostname/git log; git rev-parse --is-inside-work-tree; ./venv/bin/python -m core.agenda.
2. agenda.urmator_cluster() -> zilieri | contracte_speciale. Verifica temeiul (Legea 52/2011 + CF art.76/137).
3. Increment rosu->verde->mutatie, commit local. La inchidere: gard (§9) + registre + bifare Inventar A +
   regenerare secventa + nota narativa. FISIER de test NOU -> bifa in commit separat.
4. La finalul rularii: push de siguranta pe backup/lant-<data> (§2.3 pct.8).
5. Fara limita de clustere (pct.5 eliminat) - continua pana la un criteriu de oprire. Sterge PREDARE_LANT.md dupa reluare.
