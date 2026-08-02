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

- fir: d101 reconstructie + Conditia 2 audit semantic + ciclul clasa cale-fisier (GREENLIGHT Costin 01.08, ordine impusa: audit INAINTE de reconstructie)
- ultim: d406 reparat (cale plan_oficial -> anaf_surse), b845763.
- urmator: T1 ciclul clasa cale-fisier -> T2 audit semantic 8 valide -> T3 reconstructie d101. IN LUCRU (T1).
- pasi:
  T1. [ciclul neconformitate pe bug d406 cale] grep clasa "cale relativa la radacina": 2 instante (d406 reparat, plata_salarii CORECT - sepa_surse/ exista). Gard: test care asorteaza ca fisierele de date deschise prin cale construita EXISTA (nu set gol tacut). Commit.
  T2. [GATA 01.08] Audit semantic: toate 8 emit doar campuri OFICIALE (struct.txt + 3 confirmate in validator: d301 temei, d394 tvaDedAI11/21). d101 = SINGURA cu numerotare proprie -> ordine = doar d101. Gard core/test_audit_campuri_oficiale.py + DECIZII 01.08.
  T3. [reconstructie d101] rescrie calcul_d101 pe P oficiale (P7=P3+P6, P10=P7+P8-P9, P41=P411+P412, totalPlata_A=S(P1..P53)) + build_xml P ca ATRIBUTE + scadenta LL+3 (an>2025) + R17/R38/R41/R42/R48 + grup. Numerotarea inventata DISPARE (fara adaptor). Proba Conditia 1: tabel P-emis/P-oficial/formula/sursa + golden calculat de mana din exemplul OPANAF. Commit.
  T3. [GATA 01.08] d101 RECONSTRUIT pe OPANAF 206/2025 - calcul_d101 pe P oficiale (P41=impozit) + build_xml P ca ATRIBUTE + scadenta LL+3 + numerotarea inventata DISPARUTA. Golden calculat de mana + DUK valid. Datoria d101 inchisa, smoke d101 -> asertiune, d101 in gardul audit. Sweep DUK acum 9/9 valide.
  STARE = GATA (T1+T2+T3 comise)

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
| tichete masa/vacanta | salarizare | test_salarizare.py | PARTIAL 31.07 — fond fiscal verificat la sursa: valoare (45), cote (imp/CAS/CASS), plafon vacanta, cadou, baza impozit (#3); deschis: D2 nr tichete, D3 exces vacanta, citate portal | FISCAL | Legea 201/2025; HG 1045/2018 art.10(3); CF art.76(3)h/78/142(r)/157(2); OUG 8/2009 art.1; L296/2023 |  |
| concedii medicale | salarizare | test_salarizare.py | PARTIAL 31.07 — verificat+aplicat: procente pe cod (carantina 07=100%), split 1-5, plafon 12 sm, CAS 25% uniform + CASS 01/07/10 UNIFICATE intr-o functie canonica (taxe_cm, apelata si de d112; arbori-paraleli verde+mutatie; DUK cod01 valid); deschis: CM4 plafon in calcul_cm, D-field coduri speciale (08/06 gap DUK pre-existent); gri: deducere, tier-1 just.ro art.139(1)o | FISCAL | OUG 158/2005 art.10/12/17/20; Legea 141/2025 si 136/2020; CF art.139(1)o+140 (CAS salariat activ; art.144=alte categorii)/142/155(1)i; OUG 34/2024 |  |
| tichete culturale | salarizare | test_salarizare.py |  | FISCAL |  |  |
| tichete cresa | salarizare | test_salarizare.py |  | FISCAL |  |  |
| nomenclator cod_oblig<->cod_bugetar | d100 | test_d100.py |  | STRUCTURA |  |  |
| cota micro 121 (flag) | d100 | test_d100.py |  | STRUCTURA |  |  |
| checksum totalPlata_A (R11b) | d100 | test_d100.py |  | STRUCTURA |  |  |
| scadente/nr_evidenta | d100 | test_d100.py |  | STRUCTURA |  |  |
| structura P1-P53 | d101 | test_d101.py |  | STRUCTURA |  |  |
| cota profit 16% + IMCA | d101 | test_d101.py |  | FISCAL |  |  |
| R17 Data_S / termen | d101 | test_d101.py |  | STRUCTURA |  |  |
| amortizare | d101 | test_d101.py |  | FISCAL |  |  |
| baze contributii (CAS/CASS/imp/CAM) | d112 | test_d112.py |  | FISCAL |  |  |
| concedii medicale (asiguratB3/D) | d112 | test_d112.py |  | FISCAL |  |  |
| suprataxare prag | d112 | test_d112.py | √ 02.08 (bump: V3 salariu_minim 2025 corectat 3700->4050 HG 1506/2024 FIX5 dupa √ 29.07; praguri COTA-DERIVATE nu literal - salarizare.py:129 sm=cota, d112 _sal_minim=cota; recalculat sm 2025/2026H1=4050 2026H2=4325 identic cu codul: (4050-300-2000)*25%=437.50, (4325-200-2000)*25%=531.25) | FISCAL | CF art.146 alin.(5^6) | test_sub_minim_nescutit_emite_asigexc2_fara_motivexc test_peste_minim_asigexc_zero |
| rotunjire aritmetica (A91b) | d112 | test_d112.py |  | FISCAL |  |  |
| limita text 75 | d112 | test_d112.py |  | STRUCTURA |  |  |
| nomenclator cod_oblig | d112 | test_d112.py |  | STRUCTURA |  |  |
| sect_II tip_venit (impozit retinut) | d205 | test_d205.py |  | FISCAL |  |  |
| checksum totalPlata_A | d205 | test_d205.py |  | STRUCTURA |  |  |
| trunchiere den/adresa | d205 | test_d205.py |  | STRUCTURA |  |  |
| rotunjire | d205 | test_d205.py |  | FISCAL |  |  |
| cote TVA -> randuri | d300 | test_d300.py |  | FISCAL |  |  |
| exigibilitate / TVA la incasare | d300 | test_tva_incasare.py |  | FISCAL |  |  |
| taxare inversa | d300 | test_d300.py |  | FISCAL |  |  |
| pro-rata deducere | d300 | test_d300.py |  | FISCAL |  |  |
| randuri / checksum | d300 | test_d300.py |  | STRUCTURA |  |  |
| rotunjire aritmetica | d300 | test_d300.py |  | FISCAL |  |  |
| ajustari | d300 | test_d300.py |  | FISCAL |  |  |
| tipuri operatiune 1-5 | d301 | test_d301_rollup.py |  | FISCAL |  |  |
| rollup S4.1->S4 | d301 | test_d301_rollup.py |  | FISCAL |  |  |
| checksum totalPlata_A (R28) | d301 | test_d301_rollup.py |  | STRUCTURA |  |  |
| baza = val x curs | d301 | test_d301_rollup.py |  | FISCAL |  |  |
| cota TVA | d301 | test_d301_rollup.py |  | FISCAL |  |  |
| tipuri operatiune IC (L/A/P/S) | d390 | test_d390.py |  | FISCAL |  |  |
| nomenclator tari (HR->CR) | d390 | test_d390.py |  | STRUCTURA |  |  |
| rotunjire aritmetica (A91b) | d390 | test_d390.py |  | FISCAL |  |  |
| reclasificari manuale | d390 | test_d390.py |  | FISCAL |  |  |
| exigibilitate / prag | d390 | test_d390.py |  | FISCAL |  |  |
| tipuri operatiune (pct.215) | d394 | test_d394.py |  | STRUCTURA |  |  |
| tip_partener | d394 | test_d394.py |  | STRUCTURA |  |  |
| cote acceptate | d394 | test_d394.py |  | FISCAL |  |  |
| rezumat1 campuri complete | d394 | test_d394.py |  | STRUCTURA |  |  |
| nomenclator codPR (art.331) | d394 | test_d394.py |  | STRUCTURA |  |  |
| taxare inversa | d394 | test_d394.py |  | FISCAL |  |  |
| totalPlata_A (R17) | d394 | test_d394.py |  | STRUCTURA |  |  |
| plan conturi pe norma | d406 | test_limita_text_anaf.py |  | STRUCTURA |  |  |
| UoM UN/ECE | d406 | test_limita_text_anaf.py |  | STRUCTURA |  |  |
| MovementType nomenclator | d406 | test_limita_text_anaf.py |  | STRUCTURA |  |  |
| BaseRate (encoding pro-rata) | d406 | test_limita_text_anaf.py |  | STRUCTURA |  |  |
| registration_number (00+CUI) | d406 | test_limita_text_anaf.py |  | STRUCTURA |  |  |
| SourceDocuments (facturi reale, PARTIAL) | d406 | test_limita_text_anaf.py |  | FISCAL |  |  |
| structura XSD (Header/MasterFiles/GLE) | d406 | test_limita_text_anaf.py |  | STRUCTURA |  |  |
| structura declaratie710 | d710 | test_d710.py |  | STRUCTURA |  |  |
| nomenclator COD_BUGETAR | d710 | test_d710.py |  | STRUCTURA |  |  |
| checksum R11b | d710 | test_d710.py |  | STRUCTURA |  |  |
| R15 termen definitivare | d710 | test_d710.py |  | STRUCTURA |  |  |
| scadente | d710 | test_d710.py |  | STRUCTURA |  |  |
| plafon diurna neimpozabila | deconturi | test_versionare_formule.py |  | FISCAL | CF art.76(2) lit.k + alin.(4^1); HG 714/2018; HG 518/1995 | (fara test de VALOARE - doar dispecer versionare; golden de scris) |
| credit sponsorizare / D177 | sponsorizari | test_operatiuni_speciale.py |  | FISCAL | CF art.25(4) lit.i; OUG 115/2023; Ordin ANAF 3562/2024 | test_plafon_dublu_min_ca_impozit test_credit_sub_plafon_lasa_redirectionabil test_micro_fara_credit test_beneficiar_neinscris_fara_credit |
| rezerva legala | motor | test_versionare_formule.py |  | FISCAL | Legea 31/1990 art.183; OMFP 1802/2014 pct.421 | (fara test de VALOARE - doar dispecer versionare; golden de scris) |
| zilieri (impozit+CAS) | contracte_speciale | test_versionare_formule.py |  | FISCAL | Legea 52/2011 art.9^1; CF art.76(2) lit.g/i | (fara test de VALOARE - doar dispecer versionare; golden de scris) |
| regim marja second-hand | tva_marja | test_versionare_formule.py |  | FISCAL | CF art.312 (norme pct.86) | (fara test de VALOARE - doar dispecer versionare; golden de scris) |
| regim marja turism | tva_marja_turism | test_versionare_formule.py |  | FISCAL | CF art.311 | (fara test de VALOARE - doar dispecer versionare; golden de scris) |
| impozit dividend | decontari_asociati | test_impozit_dividend.py |  | FISCAL | CF art.97; Legea 141/2025 | test_cota_dividend_si_lichidare_sursa_din_cote |
| contributii PFA (praguri CAS/CASS pe sm) | d212 | test_d212_reper.py |  | FISCAL | CF art.148-149 (CAS), art.154/170 (CASS), art.68-69 (venit net); Legea 141/2025 (plafon CASS 72 sm) | test_d212_reper_din_cota_nu_literal test_d212_apare_in_graful_salariu_minim (reper vizibil; golden VALORI CAS/CASS de scris) |

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
