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

- fir: SWEEP DUK toate declaratiile (redirectionare Costin 31.07: inainte de reconstructii, mapez cate sunt sparte pe validatorul CURENT)
- ultim: sweep rulat pe schema efemera + profil complet + date minime adecvate (salariat/factura UE/dividende). Rezultat: 7 VALID (d100,d112,d205,d300,d301,d390,d394), 2 SPARTE: d101 (model P inventat, reconstructie) + d406 (DUK: AccountID cont [731] nu e in planul de conturi din chart - o inregistrare refera un cont absent din cei 169 generati; de investigat: chart incomplet vs booking gresit). Claim 16.07 "toate 9 valide" INFIRMAT: 2/9 sparte azi.
- urmator: gard smoke-sweep DUK LIVRAT (core/test_smoke_duk.py: 7 valide asertate + d101/d406 xfail strict). RAMANE DECIZIE COSTIN: ordinea reconstructiilor (d101 intai? d406? ambele?). Posibil edge d394: luna doar cu operatiuni UE -> R112.3 serieFacturi la op_efectuate=0 (de confirmat). BLOCAT: cere decizie ordine.
- pasi:
  1. [GATA] sweep no-data + sweep cu date (salariat/factura UE) -> 7 valid / 2 sparte.
  2. reconstructie d101 (temei OPANAF 206/2025 validat) - cand Costin da drumul.
  3. investigare d406 cont 731 (SAF-T) - separat.
  4. [GATA 01.08] gard smoke-sweep DUK permanent: core/test_smoke_duk.py.
  STARE = BLOCAT: sweep + gard gata, cere decizie ordine reconstructii (d101/d406)


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
- urmator: următorul cluster FISCAL fără temei din Inventar A: tichete masă/vacanță (salarizare) — Legea 201/2025 dă plafonul tichetului de masă (deja în common.py=45), de verificat la sursă tratamentul fiscal complet (CASS+impozit, fără CAS/CAM) și tichetele de vacanță. NEÎNCEPUT.
- pasi:
  · [GATA] §3.1 format · inventar (60 clustere, 4 √) · core/temeiuri.py (CLI) · gard validator-regulă · garda anti-stale per funcție.
  · [ÎN CURS] 2b — locuri fără temei, pe CLUSTER, cu validarea ta: deducere personală [√ 31.07] → tichete → concedii medicale → apoi celelalte 10 module.
  · [GATA 31.07] Temei STRUCTURAT (etapele 1-4): common.Temei(act/.../data_out) pe toate cotele COTE; cota() ridica la expirare (data_out = mecanism principal de deriva, nu proxy); gard ratchet in verificator; Inventar A generat partial + overlay persistent; GARZI cat.3 = limita reala (schimbare de lege intre data_in si data_out nu e detectabila). Commit-uri 3c37bfa..9ed8899.
  · [RĂMAS] cele 113 citări normative (decizia #1) · datoriile xfail deschise.

- fir (în așteptare): Modelarea contractului în timp (Sesiunea A · salarizare)
- ultim: 2b-scrieri comis — creare/editare/import scriu pe salariu_istoric, citiri pe salariu_curent (reparat si bug-ul activ din import, PASUL 1)
- urmator: 2b-coloană — DROP salariati.salariu_brut din tabel + migrare, UI schimbare salariu (valabil_din), scoaterea bridge-ului salariu_la. NEÎNCEPUT.

---

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

## Inventarul de acoperit în A

Per CLUSTER de reguli, nu per fișier (30.07.2026) — un √ pe fișier ascundea că doar o parte din
reguli era verificată (vezi salarizare 29.07). `Verificat la sursă`: `√ DD.MM` = testele afirmă
LEGEA la data aceea (garda anti-stale pică `√`-ul dacă codul se schimbă substanțial după). `Risc`:
**FISCAL** = produce o cifră într-o declarație, greșeala e INVIZIBILĂ (validatorul acceptă) și ajunge
la ANAF; **STRUCTURA** = mapare/nomenclator/checksum/XML, greșeala e VIZIBILĂ (validatorul respinge).
Estimare de structură — se rafinează la citirea fiecărui modul.

| Cluster | Modul | Teste | Verificat la sursă | Risc | Temeiuri | Funcție(test) |
|---|---|---|---|---|---|---|
| facilitate salariu minim | salarizare | test_salarizare.py | √ 31.07 (bump: FIX3 a mutat net-ul asertat in test_minim_4325_are_facilitate_sem2; facilitatea reconfirmata la sursa OUG 89/2025 art.III + HG 146/2026, neschimbata) | FISCAL | OUG 156/2024 art.LXVI; OUG 89/2025 art.III; HG 146/2026 | test_minim_4325_are_facilitate_sem2 test_facilitatea_ramane_conditionata_de_norma_intreaga test_facilitate_pe_minim_cu_cm_ramane_intreaga test_facilitate_prorata_luna_angajare |
| suprataxare part-time | salarizare | test_salarizare.py | √ 29.07 | FISCAL | CF art.146 alin.(5^6)-(5^7); art.168 alin.(6^1) | test_part_time_2000_suprataxa_pe_angajator test_part_time_exceptat_fara_suprataxa test_norma_intreaga_sub_minim_este_suprataxata test_part_time_sub_minim_ramane_suprataxat test_exceptatul_nu_e_suprataxat_indiferent_de_norma test_peste_minim_nu_se_suprataxeaza test_suprataxa_baza_pe_minimul_diminuat_ambele_semestre |
| proratare angajare/incetare | salarizare | test_salarizare.py | √ 29.07 | FISCAL | OUG 156/2024 art.LXVI alin.(4); OMF 1855/2022 pct.2 | test_suprataxa_prag_prorata_luna_angajare test_facilitate_prorata_luna_angajare test_suprataxa_si_facilitate_prorata_la_incetare |
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
| suprataxare prag | d112 | test_d112.py | √ 29.07 | FISCAL | CF art.146 alin.(5^6) | test_sub_minim_nescutit_emite_asigexc2_fara_motivexc test_peste_minim_asigexc_zero |
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

Numărul nu e ținta. Ținta: fiecare cluster FISCAL să aibă cifra afirmată cu temei citat la sursă.

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
