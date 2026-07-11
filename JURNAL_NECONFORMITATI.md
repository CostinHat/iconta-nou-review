
## NC-22 (10.07.2026) — CAMP_DIALECT in rip_ecran.js
6 campuri construite ca <label>text<br>input (linii 61-70), in loc de structura
canonica .camp + .camp-eticheta (Design System v1.1, regula stabilita la #61).
Detectat mecanic de verificator (categorie noua CAMP_DIALECT). De migrat pe canonic.

## NC-23 (10.07.2026) — DIACRITICE in etichetele REGISTRU (operatiuni_ecran.js)
Etichetele afisate din configuratia REGISTRU (titluri operatiuni, etichete campuri,
optiuni select) sunt fara diacritice ("Suma incasata/platita", "Incasare de la client").
Incalca regula 6. Verificatorul nu le prinde: scaneaza doar linii cu </placeholder,
REGISTRU e configuratie pura. De reparat: diacritice in etichete + extindere detector.

## NC-24 (10.07.2026) — R4 nav.setInapoi: lista completa ecrane nemigrate
19 fisiere fara setInapoi (verificat grep -L): activitate_cabinet, admin_gratuite,
admin, admin_sanatate, asistenti, asistent, cabinet, capacitate, control,
etransport_ecran, login, produse_ecran, raporteaza, recomanda, rip_ecran, semafor,
termene, tipare, validat. operatiuni_ecran migrat acum (patch 61b), scos din lista.
De migrat R4 (Sonnet), conform planului Faza B.

## NC-25 (10.07.2026) — Operatiuni speciale: test functional "Genereaza nota" neexecutat
Patch-urile 61a-61d (aliniere campuri + nav.mergi cu scroll memorat + fix corp stale
+ fix .closest(".camp")) verificate sintactic si vizual (navigare stabila, scroll
memorat). Ramane de rulat: generare efectiva a unei note (ex. TVA la incasare) si
verificare ciorna in Registru jurnal — pt validarea end-to-end a fix-ului closest.

## Test #62 (10.07.2026) — Amortizare MF liniara: PASS
Verificat pe KAI PERFORMANCE (tenant_002), luna 07/2026: 3 linii generate
(Laptop Dell 166.67, Dacia Duster 1250.00, Laptop test 166.67), total 1583.34 lei.
Aritmetica validata manual (formula liniara, start luna urmatoare PIF, stop la DNF)
- coincide exact cu rezultatul din baza. ERP test corect exclus (PIF in luna curenta).
Cont 6811/2813 monografie corecta.
JURNAL_OKcat

## Test #64 (10.07.2026) — Stocuri: fise CV + CMP: PASS
11/11 teste unitare pytest (core/test_stocuri_cv.py). Verificare end-to-end pe
tenant_002 (KAI), 2 articole, 5 miscari: CMP recalculat corect la intrare (5.00,
7.00 lei), neschimbat la iesiri succesive, sold cantitate/valoare exact la fiecare
linie. Surse diverse (inventar, reteta) alimenteaza corect aceeasi fisa - integrare
reala confirmata, nu doar motor izolat.

## Test #65 (10.07.2026) — Operatiuni speciale (30, ecran generic): PASS
Testat end-to-end operatiunea "sponsorizare" (POST /tenants/2/nota-sponsorizare):
1000 lei mod contract -> nota 6582=401 corecta, status ciorna, descriere pastrata.
Numar gol la generare e comportament normal (populat abia la validare); Registru
jurnal are deja fallback descriere||numar||#id (firme.js:1172), afisare corecta.
Nota de test stearsa dupa verificare. Include si fix-urile de aliniere/navigare
din aceasta sesiune (patch 61a-61d): structura .camp, nav.mergi cu scroll memorat.

## Test #66 (10.07.2026) — Perioada blocata: FAIL initial -> PASS dupa reparatie
Bug real gasit: doar 3 din 39 puncte de inserare in {schema}.inregistrari verificau
perioada blocata (doar editare/stergere/validare nota manuala). Toate cele 30 module
+ crearea de nota noua + amortizarea ocoleau blocarea complet (testat empiric:
amortizare generata cu succes pe luna blocata, status validata direct).
REPARATIE: trigger SQL (verifica_perioada_blocata) pe INSERT/UPDATE/DELETE, aplicat
pe toate cele 6 scheme tenant existente + tenant_template.sql (tenanti noi). Exception
handler specific (nu Exception generic - doar traduce PERIOADA_BLOCATA) -> 423 curat.
Testat: amortizare pe luna blocata->423, luna libera->200 (flux normal nestricat),
creare nota manuala pe luna blocata->423 (cazul gaurii reale, acum acoperit).

## Test #67 (10.07.2026) — PFA partida simpla + RIP: PASS
Motor complet testat end-to-end pe AMZUICĂ (tenant_004, id=13): adaugare incasare
5000+plata deductibila 800 (sold 4200 exact), validare, fisa D212 pe 2025 cu date
reale (venit 80000, cheltuiala 15000): CAS 12150 (baza fixa 12x4050, 25%), CASS
6500 (baza=venit net, regula 2025), impozit 4635 (10%), total 23285 - aritmetica
verificata manual, exacta. Motorul refuza corect calculul pt alt an decat 2025
(plafoane neverificate) - comportament defensiv corect, nu bug.
Gaura similara cu #66 gasita si reparata: rip_operatiuni nu avea trigger perioada
blocata. Extins acelasi tipar (trigger pe data_operatiune) pe toate 6 scheme +
tenant_template.sql. Testat: 423 pe luna blocata, 200 pe luna libera.

## Test #68 (10.07.2026) — Salariat nou + contract: FAIL -> construit + PASS
Gaura reala: UI de adaugare salariat individual lipsea complet (doar import bulk
migrare exista). Backend (POST /tenants/{id}/salariati) era gata dar neapelat.
Construit ecran nou "Salariat nou" in ecranSalariati (firme.js), structura canonica
.camp + grila-campuri (identic tipar #61), nav.mergi pentru scroll.

Bug de sistem critic gasit in constructie: salariati_api.py folosea coloana
tip_norma (text) peste tot, dar DB are part_time (boolean) - redenumita intr-o
migrare anterioara (03.07.2026) fara actualizarea codului. TOATA lista de
salariati era stricata (500) pentru orice tenant - bug preexistent, invizibil
pana acum (nimeni nu testase GET /salariati). Reparat: traducere API<->DB la
granita (tip_norma<->part_time), contract API neschimbat. Confirmat: KAI avea
deja 2 salariati (Ionescu Maria, Popescu Ion) ascunsi de eroare, acum vizibili.

2 bug-uri UX gasite si reparate live cu Costin: (1) Ore/zi permitea valori
negative (fara min pe input number) - fix min="0" pe toate campurile numerice.
(2) step=0.01 aplicat uniform gresit (bani vs ore vs persoane) - diferentiat:
ore_zi=0.5, persoane_intretinere=1, salariu_brut=0.01. (3) Dupa salvare iesea
din formular direct la lista (nav.inapoi() inchidea toata fereastra) - fix:
ramane pe formular golit cu mesaj confirmare + buton separat "Gata, inapoi la
lista" (nav.inapoiPas(), nu nav.inapoi()).

## Test #69 (10.07.2026) — Stat de plata: calcul brut-net: PARTIAL (confirmat)
Motor calcul_salariu() verificat corect pe cazul de baza (normă întreagă, brut peste
minim, fara persoane): aritmetica exacta (Popescu Ion brut 4500 -> CAS 1125, CASS 450,
impozit 212.49, net 2712.51 - identic UI si rulare directa a functiei).

BUG FISCAL confirmat la sursa oficiala (legislatie.just.ro + CECCAR, OUG 89/2025 art.
III): facilitatea 200/300 lei cere CUMULATIV: (a) norma intreaga, (b) functie de baza,
(c) salariul de baza EGAL cu minimul (nu doar <=), (d) venit brut total (fara tichete)
<= 4300 lei S1 / 4600 lei S2 2026. Codul actual (core/salarizare.py, calcul_salariu)
aplica facilitatea oricui are brut<=sm, IGNORAND toate cele 4 conditii - orice norma
partiala cu brut mic primeste incorect facilitatea (confirmat empiric: Ionescu Maria,
part-time 4h/zi, brut 1956.52, a primit facilitate=200 incorect).

Gasit si un mecanism SEPARAT, mai vechi (Cod fiscal, podea CAS/CASS la nivelul
salariului minim pentru norma partiala) mentionat de avocatnet.ro dar neverificat
inca la sursa oficiala si neimplementat deloc in motor.

DECIZIE: fix marcat ca "logica fiscala noua" (regula model: Opus 4.8, nu Sonnet).
De facut sesiunea urmatoare cu Opus: (1) adauga parametri norma_intreaga + venit_brut_total
in calcul_salariu, conditie eligibilitate completa (a-d), (2) cerceteaza la sursa oficiala
mecanismul podea CAS/CASS norma partiala, (3) verifica toate D112-urile deja generate
pe clienti reali pentru norma partiala - posibil facilitate aplicata gresit retroactiv.

## Completare #69 — locatie exacta pt sesiunea Opus
core/stat_plata_api.py: part_time CITIT din DB (linia 27, unpacking randuri) dar
NICIODATA transmis catre salarizare.calcul_salariu() (liniile 36 si 80 - apelat doar
cu persoane=pers, la_data=ref, fara part_time/sub_26/copii_scoala/functie_baza).
De asemenea zero verificare venit_brut_total <= plafon (4300/4600) inainte de a
acorda facilitatea. Ambele apeluri (linia 36 traseu normal, linia 80 alt traseu -
probabil fisa individuala) trebuie corectate identic.

## NC-26 (10.07.2026) — AUDIT FISCAL LA SURSA cerut, nefacut inca pe scara larga
Azi (10.07) s-a verificat la sursa oficiala (legislatie.just.ro + CECCAR) DOAR
facilitatea 200 lei din calcul_salariu (#69) - a iesit bug real. Restul motorului
de salarizare (deducere personala, plafoane, CAS/CASS, art. 77 CF) NU a fost
reverificat azi, desi a fost testat doar aritmetic-intern (cod se leaga cu el
insusi, nu neaparat cu legea curenta). Similar #62 (amortizare, DNF vs Catalogul
HG 2139/2004), #65 (credit fiscal sponsorizare D177), #67 (regula "12x salariul
minim" pt CAS PFA, valabila 2025 - de reconfirmat neschimbata).

DE FACUT: audit fiscal dedicat la sursa oficiala (Opus, model_selection: logica
fiscala/verificare sursa) pe intreg core/salarizare.py, nu doar facilitatea 200 lei:
- deducere_personala(): plafoane si procente (art. 77 CF) - sursa curenta 2026
- CAS/CASS/impozit cote - confirmate deja general (25%/10%/10%) dar verifica
  praguri si exceptii (motiv_exceptare, scutit_contrib_minim)
- CAM 2.25% - baza de calcul corecta (brut intreg, fara facilitate - de confirmat)
- amortizare: DNF-urile din configurarea MF vs Catalogul mijloacelor fixe actual
- sponsorizare: formula credit fiscal D177 la sursa
- PFA/RIP: plafoane D212 2025 (CAS baza fixa 12x minim) - valabilitate neschimbata
De facut inainte de a declara oricare din #62/65/67/68/69 "PASS fiscal complet" -
in prezent sunt doar "PASS aritmetic intern".

## Test #69 (11.07.2026) — Stat de plata brut-net: PARTIAL -> PASS (2 bug-uri fiscale reparate)
Sesiune Opus, verificare la sursa oficiala (legislatie.just.ro + CECCAR + mfinante.gov.ro):

BUG 1 (facilitate acordata gresit) - REPARAT: OUG 89/2025 art.III cere CUMULATIV:
norma intreaga + functie baza + brut EXACT=salariul minim + venit brut total<=plafon
(4300 S1/4600 S2). Cod vechi: doar "b<=sm". Adaugat cota noua plafon_facilitate_salariu_minim
(common.py) + conditii complete in calcul_salariu. Part-time exclus explicit de la facilitate.

BUG 2 (suprataxare part-time lipsa) - IMPLEMENTAT: art.146 alin.5^7 Cod fiscal - pt
part-time cu brut<(minim-facilitate), angajatorul suporta CAS/CASS suplimentar pe
diferenta pana la baza-podea (4125 in S2). Retinerea angajatului ramane pe venit real.
Monografie: 6451=4315 (CAS unitate) + 6453=4316 (CASS unitate), conditionate. Exceptii:
elev/student<26, pensionar, multi-contract (param exceptat_suprataxare).

Verificat end-to-end pe KAI (an 2026 luna 8): Ionescu Maria (part-time 2500) - suprataxa
cas 406.25 + cass 162.50, cost angajator 3125 (era subevaluat cu ~569 lei/luna inainte).
Popescu/Georgescu (norma intreaga) neafectati. 6 cazuri de test unitare verificate manual.

Semnatura calcul_salariu extinsa append-only (norma_intreaga=True default) - apelantii
existenti (d112.py, stat_plata vechi) merg neschimbat.

RAMAS PE BACKLOG (NC-27): D112 pentru part-time - declararea/plata catre buget se face
la baza-podea intreaga (nu doar diferenta pe cheltuieli). d112.py:323 apeleaza cu
norma_intreaga=True default - de verificat si corectat separat pt part-time. Plus:
verificare retroactiva D112-uri deja depuse pt part-time (CAS/CASS subevaluat).

## Test #70 (11.07.2026) — Deducere personala + suplimentara: PASS (fix rotunjire)
Audit complet la sursa oficiala (art.77 Cod fiscal - Lege5/Ordonanta 16/2022 + SD Worx):
TOATE procentele si pragurile CORECTE: 20% baza, +5%/persoana (max 4), 15% tineri<26,
100 lei/copil scoala, plafon minim+2000, degresie -0.5%/50 lei, conditie tineri (brut>2000).

BUG confirmat si reparat: deducerea NU era rotunjita la 10 lei in sus. Legea (art.77 +
SD Worx) cere rotunjire la 10 lei in favoarea contribuabilului. Cod vechi intorcea total
cu 2 zecimale -> impozit usor supraevaluat sistematic la orice salariat cu deducere
degresiva. Ex: brut 4500 -> deducere 800.13 (gresit) vs 810 (corect), impozit -0.99 lei,
net +0.99 lei in favoarea salariatului. Rotunjirea aplicata la TOTAL (art.77 alin.2:
deducerea = baza+suplimentara ca intreg), o singura data.

Verificat end-to-end pe KAI (luna 8): deduceri acum multipli de 10 (Georgescu 160,
Ionescu 1090, Popescu 810), impozite scazute corect. Aritmetica validata manual pe
6 cazuri (minim, degresie, tineri, copii, peste plafon).

## Test #71 (11.07.2026) — Facilitate 200 lei S2 2026: PASS
Acoperit de fix-ul #69 (conditii cumulative facilitate). Verificat explicit pe cazul S2:
- S1 (martie, minim 4050): facilitate 300 corect
- S2 (august, minim 4325): facilitate 200 corect (tranzitia 300->200 pe data functioneaza)
- plafon S2: venit total 4650>4600 -> facilitate 0; venit 4600 exact -> facilitate 200 (<=)
Tranzitia semestriala gestionata de cotele datate, plafon corect la granita.

## Test #72 (11.07.2026) — Concediu medical coduri + procente: PARTIAL (split reparat)
Sesiune Opus, verificare la sursa (OUG 158/2005 + OUG 91/2025 + Legea 64/2026 +
Ordinul 506/1030/2026, textul oficial cnas.ro art.78^4). CM e BACKEND-ONLY (endpoint
main.py:5130 + motor calcul_cm, ZERO UI inca).

CORECTE la sursa: procente cod 01 (55/65/75 progresiv), maternitate 85%, coduri 100%,
perioada diminuarii (01.02.2026-31.12.2027), regula "o data per episod".

BUG SPLIT reparat: zile_ang = min(zile_platite, max(5-diminuare,0)) dadea 4 zile
angajatorului cand diminuare=1. Oficial: angajatorul suporta zilele 2-6 = 5 zile
lucratoare PLATITE, FNUASS din ziua 7. Prima zi diminuata e neplatita, NU reduce
plafonul de 5. Impact real: dosarele de recuperare CNAS erau respinse (alocare
eronata perioada angajator). Reparat: zile_ang = min(zile_platite, 5). Verificat 5 cazuri.

RAMAS PARTIAL (piesa dedicata Opus - aliniere nomenclator CM la CNAS inainte de fix):
1. Nomenclatorul iConta (51=izolare, 06=urgente) DIFERA de cel oficial CNAS
   (07=carantina/izolare, 14=oncologic/neoplazii, 12/13/14=PNS). De aliniat intai.
2. Excepatii diminuare gresite (dupa nomenclatorul corect): cod 06 (urgente) exceptat
   gresit - NU e in lista oficiala; cod 14 (oncologic) LIPSESTE din exceptii - ar
   trebui adaugat. Lista oficiala exceptii (art.78^4, de la 01.06.2026): maternitate
   (c), oncologic (d1), risc maternal (e), PNS (12/13/14), spitalizare, +accidente
   munca (L346/2002) + izolare (L136/2020).

## Test #73 (11.07.2026) — Part-time: PASS
Verificare dedicata la sursa (art.146 Cod fiscal + art.77 + Pluxee/zarinacrm). Acoperit
in mare de fix-ul #69, verificat explicit pe 6 colturi neatestate:
- PT cu persoane intretinere: deducere pe VENIT REAL (nu podea) - confirmat corect la
  sursa (Pluxee: deducerea part-time proportional cu venitul brut real)
- PT sub 26 exceptat: deducere tineri + fara suprataxare - corect
- granita EXACT la podea 4125: fara suprataxare (corect, nu se suprataxeaza la egalitate)
- PT peste podea (4200): fara facilitate, fara suprataxa - corect
- pensionar exceptat: suprataxa 0 - corect
Aritmetica validata manual pe toate cazurile.

LIMITARE CUNOSCUTA (notata, nu bug): deducerea NU se acorda la part-time care nu e
functia de baza (al doilea job) - codul are param functie_baza, dar stat_plata trateaza
toti salariatii ca functie de baza implicit. Rezonabil pt firme mici, de rafinat pt
multi-contract (impreuna cu exceptat_suprataxare, care necesita si el declaratie).

## Test #74 (11.07.2026) — Fluturasi PDF: PASS
Fluturasul afiseaza corect perspectiva ANGAJATULUI (brut, facilitate, CAS, CASS,
deducere, impozit, net) - suprataxa part-time NU apare in retineri (corect, e cost
angajator, nu afecteaza netul salariatului). Costul total angajator (jos) include deja
suprataxa via calc['cost_angajator'] (fix #69). Imbunatatire: cand exista suprataxa,
nota de cost o mentioneaza explicit (transparenta - altfel apareau bani "din senin").
Bug prins in constructie: _dec nu era importat in stat_plata_api - inlocuit cu float.
Verificat end-to-end: PDF valid generat pt Ionescu (PT, "suprataxa part-time 568,75 lei"
in cost) si Popescu (NI, fara mentiune). Ambele HTTP 200, PDF-uri valide.

## Test #75 (11.07.2026) — Contracte speciale (zilieri, cenzori, mandat): PASS
Verificare la sursa (Legea 52/2011 + art.76(2) lit.r/g/i Cod fiscal + ANAF regim_zilieri
+ infotva 2025/2026). Motor contracte_speciale.py corect pt regimul ACTUAL:
- ZILIERI: impozit 10% pe (brut-CAS), CAS 25% pe brut, FARA CASS, FARA CAM. Confirmat
  la sursa (art.139(1)s + art.76(2)r CF: din mai 2019 zilierii datoreaza CAS 25%; nu
  sunt asigurati in sanatate deci fara CASS). Codul e aliniat la regimul actual, nu la
  cel vechi ("fara contributii" - depasit). Impozit 10% (nu 16% din textul original L52,
  suprascis de art.76(2)r CF). Monografie: 641=421, 421=4315, 421=444, 421=5311 (fara CASS).
- MANDAT/CENZOR: CAS 25% + CASS 10% + impozit 10% pe (brut-CAS-CASS), fara CAM. Corect.
Aritmetica verificata manual: zilier 500 -> net 337.50; mandat 2000 -> net 1170.
OBSERVATIE minora (nu bug): remuneratie_minima_zilier foloseste 165.33 ore/luna ->
orar 26.16, vs minimul orar oficial 25.95 (166.667 ore/luna). Rezultat conservator
(peste minim), de aliniat divizorul daca se doreste precizie la minimul orar exact.
