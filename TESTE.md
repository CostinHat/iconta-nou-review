# TESTE.md — planul de testare

**29.07.2026.** Registrul campaniei de testare a aplicației.

Campania are **două sesiuni distincte** (A, B), precedate de o **Faza 0** de pregătire — în ordine:

- **Faza 0 — decuplarea suitei de firmele persistente (GATA, 29.07).** Niciun test nu mai
  depinde de o firmă din baza (`tenant_001/002/003`): cine atinge baza își construiește
  subiectul pe schemă efemeră din `tenant_template` (comisă + DROP pentru scriitori, ROLLBACK
  pentru cititori) sau pe fake cursor. Prerechizit pentru B — firmele F1–F7 se **construiesc**,
  nu se presupun. Gardă permanentă: `core/test_teste_decuplate.py`. Vezi DECIZII 29.07.
- **Sesiunea A — alinierea la legislație.** Fiecare test fiscal se rescrie ca să afirme
  **regula de drept**, nu implementarea. Un test o dată; se validează, apoi următorul. Nu
  are nevoie de date; e pură.
- **Sesiunea B — testarea pe flux.** Cele 7 firme de test, cele 11 etape ale muncii unui
  contabil, cu regula cascadei.

**A înaintea lui B, și nu invers.** În A verifici legea o dată; în B o folosești. Fișierul
de așteptări al firmelor de test (B) se scrie din temeiurile deja verificate în A, nu de la
zero. Invers ar însemna să verifici de două ori — sau, mai probabil, a doua oară din memorie.

---

## În lucru acum

Firul curent — de aici derivă URMATORUL PAS al agendei. Se ține la ZI (regula de
redirecționare: ce se lucrează intră aici ÎNAINTE de a începe).

> **Stare:** site în mentenanță (46507b5) — allowlist pe IP-ul lui Costin; revenire cu `mentenanta.sh off`.

- fir: motor cluster "rezerva legala" — formula contabila CONFORMA (gard) + deductibilitate fiscala art.26(1)a = decizie produs (lant)
- ultim: credit sponsorizare|sponsorizari profit conform + datorie micro (5d1f5e8).
- urmator: cluster inchis (formula contabila gardata + deductibilitate fiscala = decizie produs). Ruleaza urmator_cluster(). GATA.
- pasi:
  RL1. [verificare + decizie] Formula rezervei legale CONTABILE (motor.py: 5% profit, plafon cumulat 20% capital - rezerva existenta) = CORECTA structural (Legea 31/1990 art.183, OMFP 1802/2014 pct.421), period-aware. Lipsea test NUMERIC (doar tautologic). Gard golden adaugat. NECONFORMITATE: deductibilitatea FISCALA CF art.26(1)a (baza = profit contabil + cheltuiala cu impozitul, plafon 20% capital subscris/varsat) LIPSESTE complet - nu se calculeaza nicaieri; d101 P6 "Deduceri fiscale" e input manual. = DECIZIE DE PRODUS (implementare + legare in d101 schimba declaratia de profit). motor.py e cod MORT (niciun apelant productie) - observatie. Commit.
  STARE = GATA (RL1 comis)

- fir: SWEEP DUK toate declaratiile (redirectionare Costin 31.07: inainte de reconstructii, mapez cate sunt sparte pe validatorul CURENT)
- ultim: sweep rulat pe schema efemera + profil complet + date minime adecvate (salariat/factura UE/dividende). Rezultat initial: 7 VALID + 2 sparte (d101, d406). d406 REZOLVAT 01.08 (bug de CALE, o linie): plan_oficial cauta d406_nomenclatoare_anaf.properties in radacina, dar fisierul e in anaf_surse/ -> set gol -> filtrarea pe norma (adaugata 15.07 tocmai pt 731 ONG) nu rula -> conturi ONG scapau in SAF-T comercial -> DUK respingea. Fix cale -> plan_oficial(A)=635, 731 exclus, d406 DUK VALID. RAMANE 1/9 SPART: d101 (reconstructie). Claim 16.07 infirmat.
- urmator: gard smoke-sweep DUK livrat (8 valide asertate incl d406 reparat + d101 xfail). d406 REPARAT (fix cale). RAMANE 1 reconstructie: d101 - cere greenlight temei OPANAF 206/2025. Posibil edge d394 (luna doar UE -> R112.3) de confirmat separat. BLOCAT: cere decizie d101.
- pasi:
  1. [GATA] sweep no-data + sweep cu date (salariat/factura UE) -> 7 valid / 2 sparte.
  2. reconstructie d101 (temei OPANAF 206/2025 validat) - cand Costin da drumul.
  3. [GATA 01.08] d406 reparat (fix cale plan_oficial -> anaf_surse/); gard test_d406.test_plan_oficial_citeste_nomenclatorul.
  4. [GATA 01.08] gard smoke-sweep DUK permanent: core/test_smoke_duk.py.
  STARE = BLOCAT: sweep+gard+d406 reparat; ramane d101 (reconstructie) - cere greenlight temei


- fir: D101 respins de DUK - reparare structura (Sesiunea A fiscal, REDIRECTIONARE Costin 31.07: prioritar peste D/d390). D101 in forma actuala NU poate fi depusa.
- ultim: descoperit la C2 - DUK respinge 'sectiune necunoscuta (P1)' (P-values ca elemente <P1>) + cod_bug=5503XXXXXX placeholder literal. Consemnat test_datorie_d101_build_xml_respins_de_duk.
- urmator: INVESTIGARE (metoda D1xx CLAUDE.md): extrag structura reala din D101Validator.jar (ultima versiune, constant pool), gasesc forma corecta P/cod_bug, construiesc XML minim valid pe DUK (o corectie/runda), PROPUN cu temei -> Costin valideaza -> implementez. IN LUCRU.
- pasi:
  1. localizeaza D101Validator.jar, versiunea maxima; unzip + strings pe clasele declaratiei; citeste TOATE atributele/elementele reale (P1..P16: element vs atribut? container?).
  2. cod_bug real pentru cod_obligatie 103 (impozit profit) - din nomenclator/validator, nu placeholder.
  3. XML minim construit manual, validat pe DUK sectiune cu sectiune pana la 'valid'.
  4. verifica clasa: d112 emite si el cod_bug=5503XXXXXX (add_oblig) - aceeasi problema? generalizare.
  5. PROPUNERE cu temei -> validare Costin -> implementare d101.py + test proba DUK + mutatie + gard.
  --- INVESTIGARE GATA 31.07 (metoda D1xx aplicata) ---
  CAUZA + SCOP REAL: D101 nu e fix mic, e RECONSTRUCTIE. (1) build_xml emite P ca ELEMENTE <P1> -> validatorul le respinge ca sectiune; corect = ATRIBUTE pe <declaratie101> (probat pe DUK: eroarea P1 dispare). (2) calcul_d101 a INVENTAT o numerotare proprie (cod: p11=impozit, p9=baza) care NU corespunde formularului oficial. Oficial (OPANAF 206/2025, D101_A600 v9/v10, anaf_surse/d101_struct_anaf.txt): ~53 campuri P cu lant de formule - P3=P1-P2, P6=P4-P5, P7=P3+P6, P8>=SUM(P081..P084), P10=P7+P8-P9, P16=P11+..+P15, P21=P17+..+P20, P22=P10-P16-P21, P34=SUM(P23..P33), P35=P22+P34, P38a=P35+P36+P37-P38, P40, P41=P411+P412 (=IMPOZIT PE PROFIT), P42=P421+P422+P423, P43, P48, P52, P53; totalPlata_A=SUM(P1..P53). Reguli: R17.1 scadenta (an_S>2025 => LL+3, cod foloseste LL+6 gresit + inconsistent cu nr_evid), R38 rezultat brut, R41 P41=P411+P412, grup (d_grup) etc. cod_bug=5503XXXXXX pare FORMAT ACCEPTAT (d112 il emite si trece) - nu e problema.
  DECIZIE CERUTA COSTIN: reconstructie D101 (rescrie calcul_d101 pe P-urile oficiale + build_xml cu P atribute, validat iterativ pe DUK pana la valid, gard test DUK) - GREENLIGHT temeiul (OPANAF 206/2025 + structura oficiala)? Campanie coheziva (un formular nu se face pe jumatate), mare. Alternativ: bounded first step sau amanat.
  COLATERAL: claim-ul 16.07 "toate 9 valide pe DUK" e nesigur - D101 clar nu e; d100/d205 confirmate azi (probele mele), d112/d390/d301/d406 NEREVALIDATE azi pe DUK curent (posibila deriva de versiune validator).
  STARE = BLOCAT: investigare gata, cere decizie temei/scop (reconstructie D101)

- fir: Contract uniform A1 - conversia generatoarelor ramase la contractul {pull, erori_generare, calcul_dNNN, build_xml, genereaza(conn,schema,perioada,...)} (Sesiunea A - arhitectura). Baseline verificator CONTRACT 6, coboara cu 1 la fiecare modul convertit.
- ultim: modul 7/10 d205 la contract (pull+genereaza(perioada); adaptor _d205; manual strict cheie_manual; DUK d205 valid; baseline 4->3). Convertite: d300,d301,d394,d710,d100,d101,d205. C (d100/d101/d205) GATA. DE DECIS (Costin): D101 build_xml respins de DUK (nu poate fi depusa) - campanie separata structura D101? Consemnat test_datorie_d101_build_xml_respins_de_duk.
- urmator: D1 - d112 (modul 8/10). RISC STRUCTURAL real (SCOPAT 31.07): d112 are DEJA pull+erori_generare; lipsesc calcul_d112+build_xml, ambele inghesuite in _d112_genereaza(prof,salariati,an,luna) ~250 linii unde calculul si XML-ul sunt IMPLETITE in aceeasi bucla per-salariat (fiecare <asigurat> emite XML imediat dupa ce-si calculeaza zecile de valori B1/B2/B3/B4/D/E1/E3 + part-time/CM/tichete; agregatele sum_imp/cas/cass/cam + C1/C2 se acumuleaza in bucla si intra in antet). Fara cusatura curata. Extragerea fidela cere Rezultat care poarta FIECARE valoare din XML (inclusiv randurile B3/D structurate) + proba golden-XML byte-identica pe fixturi ce ating toate ramurile. NEINCEPUT - cere greenlight (vezi DE DECIS).
- pasi:
  C1. [d100] pull(conn,schema,perioada)->(prof,venituri); genereaza(conn,schema,perioada,manual=None): cota din manual (cheie_manual(manual,"cota")), an=perioada.an, luna=perioada.trim*3, guard trim 1-4; adaptor _d100 -> Perioada(an,trim=), manual={"cota":..}. RED contract + mutatie + proba efemera. Baseline 6->5.
  C2. [d101] pull(conn,schema,perioada)->(prof,r{venituri,cheltuieli}); genereaza(perioada,manual); adaptor _d101 -> Perioada(an). Baseline 5->4.
  C3. [d205] pull(conn,schema,perioada)->(prof,asoc,total_div); genereaza(perioada,manual) override manual castiga; adaptor _d205 -> Perioada(an). Baseline 4->3.
  D1. [d112] extragere structurala calcul_d112/build_xml din genereaza (RISC - OPRIRE la regresie). Baseline 3->2.
  D2. [d406] idem (RISC). Baseline 2->1.
  d390-LA-URMA. 3 pull-uri impletite cu override + 2 consumatori -> 1 pull public + reclasificari->manual. Baseline 1->0.
  A2. except goale (7 codebase: d406=3 + tenant_provisioning/observare/gdpr_sterge/cron): tratat+documentat ori eliminat, niciunul gol; gard.
  A3. mutant zero sistematic: fiecare din 11 generatoare cu sursa->[] => suita PICA (test permanent, garzi cat.9).
  STARE = IN LUCRU (D1 d112 - extragere structurala, risc real)

- fir: Granite API — cota TVA lipsa = intrare incompleta -> eroare, nu default 21 (Sesiunea A · TVA, sub-fir temeiuri)
- ultim: masurare livrata — 80 cote "fara temei" = 79 TVA reale (1 fals-poz), 3 valori (21/11/19), cluster TVA verificat, 0 de cercetat / ~20 granite de reparat, rest ACCEPTATE (etaloane/fixtures/parametri). Directie confirmata Costin: default ELIMINAT, nu inlocuit; nedeterminat != 21; scutit 0 pastrat.
- urmator: GATA (31.07.2026, commit-uri 4ef863c..c11a1d4). 6 teme comise, fiecare rosu->verde->mutatie: (A) 16 endpoint-uri; (B) emitere nedeterminat; (C) cota 0 + date stocate; (D) registru GRI (80->2 baseline); (E) proba D300 scutit -> DUK VALID. Ramas descoperit: 2 GRI de agregare (main:4045/4046, temei cunoscut) + auto-match AI propune cota cu incredere mica la produs nou ambiguu (transparent, corectabil - NU tacut).
- pasi:
  1. [tema A] cota_ceruta(corp) helper (HTTPException 422 la None, 0 valid) + cele 16 endpoint-uri main.py + RED + mutatie.
  2. [tema B] potriveste_cota: 4 fallback-uri -> NEDETERMINAT (nu 21); produse_api.creeaza + _potriveste_linii ridica; dead ,21 eliminat; LinieIn->Optional=None; storno cota. RED: AI picat + linie fara cota -> emitere blocata.
  3. [tema C] produse_api:46 bug cota-0 (or 21 -> distinge None/0) + granite date stocate (main:6291, reconciliere:177, stocuri adauga_nir). RED: cota 0 ramane 0.
  4. [tema D] verificator: gard GRI cota (verde/gri/rosu, listat) + baseline recompute + ACCEPTATE.
  5. [tema E] proba D300 + factura scutita (cota 0) -> DUK VALID (lectia D3).

