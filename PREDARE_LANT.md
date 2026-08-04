Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba) inainte de a incepe.

# PREDARE LANT — 04.08.2026 (rularea 11)

Sesiune noua, context gol. Comanda de pornire: "Citeste PREDARE_LANT.md si continua lantul."
Raspunde in ROMANA. Server: `ssh iconta`, `~/iconta_nou` (branch main). Rulezi pytest/DUK/verificator/commit PE SERVER.
NOTA quoting: pentru editari de fisiere pe server foloseste `cat fisier_local | ssh iconta "python3 -"` (pipe),
NU heredoc inline in `ssh "... <<'EOF' ..."` cu ghilimele Python `"` inauntru - se ciocnesc cu ghilimelele ssh.
Pentru commit cu ghilimele simple in mesaj, foloseste `git commit -F fisier_mesaj`.

## Ritual de pornire (§5)
1. `git log --oneline -1` -> HEAD asteptat: **234460b** (sau mai nou). `git status --porcelain` -> TREE_CURAT.
2. `venv/bin/python -m pytest -q` -> asteptat ~1350 passed, 2 skipped, 21 xfailed. Verificator: `venv/bin/python3
   verificator_conformitate.py` -> TOTAL 0 candidate.
3. `venv/bin/python3 -c "from core import agenda; print(agenda.urmator_cluster())"`
   -> **(('MovementType nomenclator', 'd406'), 9, 1)** = urmatorul cluster, 9 ramase, 1 blocat (preexistent).

## Urmatorul cluster: MovementType nomenclator | d406
D406 (SAF-T). "MovementType" = nomenclatorul ANAF de miscari de stoc. Codul are DEJA MISCARI_STOC = {10:Achizitie,
20:Productie, 30:Vanzare}, MOVEMENT_IMPLICIT="10" (d406.py ~91-96), documentat validator-confirmat (trimitea "1"
care nu exista). Tipar probabil VERIFICARE + gard (ca UoM: confirma codurile pe validator/jar + default + semnal).
NOTA: clusterul URMATOR (BaseRate) e in acelasi comentariu: BASE_RATE=1 (pro-rata standard = 1 intreaga suma, NU
100). Sursa d406 = XSD saft.xsd (/opt/duk/saft/saft.xsd) + D406Validator.jar (/opt/duk/saft/val/...) - se pot EXTRAGE
codurile din jar (ca la UoM: grep pe coduri distinctive). DUK d406 = xfail preexistent (baza SAF-T nu-i valida).

## INCHIS rularea 11: UoM UN/ECE | d406
Verificat CONFORM: UOM_UNECE = coduri UN/ECE Rec.20 (nu unitati RO), validator-confirmate (proba 15.07 BUC respins +
extractie D406Validator.jar: H87/KGM/.../MWH prezente, BUC absent); default H87 + semnalare la necunoscut; XSD =
SAFcodeType (lista in validator, nu enumerare). Gard nou. Metoda utila d406: extractie coduri din jar + XSD.

## INCHIS rularea 10: plan conturi pe norma | d406
Verificat: planul SAF-T filtrat pe nomenclatorul oficial al normei (plan_oficial); conturi ne-norma excluse (ANAF
le respinge), AccountID sintetic. REPARAT drop TACIT: conturile excluse (strain) nu erau surfaced (pull nici nu le
returna); acum pull le returneaza si genereaza le SEMNALEAZA in avertisment (numite) - ca N in d394 (Costin: exclus
dar VIZIBIL). Gard DB nou. Corectat inventar (fisiere test_limita_text -> test_d406).

## REZOLVAT rularea 8 (decizie Costin executata): operatiuni N neinreg | d394 - approach (b)
Bug-ul activ N (achizitii de la neinregistrati -> D394 respins) e REZOLVAT cu approach (b) ales de Costin:
operatiunile N se EXCLUD din D394 cu AVERTISMENT VIZIBIL (numeste furnizorul+suma, in res.avertismente -> payload
coada -> UI+flux, nu doar log); restul declaratiei ramane valid. Gard anti-regresie pastrat. DATORIE (in GARZI 04.08)
pt implementarea completa (a): tip_N (camp nou contabil, UI bunuri/servicii) + tip_document 2-5 (extindere contract)
+ document_N = CAMPANIE PROPRIE dupa ce se decide UI-ul pt tip_N. Vezi DECIZII 04.08.

