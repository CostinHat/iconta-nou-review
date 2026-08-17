Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — audit vizual tenant_001 (Panificatie Salarii Speciale SRL, cabinet 1968); threads 1+3 livrate, thread 2 front cercetat (REVENIT)

## REPORNIRE (comanda exacta, gata de dat)
Continua auditul vizual tenant_001 cap-coada cu Playwright (captura PRIVITA + axe-core + mobil pe fiecare ecran
atins - Regula 14 integral), REPARAND ce gasesti; ce gasesti pe o firma cauta pe toate (Regula 13). Valorile
fiscale se verifica la sursa (anaf_surse/*_struct + XSD + DUK), NU se cer de la Costin. Fiecare gard nou: mutatie
probata RED pe cod vechi, prin rulare. DS inainte de orice cod de interfata, cu capitolul citat.
PUNCTUL LA CARE AM RAMAS: livrat thread 1 (COR/IBAN). Thread 2 (D112 podea part-time) CERCETAT temeinic dar REVENIT
(ambiguitate contestata, vezi FRONT #1 - nu e defect de calcul clar, ci interpretare pe care codebase-ul insusi n-a
rezolvat-o). RAMASE, in ordinea comenzii:
- **THREAD 3 - declarant fabricat**: LIVRAT (2 clustere, vezi LIVRAT). declarant obligatoriu in profil (7aef45e)
  + avertizat in toate declaratiile la generare (ae5bced).
- **THREAD 4 - scan toate selecturile nullable (Regula 13)**: NEFACUT. Tiparul "select obligatoriu fara optiune-
  placeholder -> prima optiune reala apare aleasa" - reparat pe cele 3 din Date firma (tura precedenta) + placeholder
  pe date_firma.js. De cautat in TOATE ecranele (operatiuni_ecran.js, configurare emitere, salariati etc.).
- **THREAD 2 - D112 podea part-time**: vezi FRONT #1 (cercetat, revenit).
- **THREAD 5 - salariati in adancime**: PARTIAL (provocat SEPA/REGES). RAMAS: Fluturas, Concediu, Adeverinta,
  Pontaj, Incetare, "+ Salariat nou" cu campuri goale - provoaca fiecare blocaj, citeste mesajul.
- **THREAD 6 - declaratiile ramase la XML+DUK**: D100, D300, D394, Bilant S1005, D205 (dus doar D112). Pasul 3 al
  wizardului (coada) NEATINS pe nicio declaratie.
- **THREAD 7 - cele 9-10 straturi migrare cap-coada**: doar meniul Import + stratul Salariati (model+parser reparat)
  privite. Restul straturilor: import->preview->salvare->confirmare->ecran, cu blocaje provocate la preview.

## FOUR-WAY (de confirmat de urmatoarea tura)
Comituri livrate: a62f46b (IBAN+SEPA/REGES), 7aef45e (declarant obligatoriu profil), ae5bced (declarant avertizat
generatoare). Plus commit registre+PREDARE (aceasta predare). Toate prin poarta verde (post-commit publica origin/main
+ backup + restart automat). De confirmat HEAD=origin=backup=RUNNING. Thread 2 (D112 podea) REVENIT - NU e in niciun
commit; d112.py ramane pe `prag_pt = float(sm)` (HEAD).

## LIVRAT (clustere RED-probate + vizual/DUK)
1. **IBAN importabil la salariati + blocaje SEPA/REGES vizibile** (a62f46b). (a) Importul (stratul 4) NU aducea
   IBAN: parser+writer+model reparate (mapare, validare mod-97, INSERT cu COALESCE, model CSV cu cor,iban). COR
   era deja mapat. (b) Butoanele SEPA/"Raspunsuri REGES" dezactivate livrau motivul DOAR prin title (invizibil pe
   touch - Regula 14 addendum) -> motiv VIZIBIL prin .caseta-info (DS cap.5). Garzi test_salariati_import_iban +
   test_salariati_blocaj_vizibil (RED->GREEN). axe/mobil Stat plata: title_only STRICT 0; PRE-EXISTENT: contrast 19
   noduri, 160 tinte <44px.
2. **THREAD 3 - declarant obligatoriu in profil** (7aef45e). declarant_nume + declarant_functie in OBLIGATORII +
   ob:true in date_firma.js (se cere EXPLICIT, ca regim_fiscal; g9 verde). Gard test_declarant_oblig. Vizual: Nume
   declarant* + Functia declarantului* cu asterisc, Salvarea fara ele blocheaza; Prenume optional. axe/mobil Date
   firma: title_only STRICT 0; pre-existent contrast 17 noduri + 31 tinte <44px.
3. **THREAD 3 - declarant avertizat in toate declaratiile** (ae5bced). d100/d101/d205/d112/d300 + bilant emiteau
   "ADMINISTRATOR" fabricat TACIT cand declarantul lipsea (d301/d390 avertizau deja) -> aliniate toate la warn. XML
   NESCHIMBAT (amprenta/DUK neatinse). Gard test_declarant_warn (RED->GREEN, verifica toate 8). Behavioral D112:
   avertisment emis, XML tot ADMINISTRATOR.

## FRONTURI DESCHISE (gasite aceasta tura, NEREPARATE)
1. **THREAD 2 - podeaua part-time D112: 3 pozitii contradictorii, CERCETAT si REVENIT (nu comis)**. Atentionarea
   DUK din comanda (D112 06/2026 E4: SP1B4_1 B4_5P 4050 vs 3750) e reala. La sursa, podeaua de suprataxare part-time
   (art.146(5^6) CAS / art.168(6^1) CASS) e calculata in TREI locuri cu TREI valori:
   - salarizare.baza_podea (fluturas, net-pay): sm - facilitate LUNAR (3750 H1 / 4125 H2) - period-aware;
   - d112.pull:680 prag_pt + d112_reconciliere:182: sm INTEGRAL (fix 06.08, 4050 H1 / 4325 H2);
   - DUK (SP1B4_1) + structura ANAF (anaf_surse/d112_struct_anaf.txt: "sm=4050; sm=sm-300"): 3750 FIX pe tot 2026
     (referinta 1 ianuarie), verificat pe DUKIntegrator IUNIE si AUGUST (ambele cer 3750).
   DECIZIA 06.08 (sm integral=4050) e DELIBERATA, aparata cu art.LXVI (facilitatea = doar norma intreaga) in DOUA
   teste: test_pull_declaratii.py:634 (test_d112_part_time_baza_minima_salariul_minim_integral) SI
   test_d112_reconciliere.py:307. AM INCERCAT doua fix-uri (sm-fac lunar -> aliniat cu fluturas dar DUK inca
   atentioneaza H2; referinta-ianuarie 3750 -> DUK curat H1+H2 dar diverge de fluturas + contrazice cele 2 teste).
   AMBELE contrazic teste deliberate cu temei legal. NU e un defect de calcul CLAR, ci o interpretare pe care
   codebase-ul insusi n-a rezolvat-o (D112=4050 vs fluturas=sm-fac vs DUK=3750). REVENIT la HEAD; cere autoritate
   externa (ANAF/consultant) pe: (a) podeaua part-time e period-aware sau referinta-1-ian? (b) facilitatea (art.LXVI)
   reduce podeaua part-time sau doar norma intreaga? (c) de ce fluturas si D112 difera azi (baza_podea sm-fac vs
   prag_pt sm integral) - inconsistenta interna preexistenta de reconciliat. TOATA analiza + probele DUK sunt aici.
2. **E7 cod boala "17" in afara nomenclatorului D_9 (01-15)**: genereaza D112 pt tenant_001 septembrie CRAPA cu
   ValueError clar (cod 17 cardiovascular, seed CONCEDII). App-ul blocheaza CORECT cu mesaj spre ecranul Concedii
   medicale. De verificat la sursa: cod 17 e cod CM valid ce ar trebui mapat in D_9, sau seed-ul e gresit? (Regula 5.)
3. **FOLLOW-UP thread 3 (mic)**: DS cap.17 DEFAULT_FISCAL_TACIT (verificator .py+.js pe `x or "literal"`) NU prinde
   inca `declarant_* or "ADMINISTRATOR"` - de extins regula ca sa inchida mecanic clasa (azi inchisa de
   test_declarant_warn source-scan). d394 foloseste reprezentant/declarant fara "ADMINISTRATOR" (nu fabrica) - neatins.

## BACKLOG (mostenit, tot deschis)
Umbrire strat migrare (badge C3). Mesaj TVA semafor cu tip_decont + fara diacritice (common.py:57-58, gaura de gard
test_control_fiscal_diacritice). Tensiune semafor D100 micro pe zero. D406 SAF-T micro neplatitor. Constatari infra
vizuala (contrast, tinte <44px) - Costin da ordinea.