- fir: Temeiuri citabile mecanic + reverificarea locurilor fără temei (Sesiunea A · transversal)
- ultim: runda 4 comisă — (B) gardă bump-motiv: o bifă din Inventar A mutată înainte cere motivul scris în coloană, altfel garda anti-stale devine ornament (105ef50); (C/FIX5) salariu minim 2025 corectat 4050 → HG 1506/2024 (era 3700 = valoarea 2024 H2, act greșit), datorie xfail închisă și consemnată în DECIZII.md (cf31ddb); (A) confirmat că plafonul deducerii e DERIVAT (salarizare.py: sm+2000), zero literal 6050/6325 → niciun bug activ (semestrul 2: sm=4325 → prag=6325 automat). Fiecare fix: roșu→verde→mutație, commit separat.
- urmator: CORECTIE REGULA temei 01.08 GATA (3 etape). (1) corectie DECIZII (ab0f359); (2) data_out ESTIMAT pe 7 valori + gard nicio-cota-fara-data_out (4c23994); (3) 2 GRI atasate (tva_redusa in COTE + main.py period-aware) + GRI_BASELINE 2->0 PRAG. Temei structurat=0, GRI=0. Ambele garzi in PRAG. GATA markeri TEMEI functie 01.08: criteriu structural EVALUAT (57 prinse, 5/7, ~18 fals-poz rotunjire) si RESPINS -> lista EXPLICITA (salarizare 6 functii salariu/CM), toate 6 marcate ACUM, gard verificator PRAG 0. DECIZII 01.08. Limita: nu auto-detecteaza (alte clustere se adauga la confirmare).
- pasi:
  · [GATA] §3.1 format · inventar (60 clustere, 4 √) · core/temeiuri.py (CLI) · gard validator-regulă · garda anti-stale per funcție.
  · [ÎN CURS] 2b — locuri fără temei, pe CLUSTER, cu validarea ta: deducere personală [√ 31.07] → tichete → concedii medicale → apoi celelalte 10 module.
  · [GATA 31.07] Temei STRUCTURAT (etapele 1-4): common.Temei(act/.../data_out) pe toate cotele COTE; cota() ridica la expirare (data_out = mecanism principal de deriva, nu proxy); gard ratchet in verificator; Inventar A generat partial + overlay persistent; GARZI cat.3 = limita reala (schimbare de lege intre data_in si data_out nu e detectabila). Commit-uri 3c37bfa..9ed8899.
  · [RĂMAS] cele 113 citări normative (decizia #1) · datoriile xfail deschise.

- fir (în așteptare): Modelarea contractului în timp (Sesiunea A · salarizare)
- ultim: 2b-scrieri comis — creare/editare/import scriu pe salariu_istoric, citiri pe salariu_curent (reparat si bug-ul activ din import, PASUL 1)
- urmator: 2b-coloană — DROP salariati.salariu_brut din tabel + migrare, UI schimbare salariu (valabil_din), scoaterea bridge-ului salariu_la. NEÎNCEPUT.

---

## Implementarea modelului de temei (01.08)
- ETAPA 1 [GATA]: data_out=None pe curente + derivare din succesor + verificat_la/de_cine + EXPIRA_DUPA_LUNI scos + cota() ridica doar pe gol real + gard inversat + raport cote_neconfirmate (expirare_cote reformulat). Alerta email aliniata (fara expira/REFUZA pe curente).
- ETAPA 2 [NEINCEPUT]: text_citat + nivel_sursa + lant_acte pe cele 12 COTE + 6 functii; gard nivel_sursa obligatoriu.
- ETAPA 3 [GATA]: core/graf_temei.py - analizor AST cota("x") + inchidere tranzitiva. Proba: depinde_de("salariu_minim")=12 functii (deducere_personala+calcul_salariu DIRECT; sub-conceptele facilitate/plafon12sm/suprataxare/prag-tineri traiesc IN ele, vazute prin ele). Limita: literal hardcodat ocoleste graful (gardul GRI la 0 = conditia). Pct.7 nedecis (masurare, alta tura).

# SESIUNEA A — alinierea la legislație

## Problema

Un test poate fi corect tehnic — izolat, curat, cu mutație dovedită — și complet inutil,
dacă afirmă **ce face codul** în loc de **ce cere legea**.

Trei cazuri, toate cu suita verde luni de zile:

- **D301** — regula că secțiunea 4.1 se preia DIN secțiunea 4 (OPANAF 592/2016) nu era
  scrisă nicăieri. Generatorul o încălca, ANAF respingea declarația pe cazul cel mai
  frecvent (servicii UE). Nu exista **niciun** test pe D301.
- **D390** — rotunjirea era bancară (`round()`), deși D112 documenta în cod că ANAF cere
  aritmetică și că cea bancară fusese RESPINSĂ de validator (regula A91b). Ambele treceau.
- **Limita de 75 de caractere** — respectată în 6 din 11 locuri unde se emitea numele
  declarantului. Niciun test n-o afirma; jumătatea nerespectată a trăit până când ANAF a
  respins declarația unei firme cu denumire lungă.

Cauza e aceeași: testele reproduceau implementarea. Un test scris din citirea codului
**încremenește codul, inclusiv greșelile lui**.

**Observație de metodă (29.07.2026).** Verificarea la sursă a unui singur test (facilitatea la
salariul minim) a scos trei fațete ale aceleiași lipse de model — contractul n-are dimensiune
temporală. Nu s-ar fi văzut din cod: fiecare fațetă arată ca un caz izolat până când se citește
articolul întreg, care le enumeră pe toate patru într-un singur alineat.

## Regula

**Orice test care afirmă o valoare, o cotă, un prag, o rotunjire sau o structură fiscală
citează temeiul lângă assert.** Nu într-un document separat — pe linie, unde se vede când
cineva îl modifică.

```python
# FĂRĂ sursă — reproduce formula din cod, nu apără nimic:
assert calcul_tva(1000, 21) == 210

# CU sursă — afirmă regula, pică dacă cineva „optimizează" implementarea:
assert _int(112.5) == 113   # ANAF cere rotunjire ARITMETICĂ, nu bancară.
                            # D112 regula A91b: CAM calculat 112, cerut 113 (respins de validator).
```

## Ce se face când temeiul lipsește

**Dacă regula nu e verificată la sursă, testul NU se scrie.** Se pune `xfail(strict=True)`
în `core/test_datorie.py`, cu motivul „temei neverificat: <ce anume>".

Un test scris pe presupunere e mai periculos decât absența lui: dă siguranță falsă, iar
când cineva îl vede roșu repară **codul** ca să se potrivească cu presupunerea.

Pe 27.07 era să se întâmple: cerusem ca `total_plata_A` la D301 să se calculeze din
secțiunile 1–4. Verificarea empirică la DUK a arătat că ANAF impune altceva (regula R28,
checksum peste toate cinci). Dacă testul se scria pe acea presupunere, generatorul ar fi
fost „reparat" ca să producă o declarație pe care ANAF o respinge.

## Cum se lucrează în sesiunea A

**Un test o dată. Se validează, apoi următorul.** Fără fragmentare pe alte subiecte: în
sesiunea A se aliniază produsul cu specificațiile legale, atât.

Pentru fiecare test:

1. **Ce afirmă azi** — se citește testul existent, nu se presupune.
2. **Ce cere legea** — se verifică la sursă oficială (Cod fiscal, OMFP, OPANAF, OUG,
   instrucțiunile formularului). Se notează temeiul exact: act, articol, alineat.
3. **Se compară.** Trei rezultate posibile:
   - **coincide** → testul se rescrie cu temeiul citat pe linie;
   - **diferă** → **e reparație fiscală, nu rescriere de test.** Se repară codul, cu
     dovadă (validator, zero regresie), apoi testul;
   - **legea nu spune** → nu se scrie test. `xfail` în `test_datorie.py` cu „temei
     neverificat".
4. **Se validează** înainte de a trece mai departe.

Rezultatul sesiunii A: o suită care afirmă legea, nu implementarea.

## PREDARE PART II (02.08.2026) — mecanismul de localizare act -> clustere (PART I livrat, PART II ramas)

PART I LIVRAT (condiile, in ordine): V1 inventar complet + criteriu (43b2f5c), V2 graful vede doar prin cota()
(609cc6b), V3 resetarea propagata pe graf + ratchet stale (a8889b8). Fundament pe care se sprijina PART II:
- core/temeiuri.py: gaseste(act) -> locurile din core/*.py care CITEAZA actul (substring, forme partiale).
- core/agenda.py: cote_cluster(rand) -> cotele de care depinde un cluster (test->sursa->graf). stare_sesiune_a()
  -> randurile inventarului (cluster, modul, Temeiuri, Functie(test)).
- core/graf_temei.py: depinde_de(cota) -> functiile care depind de o cota (direct/tranzitiv).
- common.COTE: fiecare valoare cu Temei (act/nr/an/art + lant_acte).

PART II - de construit (core/localizare.py + test cu probele):
1. INDEX act -> clustere, din temeiuri atasate:
   - cote_lovite(act) = cheile COTE al caror Temei (str + lant_acte) contine actul.
   - clustere_direct(act) = randuri din inventar a caror coloana Temeiuri contine actul.
   - functii(act) = temeiuri.gaseste(act) (markeri TEMEI + obiecte Temei in cod).
   - clustere_indirect(act) = randuri cu cote_cluster(rand) ∩ cote_lovite(act) != {}, MINUS clustere_direct
     (lovite prin VALOARE din graf - marcate DISTINCT de cele lovite direct prin citare).
   - declaratii(act) = modulele clusterelor lovite (d100..d710, salarizare, + orfanele V1).
2. INTEROGARE(act) -> {clustere_direct, clustere_indirect, cote, functii, teste=Functie(test) ale clusterelor
   lovite, declaratii}.

PROBE (de rulat, output brut):
- Legea 141/2025 -> TVA (tva_standard/tva_redusa citeaza) SI concedii (Temeiuri: 'Legea 141/2025 si 136/2020';
  modifica art.17 OUG 158/2005). Daca lista e INCOMPLETA -> granita intre clustere e trasata gresit: repara
  GRANITA, nu interogarea (ramificatie: tichete culturale/cresa vs masa/vacanta - Legea 165/2018 le da pe toate 4).
- OUG 158/2005 si art.77 CF -> verificat MANUAL ca listele sunt complete.
- salariu_minim (COTA, nu act) -> reverse-graf: deducere, facilitate, plafon 12 sm, suprataxare part-time, prag
  tineri, tichete vacanta. RISC CUNOSCUT (V2): 'tichete vacanta' (plafon 6 sm, beneficii_api) poate sa NU apara
  daca plafonul e hardcodat, nu cota() - atunci graful nu vede dependenta -> spune care si de ce (blind spot V2).

RAMIFICATII PART II: (a) act cu lista incompleta -> repara GRANITA de cluster; (b) daca repararea granitei ar
CADEA vreo bifa -> OPRESTE, raporteaza (nu reseta singur - vezi si cele 3 stale de la V3); (c) daca lista testelor
fara cluster trece de ~20, gard pe ratchet.

DE DECIS COSTIN (din V3, deschis): 3 bife 29.07 (suprataxare part-time, proratare, suprataxare prag) sunt STALE -
stau pe salariu_minim 2025 corectat 3700->4050 dupa √. De reverificat la sursa. Ratchet baseline=3 in test_agenda
le tine vizibile fara sa le reseteze; la reverificare, coboara baseline-ul.

## PAS 1 (02.08.2026) — forma grafului de dependente intre clustere (masurat inainte de secventa)

Edge A->B (A dupa B) = o functie a lui A (testele lui -> functii-sursa -> inchidere pe graf_temei) atinge o
functie DETINUTA de B, fara co-locatie (functie partajata = fatete, nu dependenta). Cifre:
- TOTAL clustere: 70. RADACINI (zero dependente): 63. Cu functii mapate (via teste): 8.
- ADANCIME MAX a lanturilor: 2 (facilitate -> deducere). Muchii: 7, TOATE in familia salarizare.
- CICLURI: 1 -> `facilitate salariu minim <-> deducere personala` (co-locatie in calcul_salariu: calculul net
  foloseste deducerea; deducerea si facilitatea traiesc in aceeasi functie). NU il tai singur (decizie Costin).
- COMPONENTE cu >1 nod: 1 (7 clustere: facilitate, deducere, suprataxare part-time, proratare, suprataxare prag,
  contributii PFA, impozit dividend). Restul 63 = izolate.

Muchii reale: facilitate->deducere; suprataxare part-time->{deducere,facilitate}; proratare->{deducere,facilitate};
deducere->facilitate; suprataxare prag->facilitate; impozit dividend->facilitate; contributii PFA->facilitate.

CONSECINTE:
- Ordinea CONTEAZA PUTIN: adancime 2, 63/70 radacini -> campania e aproape LINIARA (departajare, nu lant lung).
- Ciclul e INTRE CLUSTERE BIFATE (facilitate+deducere = √) -> NU blocheaza secventa celor NEBIFATE. Cele 2 nebifate
  din componenta (contributii PFA, impozit dividend) depind doar de facilitate (bifat) -> LIBERE. Deci toate
  clusterele nebifate sunt libere: secventa = departajare determinista, nu sortare pe lant.
- Cele 63 izolate: structura/declaratii care depind doar de cote de BAZA (deja verificate cu temei), nu de alte
  clustere. Dependentele ascunse cunoscute (d100/d212) au fost rutate prin cota() (campania anterioara) -> graful
  le vede acum. Nu s-au gasit alte clustere invizibile grafului la aceasta masurare.

## Secventa de verificare (persistata 02.08.2026 - NU se recalculeaza la fiecare rulare)

Ordine DETERMINISTA a celor 64 clustere nebifate+neblocate, sortare topologica pe graf_clustere + departajare
(a) FISCAL>STRUCTURA (b) deblocari desc (c) ordinea inventarului. Rescrisa 02.08: tichete masa/vacanta BIFAT ->
iesit din secventa (65->64); concedii medicale (salarizare+d112) INCHISE 02.08 -> 64->62; tichete culturale (functionalitate noua livrata) INCHIS 02.08 -> 62->61. tichete cresa (functionalitate noua livrata) INCHIS 02.08 -> 61->60. cota profit 16% + IMCA (cota verificata + IMCA implementat art.18^1) INCHIS 02.08 -> 60->59. amortizare|d101 (tratament art.28 aliniat; datorie MF metode) INCHIS 03.08 -> 59->58. baze contributii|d112 (cotele CAS/CASS/imp/CAM rutate period-aware prin COTE, value-preserving, aliniere Sesiunea A) INCHIS 03.08 -> 58->57. rotunjire aritmetica (A91b)|d112 (contributii aritmetice verificate; REPARAT minimul part-time care rotunjea bancar in B4_*P declarat) INCHIS 03.08 -> 57->56. sect_II tip_venit|d205 (structura OPANAF 102/2025 verificata; REPARAT impozit dividende hardcodat 10% -> period-aware 16%/2026 Legea 141/2025) INCHIS 03.08 -> 56->55. rotunjire|d205 (sumele fiscale rotunjesc aritmetic - verificat, deja corect prin _i ROUND_HALF_UP; gardat cross-generator + proba) INCHIS 03.08 -> 55->54. cote TVA->randuri|d300 (livrari 21/11/9 corecte; REPARAT achizitii deductibile 11% R74->R23 si 9% R76->manual, proba DUK; datorie 9% auto) INCHIS 03.08 -> 54->53. exigibilitate/TVA la incasare|d300 (IMPLEMENTAT art.282/297 OUG 8/2026: exigibilitate din decontari, suta marita, proportional, proba DUK) INCHIS 03.08 -> 53->52. taxare inversa|d300 (rd.12 reparat - R12_ lipsea din allow-list; GRI reverse-charge reconfirmat la sursa art.331+structuri) INCHIS 03.08 -> 52->51. pro-rata deducere|d300 (verificat corect art.300 - R31 ajustare Rd.33, net R28xpro_rata; gap de acoperire inchis + proba DUK) INCHIS 03.08 -> 51->50. rotunjire aritmetica|d300 (verificat aritmetic ROUND_HALF_UP, deja in gardul de identitate; proba d300-specifica) INCHIS 03.08 -> 50->49. ajustari|d300 (REPARAT R29/R30/R35/R36 aruncate din allow-list - ajustari/regularizari nedeclarate; proba DUK) INCHIS 03.08 -> 49->48. tipuri operatiune 1-5|d301 (verificat maparea tip->sectiune OPANAF 592/2016; gard tipuri 1/2/3 + proba DUK toate 5) INCHIS 03.08 -> 48->47. rollup S4.1->S4|d301 (verificat COMPLET - S4.1 subset din S4 OPANAF 592/2016, TVA nedublat, checksum, proba DUK; test_d301_rollup.py dedicat) INCHIS 03.08 -> 47->46. baza=val x curs|d301 (verificat CF art.290 alin.(2): baza=elemente_valuta x curs BNR/BCE la exigibilitate, rotunjire ROUND_HALF_UP corecta; REPARAT fabricare tacita curs=1 pe valuta - gard calc_baza pe None/<=0 + scos or 1 din generator+reader + scos DEFAULT 1 din schema; proba 1000x4.977=4977 / EUR fara curs->ValueError / RON=1->1234) INCHIS 03.08 -> 46->45. cota TVA|d301 (standard period-aware corect; REPARAT cota redusa literal 11 -> period-aware din common.cota, omisa pt perioade < 08.2025 unde reducerile erau 9%/5%; 2026 neschimbat [21,11,0]; decizie de produs deschisa: modelare 9%/5% coexistente) INCHIS 03.08 -> 45->44. tipuri operatiune IC (L/A/P/S)|d390 (VERIFICAT - mapare tip->simbol = nomenclator OPANAF 705/2020 L/T/A/P/S/R; codO/totalPlata_A/anti-drop conforme; gard-pin TIPURI==oficial adaugat) INCHIS 03.08 -> 44->43. rotunjire aritmetica (A91b)|d390 (VERIFICAT - _int ROUND_HALF_UP, gardat dublu identitate+scan; proba d390 pe valoare adaugata) INCHIS 03.08 -> 43->42. reclasificari manuale|d390 (FIX asimetrie: read-side facea fallback tacit la default pe reclasificare invalida; acum valideaza direciția ca write-side si ridica, TIPURI_DIRECTIE sursa unica in d390.py) INCHIS 03.08 -> 42->41. exigibilitate / prag|d390 (VERIFICAT - incadrare pe data_emitere = exigibilitate art.283/284, fara prag art.325; gard temporal pe pull adaugat; edge-case ziua-15 consemnat = decizie schema) INCHIS 03.08 -> 41->40. cote acceptate|d394 (VERIFICAT - d394 e modelul period-aware; cota_standard din common.cota, set fix = validator v5, fara literal hardcodat; garduri pin + cross-modul common⊆d394 adaugate) INCHIS 03.08 -> 40->39. taxare inversa|d394 (11/12 conform; NECONFORMITATE lit.l gaze naturale gasita, CORECTARE blocata pe codPR D394 neconfirmat la sursa - gard anti-regresie + datorie xfail(strict); input cerut: codPR gaze post-2021) INCHIS 03.08 -> 39->38. SourceDocuments|d406 (FIX period-awareness TaxCode livrari - TAXCODE_LIVRARI_PRE era definit dar nefolosit, factura veche emitea coduri post gresite; helper _taxcode_livrari pe data + gard. Payments/achizitii/adrese = observatii documentate) INCHIS 03.08 -> 38->37. plafon diurna neimpozabila|deconturi (calcul curent CONFORM art.76 alin.4^1 + gard golden; NECONFORMITATE period-awareness istorica - varianta unica aplica valorile de azi retroactiv, fix blocat pe HG diurna lipsa; datorie xfail strict) INCHIS 03.08 -> 37->36. credit sponsorizare / D177|sponsorizari (PROFIT conform art.25 alin.4 lit.i + gard existent; micro NU period-aware=datorie xfail (blocat pe text istoric art.56 alin.1^5 abrogat); D177 formular absent=decizie produs; endpoint neperiodizat=observatie) INCHIS 03.08 -> 36->35. rezerva legala|motor (formula CONTABILA conforma Legea 31 art.183 + gard golden adaugat; deductibilitatea FISCALA art.26(1)a - add-back impozit + plafon capital subscris - LIPSESTE = decizie produs; motor.py cod mort fara apelant) INCHIS 03.08 -> 35->34. zilieri (impozit+CAS)|contracte_speciale (FIX period-awareness: CAS 25%% aplicat din 2018-01-01, dar exista legal doar de la 01.05.2019 OUG 26/2019; 2 variante datate - 2018 doar impozit 10%%, 2019 CAS+impozit; impozit/CASS conforme) INCHIS 03.08 -> 34->33. regim marja second-hand|tva_marja (VERIFICAT - TVA pe marja = marja x cota/(100+cota) suta marita conform CF art.312 alin.(4), marja negativa->0; gard golden adaugat (lipsea test numeric); observatii main.py: cota neperiodica + la_data nepasat) INCHIS 03.08 -> 33->32. regim marja turism|tva_marja_turism (VERIFICAT - suta marita CF art.311 alin.4 + scutire proportionala non-UE alin.5, marja negativa->0; gard golden adaugat; neintegrat in datorie.py = observatie) INCHIS 03.08 -> 32->31. impozit dividend|decontari_asociati (FIX cote istorice: intrarea pre-2026 era 10%% fals (10%% = impozit pe venit art.78, nu pe dividende) -> 2023-2025 supra-impozitate; 3 intrari verificate la sursa 5%%/8%%/16%% (OUG 50/2015, OG 16/2022, Legea 141/2025); teste care cimentau 10%% actualizate) INCHIS 03.08 -> 31->30. contributii PFA (praguri CAS/CASS pe sm)|d212 (VERIFICAT calcul conform - CAS art.148, CASS art.170 alin.1 liniar, sm period-aware; REPARAT citare temei plafon 72 sm: Legea 141/2025 -> Legea 239/2025 art.XII pct.19; obs: calea 2026 dormanta) INCHIS 03.08 -> 30->29. nomenclator cod_oblig<->cod_bugetar|d100 (FIX cont bugetar obsolet: 20470101 (pre-2018) -> 5503XXXXXX, coroborat cu d101/d112; sursa unica d100.COD_BUGETAR importata si de d710; gard anti-drop pe cod nemapat; teste actualizate) INCHIS 03.08 -> 29->28. cota micro 121 (flag)|d100 (VERIFICAT - generator conform struct poz.17a (121->cota=1, 103->fara cota); gard bidirectional in build_xml: 121-fara-cota si cota-pe-alt-cod ridica ValueError, imposibil XML respins) INCHIS 03.08 -> 28->27. checksum totalPlata_A (R11b)|d100 (VERIFICAT valoarea emisa corecta 2x sum DUK R11b; REPARAT divergenta res.total_plata_a (1x) vs emis (2x) - aliniat la sursa unica res.total_plata_a=checksum emis de build_xml, ca celelalte declaratii) INCHIS 03.08 -> 27->26. scadente/nr_evidenta|d100 (VERIFICAT - nr_evidenta 23 poz conform struct (fix R16 poz.18), scadenta 25 luna urmatoare (poz.15) format ZZ.LL.AAAA; gard scadenta adaugat (lipsea); obs alte reguli scadenta pt obligatii nengerate) INCHIS 03.08 -> 26->25. structura P1-P53|d101 (VERIFICAT conform si complet OPANAF 206/2025 - toate formulele P3-P53 rand-cu-rand, totalPlata_A sum P1..P53, P13 rezerva legala corect, d_grup tratat; deja gardat golden+DUK, fara fix) INCHIS 03.08 -> 25->24. R17 Data_S/termen|d101 (neconformitate aparenta REZOLVATA: scadenta D101 parea inversata fata de lege dar valoarea validatorului 2022-2025=iunie e legal corecta via OUG 153/2020 art.I alin.13 lit.a - act ratat de prima cercetare; 2026=martie baza=jar-ul DUK, OUG 8/2026->iunie cand jar-ul se actualizeaza; decizie Costin: urmeaza validatorul pe ambele ramuri; temeiuri corectate) INCHIS 03.08 -> 24->23. limita text 75|d112 (2 neconformitati trunchiere reparate: numeAsig/prenAsig salariat (C75) erau netrunchiate -> nume >75 respins; functie_declar are C(50) nu 75, se trunchia la 74; reparat _t pe nume salariat + _t(...,50) pe functie) INCHIS 03.08 -> 23->22. nomenclator cod_oblig|d112 (VERIFICAT conform - toate 6 codurile cod_oblig<->cod_bugetar coincid cu nomenclatorul ANAF: 602/412/432->5503XXXXXX, 480 CAM->20470300XX distinct, 458/459->5503XXXXXX; lipsea gardul pe cod_bugetar, adaugat) INCHIS 03.08 -> 22->21. checksum totalPlata_A|d205 (VERIFICAT valoarea emisa CONFORMA - totalPlata_A=nrben+Tcastig+Tpierd+T_VB+T_GAR+Tbaza+Timp exact ca ANAF struct D205 OPANAF 102/2025 l.80-85, DUK-valid; REPARAT capcana latenta clasa-d100: res.total_plata_a tinea DOAR Timp, build_xml recalcula checksum-ul INDEPENDENT - d205 outlier de la conventia tuturor declaratiilor; aliniat sursa unica: calcul_d205->res.total_plata_a=checksum, build_xml il emite) INCHIS 03.08 -> 21->20. INCHIS 03.08 -> 21->20. trunchiere den/adresa|d205 (NECONFORMITATE reparata probata DUK: campurile text se trunchiau la 75 default, dar struct D205 OPANAF 102/2025 + DUK dau den C200/adresa C1000/functie_declar C50/den1 C100; den/adresa over-trunchiate=pierdere date, functie 51-75 si den1 >100 respinse de ANAF; fix limite explicite in build_xml, proba DUK pe inputuri lungi=valid) INCHIS 03.08 -> 20->19. Identitate = cluster | modul (nume duplicate intre module).

**REGULA DE ORDONARE.** Clusterul A vine dupa B daca o functie din A foloseste o valoare care APARTINE lui B (dependenta din graf_clustere). Sortare topologica pe aceste dependente. Departajare cand mai multe sunt libere simultan, in ordinea: (a) intra intr-o declaratie DEPUSA la ANAF - proxy Risc=FISCAL, aproximatie DECLARATA, nu echivalenta; (b) cate clustere deblocheaza; (c) ordinea din inventar. Secventa se PERSISTA, nu se recalculeaza la fiecare rulare - altfel pozitia 7 de azi nu e pozitia 7 de maine. Se rescrie DOAR cand se schimba graful sau se adauga clustere, cu motivul consemnat (vezi randul 'Rescrisa 02.08' de mai sus).
1. randuri / checksum | d300
2. checksum totalPlata_A (R28) | d301
3. nomenclator tari (HR->CR) | d390
4. tipuri operatiune (pct.215) | d394
5. tip_partener | d394
6. rezumat1 campuri complete | d394
7. nomenclator codPR (art.331) | d394
8. totalPlata_A (R17) | d394
9. plan conturi pe norma | d406
10. UoM UN/ECE | d406
11. MovementType nomenclator | d406
12. BaseRate (encoding pro-rata) | d406
13. registration_number (00+CUI) | d406
14. structura XSD (Header/MasterFiles/GLE) | d406
15. structura declaratie710 | d710
16. nomenclator COD_BUGETAR | d710
17. checksum R11b | d710
18. R15 termen definitivare | d710
19. scadente | d710
## Inventarul de acoperit în A

Per CLUSTER de reguli, nu per fișier (30.07.2026) — un √ pe fișier ascundea că doar o parte din
reguli era verificată (vezi salarizare 29.07). `Verificat la sursă`: `√ DD.MM` = testele afirmă
LEGEA la data aceea (garda anti-stale pică `√`-ul dacă codul se schimbă substanțial după). `Risc`:
**FISCAL** = produce o cifră într-o declarație, greșeala e INVIZIBILĂ (validatorul acceptă) și ajunge
la ANAF; **STRUCTURA** = mapare/nomenclator/checksum/XML, greșeala e VIZIBILĂ (validatorul respinge).
Estimare de structură — se rafinează la citirea fiecărui modul.

### Criteriul de apartenenta la cluster (V1, 01.08.2026)

Un CLUSTER = o regula fiscala/structurala distincta (sau un grup strans cuplat) care produce o valoare
intr-o declaratie sau un modul de calcul, sprijinita pe un set coerent de temeiuri, verificata de un set de
functii de test (coloana Functie(test)). Granita e REGULA, nu fisierul: un fisier de test acopera mai multe
clustere.

- CO-LOCATIE: o regula partajata intre doua clustere apare in Functie(test) al AMBELOR (ex. proratarea se
  aplica SI facilitatii SI suprataxarii). Garda anti-stale reseteaza clusterele co-locate IMPREUNA (mesajul
  le numeste). Nu se duplica regula intr-un cluster nou.
- ORFAN: o regula fiscala in cod (functie cu marker TEMEI SAU care citeste o cota SAU un rate literal) fara
  NICIUN rand in inventar. Un orfan nu e verificat de nimeni si nu va fi -> se ADAUGA ca rand. Detectia e
  MARGINITA de markeri+graf: o regula cu rate hardcodat, fara marker si fara cota, e INVIZIBILA (cazul
  bilant_api) - se inchide doar cu gardul GRI de literale la 0 (GARZI cat.3, LIPSA).
- TEST DE MECANISM vs DE VALOARE: un test care verifica MASINARIA (graf de dependente, temei structurat,
  dispecer de versionare, cota() period-aware, generarea inventarului, blocaj motivat) NU asertaza o valoare
  fiscala a unui cluster - nu apartine niciunui cluster, prin design. Doar testele care asertaza o CIFRA/
  structura ceruta de lege intra in Functie(test).

| Cluster | Modul | Teste | Verificat la sursă | Risc | Temeiuri | Funcție(test) |
|---|---|---|---|---|---|---|
| facilitate salariu minim | salarizare | test_salarizare.py | √ 31.07 (bump: FIX3 a mutat net-ul asertat in test_minim_4325_are_facilitate_sem2; facilitatea reconfirmata la sursa OUG 89/2025 art.III + HG 146/2026, neschimbata) | FISCAL | OUG 156/2024 art.LXVI; OUG 89/2025 art.III; HG 146/2026 | test_minim_4325_are_facilitate_sem2 test_facilitatea_ramane_conditionata_de_norma_intreaga test_facilitate_pe_minim_cu_cm_ramane_intreaga test_facilitate_prorata_luna_angajare |
| suprataxare part-time | salarizare | test_salarizare.py | √ 02.08 (bump: V3 salariu_minim 2025 corectat 3700->4050 HG 1506/2024 FIX5 dupa √ 29.07; praguri COTA-DERIVATE nu literal - salarizare.py:129 sm=cota, d112 _sal_minim=cota; recalculat sm 2025/2026H1=4050 2026H2=4325 identic cu codul: (4050-300-2000)*25%=437.50, (4325-200-2000)*25%=531.25) | FISCAL | CF art.146 alin.(5^6)-(5^7); art.168 alin.(6^1) | test_part_time_2000_suprataxa_pe_angajator test_part_time_exceptat_fara_suprataxa test_norma_intreaga_sub_minim_este_suprataxata test_part_time_sub_minim_ramane_suprataxat test_exceptatul_nu_e_suprataxat_indiferent_de_norma test_peste_minim_nu_se_suprataxeaza test_suprataxa_baza_pe_minimul_diminuat_ambele_semestre |
| proratare angajare/incetare | salarizare | test_salarizare.py | √ 02.08 (bump: V3 salariu_minim 2025 corectat 3700->4050 HG 1506/2024 FIX5 dupa √ 29.07; praguri COTA-DERIVATE nu literal - salarizare.py:129 sm=cota, d112 _sal_minim=cota; recalculat sm 2025/2026H1=4050 2026H2=4325 identic cu codul: (4050-300-2000)*25%=437.50, (4325-200-2000)*25%=531.25) | FISCAL | OUG 156/2024 art.LXVI alin.(4); OMF 1855/2022 pct.2 | test_suprataxa_prag_prorata_luna_angajare test_facilitate_prorata_luna_angajare test_suprataxa_si_facilitate_prorata_la_incetare |
| deducere personala | salarizare | test_salarizare.py | √ 31.07 | FISCAL | Cod fiscal art.77 alin.(4)/(10)(a); pliant ANAF AJFP Vrancea (deducere personala) | test_deducere_degresiva_pe_trepte test_deducere_copil_scoala test_deducere_zero_fara_functie_baza test_deducere_4plus_persoane_45pct test_tanar_sub26_brut_mic_primeste_deducere test_deducere_la_data_obligatoriu |
| tichete masa/vacanta | salarizare | test_salarizare.py test_tichete_pontaj.py test_exces_vacanta_d112.py | √ 02.08 (bump: D2 nr tichete = zile efectiv lucrate din pontaj CONFIRMAT cap.23 - fe99cc2/5a5b63c/f83da8a/61c0260; D3 exces vacanta in brut declarat DUK-valid 9a82748; fond 31.07 valoare45/cote/plafon6sm/cadou; #3 baza CASS ramane GRI - verbatim art.78 neconfirmabil, fond prin derivare art.157->78. Teste D2 in test_tichete_pontaj, D3 in test_exces_vacanta_d112) | FISCAL | Legea 201/2025; HG 1045/2018 art.10(3); CF art.76(3)h/78/142(r)/157(2); OUG 8/2009 art.1; L296/2023 | test_exces_vacanta_intra_in_baza_salariala test_cass_doar_pe_01_07_10 test_tichete_scad_cu_zilele_de_co test_tichete_blocheaza_daca_pontaj_neconfirmat test_d112_cu_exces_vacanta_valid_duk |
| concedii medicale | salarizare | test_salarizare.py | √ 02.08 (bump: PARTIAL 31.07 -> inchis 02.08 - cod 02 GRI + unificare taxe_cm confirmata + D-field cod 06/08 DUK-valid pe clusterul d112; CM1 GRI, CM4/cod05 datorii) — procente pe cod (01=55/65/75 progresiv, 02/03/04 FAAMBP 80/100, 05/06/07/12/14/51=100, 08/09=85, 13/15/rest=75, 10 art.19), split 1-5/FNUASS, diminuare 1 zi, CAS 25% uniform + CASS 01/07/10 UNIFICAT (taxe_cm canonic, apelat si de d112.py:186 - fara divergenta, cautat clasa nu instanta); cod 02 accident traseu GRI (FAAMBP corect; nerecunoscut ITM -> recodificare la 01, nu ramura pe cod 02); DUK cod 01 valid. GRI: CM1 verbatim art.139(1)(o) neobtinut la MO. DATORII declarate (test_datorie): CM4 plafon 12sm in calcul_cm neaplicat, cod 05 sub-randuri infectocontagioase | FISCAL | OUG 158/2005 art.10/12/17/20; Legea 141/2025 si 136/2020; CF art.139(1)o+140 (CAS salariat activ; art.144=alte categorii)/142/155(1)i; OUG 34/2024 | test_cass_doar_pe_01_07_10 test_cm_cas_25pct_uniform test_cm_split_angajator_max_5 test_carantina_cod07_este_100pct |
| tichete culturale | salarizare | test_tichet_cultural.py test_salarizare.py | √ 02.08 (FUNCTIONALITATE NOUA livrata; temeiuri VERDE anaf_surse/RAPORT_verificare_temeiuri.md: impozit 10% art.76(3)h/v13, CAS nu art.142r/v10, CASS nu art.157(2)/v11 [DIVERGENTA vs masa], CAM nu 220^4(2)/v12, nu in plafon 33% v14, nominal 10-multiplu-50 art.22(2)/v15; plafon semestrial plafon_cultural() 220/450 si 250/490 confirmate primar, fereastra GRI oct2025-mar2026 BLOCATA; D112 camp E3_74 emis la nivel etalon prin impozit). Gard BILETE_VALOARE_TRATAMENT. | FISCAL | Legea 165/2018 art.21/22; CF art.76(3)h/142(r)/157(2)/220^4(2)/25(3)b3; ordine MF/MC 361/2680-2025 si 369/2624-2026 | test_plafon_cultural_ferestre_confirmate test_plafon_cultural_fereastra_gri_blocheaza test_cultural_impozit_fara_cass test_cultural_diferit_de_masa_pe_cass test_bilete_valoare_declara_toate_tratamentele |
| tichete cresa | salarizare | test_tichet_cresa.py test_salarizare.py | √ 02.08 (FUNCTIONALITATE NOUA livrata; tratament fiscal = ca CULTURAL: impozit 10% art.76(3)h, CAS nu 142r, CASS nu 157(2) [DIVERGENTA vs masa], CAM nu 220^4(2); nominal 10-multiplu-100 art.19(2); plafon 450/luna/copil art.19(1) baza confirmata, indexare 740 GRI verdict 17 BLOCATA cf regula de lant; D112 camp E3_72 etalon prin impozit). Gard BILETE_VALOARE_TRATAMENT + plafon_cresa. | FISCAL | Legea 165/2018 art.19; CF art.76(3)h/142(r)/157(2)/220^4(2) | test_plafon_cresa_450_per_copil test_cresa_impozit_fara_cass test_cresa_in_registru_fara_cass test_cresa_seteaza_peste_plafon_1_copil_blocheaza_indexarea test_cresa_db_roundtrip_baza_450 |
| nomenclator cod_oblig<->cod_bugetar | d100 | test_d100.py (+test_d710.py) | √ 03.08 (FIX cont bugetar obsolet. D100 mapa cod_oblig 121/103 la 20470101 - OBSOLET, inlocuit oficial cu 5503 din 26.07.2018 (d100_struct_anaf.txt:562), fara X-padare C(10). Coroborare: d101 (acelasi cod 103) si d112 emit deja 5503XXXXXX. FIX: COD_BUGETAR -> "5503XXXXXX" (sursa unica, d710 importa din d100). GARD anti-drop: cod_oblig nemapat -> ValueError (nu omite tacit atributul obligatoriu). Teste care cimentau 20470101 actualizate) | STRUCTURA | nomenclator ANAF D100 (cont unic 5503 din 26.07.2018, d100_struct_anaf.txt; cod_bugetar C(10) X-padat) | test_cod_bugetar_din_nomenclator |
| cota micro 121 (flag) | d100 | test_d100.py | √ 03.08 (VERIFICARE + gard. Generator CONFORM struct D100 poz.17a: micro (cod_oblig 121) emite cota="1", profit (103) fara cota (daca 121 atunci cota=1 altfel null). Rata micro pt suma = period-aware din registru (impozit_micro 1%%), separata de flag-ul structura cota="1". GARD bidirectional in build_xml: 121 fara cota="1" -> ValueError; cota pe alt cod -> ValueError (face imposibil XML respins, inclusiv apel direct)) | STRUCTURA | struct D100 poz.17a (cota N(1): daca cod_oblig=121 atunci cota=1 altfel null) | test_cota_micro_121_gard_bidirectional test_micro_are_cota_1_pe_obligatie |
| checksum totalPlata_A (R11b) | d100 | test_d100.py | √ 03.08 (VERIFICAT + aliniere sursa unica. Valoarea emisa (totalPlata_A = 2x sum(suma_dat), DUK R11b) era CORECTA. DAR divergenta: res.total_plata_a era 1x sum, iar build_xml recalcula 2x INDEPENDENT (nu din res) - d100 exceptia de la conventia tuturor declaratiilor (d101/d390/d710 emit res.total_plata_a). FIX: res.total_plata_a = checksum (2x sum) + build_xml il emite (o sursa). Gard: res==XML==2x sum) | STRUCTURA | DUK regula R11b (totalPlata_A = suma_dat+suma_ded+suma_plata+suma_rest = 2x sum la obligatia simpla) | test_totalplata_a_checksum_r11b_din_res |
| scadente/nr_evidenta | d100 | test_d100.py | √ 03.08 (VERIFICARE + gard scadenta. nr_evidenta CONFORM struct (23 poz: 10+cod_oblig+01+LLAA+ZZLLAA+0+0+00+control; poz.18="0" dupa fix R16), gardat de 3 teste. scadenta = 25 a lunii urmatoare perioadei (struct poz.15), format ZZ.LL.AAAA - conform pt 121/103 trimestrial (Q1-Q3 25 apr/jul/oct, Q4 25 ian). Lipsea test scadenta -> gard adaugat. Obs: alte reguli scadenta (25/12, 28-29/07) sunt pt obligatii nengerate de d100; Q4 profit definitivare = D101) | STRUCTURA | struct D100 poz.15 (scadenta 25 luna urmatoare, ZZ.LL.AAAA) + poz.20 (nr_evid 23 poz + suma control) | test_scadenta_25_luna_urmatoare_perioadei test_nr_evid_cifra_de_control |
| structura P1-P53 | d101 | test_d101.py | √ 03.08 (VERIFICAT CONFORM SI COMPLET fata de OPANAF 206/2025. Toate formulele derivate P3-P53 coincid rand-cu-rand (P3=P1-P2, P7=P3+P6, P10=P7+P8-P9, P16=SP11..15, P22=P10-P16-P21, P34=SP23..33, P38a, P40 profit impozabil, P41=P411+P412, P48 dispecerat P46/P47, P52/P53, totalPlata_A=sum P1..P53 fara sub-randuri din care). P13 rezerva legala (A1) corect. d_grup tratat. FARA fix - deja gardat de golden lant formule + proba DUK (§9 acoperit)) | STRUCTURA | OPANAF 206/2025 (D101_A600 v10, structura P1-P53 + totalPlata_A poz.20) | test_golden_lant_formule_oficiale test_d101_reconstructie_proba_duk_valid |
| cota profit 16% + IMCA | d101 | test_d101.py | √ 03.08 (cota 16% verificata CF art.17 + COTE impozit_profit, test cu temei; IMCA CF art.18^1 IMPLEMENTAT: formula 1%x(VT-Vs-I-A) negativ->0 + prag 50mil euro + wiring P47/comparatie P48 + PROBA DUK. Gap minor: cota din COTA_STANDARD literal, nu cota() - rutare follow-up) | FISCAL | CF art.17 (cota 16%); CF art.18^1 (IMCA); OUG 8/2026 | test_golden_lant_formule_oficiale test_cota_profit_16pct_din_cota_cu_temei test_imca_formula_1pct test_datoreaza_imca_prag_50mil_euro test_imca_wiring_p47_si_comparatie_p48 test_imca_d101_duk_valid |
| R17 Data_S / termen | d101 | test_d101.py | √ 03.08 (neconformitate aparenta -> REZOLVATA cu decizie Costin + act gasit. Scadenta D101 e period-aware; parea inversata fata de lege, dar valoarea validatorului (2022-2025 -> 25 iunie) e LEGAL CORECTA via OUG 153/2020 art.I alin.(13) lit.a (derogare art.42, aplicabil 2021-2025, MO 817/04.09.2020) - prima cercetare ratase actul. 2026 -> 25 martie baza art.42 = ce cere jar-ul DUK; OUG 8/2026 il muta la iunie de la fiscal 2026 cand validatorul se actualizeaza (depunere in 2027; proba DUK pe 2026 va semnala). Decizie: tool-ul urmeaza validatorul pe ambele ramuri. Temeiuri corectate OPANAF->OUG 153/2020 + Legea 227/2015 art.42) | STRUCTURA | OUG 153/2020 art.I alin.(13) lit.a (2022-2025 iunie) + Legea 227/2015 art.42(1) baza + OUG 8/2026 art.6 pct.12 (2026 iunie viitor) | test_scadenta_LL_plus_3_pentru_an_peste_2025 |
| amortizare | d101 | test_d101.py | √ 03.08 (tratamentul amortizarii in d101 aliniat CF art.28: amortizare FISCALA P11 dedusa in P16, amortizare CONTABILA P28 adaugata inapoi in P34; prag MF amortizabil 5000 lei art.28 alin.2b/OUG8-2026. Golden cu temei. DATORIE separata MF/D406: degresiva/accelerata necalculate - xfail test_datorie_mf_metode_amortizare, impact pe contabil/SAF-T nu pe d101) | FISCAL | CF art.28 (amortizarea fiscala); OUG 8/2026 (prag 5000) | test_amortizare_ajustare_fiscala_art28 test_mf_prag_amortizabil_5000_art28 |
| baze contributii (CAS/CASS/imp/CAM) | d112 | test_d112.py | √ 03.08 (cotele salariale rutate PERIOD-AWARE prin cota() din COTE, nu literale: CAS 25% CF art.138 lit.a, CASS 10% CF art.156, impozit 10% CF art.78 alin.2, CAM 2.25% CF art.220^3 alin.1 - toate verificate VERBATIM la sursa. Value-preserving: golden D112 + DUK neschimbate. Gard anti-hardcode pe sursa functiilor) | FISCAL | CF art.138 (CAS 25%); CF art.156 (CASS 10%); CF art.78 (impozit 10%); CF art.220^3 (CAM 2.25%) | test_cotele_contributii_din_cote_cu_temei test_d112_ruteaza_cotele_prin_cote_nu_literale test_d112_cas_cass_valori_neschimbate_dupa_rutare |
| concedii medicale (asiguratB3/D) | d112 | test_exces_vacanta_d112.py test_pull_declaratii.py | √ 02.08 — D-field per cod: D_9/D_10/D_11(cod 06 urgenta, HG 423/2020, C(3) obligatoriu daca D_9=06)/D_23; cod 08 maternitate Rd.3 (C2_31/32/34/36) 100% FNUASS; taxe CM prin taxe_cm canonic. DUK VALID: cod 01/06/08 (raw, 02.08). DATORIE declarata (test_datorie): cod 05 sub-randuri infectocontagioase Rd.1.1-1.4 nedefalcate (emise 0, corect cat timp nu exista cod 05 in luna) | FISCAL | OUG 158/2005; structura D112 (D_11 cf HG 423/2020) | test_d112_cod06_urgenta_valid_duk test_d112_maternitate_cod08_c2_rd3 test_d112_urgenta_cod06_emite_d11 |
| suprataxare prag | d112 | test_d112.py | √ 02.08 (bump: V3 salariu_minim 2025 corectat 3700->4050 HG 1506/2024 FIX5 dupa √ 29.07; praguri COTA-DERIVATE nu literal - salarizare.py:129 sm=cota, d112 _sal_minim=cota; recalculat sm 2025/2026H1=4050 2026H2=4325 identic cu codul: (4050-300-2000)*25%=437.50, (4325-200-2000)*25%=531.25) | FISCAL | CF art.146 alin.(5^6) | test_sub_minim_nescutit_emite_asigexc2_fara_motivexc test_peste_minim_asigexc_zero |
| rotunjire aritmetica (A91b) | d112 | test_d112.py | √ 03.08 (rotunjirea contributiilor = ARITMETICA/half-up, nu bancara - ANAF structura D112 'Contributiile se rotunjesc aritmetic', DUK regula A91b CAM 112->113. _d112int (ROUND_HALF_UP) pe toate contributiile. REPARAT: minimul part-time (prag_zile, cas_min_pt, cass_min_pt) folosea round() BANCAR - _d112int ulterior era no-op pe valoarea deja intreaga, deci bancarul ajungea in B4_*P declarat; prag_zile=1226 -> CAS 306 in loc de 307. Rutat prin _d112int, proba pe valori reale) | FISCAL | ANAF structura D112 0126_030226 (rotunjire aritmetica); DUK regula A91b | test_rotunjire_aritmetica_nu_bancara test_partime_minim_rotunjeste_aritmetic_nu_bancar test_partime_minim_foloseste_d112int_nu_round_bancar test_toate_generatoarele_rotunjesc_aritmetic |
| limita text 75 | d112 | test_d112.py | √ 03.08 (2 neconformitati de trunchiere reparate fata de structura D112 0126_030226. (A) numeAsig/prenAsig (nume/prenume salariat C75) erau doar escapate, NEtrunchiate -> nume >75 respins; (B) functie_declar are C(50) nu C(75), se trunchia la 74 in loc de 50. Reparat: _d112esc(_t(...)) pe nume salariat + _t(...,50) pe functie. Restul campurilor (nume_declar/prenume_declar C75, den) erau deja corecte) | STRUCTURA | structura ANAF D112 0126_030226: numeAsig/prenAsig C(75), functie_declar C(50) | test_limita_75_asigurat_si_functie_declar_50 |
| nomenclator cod_oblig | d112 | test_d112.py | √ 03.08 (VERIFICAT CONFORM. Toate 6 codurile cod_oblig<->cod_bugetar din add_oblig coincid cu nomenclatorul oficial ANAF (structura D112 Nomenclator 3): 602/412/432 -> 5503XXXXXX, 480 CAM -> 20470300XX (distinct), 458/459 suportat angajator -> 5503XXXXXX. Fara neconformitate. Testul vechi verifica doar codOblig ca substring - lipsea gardul pe cod_bugetar; adaugat) | STRUCTURA | structura ANAF D112 Nomenclator 3 (Obligatii de plata BS/BASFS): 602/412/432/480/458/459 + coduri bugetare | test_cod_oblig_pereche_cu_cod_bugetar_corect test_codurile_de_obligatie_corecte |
| sect_II tip_venit (impozit retinut) | d205 | test_d205.py | √ 03.08 (structura sect_II + tip_venit verificate la sursa anaf_surse/d205_struct_anaf.txt = OPANAF 102/2025: tip_venit=08 '1.a venituri din dividende' cu tip_plata=2 + divid_D/divid_P + baza1/imp1; sect_II frate cu benef; totalPlata_A = suma tuturor campurilor. REPARAT impozit retinut pe dividende: era hardcodat 10%, acum PERIOD-AWARE prin cota('impozit_dividend') - 16% de la 01.01.2026 CF art.97/Legea 141/2025 (era 10% pana in 2025). Proba DB reala: 50000 div 2026 -> 8000, nu 5000; proba DUK valida) | FISCAL | OPANAF 102/2025 (structura D205); CF art.97 + Legea 141/2025 (impozit dividende 16% de la 2026) | test_d205_contract_pull_genereaza_perioada test_impozit_dividend_period_aware_cf_art97 test_d205_rata_dividend_din_cota_nu_hardcodat test_d205_contract_proba_duk_valid |
| checksum totalPlata_A | d205 | test_d205.py | √ 03.08 (VERIFICAT valoarea emisa CONFORMA + aliniere sursa unica. totalPlata_A emis = nrben+Tcastig+Tpierd+T_VB+T_GAR+Tbaza+Timp (formula EXACTA ANAF struct D205, OPANAF 102/2025, l.80-85) - corect, DUK-valid. DAR capcana latenta clasa-d100: res.total_plata_a tinea DOAR Timp, iar build_xml recalcula checksum-ul INDEPENDENT - d205 outlier de la conventia tuturor declaratiilor (d100/d101/d300/d390/d710 emit res.total_plata_a). FIX red->green: calcul_d205 calculeaza checksum-ul -> res.total_plata_a; build_xml il EMITE din res (o sursa). Gard: res==header emis==suma sect_II din XML) | STRUCTURA | ANAF struct D205 OPANAF 102/2025 l.80-85 (totalPlata_A=suma nrben+Tcastig+Tpierd+T_VB+T_GAR+Tbaza+Timp); DUK proba | test_total_plata_a_res_egal_checksum_emis test_totalPlata_A_e_suma_tuturor_campurilor_sect_II test_d205_contract_proba_duk_valid |
| trunchiere den/adresa | d205 | test_d205.py | √ 03.08 (NECONFORMITATE reparata, probata DUK. Campurile text D205 se trunchiau la 75 (default text_anaf), dar struct ANAF OPANAF 102/2025 + validatorul DUK dau: den C(200), adresa C(1000), functie_declar C(50), den1 beneficiar C(100). den/adresa OVER-trunchiate 76-200/76-1000 = pierdere de date (D205 absent din lista 27.07 de respingere >75); functie 51-75 si den1 >100 emiteau si ANAF le RESPINGEA. Probe DUK: den 200 valid/201 erori, adresa 1000/1001, functie 50/51, den1 100/101. FIX: limite explicite _t(...,200/1000/50/100) in build_xml. Proba DUK pe inputuri lungi trunchiate = valid) | STRUCTURA | ANAF struct D205 OPANAF 102/2025 (den C200, adresa C1000, functie_declar C50, den1 C100); probat direct pe validatorul DUK (boundary 200/201, 1000/1001, 50/51, 100/101) | test_trunchiere_den_adresa_functie_den1_la_limitele_anaf test_trunchiere_lunga_ramane_duk_valida |
| rotunjire | d205 | test_d205.py | √ 03.08 (sumele fiscale D205 - baza1/imp1/dividende/parte - se rotunjesc ARITMETIC prin _i = Decimal.quantize(ROUND_HALF_UP), aceeasi regula ANAF ca la D112 (validator A91b). Deja corect prin constructie; GARDAT acum: _i adaugat in gardul cross-generator de identitate + proba d205-specifica _i(2.5)=3/_i(0.5)=1 aritmetic nu bancar. Fara schimbare de comportament) | FISCAL | ANAF structura D205 (OPANAF 102/2025) + regula A91b (rotunjire aritmetica) | test_d205_rotunjeste_aritmetic_nu_bancar test_rotunjirea_e_identica_intre_generatoare |
| cote TVA -> randuri | d300 | test_d300.py | √ 03.08 (maparea cotelor pe randuri verificata la sursa structura_D300_v12.0.0 + proba DUK: LIVRARI 21->Rd.9, 11->Rd.10, 9(art.III L141/2025)->Rd.11 - corecte. REPARAT ACHIZITII DEDUCTIBILE: 11% era la R74 (=Rd.24.1 cota 19% legacy, marja 18-20% - respins DUK) -> mutat la R23 (Rd.25, DUK valid); 9% era la R76 (=taxare inversa Rd.27.4, respins DUK + pierdut din R27) -> scos din auto, semnalat pentru declarare MANUALA (validatorul instalat respinge si R75 din v12). DATORIE: 9% deductibil auto - xfail test_datorie_d300_9pct_deductibil_auto) | FISCAL | structura_D300_v12.0.0 (marja randuri) + Legea 141/2025 (cote 21/11/9) | test_cote_tva_maparea_pe_randuri_d300 test_9pct_deductibil_nu_emite_rand_invalid_si_avertizeaza test_cote_tva_d300_proba_duk_valid |
| exigibilitate / TVA la incasare | d300 | test_d300.py (+test_tva_incasare.py) | √ 03.08 (IMPLEMENTAT: firma pe sistem -> D300 calculeaza exigibilitatea din DECONTARI - incasari cont 4111 / plati cont 401 validate in perioada, suta marita art.282(8), proportional pe plati partiale art.282(3); deducere amanata la plata art.297(2-3); taxare inversa exclusa art.282(6). Sursa = note contabile legate de factura, nu emiterea/platita_la. Fara cap 90 zile - eliminat de OUG 8/2026. Proba DB reala + DUK) | FISCAL | CF art.282 + art.297 (OUG 8/2026); plafon 5M COTE | test_tva_la_incasare_exigibilitate_pe_decontari_suta_marita test_tva_la_incasare_partial_proportional test_tva_incasare_exigibil_la_decontare_nu_la_emitere test_tva_incasare_d300_proba_duk_valid |
| taxare inversa | d300 | test_d300.py | √ 03.08 (CF art.331: beneficiarul auto-taxeaza; se declara MANUAL in rd.12 colectata + rd.27/R25 deductibila = net zero. REPARAT: R12_ lipsea din allow-list-ul manual -> rd.12 era silentios ignorat (sub-declarare); adaugat. Proba DUK pe decont echilibrat rd.12=rd.27 + gard anti-drop. GRI reverse-charge D300/D394 inchis - reconfirmat la sursa art.331 + structuri D300 Rd.12 / D394 tip bun) | FISCAL | CF art.331; structura D300 Rd.12; structura D394 (bun/defalcare) | test_taxare_inversa_rd12_se_declara_manual test_taxare_inversa_r12_fara_fix_ar_fi_dropped test_taxare_inversa_d300_proba_duk_valid |
| pro-rata deducere | d300 | test_d300.py | √ 03.08 (CF art.300, regim mixt: deducere pro-rata cand nu se tin evidente separate. D300 CORECT prin constructie: R31_2 = Ajustari conform pro-rata (Rd.33 struct v12) = -(taxa dedusa x fractia nedeductibila); total dedus R32 = R28 x pro_rata/100 - NU scalare directa. Verificat + GARDAT: pro_rata=80% -> R28=210, R31=-42, R32=168; pro_rata=100 fara ajustare; proba DUK) | FISCAL | CF art.300 (deducere regim mixt); structura D300 Rd.33 (ajustari pro-rata) | test_pro_rata_ajustare_deductibila_art300 test_pro_rata_100_fara_ajustare test_pro_rata_d300_proba_duk_valid |
| randuri / checksum | d300 | test_d300.py |  | STRUCTURA |  |  |
| rotunjire aritmetica | d300 | test_d300.py | √ 03.08 (sumele fiscale D300 se rotunjesc ARITMETIC prin _int = numar_fiscal.quantize(ROUND_HALF_UP), regula A91b ANAF. Deja in gardul de identitate cross-generator (a==b==c==d cu d390/d112/d205); adaugat proba d300-specifica _int(2.5)=3/_int(0.5)=1 aritmetic nu bancar. Fara schimbare de comportament) | FISCAL | regula A91b (rotunjire aritmetica ANAF) | test_d300_rotunjeste_aritmetic_nu_bancar test_rotunjirea_e_identica_intre_generatoare |
| ajustari | d300 | test_d300.py | √ 03.08 (CF art.304 regularizari + art.305 ajustari. REPARAT: randurile de ajustare/regularizare R29 (restituiri cumparatori straini Rd.31), R30 (regularizari taxa dedusa Rd.32), R35 (sold reportat), R36 (diferente inspectie Rd.38) lipseau din allow-list-ul manual -> erau silentios aruncate (ajustari nedeclarate). Adaugate: R29/R30 intra in total dedusa R32, R35/R36 in R37 cumulat. Proba DUK + gard anti-drop) | FISCAL | CF art.304 (regularizari) + art.305 (ajustari); structura D300 Rd.31/32/37/38 | test_ajustari_regularizari_deductibila_se_declara test_regularizari_rezultat_r36_intra_in_cumulat test_ajustari_r30_fara_fix_ar_fi_dropped test_ajustari_d300_proba_duk_valid |
| tipuri operatiune 1-5 | d301 | test_d301_rollup.py | √ 03.08 (OPANAF 592/2016: maparea tip->sectiune verificata la sursa struct - 1=S1 achizitii intracom bunuri, 2=S2 mijloace transport noi (bifa mij), 3=S3 produse accizabile, 4=S4 servicii, 5=S4.1 servicii art.150 subset din S4. Rollup S4.1->S4 deja testat; adaugat gard tipuri 1/2/3 pe sectiuni proprii + proba DUK cu TOATE cele 5 tipuri) | FISCAL | OPANAF 592/2016 (structura D301, sectiuni 1-4.1) | test_tipuri_1_2_3_pe_sectiuni_proprii test_toate_tipurile_1_5_proba_duk_valid test_tip5_se_preia_in_sectiunea_4 |
| rollup S4.1->S4 | d301 | test_d301_rollup.py | √ 03.08 (OPANAF 592/2016: in Sectiunea 4.1 se preiau DIN Sectiunea 4 serviciile intracom art.150 - S4.1 e SUBSET al S4, deci fiecare op tip 5 se preia si in S4. Verificat COMPLET de test_d301_rollup.py: S4 contine S4.1, S4=S4.2+S4.1, TVA datorat o singura data (nu se dubleaza), checksum totalPlata_A include 4.1 prin definitie, fara tip5 nu se inventeaza rollup. Proba DUK cu toate tipurile - validatorul impune rollup-ul) | FISCAL | OPANAF 592/2016 (instructiuni formular 301, S4.1 preluat din S4) | test_tip5_se_preia_in_sectiunea_4 test_tip5_plus_tip4_cumuleaza_in_sectiunea_4 test_tva_datorat_o_singura_data_desi_checksum_include_4_1 test_toate_tipurile_1_5_proba_duk_valid |
| checksum totalPlata_A (R28) | d301 | test_d301_rollup.py |  | STRUCTURA |  |  |
| baza = val x curs | d301 | test_d301_rollup.py (+test_d301_curs.py) | √ 03.08 (CF art.290 alin.(2): baza in valuta = elemente_valuta x curs BNR/BCE valabil la exigibilitate; rotunjire ROUND_HALF_UP la leu intreg = struct ANAF baza integer. Formula+rotunjire CORECTE. REPARAT clasa "valoare gresita tacuta": generatorul (d301.py) + reader-ul grilei (d301_operatiuni_api.lista) faceau calc_baza(..., curs or 1) -> curs absent/0 pe EUR (moneda default) devenea tacit 1 -> baza subevaluata la ANAF fara eroare. calc_baza ridica acum pe curs None/<=0 (chokepoint); scos or 1 din generator+reader; scos DEFAULT 1 din schema (tenant nou fail-loud). Proba: 1000x4.9770=4977, EUR fara curs->ValueError, RON=1->1234. Poarta adauga() valida deja curs>0) | FISCAL | CF art.290 alin.(2) (curs de schimb pt baza in valuta) + OPANAF 592/2016 (structura D301) | test_calc_baza_refuza_curs_absent_sau_nul test_generator_d301_refuza_curs_lipsa_pe_valuta test_lista_api_refuza_curs_nul_nu_fabrica_1 test_calc_baza_corect_pe_curs_valid |
| cota TVA | d301 | test_d301_rollup.py (+test_d301_cota.py) | √ 03.08 (CF art.291: standard alin.(1) 21%% de la 01.08.2025 / 19%% inainte = period-aware CORECT prin common.cota; redusa alin.(2) 11%% de la 01.08.2025; alin.(8) cota achizitiei intracom = cota livrarii interne, deci redusa se aplica in D301. REPARAT: cota redusa era literal 11 indiferent de perioada -> gresita pt luni < 08.2025 (atunci 9%%/5%%, comasate de Legea 141/2025). Fix: redusa din common.cota(tva_redusa), OMISA cand neconfigurata (nu se ofera 11%% fals; adauga o respinge -> nu se persista tva eronat). Proba: 2026 [21,11,0] neschimbat, 2025-06 [19,0]. DECIZIE DE PRODUS deschisa: 9%%/5%% istorice coexistente cer remodelare COTE) | FISCAL | CF art.291 alin.(1)(2)(8) + Legea 141/2025 (comasare cote reduse) | test_cote_2026_standard_21_redusa_11_scutit_0 test_cote_redusa_period_aware_nu_ofera_11_pe_perioada_veche test_adauga_respinge_cota_11_pe_perioada_veche |
| tipuri operatiune IC (L/A/P/S) | d390 | test_d390.py | √ 03.08 (VERIFICARE - fara fix necesar. TIPURI=(L,T,A,P,S,R) d390.py:50 = EXACT nomenclatorul OPANAF 705/2020 (anaf_surse/d390_struct_anaf.txt): L livrari IC bunuri, T triunghiulare, A achizitii IC bunuri, P prestari IC servicii, S achizitii IC servicii, R livrari IC regim special agricultori. codO obligatoriu L/T/P/R (:206), totalPlata_A (:177), gard anti-drop manual (:159 raise) - conforme. GARD-PIN nou: TIPURI==lista oficiala, mutant probat. Obs tangentiale: reclasificare fallback tacit L/A pe tip invalid din DB (misclasif, nu drop); XI tara post-Brexit tine de clusterul nomenclator tari) | FISCAL | OPANAF 705/2020 (nomenclator tip operatiune D390) | test_tipuri_operatiune_sunt_exact_nomenclatorul_oficial_opanaf_705_2020 test_d390_manual_tip_necunoscut_ridica_nu_dispare test_reclasificare_ignora_tip_invalid |
| nomenclator tari (HR->CR) | d390 | test_d390.py |  | STRUCTURA |  |  |
| rotunjire aritmetica (A91b) | d390 | test_d390.py | √ 03.08 (VERIFICARE - fara fix. d390._int (d390.py:59) = ROUND_HALF_UP (schimbat de la round() bancar 27.07). ANAF cere half-up nu bancar (DUK regula A91b - referinta validator, nu act normativ §3.1). Deja gardat dublu: identitate cross-generator (test_rotunjirea_e_identica_intre_generatoare importa d390._int) + scan anti-round() bancar (test_toate_generatoarele_rotunjesc_aritmetic). Adaugat proba d390 pe valoare: _int(0.5)=1/2.5=3/112.5=113 (mutant bancar 0/2/112)) | FISCAL | DUK regula A91b (rotunjire aritmetica ANAF - referinta validator) | test_d390_rotunjeste_aritmetic_nu_bancar_A91b test_rotunjirea_e_identica_intre_generatoare test_toate_generatoarele_rotunjesc_aritmetic |
| reclasificari manuale | d390 | test_d390.py | √ 03.08 (FIX asimetrie read-side. Scrierea (salveaza_reclasificare) valida tip+DIRECTIE (emisa:L/T/P/R, primita:A/S); citirea (calcul_d390+operatiuni_auto) facea fallback TACIT la default pe tip invalid, fara verif directie -> misclasificare tacuta daca un override ocolea API (migrare/DB). Contrazicea gardul liniilor manuale (:159). Fix: TIPURI_DIRECTIE mutat in d390.py (sursa unica, import in API fara ciclu) + helper _reclasificare_tip valideaza direciția si RIDICA in ambele cai citire. Pe date valide 0 schimbare. Proba: recl "Z"/"A-pe-emisa" -> ValueError) | FISCAL | DECIZII 21.07 (tranzitie directie: achizitia nu devine livrare) + OPANAF 705/2020 (semantica L/A/P/S/T/R) | test_reclasificare_tip_invalid_ridica_nu_revine_tacit test_reclasificare_directie_gresita_ridica test_reclasificare_muta_tipul_fara_dubla_numarare |
| exigibilitate / prag | d390 | test_d390.py (+test_pull_declaratii.py) | √ 03.08 (VERIFICARE - conform in cazul normal. D390 incadreaza pe data_emitere (pull, fereastra [M-01,(M+1)-01)); CF art.283/284: exigibilitatea intracom = DATA EMITERII facturii, deci data_emitere = exigibilitate -> corect. CF art.325 alin.(4): fara prag valoric, doar lunile cu exigibilitate; d390_are_operatiuni + refuz pe zero = conform. Gard temporal nou pe fereastra pull (golul: testele calcul ocoleau pull). EDGE-CASE consemnat (decizie schema): plafonul "ziua 15 a lunii urmatoare faptului generator cand factura intarzie" (art.284) neimplementabil - facturi n-are data faptului generator) | FISCAL | CF art.283 (exigibilitate livrari IC) + art.284 (achizitii IC) + art.325 (recapitulativa, fara prag) | test_d390_pull_incadreaza_pe_data_emitere_exigibilitate |
| tipuri operatiune (pct.215) | d394 | test_d394.py |  | STRUCTURA |  |  |
| tip_partener | d394 | test_d394.py |  | STRUCTURA |  |  |
| cote acceptate | d394 | test_d394.py | √ 03.08 (VERIFICARE - conform, d394 e modelul-tinta al lui d301. cota_standard (d394.py:258) period-aware din common.cota (evita int(0.21)=0); cotele operatiunilor validate contra set fix d394.COTE=(0,5,9,11,19,20,21,24) = validator ANAF v5 OPANAF 2194/2025 (21/11 de la 01.08.2025) peste structura 2020; agregare pe cota reala (rectificative vechi -> 19/9/5). Fara literal hardcodat. Garduri: pin set v5 + CROSS-MODUL common.COTE tva_* subseteaza d394.COTE (cota noua in common neacoperita -> cade)) | FISCAL | OPANAF 2194/2025 (validator v5 cote) + structura D394 (cota in 0,5,9,11,19,20,21,24) | test_d394_cote_acceptate_sunt_setul_validatorului_v5 test_d394_cote_acopera_toate_cotele_tva_din_common test_cota_standard_vine_din_sursa_unica |
| rezumat1 campuri complete | d394 | test_d394.py |  | STRUCTURA |  |  |
| nomenclator codPR (art.331) | d394 | test_d394.py |  | STRUCTURA |  |  |
| taxare inversa | d394 | test_d394.py (+test_datorie.py) | √ 03.08 (11/12 CONFORM + 1 DATORIE. art.331 alin.(2) are 12 litere a-l; codul implementeaza 11 (a-k) corect (motor taxare_inversa.CATEGORII + mapare d394.CODPR 21-31). NECONFORMITATE: lit.l GAZE NATURALE lipseste din ambele. CORECTARE blocata - codPR D394 gaze nu e in sursele repo (Ghid 2016, anterior Legii 296/2020; 32-35 rezervate tip2). §3 nu se inventeaza. GARD anti-regresie: CATEGORII subseteaza CODPR (fixul pe jumatate pica). DATORIE xfail(strict) gaze in test_datorie. Input cerut: codPR gaze post-2021) | FISCAL | CF art.331 alin.(2) lit.a-l (12 categorii) + alin.(6) expirare + structura D394 op11 (codPR) | test_toate_categoriile_taxare_inversa_au_codpr_d394 test_datorie_gaze_naturale_taxare_inversa_art331_lit_l |
| totalPlata_A (R17) | d394 | test_d394.py |  | STRUCTURA |  |  |
| plan conturi pe norma | d406 | test_limita_text_anaf.py |  | STRUCTURA |  |  |
| UoM UN/ECE | d406 | test_limita_text_anaf.py |  | STRUCTURA |  |  |
| MovementType nomenclator | d406 | test_limita_text_anaf.py |  | STRUCTURA |  |  |
| BaseRate (encoding pro-rata) | d406 | test_limita_text_anaf.py |  | STRUCTURA |  |  |
| registration_number (00+CUI) | d406 | test_limita_text_anaf.py |  | STRUCTURA |  |  |
| SourceDocuments (facturi reale, PARTIAL) | d406 | test_d406.py | √ 03.08 (FIX period-awareness. Partea solida (27.07): SalesInvoices/PurchaseInvoices cu linii reale pe produs, reconciliate, DUK-valid. REPARAT: TAXCODE_LIVRARI_PRE_2025_08 era DEFINIT dar nefolosit -> pull() emitea mereu codurile post indiferent de data (19%@luna veche -> 310312 taxare inversa gresit). Helper _taxcode_livrari period-aware pe data_emitere la ambele situri livrari; gard. Docstring stale actualizat. OBSERVATII (DECIZII 03.08): Payments gol=datorie pe date, TaxCode achizitii grosier, adresa placeholder, lipsa golden) | FISCAL | Legea 141/2025 (coduri TaxCode livrari 01.08.2025) + structura D406/SAF-T | test_taxcode_livrari_period_aware |
| structura XSD (Header/MasterFiles/GLE) | d406 | test_limita_text_anaf.py |  | STRUCTURA |  |  |
| structura declaratie710 | d710 | test_d710.py |  | STRUCTURA |  |  |
| nomenclator COD_BUGETAR | d710 | test_d710.py |  | STRUCTURA |  |  |
| checksum R11b | d710 | test_d710.py |  | STRUCTURA |  |  |
| R15 termen definitivare | d710 | test_d710.py |  | STRUCTURA |  |  |
| scadente | d710 | test_d710.py |  | STRUCTURA |  |  |
| plafon diurna neimpozabila | deconturi | test_deconturi.py (+test_datorie.py) | √ 03.08 (calcul CURENT CONFORM + datorie istorica. Plafon = min(2,5x diurna bugetara; 3 salarii/zile lucratoare) x zile = conform CF art.76 alin.(4^1) pt 2023+ (verificat la sursa). Adaugat gard golden (lipsea). NECONFORMITATE period-awareness: _VARIANTE_PLAFON_DIURNA are o singura varianta (2018) care aplica retroactiv valorile de azi (23 lei + cap 3-salarii intrat 2023). Fix BLOCAT: valorile HG diurna istorice nu-s in surse; §3 nu se inventeaza. Datorie xfail strict; input cerut HG 714/2018 istoric) | FISCAL | CF art.76(2) lit.k + alin.(4^1); HG 714/2018; HG 518/1995; Legea 72/2022 (cap 3-salarii) | test_plafon_diurna_curent_conform_art76 test_plafon_diurna_capul_3_salarii_musca_pe_salariu_mic test_datorie_plafon_diurna_period_aware_istoric |
| credit sponsorizare / D177 | sponsorizari | test_operatiuni_speciale.py (+test_datorie.py) | √ 03.08 (PROFIT CONFORM + observatii. Credit profit = min(0,75%% CA; 20%% impozit) + registru = conform CF art.25 alin.(4) lit.i (verificat la sursa); report 7 ani corect eliminat (2022). Gardat de test_operatiuni_speciale.py. NECONFORMITATE micro: credit=0 la orice data desi 2019-2023 avea credit (fostul art.56 alin.1^5 abrogat OUG 115/2023) - fix blocat pe text istoric neconsolidat, DATORIE xfail strict. D177 formular ABSENT = decizie de produs (Ordin 3562/2024). Endpoint neperiodizat = observatie) | FISCAL | CF art.25(4) lit.i (profit) + fostul art.56 alin.1^5 (micro, abrogat OUG 115/2023) + Ordin ANAF 3562/2024 (D177) | test_plafon_dublu_min_ca_impozit test_credit_sub_plafon_lasa_redirectionabil test_micro_fara_credit test_beneficiar_neinscris_fara_credit |
| rezerva legala | motor | test_operatiuni_speciale.py | √ 03.08 (formula CONTABILA conforma + deductibilitate fiscala = decizie produs. Rezerva contabila (motor.py: 5% profit, plafon cumulat 20% capital - rezerva existenta) = corecta structural (Legea 31/1990 art.183, OMFP 1802/2014 pct.421), period-aware. Adaugat gard golden pe valoare (lipsea). NECONFORMITATE: deductibilitatea FISCALA CF art.26(1)a (baza = profit + cheltuiala impozit, plafon 20% capital subscris/varsat) LIPSESTE - d101 P6 e input manual; = DECIZIE DE PRODUS (schimba declaratia profit). motor.py e cod mort (niciun apelant productie)) | FISCAL | Legea 31/1990 art.183; OMFP 1802/2014 pct.421 (rezerva contabila); CF art.26 alin.(1) lit.a (deducere fiscala) | test_rezerva_legala_5pct_plafon_20pct_capital |
| zilieri (impozit+CAS) | contracte_speciale | test_versionare_formule.py | √ 03.08 (FIX period-awareness CAS. Impozit 10%% (CF art.76(2) lit.r) + CASS 0 (nu-s in art.157) = CONFORME. REPARAT: codul aplica CAS 25%% din 2018-01-01, dar CAS pe zilieri exista legal doar de la 01.05.2019 (OUG 26/2019: adauga CF art.139(1) lit.s + Legea 52/2011 art.9^1; abroga exceptarea art.142 lit.t). 2 variante datate: 2018 doar impozit 10%% (net 90); 2019 CAS 25%% + impozit pe brut-CAS (net 67,5). Verificat /tmp/cf.txt. Obs: plafon zile 90/an doar in docstring, neaplicat) | FISCAL | CF art.76(2) lit.r (impozit) + art.139(1) lit.s (CAS, OUG 26/2019) + Legea 52/2011 art.9^1; CF art.142 lit.t (fosta exceptare) | test_calcul_zilier_dispecer_versionat |
| regim marja second-hand | tva_marja | test_versionare_formule.py | √ 03.08 (VERIFICARE - motor CONFORM. TVA pe marja = marja x cota/(100+cota) (suta MARITA, TVA extras din marja), conform CF art.312 alin.(4) (baza=marja EXCLUSIV taxa); marja negativa -> TVA 0. NU cota/100. (art.313=aur, codul citeaza corect 312). Lipsea test numeric -> gard golden (marja 400 cota 21 -> 69,42; negativa -> 0; cota 19 -> 63,87). OBSERVATII main.py: cota_ceruta nu valideaza period-aware; la_data nu se paseaza la motor) | FISCAL | CF art.312 alin.(4) (baza=marja exclusiv taxa; norme pct.86) | test_tva_marja_formula_suta_marita_art312 |
| regim marja turism | tva_marja_turism | test_versionare_formule.py | √ 03.08 (VERIFICARE - motor CONFORM. TVA = marja_taxabila x cota/(100+cota) suta marita (CF art.311 alin.4); scutire PROPORTIONALA non-UE (alin.5, coef cost_non_ue/cost_total) tratata; marja negativa -> 0; cota period-aware (param). Consistent cu art.312. Lipsea test numeric -> gard golden (tot UE 69,42; 50%% non-UE scutita 200/TVA 34,71; negativa 0). OBSERVATII: neintegrat in datorie.py (fara apelant); cota din default la integrare de luat period-aware) | FISCAL | CF art.311 alin.(4) (marja exclusiv taxa) + alin.(5) (scutire non-UE) | test_marja_turism_formula_suta_marita_si_scutire_non_ue_art311 |
| impozit dividend | decontari_asociati | test_impozit_dividend.py | √ 03.08 (FIX cote istorice. Mecanism period-aware corect (common.cota), DAR datele gresite: intrarea pre-2026 era 10%% (petic "else 10") - 10%% NU a fost niciodata cota pe dividende (e impozit pe VENIT art.78) -> 2023-2025 primeau 10%% in loc de 8%%. REPARAT: 3 intrari verificate la sursa - 5%% (2016-2022, Legea 227/2015+OUG 50/2015), 8%% (2023-2025, OG 16/2022), 16%% (2026, Legea 141/2025). Teste care cimentau 10%% actualizate la 8%%. Proba 2020->5%%, 2024->8%%, 2026->16%%) | FISCAL | CF art.97 alin.(7); OUG 50/2015 (5%% din 2016); OG 16/2022 (8%% din 2023); Legea 141/2025 (16%% din 2026) | test_impozit_dividend_period_aware_din_cote test_cota_dividend_si_lichidare_sursa_din_cote |
| contributii PFA (praguri CAS/CASS pe sm) | d212 | test_d212_reper.py | √ 03.08 (VERIFICARE - calcul CONFORM. CAS 25%% praguri 12/24 sm (CF art.148), CASS 10%% LINIAR 6 sm..plafon 60/72 sm (CF art.170 alin.1 - treptele doar pt venituri pasive, nu PFA), impozit 10%% pe net-CAS-CASS. sm period-aware. REPARAT citare temei: plafonul 72 sm 2026 era atribuit gresit "Legea 141/2025" -> corect Legea 239/2025 art.XII pct.19 (valoarea 72 sm corecta). Obs: calea 2026 dormanta in productie (poarta an=2025), de ridicat la 2027) | FISCAL | CF art.148-149 (CAS), art.170 alin.(1) (CASS PFA liniar), art.68-69 (venit net); Legea 239/2025 art.XII pct.19 (plafon CASS 72 sm 2026) | test_d212_reper_din_cota_nu_literal test_d212_apare_in_graful_salariu_minim |

Numărul nu e ținta. Ținta: fiecare cluster FISCAL să aibă cifra afirmată cu temei citat la sursă.

### V1 (01.08.2026) — inventar completat: reguli si teste care erau fara cluster

INAINTE: 62 clustere. DUPA: 69 (+7 orfane adaugate mai sus). Cifra corecta > cifra stabila.

(A) REGULI FISCALE ORFANE (marker TEMEI, modul absent din inventar) - ADAUGATE ca randuri: deconturi.plafon_diurna,
sponsorizari.plafon_credit+credit_sponsorizare, motor.rezerva_legala, contracte_speciale.calcul_zilier,
tva_marja.vanzare_marja, tva_marja_turism.marja_turism_special, decontari_asociati.cota_dividend. Toate produceau
o valoare fiscala fara sa apara in inventar. GOL: 5 au DOAR test de dispecer (versionare), niciun golden de
VALOARE la sursa (plafon_diurna, rezerva_legala, calcul_zilier, vanzare_marja, marja_turism_special) - regula
exista, nimic nu-i verifica cifra contra legii. De scris la reverificarea clusterului.

(B) TESTE care asertaza o valoare fiscala, absente din Functie(test) - clasificate (scan pe core/test_*.py):
- MECANISM (legitim fara cluster, verifica masinaria): test_graf_temei(4), test_temei_structurat(7),
  test_versionare_formule(13), test_expirare_cote_de_baza(5), test_inventar_a(3), test_perioada_indisponibila(3),
  test_impozit_dividend period-aware, test_tva_incasare plafon_pe_data.
- DE VALOARE, apartin unui cluster EXISTENT dar NELISTATE (test_salarizare, ~10): deducere
  (test_peste_plafon_deducere_zero, test_minim_difera_pe_semestru, test_brut_6000_fara_dependenti_sem2),
  concedii (test_cass_doar_pe_01_07_10, test_cm_cas_25pct_uniform, test_cm_prima_zi_diminuata_boala ...).
  NU le-am adaugat la clusterele BIFATE (√ deducere/concedii): garda anti-stale le-ar compara cu commitul √ si,
  daca vreuna s-a schimbat dupa, √-ul ar CADEA. HELD - de adaugat la reverificarea clusterului, cu proba ca nu
  cad √-urile (ramificatie: nu resetez singur).
- DE VALOARE, acum acoperite de orfanele adaugate: test_operatiuni_speciale(4 -> sponsorizari),
  test_cota_dividend (-> decontari_asociati).

### PAS 6 (02.08.2026) — au temei cele 7 orfane adaugate la V1?

Verificat mecanic (marker TEMEI in docstring + Temeiuri in inventar):
- AU marker TEMEI (6): deconturi.plafon_diurna, sponsorizari.plafon_credit+credit_sponsorizare, motor.rezerva_legala,
  contracte_speciale.calcul_zilier, tva_marja.vanzare_marja, tva_marja_turism.marja_turism_special.
- decontari_asociati.cota_dividend: FARA marker de functie - dar e CITITOR SUBTIRE (intoarce cota(impozit_dividend)),
  temeiul traieste in COTE (CF art.97 / Legea 141/2025) + Temeiuri in inventar. Nu e regula de formula -> nu cere marker.
CONCLUZIE: toate 7 clusterele orfane AU temei; niciunul fara. NU se bifeaza inca: 5 au DOAR test de dispecer
(versionare), fara golden de VALOARE la sursa (plafon_diurna, rezerva_legala, calcul_zilier, vanzare_marja,
marja_turism_special) -> in secventa de verificat. sponsorizari + decontari au teste de valoare (test_operatiuni_speciale
/ test_impozit_dividend), dar nebifate pana la reverificare la sursa cu golden calculat de mana.

LIMITA declarata (bilant_api): detectia vede doar reguli cu marker TEMEI sau cota(). O regula cu rate hardcodat
fara marker e invizibila - se inchide cu gardul GRI de literale la 0 (GARZI cat.3, LIPSA). De construit separat.

### V2 (01.08.2026) — graful vede tot? NU. Vede doar dependentele rutate prin cota()

Graful (`graf_temei`) leaga functie -> cota DOAR prin apeluri `cota("x")` in corp. Numarul de clustere cu
ZERO dependente in graf e MARE: cele 29 structurale (nomenclator/checksum/XML) - fundamental zero; iar dintre
cele 40 fiscale, majoritatea iau rata ca INPUT contabil (`manual`) sau o hardcodeaza -> tot zero in graf.
Dependenta e vizibila azi doar in familia salarizare (calcul_salariu/deducere/taxe_cm cheama cota). Deci
"graful vede tot" e FALS: e complet doar unde se foloseste cota().

3 clustere verificate MANUAL (citit codul):
1. checksum totalPlata_A (d100, STRUCTURA) - suma campurilor de obligatie, nicio valoare fiscala.
   VERDICT: FUNDAMENTAL (zero dependenta reala).
2. cota micro 121 (d100) - rata vine ca input (`manual`); DEFAULT hardcodat `Decimal("1")` (micro) /
   `Decimal("16")` (profit), ocoleste cota() (d100.py:239-247). VERDICT: DEPENDENTA ASCUNSA - cotele
   micro 1%/3% + profit 16% nu-s in COTE, graful e orb. Vizibil prin: mutare in COTE + cota(), sau gardul GRI.
3. d212_engine (PFA/D212 - modul ORFAN, absent din inventar, dar LIVE prin rip_api/control_fiscal_api) -
   hardcodeaza `PlafoaneD212(salariu_minim=4050)` ca reper anual (d212_engine.py:28-34). Toate pragurile
   CAS/CASS (12/24/60/72 sm) = multipli de acest 4050 literal. VERDICT: DEPENDENTA ASCUNSA pe salariu_minim -
   graful nu vede D212 depinzand de salariul minim. Valoarea e SURSA-VERIFICATA (11.07: reperul D212 = sm la
   1 ian, FIX pe an, deliberat neschimbat de majorarea 4325) - corecta azi, dar LINK-ul e invizibil.
   Vizibil prin: `cota("salariu_minim", date(an,1,1))` in loc de literalul 4050 (pastreaza semantica "fix pe an").

DEPENDENTE NEVAZUTE enumerate: (a) micro/profit rate default (d100); (b) d212 salariu_minim reper (+ toate
pragurile sm). CE LE FACE VIZIBILE: rutarea literalului prin cota()/COTE (specific) + gardul GRI de literale
fiscale la 0 (general, GARZI cat.3 LIPSA - inca de construit). Niciuna nu produce azi o cifra GRESITA (default pe
cale manuala; d212 sursa-verificat) - sunt goluri de VIZIBILITATE, nu buguri active. REPARATIE = gardul GRI
(campanie separata) + reroute; d212 e si orfan de inventar (de adaugat ca rand la fel ca V1).

## Estimare de efort pe clusterele nebifate (ESTIMARE, 01.08.2026 — NU angajament)

**Estimarea NU e criteriu de prioritizare.** Departajarea in secventa se face pe RISC (intra intr-o declaratie depusa la ANAF), nu pe efort - un cluster MIC si riscant se face inaintea unuia MARE si izolat. Estimarea serveste doar la a sti ORIZONTUL campaniei, nu ordinea. (Regula de ordonare: la sectiunea Secventa de verificare.)

Cerută de două ori, neapărută în raport. Estimare din COD + inventar, clusterele **NU** sunt verificate
aici — doar clasate pe efort. Calibrare din cele 7 atinse: **MARE** (o zi sau mai mult — multe reguli,
surse contradictorii, ca *deducere personală* √31.07) · **MEDIU** (câteva ore — mai multe valori/coduri,
ca *tichete* / *concedii medicale* PARTIAL 31.07) · **MIC** (sub o oră — puține valori, sursă clară:
nomenclatoare, checksum-uri, trunchieri, rotunjiri).

Nebifate: **55** din 62 (7 atinse: 5 √ + 2 PARTIAL). Repartiție efort × risc:

| Efort | FISCAL | STRUCTURA | Total | Interval/buc | Sub-total |
|---|---|---|---|---|---|
| MARE  | 6  | 0  | **6**  | 1–1,5 zile | 6–9 zile |
| MEDIU | 12 | 4  | **16** | 2–4 h       | ~4–8 zile |
| MIC   | 8  | 25 | **33** | 0,3–1 h     | ~1,5–4 zile |
| **Total** | **26** | **29** | **55** | | **≈ 12–21 zile** |

Centru realist: **~15 zile-om** de lucru focalizat (RED→verde→mutație→sursă per cluster), reductibil vezi caveat.

**MARE (6, toate FISCAL):** cota profit 16%+IMCA (d101) · amortizare (d101) · exigibilitate/TVA la încasare
(d300) · pro-rata deducere (d300) · ajustări (d300) · SourceDocuments facturi reale (d406).

**MEDIU (16):** *FISCAL(12)* tichete culturale · tichete creșă · baze contribuții CAS/CASS/imp/CAM (d112) ·
concedii medicale asiguratB3/D (d112) · sect_II tip_venit (d205) · cote TVA→rânduri (d300) · taxare inversă
(d300) · tipuri operațiune 1-5 (d301) · tipuri operațiune IC L/A/P/S (d390) · reclasificări manuale (d390) ·
exigibilitate/prag (d390) · taxare inversă (d394). *STRUCTURA(4)* tipuri operațiune pct.215 (d394) · rezumat1
câmpuri complete (d394) · plan conturi pe normă (d406) · structură XSD Header/MasterFiles/GLE (d406).

**MIC (33):** *FISCAL(8)* rotunjire A91b (d112) · rotunjire (d205) · rotunjire aritmetică (d300) · rollup
S4.1→S4 (d301) · bază=val×curs (d301) · cotă TVA (d301) · rotunjire aritmetică (d390) · cote acceptate (d394).
*STRUCTURA(25)* d100 ×4 (nomenclator cod_oblig↔bugetar, cotă micro 121, checksum R11b, scadențe/nr_evidența) ·
d101 ×2 (structură P1-P53, R17 Data_S) · d112 ×2 (limită text 75, nomenclator cod_oblig) · d205 ×2 (checksum
totalPlata_A, trunchiere den/adresă) · d300 (rânduri/checksum) · d301 (checksum R28) · d390 (nomenclator țări
HR→CR) · d394 ×3 (tip_partener, nomenclator codPR art.331, totalPlata_A R17) · d406 ×4 (UoM UN/ECE,
MovementType, BaseRate, registration_number) · d710 ×5 (structură decl710, nomenclator COD_BUGETAR, checksum
R11b, R15 termen, scadențe).

**Caveat — reduce totalul (nu reflectat în cifra brută):**
- **structura P1-P53 (d101) + R17 Data_S** sunt de facto ACOPERITE de reconstrucția d101 din 01.08 (golden
  lanț formule + DUK valid, DECIZII 01.08); rămâne doar bump de inventar, nu muncă. −2 MIC efectiv.
- Clusterele de **cotă TVA** (d300 cote→rânduri, d301 cotă TVA, d394 cote acceptate) se sprijină pe clusterul
  TVA DEJA verificat (Legea 141/2025 în common.COTE, period-aware, golden test_d394) — efort real spre capătul
  de jos al intervalului.
- **d112 baze/concedii** se sprijină pe salarizare deja verificată (taxe_cm canonic, apelat și de d112).
Cu discount-urile, banda efectivă coboară spre **~10–16 zile**.



---

# SESIUNEA B — testarea pe flux

## Starea sesiunii B

| Fază | Stare | Când |
|---|---|---|
| Faza 0 — decuplarea suitei de firmele persistente | închisă | 29.07 |
| Faza 1 — cele 7 firme (F1–F7) pe flux | neîncepută | |

Etapele fluxului (Faza 1), `√ DD.MM` = etapa are teste cap-coadă pe o firmă:
| Etapă | Stare |
|---|---|
| 1. Migrare / preluare | |
| 2. Configurare firmă | |
| 3. Intrare documente primare | |
| 4. Salarizare | |
| 5. Contabilizare | |
| 6. Sfârșit de lună | |
| 7. Verificări interne | |
| 8. Declarații — generare | |
| 9. Declarații — depunere | |
| 10. Ieșiri externe | |
| 11. Transversal | |


## De ce pe flux, nu pe zone

Campania din iunie a testat pe **zone** (ecrane, module): 17 zone, ~190 de teste, verde.
N-a fost destul — D101 a trecut testele de zonă pentru că nimeni n-a verificat că registrul
*de sub el* avea rânduri. Zonele ascund **propagarea**; un test pe flux o urmărește.

## Regula cascadei

**Un eșec la etapa N invalidează toate rezultatele de la N+1 în jos.** Nu ai voie să declari
„D300 verde" dacă etapa 5 (contabilizare) n-a fost dovedită pe aceleași date.

## Regula bazei nule

**Orice declarație cu bază 0, zero linii sau total 0 e EROARE până la proba contrară.**
„Fără activitate" se declară EXPLICIT (firma F7), nu se deduce din tăcere.

DUKIntegrator validează STRUCTURA, nu conținutul. Dovedit de trei ori: D101 (bază zero din
query rupt), D406 (registru gol sub mască), D112 (salarii zero din coloană dispărută) —
toate treceau validatorul.

## Firmele de test

Setul e derivat din **legislație**, nu din ce s-a construit. Dimensiunile care produc
comportament diferit:

| Dimensiune | Valori | Temei |
|---|---|---|
| Sistem contabil | partidă dublă / simplă | L 82/1991; OMFP 1802/2014; OMFP 170/2015 |
| Regim TVA | neplătitor · lunar · trimestrial · la încasare · art. 317 | CF art. 310, 316, 317, 322, 282(5) |
| Impozit | micro 1%/3% · profit 16% · PFA real · PFA normă | CF Titlul II, III, IV |
| Operațiuni | achiziții IC · servicii UE · taxare inversă · salariați · fără activitate | CF art. 307, 331; OUG 158/2005 |

| ID | Formă | TVA | Impozit | Ce testează UNIC |
|---|---|---|---|---|
| **F1** | SRL | lunar | micro 1% | comerț cu stoc, 3 salariați, descărcare de gestiune, D300 lunar, D394, D112, D101, D406 |
| **F2** | SRL | trimestrial | profit 16% | D300 **trimestrial**, D100, amortizare, mijloace fixe, registru de casă |
| **F3** | SRL | neplătitor + **art. 317** | micro 3% | **D301** (achiziții IC + servicii UE tip 5), **D390**, taxare inversă |
| **F4** | SRL | **TVA la încasare** | micro | exigibilitate la încasare — logică complet separată |
| **F5** | PFA | plătitor | **sistem real** | partidă simplă, RIP, **D212**, D710, contribuții PFA |
| **F6** | PFA | neplătitor | **normă de venit** | fără evidență de venituri, doar D212 pe normă |
| **F7** | SRL | plătitor | micro | **fără nicio operațiune** — singura care are voie să dea bază 0 |

**Două cabinete**, ca să se testeze și izolarea între cabinete:
Cabinetul A — F1, F2, F3, F7 · Cabinetul B — F4, F5, F6

**Fiecare firmă are un an fiscal complet (2026)**, cu cifrele așteptate calculate din
temeiurile verificate în sesiunea A, înghețate într-un fișier de așteptări **scris înainte
de a rula aplicația pe date**. Altfel copiezi output-ul și testezi că 1 = 1.

## Cele 11 etape

Pentru fiecare: **invariantul** și **capcana** (modul cunoscut de eșec, din cele întâlnite).

### 1. Migrare / preluare firmă
Sold inițial, plan de conturi, parteneri, stocuri, mijloace fixe, RIP (PFA), pre-fill ANAF v9.
**Invariant:** Σdebit = Σcredit pe soldul preluat; nr. rânduri importate = nr. din fișier −
duplicate raportate explicit.
**Capcană:** import „reușit" cu 0 rânduri; dedup care înghite tot; schema tenantului ≠ template.

### 2. Configurare firmă
`tip_firma`, regim TVA și perioadă fiscală, vector fiscal, an fiscal, utilizatori, roluri.
**Invariant:** fiecare regim produce exact setul de straturi și declarații așteptat.
**Capcană:** regim schimbat retroactiv care rescrie tăcut trecutul.
**Firme:** toate șapte produc vectori fiscali diferiți — etapa care le distinge.

### 3. Intrare documente primare
Facturi emise/primite, e-Factura, extras bancar, casă, Raport Z, NIR, documente fotografiate.
**Invariant:** fiecare document → exact o intrare în registru; total documente = total listă
= total raport.
**Capcană:** parser care întoarce 0 linii tratat ca „lună fără documente"; semn inversat;
document dublat la reimport.

### 4. Salarizare
Contracte, stat de plată, concedii medicale, part-time, fluturași, tichete.
**Invariant:** brut − reținute = net pe fiecare salariat; Σ stat = Σ rulaj 421/4315/4316/444/436.
**Capcană:** salariat exclus tăcut din stat; **sau coloană dispărută din schemă → salarii
ZERO** (dovedit 27.07; acoperit acum de `common.cere_coloane_cursor`).

### 5. Contabilizare
Motor, note automate, note manuale, patru-ochi, stornare.
**Invariant:** Σdebit = Σcredit per notă și per perioadă; nicio notă validată fără
document-sursă; storno = oglinda exactă.
**Capcană:** notă rămasă ciornă → nu intră în rulaj → **exact mecanismul bazei zero**.

### 6. Operațiuni de sfârșit de lună
Închidere TVA, amortizare, descărcare de gestiune, diferențe de curs, închidere de an.
**Invariant:** după închidere, 4426/4427 sold 0; stoc cantitativ ↔ valoric coerent.
**Capcană:** operațiune rulată de două ori; rulată pe lună închisă.

### 7. Verificări interne
Semafor, control încrucișat, alerte, monitor fiscal.
**Invariant:** pe firmă cu eroare **injectată deliberat**, verificatorul o GĂSEȘTE; pe firmă
curată, verde cu motiv explicit.
**Capcană:** gri raportat ca verde; verificator care compară o funcție cu ea însăși.

### 8. Declarații — generare
Toate declarațiile datorate, pe toate cele 7 firme, toate lunile.
**Invariant:** fiecare cifră din XML = cifra din fișierul de așteptări. **Bază 0 doar la F7.**
**Capcană:** query rupt → generator gol → XML valid. Ramură scrisă și niciodată executată
(D301 tip 5).

### 9. Declarații — depunere
DUKIntegrator, SPV, D710 rectificativă.
**Invariant:** declarația depusă se stochează cu hash; regenerarea produce același hash sau
se raportează diferența.
**Capcană:** DUK tratat ca dovadă de conținut. **Nu e.** Plus validare care nu rulează deloc
și raportează gri permanent (D406, 27.07 — `an`/`luna` nepasate).

### 10. Ieșiri externe
SAGA, WinMentor, D406, rapoarte, portal client, export GDPR.
**Invariant:** totalurile din export = totalurile din aplicație, calculate pe **a doua cale**.
**Capcană:** rută inaccesibilă (a mușcat la SAGA); encoding; denumire de fișier.

### 11. Transversal (la FIECARE etapă, nu la sfârșit)
Izolare tenanți, acces/roluri, integritate în timp, backup + **restaurare**.
**Invariant:** două firme cu date identice, citire încrucișată → 0 rânduri; apel
neautentificat → 401; obiect din alt tenant → 404.
**Capcană:** `search_path` nesetat; constrângere nescopată la `current_schema()`; job de
fundal pe tenantul greșit.

## Cele trei niveluri de test

| Nivel | Ce dovedește | Regula |
|---|---|---|
| **N1 — calcul pur** | formula fiscală | fără DB, fără fake; cifre din exemplul oficial |
| **N2 — integrare pe DB reală** | granița cod ↔ bază | Postgres real; **fake interzis pe `core.d*`** |
| **N3 — cap-coadă pe firmă de test** | că fluxul întreg produce adevărul | de la import până la XML validat |

Cele ~1049 de teste actuale sunt aproape toate N1. N2 a apărut pe 27.07
(`test_pull_declaratii.py`). **N3 nu există** — e ce construiește sesiunea B.

### Izolarea unui test de integrare

Depinde de **cine deține conexiunea** (stabilit 29.07):

- funcție **cititoare** care primește `conn` → trăiește în tranzacția fixturii → **ROLLBACK**
  curăță (tiparul din `test_pull_declaratii`);
- funcție **scriitoare** care își deschide propria conexiune și comite → ROLLBACK-ul
  fixturii n-are ce anula → **schemă efemeră comisă + DROP la teardown**, cu `DROP IF EXISTS`
  la setup pentru siguranță la crash.

**Nu se refactorizează cod de producție ca să servească un test.**

Și: **niciun test de integrare nu depinde de o firmă persistentă din bază.** Un test legat
de o firmă anume trece pentru că firma există, nu pentru că logica e corectă — și devine
roșu când cineva îi schimbă datele, fără să se fi modificat cod.

---

# Ordinea de execuție

## Sesiunea A
Testele fiscale, unul câte unul, până la epuizarea inventarului. Nu are nevoie de date.

## Sesiunea B

**Faza 0 — curățenie (blocantă).** Ștergerea completă a datelor actuale: firme, cabinete,
utilizatori. Tot ce e acum e de test, nimic real.

**Faza 1 — cele 7 firme.** Creare prin **interfață**, ca un contabil care intră prima dată,
nu prin script. Așa se testează etapele 1–2 și se prind problemele pe care le vede omul.
Fișierul de așteptări se scrie **înainte**, din temeiurile verificate în sesiunea A.

**Faza 2 — etapele 3→11**, în ordine, cu regula cascadei.

**Faza 3 — gardurile** care împiedică regresia. Vezi `GARZI.md`.

---

# Cum se consemnează

- **Rezultatul fiecărei etape** — în „Starea sesiunii B" (Faza 1) și „Inventarul de acoperit în A" de mai sus, cu data.
- **Defectele găsite** — în `DECIZII.md`, cu **cauza**, nu doar cu simptomul.
- **Ce nu se repară imediat** — `xfail(strict=True)` în `core/test_datorie.py`, NU notă
  într-un fișier. Un registru pe care trebuie să ți-l amintești nu funcționează.
- **Gardurile noi** — în `GARZI.md`, în aceeași zi.

---

# Reguli de lucru

1. **Verificare la sursă înainte de orice afirmație.** Valorile fiscale se verifică la
   ANAF/lege, nu din memorie. Trigger: „lipsește", „nu există", „e greșit".
2. **Proba pe date reale.** Nicio etapă nu e „gata" pentru că trece validatorul sau pentru
   că testele sunt verzi. Un test care rămâne verde când generatorul întoarce `[]` nu
   testează nimic.
3. **Ancorele se citesc din fișier, nu se scriu din memorie.**
4. **Nicio comandă de commit fără poartă** — pe suită ȘI pe proba funcțională.
5. **Nu se repară pe suspiciune.** Se măsoară întâi. Pe 27.07, „float pe bani e greșit" era
   adevărat ca principiu și fals ca diagnostic: 0 din 5000 de valori pierdeau precizie.
6. **Un test nu se scrie fără temei verificat.** Vezi sesiunea A.

## PREDARE §6 (01.08.2026) — Campania versionare formule pe la_data: CAMPANIE COMPLETA (pas 0-5)

OPRIRE §6 (limita de context, NU fragmentare-pentru-confirmare): pas 3-5 sunt DECISE in comanda aprobata,
nu se re-decid. Se continua fara sa se intrebe nimic. Predare la granita de commit (26fe9ca), tot ce e
comis e functional (suita 1195 verde, verificator 0).

GATA (5 commit-uri):
- PAS 0 (19faad6): cota_dividend + lichidare -> COTE["impozit_dividend"]. FLAG: 10% pre-2026 neverificat la
  sursa (posibil 8% 2023-2025), REDARE, de reconfirmat la MO.
- PAS 1 (3ee3ad7): TIPARUL. common.alege_varianta(variante, la_data) = cota() pe COD. deducere_personala ->
  _deducere_personala_2018 (varianta) + _VARIANTE_DEDUCERE (registru cu temei) + dispecer public.
  graf_temei EXTINS sa lege dispecerul de variantele din _VARIANTE_* (module-var -> functii).
- PAS 2a (ff8fd84): plafon_la (valoare) -> COTE["plafon_tva_incasare"].
- PAS 2b (35b4732): d101._scadenta + d710 d_recN (structura) -> variante datate.
- PAS 2c (26fe9ca): calcul_cm (fereastra diminuare) -> _calcul_cm_core(diminuare_activa) + 3 variante.

TIPARUL de aplicat (mecanic) la PAS 3 - functii STABILE (o singura versiune azi):
  Pentru fiecare functie F(args, la_data):
    1. redenumeste corpul: def F -> def _F_2018 (sau anul in vigoare al regulii).
    2. registru: _VARIANTE_F = [("<data_in>", _F_2018, c.Temei(<act>, ..., nivel_sursa="REDARE",
       de_cine="Code/Costin", verificat_la="2026-07-31"))].
    3. dispecer public F: docstring cu markerul TEMEI (daca F e in _TEMEI_FUNCTII), apoi
       fn,_ = c.alege_varianta(_VARIANTE_F, la_data or date.today()); return fn(args...).
    Import in modul daca lipseste: from core.common import alege_varianta as _av, Temei as _Tm (sau c.*);
    from datetime import date. Foloseste STRING pt data_in ("2018-01-01") - _ca_data o converteste.
  Roșu->verde->mutatie->commit, un MODUL per commit.

PAS 3 - lista (11 functii, cu modul; toate SINGLE BODY azi):
  salarizare.py: procent_cm, taxe_cm, calcul_cm_cod10, calcul_salariu  (calcul_salariu e mare: dispecer
     subtire care forwardeaza; NU duplica corpul - redenumeste in _calcul_salariu_2018).
  deconturi.py: plafon_diurna
  sponsorizari.py: plafon_credit, credit_sponsorizare
  motor.py: rezerva_legala
  contracte_speciale.py: calcul_zilier
  tva_marja.py: vanzare_marja  -> RAMIFICATIE: verifica intai daca doar CITESTE cota (base x cota) fara
     regula proprie; daca da, RECLASIFICA (nu e functie de regula), scoate-o din lista, spune, lista scade la 10.
  tva_marja_turism.py: marja_turism_special (prorata scutire non-UE = regula, ramane)
  ATENTIE (ramificatie Costin): daca vreo functie se dovedeste ca ARE puncte de schimbare (nu stabila),
  trateaz-o ca la pas 2 (variante datate reale, nu 1 versiune).

PAS 4 - GARD (ratchet -> PRAG 0 in aceeasi campanie): in verificator, pt fiecare functie din _TEMEI_FUNCTII
  (+ eventual lista extinsa a celor 11+), verifica AST ca are un dispecer pe la_data (corpul cheama
  alege_varianta pe un registru _VARIANTE_*). Baseline = cate NU au inca; coboara la 0 cand toate convertite;
  la 0, PRAG (orice regula fiscala noua fara dispecer BLOCHEAZA). Nota: procent_cm nu ia la_data direct (ia
  cod/zile) - decide daca intra in gard sau are exceptie declarata (apelat de calcul_cm care e versionat).

PAS 5 - CONSUMATORI (proba pe cifra, cerinta finala): verifica adeverinta:50, d112.py:443 (rectificativa),
  stat_plata_api.py:60/145, salarii_contare.py:55 - toate paseaza la_data pana la capat.
  PROBA CERUTA: genereaza o adeverinta pentru o luna din 2025 si arata ca foloseste regulile 2025 (nu 2026).
  Ramificatie Costin: daca vreun consumator NU paseaza la_data -> repara-l (e chiar bugul campaniei).

La final: Raport §2 etapa 5 pentru TOATA campania (pas 0-5).

---
CAMPANIE COMPLETA (01.08.2026) — pas 3-5 livrate:
- PAS 3 (7 commit-uri, un modul fiecare): cele 11 functii de regula ramase -> dispecer pe la_data.
  salarizare 783cca4 (procent_cm/taxe_cm/calcul_cm_cod10/calcul_salariu; procent_cm primeste la_data din
  _calcul_cm_core; calcul_salariu = dispecer subtire; graf_temei test actualizat variant-aware). deconturi
  4fa6ffd (plafon_diurna). sponsorizari 0f423e5 (plafon_credit + credit_sponsorizare, paseaza la_data intern).
  motor 3822edd (rezerva_legala). contracte_speciale 3c3611c (calcul_zilier). tva_marja 126e9b9 (vanzare_marja).
  tva_marja_turism 1606d61 (marja_turism_special). RAMIFICATIE rezolvata: vanzare_marja NU e simplu cititor de
  cota (aplica regula regimului marjei) -> RAMANE in lista (11, nu 10). Fiecare: rosu->verde->mutatie.
- PAS 4 (8c0ea86): GARD verificator - fiecare din cele 13 functii de regula (_VERSIONARE_FUNCTII) trebuie sa
  fie dispecer pe la_data (AST: corpul cheama alege_varianta(_VARIANTE_*, ...)). Ratchet la PRAG 0 in aceeasi
  campanie (toate 13 convertite). Mutatie: rezerva_legala single-body -> TOTAL 1 BLOCHEAZA.
- PAS 5 (ee8a717): consumatorii. adeverinta:50, d112:443, stat_plata_api:60/145, salarii_contare:55 paseaza
  DEJA la_data. Reparat salariati_api:334 (calcul_cm_cod10 nu pasa la_data). Proba schema efemera: adeverinta
  2026-06 (era 2025: sm 4050+facilitate 300) net 2574.75 vs 2026-08 (sm 4325+facilitate 0) net 2455.75.
- GOL PRE-EXISTENT descoperit (NU al campaniei; cota, nu formula): calcul_salariu pre-2026 RIDICA fiindca
  plafon_facilitate_salariu_minim (COTE) incepe 2026-01-01 - nicio valoare 2025. Adeverinta pentru o luna
  2025 crapa. DE DECIS (Costin): backfill plafon 2025 la sursa SAU ramane limita declarata (app n-are date
  reale pre-2026). NU s-a inventat o valoare.
  REZOLVAT (01.08.2026, blocaj motivat): NU backfill - LIMITA DECLARATA. cota() ridica PerioadaIndisponibila
  (tag PERIOADA_BLOCATA -> UI 423, nu 500) cu cele 4 elemente. Gard verificator GARD BLOCAJ MOTIVAT PRAG 0.
  Cote late-start care rup un calcul: plafon_facilitate_salariu_minim + tichet_masa_plafon (ambele 2026-01-01,
  calcul_salariu). Restul cotelor de regula: cas/cass/impozit/cam (2018), salariu_minim/facilitate (2025-01-01
  =podea) - nu rup in [2025, azi]. Nota (nu regula): tva_redusa (2025-08-01) rupe calcul_tva pt facturi
  pre-08.2025 (cititor subtire, acelasi mecanism central). Commit-uri 1d37d3a + 1de6ac9. Backfill 2025 = de decis Costin.