Clustere d394 inchise rularea 6-9 (TOATE d394 din secventa GATA): tip_partener (pct.216), rezumat1 (tp1/tp3 conform + N=approach b excludere cu avertisment), nomenclator codPR (validator-confirmat, gaze 36; lit.l rezolvat 6675f19), totalPlata_A R17 (sursa unica + R17 pe validator). Datorie d394 ramasa: suport COMPLET N (approach a) = campanie proprie dupa UI tip_N (GARZI 04.08).

## Ce am facut in rularea asta (MULT: audit mare + 6 clustere; HEAD 93b01a6 -> c185188)
### A. AUDIT "limita text" pe TOATE cele 9 declaratii cerute de Costin + d710 (2 commituri: 7be77a3 + 1687dec)
Datoria "limita text 75" din predarea rularii 3 e ACHITATA. Premisa veche (comentariul text_anaf: "ANAF respinge
orice text >75") era FALSA - INFIRMATA de proba DUK boundary-cu-boundary pe fiecare camp. Rezultat:
- **core.common.LIMITE_TEXT_ANAF** = SURSA UNICA a limitelor de text {declaratie: {camp: C(n)}}, din structura
  oficiala, confirmate DUK (den/denR/denP/denO 200, adresa/adresaR 1000, functie_declar 50, functie_reprez 100,
  nume/prenume/numeAsig/prenAsig/den_intocmit/calitate_intocmit 75, den1 100, banca/cont 50, telefon 15, mail 200;
  d406 SAF-T: tipuri XSD 18/35/70/256).
- **common.text_anaf CERE acum limita explicit** (scos default-ul global 74 - un apel fara limita = TypeError).
  Toate generatoarele (d100/d101/d112/d205/d300/d301/d390/d394/d710/d406) paseaza limita din registru.
- 3 clase de defect reparate: OVER-trunchiere (den/adresa/nume taiate la 74 = pierdere date); UNDER-trunchiere
  (functie_declar 74>50 => ANAF RESPINGEA); FARA-limita (denO/denP/mail/banca/cont/telefon/Customer-Supplier Name
  SAF-T netrunchiate => respingere daca depaseau).
- **GARD DE CLASA** (cerut de Costin): `test_limitele_de_text_vin_din_registry` (core/test_limita_text_anaf.py) -
  scaneaza AST fiecare generator, RESPINGE orice apel text_anaf/_t care nu ia limita din LIMITE_TEXT_ANAF. O limita
  ne-oficiala (literal / lipsa) e imposibila. Plus test_generatoarele_trunchiaza_la_limita_per_camp +
  test_limite_text_confirmate_pe_duk_boundary (proba DUK). Testul blanket-75 rescris pe limite per-camp.
- Ramase: nr_doc d301 EXCLUS din registru (DUK respinge si la C(20) - nu-i limita de lungime, are alte reguli).
  d406 DUK boundary N-A putut fi probat (d406 DUK = xfail preexistent "cont referit absent din chart"); limitele
  d406 vin din XSD SimpleTypes (oficial), pazite de gardul de clasa + validarea XSD SAF-T.

### B. Clustere din lant inchise (verzi, bifate in Inventar A)
- **checksum totalPlata_A | d205** (3a1f69c): aliniere sursa unica (ultimul outlier clasa-d100).
- **trunchiere den/adresa | d205** (bbf1967): neconformitate DUK (den200/adresa1000/functie50/den1-100).
- **randuri / checksum | d300** (8192249): verificat + excludere 14.1/14.2.
- **checksum totalPlata_A (R28) | d301** (93b01a6): verificat + gard legatura.
- **nomenclator tari (HR->CR) | d390** (c185188): NECONFORMITATE - maparea HR->CR era GRESITA. Proba DUK: tara=CR
  RESPINSA ("nu se afla in lista"), tara=HR VALID. _TARA_XML golit, Croatia emite HR. Restul TARI_UE conform
  (GB/XI DUK-valide pt 2026). Un partener croat real facea D390 respins - bug latent.
- **tipuri operatiune (pct.215) | d394** (bb6e0c4): VERIFICAT (TIPURI = exact structura, pin adaugat) + DATORIE ASI.
  Probat izolat pe DUK: validatorul accepta 8 tipuri (L/V/A/C/N/LS/AS/AI) dar RESPINGE **ASI** ("nu se afla in
  lista") - struct pdf are ASI, jar-ul NU (discrepanta pdf-vs-jar). Corectare BLOCATA pe decizie produs (scoate ASI
  vs remapare vs versiune validator - schimba ce declara contabilul). Gard anti-regresie adaugat. VEZI datoria jos.
- (guvernanta §2.3 c1a679c: PREDAREA trimite la reguli - vezi prima linie a acestui fisier.)

## LECTIE MARE a rularii (de tinut minte): COMENTARIUL NU E O PROBA
De DOUA ori in aceasta rulare un comentariu de cod care declara o regula "corecta si verificata" era GRESIT, si
DUK a aratat imediat adevarul: (1) text_anaf "ANAF respinge >75" - fals, fiecare camp are C(n) propriu; (2) d390
"HR se scrie CR in nomenclator" - fals, e HR. Regula: orice remapare/limita (tara, cod bugetar, tip, lungime) se
PROBEAZA pe validatorul DUK, nu se ia pe incredere din comentariu. (Extinde R17: validatorul e autoritatea.)

## Reguli permanente (rezumat - detaliile in CLAUDE.md §2.2/§2.3)
- NU push pe main (decizia c). Push de siguranta la finalul rularii: `git push -f origin HEAD:backup/lant-20260803`.
  Ultimul la c185188.
- Nu opri lantul la granite curate. Continua pana la un criteriu §2.3 (blocat / decizie produs / neconformitate care
  cere oprire / poarta rosie sau tree murdar / context epuizat). Oprirea rularii asta = CONTEXT (pct.6), la c185188.
- Fiecare cluster: red->green sau verificare, gard §9, DECIZII/GARZI/TESTE actualizate, Inventar A bifat √, secventa
  regenerata (renumerotare DOAR pe blocul secventei - atentie sa nu atingi alte liste numerotate din TESTE.md),
  consistenta secventa==calculata (test_agenda), commit LOCAL.
- Gard anti-stale test_agenda: bifa Inventar A in ACELASI commit doar daca fisierul de test EXISTA deja in git.
- §3: TEXTUL/STRUCTURA castiga fata de intelegere, DAR probeaza pe DUK (vezi lectia de mai sus + R17). Atentie la
  derogari temporare (OUG) care nu-s in textul consolidat.

## Datorii deschise (in DECIZII.md, campania "achitare datorii")
ACHITATA rularea 3-4: limita text (toate declaratiile). ACHITATA rularea 6: ASI in D394 - REZOLVAT cu greenlight Costin. ASI scos din TIPURI/TIP_COTA_ZERO/REZ1_FARA_TVA (8 tipuri A,L,C,V,AI,LS,AS,N, aliniat validatorul J8). OPANAF 77/2022 (MO 95/2022, salvat anaf_surse/opanaf_77_2022.* cu sha256) CONFIRMA fost-ASI->AS. Fara date ASI de migrat (op1.tip nepersistat). Gard devenit INVERS (test_asi_ramane_scos_gard_invers). NOUA DATORIE (follow-up non-blocanta, rularea 6): d301_struct (2013) si d390_struct (2020) sunt surse INVECHITE in anaf_surse/ - reimprospateaza-le de la ANAF si re-verifica listele de tipuri/nomenclatoare pe validatorul curent, ca la d394 (codul lor e deja validator-verificat, non-urgent). d394_struct marcat INVECHIT (sursa curenta = opanaf_77_2022). LECTIE: un pdf de structura vechi in anaf_surse/ e o mina - marcheaza-l INVECHIT, sursa de tipuri/nomenclatoare = validatorul INSTALAT + ordinul din MO. Vezi DECIZII 03-04.08. Ramase: d406 DUK xfail (cont referit absent) - cand se
repara, se poate adauga proba boundary d406. nr_doc d301 (reguli de format DUK, nu lungime). Preexistente: A2
(D390 ziua 15), A3 (D177 form), C1/C2 (tichete cresa/culturale MO), C3 (amortizare MF neliniara xfail), C4 (D112
avantaje 8.3), C5 (migrare tichete). D101 scadenta lege-vs-validator (decizie produs Costin).

## Xfail-uri (21) = registrul de datorie (test_datorie.py) + d101/d406 smoke DUK (test_smoke_duk). Nu le "repara"
fara sa citesti motivul.
