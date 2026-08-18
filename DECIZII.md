# iConta — REGISTRU DE DECIZII

**De ce am facut asa.** Pentru CE s-a facut si CAND -> ISTORIC.md. Pentru ce urmeaza -> DE_FACUT.md.
Pentru norma UI -> DESIGN_SYSTEM.md. Pentru cod -> git.

## 27.07.2026 — D406 (SAF-T) NU e depunabil: gap cunoscut

Verificat la sursa (git + ANAF). In D406 periodic, SourceDocuments (SalesInvoices/PurchaseInvoices) e OBLIGATORIU la nivel de linie de factura (InvoiceLine cu AccountID + TaxInformation). Generatorul nostru (core/d406.py) emite, de la snapshot-ul initial (cbf24ce), o SINGURA linie sintetica per factura (cont 707/371, cantitate 1, pret = net total, descriere = numele partenerului), NU liniile reale din `factura_linii` (n. atins niciodata); Payments = gol.

Proba DUK din IULIE (15-16.07, nu iunie) a fost pe STRUCTURA: 15.07 validatorul accepta "orice gunoi" (namespace), apoi "36 erori -> 1", apoi 16.07 "VALID pe date reale + profil minim izolat — 5 discrepante structurale". DUK verifica FORMA, nu completitudinea continutului -> un fisier cu facturi sintetice trece validarea dar e INCOMPLET fata de cerinta ANAF.

CONSECINTE (27.07): afirmatia PERMISE "D100-D406 pe DUK" era inselatoare pentru D406 -> mutata pe INTERZISE; F035/F036/F037 -> PARTIAL. Generatorul NU se repara acum (sesiune separata). REPARATIA presupune: SalesInvoices/PurchaseInvoices cu liniile REALE pe produs (din factura_linii: cod, cantitate, pret unitar, AccountID + TaxInformation pe fiecare linie) + sectiunea Payments; apoi re-validare DUK pe CONTINUT real.

## 27.07.2026 -- D301: ecran de introducere + rollup fiscal S4.1->S4 (bug prins de proba DUK)

D301 (decont special TVA) avea generatorul (core/d301.py) dar ZERO cale de introducere a operatiunilor: fara rute, fara UI -> tabela d301_operatiuni netouched -> declaratie mereu goala. Adaugat: ecran incorporat in fluxul de declaratii (declaratii.js, panou d301 in pas2, geaman cu d390-clasificare), rute GET/POST/DELETE /tenants/{id}/d301-operatiuni (cere_cabinet), backend core/d301_operatiuni_api.py.

Decizii fiscale, verificate LA SURSA (nu deduse din DUK):
- Cota TVA: 21% standard / 11% redusa / 0% (Legea 141/2025, din 01.08.2025). Standardul vine din common.cota('tva_standard', data) PERIOD-AWARE, nu constanta literala (o cota hardcodata devine gresita la urmatoarea schimbare, ca 19->21).
- TVA se CALCULEAZA (baza x cota) si se STOCHEAZA: d301.calcul_d301 CITESTE tva din DB, nu-l recalculeaza (doar baza=val x curs). Fara stocare -> tva=0 -> declaratie valida structural dar substantial gresita (fals-verde). baza NU se stocheaza (generatorul o recalculeaza; tabela n-are coloana baza).
- data_doc: format ANAF ZZ.LL.AAAA (structura poz.35, C(10), DA), validat la backend -- DUK respinge orice altceva ("data calendaristica eronata").

ROLLUP S4.1->S4 (bug REAL prins de proba, contrar afirmatiei "tip 5 cu parinte 4 - facut deja"): OPANAF 592/2016, instructiunile formularului 301: "In sectiunea 4.1 se preiau DIN sectiunea 4 doar achizitiile de servicii intracomunitare pentru care beneficiarul e obligat la plata TVA cf. art. 307 alin. (2)". Deci S4.1 (tip 5) e SUBSET al S4. calcul_d301 punea tip 5 DOAR in tot[5] -> baza4=0 -> DUK respingea (R32: "4.1 fara 4"; R24/R25: baza4 != suma sectiunilor tip 4). D301 fusese "validat" pe un caz FARA tip 5 -- acelasi tipar verde-pe-cazul-care-nu-atinge-defectul. Reparat: tip 5 se preia SI in tot[4] (header) SI emite ambele randuri <sectiune tip=4>+<sectiune tip=5> (detaliu). totalPlata_A ramane formula oficiala (baza1..5 + tva1..5, SUMA DE CONTROL, nu TVA datorat): DUKIntegrator R28 o impune si RESPINGE orice alt total (dovedit numeric: total pe sectiunile 1-4 = 6022 -> R28 cere 12044). Cu rollup, checksum-ul include serviciul in baza4 SI baza5 PRIN DEFINITIE -- nu e dubla impozitare: TVA-ul DATORAT e tva4 (serviciul o singura data). DUK = judecatorul final peste instructiunile PDF (CLAUDE.md). Regresie: core/test_d301_rollup.py.

Proba: operatiune tip 5 (servicii UE, EUR, curs 4.9770, cota 21%) pe tenant_001 iunie 2026 -> D301 -> DUKIntegrator "valid" (baza4=baza5=4977, tva 1045, totalPlata_A=12044); op de proba stearsa. Porti: pytest 1048 passed, verificator TOTAL 0, DUK valid. NOTA: proba pe tenant_001, NU tenant_002 -- tenant_002 (DANTE INTERNATIONAL) n-are IBAN in profil, generatorul refuza corect; nu s-a fabricat un IBAN pe o firma reala.

LECTIE (regula, nu caz izolat): totalPlata_A NU e TVA-ul datorat, e SUMA DE CONTROL definita de structura ANAF (poz.28) ca baza1..5 + tva1..5. Doua lucruri diferite cu acelasi nume "total". Regula "cele 4 sectiuni" din instructiuni priveste COLOANELE (curs, baza, TVA), nu totalul. Cu rollup, checksum-ul include serviciul in baza4 SI baza5 prin definitie -- fara dubla impozitare, pentru ca TVA-ul DATORAT ramane tva4. Consecinta pentru orice generator viitor: cand structura ANAF are un camp "total", verifica DACA e suma fiscala sau checksum de structura. Un checksum NU se "corecteaza" dupa logica fiscala -- se calculeaza cum cere structura, altfel DUK il respinge (aici R28). DUK = judecatorul final peste instructiunile PDF.

## 29.07.2026 -- Faza 0 (curatenie date de test): criterii si lectii

Context: golirea completa a bazei de firme/cabinete/utilizatori (TESTE.md Faza 0), inainte de cele 7 firme derivate din legislatie.

CRITERIU stergere: un tabel din public se sterge la curatenia de date DOAR daca are legatura STRUCTURALA cu firma/cabinetul/userul (FK sau coloana tenant_id/firm_id/user_id). Numarul de randuri NU e criteriu. alerte_fiscale (39 randuri) e tabel GLOBAL cu stiri ANAF reale scrapate de monitor_fiscal - fara nicio legatura la firma. Stergerea n-ar fi curatat niciun reziduu si ar fi pierdut istoric care nu se reface (ANAF roteste pagina de noutati). PASTRAT.

CRITERIU izolare test de integrare: depinde de CINE detine conexiunea.
 - functie CITITOARE care primeste conn -> traieste in tranzactia fixturii -> ROLLBACK curata (tiparul test_pull_declaratii);
 - functie SCRIITOARE care isi deschide propria conexiune si comite -> ROLLBACK-ul fixturii n-are ce anula -> schema efemera COMISA + DROP la teardown, cu DROP IF EXISTS la setup pentru siguranta la crash.
Nu se refactorizeaza cod de productie ca sa serveasca un test (coada nu misca cainele). Gasit 29.07 la decuplarea test_spv_receive si test_etransport_send de tenant_002.

SCAN COMPLET (nu partial): scanul dupa teste cuplate la tenant a gasit PATRU fisiere, nu doua cate la prima cautare - test_spv_receive, test_etransport_send, test_limita_text_anaf, test_control_incrucisat. Un scan partial da impresia ca s-a terminat.

LECTIE (gard cu punct orb): un gard care sare pe SINGURA firma unde ar trebui sa prinda are punct orb fix unde traieste bug-ul. 27.07: reparasem limita de 75 de caractere si scrisesem gardul test_limita_text_anaf pe tenant_001 (denumire 115 car.). Toate cele 5 generatoare care inca emiteau den/adresa BRUT (d100/d101/d205/d406/d710) sareau cu "nu se datoreaza" - deci gardul era verde exact pentru ca nu atingea cazul. Descoperit 29.07 abia cand testul a fost decuplat de firma persistenta si a primit o firma efemera care datora toate declaratiile. Consecinta pentru orice gard: daca sare pe cazul-limita, nu e gard - verifica ce ACOPERA efectiv, nu cate teste trec.

TEMEI limite de lungime SAF-T (d406): <Name>=SAFlongtextType 256, <StreetName>/<LastName>=SAFmiddle2textType 70, din XSD-ul SAF-T. NU 75 (limita ANAF pentru declaratiile clasice D1xx/D3xx). Verificat la sursa 29.07 - _t() cu 74 ar fi depasit la StreetName/LastName si ar fi trunchiat inutil Name. Fiecare format are limitele lui; nu se presupune ca sunt aceleasi. Golurile reziduale (d205/d390 neexercitate, d710 lipsa din garda) -> xfail(strict) in test_datorie.py, cad singure la Faza 1.

---

## Cum se foloseste
- Se ADAUGA la sfarsit, cronologic. Nu se editeaza istoria. O decizie rasturnata primeste
  intrare noua care trimite la cea veche.
- NU e normativ. Norma traieste unde se APLICA si se VERIFICA mecanic (DESIGN_SYSTEM.md +
  verificator, docstring de modul, cod). Registrul trimite catre ea. Doua surse de adevar = drift.
- Nu se citeste tot. Se cauta: grep -n "pontaj" DECIZII.md

## Ce intra AICI (si nu se pierde in chat)
1. Orice raspuns la un STOP al lui Claude Code -> e decizie, se scrie.
2. Orice verificare la sursa care a schimbat un plan.
3. Orice RESPINS/AMANAT, cu motiv.
4. Orice alternativa respinsa - de ce NU, nu doar ce DA.

## Format
    ### [DATA] TITLU  (unde s-a aplicat: fisier/commit)
    DECIZIE: ce s-a hotarat, intr-o propozitie.
    TEMEI: sursa verificata (lege/OPANAF/doc oficial/grep) sau rationament.
    ALTERNATIVA RESPINSA: ce nu s-a facut si de ce.
    LIMITA: ce nu s-a verificat. Ce ar rasturna decizia.

---

### 16.07.2026 F149 RESPINS — case de marcat / POS / imprimante  (FUNCTIONALITATI.csv:150)
DECIZIE: nu se construieste integrare hardware (case de marcat, POS, imprimante termice, cantare).
TEMEI: iConta = platforma de CABINET, nu de vanzare. Casa de marcat sta la clientul clientului.
Zero reutilizare in platforma: drivere per producator (Datecs/Tremol/Custom/Epson) + certificare AMEF.
Valoarea fiscala intra deja prin raportul Z in registrul de casa.
ALTERNATIVA RESPINSA: "o au concurentii (SAGA/SmartBill/Oblio/WinMentor)" - ei vand FIRMEI care
emite bonuri; iConta vinde CABINETULUI. Alt client, alta arhitectura.
LIMITA: daca apare un cabinet cu multi clienti retail care cer asta, se reevalueaza.

### 17.07.2026 Model certificat SPV: aplicatie + certificat per cabinet  (ARHITECTURA_SPV.md)
DECIZIE: iConta = aplicatie inrolata la ANAF cu UN Client ID; fiecare cabinet autorizeaza cu
certificatul LUI. iConta NU e imputernicit, NU detine certificat.
TEMEI: procedura oficiala ANAF (static.anaf.ro/.../Oauth_procedura_inregistrare_aplicatii_portal_ANAF.pdf)
- dezvoltatorul e identificat printr-un client app id; utilizatorii prin serialul certificatului.
Verificat 17.07 ca SmartBill face identic (ajutor.smartbill.ro/article/982).
ALTERNATIVA RESPINSA: modelul (2), iConta imputernicit cu certificat central - ar cere declaratia
150 per firma client, ar muta RASPUNDEREA PE DEPUNERE la iConta, si un token stricat ar opri
toti clientii. Contrar identitatii de produs: contabilul depune, iConta e unealta.
CONSECINTA: firma (SRL) = vehicul comercial (contracte, facturi, GDPR-procesator), NU intra in
lantul ANAF. Contul de dezvoltator e pe persoana fizica (CNP), nu pe CUI.

### 17.07.2026 F127/F128 AMANAT — fara API de depunere; SPVWS2 cere certificat local  (FUNCTIONALITATI.csv)
DECIZIE: amanate, nu respinse. Termen de reevaluare: 17.08.2026.
TEMEI: (a) nomenclatorul OAuth ANAF contine DOAR e-Factura si e-Transport; (b) README oficial
MfpAnaf/ClientSPV listeaza "transmitere declaratii" la sectiunea de VIITOR; (c) SPVWS2 se
autentifica prin mTLS cu certificat local (Sign.java: KeyStore PKCS11) - sub eIDAS cheia privata
nu paraseste dispozitivul calificat, deci nu ajunge pe serverul Linux. Varianta cloud certSIGN
cere aplicatia vToken pe Windows/macOS. NICI SmartBill nu are mesaje SPV - e limita ANAF pentru
toti jucatorii cloud, nu gaura in iConta.
ALTERNATIVA RESPINSA: agent desktop la cabinet care ruleaza cu tokenul - e ALT PRODUS
(instalare + update + suport pe calculatoare straine).
LIMITA: verificat certSIGN (1 din 4 furnizori). Intrebare trimisa la spv.webservice@mfinante.ro.
Raspunsul afirmativ la OAuth pentru SPVWS2 rastoarna decizia si redeschide si rapoartele
'cerere' (vector fiscal, situatie sintetica, neconcordante D112-REVISAL).

### 17.07.2026 Inventar declarativ: 3 gauri reale, nu 40  (DE_FACUT.md)
DECIZIE: se construiesc D106, D230, D307. Restul: respins sau amanat cu motiv.
TEMEI: comparatie MECANICA (grep) cu lista oficiala ANAF (static.anaf.ro/.../descarcare_declaratii.htm).
Construite: D100, D101, D112, D205, D212, D300, D301, D390, D394, D406 + bilanturi S1005/S1003.
DECLANSATOR: alerta monitor_fiscal (OPANAF 138/2026, D204) a scos la iveala ca D204 nu exista -
si nu ca decizie, ci ca ABSENTA NETRATATA. Problema de proces: cele 9 declaratii au venit din ce
s-a vazut la cabinete, nu dintr-o lista completa.
ALTERNATIVA RESPINSA: "toate tipurile de declaratii". Fiecare formular = abonament permanent la
mentenanta (OPANAF le modifica anual). 40 de formulare = 40 de abonamente, pentru un singur om.
Nu constructia e costul, ci intretinerea.
REGULA PERMANENTA: orice declaratie noua intra in monitorul fiscal ODATA cu ea. Construita si
nemonitorizata = datorie, nu functionalitate.
LIMITA: nivelul 3 (D204, D104, D107, D108, D180, D223, D209, D221) ramane nedecis pana se stie
daca cabinetele-tinta au asocieri/ONG-uri. Intrebare de piata, nu tehnica.

### 17.07.2026 F131 notificari scadenta: praguri {-3, +1, +7}, opt-in OFF  (commit 10c91b1, 71cb9ca)
DECIZIE: praguri {-3, +1, +7} zile fata de scadenta. Opt-in per firma, implicit OFF. Supape:
notificare_stop + notificare_amanata_pana per factura. Reply-to = firma_profil.email,
From = contact@iconta.eu. "Stadiul curent" la zi ratata de cron, nu match exact pe azi.
TEMEI: emailul pleaca spre CLIENTUL firmei, in numele firmei - e act comercial catre un tert,
nu notificare interna ca F103. Scenariul care doare: firma a negociat telefonic o amanare,
cronul trimite somatia oricum, firma pierde clientul si da vina pe iConta.
ALTERNATIVA RESPINSA: pragul +14 (a doua somatie automata) - escaladarea o decide omul, nu cronul.
ALTERNATIVA RESPINSA: From pe domeniul firmei - ar pica SPF/DMARC -> spam.
LIMITA: daca un cabinet cere praguri proprii, setul devine configurabil per firma.

### 17.07.2026 F135 pontaj: informativ, NU alimenteaza proratarea  (LIVE, commit a52ded3; core/pontaj.py)
DECIZIE: pontajul v1 = evidenta de prezenta pura. NU atinge calculul salarial.
TEMEI: verificare la sursa (Claude Code, stat_plata liniile 32-33): brutul e DEJA proratat dupa
concedii medicale - brut_lucrat = brut x (zile_luna - cm_zile) / zile_luna. Un pontaj care ar
prorata brutul dupa absente ar atinge formula fiscala.
ALTERNATIVA RESPINSA: (b) pontajul alimenteaza proratarea - ar cere stabilirea, la sursa in
Codul fiscal, a ce tipuri de absenta prorateaza. Risc fiscal pentru castig de comoditate.
LIMITA: se reevalueaza cand apare un caz real (contabil care cere proratare automata pe absente
nemotivate). Pana atunci contabilul ajusteaza manual.

### 17.07.2026 F136 adeverinte: un singur tip, generic; NU "pentru banca"  (LIVE, commit 6891bfc; core/adeverinta.py)
DECIZIE: o singura adeverinta de salariat, generica, cu camp liber "scopul" si camp "mentiuni".
TEMEI LEGAL (verificat la sursa): art. 34 alin. (5) Codul Muncii (Legea 53/2003) - angajatorul e
obligat sa elibereze document care atesta ACTIVITATEA DESFASURATA, DURATA ACTIVITATII, SALARIUL,
VECHIMEA IN MUNCA / IN MESERIE / IN SPECIALITATE. Dublat de art. 40 alin. (2) lit. h).
Termen legal: 15 zile de la solicitare (HG 905/2017); 60 zile in insolventa/faliment.
MODELUL E LA LATITUDINEA ANGAJATORULUI - nu exista format impus, nu se inregistreaza la ITM.
Cele 5 elemente de mai sus sunt continutul minim OBLIGATORIU.
ALTERNATIVA RESPINSA: "adeverinta de venit pentru banca" - verificat: Raiffeisen si Salt Bank au
formulare PROPRII tipizate, pe care le vor completate (Raiffeisen cere DOI reprezentanti legali).
Un PDF generic nu e acceptat. In plus, din 2026 bancile verifica veniturile direct la ANAF;
adeverinta se mai cere doar in situatii speciale. Am fi construit pentru un flux in declin,
cu o promisiune pe care n-o putem tine.
CAZURI REALE RAMASE (fara format impus): gradinita/scoala, viza, notar, inchiriere, medic de
familie, instanta. In ecran: nota onesta "pentru credit bancar, banca cere formularul propriu".
DECIZII DE IMPLEMENTARE (17.07): nr. de iesire = input MANUAL al contabilului (nu contor cu
schema) - F146 registratura l-ar automatiza; salariul = brut+net pe o luna de referinta (an/luna),
net calculat prin salarizare.calcul_salariu. Datele auto: firma+salariat+net din DB; restul (CI,
CIM, tip contract, departament, vechime, scop, mentiuni) = input.
LIMITA: nu acoperim cerintele exacte per institutie (variaza) - doar minimul legal art.34(5).
Vechimea "in munca/meserie/specialitate" totala (cariera) nu e in DB -> input manual; din
data_angajare se poate pre-completa doar vechimea in ACEASTA firma.

### 17.07.2026 Proratare CM + zile lucratoare: exclud sarbatorile, sursa unica  (core/scadente.py + stat_plata_api.py + d112.py + main.py + flux_concediu.js)
DECIZIE: numarul de zile lucratoare ale lunii (NUMITORUL proratarii CM) SI zilele de CM
(NUMARATORUL, auto-calc) exclud sarbatorile legale. Sursa UNICA: scadente.zile_lucratoare_luna
/ zile_lucratoare_interval, cu Pastele ortodox CALCULAT (formula Meeus), NU hardcodat.
TEMEI (verificat la sursa): OUG 158/2005 art. 10 alin. (5)-(6) - din zilele calendaristice de
CM se platesc zilele LUCRATOARE, iar la stabilirea lor se tin cont de sarbatorile legale
(exemplu oficial confirma ca se scad). Vinerea Mare = sarbatoare legala (Legea 220/2016),
depinde de data Pastelui -> se calculeaza, nu se hardcodeaza.
ALTERNATIVA RESPINSA: weekday<5 (ce era in cod, in 4 locuri: stat_plata x2, main.py, d112).
Ignora sarbatorile -> proratare gresita in ORICE luna cu sarbatoare pe zi lucratoare + un CM.
Ex. aprilie 2026 (Vinerea Mare 10 + Paste 13): brut 5000, CM 5 zile -> dadea 3863,64 in loc de
3750 (diferenta 113,64 lei/luna), si zile CM gresite RAPORTATE IN D112.
INCIDENT (de ce centralizarea conteaza): exista DEJA o a doua sursa de adevar hardcodata -
tabelele _D112_NZL_2025/2026 in d112.py - CORECTE (excludeau sarbatorile) dar: (a) doar 2 ani,
(b) o linie folosea tabelul 2026 pentru ORICE an, (c) coexistau cu un weekday<5 gresit in
ACEEASI functie. Doua definitii ale "zilei lucratoare" in acelasi cod = exact ce ascunde bug-ul
(fluturasul dadea o cifra, D112 alta). Eliminate; formula Meeus le reproduce EXACT pe 2025+2026.
LIMITA: calendarul valabil [2024, 2099] (setul fix cu 6-7 ian din 2024; offset iulian +13 pana
2099). In afara -> ValueError VIZIBIL, nu rezultat tacut gresit (cum era 2025, care lipsea
complet si dadea weekday<5). Setul de sarbatori fixe (art. 139 Codul muncii) se reverifica daca
legea se schimba. NUMARATORUL cm_zile ramane suprascriabil de contabil (auto-calc = doar default).

### 17.07.2026 Lot 4 Stoc — F138 multi-gestiune AMANAT PANA LA TESTARE (nu pe nedeterminat)  (specificatie, neimplementat)
DECIZIE: multi-locatie descriptiva (Tier 1, doar eticheta pe miscare, CMP global) se
construieste ACUM. Multi-gestiune cu CMP separat per depozit (Tier 3) se AMANA explicit
pana la faza de testare/dare in folosinta a aplicatiei complete, nu pe nedeterminat.
TEMEI: verificat SAF-T D406 - sectiunea de stocuri NU e obligatorie decat la cererea
expresa ANAF (termen minim 30 zile de la solicitare), si chiar si atunci doar daca
evidenta e cantitativ-valorica sau operativ-contabila. Stocurile pe global-valoric NU
se raporteaza deloc (smarttax.ro, forum.sagasoft.ro - caz real cu depozit + puncte de
lucru pe gestiuni distincte, global-valoric).
TREI NIVELURI, nu doar "cu/fara multi-depozit":
  1. Multi-LOCATIE (eticheta descriptiva pe miscare, CMP ramane global) - ieftin, aditiv,
     NU atinge fiscalul. BUILDABIL ACUM.
  2. Multi-GESTIUNE global-valoric (depozite separate, dar fiecare tot global-valoric) -
     mediu, nu intra in raportarea D406 stocuri.
  3. Multi-GESTIUNE cantitativ-valorica (CMP separat per depozit, transfer = ricoseu in
     valorizare, D406 segmentat) - scump, ireversibil odata ce intra date reale.
MOTIVUL AMANARII (nu respingerii): promisiunea de produs e "contabilitate completa".
Nivelul 3 e parte din acea promisiune, dar formatul lui (separare stricta pe depozit vs.
stoc comun cu raportare pe locatii, CMP unic vs per-gestiune) depinde de CUM lucreaza
cabinetele-tinta - necunoscut azi. Construit pe ghicit, o corectie ulterioara nu e
git revert, e o discutie cu un cabinet despre de ce cifrele lui din ultimele luni difera.
REPER DE TIMP: reevaluare la faza de testare a aplicatiei complete (nu "cand apare
cazul", ca sa nu devina a doua D204 - uitata pana o scoate la iveala intamplarea).
Pana atunci: NEVOI_RATATE.md capteaza orice semnal real (cabinet care cere multi-depozit
in discutii de vanzare/suport) + verificare directa in firma_profil (puncte de lucru
existente) inainte de a intra in constructie.
ALTERNATIVA RESPINSA: constructia acum a nivelului 3, pe presupunere - risc simetric cu
ce a produs bug-ul CM de azi (forma gresita, scrisa o data, propagata tacut in CMP/D406
pentru TOTI clientii, nu doar cel cu multi-depozit).

### 17.07.2026 F140 analitica de stoc: fara model de forecast (consum comparabil in loc)  (core/stocuri_cv_api.py analitica; LIVE)
DECIZIE: F140 livreaza stoc critic + inert + ABC-Pareto + consum pe perioade comparabile
(iesiri 30 zile vs 30 anterioare). "Prognoza pe perioade comparabile" din descrierea initiala
NU se implementeaza ca model de forecast (predictie de cerere).
TEMEI: un forecast onest cere alegerea metodei (medie mobila? sezonalitate? trend?) si a
orizontului, care depind de tiparul de vanzare al fiecarei firme - necunoscut azi. Consumul
comparabil (cifre reale, nu predictie) da contabilului baza de decizie fara sa fabric o cifra
"prognozata" pe care produsul nu o poate sustine (acelasi rationament ca la adeverinta de venit
pentru banca, F136: nu promitem un flux pe care nu-l putem tine).
ALTERNATIVA RESPINSA: medie mobila simpla etichetata "prognoza" - ar da fals aer de predictie
unei extrapolari triviale; utilizatorul ar lua decizii de aprovizionare pe o cifra fara temei.
LIMITA: daca apare cerere reala de reaprovizionare automata pe baza de consum, se reia ca item
separat cu metoda stabilita explicit. ABC clasifica pe cumulativul INAINTE de item (primul
articol e mereu A, oricat de dominant), nu dupa - altfel articolul dominant iesea clasa C.

### 17.07.2026 F139 landed cost: contul de credit al accesoriului = confirmarea contabilului, nu ghicit  (core/stocuri.py nir_gv; LIVE)
DECIZIE: transport + taxe se repartizeaza PROPORTIONAL cu costul de baza al liniilor (cheia
standard cand nu e direct atribuibil), cu restul de rotunjire pe ultima linie ca suma repartizata
sa fie EXACT accesoriul. Capitalizarea intra in 371 (reduce adaosul, intra in K/descarcare).
Contul de CREDIT al accesoriului e PARAMETRU vizibil in formular, default 401 (transport furnizor)
si 446 (taxe vamale), pe care contabilul il confirma sau schimba.
TEMEI: OMFP 1802/2014 - costul de achizitie include taxele nerecuperabile de import si cheltuielile
de transport direct atribuibile. Regula de aur (CLAUDE.md): codurile de cont sunt coduri fiscale,
nu se ghicesc silentios in cod - de aceea contul e alegerea utilizatorului, cu default conventional
VIZIBIL, nu ascuns intr-o constanta. Notele sunt ciorne (contabilul valideaza).
ALTERNATIVA RESPINSA: (a) contul hardcodat 446 in motor fara ca utilizatorul sa-l vada - ar ascunde
o alegere fiscala intr-o constanta; import vs achizitie interna cer conturi diferite. (b) repartizare
pe cantitate/greutate - nu avem greutatea articolelor; proportional cu valoarea e cheia disponibila.
LIMITA: TVA-ul aferent accesoriului (transport are TVA deductibil, taxele vamale nu) se trateaza
SEPARAT de contabil - nir_gv capitalizeaza doar valoarea neta a accesoriului, nu-i calculeaza TVA-ul.

### 17.07.2026 F142 inventar pe mobil: acumulare pe ecran, nu sync multi-numarator  (static/js firme.js; LIVE)
DECIZIE: "cantitatile urca in timp real" din descriere = acumulare CLIENT-SIDE pe ecran pe masura
ce se scaneaza/numara, finalizata printr-o singura postare prin motorul inventar() existent.
Sincronizarea live intre mai multi numaratori simultan NU se construieste acum.
TEMEI: sync multi-numarator cere un TABEL DE SESIUNE de inventar (cine, ce a numarat, cand,
reconciliere) = schema noua = STOP de arhitectura (garda BRIEF). Coloanele autorizate pe 17.07
(locatie/barcode/nivel_minim/nir.transport/taxe) NU includ asa ceva. Un cabinet numara de regula
cu 1 telefon pe rand; multi-numarator simultan e nevoia unui depozit mare - aceeasi intrebare de
piata ca multi-gestiunea Tier 3 [[vezi Lot 4 Stoc F138]].
ALTERNATIVA RESPINSA: postare per articol la fiecare scanare (o ciorna per articol) - ar inunda
jurnalul cu zeci de ciorne pentru un inventar; acumularea + o singura postare da o ciorna per
diferenta reala. NUMARARE OARBA implicita (nu afiseaza scripticul): buna practica de control,
evita ajustarea numaratului la cifra asteptata.
LIMITA: se reia cu tabel de sesiune daca apare un cabinet cu inventar pe echipa. Pana atunci
NEVOI_RATATE.md capteaza semnalul.

### 17.07.2026 F144 profit-pe-produs / articol / agent RAMAS DESCHIS — vanzarea si descarcarea gestiunii sunt acte deconectate prin design  (core/rapoarte_comerciale_api.py; F144 v1 = doar felia fara aceasta problema)
DECIZIE: F144 v1 livreaza DOAR rapoartele care se pot construi pe schema actuala, read-only, din
`facturi` (fisa client/furnizor, vanzari pe partener, durata medie de incasare). Profit pe produs,
vanzari pe articol si vanzari pe agent NU se construiesc acum si NU se amana tacit — raman decizie
deschisa cu temeiul de mai jos.
TEMEI (verificat la sursa, Claude Code 17.07): vanzarea si descarcarea gestiunii sunt DOUA acte
deconectate prin design, nu printr-o coloana lipsa. Dovezi:
  - `miscari_stoc` NU are `factura_id` — se leaga doar de `inregistrare_id` (nota proprie) + `document`
    text liber (tenant_template.sql, DDL miscari_stoc).
  - `facturi_api.py` nu are NICIO referinta la stoc — emiterea facturii nu creeaza nicio iesire
    (grep "miscari_stoc|stoc|iesire|articol" core/facturi_api.py = 0).
  - descarcarea cantitativ-valorica e o ruta MANUALA separata (POST /tenants/{id}/stocuri/iesire,
    main.py:4859), cu corp {articol_id, data, cantitate} tastat de om, fara referinta la factura.
  - `factura_linii` nu are `articol_id` — venitul nu poate fi atribuit pe produs.
Ruptura NU e uniforma pe cele doua metode de gestiune:
  - CANTITATIV-VALORIC (miscari_stoc cu articol_id): ruptura e DEFECT — acelasi eveniment economic
    introdus de doua ori (factura + iesire manuala). Costul exista pe articol (miscari_stoc.valoare
    la CMP), dar nu are cheie de join spre vanzare.
  - GLOBAL-VALORIC (stocuri.descarcare_gv, lunar din totaluri contabile): ruptura NU e defect, e
    METODA. Costul pe articol nu exista prin constructie. Profit pe produs e IMPOSIBIL structural.
ALTERNATIVA RESPINSA: coloana `cost_achizitie` pe `factura_linii` — a doua sursa de adevar pentru
acelasi numar (costul traieste deja in descarcarea de gestiune, Lot 4). Ar diverge tacut.
ALTERNATIVA RESPINSA: `articol_id` pe `factura_linii` SINGUR — nu rezolva: leaga venitul de articol,
dar costul tot nu are cheie de join spre factura (miscari_stoc fara factura_id). Jumatate de punte.
LIMITA DECLARATA: pentru firmele pe GLOBAL-VALORIC, profit pe produs ramane gri PERMANENT, indiferent
de ce se construieste ulterior. NU se promite in UI (acelasi principiu ca adeverinta de venit / forecast:
nu promitem un flux pe care nu-l putem tine).
RAMAS DESCHIS: puntea factura -> iesire stoc pentru firmele CANTITATIV-VALORICE (elimina dubla
introducere si creeaza cheia de join venit<->cost) = LOT PROPRIU, nu acum. Carenta dublei introduceri
= DE_FACUT.md sectiunea CARENTE pct.4.

### 17.07.2026 Semafor fiscal faza 3: D394+D406 conectate; categorie contribuabil RESPINS; D301/D205 DESCHIS  (core/control_fiscal_api.py, core/scadente.py)
DECIZIE: semaforul deriva acum si D394 si D406 din vectorul existent. Nu se adauga atribut nou de
schema. D301 si D205 raman decizie deschisa (mecanism diferit).
TEMEI D406 (verificat la sursa, nu din memorie): OPANAF 1783/2021 Anexa nr.4, citit 17.07.2026 la
legislatie.just.ro/public/DetaliiDocument/248326 - "Contribuabilii care nu sunt inregistrati in
scopuri de TVA transmit Declaratia informativa D406 trimestrial"; platitorii urmeaza perioada
fiscala TVA (lunar/trimestrial). Astfel golul semnalat singur (neplatitorul n-are perioada fiscala
TVA) se inchide: neplatitor -> trimestrial, nu ghicit. Termen: ultima zi luna urmatoare (scadente.py).
TEMEI D394: OPANAF 3769/2015 upd 2194/2025 - doar platitori normali de TVA (art.316), perioada =
perioada TVA, termen 30 luna urmatoare. Ambele atribute (platitor_tva + tip_decont) exista in vector.
DEFECT COLATERAL REPARAT: scadente.py calcula d394 cu ziua 30 fixa -> crapa pe februarie (30 feb
inexistent). Latent (scadenta d394 nu fusese chemata niciodata, grep=0). Reparat: ziua = min(30,
ultima zi a lunii) - principiul legal "termen pe zi inexistenta = ultima zi". test_scadente.py apara.

ALTERNATIVA RESPINSA - atribut nou "categorie contribuabil" in vector (pt evaluarea istorica D406
pe categorii, mari 2022/mijlocii 2023/mici 2025): brieful declara semaforul ca ORIZONT SCURT (an
curent + decembrie an-1). Evaluarea istorica 2022-2024 e in afara orizontului PRIN CONSTRUCTIE -
atributul n-ar avea ce evalua. Din 2025 toate categoriile sunt obligate, deci categoria nu mai
decide DACA (toti depun), doar a decis CAND (istoric, in afara orizontului). Schema evitata.

RAMAS DESCHIS (nu se construieste) - D301 si D205: cer mecanism FACT-driven, nu vector-driven.
D301 (decont special TVA) = per LUNA cu operatiuni IC efective la un neplatitor; D205 (informativa
retineri la sursa) = rulaj pe cont 457 (dividende distribuite). Niciuna nu se decide dintr-un atribut
permanent de vector, ci dintr-un FAPT contabil pe perioada.
INTREBAREA DESCHISA (de decis, nu de presupus): mecanismul fact-driven EXISTA deja - control_incrucisat.py
citeste fapte contabile din note cu status='validata'. Deci NU e o extindere de design noua. Intrebarea
reala e de arhitectura: semaforul (azi vector-driven, "ce obligatii ai") devine si FACT-aware (citeste
notele ca sa stie ce s-a intamplat efectiv), SAU raman DOUA motoare separate cu roluri distincte -
vector-driven pentru obligatii declarative, fact-driven (control_incrucisat) pentru coerenta contabila?
De asta depinde nu doar D301/D205, ci si daca semaforul si controlul incrucisat converg sau nu.
LIMITA: pana la decizie, D301/D205 lipsesc din semafor - documentat aici, NU absenta netratata (lectia D204).

### 17.07.2026 Lot 6 F148 arhivare cloud AMANAT — nu doua integrari OAuth in paralel  (FUNCTIONALITATI.csv F148)
DECIZIE: F148 (sincronizare arhiva in Drive/OneDrive) se amana pana cand OAuth-ul SPV (conectorul
ANAF) e LIVE si testat. Nu se deschid doua integrari OAuth simultan. Lot 6 = F146 + F147 acum.
TEMEI: F148 cere un AL DOILEA flux OAuth (Google/Microsoft), pe langa OAuth ANAF care e in curs si
inca netestat complet (asteapta confirmarea inrolarii certificatului, 1-4 zile - vezi starea sesiunii
17.07). Doua integrari OAuth deschise in paralel = suprafata de auth dubla, refresh/rotatie de token
pe doi furnizori, si risc de a confunda un bug de flux cu altul exact cand SPV nu e inca inchis.
ALTERNATIVA RESPINSA: construirea F148 acum, in paralel cu SPV - castig de viteza aparent, dar
dubleaza complexitatea de autentificare intr-un moment fragil; un token stricat pe un flux ar
ingreuna diagnoza pe celalalt.
LIMITA / reevaluare: se reia cand OAuth SPV e confirmat LIVE si testat pe un cabinet real. Pana
atunci arhiva ramane locala (F148 = doar sincronizarea externa, nu arhivarea in sine).

### 17.07.2026 Lot 6 F146 registratura: registru UNIC intrare-iesire, v1 manual  (core/registratura_api.py; LIVE)
DECIZIE: registratura = un singur numar secvential per an, comun intrarilor si iesirilor, cu coloana
`directie` care marcheaza sensul (nu doua serii separate). v1 = registru MANUAL (contabilul
inregistreaza orice document si primeste numarul); fara hook automat la facturi/adeverinte.
TEMEI: registratura generala RO la firme private nu are format impus legal (instrument intern de
organizare); practica cea mai comuna e registrul unic de intrare-iesire cu un numar curent pe an.
Numarul se aloca din MAX(numar) per an +1 (resetare anuala naturala), cu UNIQUE(an, numar) care
garanteaza seria. Contorul nu e o coloana separata in firma_profil - se deriva din tabel.
ALTERNATIVA RESPINSA: doua serii separate (intrare 1..N, iesire 1..N) - unele firme le tin, dar
registrul unic e mai simplu si mai raspandit; se poate adauga o a doua serie daca un cabinet o cere.
ALTERNATIVA RESPINSA (v1): hook automat la emiterea facturii/adeverintei (nr_iesire din F136) -
atinge fluxuri LIVE; se face dupa ce registrul manual e stabil. F136 nr_iesire ramane input manual
pana atunci (asa cum e documentat in decizia F136 17.07).
LIMITA: v1 nu leaga automat documentele existente; contabilul le inregistreaza cand vrea un numar.

### 17.07.2026 Lot 6 F147 generare contracte: mail-merge editabil, fara stocare  (core/contracte_api.py; LIVE)
DECIZIE: F147 = mail-merge. Firma isi scrie propriul text de contract cu marcaje {{...}} dintr-un
vocabular FIX (verificat la scriere), iar generarea completeaza datele partenerului (clienti) +
firmei (firma_profil) si scoate PDF. Contractul generat NU se stocheaza (doar descarcare).
TEMEI: acelasi principiu ca adeverinta pentru banca (F136) - NU promitem un flux pe care nu-l putem
tine. A autora noi continut legal de contracte = raspundere + mentenanta juridica (fiecare business
are alt contract, legea se schimba). Facem SUBSTITUTIE, nu drept. Vocabularul fix de marcaje
(MARCAJE in contracte_api) previne marcaje orfane la o litera gresita - acelasi tipar anti-orfan ca
tip_raport F145 / directie F146. PDF pe tiparul adeverinta.py (DS cap.7 reportlab).
ALTERNATIVA RESPINSA: sabloane predefinite de noi (contracte-tip gata scrise) - comod pentru user,
dar ne-am asuma autorarea si mentenanta juridica; un sablon invechit tacit dupa o schimbare de lege
ar induce in eroare. Contrar lectiei F136.
ALTERNATIVA RESPINSA: stocarea contractelor generate + auto-inregistrare in Registratura (F146) -
inca un tabel + hook; v1 ramane stateless (descarcare). Urma = optional prin F146 manual. Se poate
adauga daca apare nevoia reala.
LIMITA: partenerul se ia din clienti (sau campuri manuale la generare); furnizorii nu sunt inca in
selector. v1 scoate PDF final (nu doc editabil) - editarea inainte de semnare o face utilizatorul in
sablon sau dupa, in alt program.

### 18.07.2026 Lot 7 F161 vreau contabil: BLOCAT pe determinarea gratuit-vs-cabinet (user vs tenant)  (STOP, neconstruit)
DECIZIE: F161 (conversia contului gratuit sub un cabinet) NU se construieste inca. Blocant descoperit
la sursa: determinarea "cont gratuit vs client gestionat de cabinet" e pe USER, nu pe TENANT.
TEMEI (verificat 18.07): _eGratuit() = rol client && !u.firm (portal.js:18); session.firm =
user.accounting_firm_id (auth_api:72), care e NULL pentru ORICE client. Deci un client gratuit si un
client-portal de cabinet au amandoi firm=NULL -> _eGratuit=true pentru amandoi. Conversia F161
schimba tenant.accounting_firm_id (nivel tenant), dar gate-ul UI e pe user -> dupa conversie userul
ramane rol client cu accounting_firm_id NULL -> _eGratuit ramane true -> firma convertita ar vedea in
continuare UI-ul gratuit, nu portalul gestionat. "Doar UPDATE accounting_firm_id" nu tranzitioneaza
utilizatorul. (Efect secundar: pare un bug latent - un client-portal de cabinet, daca exista, ar fi
clasificat gratuit.)
CE CERE F161 DE FAPT: determinarea sa devina la nivel de TENANT (firma e gestionata daca
tenant.accounting_firm_id e setat) - expus in context/sesiune (ex. tenant_are_cabinet) si folosit de
_eGratuit. Schimbare de temelie a clasificarii gratuit/client (atinge comportament gratuit LIVE +
repara bug latent), nu simplul wiring presupus de brief pentru Lot 7.
ALTERNATIVA RESPINSA: construirea fluxului cabinet (cod invitatie + cerere + acceptare + UPDATE) fara
fixul de determinare - ar livra o conversie care nu schimba experienta utilizatorului = fundatura.
INTREBARE DESCHISA pentru Costin: (a) fac acum fixul de determinare tenant-based (deblocheaza F161
curat + repara latentul), apoi F161 pe deasupra; SAU (b) F161 ramane amanat pana la o sesiune dedicata
determinarii. Decizia inainte de cod - garda schema + garda "umbla peste ce functioneaza" (gratuit LIVE).
LIMITA: nu s-a verificat daca exista deja clienti-portal de cabinet in productie (care ar suferi de
misclasificarea latenta); de verificat inainte de a atinge _eGratuit.

---

## F161 "Vreau contabil" — model de alocare (DESCHIS, apoi REDUS, 18.07.2026)

Context: contul gratuit e o firma care are DEJA un contabil (altfel n-ar putea depune
bilant). "Vreau contabil iConta" a fost initial inteles ca migrare/conversie — gresit.

Clarificare Costin (in ordine):
1. iConta NU aloca clientul catre cabinet. Temei: platforma nu e agentie de matchmaking;
   alocarea l-ar pune pe Costin arbitru intre cabinete (de ce X si nu Y, ce raspundere pe
   alegere proasta). Pozitie de evitat.
2. Nu exista "invitatie" nici intr-un sens, nici in altul:
   - cabinet vrea iConta -> se inregistreaza self-service (F108, LIVE);
   - cabinet are client -> clientul are portal (LIVE).
3. F161 ca "buton de conversie / vreau contabil" cu flux de acceptare NU exista ca atare.

CE RAMANE (tehnic, nu model de business): cand un cabinet adauga o firma cu un CUI care
exista deja ca tenant gratuit, tenantul existent se LEAGA de cabinet (datele raman) sau
se creeaza tenant nou gol (datele se pierd)? = preluare tenant. De verificat la sursa
(tenant_provisioning + ruta adaugare firma) inainte de a declara ceva de construit.

BLOCAJ SECUNDAR REZOLVAT: determinarea gratuit-vs-cabinet era pe user, conversia pe tenant.
Reparat 18.07 (commit cb3891f, Tema A): determinare acum tenant-based (_eGratuit =
rol client && !tenant_are_cabinet). Dovada prod: 0 useri rol=client -> 0 reclasificari.
Test ROLLBACK ambele directii. Tema B (schema noua tenant_requests) NU se construieste.

---

## Contul gratuit = varf de lance comercial contra SmartBill (18.07.2026)

Pozitionare (Costin): SmartBill a crescut fiindca SAGA emitea facturi din ecranele
CONTABILULUI — firma nu-si putea emite singura o factura fara sa treaca prin contabil,
printr-un program facut pentru contabili. SmartBill a dat firmei un ecran de emitere
simplu, facut pentru EA, separat de contabilitate.

Contul gratuit iConta (F153) e aceeasi miscare: firma emite singura, comod, gratis;
contabilul ei ramane pe SAGA cu bilantul. iConta NU concureaza SAGA pe contabilitate —
o ocoleste pe partea slaba (emitere catre firma). Odata ce firma emite in iConta,
piciorul e in usa pentru restul.

CONSECINTA pe prioritati (F154-F160):
- Ce face emiterea MAI USOARA decat SmartBill = prioritate reala (terenul de lupta).
- e-Factura SPV in cont gratuit (F160) NU e optional: obligatoriu legal B2B, concurenta
  o are. Firma care emite B2B fara SPV = oferta incompleta. F160 e parte din carlig.
- F161 "vreau contabil" ca buton de conversie = NU exista. Valoarea contului gratuit e
  emiterea in sine, deja LIVE.

CARLIG SUPLIMENTAR (Costin): firmele au si alte nevoi pe care le fac singure, fara
contabil — de identificat si adaugat la contul gratuit. Filtru: o functie apartine
contului gratuit DOAR daca firma o face singura, azi, fara contabil, SI se poate livra
fara a atinge partida dubla. Proforma trece; "vreau profitul" nu (cere contabilitate =
teren SAGA, nu se concureaza acolo).

---

## Cont gratuit vs concurenta — paritate, lipsuri, "gratuit" conditionat (18.07.2026)

Cercetare la sursa (SmartBill, Oblio, FGO, Factureanu), filtrata pe "firma face singura".

PARITATE ATINSA (LIVE in cont gratuit, marcate retroactiv de Lot 7): facturi (F153),
proforme+avize (F154), chitante (F157), model factura (F158), link plata (F159),
WooCommerce (F156), recurente (F155). Miezul documentar = complet.

LIPSURI fata de oferta gratuita a concurentei:
1. e-Factura SPV (F160) — GOL DE PARITATE, singurul care conteaza. Universal la concurenta.
   Obligatoriu legal B2B din 2025. BLOCAT pe OAuth ANAF (acelasi email ca F121/F126).
2. Export catre programul contabilului (SAGA/WinMentor/Ciel) — ABSENT din registru.
   Oblio il are. Nu e functie de firma, e PUNTEA care face pozitionarea posibila: firma
   emite in iConta, contabilul ramane pe SAGA. Fara export, firma nu poate folosi iConta
   fara sa-si enerveze contabilul. Posibil cel mai important gol strategic. De verificat
   la sursa daca exista vreun export in cod.
3. e-Factura primita -> NIR automat — ABSENT pentru cont gratuit. Oblio il are.
   Diferentiator, nu paritate.

"GRATUIT" CONDITIONAT IN PIATA (fiecare are alt asterisc):
- SmartBill: 30 zile trial (12 luni doar firme in primul an). Apoi platit. Costuri ascunse
  peste prag (credite >5E, upgrade fortat). = momeala de intrare.
- Oblio: gratuit pe viata DOAR sub 3 documente/luna. Peste -> 29E/an. Simbolic.
- FGO: gratuit NELIMITAT ca numar, DAR e-Factura se exporta MANUAL in XML si o incarci
  tu in SPV. Fara trimitere directa in gratuit. = asteriscul lor.
- Factureanu: singurul gratuit pe viata REAL, nelimitat, CU SPV direct, fara card. Etalon.

GOL DE PIATA: nimeni nu da simultan gratuit-nelimitat + SPV-direct + fara card, in afara
de Factureanu. POZITIONARE POSIBILA (daca se rezolva SPV direct): "gratuit nelimitat, SPV
direct, SI legat de un cabinet real cand vrei contabilitate completa". Factureanu e doar
facturare; iConta are contabilitatea in spate = diferentiator ne-egalabil de un facturator pur.

REVERS CINSTIT: fara SPV direct, iConta e SUB FGO (care macar e nelimitat). SPV nu e un gol
de paritate printre altele — e PRAGUL sub care oferta nu exista in piata. Ridica prioritatea
confirmarii OAuth ANAF.

---

## Retentie cont gratuit inactiv — 1 an (18.07.2026)

DECIS (Costin): un cont gratuit inactiv 12 luni se sterge.

Doua feluri de "cont gratuit mort", tratate diferit:
1. Mort prin MIGRARE — firma a ajuns la un cabinet iConta. Contul gratuit e un dublu
   inutil cu acelasi CUI ca firma reala din cabinet. Datele gratuite NU se transfera
   (contul gratuit e unealta de emitere, nu sursa de adevar contabil - facturile reale
   sunt inregistrate de contabil, pastrate legal la el 5-10 ani). "Creeaza tenant nou gol"
   la migrare = CORECT, nu bug. RAMAS de verificat la sursa: ce se intampla cu contul
   gratuit vechi dupa migrare - ramane activ (firma poate emite din DOUA locuri cu acelasi
   CUI)? Se inchide? De inchis la migrare = igiena.
2. Mort prin ABANDON — firma s-a inregistrat, a emis cateva facturi, n-a mai intrat.
   Nu s-a dus la niciun cabinet. -> tinta regulii de 12 luni.

TEMEI GDPR (verificat la sursa 18.07.2026):
- GDPR nu prescrie termen fix (Art. 5 storage limitation): datele nu se pastreaza mai
  mult decat e necesar scopului. Termenul il decide operatorul, DAR trebuie justificat
  si documentat. -> aceasta intrare e documentatia.
- "Poate imi trebuie mai tarziu" e INTERZIS explicit ca temei (data minimisation).
  Deci "il tinem in caz ca revine clientul" NU e o baza legala.
- Exceptia de retentie contabila (5-10 ani, evidente fiscale) NU se aplica contului
  gratuit: documentul contabil oficial e la contabil, nu ciornele din contul gratuit.
  Pentru cont gratuit exista obligatia de STERGERE cand scopul (emitere activa) a incetat,
  nu de pastrare.

JUSTIFICAREA cifrei (1 an): scopul contului gratuit e emiterea activa. 12 luni fara login
= scop incetat. 1 an acopera si firmele sezoniere (activitate pe val) fara sa piarda
clientul care revine, dar nu tine date "in caz ca". Aliniat cu practica pietei (Glasgow
Online: 1 an inactivitate -> stergere).

CERINTE la implementare (GDPR, obligatorii cand se construieste):
- Stergerea trebuie sa acopere SI backupurile. Contul sters ramane in dumpurile zilnice
  max 7 zile (retentia backup existenta) - rezonabil, dar de stiut/documentat.
- Preaviz inainte de stergere (buna practica, nu obligatoriu legal): email de avertisment
  + fereastra de restaurare, ca sa nu para stergere abuziva.

STARE: decizie luata, NU se construieste acum (0 conturi gratuite reale). Se implementeaza
cand exista conturi + cand se construieste fluxul de preluare (punctul 1).

### 18.07.2026 F171 export SAGA: gol strategic LIVRAT (facturi emise -> XML SAGA), SAGA-only  (core/export_saga.py; LIVE)
DECIZIE: exportul catre programul contabilului (gol strategic notat 18.07 in DE_FACUT + DECIZII
"cont gratuit paritate/lipsuri") e LIVRAT pentru SAGA. Firma emite in iConta, exporta XML, contabilul
importa in SAGA (Diverse -> Import date din fisiere generate). Puntea care face posibila pozitionarea
"firma emite in iConta, contabilul ramane pe SAGA".
TEMEI (verificat la sursa 18.07): structura XML si cele 3 reguli SAGA de la manual.sagasoft.ro/sagac/
topic-76 + forum oficial. (1) directia se decide prin CIF (Furnizor=firma-client -> SAGA claseaza
iesire, nu se marcheaza directia); (2) nume fisier obligatoriu F_<cif>_<nr>_<data>.xml; (3) data
zz.ll.aaaa, moneda RON, sume/cota 2 zecimale punct. Rotunjire fiscala Decimal+ROUND_HALF_UP (reutilizat
_q + totaluri_din_linii din facturi_api). Read-only: ruta noua citeste factura, produce XML; fara
schema, fara UPDATE, fara atingere pe emitere/facturi_api.
ALTERNATIVA RESPINSA: WinMentor/Ciel acum - SAGA acopera majoritatea pietei; codul e structurat pe
format (un generator per format) ca sa primeasca altele ulterior, dar se livreaza doar SAGA.
LIMITA DECLARATA:
  - SAGA-only. WinMentor/Ciel = later (alt generator, alta structura XML).
  - Encoding UTF-8 in XML - SAGA modern il accepta; de confirmat vizual la primul import real ca
    diacriticele intra corect (SAGA vechi cerea Windows-1250). Daca pica, se schimba encoding-ul.
  - Camp fara sursa in iConta lasat GOL, nu inventat: FurnizorCapital (nu exista in firma_profil),
    ClientNrRegCom/Banca/IBAN (clienti n-are aceste campuri), CodArticolFurnizor/Client (facturile
    n-au cod de articol -> SAGA pune linia pe "Nedefinit", documentat acceptabil).
  - Doar facturi EMISE tip 'factura' (inclusiv storno, sume negative). Proforme/avize excluse (SAGA
    importa facturi).

---

## Semafor fiscal — fact-aware controlat (B) + motiv pe orice culoare (18.07.2026)

Context: semaforul (control_fiscal_api) acopera 7/9. D205 si D301 lipsesc fiindca NU
se datoreaza pe vector, ci pe FAPT: D205 doar la dividende distribuite (rulaj 457);
D301 doar in lunile cu operatiuni IC. Semaforul, vector-driven, nu vede faptul.

Doua motoare SEPARATE azi:
- control_fiscal_api: "ce esti OBLIGAT sa depui si ai depus?" Vector-driven.
- control_incrucisat: "ce ai declarat corespunde cu evidenta?" Fact-driven, note validata.
Culori cu sensuri diferite: semafor rosu = "depune"; control rosu = "cifra gresita".

DECIS: B (fact-aware controlat). Semaforul cheama o functie mica ce CITESTE faptul
(457, operatiuni IC) si decide verde/rosu. Motoarele raman SEPARATE, legate printr-o
punte (o functie), nu fuzionate. 9/9 real.

C (fuziune) RESPINS: topeste "obligatie" si "adevar" intr-o culoare ambigua (rosu = ori
"n-ai depus" ori "cifre gresite", contabilul nu mai stie ce sa faca din culoare) =
distructie de semnal la nivel de PRODUS. Plus motor mare greu de intretinut (regula
"nu construi paralel"). Riscul "firma noua vede semafor mut" = respins de Costin: firma
de cont gratuit nu face contabilitate (F153 "fara panou fiscal"); firma de cabinet are
contabil care valideaza. B da acelasi beneficiu (semafor constient de fapte) FARA costul.

CERINTA (Costin): semaforul NU e doar culoare. Fiecare verdict poarta MOTIVUL, pe ORICE
culoare, inclusiv verde. Temei: verdele tacit e cel mai slab semnal de audit (ambiguu
intre "verificat curat" si "neverificat"). "D300 depusa 24.04 la termen, coerenta 4427"
transmite ca sistemul a muncit. Increderea vine din a arata CUM s-a ajuns la culoare.
Aliniat control_incrucisat: "fiecare constatare isi declara temeiul si limita".

Legatura cu #2 (punte factura->stoc): ambele rezolva aceeasi tensiune (surse de fapt
contabil deconectate). Puntea din B se construieste CU #2 in minte - una singura
refolosita, nu doua paralele.

### 18.07.2026 Semafor B LIVRAT: D205/D301 fact-aware + motiv pe orice culoare  (core/control_fiscal_api.py, control_incrucisat.py; LIVE)
Implementarea deciziei B din commit 898482a (aceeasi zi). Semaforul acopera acum 9/9.
PUNTEA (motoare separate, nu fuziune): control_incrucisat capata functii generale de citit faptul din
note validate - rulaje_interval (rulaj pe cont, interval; rulaje_luna deleaga la ea acum, o singura
sursa - regula "nu construi paralel"), dividende_distribuite (rulaj 457 pe an, ca d205.py) si
d301_luni_operatiuni (tabelul d301_operatiuni pe luna). control_fiscal_api.declaratii_fapt le CHEAMA,
nu le absoarbe. Faptul face #2 (punte factura->stoc) refolosibil: rulaje_interval e general.
D205: dividende distribuite = rulaj cont 457 in an -> datorata; fara 457 dar cu note -> nu se
datoreaza; fara note -> gri (nu pot verifica). D301: doar neplatitori TVA, per luna cu operatiuni IC
(d301_operatiuni); platitor TVA -> nu se datoreaza.
MOTIV pe orice culoare (cerinta Costin): fiecare linie din evalueaza_firma poarta `motiv` textual cu
temei - verde ("D300 depusa 24.04, la termen"), rosu ("nedepusa, termen depasit"), gri (cauza),
neaplicabil ("nu se datoreaza - niciun rulaj 457"). UI: control.js + firme.js afiseaza motivul ca
temei sub fiecare rand (pattern cf-incr-temei, aliniat control_incrucisat, direcvionat de brief).
Verificat: 0 linii fara motiv pe tenant_002; D205 detectat pe rulaj 457 real. control_incrucisat 23
teste intacte (delegarea rulaje_luna e behavior-preserving).
LIMITA: D205 evaluat pe anul precedent (an-1); D301 pe orizontul scurt (an + dec an-1). Faptul D301 =
ce s-a INREGISTRAT in d301_operatiuni (daca firma n-a inregistrat operatiunile IC, semaforul nu le
vede - limita oricarui motor fact-driven, declarata in motiv: "nicio operatiune IC inregistrata").

---

## Punte factura -> stoc: poarta obligatorie "pleaca marfa acum?" (18.07.2026)

Problema (verificata la sursa, neschimbata din 17.07): vanzarea si descarcarea gestiunii
sunt acte deconectate. factura_linii fara articol_id, miscari_stoc fara factura_id,
/stocuri/iesire ruta manuala separata. Rezultat: dubla introducere (omul factureaza SI
descarca separat) + profit-pe-produs imposibil (nicio cheie de join venit<->cost).

Aviz verificat (18.07): clone structural al facturii (aceeasi tabela `facturi` tip='aviz',
aceleasi linii factura_linii, nu se contabilizeaza, NU atinge stocul). Distinctia
"marfa cu factura vs cu aviz" NU exista in cod, e doar eticheta UI. Deci puntea NU e
"factura->stoc SAU aviz->stoc" ca structuri diferite - ambele impart factura_linii.
O singura schimbare structurala serveste amandoua.

INTREBAREA REALA nu era "ce document descarca" ci "CAND pleaca marfa" - fiindca factura
poate fi avans / livrare ulterioara / serviciu / custodie (clientul plateste dar marfa
nu pleaca). Factura NU e momentul descarcarii.

DECIS (Costin): POARTA OBLIGATORIE la emitere. Inainte de a emite factura, utilizatorul
raspunde OBLIGATORIU: "Pleaca marfa acum? DA / NU". Nu poate emite fara raspuns.
- DA -> factura descarca gestiunea: se genereaza iesirea din stoc (miscari_stoc legat
  de factura prin factura_id), DOAR pe liniile care au articol de stoc. Liniile fara
  articol (servicii) se ignora - poarta e una singura, se aplica doar unde are sens.
- NU -> factura pur fiscala, stocul neatins (avans, livrare ulterioara, serviciu).

De ce poarta obligatorie si nu bifa optionala: bifa se poate uita (stoc gresit tacit).
Raspunsul cerut inainte de emitere NU se poate uita. "Nu mai are cum sa uite" (Costin).
Un singur document (factura), nu obliga emiterea separata de aviz pentru fiecare vanzare.

Avizul RAMANE pentru livrarea DECUPLATA de factura: cazul "am facturat luna trecuta cu
NU, marfa pleaca azi" -> avizul de livrare descarca ce factura-cu-NU a lasat nedescarcat.
Deci avizul nu se elimina; acopera livrarea ulterioara. Pentru cazul comun (facturez si
livrez odata), poarta DA rezolva totul intr-un act.

STRUCTURA (schema noua - de aceea aceasta decizie se scrie inainte de cod):
- articol_id pe factura_linii (cheia care lipseste; serveste si factura si aviz, aceeasi
  tabela). Optional pe linie: liniile de serviciu raman fara.
- factura_id pe miscari_stoc (cheia de intoarcere, pentru profit-pe-produs).
- descarcarea REFOLOSESTE iesire() existent (motorul CV, /stocuri/iesire main.py:5050) -
  nu se construieste motor paralel. Puntea alimenteaza iesire(), nu il inlocuieste.
- rulaje/join pentru profit-pe-produs refoloseste rulaje_interval (extras la semafor B,
  c377746) - o punte, nu doua.

LIMITE:
- Global-valoric (GV): profit-pe-produs ramane GRI permanent (cost pe articol nu exista
  prin constructie). Poarta se aplica doar la CV. La GV, descarcarea ramane global-valorica
  lunara existenta (F088).
- Facturi cu marfa + servicii mixte: DA descarca doar liniile cu articol_id, restul ignora.

ATINGE COD LIVE (emiterea): de aceea e schema + poarta, nu "da-i drumul". Se construieste
cu grija maxima: emiterea existenta NU se strica pentru cine emite fara marfa (NU = flux
actual neatins). Poarta e aditiva, nu inlocuieste fluxul de emitere.

### 18.07.2026 Punte factura->stoc LIVRATA (F172) + profit-pe-produs LIVE la CV (F144)  (core/stocuri_cv_api.py, facturi_api.py; LIVE)
Implementarea deciziei "Punte factura -> stoc" (18.07). Poarta obligatorie "Pleaca marfa acum? DA/NU"
la emitere (caseta-poarta, DS cap.5 v2.14). Schema aditiva: articol_id pe factura_linii, factura_id pe
miscari_stoc (NULL-able, FK ON DELETE SET NULL). Descarcarea REFOLOSESTE iesire() (param aditivi
factura_id + commit=False pt atomicitate; /stocuri/iesire neatins). Puntea rulaje/join refoloseste ce
exista - o punte, nu doua.
PORTI RESPECTATE: (1) emiterea FARA marfa (NU / servicii / gratuit) = flux IDENTIC cu azi (poarta
aditiva, aprinsa doar cand o linie are articol_id la firma cabinet CV); (2) DS poarta noua (caseta-poarta
per-factura) = stabilita cu Costin (pas de confirmare) + scrisa in DESIGN_SYSTEM v2.14 + verificator
POARTA_INLINE; (3) descarcare = nota ciorna existenta (iesire), fara ambiguitate fiscala (cont din articol).
CONT GRATUIT EXCLUS explicit (nu tine gestiune; adevarul e la contabil pe SAGA) - accounting_firm_id NULL
-> articol_id anulat, emite ca azi. Aliniat determinarea tenant-based (Tema A).
F144 profit-pe-produs: decizia deschisa (17.07) INCHISA pentru CV - join venit(factura_linii.articol_id)
<-> cost(miscari_stoc.factura_id la CMP). Verificat: Widget X venit 100 - cost 60 = profit 40.
LIMITA (declarata): GV ramane fara profit-pe-produs (cost pe articol inexistent prin constructie);
descarcarea GV ramane global-valorica lunara. Stoc insuficient la descarcare -> raportat, nu rupe factura.

### 18.07.2026 D106 RESPINS - in afara publicului iConta (doar firme de stat)  (nu se construieste; DE_FACUT inventar)
DECIZIE: D106 nu se construieste. In afara publicului tinta iConta.
TEMEI (verificat la sursa): OPANAF 1292/20.05.2014 + instructiuni ANAF (instr_106_2014.pdf) - D106
"Declaratie informativa privind dividendele cuvenite actionarilor" se depune DOAR de societatile
nationale, companiile nationale si societatile cu capital de stat (stat actionar unic/majoritar/de
control), potrivit OG 64/2001. Clientii iConta = cabinete cu firme PRIVATE (SRL/PFA/micro) - D106 nu
li se aplica NICIODATA. Zero utilizatori. (Denumire + reglementare confirmate si pe static.anaf.ro/
static/10/Anaf/Declaratii_R/106.html; validatorul exista oficial - versiuni.xml, D106Validator.jar
J1.0.1 - dar nu conteaza, nu se construieste.)
ALTERNATIVA RESPINSA: "e cea mai frecventa declaratie lipsa, orice SRL care distribuie profit"
(inventar DE_FACUT 17.07) - EROARE de inventar. Frecventa presupusa era pe dividende in general, dar
dividendele firmelor PRIVATE sunt acoperite deja de D205 (impozit retinut la sursa, LIVE). D106 e
PARALELA pentru firme de stat, NU suprapunere redundanta cu D205 - alt public, alt obiect.
LIMITA: daca iConta capata vreodata un client firma de stat (improbabil pentru cabinete private), se
reia. Pana atunci zero utilizatori; fiecare formular construit = abonament permanent de mentenanta.
CONSECINTA REGISTRU: nivelul 2 "merita construite" scade de la 3 la 2 (D230, D307). D106 nu figura in
FUNCTIONALITATI.csv (nu era functionalitate planificata) - nimic de flipat acolo; corectat doar
inventarul din DE_FACUT.md.

### 18.07.2026 D230 RESPINS + D307 AMANAT (impreuna cu D106 - inventar nivel 2 inchis)  (FUNCTIONALITATI.csv F173-F175)
Verificate la sursa cele 3 declaratii ramase "nivel 2" din inventarul 17.07; NICIUNA nu se
construieste acum. (D106 = intrare proprie mai sus, 929735b: firme de stat, RESPINS.)
D230 RESPINS: "declaratie de redirectionare a 3,5% din impozitul pe venit catre o entitate nonprofit"
e declaratie PERSONALA a SALARIATULUI (persoana fizica), nu a firmei. Salariatul o depune singur;
PFA o rezolva prin D212 (LIVE). Cabinetul nu depune declaratiile personale ale angajatilor clientilor
sai - in afara modelului de produs. Temei: CF art. 123^1 (redirectionare, optiunea contribuabilului PF).
D307 AMANAT (prioritate joasa): "ajustarea TVA in cazul anularii inregistrarii in scopuri de TVA"
(transfer de active, leasing, anularea codului de TVA). SE APLICA firmelor private din portofoliu, DAR
e o EXCEPTIE RARA - o data in viata firmei sau niciodata. Se construieste cand un cabinet real are
efectiv cazul, NU preventiv (fiecare formular construit = abonament permanent de mentenanta; regula
inventarului: nu se cara declaratii nedecise/nefolosite).
CONSECINTA: inventarul "nivel 2 - merita construite" (3 pozitii pe 17.07) e INCHIS: 0 de construit acum
(D106/D230 in afara publicului, D307 la cerere reala). Adaugate in FUNCTIONALITATI.csv F173/F174/F175.
LIMITA: D307 se reia la primul caz real (semnal din suport/cabinet). D106/D230 doar daca se schimba
publicul (firme de stat / depunere de declaratii personale) - improbabil.

### 18.07.2026 Harta de prioritati - ce ramane si de ce nu se face preventiv  (registru viu, orientare)
Miezul e COMPLET: contabilitate, salarizare, 9/9 declaratii LIVE + validate DUK, stoc CV, facturare,
control fiscal (semafor 9/9 fact-aware), export SAGA, punte factura->stoc. Ce ramane = EXPANSIUNE la
cerere, nu goluri de miez.
URGENT (se poate face ACUM): backup OFF-SITE (F170) - local e LIVE + restaurare confirmata, dar pe
acelasi disc ca baza; nu supravietuieste mortii discului. Hetzner Storage Box.
BLOCAT PE ANAF (se deblocheaza la confirmarea OAuth): clusterul SPV - F121 (e-Transport prin API),
F126 (e-Factura SPV), F160 (e-Factura in cont gratuit = PRAGUL pozitionarii contra SmartBill/FGO,
sub el oferta gratuita nu exista in piata). Nu se pot testa pana nu vine confirmarea inrolarii.
LA SEMNAL (nu preventiv - fiecare = abonament de mentenanta): integrari (PSD2 F130, plati reale F123,
borderouri curieri/card F132); paritate concurenta (tichete de masa F133, coduri COR F137, centre de
cost F143, cloud extern F148); F161 (la primul client gratuit care CERE sa migreze sub cabinet);
D307/F175 (la primul caz real de anulare cod TVA). Se construiesc cand un cabinet real are cazul.
CERE OM (nu SSH): SAGA import real (confirmare encoding + clasificare iesire), audit vizual ~20 ecrane
ramase, pilot fiscal cu Daniela [D], teste telefon [T].
TEMEI: "toate tipurile" nu e o valoare - fiecare formular/integrare construit nefolosit e datorie de
mentenanta (OPANAF/API se schimba anual), pentru un singur om. Expansiunea urmeaza cererea reala, nu o
anticipeaza. Blocantul real unic care conteaza comercial = OAuth ANAF (clusterul SPV + gratuit).

### 18.07.2026 Igiena preluare tenant: SEMNAL la coliziune CUI, nu suspendare automata  (core/tenant_provisioning.py coliziune_gratuit_v1; FUNCTIONALITATI.csv:88 F092)
DECIZIE (raspuns la STOP Tema 3, Costin a ales optiunea A): cand un cabinet adauga o firma cu CUI-ul
unui cont gratuit VECHI inca activ, la creare se SEMNALEAZA cabinetului ca acel cont gratuit poate
inca emite din alt loc cu acelasi CUI (risc de emitere dubla / numerotare divergenta). NU se suspenda
automat contul gratuit. Semnalat pe ambele cai de preluare: tenant_creeaza (mesaj msg-avert in firme.js)
si migrare_importa (camp coliziune_gratuit in raportul de import).
TEMEI (verificat la sursa, grep 18.07): provision_tenant valida doar cifra de control CUI, nu atingea
tenantul gratuit cu acelasi CUI; nici tenant_creeaza (main.py:1016) nici migrare_importa (main.py:1229)
nu-l suspendau -> contul gratuit ramanea activ=true, logabil, emitent. Poarta de enforcement EXISTA deja
(auth_api.py:335 refuza selectarea unui tenant gratuit daca nu e activ=true) si mecanismul de inchidere
EXISTA deja (/admin/conturi-gratuite/{id}/suspenda, superadmin) - lipsea doar DECLANSAREA + vizibilitatea.
ALTERNATIVA RESPINSA: (B) suspendare automata la preluare + email catre detinatorul gratuit - inchide un
cont fara consimtamantul detinatorului (decizie de scop mai mare, GDPR/relatie client); (C) doar raport de
coliziune in panoul admin, fara semnal la momentul crearii - prea tarziu, cabinetul nu afla la actiune.
A castiga pentru ca inchiderea unui cont = decizie umana, dar semnalul trebuie sa apara EXACT cand se
creeaza dublura, nu ascuns intr-un raport.
LIMITA: semnalul e informativ - nu impiedica emiterea din contul gratuit pana cand un superadmin il
suspenda manual. Daca in practica coliziunile devin frecvente si suspendarea manuala nu tine pasul, se
reevalueaza optiunea B (suspendare automata cu notificare). Match pe cifrele CUI (regexp_replace \D) -
prinde prefix RO; nu s-a testat pe CUI cu spatii/puncte interne (nomenclatorul ANAF nu le foloseste).

### 18.07.2026 Backup off-site pe Hetzner Storage Box (rsync-over-SSH, fail-safe)  (config/iconta-backup.sh v2; FUNCTIONALITATI.csv F170 LIVE)
DECIZIE (raspuns la STOP Tema 1, Storage Box provizionat de Costin): backup-ul off-site se face pe
Hetzner Storage Box prin rsync-over-SSH cu cheie dedicata (port 23), retentie off-site 30 zile (>7 local),
fail-safe (esecul off-site NU pica backup-ul local), confirmare remote + email Brevo la 2 esecuri consecutive.
TEMEI: /var/backups sta pe ACELASI disc Hetzner ca baza -> apara de stergere accidentala, NU de moartea
discului. Sunt date fiscale ale unor firme reale. Copia off-site e conditia de supravietuire a discului.
DECIZII TEHNICE (cu temei, ca sa nu se reinventeze):
- CHEIE DEDICATA a userului postgres (cel care ruleaza backup-ul), nu parola, nu cheia de laptop
  "iconta-hetzner". Cheia privata de laptop nu se copiaza pe server; s-a generat una noua pe server
  (/var/lib/postgresql/.ssh/iconta-storagebox) si i s-a instalat publica in Storage Box. Parola one-time
  a fost folosita O SINGURA DATA pentru install-ssh-key; accesul e acum doar pe cheie.
- EMAIL prin curl DIRECT la endpoint-ul Brevo (nu import core/observare.py): userul postgres nu poate
  accesa fiabil venv-ul/codul app din /home/costin; curl la acelasi https://api.brevo.com/v3/smtp/email
  cu acelasi sender = ACELASI canal, fara dependenta fragila cross-user. BREVO_API_KEY ajunge in mediu
  prin systemd EnvironmentFile (citit de systemd ca root INAINTE de drop la postgres) - postgres nu
  citeste direct fisierul din home-ul lui Costin.
- RETENTIE off-site pe DATA din NUMELE fisierului (regex pe iconta_v2_YYYYMMDD_), nu pe mtime remote:
  shell-ul limitat al Storage Box nu expune find/mtime fiabil; numele e sursa determinista.
- FAIL-SAFE structural: backup-ul local ruleaza PRIMUL si sub set -e (esecul lui trebuie sa fie zgomotos);
  off-site ruleaza intr-o functie apelata sub `if` (care suspenda set -e) -> orice esec off-site se
  logheaza + numara, dar iese cu succes, ca localul sa nu fie afectat.
ALTERNATIVA RESPINSA: (a) rsync --delete oglindire director local->remote - ar fi limitat off-site la 7
zile ca localul, pierzand marja de 30; (b) stergerea vreodata a backup-ului local - LOCAL = SACRU,
niciodata sters de logica off-site; (c) S3/alt cloud - Storage Box e destul pentru un singur disc de aparat
si e deja platit; multi-cloud geo-redundant = scop mai mare, la nevoie reala.
LIMITA: Storage Box = single-provider (nu geo-redundanta intre furnizori). Daca datele cresc mult,
retentia de 30z off-site trebuie recalibrata la spatiul Storage Box.
INCHISA 18.07 (aceeasi zi): restaurarea DIN off-site testata cap-coada - descarcat ultimul dump prin
sftp -> pg_restore intr-o baza de test iconta_restore_offsite_test -> scheme identice cu iconta_v2
(public+tenant_001+tenant_002), public.tenants 2=2, tenant_002.facturi=5 -> dropdb. Baza vie neatinsa.
Deci off-site-ul nu doar se urca, ci se si RESTAUREAZA.

### 18.07.2026 Flux OAuth SPV/ANAF VALIDAT end-to-end pe productie  (core/spv_conector.py; ARHITECTURA_SPV.md)
DECIZIE: conectorul OAuth SPV este validat cap-coada pe PRODUCTIE (18.07) - authorize real la
logincert.anaf.ro cu certificatul ADMIN, ANAF a acceptat client_id + redirect_uri (/anaf/oauth/callback,
NU /efactura), callback-ul a schimbat code->token, tokenul a fost salvat criptat Fernet (access 90z /
refresh 365z) si e decriptabil (ia_token_activ). Deci: OAuth merge, criptarea merge, decriptarea merge,
rotatia e implementata. Tokenul de test (id=20, accounting_firm_id=1, certificatul personal al lui Costin)
a fost STERS dupa validare (nu e conexiune reala de cabinet).
TEMEI: portalul de inrolare ANAF era inaccesibil (sesiune respinsa) -> nu se putea citi redirect_uri
inregistrat. S-a testat invers: URL de authorize cu valoarea din cod, ANAF a confirmat prin acceptare.
Istoricul contrazicea Bitwarden (care avea /efactura, ruta VECHE esuata cu invalid_client); productia a
dat verdictul: /anaf/oauth/callback e corect. redirect_uri NU se aliniaza pe /efactura.
MODEL (reconfirma DECIZIA 1 din ARHITECTURA_SPV): Costin = ADMINISTRATOR de platforma, NU cabinet. NU se
conecteaza la SPV in numele nimanui. Conexiunea reala se face PER CABINET din UI (Setari -> Conectare SPV),
cu accounting_firm_id = cabinetul LOGAT (nu hardcodat), fiecare cabinet cu certificatul LUI pe firmele LUI.
ALTERNATIVA RESPINSA: a pastra tokenul de test in DB "ca dovada" - ar fi legat certificatul personal al
adminului de firma 1 si ar fi creat confuzie (token de admin != token de cabinet). Dovada traieste in
DECIZII+ISTORIC, nu intr-un rand fals in spv_token.
LIMITA / RAMAS PENTRU PRODUCTIE REALA (in ordine): (a) cron refresh la 90 zile - golul #1 (spv_refresh.py
+ timer; fara el token-urile expira tacit si cabinetul reautorizeaza cu stickul); (b) popularea
spv_cui_acoperit la conectare (sondaj empiric per-CIF - necunoscuta "ce CUI-uri acopera tokenul", nerezolvata
inca); (c) features F126/F160 peste conector (apeluri prin apel_anaf). Necunoscuta CUI se lamureste la
prima conexiune reala de cabinet (decodare JWT + apel TestOauth).

### 18.07.2026 (corectie) Token SPV id=21 = TOKEN DE DEZVOLTARE, se PASTREAZA  (rastoarna intrarea "token de test sters" de mai sus, commit 2216b35)
DECIZIE: tokenul SPV real obtinut cu certificatul admin (Costin) se PASTREAZA ca token de DEZVOLTARE,
pentru a construi si testa e-Factura (apel_anaf pe endpoint-uri SPV reale). accounting_firm_id=1 = mediu
de test, NU conexiune de cabinet real. Rastoarna decizia anterioara de azi (stergerea tokenului de test):
primul token (id=20) fusese deja sters cand a venit corectia; s-a re-autorizat -> token nou id=21, pastrat.
TEMEI: dezvoltarea e-Factura are nevoie de un token valid pe SPV real; certificatul admin il furnizeaza
fara sa astepte primul cabinet. Modelul de productie NU se schimba: cabinetele reale se conecteaza din UI
(Setari -> Conectare SPV), fiecare cu certificatul LOR -> propriul token, accounting_firm_id = cabinetul
LOGAT (nu hardcodat). Firma 1 + certificatul admin = doar bancul de test.
NECUNOSCUTA CUI - REZOLVATA (vezi ARHITECTURA_SPV.md): JWT-ul decodat pe token real arata ca tokenul NU
contine CUI-uri, doar roluri de serviciu (EFACTURA/ETRANSPORT). Deci spv_cui_acoperit se populeaza
OBLIGATORIU empiric (apel per-CIF: 200/403), nu din token. Serialul = claim `serial`.
ALTERNATIVA RESPINSA: sa astept primul cabinet real ca sa am token de dezvoltare - ar bloca constructia
e-Factura pe nedefinit. Tokenul admin deblocheaza dezvoltarea acum, fara sa afecteze modelul de productie.
LIMITA: tokenul id=21 traieste doar in DB, in afara ferestrei de backup 03:00 - la un restore se pierde
si se reconecteaza (2 min, e autorizare, nu date). Ramas inainte de e-Factura: (a) popularea empirica
spv_cui_acoperit, (b) cron refresh 90 zile (spv_refresh.py + timer), apoi (c) F126/F160 peste apel_anaf.

### 18.07.2026 Cron refresh token SPV (F177) - golul #1 al conectorului, fundatia pentru F126  (core/spv_refresh.py; ARHITECTURA_SPV.md sectiunea CRON REFRESH)
DECIZIE: refresh-ul automat al token-urilor SPV se face printr-un driver systemd (spv-refresh.timer,
zilnic 03:30 dupa backup), care reimprospateaza TOATE token-urile active cu access_expira sub o marja de
15 zile, refolosind spv_conector.reimprospateaza_token (rotatie: salveaza ambele valori noi).
TEMEI: access token-ul ANAF expira la 90 zile; fara refresh automat cabinetul se deconecteaza TACIT si
reautorizeaza cu stickul. Era golul #1 identificat la diagnosticul conectorului (F176). Functia de refresh
exista deja - lipsea doar driverul.
DECIZII DE DESIGN:
- MARJA 15 zile > avertismentul UI de 7 zile (MARJA_REFRESH_ZILE): cronul actioneaza INAINTE ca ecranul
  sa alarmeze, cu spatiu; "sub 15 zile", nu "la fix 90", ca sa nu prinzi exact expirarea.
- FAIL-SAFE fara dezactivare la prima eroare: fiecare token in tranzactie separata (db.get_conn commit/
  rollback); la esec rollback -> tokenul RAMANE activ, retry a doua zi. reimprospateaza_token cheama
  dezactiveaza_token pe conn, dar rollback-ul o anuleaza - INTENTIONAT: cu 15z marja (~15 incercari),
  o eroare ANAF tranzitorie nu trebuie sa forteze reconectarea cabinetului. Orice esec -> email Brevo.
- EMAIL prin core.observare (in-process Python), NU curl ca la backup off-site: aici driverul ruleaza
  ca user costin cu env-ul complet (acces la cod+venv), deci refolosim canalul canonic, nu unul paralel.
- systemd timer, NU crontab (cerinta + pattern-ul proiectului = iconta-backup.timer).
ALTERNATIVA RESPINSA: dezactivare la prima eroare (cum zicea prima varianta a arhitecturii "Esec ->
activ=false") - ar forta reconectari inutile pe erori tranzitorii ANAF (frecvente) cand exista 15z marja.
Tokenul moare doar cand refresh-ul chiar nu se mai poate reinnoi (refresh 365z expirat / invalid_grant
persistent), cu alertare zilnica intre timp. Si: crontab - deprecat in proiect.
DOVADA: test functional real pe token_id=21 (dev, certificat admin) - refresh fortat prin driver (marja
200z) -> access_expira avansat cu 90z, reimprospatat_la setat, cifertext rotit (token nou criptat),
decriptabil, serial identic; selectia normala (15z) = 0 pe tokenul proaspat. Timer activ, next 19.07 03:30.
LIMITA: reimprospateaza_token trateaza orice non-200 la fel (nu distinge invalid_grant permanent de 5xx
tranzitoriu) - rafinarea cere schimbare in _post_token, amanata pana la primul cabinet real; marja 15z
acopera tranzitoriile. Testat pe un singur token dev, nu pe mai multe cabinete simultan.

### 18.07.2026 Host e-Factura = webserviceapl.anaf.ro (NU api.anaf.ro)  (core/efactura_send.py FCTEL_BASE_TPL)
DECIZIE: baza REST pentru e-Factura (upload/stareMesaj/descarcare/listaMesajeFactura) =
https://webserviceapl.anaf.ro/{prod|test}/FCTEL/rest. O SINGURA constanta (FCTEL_BASE_TPL,
env-overridable EFACTURA_FCTEL_BASE) + helper fctel_base(mode); upload/stare/descarcare (pasul 2)
o refolosesc, NU rescriu host prin apeluri.
TEMEI: listarea oficiala ANAF (static.anaf.ro/.../url_eFactura.html) - sursa de autoritate.
ALTERNATIVA RESPINSA: https://api.anaf.ro/{prod|test}/FCTEL/rest, copiat din build-ul vechi
/opt/iconta/main.py - host ISTORIC/stale. Build-ul vechi e sursa istorica (util pt structura XML
si nume endpoint), NU autoritate pe host. Nu se copiaza magic string din /opt/iconta.
LIMITA: corect verificat pe listare; devine critic la primul upload TEST (pasul 2) - daca host-ul
s-a schimbat din nou, acolo se vede. Generatorul pur (pasul 1) nu atinge host-ul.

### 18.07.2026 Generator e-Factura XML SEND (pasul 1, F126/F160)  (core/efactura_send.py + test)
DECIZIE: generatorul XML de trimitere (UBL 2.1 / CIUS-RO) e core/efactura_send.py - PUR (fara
DB/retea in genereaza_xml), cu loader separat pe schema CURENTA. Fundatia comuna F126 (cabinet) +
F160 (gratuit). Pasul 1 din ordinea aprobata (1->5); pasul 2 = upload pe TEST = validatorul real.
TEMEI: reutilizarea structurii XML dovedite din build-ul vechi (_efx_build_xml) - reg de aur, nu
rescriu de la zero - DAR loader rescris (build vechi citea tabel `clienti` inexistent; curentul are
cumparatorul denormalizat pe facturi.tert_nume/tert_cui/tert_adresa). Rotunjire fiscala Decimal +
ROUND_HALF_UP (regula iConta), nu round().
DOVADA: 6 teste pe date minime construite manual (structura, sume, rotunjire half-up != bankers,
VAT furnizor doar daca platitor, taxare_inversa ridica NotImplementedError, host o singura constanta)
+ test functional real pe tenant_002 factura 1: net 10000 / TVA 2100 / total 12100 = exact ca in DB,
XML bine-format (ElementTree).
LIMITE v1 (de rezolvat la/dupa TEST, NU ghicite): (1) cumparatorul are doar adresa libera in schema,
CIUS cere oras (BT-52) - CityName = oras daca vine, altfel adresa libera (fallback), formularul de
factura trebuie sa capteze orasul separat inainte de send real; (2) doar factura standard cu TVA
(S/Z); taxare_inversa (AE), neplatitor TVA (O), storno/nota de credit (381) - netratate v1, se adauga
dupa confirmare pe TEST. NU exista validator e-Factura local (DUK = doar declaratii) -> validatorul
real e upload-ul TEST (pasul 2).

### 18.07.2026 Tabel urmarire trimiteri e-Factura (efactura_trimiteri) - PER-TENANT + garda idempotenta  (core/migrare_efactura_trimiteri.py; tenant_template.sql)
DECIZIE (schema stabilita de Costin, raspuns la poarta pasul 2): tabelul efactura_trimiteri traieste
PER-TENANT (in fiecare tenant_NNN), nu in public. Masina de stari: pregatit -> eroare_upload | incarcat
-> in_prelucrare -> ok | nok. Coloane pentru id-urile ANAF (index_incarcare, id_descarcare), amprente XML
(xml_sha256, xml_semnat_sha256), mediu ('test'/'prod').
TEMEI PER-TENANT: FK-ul e spre facturi(id), care e tabela per-tenant; trimiterea apartine facturii, nu
cabinetului (tokenul e per-cabinet in public.spv_token, dar factura si trimiterea ei sunt ale firmei).
GARDA CRITICA - index unic partial uq_efactura_trimiteri_viu pe (factura_id) WHERE mediu='prod' AND
stare IN ('incarcat','in_prelucrare','ok'): un SINGUR send viu per factura pe PROD. Temei: upload-ul ANAF
NU e idempotent - o dubla trimitere = dubla factura la ANAF (eroare cu consecinte fiscale reale). Pe
'test' NU blocheaza (validari repetate permise in dezvoltare).
ALTERNATIVA RESPINSA: tabel in public cu tenant_id - ar rupe coerenta cu restul (facturile sunt
per-schema) si ar cere tenant_id peste tot; guard global fara mediu - ar bloca si validarile TEST repetate.
DOVADA: migrare 2/2 scheme OK (tenant_001, tenant_002); test functional al indexului in tranzactie ROLLBACK:
2x test permis, al 2-lea prod viu BLOCAT (UniqueViolation), prod/nok permis langa un viu, 0 reziduu.
LIMITA: garda acopera doar starile 'viu' pe prod; o factura respinsa (nok) se poate re-trimite (corect).
Curatarea/retentia xml_trimis (text mare) si zip_raspuns_path (fisier) - de decis cand creste volumul.

### 18.07.2026 (corectie host) e-Factura: TREI host-uri pentru TREI metode (verificat LIVE)  (core/efactura_send.py)
DECIZIE: host-urile e-Factura, verificate live (nu din listare interpretata, nu din build vechi):
  - UPLOAD/stare/descarcare prin OAuth (Bearer) -> https://api.anaf.ro/{prod|test}/FCTEL/rest
  - VALIDARE structura (fara token/drept)        -> https://webservicesp.anaf.ro/prod/FCTEL/rest/validare/FACT1
  - Metoda cu CERTIFICAT client (mTLS)           -> https://webserviceapl.anaf.ro/... (NU server-side OAuth)
Fiecare = o singura constanta (FCTEL_BASE_TPL, FCTEL_VALIDARE_TPL).
TEMEI (dovada reproductibila): (1) handshake TLS pur catre webserviceapl.anaf.ro -> SSLV3_ALERT_
HANDSHAKE_FAILURE (cere certificat client); catre api.anaf.ro -> 401 (TLS ok, cere doar auth).
(2) upload cu tokenul pe api.anaf.ro/test -> HTTP 200 + raspuns ANAF real ("Nu aveti drept..."),
deci api.anaf.ro E host-ul OAuth. (3) validare pe webservicesp.anaf.ro -> 200 + verdict schematron.
RASTOARNA decizia din 18.07 care pusese webserviceapl.anaf.ro pentru upload: aia e ruta mTLS din
listare, nu OAuth. Corectia vine de la SURSA LIVE (handshake + raspuns), autoritate peste listarea
interpretata gresit SI peste build-ul vechi (care avea api.anaf.ro corect pt OAuth). Regula ramane:
host din verificare la sursa, nu din memorie.
ALTERNATIVA RESPINSA: webserviceapl.anaf.ro pt upload (nu face handshake fara cert); un singur host
pt toate (sunt trei metode distincte, trei host-uri).
LIMITA: verificat live 18.07; daca ANAF muta host-urile, se reverifica cu aceleasi 3 comenzi.

### 18.07.2026 e-Factura structura BR-RO validata la sursa (validator ANAF) + adresa cumparator  (core/efactura_send.py; migrare_efactura_adresa.py)
DECIZIE: XML-ul de trimitere se valideaza pe validatorul oficial ANAF (webservicesp .../validare/FACT1),
FARA drept pe CIF - judecatorul de structura, ca DUK pentru declaratii. Functia valideaza() intoarce
(ok, mesaje). Decuplat de drept: putem valida structura chiar daca certificatul nu are drept SPV pe CIF.
TEMEI (descoperit la sursa, nu ghicit): prima validare a picat cu:
  - BR-RO-110: tara cumparator RO -> BT-54 (judet) OBLIGATORIU (cod ISO 3166-2:RO). Schema avea doar
    tert_adresa text liber -> ADAUGAT facturi.tert_oras (BT-52) + facturi.tert_judet (BT-54).
  - BR-RO-100: vanzator in Bucuresti (RO-B) -> localitatea (BT-37) trebuie SECTOR1..6, nu 'Bucuresti'.
    Helper _localitate() deriva sectorul din oras+adresa; aplicat AMBELOR parti.
Dupa populare (cumparator judet+oras) + regenerare -> validator: {"stare":"ok"}. Confirmat pe tenant_002
factura 1 (vanzator DANTE Bucuresti -> SECTOR6/RO-B; cumparator -> SECTOR3/RO-B). 6 teste unitare pass.
ALTERNATIVA RESPINSA: a ghici cardinalitatea BR-RO din memorie - validatorul e ieftin (0.16s) si
autoritar; un nok pe TEST costa un ciclu, nu o depunere. Munca de schema (coloane tert) s-a facut DOAR
dupa ce validatorul a confirmat ca BT-54 e obligatoriu, nu speculativ.
LIMITA: cod postal cumparator (BT-53, optional) inca nestructurat; sectorul pt Bucuresti se deriva prin
regex din adresa - daca adresa nu contine 'Sector N', ramane orasul (validatorul ar semnala). taxare
inversa/neplatitor/storno inca netratate (v1).

### 18.07.2026 F160 e-Factura cont gratuit: reguli de arhitectura + POARTA pe cheia token gratuit  (core/efactura_send.py)
DECIZIE (3 reguli nenegociabile pentru trimiterea e-Factura, valabile si F126 si F160):
1. POARTA validare/FACT1 OBLIGATORIE inainte de ORICE upload. trimite() cheama valideaza() si NU
   uploadeaza daca validatorul nu intoarce stare:ok. E gratis, fara auth/drept - nu exista scuza sa
   trimiti structura nevalidata la SPV. Diferentiatorul vs SmartBill: nu trimitem gunoi, validam la ANAF intai.
2. _localitate() STRICT: daca in Bucuresti (RO-B) nu se extrage clar SECTOR1..6 din adresa, NU inventa ->
   EDateIncomplete ("completeaza sectorul"), butonul blocheaza, nu trimite. Sector gresit = nok sau factura
   acceptata cu date gresite. Filozofia control_incrucisat: gri nu se falsifica in verde.
3. Upload real ramane NETESTAT live in dev (dev token n-are drept pe niciun CIF real, ca F176). Lantul e
   dovedit izolat (generator, valideaza, tracking, mecanism OAuth), dar recipisa live (upload->stareMesaj->
   descarcare) e "pending drept", declarat onest - nu se coloreaza verde. Se dovedeste doar cu user real /
   CIF cu drept.
TEMEI DOVADA: trimite() pe TEST tenant_002 -> poarta valideaza=ok, apoi upload -> "Nu aveti drept in SPV
pentru CIF=14399840". 8 teste unitare (inclusiv sector strict + blocare).

POARTA (STOP, cere decizie): F160 = e-Factura din CONTUL GRATUIT, dar conectorul SPV e CABINET-ONLY:
  - public.spv_token.accounting_firm_id e NOT NULL; contul gratuit are accounting_firm_id NULL (tenant fara cabinet).
  - /spv/autorizare e gardat pe cere_cabinet -> contul gratuit nici nu poate porni OAuth-ul.
Deci tokenul gratuit nu are cum sa fie cheiat/stocat azi. E schimbare de SCHEMA pe tabel LIVE (spv_token) +
modificare de cod LIVE (connect) -> nu se decide unilateral.
PROPUNERE (de confirmat): spv_token primeste tenant_id (nullable) + accounting_firm_id devine nullable, cu
CHECK ca exact unul e setat (cabinet XOR gratuit); ia_token_activ/apel_anaf/salveaza_token/url_autorizare
capata un "principal" (firm_id SAU tenant_id); /spv/autorizare gratuit pe cere_context (nu cere_cabinet).
Restul lantului F160 (generator+poarta+upload+tracking) e gata si asteapta doar cheia tokenului.
LIMITA: pana la decizie, F160 = PARTIAL (lant gata, connect gratuit blocat). F126 (cabinet) NU e blocat de
asta - are deja token per accounting_firm.

### 18.07.2026 spv_token = PRINCIPAL (cabinet XOR firma gratuita), optiunea 1  (core/spv_conector.py; migrare_spv_token_principal.py)
DECIZIE: tokenul SPV apartine unui PRINCIPAL - cabinet XOR firma self-service (gratuita) - nu unei
tabele de firme. Un SINGUR tabel public.spv_token, cheiat pe accounting_firm_id SAU tenant_id.
TEMEI: un singur tabel = o singura cale de refresh, F177 ramane SURSA UNICA de reinnoire. Determinarea
gratuit-vs-cabinet e la nivel de tenant (reparat azi) - tokenul respecta aceeasi distinctie.
ALTERNATIVE RESPINSE: (2) tabel separat pt gratuit = doua surse de adevar, F177 sare peste tokenul
gratuit -> expira tacit = esec de siguranta; (3) accounting_firm_id sintetic per tenant gratuit =
reconfleaza cabinet cu firma gratuita, anuleaza determinarea la nivel de tenant reparata azi = regresie.
PATRU GARDURI (nenegociabile):
1. XOR in DB, nu in cod: CHECK ((accounting_firm_id IS NOT NULL)::int + (tenant_id IS NOT NULL)::int = 1).
   Plus unique partial: un singur token VIU (activ) per principal.
2. Un singur resolver spv_principal(context) -> (kind, id). /spv/autorizare SI refresh-ul F177 branseaza
   prin ACELASI loc (SQL-ul de principal centralizat), nu imprastiat prin connector.
3. Capcana F177: query-ul de reinnoire NU filtreaza pe accounting_firm_id IS NOT NULL (ar sari tacit
   peste tokenele gratuite). Selecteaza pe principal. TEST dedicat: token gratuit care expira -> cronul
   il prinde. E regresul cel mai probabil.
4. Poarta de autorizare STRANSA: cere_cabinet -> cere_context, DAR caller-ul trebuie sa DETINA principalul
   (admin firma gratuita autorizeaza DOAR tenantul lui; admin cabinet doar firma lui). NU "orice user autentificat".
ORTOGONAL: maparea CIF-uri per token (spv_cui_acoperit) ramane cum e, n-o atinge aici.
LIMITA: pana la wiring-ul complet F160, cabinetul (F126) ramane neafectat; refactorul pastreaza calea
cabinet identica (test_spv_conector verde).

### 18.07.2026 (construit) spv_token principal - cele 4 garduri verificate  (commit urmator)
CONSTRUIT si dovedit optiunea 1: schema (tenant_id + CHECK XOR + unicitate partiala per principal +
1 token viu/principal), connector refactorizat pe Principal, spv_rute cu resolver spv_principal
(cere_context + proprietate), F177 pe principal. GARDURILE:
1. XOR in DB: CHECK ((accounting_firm_id IS NOT NULL)::int + (tenant_id IS NOT NULL)::int = 1) + indecsi
   partiali uq_spv_token_firm/tenant + _viu. 2. Resolver unic spv_principal (context) + principal_din_rand
   (rand) -> acelasi tip Principal, _principal_sql = unicul loc cu schema cheii. 3. Capcana F177 prinsa:
   query pe activ (nu pe accounting_firm_id IS NOT NULL) + TEST dedicat (test_cron_F177_prinde_token_gratuit,
   test_refresh_gratuit_deriveaza_principal_tenant). 4. Poarta: cere_context, dar spv_principal cere
   PROPRIETATEA (cabinet=firma lui; gratuit=tenantul lui din user_tenants, verificat accounting_firm_id NULL).
DOVADA: 31 teste pass (23 conector + 8 generator); cabinet neafectat (apel_anaf(principal_firm(1)) live -> 200,
token 21 intact, stare_conexiune conectat); migrare aplicata ca postgres (owner). Ortogonal: spv_cui_acoperit neatins.
RAMAS pentru F160 complet: buton/ruta "Trimite in SPV" in portalul gratuit; recipisa live pending drept (ca F176).

### 18.07.2026 F160 e-Factura din cont gratuit - ruta + buton, flux LIVE (mai putin recipisa)  (main.py; facturi_ecran.js)
DECIZIE: ultima veriga F160 - ruta POST /tenants/{tid}/facturi/{fid}/trimite-spv + butonul "Trimite in SPV"
per factura emisa. PORTI in ORDINE FIXA (efactura_send.trimite), niciuna sarita:
1. TOKEN VIU (principalul are token activ?) -> altfel 409 fara_token ("conecteaza ANAF intai"). Nu upload fara token.
2. VALIDARE/FACT1 (Regula 1) -> nok: intoarce erorile BR-RO, NU uploada. Diferentiatorul vs SmartBill.
3. IDEMPOTENCY (send viu incarcat/in_prelucrare/ok pe factura+mediu) -> 409 deja_trimisa. Upload ANAF nu e idempotent.
4. UPLOAD pe tokenul PRINCIPALULUI via apel_anaf -> scrie randul indiferent de rezultat (ok/eroare + mesaj integral).
Principalul = spv_principal(ctx) (cabinet=firma lui, gratuit=tenantul lui); ruta pe cere_context, proprietate impusa.
BUTON (Regula 0, DS): pe detaliul facturii emise (nu global), semafor cu tokeni (gri netrimisa/pending drept,
galben in_prelucrare, verde ok+recipisa, rosu nok/eroare cu mesaj la click); confirmare prin confirmaCaseta
(fara confirm()/alert()). Poll-ul stareMesaj/descarcare NU e sincron in ruta.
DOVADA: stiva completa HTTP - token mintuit pt cabinet (firm 1) -> POST trimite-spv factura reala -> auth +
spv_principal + 4 porti + upload live -> ExecutionStatus=1 "Nu aveti drept pentru CIF" (asteptat, dev token).
Toate portile dovedite izolat (fara_token/nevalidat/deja_trimisa/upload). node --check + verificator 0.
CARENTA declarata onest (nu colorata verde): recipisa LIVE (upload->stareMesaj->descarcare) e PENDING DREPT -
se dovedeste doar cu un patron real cu certificat inrolat cu drept SPV pe CIF-ul lui (ca F176). Piesa separata
ramasa: cron de poll stareMesaj/descarcare care avanseaza incarcat->ok/nok + preia recipisa.

### 18.07.2026 F178 cron poll e-Factura - jumatatea de PRIMIRE, masina de stari completa  (core/spv_poll.py)
DECIZIE: cronul de poll (stareMesaj/descarcare) NU e "dupa ce ai CIF real" - e jumatatea de PRIMIRE a
propriului send. Fara el o factura urcata ramane blocata in 'incarcat' la infinit, nimic n-o avanseaza;
masina de stari e incompleta si F160 nu functioneaza cu adevarat pentru un patron real chiar daca send-ul
merge. Se construieste + unit-test ACUM; doar dovada LIVE (incarcat->ok live) ramane pending drept.
GARDURI (toate implementate + testate): (1) reutilizeaza apel_anaf pe tokenul principalului (cabinet XOR
gratuit, derivat din tenant) - nu duplica token/refresh; (2) scope strict: terminale (ok/nok/eroare_upload)
NU se re-interogheaza (nu intra in de_polat); (3) token expirat -> apel_anaf face refresh, altfel SKIP randul,
NU-l marca (auth-fail != factura respinsa) - test dedicat; (4) rata: 1000/min verificat la sursa (apel_anaf
429 backoff) + sleep intre randuri + timer la 30 min; cuota ZILNICA stareMesaj/descarcare NU e in sursele
locale -> conservator, NU fabricata; (5) timeout: blocat in in_prelucrare peste prag -> 'investigatie' (gri,
verifica manual, nu abandon tacit); pragul (2z) conservator, ANAF nu documenteaza public timpul -> de confirmat
la sursa; (6) parsare defensiva: logheaza raspunsul brut integral la prima interogare reala, forma neasteptata
-> gri + log, nu swallow spre verde.
DOVADA: 9 teste (6 clasificator pur pe formele documentate ANAF: in prelucrare/ok/nok/"XML cu erori"/timeout->
investigatie/gunoi->neasteptat; 3 integrare DB+mock: ok->descarca recipisa salvata+sha, skip-auth nu marcheaza,
terminal exclus din de_polat). Rulare reala (0 randuri, tabel curat), timer spv-poll activ (30 min). Starea
'investigatie' adaugata la CHECK (per-tenant + template). Semafor buton: investigatie = gri, ne-retrimisibila.
LIMITA (onest, ca F176): round-trip live incarcat->ok se dovedeste doar cu un patron real cu CIF cu drept SPV;
descarcarea recipisei nu se coloreaza verde live pana atunci. Cuota zilnica + timpul de prelucrare = de confirmat.

### 18.07.2026 F179 cron receive e-Factura - jumatatea de PRIMIRE a F126 (pasii 3+4)  (core/spv_receive.py; migrare_efactura_primite.py)
DECIZIE: cronul de RECEIVE (facturi furnizori din SPV) + tabelul efactura_primite (per-tenant). Listeaza
filtru=P (FACTURA PRIMITA) per tenant, descarca facturile noi, le insereaza CIORNA. Pasii 3 (schema dedup)
si 4 (cron) din ordinea aprobata; pasul 5 (four-eyes UI) ramas.
SCHEMA efactura_primite (stabilita de Costin): id_mesaj_anaf UNIC (dedup), cif_emitent/cif_beneficiar,
xml_brut + xml_sha256, status (descarcata/ciorna/validata/respinsa), factura_id NULL pana la four-eyes.
TREI GARDURI (nenegociabile, implementate + testate):
1. id_mesaj_anaf UNIC + ON CONFLICT DO NOTHING - cronul ruleaza la 30 min pe fereastra 2-3z suprapusa,
   aceeasi factura apare la mai multe rulari; fara dedup = duplicate la fiecare rulare.
2. cif_beneficiar VALIDAT la insert (== CIF tenant), nu doar stocat. Pe token de cabinet care acopera N
   CIF-uri, factura se leaga de tenantul al carui CIF = cif_beneficiar; mismatch -> NU importa + log.
   Anti-scurgere INTRE CHIRIASI la nivel de insert, nu de afisare.
3. Masina de stari + factura_id NULL pana la four-eyes: descarcata (auto) -> ciorna (parsata, prezentata)
   -> validata (om confirma, ABIA atunci cheltuiala + factura_id) / respinsa. NU auto-crea cheltuiala la
   import; evidenta contabila doar din status=validata (filozofia control_incrucisat, nu falsifica in verde).
REUTILIZARE: lista_mesaje/descarca prin apel_anaf pe principal (partajat cu F178, fara client paralel);
principal_pentru_schema extras in efactura_send (folosit si de F178). Alimenteaza efactura_import existent.
DOVADA: 4 teste (anti-scurgere, ciorna daca parsabila, descarcata fallback, dedup) + 23 SPV fara regresie;
rulare reala prin stack (listaMesajeFactura prod filtru=P -> ANAF "fara drept", asteptat). Timer spv-receive
activ (30 min, offset :17/:47 fata de F178 :07/:37). Migrare efactura_primite 2/2 scheme + template.
LIMITA (onest, ca F176): importul LIVE (descarca factura reala) se dovedeste doar cu un CIF cu drept SPV.
RAMAS pentru F126 complet: pasul 5 four-eyes (ecran contabil: ciorna -> validare -> cheltuiala + factura_id).

### 18.07.2026 F126 e-Factura complet - pasul 5 four-eyes + LIVE cap-coada  (main.py rute facturi-primite; facturi_ecran.js)
DECIZIE: pasul 5 (four-eyes UI) inchide F126 receive cap-coada. Ecran de validare a facturilor primite:
prezinta datele PARSATE (nu XML brut - efactura_import.parseaza_xml, arhiva bruta la click), cont de
cheltuiala SUGERAT (din istoricul aceluiasi furnizor) dar CONFIRMAT de om, doua actiuni Valideaza/Respinge.
GARD FOUR-EYES (verificat la sursa - grep INAINTE de a scrie): patru-ochi la efactura_primite = separare
AUTOMAT (cron F179 = ochiul 1) vs UMAN (contabil = ochiul 2), NU user A vs user B. Regula creat_de != aprobat_de
traieste DOAR pe declaratii_coada (asistenti_api/coada_api) si e corecta ACOLO (om pregateste, om aproba);
NU se copiaza la primite (masina importa, om valideaza). Un cabinet cu UN singur contabil trebuie sa poata
valida. Gardul real = rol/acces la tenant + status='validata' actiune umana explicita; ZERO validated_by != imported_by.
IDEMPOTENT: SELECT ... FOR UPDATE + verifica status (dublu-click/doua taburi -> deja_validata, nu a doua cheltuiala).
CONDUCTA UNICA: valideaza reutilizeaza _factura_din_parsat (acelasi INSERT ca /import-efactura upload manual,
extras DRY) -> factura directie=primita in facturi -> intra AUTOMAT in verificatorul TVA existent (D300 vs 4426),
nu ramane orfana. cont_cheltuiala + motiv_respins adaugate la efactura_primite (respinsa NU se sterge - istoric).
DOVADA: backend HTTP cap-coada (GET lista preview parsat; valideaza -> factura_id legat + validata + cont;
idempotent deja_validata; respinge + motiv; 422 fara motiv); ecran node --check + verificator 0. Anatomia
ecranului = bon OCR four-eyes existent (cont editabil, buton-verde, confirmaCaseta, fara confirm/alert).
LIMITA (onest, ca F176): import/recipisa LIVE pending drept - ecranul testat cu ciorna INJECTATA (factura
parsata, factura_id NULL). Round-trip real se dovedeste cu un patron real cu CIF cu drept SPV.
F126 -> LIVE (cap-coada: send + receive + four-eyes). F127/F128 raman AMANATE.

### 18.07.2026 F121 e-Transport trimitere - pasul 2 mecanism (functii + garda timp + tabel)  (core/etransport_send.py)
DECIZIE: mecanismul de trimitere e-Transport UIT construit peste conectorul principal (drept UNIFICAT):
functii upload_uit/stare_uit/lista_uit prin apel_anaf pe spv_principal (fara client paralel), garda de
timp UIT specifica, tabel etransport_trimiteri, orchestrator trimite cu porti in ordine.
DREPT UNIFICAT (verificat la sursa, ARHITECTURA_SPV.md): acelasi token SPV acopera si e-Transport
(JWT roluri EFACTURA+ETRANSPORT; OMFP 660/2017 = toate serviciile). spv_principal NU se dubleaza, NU e
principal separat - optiunea (a). Per-CIF drept ramane empiric (403/fara drept pe lista/upload).
PORTI (in ordine fixa, ca la e-Factura): 1) GARDA DE TIMP (fereastra_uit - specifica, NU copiata de la
factura: max 3 zile inainte de miscare, UIT valabil 5z national/15z intracom, dupa expirare BLOCAT);
2) IDEMPOTENCY (dedup xml_sha256 pe prod - upload ANAF nu e idempotent, UIT dublu); 3) VALIDARE pe TEST
(mediu=test - NU exista validator fara auth ca validare/FACT1, confirmat la sursa; nu trimite prod nevalidat);
4) UPLOAD prod -> scrie randul + UIT + valabilitate.
ENDPOINT-URI la sursa: ETRANSPORT/ws/v1, PARAMETRII IN PATH (upload/ETRANSP/{cif}/{versiune=2},
stareMesaj/{id}, lista/{zile}/{cif}) - diferit de e-Factura (FCTEL/rest, query). Persistat in ARHITECTURA_SPV.md.
DOVADA: 8 teste (garda timp national/intracom/prea-devreme/expirat; URL path-params; porti trimite cu mock).
Migrare etransport_trimiteri 2/2 + template.
LIMITA (onest, ca F176): formatul EXACT al raspunsului upload/stareMesaj (ExecutionStatus/UIT) e din pattern
ANAF, parsare DEFENSIVA, de confirmat la primul raspuns real. Trimiterea LIVE pending drept e-Transport pe CIF real.
RAMAS: F121 UI (pasul 4) - buton Trimite UIT time-critical cu avertisment "mai ai X zile"/"UIT expira in Y".
Cand F121 transmite -> F044 (generator) -> LIVE.

### 18.07.2026 F121 e-Transport UI (pasul 4) - buton Trimite UIT + semafor de timp -> F044+F121 LIVE  (etransport_ecran.js; main.py)
DECIZIE: UI-ul de trimitere e-Transport peste cardul F044 existent (NU ecran nou): buton "Trimite UIT" +
avertisment de fereastra + lista UIT-uri trimise. Inchide e-Transport cap-coada. F044 -> LIVE (XML-ul merge
la API, nu doar manual) + F121 -> LIVE.
GARDURI SPECIFICE e-Transport (cerinta pe TERMEN pe care factura n-o avea):
1. SEMAFOR DE TIMP vizibil, SEPARAT de semaforul de trimitere (doua dimensiuni): fereastra ("declara pana
   in X") + valabilitate UIT ("expira in Y"). verde=in fereastra/valabil, galben=aproape (~1 zi), rosu=expirat.
   O notificare poate fi trimisa cu succes (trimitere verde) dar cu UIT aproape expirare (timp galben) - nu se contopesc.
2. Butonul Trimite respecta portile backend: _fereastraUit client-side blocheaza butonul in afara ferestrei
   cu motivul ("prea devreme", "expirat") - userul nu apasa ca sa esueze la ANAF; backend re-verifica (autoritar).
3. Fara batch tacit: UIT-urile trimise sunt vizibile pe card cu semaforul de timp, nu ascunse intr-un cron.
4. confirmaCaseta (fara confirm/alert), anatomia cardului.
Rute: POST /etransport/trimite (genereaza XML + trimite() cu porti; intracom = tip AIC/10 -> UIT 15z),
GET /etransport/trimiteri (semafor timp + trimitere calculate server-side).
DOVADA: backend HTTP - POST blocheaza prea-devreme (blocat_timp cu motiv); GET intoarce 2 semafoare distincte
(UIT_ROSU: trimitere=verde, timp=rosu; galben; verde). node --check + verificator 0. 8 teste unit backend.
LIMITA (onest, ca F176): proba live (upload real + UIT de la ANAF) pending drept e-Transport pe CIF real -
ecranul testat cu notificare injectata + poarta validare pe TEST. Necolorat verde dus-intors in direct.

### 19.07.2026 F163 — control intre declaratii: azi D-vs-EVIDENTA, nu D-vs-D  (core/control_incrucisat.py:verifica_d390; FUNCTIONALITATI.csv F163)
DECIZIE: F163 (control incrucisat intre declaratii) se face v1 ca D390 (bunuri IC) vs EVIDENTA contabila
VALIDATA, NU declaratie-vs-declaratie (D390<->D300). Motorul existent (verifica_tva/verifica_d112 sunt deja
D-vs-contabilitate) se extinde pe o pereche noua; nu se construieste modul paralel.
TEMEI (verificat la sursa azi, nu din memorie):
  1. Randurile intracom ale D300 (R1_1 livrari, R5_1 achizitii) sunt MANUAL-ONLY: d300.calcul_d300 le
     populeaza DOAR din dict-ul 'manual' (transmis prin body la generare, declaratii_api.py:_d300), nu din
     facturi. Bucla automata pe facturi umple doar colectata pe cote (R9/R10/R11) si deductibila (R22/R74/R76).
  2. Manualul NU se persista: public.declaratii_depuse (coada_api.py) e jurnal gol - (tenant_id, an, luna, tip,
     data_depunere, sursa), fara valori de randuri, fara XML depus. Nu exista tabel cu decontul depus.
  => Un D300 regenerat de F163 fara manual are mereu R1_1=R5_1=0 -> ROSU pe orice firma cu IC (zgomot, nu
     semnal); iar reconstruit din aceleasi facturi ca D390 -> VERDE trivial (aceeasi sursa). Deci a doua sursa
     reala pentru cross-check e evidenta contabila validata (note status='validata'), nu a doua declaratie.
REGULA DIRECTIONALA (asimetrica, VIES = sursa mai autoritara pt IC - partenerul a raportat pe latura lui):
  declarat la VIES (D390) DAR absent din evidenta validata = ROSU (remediu SUGERAT: contabilizeaza SAU
  corecteaza recapitulativa - corectia o confirma omul, nu e mecanica); invers (in evidenta, neraportat la
  VIES) = GRI (decalaj de perioada posibil); ambele>0 cifre diferite = GRI (decalaj exigibilitate art.284,
  regularizari, rotunjire = legitime) - NICIODATA rosu pe diferenta de cifre; ambele 0 = tacut.
ALTERNATIVA RESPINSA:
  (a) D-vs-D real acum, regenerand D300 -> rosu fals pe orice IC (vezi temei 1-2). Respins: zgomot erodeaza
      increderea (mai rau decat lipsa controlului).
  (b) Reconstruire D300 din aceleasi facturi ca D390 -> verde trivial, zero semnal. Respins: circular.
  (c) Servicii IC (D390 bazaP/bazaS) in v1 -> respins: d300 nu expune R3_1_1/R7_1_1 azi; ar cere extinderea
      generatorului (reparatie reala), nu mapping paralel. Ramane v2.
LIMITA / CE RASTOARNA DECIZIA:
  - v2 F163 = persistarea randurilor declaratiilor DEPUSE (coloana/tabel la generare/depunere). Abia atunci
    D-vs-D real (D390 depus vs D300 depus). Prerechizit util si altor controale, nu doar F163.
  - v1 verifica doar BUNURI IC (livrari L / achizitii A, auto-maparea D390: emisa->L, primita->A). Servicii,
    triangulatie (T/R), si coerenta cu D300 DEPUS raman neacoperite (declarate ca limita in fiecare finding).

### 19.07.2026 F164 — alerte control fiscal: pull->push prin clopotelul existent, dedup pe persistenta  (core/alerte_control_fiscal.py; FUNCTIONALITATI.csv F164)
DECIZIE: findingurile ROSII de control fiscal (verifica_tva/d112/d390) se imping catre contabil printr-un
strat de PUSH peste clopotelul in-app EXISTENT (notificari_api), nu printr-un canal nou. Cron zilnic agatat
de core.notificari_scadenta (ruleaza deja 08:00), nu timer nou. O notificare AGREGATA per firma catre
validatorii_cabinetului (contabilii). Doar ROSU; gri ramane pull.
TEMEI: restanta 17.07 "alertele fiscale nu ajung la om" = lipsea stratul pull->push, NU canalul. Verificat la
sursa (grep): control_fiscal e pull-only (2 endpoint-uri cere_cabinet, calcul la deschidere); clopotelul
(public.notificari, badge+panou+read-state) exista si e declansat doar de de_validat/solicitare_client - niciun
finding fiscal. Canal + tintire (validatorii_cabinetului) + dedup (pattern public.alerte_emise/F103) = infra
reutilizabila. Destinatar = contabilul (findingurile cer corectii contabile), nu patronul.
GARDUL CRITIC (dedup pe persistenta): jurnal public.alerte_control_emise, cheie (tenant, verificator, perioada).
Un rosu care PERSISTA neschimbat = O SINGURA alerta, nu una pe zi (altfel spam zilnic pana la rezolvare).
Re-notifica DOAR daca: apare un verificator rosu NOU pe firma, SAU un rosu dispare si reapare (rezolvat -> sters
din jurnal -> reaparitia conteaza ca nou). Doua rulari aceeasi zi = o alerta. Jurnalizeaza DOAR ce s-a LIVRAT
efectiv (0 contabili -> nu marca, retry cand apar validatori - altfel un finding ar fi suprimat fara sa-l fi vazut
cineva).
ALTERNATIVA RESPINSA:
  (a) al doilea sistem de notificari - respins (clopotelul acopera; doua canale = drift).
  (b) push la FIECARE rulare a unui rosu persistent - respins: spam zilnic; contabilul dezactiveaza tot canalul.
  (c) email direct - amanat la v2 (digest Brevo), dupa ce push-ul in-app se dovedeste.
  (d) gri in clopotel - respins: "nu pot verifica" e informatie, nu actiune; nu spamam cu ce nu se poate rezolva.
  (e) push per finding (nu agregat) - respins: consecvent cu filtrarea anti-dublura din portofoliu, o firma = o alerta.
  (f) CREATE la runtime in cron - imposibil: PG15+ revoca CREATE pe public de la iconta_user; tabel creat de
      superuser (owner iconta_user, ca public.notificari), DDL = sursa de adevar in modul (DDL_JURNAL).
LIMITA / CE RASTOARNA DECIZIA:
  - Clopotelul ruteaza pe click doar link='validat' (navigator.js) - notificarea fiscala apare cu text+badge
    corect, dar click-ul nu deschide inca ecranul de control. Routing 'control-fiscal:{tid}' = follow-up mic.
  - Cronul verifica LUNA CURENTA (ca ecranul). Un rosu de luna trecuta nerezolvat iese din detectie la schimbarea
    lunii (consecvent cu ecranul, care tot luna curenta arata).
  - v2: digest email (Brevo) pentru contabilii care nu intra zilnic; routing click in clopotel.

### 19.07.2026 F164 routing clopotel: click pe notificare -> ecranul firmei; window._navGlobal era mort  (static/js/navigator.js + static/js/ecrane/control.js)
DECIZIE: click pe notificarea de control fiscal (link="control-fiscal:{tid}") deschide ecranul de control
al FIRMEI respective (auto-drill in detaliu), nu portofoliul general - contabilul a dat click pe "Firma X are
N rosii", vrea firma X. Implementat prin param optional randeazaControl(corp, nav, tidAuto): dupa portofoliu,
gaseste firma dupa tenant_id si reutilizeaza EXACT click-ul de rand (detaliuFirma cu obiectul firma complet,
aceeasi stiva portofoliu->detaliu). tid malformat -> log + fallback (ramai pe ecran), nu ecran alb.
TEMEI / DESCOPERIRE: routing-ul clopotelului se facea prin window._navGlobal, dar acesta NU era atribuit
nicaieri -> cazul 'validat' era COD MORT (click nu ruta nimic). Handler-ul clopotelului e functie de modul, in
afara closure-ului creeazaNavigator unde traieste `nav`. Reparat minimal-invaziv: window._navGlobal = nav la
crearea navigatorului (realizeaza pattern-ul deja presupus de cod), + cazul nou de routing langa 'validat'
(nu rescriu dispatcher-ul). EFECT SECUNDAR (intentionat de autorul original): click pe notificarea 'de_validat'
acum chiar duce acasa (inainte nu facea nimic) - comportament dorit, nu regresie.
ALTERNATIVA RESPINSA: (a) threading `nav` prin _clopotInit + panou builder - mai mult refactor si risc de ordine
de initializare (nav e const definit dupa apelul _clopotInit); global-ul e pattern-ul existent, 1 linie. (b) sa
deschid portofoliul general si sa las omul sa caute firma - respins de gard #3 (filtrat pe firma, nu lista).
LIMITA: JS static, fara build - schimbarea e live la reincarcare. Verificat: 7/7 parsare in node (inclusiv
malformat->fallback, rute existente intacte) + curl HTTP real (token cabinet): /control-fiscal/2 = ruta deschisa
de click intoarce firma corecta. Apelantii existenti (cabinet.js/asistent.js, 2 args) neatinsi.

### 19.07.2026 F184 — punte legislatie->re-verificare v1: cota TVA facturi emise, value-aware, la push  (core/control_incrucisat.py:verifica_cota_tva; FUNCTIONALITATI.csv F184)
DECIZIE: puntea "cand o valoare legislativa se schimba, firmele afectate devin rosii" se face v1 conectand un
check VALUE-AWARE (cota TVA facturi emise vs cota standard pe perioada) la push-ul F164 existent. Declansator =
cronul zilnic existent (nu COTE-driven proactiv - ala e v2, poate inutil). Doar checkul acum.
TEMEI (verificat la sursa 19.07):
  1. Valorile fiscale sunt PARAMETRIZATE cu DATA in common.COTE (nu hardcodate); cota() e period-aware. Semnalul
     de schimbare exista structural (ex. tva_standard 19->21 de la 01.08.2025, Legea 141/2025) - dar in COD (lege
     noua = rand nou + deploy), nu in DB. monitor_fiscal (text) e DECONECTAT de COTE (scrie doar alerte_fiscale).
  2. Verificatorii control_incrucisat (tva/d112/d390 din push F164) NU consuma cota() -> re-rularea lor dupa o
     schimbare de valoare nu produce nimic (compara declaratie vs contabilitate, ambele cu aceeasi cota). Golul.
  3. verifica_tva_pe_cota (verificatoare.py) era PRIMITIVA ORFANA (zero apelanti), per-tranzactie, period-aware,
     BLOCANT pe cota gresita. Fructul jos: deorfanizat printr-un wrapper la nivel de firma, NU rescris.
GARD ANTI-FALS-POZITIV: se verifica DOAR liniile la o cota din FAMILIA STANDARD (istoricul tva_standard, {19,21}).
Cotele reduse (9/5) si scutit NU depind de schimbarea cotei standard -> ignorate; altfel 9% ar aparea mereu
"gresit" fata de 21% = rosu fals pe orice firma cu cota redusa. Rosu doar pe cota clar gresita PENTRU PERIOADA.
ALTERNATIVA RESPINSA:
  (a) re-rula verificatorii existenti dupa schimbare - nu produc nimic (nu depind de valori). Respins (raport C).
  (b) declansator COTE-driven proactiv acum - amanat v2: cronul zilnic prinde deja rosul a doua zi; proactiv are
      sens doar daca ziua conteaza (de decis dupa ce v1 merge).
  (c) monitor_fiscal ca declansator - respins: text, nu valoare structurata; ramane proza informativa separata.
  (d) verifica pe (total-tva, tva) la nivel de factura - respins: factura poate avea cote mixte -> fals-pozitiv;
      se verifica per LINIE, doar liniile standard.
  (e) sub grupul "Declaratie vs contabilitate" - respins: e conformitate a facturilor emise, nu decl-vs-contab;
      grup SEPARAT "Conformitate facturi emise" (aditiv, nu reorganizare).
LIMITA / CE RASTOARNA DECIZIA:
  - Nu verifica clasificarea de PRODUS (daca produsul chiar cere cota standard), doar coerenta de PERIOADA.
  - Declansator zilnic, nu proactiv: un rosu apare a doua zi dupa schimbare, nu instant. v2 daca instant conteaza.
  - Cotele traiesc in COD (common.COTE); o lege noua tot cere editare + deploy (nu update de config).

### 19.07.2026 v2 F184 (declansator COTE-driven proactiv) — RESPINS  (DE_FACUT.md; firmeaza "amanat v2" din decizia F184 de mai sus)
DECIZIE: declansatorul COTE-driven proactiv (re-verificare INSTANT la depasirea unei date de valabilitate din
common.COTE) NU se construieste. In decizia F184 de mai sus era notat "amanat v2, poate inutil"; se firmeaza acum
ca RESPINS, nu doar amanat.
TEMEI: cotele traiesc IN COD (common.COTE); o cota noua cere oricum editare + deploy manual; cronul zilnic (F184
v1) prinde firmele neconforme a doua zi. Declansatorul instant n-ar castiga nimic real fata de un eveniment care
deja implica deploy. Decalajul de o zi = nesemnificativ.
LIMITA / CE RASTOARNA: daca vreodata cotele trec dintr-un tabel de config editabil FARA deploy (schimbare de
arhitectura), instant-ul ar putea conta - atunci se reevalueaza. Distinct de v2 F164 (digest email), care ramane
PLANIFICAT (nu respins).

### 19.07.2026 F185 — gardul INVERS al coliziunii CUI (cabinet->gratuit), simetric cu F092  (core/auth_api.py inregistreaza_cont_gratuit; FUNCTIONALITATI.csv F185)
DECIZIE: register cont gratuit pe un CUI DEJA sub un cabinet -> SEMNAL la inregistrare (coliziune_cabinet),
simetric cu F092 (coliziune_gratuit_v1 = gratuit->cabinet). Doar semnal, NU blocaj, NU auto-inchidere.
TEMEI (verificat la sursa 19.07): F092 acopera doar directia gratuit->cabinet (provision_tenant). inregistreaza_
cont_gratuit (auth_api.py:301) verifica doar conturile gratuite (un CUI = un cont gratuit), NU si daca CUI-ul e
sub un cabinet -> un CUI gestionat de un cabinet isi putea deschide cont gratuit self-serve NESEMNALAT (asimetrie).
Riscul e simetric (emitere dubla pe acelasi CUI). Reutilizat pattern-ul F092 (regexp_replace pe cifrele CUI,
activ=true), nu unul nou.
ALTERNATIVA RESPINSA: (a) blocaj dur la inregistrare - respins: proprietarul poate avea motive legitime, il
informezi nu-l opresti (consecvent cu decizia GDPR 18.07); (b) auto-inchidere a unuia - respins, inchiderea unui
cont = decizie umana (aceeasi ca F092); (c) sa expun numele/detaliile cabinetului registrantului - respins din
privacy: doar EXISTENTA (boolean).
LIMITA: semnalul e informativ, nu impiedica emiterea din niciun cont pana la suspendare manuala (superadmin).
Vizibilitatea persistenta pentru follow-up (raport superadmin de coliziuni active) = F186 PLANIFICAT, nu gard
critic. Match pe cifrele CUI (prinde prefix RO); nu testat pe CUI cu spatii/puncte interne (ANAF nu le foloseste).

### 19.07.2026 Diacritice: reparate 9 mesaje backend user-facing; comentarii si Tier 2 neatinse  (main.py, core/auth_api.py, core/produse_api.py)
DECIZIE: regula DS de diacritice ("textele afisate CU diacritice; cod/comentarii/markeri FARA") aplicata la
mesajele backend user-facing ASCII. Reparate 9 stringuri clar afisate userului (HTTPException/mesaj): Contactati->
Contactati (2x), negasit, "Daca emailul exista", chitanta/foloseste/factura/cheltuiala, blocata/inchisa,
inregistrare/ciorna/validata, foloseste (reges-config marker PASTRAT), "denumire lipsa". Corectate DOAR
adjectivele/verbele gresite; substantivele articulate corecte (perioada/luna/factura ca subiect) lasate.
CE NU S-A ATINS (temei):
  1. Diacritice in comentarii/docstring = IN AFARA regulii DS. Regula acopera identificatori/chei/markeri, NU
     comentarii (verificat cu Costin 19.07). Comentariile nu se afiseaza, nu-s gardianizate (verificatorul verifica
     doar text AFISAT fara diacritice, directia b). ~340 linii py + ~85 js pre-existente NU se sweep-uiesc - churn
     cosmetic fara valoare, zero risc functional. Include si docstring-urile F163/F184 din sesiune.
  2. Tier 2 (campul `motiv` cu "exista deja" in articole_import/retete_import/stocuri_cv) NEATINS: campul `motiv`
     DUBLEAZA ca marker (comparat in cod/teste: motiv=="cnp_invalid"/"cont_nepartener"/"cui_invalid"). Un text si
     marker SI afisat nu se atinge (riscul de a rupe o comparatie nu merita corectia cosmetica).
  3. Harta judetelor din d394.py ("ARGES"/"ARGEȘ"->cod) = chei de normalizare intentionate, alimenteaza D394
     (ANAF). Neatins - diacriticele pot rupe validarea, cheia dubla e deliberata.
AUDIT (directia a identificatori/chei + directia b frontend afisat): CURAT, nimic de reparat - codul era deja
conform unde e gardianizat. Singura nonconformitate reala = mesajele backend ASCII (backend nu e gardianizat).
LIMITA: lista celor 9 nu e exhaustiva pe tot backend-ul (main.py 7000+ linii); acopera cazurile clare gasite cu
un set de cuvinte frecvente. Extinderea gardianului la backend (nu doar frontend) = imbunatatire viitoare, daca merita.

### 19.07.2026 F187 export WinMENTOR: LIVE (servicii, dependent de config), Ciel BLOCAT pe specificatie  (core/export_winmentor.py; FUNCTIONALITATI.csv F187)
DECIZIE: export facturi emise catre WinMENTOR LIVRAT, oglindeste F171 SAGA (reutilizeaza conducta
date_factura/facturi_emise_luna/_firma), dar cu limita DECLARATA: NU e self-contained ca SAGA.
TEMEI (verificat la sursa OFICIALA 19.07, pdftotext pe download.winmentor.ro/.../22 Structuri import,
Facturi clienti.pdf Rev.1.2 + Articole noi.pdf): WinMentor cauta articolul in nomenclatorul lui; daca lipseste,
in Articole.txt co-locat; altfel importul ESUEAZA (NU auto-creeaza). Deci export = DOUA fisiere INI (Facturi.txt
+ Articole.txt), cod articol derivat determinist consecvent. Corectie oficiala vs sursa secundara (blog): UM vine
din TRANZACTIE (linia Facturi.txt), NU din Articole.txt; Clasa/GestiuneImplicita GOALE = valide. Gard encoding
Windows-1250 (s/t moderne->cedila legacy, apoi strict; neencodabil->422, nu byte gresit tacit - riscul BR-RO).
Gard factura: status='emisa' (facturi n-au 'validata'; exclude 'de_preluat'/'anulata').
DEPENDENTA DE CONFIG (explicita, nu ascunsa): exportul WinMentor cere config nomenclator WinMentor al cabinetului
(clasa, gestiune, UM pre-definite; constanta 'cod partener=cod fiscal' pt CodClient=CIF). v1 = SERVICII + articole
simple (Serviciu=D, ContServiciu=704, Clasa/Gestiune goale); stoc complex cu gestiune = v2/dependent de cabinet real.
Daca un cabinet emite marfuri cu gestiune, se semnaleaza ca exportul cere config, NU ca 'merge automat'.
COLATERAL: reparat bug latent F171 - ruta /tenants/{tid}/facturi/{factura_id} era netipata -> capta literalele
/facturi/export-saga si /facturi/export-winmentor (factura_id='export-...'->422), umbrind exportul-zip pe luna. Fix:
{factura_id:int} (literalele trec la rutele lor). SAGA month export era nereachable de la F171 - nimeni nu-l lovise.
ALTERNATIVA RESPINSA: (a) descrierea bruta ca CodArticol - respins, codurile WinMentor au format alfanumeric fix;
(b) "toate articolele = serviciu" tacit - respins (fals-verde pt firme cu marfa); Serviciu/config = explicit, default
servicii; (c) UTF-8 - respins, WinMentor cere Windows-1250; (d) Partner.txt companion in v1 - amanat v2 (CodClient=CIF
cu config e suficient pt v1).
CIEL = BLOCAT pe specificatie (NU planificat orb): 3 necunoscute - (1) versiune (v6/v7/NextUp au formate DIFERITE,
sursa facturis.ro); (2) spec neclar publica (nu exista portal oficial ca WinMentor); (3) cere coduri ANALITICE pe
care iConta poate sa nu le aiba la granularitatea Ciel. Se deblocheaza doar cu spec de la sursa Ciel / cabinet real
care importa in Ciel. NU se construieste pe sursa secundara (ar rupe importul, ca BR-RO).
LIMITA: round-trip real (import efectiv in WinMentor) pending cabinet real cu WinMentor configurat, ca proba SPV.
Cod complet + verificat contra spec oficial (11 teste + functional real), dar necolorat verde importul live.

### 19.07.2026 Gardieni verificator: 2 adaugati (ESC, caseta-atentie), 3 candidati RESPINSI ca fals-pozitivi  (verificator_conformitate.py)
DECIZIE: mutat 2 reguli DS din manual in automat - ESC_LOCAL (cap.10, securitate: variante locale _esc/escB/...
in loc de esc() canonic, risc XSS) + CASETA_ATENTIE (cap.5: #fdf3f3 inline in loc de .caseta-atentie, simetric cu
CASETA_INFO/POARTA_INLINE). Ambii 0 acum (protejeaza contra regresiei). TOTAL ramane 0.
RESPINSI (fals-pozitive dovedite la rulare - un gardian zgomotos e mai rau ca lipsa lui, ca un control rosu pe
diferenta legitima):
  - card-inactiv fara 'activ' (cap.2b): gardianul a aprins 9 candidati in migrare.js care sunt PASI DE WIZARD
    (nr:, .mig-pasi), NU carduri firme-optiune - semnatura {cheie:...desc:...} e partajata, line-regex nu distinge
    cert firme-optiune de pasi de migrare fara euristici fragile.
  - panou gri-pe-gri (cap.16): "invizibil" depinde de PARINTE (panou alb vs corp gri) + prezenta bordurii - context
    pe care regex-ul pe linii nu-l stie. Cele 3 background:var(--fundal) gasite: 2 au bordura (vizibile), 1 <pre>
    ambiguu - de privit vizual, nu clar violari.
  - background/border hex ad-hoc (cap.15): prea multe bg-uri inline legitime -> extinderea CULORI_HARDCODATE de la
    color: la background:/border: ar da fals-pozitive.
TEMEI: cele 3 nu se pot distinge cert legitim-vs-gresit prin regex pe linii (cer context de randare / parinte /
scop). Raman verificare manuala (DE_FACUT). 9 reguli DS raman audit vizual (randat/comportamental).
LIMITA: verificatorul e regex pe linii, doar ecrane JS - prinde semnatura textuala, nu randarea/asezarea/comportamentul.

### 19.07.2026 F188 pre-completare ANAF v9 la onboarding: SUGEREAZA, userul CONFIRMA  (core/anaf_api.py + main.py; static/js/ecrane/login.js + firme.js)
DECIZIE: la inregistrare (cont gratuit + cabinet adauga firma) CUI-ul pre-completeaza datele firmei din API-ul
public ANAF v9 - denumire in formular, adresa/CAEN/nr.Reg.Com./TVA/TVA-incasare in firma_profil la creare.
TEMEI: date PUBLICE ale propriei firme a userului (legal); infra exista deja ~80%% (anaf_api.valideaza_cui +
endpoint /public/verifica-cui + /tenants/{tid}/verifica-cui + coloane firma_profil). Verificat la sursa cu apel
REAL pe 14399840: v9 intoarce denumire/adresa/cod_CAEN/nrRegCom/scpTVA/RTVAI.statusTvaIncasare/stare_inactiv.
Parser extins cu nrRegCom + statusTvaIncasare; REPARAT bug latent (citea 'codCAEN', real e 'cod_CAEN' -> CAEN era gol).
GARDURI (aceeasi disciplina ca four-eyes: masina sugereaza, omul decide):
  - NON-SUPRASCRIERE: nu se pierde ce a tastat userul manual (completeaza doar campul gol sau neatins de la ultima
    pre-completare ANAF). Datele ANAF pot fi stale -> userul corecteaza, campuri EDITABILE.
  - DEGRADARE GRATIOASA: CUI invalid / ANAF 404 / ANAF jos -> mesaj discret "completeaza manual", formular INTACT,
    NU crapa, NU sterge ce a tastat. valideaza_cui intoarce {gasit:False} (HTTP 200), nu exceptie.
  - DEBOUNCE 500ms: un apel per CUI complet, nu pe fiecare tasta (rate limit ANAF 1/sec).
  - COALESCE la stocare: gol ANAF nu suprascrie existentul; 'nume' setat de user NU se atinge.
RAMAN MANUALE (v9 nu le are): telefon, email, IBAN, cod postal - marcaj UX clar (pre-completat vs de completat).
ALTERNATIVA RESPINSA: (a) suprascriere oarba a denumirii - respins (pierde input user, ANAF poate fi stale);
(b) blocarea campurilor pre-completate - respins (userul trebuie sa poata corecta); (c) cod TVA intracom din v9 -
NU e in v9, e VIES (serviciu separat verifica_vies) - amestecul ar fi gresit; VIES la onboarding = v2 daca merita.
LIMITA: register-gratuit foloseste buton explicit "Verifica la ANAF" (pre-existent), cabinet foloseste blur -
ambele pre-completeaza; nu am reorganizat UI-ul existent (DS: reorganizarea = STOP). oras/judet NU se extrag din
adresa structurata inca (adresa_sediu_social exista in v9) - flat adresa in v1, structurat = v2.

### 20.07.2026 MARKETING — ce se poate afirma onest despre "contabilitate completa"  (temei: inventar FUNCTIONALITATI.csv + verdict verificat)
DECIZIE: afirmatiile de marketing se ancoreaza in inventarul REAL (180 functionalitati, ~161 LIVE), nu in impresie.
Pozitionare: "contabilitate completa" = MASA (paritate cu competitia); "control fiscal automat" = DIFERENTIATOR
(varf de lance in mesaj).
TEMEI (verificat la sursa 20.07, inventar pe 7 zone): COMPLET - facturare, contabilitate primara (carte mare +
inchidere + casa + balanta + partida simpla), declaratii-GENERARE (toate 9, validate DUK), stocuri (NIR/CV/GV/
inventar/transfer), control fiscal. PARTIAL - salarizare (lipsa fisier bancar salarii + coduri COR), banca (lipsa
Open Banking, azi import de fisier). BLOCAT - depunerea declaratiilor direct la ANAF (F127: nu exista API de
depunere pt niciun soft cloud). NEPROBAT LIVE - e-Factura round-trip pe CIF real cu drept SPV (cod complet, pending
ca F176).

AFIRMATII PERMISE (adevarate, aparabile legal):
- "Software PENTRU contabilitate completa" - NU "oferim contabilitate" (CECCAR: iConta e INSTRUMENT, contabilul
  autorizat presteaza serviciul). Zone COMPLET: facturare, contabilitate primara, declaratii-generare, stocuri,
  control. PARTIAL declarat: salarizare, banca.
- "Genereaza si valideaza toate declaratiile (D100-D406 SAF-T) pe validatorul oficial ANAF (DUK)" - diferentiator.
- "Control fiscal automat: control incrucisat D300/D112/D390/cota TVA + semafor + alerte" - COMPLET+, varf de lance.
- "Depunerea o faci din SPV cu XML verificat de iConta (ANAF nu ofera depunere prin API niciunui soft cloud)" -
  onest, transforma limita ANAF (comuna tuturor) in non-problema, nu o ascunde.

AFIRMATII INTERZISE (overclaim / fals - risc legal + erodare incredere):
- "Depune cu un click la ANAF" - FALS (F127 blocat, depunere manuala din SPV).
- "e-Factura functionala live end-to-end" - PREMATUR (round-trip neprobat pe CIF real cu drept SPV). A se afirma
  DOAR dupa proba live reala.
- "100%% fara alt tool" - FALS (portal SPV necesar pt depunere + mesaje SPV).
LIMITA: inventarul reflecta starea 20.07.2026; se reevalueaza cand F127 (depunere) sau proba e-Factura live se
deblocheaza -> atunci afirmatiile INTERZISE de mai sus pot deveni permise. Pana atunci, NU.

### 20.07.2026 D212/PFA: partida simpla separata, INTENTIONAT (nu drift)  (core/rip_api.py + d212_engine.py; firma_profil.tip_firma de introdus)
CONSTATARE (grep 20.07): D212 ruteaza prin core/rip_api.py (fisa_d212) + d212_engine.py, IN AFARA
core/declaratii_api.py unde stau celelalte 9 (D100-D406). VERIFICAT LA SURSA: declaratii_api.py are ZERO
referinte D212; rip_api importa calculeaza_d212 din d212_engine.
DECIZIE: INTENTIONAT, nu drift. D212 ramane separat.
TEMEI: D212 = regim PARTIDA SIMPLA (registru incasari-plati / RIP), celelalte 9 = PARTIDA DUBLA (note
contabile validate). Surse de date DIFERITE - unirea lor ar amesteca cele doua sisteme contabile.
NU e paralel cu un discriminator existent (verificat 20.07): baza_contabila ('A') = norma pt nomenclatorul
D406/SAF-T, regim_fiscal = micro/profit (regimul CIT al SRL) - NICIUNUL nu discrimineaza srl/pfa (partida
dubla vs simpla). Deci tip_firma e discriminator GENUIN NOU, nu dublura -> justificat.
CONSECINTA (de introdus - flux planificat, inca neconstruit): tip_firma (srl/pfa) in firma_profil ca
discriminator UNIC pentru doua fluxuri:
  - meniu (firme.js): PFA arata cardul Incasari/plati + D212, ascunde partida dubla; SRL invers. (Azi cardul
    'rip' e vizibil universal - firme.js:188 - starea pe care asta o schimba.)
  - migrare (migrare_api.STRATURI): PFA ruleaza strat 'rip', sare solduri/plan_conturi/solduri_parteneri
    (fara sens la partida simpla). Azi STRATURI = firme/vector_fiscal/solduri/solduri_parteneri/salariati/
    asociati/mijloace_fixe/istoric_declaratii/plan_conturi (fara 'rip', fara ramificatie pe tip).
ALTERNATIVA RESPINSA: "cardurile vizibile universal, contabilul discerne" - respinsa la momentul preluarii:
migrarea trebuie sa STIE pe ce cale ruteaza straturile de import; discernamantul uman nu ruteaza cod.
LIMITA: PFA n-are balanta de deschidere - registrul e cronologic; se importa operatiunile anului curent.
Round-trip real (migrare + flux PFA cap-coada) pending primul cabinet cu PFA.

### 20.07.2026 F189 tip_firma SRL/PFA — filtrare carduri + selector la creare  (firme.js, tenant_provisioning.py, auth_api.py, tenant_template.sql; FUNCTIONALITATI.csv:F189)
DECIZIE: se implementeaza fluxul PLANIFICAT in decizia de mai sus (D212/PFA separat). La creare firma
se alege regimul (selector Tip firma, default srl). Meniul firmei ascunde la PFA cardurile de partida
dubla (Declaratii, Registru jurnal, Balanta, Bilant, Operatiuni speciale) si ascunde la SRL cardul
Incasari/plati. Control fiscal ramane vizibil la PFA (semafor partial, acceptat).
TEMEI: partida simpla PFA/II/IF (OMFP 170/2015, ca F077 Registru incasari/plati) nu produce
declaratii de partida dubla / jurnal / balanta / bilant -> cardurile respective n-au sens la PFA.
Discriminatorul tip_firma e deja stabilit genuin nou (nu baza_contabila, nu regim_fiscal) in decizia
precedenta. Verificat functional 20.07: provision PFA+SRL prin codul real -> tip_firma persistat,
lista il intoarce, filtrul ascunde/arata corect; ROLLBACK, zero firme test pe prod.
ALTERNATIVA RESPINSA: (a) a tine tip_firma in public.tenants ca sa fie usor de citit in lista -
respinsa, coloana traieste deja in firma_profil (schema-per-tenant) din 01_ddl_tip_firma.sql; a o
dubla in public.tenants = doua surse de adevar (drift). In loc, lista (auth_api.tenantii_userului)
aduce tip_firma per schema, cu SAVEPOINT pe fiecare firma ca o firma fara profil sa nu avorteze
tranzactia si sa degradeze silentios toate firmele la 'srl'. (b) a lasa selectorul sa scrie doar in
firma_profil-ul existent, fara a atinge template-ul - respinsa: VERIFICAT LA SURSA ca tenant_template.sql
(schema firmelor NOI) NU avea coloana tip_firma, deci INSERT-ul din provision_tenant ar fi crapat la
orice firma noua. Adaugat DDL in template, oglindit dupa 01_ddl_tip_firma.sql (coloana + CHECK).
LIMITA: filtrul e pe cheia cardului (lista DOAR_SRL/DOAR_PFA in firme.js) - un card nou adaugat la
meniu apare implicit la ambele regimuri pana e clasificat explicit. Migrarea (straturi_pentru) era deja
filtrata pe tip_firma inainte de aceasta tema. Round-trip real PFA cap-coada ramane pending primul PFA.

### 20.07.2026 F190/F191 Import RIP la preluare PFA + meniu migrare filtrat pe regim  (rip_migrare_api.py, main.py, migrare.js; FUNCTIONALITATI.csv:F190,F191)
DECIZIE: ruta POST /tenants/{id}/rip-import/incarca (import registru incasari-plati la preluarea unui
PFA, istoric cronologic, NU balanta de deschidere) + buton "Import RIP" doar la PFA in meniul de
migrare per-firma. Importul e idempotent la reimport (dedup). Meniul de migrare per-firma ascunde
straturile de partida dubla cand firma e PFA.
TEMEI: preluarea PFA = partida simpla (OMFP 170/2015). Ruta urmeaza tiparul verificat la sursa al
celorlalte rute de import (solduri/salariati/istoric): upload -> parse -> raport respinse INAINTE de
commit -> import atomic -> seteaza_status('rip') pentru reminder().
FIX LA SURSA (bug preexistent gasit prin test functional): core/rip_migrare_api._norm_metoda intorcea
'casa', dar CHECK-ul DB pe rip_operatiuni.metoda cere IN ('numerar','banca') (verificat pe tenant_002 +
aliniat cu modulul live core/rip_api.py, care foloseste 'numerar'). Orice import de operatiune cash ar
fi esuat. Corectat la 'numerar'.
DEDUP (cheia de identitate): VERIFICAT LA SURSA - rip_operatiuni NU are unique constraint (doar PK pe id),
tabela goala pe tenant_002 (fara pattern empiric). Cheia aleasa = (data_operatiune, tip, suma, explicatie,
metoda). 'tip' INCLUS peste sugestia initiala: aceeasi suma/data/explicatie pe sens opus (incasare vs
plata) sunt operatiuni distincte, nu duplicate. 'categorie'/'document' EXCLUSE: reclasificabile de
contabil - includerea lor ar sparge idempotenta dupa reclasificare. Verificat functional: reimportul
aceluiasi fisier de 2x -> a doua rulare importate=0, sarite_duplicat=2, registrul ramane la 2 randuri.
MENIU FILTRAT (sursa unica de adevar): straturile ascunse la PFA vin din migrare_api.straturi_pentru
(deja filtreaza pe STRATURI_META), expus prin GET /migrare/straturi - NU o lista duplicata in JS.
ALTERNATIVA RESPINSA: (a) lista de straturi de dubla hardcodata in migrare.js - respinsa, ar fi a doua
sursa de adevar fata de STRATURI_META (drift); in loc, endpoint + filtru pe cheia stratului. (b) dedup
pe unique constraint DB - respinsa acum (ar cere migratie de schema pe toate tenant-urile + decizie de
identitate batuta in cuie); dedup in cod la import e suficient pentru scopul (reimport sigur). (c) a
ascunde straturile de dubla si pentru Articole/Retete la PFA - nu: n-au cheie de strat in STRATURI_META,
raman la ambele (stoc/gestiune poate exista si la PFA cu gestiune CV).
LIMITA: dedup e fata de starea DINAINTE + ce s-a inserat in acelasi batch (un fisier cu doua randuri
strict identice pastreaza doar unul - tratat ca dublura de export, nu ca doua operatiuni reale). Daca
/migrare/straturi pica, meniul degradeaza gratios (arata tot); RIP ramane gated separat pe tip==='pfa',
deci nu apare la SRL nici in fallback. Reimportul dupa ce contabilul a EDITAT manual o operatiune
preluata (schimba suma/explicatie) nu o mai recunoaste ca duplicat - acceptabil (a devenit alt rand).

### 20.07.2026 F129 SPART - verificare individuala a 5 declaratii (D392/D094/D207/D700/D710)  (FUNCTIONALITATI.csv F192-F196)
DECIZIE: F129 ("Declaratii D392, D094, D207, D700, D710", bundle generic "informative/inregistrare
ramase", PLANIFICAT din analiza concurentei 13.07) era inventar NEEXAMINAT individual - exact tiparul
D230. Trecute toate 5 prin regula de aur la sursa oficiala ANAF (20.07). Verdicte individuale, F129
dizolvat, inlocuit cu 5 intrari (F192-F196):
- D710 (F192) DE CONSTRUIT: declaratie rectificativa a D100 (corectare obligatii bugetul de stat,
  autoimpunere/retinere). Aplicabila LARG (oricine depune D100). Activa (OPANAF 649/2025). Model de cod
  = d100.py (LIVE). Singura din 5 clar de construit.
- D207 (F193) AMANAT (ca D307): informativa impozit retinut la sursa pe beneficiari NEREZIDENTI (art.
  224 CF, OPANAF 179/2022 actualiz. 303/2026 - activa). Aplicabila dar NISA (doar firme cu plati la
  nerezidenti). Model structural = D205 (LIVE). Se construieste la caz real, nu preventiv.
- D392 (F194) RESPINS: depunerea 392A/392B SUSPENDATA prin lege pana la 31.12.2026 (art. LXII OUG
  115/2023). Nu se construieste motor pentru declaratie cu depunere suspendata legal.
- D094 (F195) RESPINS: nu mai exista de sine-statator - inglobat in D700 sectiunea B.II (mentiuni
  schimbare perioada fiscala). CONFIRMAT LA SURSA: lipseste din nomenclatorul DUK (anaf_surse/versiuni.xml),
  spre deosebire de celelalte 4 care au validator. Obligatia se satisface prin D700.
- D700 (F196) RESPINS: declaratie de mentiuni ADMINISTRATIVE (modificare vector fiscal/domiciliu/perioada),
  depusa direct in SPV la schimbare - nu se genereaza din evidenta contabila. Aliniat deciziei "nivel 4"
  din 17.07 (D010/D060/D093 administrative, RESPINSE).
TEMEI: fiecare verificat la sursa oficiala 20.07 (static.anaf.ro formulare OPANAF + nomenclator DUK
versiuni.xml local). Publicul iConta = firme private SRL/PFA/micro; D207 nisa, D392 suspendat, D094
abrogat, D700 administrativ.
ALTERNATIVA RESPINSA: a construi bundle-ul intreg (5 motoare) asa cum figura in registru - ar fi
insemnat 4 motoare inutile (2 pt declaratii inexistente/suspendate, 1 administrativ facut in SPV, 1
nisa) + abonament permanent de mentenanta. Exact eroarea de inventar D230/D106.
LIMITA: D207 se reia la primul caz real de plata catre nerezident. D392 reevaluat doar daca suspendarea
nu se prelungeste in 2027. D710: structura XML reala (validator D710_56) inca de confirmat vs d100.py
inainte de a decide reutilizare vs motor propriu (verificare in curs, pre-cod).

### 20.07.2026 F192 D710 LIVE — motor propriu declaratie rectificativa (nu extensie D100)  (core/d710.py; FUNCTIONALITATI.csv F192)
DECIZIE: D710 construit ca MOTOR PROPRIU, nu extensie a d100.py. Verificat la sursa inainte de cod
(validator D710Validator.jar / D710_56, descarcat + instalat in ~/duk/dist/lib): namespace propriu
(declaratie710, mfp:anaf:dgti:d710:declaratie:v2) DIFERIT de D100 -> structura XML nu se reutilizeaza.
Se reutilizeaza din d100 DOAR ce e identic la sursa: nomenclatorul COD_BUGETAR + utilitarele
_nr_evid / _scadenta_zile (codurile de obligatii/scadente sunt comune).
TEMEI: fiecare regula extrasa din validator (constant pool + mesaje) si dovedita iterativ pe DUK,
stare valid FARA ERORI pe date inventate izolat (micro 121 + profit 103, toate trimestrele):
  - fiecare suma are pereche Initial (_I) / Corectat (_C) - esenta rectificarii
  - suma_plata = suma_dat (rectificare suma datorata); totalPlata_A = SUMA(dat_I+plata_I+dat_C+plata_C)
  - d_recN: atribut introdus DE LA perioada 12.2025 - nu se pune pt perioade anterioare (regula validator)
  - cod 121 (micro) trim4: scadenta 25.06 an urmator, nu 25.01 (R15) - termen special de definitivare
  - cota doar la cod 121; cod bugetar determinat de cod_oblig (nomenclator)
INTEGRARE: (a) declaratii_api.py DISPECER - da (adaptor _d710, cere `obligatii`=corectiile). (b) selector
UI generic - NU: ecranul generic da doar an/luna/trim, nu `obligatii` -> ar aparea in dropdown si ar esua;
exclus prin _DOAR_API, ramane in DECLARATII (+ test cheie DUK). (c) semafor/monitor de restante
(control_fiscal_api, termene_api) - NU: D710 e RECTIFICATIVA (eveniment, la cerere), nu obligatie periodica
cu termen; a o pune acolo ar genera fals-restanta pe toate firmele. "Monitorizarea" ei corecta = disponibila
in dispecer + validata DUK + testata (test_d710.py, 25 teste). Regula "orice declaratie noua intra in monitor"
se aplica declaratiilor PERIODICE; o rectificativa nu e datorata recurent.
ALTERNATIVA RESPINSA: extinderea d100.py cu un flag rectificativ - respinsa la sursa (namespace/structura/
atribute I-C diferite; d100 nici nu are atribut de rectificare, "d_rec eliminat" in d100.py).
LIMITA: motorul acopera rectificarea sumei DATORATE (cazul dominant). Deducerile/reducerile/sponsorizarile/
AMEF (model 8#) au reguli diferite per cod_oblig (ex. cod 103: suma_plata=suma_dat-suma_redu, suma_ded nu se
completeaza) - nu se acopera speculativ, la primul caz real, extras iterativ pe validator (ca D307). Fara
ecran dedicat de corectii inca - generabila prin API/dispecer.

### 20.07.2026 F143 centre de cost - management accounting intern, fazat  (02_ddl_centre_cost.sql, centre_cost_api.py, jurnal_api.py, firme.js; FUNCTIONALITATI.csv F143)
DECIZIE: F143 (centre de cost + bugete) se construieste ca MANAGEMENT ACCOUNTING INTERN, fazat.
VERIFICAT LA SURSA (CONCURENTA.csv, 20.07): cei 4 concurenti care il au - FGO (analiza cheltuieli pe
furnizori/centre), Keez (centre + linii de buget), WinMentor (modul Bugete plan venituri/cheltuieli),
Nexus ERP (centre cost+profit + bugete) - sunt TOTI vendori pt firme private, dimensiune interna
"unde se duc banii pe departament vs plan". ZERO legatura cu contabilitatea bugetara publica (institutii
publice / clasificatie bugetara / angajamente) - alt vocabular, alta schema. Deci sigur de construit.
SCOP + FAZARE (dupa verificarea amplorii la sursa - notele n-au azi nicio dimensiune; inserarea in
inregistrari_linii e descentralizata, 11 INSERT-uri in 6 module):
- Dimensiune pe LINIE (nu pe antet): centrul e proprietatea liniei de cheltuiala/venit (clasa 6/7); o
  nota poate acoperi mai multe centre. Nullable = nealocat.
- Faza 1 = doar note MANUALE (jurnal_api, 2 INSERT-uri). Notele AUTOMATE (casa/stocuri/banca/retete)
  raman NULL - a le atribui centru cere reguli per-sursa = design mare, la caz real (Faza 3).
- Step A (LIVE): fundatia DB - tabel centre_cost + coloana centru_cost_id + FK, template + 02_ddl_*.sql
  aplicat pe toate tenant-urile.
- Step B (LIVE): centre_cost_api (CRUD: adauga/lista/dezactiveaza; NU stergere - FK pe linii istorice,
  se dezactiveaza) + jurnal_api poarta centru_cost_id + rute + card "Centre de cost" (ecran management,
  ales de Costin vs inline) + selector pe linia de nota + afisare in registru.
- Step C (LIVE): raport "realizat pe centru de cost" (GROUP BY centru, cheltuieli clasa 6 / venituri
  clasa 7 din note VALIDATE pe perioada, + linie "nealocat" pentru coverage; ciornele si notele din
  afara perioadei excluse - dovedit pe test). Faza 1 completa.
- Faza 2 (buget vs realizat): tabel bugete separat + ecran setare + raport varianta. NECONSTRUIT azi.
ALTERNATIVA RESPINSA: dimensiune pe toate cele 11 puncte de inserare din start - respinsa, s-ar propaga
necontrolat ("adauga un camp peste tot") + notele automate n-au cum sa aleaga centru fara reguli.
LIMITA: PFA (partida simpla) vede cardul dar centrele au sens redus la partida simpla; nu s-a filtrat pe
tip_firma (management accounting = optional la ambele). Bugetele si raportul de varianta = Faza 2, nedecise
in detaliu (per cont-clasa vs global, periodicitate) - se stabilesc cand se ajunge acolo.

### 20.07.2026 F143 Faza 2 - bugete pe centru de cost (granularitate + periodicitate + UI)  (03_ddl_bugete.sql, bugete)
DECIZIE: bugete pe centru de cost, cu variantele decise la sursa (Regula de Aur, reper CONCURENTA.csv):
1. GRANULARITATE = per clasa: o pereche (buget_cheltuieli, buget_venituri) per (centru, an), NU un buget
   net unic. TEMEI: raportul Faza 1 e deja per-clasa (cheltuieli/venituri/net); un buget net global ar
   ascunde depasirea pe cheltuieli mascata de venituri sub plan (net-ul poate coincide accidental).
   Concurenta confirma separarea: WinMentor "plan venituri/cheltuieli", Nexus "bugete diferentiate",
   Keez "linii de buget". Gestioneaza natural si centrele doar-cheltuieli (buget_venituri=0).
   RESPINS: buget net unic (pierde exact finetea pe care raportul o ofera deja).
2. PERIODICITATE = anuala (per centru/an). TEMEI: cel mai simplu de intretinut pentru un cabinet mic - o
   cifra per centru/an/tip vs 12x lunar / 4x trimestrial; bugetul anual e unitatea uzuala de planificare,
   varianta se raporteaza pe an (realizat-in-an vs buget-an), consistent. RESPINS: lunar/trimestrial
   (4-12x efortul de introducere, beneficiu marginal la scara de cabinet).
3. UI = extensie a ecranului Centre de cost existent, NU ecran nou. TEMEI: bugetele-s intrinsec legate de
   centre; un al doilea card ar fragmenta feature-ul. Sectiune "Bugete (anual)" cu selector de an: buget
   ch/ve editabil per centru + realizat + varianta alaturi.
SCHEMA (step A LIVE): tabel bugete (id, centru_cost_id FK, an, buget_cheltuieli, buget_venituri,
UNIQUE(centru,an)), 03_ddl_bugete.sql aplicat pe toate tenant-urile + template.
Step B (LIVE): centre_cost_api.seteaza_buget (upsert ON CONFLICT centru+an) + raport_varianta(an)
(buget vs realizat pe tot anul, clasele 6/7) + rute GET /varianta, PUT /{id}/buget.
Step C (LIVE): sectiune "Bugete si varianta (anual)" in ecranul Centre de cost - selector de an, buget
ch/ve editabil per centru, realizat + abatere colorata alaturi. REGULA DE COLORARE (binara, fara stare
neutra): ROSU = orice abatere NEFAVORABILA (cheltuieli PESTE buget: realizat>buget; SAU venituri SUB plan:
realizat<buget). VERDE = favorabil SAU exact pe tinta (cheltuieli la/sub buget; venituri la/peste plan).
Fara culoare daca bugetul respectiv = 0 (nesetat). Confirmat 20.07 - documentat complet (initial doar
latura favorabila era scrisa; codul implementa binar, deci venituri-sub-plan=rosu venea implicit).
Faza 2 completa; F143 = LIVE integral (Faza 1 + Faza 2).
LIMITA: buget anual -> varianta se compara pe an intreg (nu pro-ratare la sub-perioada). Raportul liber
[de,pana] din Faza 1 ramane pt drill-down operational; varianta e vederea anuala de planificare.

### 20.07.2026 F133 Faza 1 - tichete de masa (tratament fiscal verificat la sursa + scop)  (04_ddl_tichet_masa.sql, common.py, salariati_api.py, d112.py)
DECIZIE: se construieste Faza 1 = DOAR tichete de MASA, cap-coada (config -> calcul -> stat -> D112).
Vacanta + cadou = Faza 2 (tema viitoare). Optiunea A confirmata de Costin (semnal deja prezent:
tichetele de masa sunt cvasi-universale, "GOL REAL de salarizare" - CONCURENTA.csv:78).
TRATAMENT FISCAL 2026 (VERIFICAT LA SURSA 20.07, nu din memorie - s-a schimbat):
- valoare max 45 lei/zi lucrata (Legea 201/2025, MO 1106/28.11.2025; S1 + iul-sep 2026, reindexare oct).
- CASS 10% + impozit 10% pe valoarea tichetelor; FARA CAS, FARA CAM. Din 2024 (Legea 296/2023) tichetele
  au fost scoase din exceptia CASS -> intra in baza CASS. Efectiv ~19% retinut din nominal.
- doar zile efectiv lucrate (nu concediu/CM/absente) -> nr tichete = zile lucrate din pontaj (F135).
- impozitul pe tichete NU beneficiaza de deducere personala (aia e pe salariu).
D112 IN SCOP (verificat 20.07): d112.py IGNORA azi tichetele - citeste doar brut/cass/impozit/baza, iar
`bazac` (brut-facilitate) e folosit pt AMBELE baze CAS si CASS. Tichetele adauga la baza CASS + impozit
DAR NU la baza CAS -> bazele diverg, deci D112 chiar cere modificare (nu e optional). Inclus in Faza 1
ca sa nu ramana gaura (reteneri fara declarare = D112 gresit).
CONFIG (step 1 LIVE): plafonul (45) traieste in common.COTE cu data+temei (ca restul valorilor fiscale);
per salariat se stocheaza DOAR valoarea aleasa de firma (salariati.tichet_masa_valoare, 0=fara), validata
0..plafon la input. Nr de tichete NU se stocheaza - se ia din zilele lucrate la calcul.
LIMITA: peste-plafon nu se permite la input (un tichet de masa nu poate depasi maximul legal). Faza 1 nu
atinge tichete vacanta/cadou.
DECIZIE (step 2, calcul - 20.07): daca PONTAJUL LIPSESTE pe luna, zilele lucrate pt tichete = 0, NU se
prezuma zile lucratoare standard. TEMEI: tichetele se acorda pe zile EFECTIV lucrate, documentate prin
pontaj; fara pontaj nu exista dovada -> nu se calculeaza tacit o baza de tichete nedocumentata (o baza
prezumata ar duce la CASS/impozit declarate pe zile care poate n-au fost lucrate). Alegerea sigura =
0 + semnal ca lipseste pontajul.
FISCAL (step 2, verificat pe calcul): impozitul pe tichete se aplica pe (nominal - CASS_tichete) - CASS
e deductibila din baza impozitului (regula Cod fiscal venit-contributii), efectiv ~19% retinut din nominal
(nu 20%). "impozit" returnat de calcul_salariu = TOTAL salariu+tichete; cost_angajator include valoarea
nominala (angajatorul cumpara tichetele). Judecatorul final pt corectitudinea D112 = validatorul DUK (step 4).

### 20.07.2026 F133 step 3 - RASTOARNA decizia "0 fara pontaj" (premisa invalidata la sursa)
DECIZIE: numarul de zile pentru tichetele de masa = ACELEASI zile lucrate pe care payroll-ul le foloseste
deja pentru salariu (zile_lucratoare_luna - concediu_medical), NU din pontaj. Rastoarna decizia
"0 fara pontaj" de mai sus (step 2), care pleca dintr-o premisa GRESITA despre pontaj.
TEMEI (verificat la sursa 20.07, step 3): (a) pontajul (F135) stocheaza DOAR exceptiile - prezenta e
implicita (lipsa unui rand pe zi lucratoare = "prezent", pontaj.py:6-7,31) -> modelul NU poate distinge
"pontaj neintrodus" de "tot prezent" (ambele = 0 randuri) -> "0 fara pontaj" nu e exprimabil; (b) F135 a
decis EXPLICIT ca pontajul e informativ si NU alimenteaza calculul salarial (pontaj.py:4, DECIZII 17.07);
(c) payroll-ul deriva deja zilele lucrate ca zile_lucratoare_luna - cm_zile (proratarea brut_lucrat +
snapshot main.py:6003), fara pontaj. Deci sursa reala a "zilelor efectiv lucrate documentate" nu e
pontajul, ci luna standard minus absentele documentate (CM). Tichetele urmeaza aceeasi baza ca salariul ->
o singura notiune de "zile lucrate" in tot statul, coerenta. Costin a ales optiunea A (20.07).
IMPLEMENTARE (step 3 LIVE): stat_plata + fluturas trec tichet_valoare (din salariat) + tichet_zile
(=zile_lucratoare-cm_zile) in calcul_salariu; linie/bloc distinct de tichete in stat si pe fluturas;
monografie: 421=4316 include CASS tichete, 642=5328 pt nominalul acordat (achizitia biletelor 5328=5121/401
= tranzactie separata, in afara statului).
LIMITA: absentele nemotivate din pontaj NU reduc zilele de tichete (pontajul nu alimenteaza payroll, F135) -
tichetele urmeaza exact zilele de salariu (luna - CM). Daca in viitor se vrea reducerea tichetelor pe
absente nemotivate, ar cere alimentarea payroll din pontaj = rasturnarea F135, tema separata.

### 20.07.2026 F133 step 4 - D112 include tichetele (VALIDAT DUK) - Faza 1 completa  (d112.py)
DECIZIE: D112 declara tichetele corect. Bazele DIVERG (confirmat structural): baza CASS include valoarea
nominala a tichetelor, baza CAS NU (tichetele n-au CAS). Sumele declarate includ CASS+impozit pe tichete.
TEMEI: dovedit pe validatorul oficial DUK (judecatorul final, CLAUDE.md) - stare VALID FARA ERORI cu un
salariat cu tichete (brut 5000 + 45 lei x 23 zile, 07/2026):
  - B4_5 (baza CASS) = 6035 = 5000 + 1035 nominal tichete; B4_7 (baza CAS) = 5000 (fara tichete)
  - B4_6 (CASS) = 604 (500 salariu + 104 tichete); angajatorA 432 (CASS total) = 604
  - angajatorA 602 (impozit) = 359 (include impozitul pe tichete)
IMPLEMENTARE: pull() paseaza tichet_valoare+tichet_zile la calcul_salariu si extrage cass_tichete/
impozit_tichete/tichete_nominal; _d112_genereaza normalizeaza imp la salariu-only (imp din calc e TOTAL),
apoi adauga uniform tichetele dupa ambele ramuri (normala + CM), baza CASS = b4base + nominal.
Non-regresie: test_d112 + test_salarizare 24/24. Baseline (fara tichete) ramane valid.
F133 Faza 1 = LIVE INTEGRAL (config -> calcul -> stat/fluturas/monografie -> D112, cap-coada).
LIMITA: combinatia CM + tichete pe acelasi salariat in aceeasi luna - tichetele se adauga peste valorile
recalculate din CM; acoperit in cod dar nedovedit izolat pe DUK (cazul rar). Tichete vacanta/cadou = Faza 2.

### 20.07.2026 F133 Faza 2a - tichete de vacanta (one-off pe luna) - fiscal verificat + model  (05_ddl_beneficii_lunare.sql, beneficii_api.py)
DECIZIE: Faza 2 spartita in 2a (vacanta) + 2b (cadou), complexitate inegala. Se construieste 2a intai
(vacanta), input ONE-OFF pe luna (confirmat de Costin), NU config permanent ca tichetele de masa.
TRATAMENT FISCAL 2026 (VERIFICAT LA SURSA): tichete de vacanta = CASS 10% + impozit 10% pe valoare,
FARA CAS (art. 142 lit. r CF) si FARA CAM; plafon neimpozabil 6 salarii minime brute/an (~24.300 lei).
Acelasi tratament fiscal ca tichetele de masa -> se pot folosi aceleasi cai (CASS+impozit, fara CAS/CAM/
deducere) in calcul_salariu; diferenta = sursa (suma one-off vs valoare x zile) + plafonul anual.
MODEL (step 1 LIVE): tabel beneficii_lunare (salariat_id, an, luna, tip, valoare, UNIQUE pe cele 4),
CHECK tip IN (vacanta,cadou) - EXTENSIBIL pt 2b (cadou adauga tip='cadou' + eventual eveniment). API
beneficii_api (seteaza upsert / lista_luna / total_an pt plafonul anual). Sumele one-off se introduc pe
luna de acordare, nu ca valoare standing pe salariat.
DE CE spart de tichetele de masa (nu extins tabelul salariati): masa = valoare permanenta/zi; vacanta/cadou
= evenimente punctuale intr-o luna -> alt model de date (per luna), altfel nu s-ar putea da o vacanta in
iulie fara sa apara si in restul lunilor.
LIMITA: peste plafonul anual (6 sal.minime) suma devine taxabila integral - 2a acopera cazul SUB plafon
(comun) + semnal la depasire; taxarea integrala peste plafon = deferata (edge rar, ca la cadou 2b).
Steps urmatoare 2a: calcul (integrare in calcul_salariu) -> stat/monografie -> D112 (validat DUK).

### 20.07.2026 F133 - clarificare fiscala tichete: net CASH scade cu taxa, valoarea pe card separat  (stat_plata_api.py)
DECIZIE: net-ul de salariu (CASH) SCADE corect cu doar TAXA pe tichete (CASS+impozit), NU cu valoarea
lor; valoarea tichetelor se primeste pe card SEPARAT. Calculul era corect - problema era AFISAJUL care
ascundea re. Semnalat de Costin ("net scade in loc sa creasca, CASS pe vacanta nu apare").
VERIFICAT LA SURSA (Edenred/impozitul.ro): "Reținerile CASS și impozit se fac direct din salariul net...
nu se scade întreaga sumă din salariul net - doar impozitele și CASS-ul. Valoarea netă a tichetelor se
adaugă la venitul disponibil, chiar dacă sunt virate pe un card separat." Manual (brut 5000, vacanta 3000):
CASS tichete 300 + impozit 270 = 570 retinut din cash -> net 2984->2414; +3000 pe card = disponibil 5414
(cu +2430 fata de fara vacanta = 3000-570).
FIX AFISAJ (calc NEATINS): stat + fluturas arata acum explicit reținerea pe tichete (CASS+impozit) +
"total disponibil = net cash + tichete pe card". Impozitul principal din stat = salariu-only (consistent cu
CASS salariu); reținerea pe tichete = separat. Pe fluturas: taxa pe tichete inainte de NET (reduce cash),
valoarea tichetelor DUPA NET (pe card) + TOTAL DISPONIBIL.
LIMITA: "net" pe stat ramane net-ul CASH (corect fiscal/legal); "total disponibil" arata imaginea completa.

### 20.07.2026 F133 Faza 2b1 - tichete cadou (neimpozabil <=300 + semnal la >300), fiscal verificat  (06_ddl_cadou_eveniment.sql, beneficii_api.py)
DECIZIE: Faza 2b (cadou) spartita in 2b1 (neimpozabil, cazul comun) + 2b2 (taxare peste prag).
Se construieste 2b1: cadou <=300 lei/eveniment legal = NEIMPOZABIL (doar cheltuiala 642=5328, fara taxa,
fara D112), cu SEMNAL clar daca >300 sau eveniment nelegal (deferat la 2b2 - NU se trateaza tacit gresit).
TRATAMENT FISCAL 2026 (VERIFICAT LA SURSA): cadou neimpozabil <=300 lei/persoana/EVENIMENT, doar pt
evenimente LEGALE (paste, craciun, 8 martie, 1 iunie). Peste 300 sau alt eveniment: DIFERENTA (nu toata
suma) se taxeaza INTEGRAL ca salariu (CAS 25% + CASS 10% + CAM 2.25% + impozit 10%) - se adauga la brut.
DECIZII DE SCOP (confirmate de Costin): (a) doar 2b1 acum (neimpozabil + semnal), taxarea peste prag = 2b2
la caz real (rar, chirurgie pe calcul_salariu+D112). (b) coloana eveniment cu 4 legale + 'altul' (nelegal
-> taxabil). (c) plafon SIMPLU 300/salariat/eveniment - MULTIPLICATORUL per copil minor (300 x (1+copii))
NU se modeleaza in 2b1, se lasa pt 2b2/tema separata (minim viabil intai).
MODEL (step 1 LIVE): beneficii_lunare primeste coloana eveniment + unique extins (salariat,an,luna,tip,
eveniment) - un cadou per eveniment; vacanta ramane unica (eveniment=''). beneficii_api: seteaza cu
eveniment + validare, lista_luna agregat (SUM), cadou_detalii_luna (per eveniment + flag taxabil).
DE CE cadoul e diferit de masa/vacanta: taxarea peste prag = CA SALARIU (CAS+CASS+CAM, adaugat la brut),
NU pista paralela CASS+impozit. De aceea 2b2 e separat si amanat.
LIMITA: in 2b1, cadoul TAXABIL (>300 sau nelegal) se raporteaza cu semnal dar NU se taxeaza automat -
contabilul trateaza manual pana la 2b2. Cheltuiala (642) se inregistreaza pe valoarea totala.

### 20.07.2026 F134 plata salarii pe card - format SEPA/ISO 20022 pain.001 (fazat) + prereq IBAN salariat  (07_ddl_iban_salariat.sql, salariati_api.py, stat_plata_api.py, main.py, firme.js)
DECIZIE (STOP, format ales de Costin): fisierul de plata a salariilor pe card = SEPA / ISO 20022
pain.001.001.03 (SEPA Credit Transfer Initiation). NU format proprietar pe banca.
TEMEI: (a) standard PUBLICAT, verificabil la sursa (XSD ISO 20022/EPC) - regula de aur, nu ghicim structura
XML; (b) bank-agnostic: acceptat de importul corporate al bancilor RO pentru plati RON multiple -> UN singur
format, nu N parsere proprietare care se rup la fiecare banca; (c) formatele proprietare (BT/BCR/ING CSV) cer
spec-ul exact al fiecarei banci, unele fara sursa publica (ar rupe importul, ca argumentul BR-RO/Ciel).
ALTERNATIVA RESPINSA: CSV/TXT proprietar pe banca pilot - lock pe o banca, sursa incompleta/neverificabila.
FAZARE: step 1 (azi LIVE) = prerequizit IBAN salariat (coloana + API + UI + validare); step 2 = generatorul
pain.001 propriu-zis (validat pe XSD oficial procurat la sursa) + endpoint + buton pe stat de plata.
DISCIPLINA IBAN (step 1): un IBAN gresit trimite banii altcuiva -> se valideaza cifra de control (mod-97,
ISO 13616/ISO 7064) INAINTE de inserare, exact ca CUI/CNP (iban_valid in salariati_api, functie pura). IBAN
romanesc: RO + 22 caractere (24 total); optional (gol = fara plata pe card, semnalat pe stat "IBAN ⚠").
LIMITA: doar RON domestic (RO IBAN). Plati in valuta / IBAN strain = tema separata daca apare cazul real.

### 20.07.2026 F137 coduri COR pe contracte - nomenclator national validat la sursa  (08_ddl_cor_ocupatii.sql, cor_incarca.py, core/cor_api.py, salariati_api.py, main.py, firme.js)
DECIZIE: COR (Clasificarea Ocupatiilor din Romania) devine nomenclator VALIDAT (era free-text nevalidat).
Codul se alege dintr-o lista oficiala, se valideaza la salvare (inexistent -> respins), nu se mai tasteaza liber.
SURSA (STOP, procurare - data.gov.ro inaccesibil din mediul de build): Costin a descarcat fisierul OFICIAL
de pe data.gov.ro (dataset "Clasificarea Ocupatiilor din Romania", lista alfabetica, Ordin 573/180/2024,
MO 344/12.04.2024). ALTERNATIVA RESPINSA: copie GitHub neoficiala - sursa secundara, regula de aur cere oficialul.
Fisierul e un doc Word exportat "Flat OPC" XML; lista traieste in /word/document.xml ca paragrafe alternand
cod (6 cifre) -> denumire. Parsat de cor_incarca.py: 4422 ocupatii unice, toate 6 cifre (auto-validat, refuza
incarcarea daca structura difera). VERIFICAT LA SURSA - niciun cod inventat.
ARHITECTURA: nomenclator NATIONAL (acelasi pt toate firmele) -> tabel GLOBAL public.cor_ocupatii, NU per-tenant
(nu intra in tenant_template). Cautare diacritic-insensitiva (nume oficiale cu ă/î/ș/ț, user tasteaza fara) pe
coloana normalizata denumire_cauta. Endpoint GET /cor (orice user logat). Validare la creare+editare salariat
(_verifica_cor); import bulk ramane lax (date de migrare, ca inainte). REGES: cod + versiune 10 (COR 2010/ISCO-08).
LIMITA: nomenclatorul e un SNAPSHOT (Ordin 573/180/2024) - la un ordin nou de actualizare COR se reruleaza
cor_incarca.py cu fisierul nou. Fluxul REGES de AdaugareContract (care trimite codul) nu e inca cablat - cand va
fi, ia codul din salariatul deja validat. Editarea COR pe angajatii existenti = buton inline pe stat (nu exista
formular de editare salariat complet).

### 21.07.2026 F125 clasificare manuala D390 - RECLASIFICARE + adaugare (nu add-only)  (09_ddl_d390_clasificare.sql, d390.py, d390_clasificare_api.py, main.py)
DECIZIE (STOP, model ales de Costin): clasificarea manuala D390 = RECLASIFICARE a operatiunilor auto-derivate
+ ADAUGARE de linii pur manuale. NU add-only.
CONTEXT (constatat la sursa): d390.calcul_d390 mapeaza ORICE factura intracomunitara pe BUNURI (emisa->L,
primita->A). Pentru o firma cu facturi de SERVICII IC in sistem, ele-s numarate ca bunuri; daca s-ar adauga
si o linie P/S manuala pt acelasi partener -> DUBLA numarare.
ALTERNATIVE RESPINSE: (a) add-only (backend il suporta deja, minim) - dubla numarare cand serviciile-s
facturate prin aplicatie; (b) marcaj tip_d390 pe factura - cel mai curat conceptual dar atinge modelul de
facturi + fluxul de emitere = scop mai mare, amanat.
MODEL: auto ramane L/A implicit. Contabilul RECLASIFICA per (directie, partener) la un tip legal pentru acea
directie (emisa: L/T/P/R; primita: A/S) -> override in d390_reclasificare (inlocuieste tipul, NU adauga ->
fara dubla numarare). Plus linii pur manuale (P/S/T/R fara factura) in d390_manual. Ambele per tenant/an/luna,
PERSISTATE - ca toate caile care genereaza D390 (wizard, pachet, control incrucisat verifica_d390) sa vada
ACELEASI clasificari (d390.genereaza auto-trage din DB cand nu-s date explicit). Rezolva si nota veche din
control_incrucisat (P/S "raman v2").
VALIDARE: tranzitiile la sursa (achizitia nu poate deveni livrare si invers); codO obligatoriu pt L/T/P/R
(ca d390.valideaza). DOVADA: XML cu reclasificare (L->P) + linie manuala (S) = stare VALID pe DUK (d390),
fara erori. _facturi_ic extras ca sursa unica a filtrului IC (folosit de calcul_d390 + operatiuni_auto, fara dublura).
FAZARE: step 1 (azi) = model + calcul + API + endpoint + teste + DUK; step 2 = UI (ecran clasificare pe D390).

### 21.07.2026 F120 educatie AI pe tipare - strat generativ peste F094 (grounded, on-demand)  (tipare_api.py, ai_client.py, main.py, tipare.js)
DECIZIE: stratul AI generativ prevazut inca de la F094 (tipare_api docstring: "materia prima pentru viitorul
strat AI ... AI-ul (stratul 5) va citi exact aceste agregate"). Butonul "Genereaza analiza AI" pe ecranul G cere
lui Claude explicatii + recomandari concrete din agregatele deterministe de respingere.
MODEL (refolosire, NU paralel): core.ai_client existent - model ales DELIBERAT de proiect (claude-sonnet-4-6,
comentariu "echilibru calitate/cost pentru narativ"). NU l-am suprascris cu opus: alegerea de model e o decizie
deja luata in cod (ai_client + raportari_ai il folosesc); F120 e exact caz "narativ". Skill claude-api spune
default opus pt cod NOU, dar aici exista conventie stabilita = decizia userului.
GROUNDING (regula de aur pe AI): promptul da DOAR agregatele reale (motive/tipuri/firme din tipare()); sistemul
cere explicit "foloseste DOAR datele furnizate, nu inventa cifre/firme/motive". Verificat: analiza reala mentioneaza
CUI/CAS/firma din date, nu fabrica. Temperatura 0.4 (grounded, nu creativ).
ON-DEMAND (cost): apel platit -> NU se ruleaza automat la deschiderea ecranului, doar la buton. Fallback curat
(ai_client.disponibil()==False sau lipsa date -> mesaj, nu eroare). Doar patron (ca F094).
LIMITA: analiza e sugestie AI, nu verdict - contabilul o cantareste. Nu se persista (se regenereaza la cerere).

### 21.07.2026 F187 UI - butonul WinMentor CABLAT + drift de registru corectat  (facturi_ecran.js, FUNCTIONALITATI.csv)
CONSTATARE (audit vizual pe cele 4 ecrane post-14.07): F187 (export WinMentor) era LIVE in backend (export_winmentor.py
+ endpoint /facturi/export-winmentor, 11 teste, spec oficiala verificata) DAR butonul nu era cablat in frontend -
in tot static/js/ zero apariti "winmentor". Registrul (FUNCTIONALITATI.csv F187) afirma insa acces UI "Facturi
(buton export luna)" - un buton FANTOMA. Doua surse de adevar divergente: registrul zicea LIVE-cu-UI, realitatea
LIVE-doar-backend. Exportul era inaccesibil din aplicatie.
DECIZIE (Costin, varianta c): se cableaza butonul SI se aliniaza registrul, intr-un commit - realitatea devine
egala cu registrul (elimina drift-ul, nu doar il documenteaza).
IMPLEMENTARE: buton "Export WinMentor luna" langa "Export SAGA luna" in Istoric facturi. Pattern identic cu SAGA
(buton-secundar, fetch zip cu Bearer, download, 404->mesaj info, mesaj ok cu calea de import WinMentor) PLUS
feedback async cap.1 CORECT (dezactivare + "Se genereaza..." pe durata cererii - pe care butonul SAGA nu-l face).
Fara ICOANE noi (buton text), fara hex crud. Registrul F187 acces UI -> "buton CABLAT 21.07 langa Export SAGA".
DOVADA (regula de aur, prin fluxul butonului): flip temporar factura tenant_002 la status=emisa + diacritice ->
export prin URL-ul exact al butonului = HTTP 200 zip cu Facturi.txt + Articole.txt; encoding cp1250 valid;
ș/ț moderne -> cedila legacy (Denumire "Consultanţă ŞI mentenanţă", octeti cp1250, zero virgula moderna);
caracter neencodabil (emoji) -> 422. Factura restaurata, tenant_002 curat. node-check + verificator DS 0 nou.
LIMITA (neschimbata): round-trip real (import efectiv in WinMentor) ramane pending cabinet cu WinMentor configurat.

### 21.07.2026 F197 previzualizare portal client din cabinet - feature nou (decizie iunie neonorata, livrata)  (auth_api.py, main.py, sesiune.js, app.js, firme.js, portal.js)
CONTEXT: diagnostic la cerere - "Acces Client" preview (buton dashboard -> portal in tab nou, #acces, ruta acces-portal)
NU exista si N-A existat niciodata (git -S = zero); ce s-a construit in iunie sub nume asemanator = INVITATIA prin email
("Acces client", card in meniul firmei), mecanism diferit. Costin: construim acum feature-ul de preview.
DECIZIE (Costin, scop): buton in FISA FIRMEI (nu dashboard) -> portal client in TAB NOU, mod preview read-only.
RUTA NOUA POST /tenants/{id}/acces-portal, NU refolosire client-acces/portal-acces-cont. DE CE: alea-s pentru clientul
REAL (invitatie + auto-servire); preview e un mod DISTINCT (emis de cabinet, read-only, tab-local) - refolosirea ar
amesteca doua contracte de acces si ar risca sa dea clientului real capabilitati preview sau invers.
READ-ONLY PE BACKEND (critic): token marcat preview=True in payload -> middleware _preview_readonly_guard blocheaza
ORICE metoda mutanta (POST/PUT/DELETE/PATCH -> 403), GET permis. Guard la nivel de REQUEST, nu ascuns butoane in UI
(UI-ul se ocoleste - un client rau-intentionat cu tokenul ar putea POST direct). Singura aparare reala = pe server.
TOKEN IN-MEMORY (sesiune.intraPreview), NU sessionStorage: sesiunea cabinet (in tab-ul ei, sessionStorage izolat
per-tab din izolare_tab_v1) ramane intacta; tokenul preview nu persista la reload; logout in preview = window.close()
(inchide tab-ul, NU sterge sesiunea cabinet). #acces=<token> in app.js (regex accepta punctul - e JWT).
CONSTRANGERE: portalul rezolva firma prin user_tenants[uid] (_tenant_client) -> preview EMITE pentru un user client
REAL al firmei; daca firma n-are client invitat -> 400 cu indrumare la "Acces client". ALTERNATIVA (rol dedicat
preview-client fara user real) RESPINSA acum - ar cere gating nou peste tot (cere_client/_tenant_client/portal); minim
viabil = refolosire user client real + flag preview.
UI: buton "Previzualizeaza portalul" in ecranul Acces client (NU card nou - ar coliziona cu cardul "Acces client"
existent). Banner .caseta-info "Previzualizare - doar vizualizare" (DS cap.5: rosul e EXCLUSIV pt distructiv; preview =
info neutra -> albastru, nu caseta-atentie rosie, desi sugerata - "echivalent DS").
DOVADA: E2E autentificat - cabinet emite (200, preview=True), GET portal 200, POST mutatie 403, firma fara client 400.

### 21.07.2026 nginx: /static/ scutit de rate limit pe nou-iconta (regresie config, fals-alarma "bug preview")  (/etc/nginx/sites-available/nou-iconta - INFRA, nu repo)
SIMPTOM: pagina alba la incarcarea portalului pe prod (nou.iconta.eu), console HTTP 429 pe module ES (date_firma.js,
emitere_ecran.js etc.). Parea bug de preview - NU era: rate limiting nginx pe serving-ul static.
CAUZA (regresie de config): config-ul VECHI iconta avea "location /static/ { proxy_pass ... }" FARA limit_req (static
scutit); config-ul NOU nou-iconta (nou.iconta.eu) a PIERDUT acest bloc -> /static/ cadea sub "location /" = zona
iconta_gen (20r/s, burst 60), gandita pt API. Un SPA cere zeci de module ES in rafala per load (app.js -> ~10 importuri
-> firme.js trage ~10 ecrane = 30-50+ cereri); _StaticNoCache pune Cache-Control:no-cache -> revalidare la fiecare load;
preview-ul deschide TAB NOU -> dubla rafala. Bucket-ul de 60 se golea mai repede decat 20r/s -> 429 pe module -> alb.
DECIZIE: staticele se scutesc de rate limit (o singura pagina cere legitim zeci de fisiere; limita de brute-force n-are
ce cauta pe .js/.css). Adaugat "location /static/ { proxy_pass 127.0.0.1:8010; }" FARA limit_req, INAINTE de "location /"
(oglindeste config-ul vechi). Limita generala + auth (5r/m) raman neschimbate pt rutele reale.
PROCEDURA PROD (nginx = daca crapa, cade site-ul): backup (.bak-21iul) -> insert -> nginx -t (TRECE) -> reload (nu
restart, zero downtime) -> verificat 40 cereri rapide /static/js/app.js = 40x200, 0x429; API inca trece (401 pe /portal).
LIMITA/SECUNDAR (DE_FACUT): Cache-Control immutable pe asset-uri versionate ?v= ar taia si revalidarile (optimizare).

### 21.07.2026 F197 fix: preview portal spargea read-only (token in-memory fragil) -> token pe cheie sessionStorage  (sesiune.js, portal.js)
BUG CRITIC (Costin, test vizual): in preview portal a putut TRIMITE o solicitare (scriere client reusita) + bannerul
LIPSEA. Parea guard de securitate absent.
DIAGNOSTIC LA SURSA (regula de aur, reprodus): backend-ul e CORECT - POST /portal/solicitari cu token preview -> 403,
cu token client real -> 200. Guard-ul (_preview_readonly_guard) functioneaza. BUG-UL era in FRONTEND: bannerul lipsea
-> estePreview() era false -> intraPreview nu pusese tokenul preview -> tab-ul folosea alt token. CAUZA: override-ul
IN-MEMORY (let _tokenPreview) e fragil - se pierde la re-render/reload/instanta modul dublata; la pierdere, token()
cadea pe sessionStorage (tokenul copiat de window.open) -> non-preview -> mutatia trecea.
DECIZIE: tokenul preview trece de la IN-MEMORY la o CHEIE PROPRIE in sessionStorage (iconta_pv_token/pv_user).
sessionStorage e per-tab izolat (izolare_tab_v1) -> NU localStorage, sesiunea cabinet din tab-ul ei ramane intacta
(exact intentia initiala). Avantaj vs in-memory: DETERMINIST - supravietuieste re-render/reload; PRECEDENTA absoluta
in token()/user()/estePreview() -> tab-ul preview foloseste DOAR tokenul preview, niciodata tokenul real. Logout =
curata cheile PV + window.close. Backend-ul (guard) ramane backstop-ul: chiar daca frontendul ar gresi, tokenul
preview e read-only pe server.
BANNER: de la .caseta-info (albastru-pal, se putea rata) la .caseta-atentie (rosu, proeminent) - "PREVIZUALIZARE -
doar vizualizare", cerut vizibil. Aici rosul e justificat (semnaleaza mod restrictionat + actiuni dezactivate).
DOVADA: reprodus POST solicitari preview 403 / client 200; frontend determinist (cheie sessionStorage, nu in-memory).

### 21.07.2026 F197 — contextul de tenant al preview-ului trece prin URL, nu doar prin raspunsul rutei  (main.py acces-portal, static/js/app.js, firme.js)
DECIZIE: /tenants/{id}/acces-portal intoarce {token, user:{rol, nume_tenant, tenant_are_cabinet}}, iar
firme.js pune userul in URL-ul de deschidere (URLSearchParams: #acces=<token>&u=<json>); app.js il citeste si-l
paseaza la intraPreview. Fara asta, preview-ul fabrica {rol:"client"} minimal -> _eGratuit()=!undefined=true ->
cadea pe portalul gratuit (4 carduri) in loc de portalul client gestionat (Solicitari/Documente/Povestea).
TEMEI (verificare la sursa care a schimbat planul): diagnosticul initial cerea doar "ruta sa intoarca user +
app.js sa-l paseze". Dar grep pe firme.js:2792 a aratat ca preview-ul se deschide cu window.open(URL, "_blank") —
in tab-ul nou ajunge DOAR tokenul din URL, obiectul user din raspunsul POST ramane in tab-ul cabinetului. Deci
userul TREBUIE carat explicit prin URL, altfel app.js n-are de unde sa-l primeasca. Valorile confirmate pe endpoint
real (curl, tenant 2 DANTE): nume_tenant="DANTE INTERNATIONAL SA", tenant_are_cabinet=true (accounting_firm_id=1).
ALTERNATIVA RESPINSA: (a) sessionStorage copiat de window.open catre tab-ul nou — respins: pentru a fi citit de tab
opener-ul ar fi trebuit sa scrie cheile PV, ceea ce ar fi flipat si tab-ul cabinetului in preview (cab citeste
_pvUser() intai). (b) A baga nume_tenant in payload-ul JWT — respins: CLAUDE.md "minim necesar in token, fara nume".
(c) Endpoint nou GET /portal/eu apelat de tab-ul nou — respins ca surplus: valoarea e deja cunoscuta la emitere.
LIMITA: daca URL-ul e trunchiat (u lipsa/corupt), app.js cade pe fallback {rol:"client"} = portal client (nu gratuit),
degradare acceptabila. Guard-ul read-only (token preview -> 403 pe scriere) ramane backstop-ul; confirmat 403/200.

### 21.07.2026 F187-fix — WinMentor exporta facturile emise FARA filtru pe status (paritate cu SAGA)  (core/export_winmentor.py, main.py:5119)
DECIZIE: exportul WinMentor lunar nu mai impune status='emisa'; exporta toate facturile directie='emisa'
tip='factura' din luna, exact ca SAGA.
TEMEI (verificare la sursa, bug reprodus): DANTE iunie 2026 — SAGA descarca (200, zip), WinMentor da 404
"nicio factura emisa". Curl pe ambele rute, acelasi tenant/luna: SAGA 200/1521B, WinMentor 404. Cauza in DB
(tenant_002.facturi): cele 2 facturi emise (ALTEX, AUCHAN) au status='de_preluat', singurul status prezent.
export_winmentor.export_luna cerea facturi_emise_luna(status='emisa') -> 0 rezultate. 'emisa' ca STATUS nu se
seteaza nicaieri prin cod (grep: niciun SET status='emisa'); e doar param-default in semnatura creeaza_factura,
suprascris peste tot cu 'de_preluat' (facturi_api.py:197/309, main.py:4015 default, woocommerce.py:56). Deci
'de_preluat' = starea NORMALA a facturii emise (asteapta preluarea in contabilitate = chiar scopul exportului),
iar filtrul F187 excludea practic toate facturile reale. Testele F187 (11) treceau fiindca erau PUR unitare pe
functiile txt, fara DB — nu atingeau calea de query.
ALTERNATIVA RESPINSA: (a) a lasa filtrul si a "muta" facturile pe status='emisa' — respins: ar cere o tranzitie
de status inexistenta in flux si ar rupe SAGA-paritatea; premisa "de_preluat=neemisa corect" e falsa. (b) a filtra
status NOT IN ('anulata','storno') doar la WinMentor — respins: ar rupe din nou paritatea cu SAGA (care nu filtreaza).
LIMITA: NICIUNUL dintre exporturi (SAGA sau WinMentor) nu exclude azi 'anulata'/'storno' — DANTE n-are astfel de
facturi, deci nereprodus. Daca se doreste excluderea lor, e o schimbare UNIFORMA pe facturi_emise_luna (afecteaza
ambele exporturi) + un default nou — de decis separat, nu se strecoara in acest fix. Regresie: test_export_winmentor.py
+2 teste (status nefiltrat + factura de_preluat inclusa).

### 21.07.2026 Export contabil (SAGA+WinMentor) — NU se exclud facturile storno; se exporta TOT  (RESPINS deschiderea din F187-fix)
DECIZIE: exporturile catre programul contabilului (SAGA + WinMentor, prin export_saga.facturi_emise_luna)
raman FARA filtru de excludere storno/anulare. Se exporta toate facturile emise ale lunii, inclusiv notele
de credit (storno). Open item-ul "exclude anulata/storno uniform" (deschis chiar azi din F187-fix) = RESPINS.
TEMEI (verificare la sursa, care a rasturnat premisa):
  1. Facturile NU iau niciodata status 'anulata'/'storno' — singurele atribuiri de status in facturi_api.py
     sunt 'emisa' / 'de_preluat'; DB confirma doar aceste doua valori. Nu exista endpoint de "anulare" factura.
     Deci un filtru `status NOT IN ('anulata','storno')` ar fi COD MORT (exclude zero randuri) — patch fantoma.
  2. Stornarea nu traieste intr-un status: storneaza() (facturi_api.py:281) creeaza o factura NOUA cu linii
     negative + storno_din_id catre original; statusul ramane 'de_preluat'. "Exclude storno" ar insemna
     `storno_din_id IS NOT NULL`, adica ascunderea NOTEI DE CREDIT din export.
  3. Semantica contabila: un export de DOCUMENTE (nu un raport de solduri) trebuie sa contina toate documentele,
     inclusiv storno-ul. Daca originalul a fost exportat/inregistrat intr-o luna anterioara, ascunderea storno-ului
     ar lasa reversarea neinregistrata in programul contabil -> sold gresit. rapoarte_comerciale exclude storno
     doar pentru ca NETEAZA (sold = total - decontat + storno) — alta semantica decat un export de documente.
ALTERNATIVA RESPINSA: filtrul `status NOT IN ('anulata','storno') AND storno_din_id IS NULL` (ca in
rapoarte_comerciale_api.py:56-57) — respins pentru export: partea de status e moarta, iar `storno_din_id IS NULL`
ar introduce un bug contabil (nota de credit neexportata). Paritatea SAGA=WinMentor se pastreaza si asa (ambele
prin facturi_emise_luna fara filtru).
LIMITA: daca vreodata apare o functie reala de ANULARE factura (status='anulata' = document nul, nu doar reversat),
atunci DA se adauga excluderea — dar in facturi_emise_luna (un loc, ambele exporturi o mostenesc) si abia atunci,
la cazul real. Azi nu exista, deci nu se cara nedecis. Vezi si DECIZII 21.07 F187-fix (paritatea).

### 21.07.2026 F182 — cont venit implicit setabil din UI: doar clasa 70, nu toata clasa 7  (core/firma_profil_api.py, static/js/ecrane/date_firma.js)
DECIZIE: selectorul si validarea pentru cont_venit_implicit permit DOAR conturi din clasa 70 (cifra de
afaceri: 701/704/705/706/707/708), derivate din core/plan_omfp.PLAN_OMFP (sursa unica), nu toata clasa 7.
TEMEI (verificare la sursa): (1) coloana firma_profil.cont_venit_implicit + citirea la emitere existau deja
(main.py:5853, COALESCE(...,'707') -> facturi.factura_emisa(cont_venit=...)); F182 = doar UI+DB+validare, motorul
contabil NEATINS. (2) Un cont de venit pe o FACTURA DE VANZARE e din clasa 70 (venituri din exploatare - cifra de
afaceri). 74x (subventii), 76x (venituri financiare - dobanzi/curs), 78x (venituri din provizioane) sunt venituri,
dar NU se factureaza catre client -> a le oferi ca implicit la emitere ar produce o nota contabila gresita.
ALTERNATIVA RESPINSA: (a) camp text liber cu validare "incepe cu 7" — respins: ar permite 766/741 (venit, dar nu
de vanzare) + typos; selectorul din plan_omfp e sigur si arata denumirea. (b) toata clasa 7 — respins, motiv (2).
(c) hardcodarea listei in JS — respins: sursa e plan_omfp (CLAUDE.md: nu se hardcodeaza valori, se citesc din sursa).
LIMITA: planul OMFP din cod nu contine 702/703 (semifabricate/produse reziduale) - daca vreo firma le cere ca
implicit, se adauga in plan_omfp (un loc), selectorul le mosteneste. Azi 6 conturi acopera cazurile reale
(707 marfa / 704 servicii / 701 produse = defaults uzuale). Fallback 707, coerent cu COALESCE-ul de la emitere.

### 21.07.2026 F186 — raport coliziuni CUI: live read, report-only, in ecranul Facturare gratuita  (main.py /admin/coliziuni-cui, admin_gratuite.js)
DECIZIE: raport superadmin al coliziunilor CUI active (cont gratuit + firma cabinet pe acelasi CUI, ambele
activ=true). Live read (self-join la deschidere), report-only (fara actiune automata), sectiune in ecranul
Facturare gratuita existent.
TEMEI (verificare la sursa + DA gate cu Costin 21.07):
  - Detectia REUTILIZATA, nu rescrisa: acelasi match pe cifrele CUI (regexp_replace(cui,'\D','')) ca F092
    (tenant_provisioning.provision_tenant) si F185 (auth_api.inregistreaza_cont_gratuit). Semnalele lor sunt
    EFEMERE (doar la eveniment); F186 = vizibilitatea persistenta lipsa.
  - Suspendarea REUTILIZATA: ruta /admin/conturi-gratuite/{id}/suspenda exista deja; blocul de coliziuni o
    apeleaza pe contul gratuit (latura care poate emite dublu). Zero ruta noua de mutatie.
ALTERNATIVA RESPINSA (DA gate):
  - Materializat intr-un tabel coliziuni_cui: respins — setul e 100% derivabil din public.tenants curent;
    materializarea cere sincronizare (ce faci cand coliziunea se rezolva) -> drift. Live = zero drift, mai simplu.
  - Card nou dedicat: respins — coliziunile privesc conturile gratuite, stau langa ele (reutilizare buton
    suspendare); un card nou ar dubla surface-ul pentru ceva rar.
  - Actiune automata (suspendare la detectie): respins — GDPR signal-not-block, aceeasi disciplina ca F185/F092
    (inchiderea unui cont = decizie umana; superadmin decide).
LIMITA: privacy — raportul e pentru SUPERADMIN (Admin iConta), care vede oricum ambele laturi in panourile lui;
arata numele cabinetului. NU e acelasi caz ca F185 (unde REGISTRANTUL vede doar existenta, boolean). Un gratuit
poate coliziona cu mai multe cabinete -> mai multe randuri (corect). Vezi si DECIZII 18.07 (F092) / 19.07 (F185).

### 22.07.2026 F183 audit de preluare = motor SEPARAT, nu control_incrucisat pe luna de migrare  (core/audit_preluare.py; main.py GET /control-fiscal/{tid}/audit-preluare; static/js/ecrane/control.js; LIVE)
DECIZIE: auditul de preluare firma e un motor NOU (core/audit_preluare.py) care verifica COERENTA
INTERNA a pachetului preluat de la contabilul anterior - NU "acelasi motor control_incrucisat aplicat
la migrare" cum era conceput in DE_FACUT. Reutilizeaza doar ANATOMIA (3 stari verde=coerent /
rosu=divergent / gri=NEVERIFICAT + temei + remediu executabil/sugerat/investigatie) + reutilizeaza cod:
solduri_api.verifica_echilibru si solduri_parteneri_api.coerenta.
TEMEI (verificat la sursa 22.07, grep + citit control_incrucisat.py integral): control_incrucisat
compara doua surse INTERNE iConta - o declaratie GENERATA din iConta (d300/d112/d390.genereaza) vs NOTE
VALIDATE in iConta (rulaje_luna). La preluare NICIUNA nu exista: contabilitatea in iConta incepe DUPA
preluare, facturile istorice nu-s in sistem. Ruland control_incrucisat pe luna preluata rulaje_luna=0
-> rosu fals "necontabilizat" pe TOT. La preluare ambele surse sunt EXTERNE (documente de la contabilul
anterior); intrebarea nu e "declarat vs contabilizat" ci "pachetul preluat e coerent cu el insusi?".
Motoare separate care se cheama, nu se absorb (aliniat DECIZII 18.07 B). Nota din rip_migrare_api.py:204
anticipa deja F183 la preluare.
SCOP v1 (raspuns la DA gate, 3 intrebari - Costin):
  - LOCATIE: fisa firmei (Control fiscal > detaliu > buton "Audit de preluare"), repetabil oricand.
    RESPINS pas-final-in-flux-migrare: auditul e TRANSVERSAL peste straturi, nu un strat cu "gata verde",
    si trebuie re-rulabil DUPA migrare, nu doar in timpul ei.
  - VERIFICARI: (1) balanta echilibrata; (2) Sigma solduri parteneri = sold sintetic din balanta;
    (3) sold de deschidere pe cont fiscal fara declaratia care-l explica in istoric = SEMNAL gri (NU
    rosu automat - soldurile fiscale au cauze legitime); (4) RIP PFA sold implicit ne-negativ + operatiuni
    clasificate. Acopera ambele regimuri: partida dubla (SRL) + partida simpla (PFA).
  - PERSISTENTA: regenerare la cerere, raport datat cu momentul rularii. RESPINS tabel-snapshot: setul e
    100% derivabil din documentele importate; materializarea cere sincronizare la reimport -> drift
    (acelasi rationament ca F186 live-not-materialized).
ALTERNATIVA RESPINSA: a extinde control_incrucisat cu un mod "preluare" - respins: ar amesteca doua
intrebari diferite (declarat-vs-contabilizat vs coerenta-pachet-extern) intr-un motor si ar cere ramuri
"daca e preluare" prin toata logica de comparatie (regula "motoare separate", "nu construi paralel").
LIMITA: auditul verifica coerenta INTERNA a pachetului preluat, NU corectitudinea evidentei contabilului
anterior (RIP-ul preluat e punct de plecare, nu adevar garantat). NEVERIFICAT v1, ramas gri VIZIBIL (nu
tacut, prin lipsa checkului): asociati/cote (100% + capital 1012), mijloace fixe (valoare ramasa vs
21x-28x), salariati (421/431x), vector fiscal vs documente. Ce ar rasturna / extinde: audit D-vs-D real
la preluare cere persistarea randurilor declaratiilor depuse (acelasi blocant ca F163, capul sectiunii
in control_incrucisat). Aparare: core/test_audit_preluare.py (11 teste pe nucleele PURE).

### 22.07.2026 Formatare sume/date in BACKEND: canonice Python + garda pe .py  (core/pdf_util.py; verificator BACKEND_UI_BRUT; DESIGN_SYSTEM v2.15 cap.4)
DECIZIE: text destinat utilizatorului construit in Python (mesaj/temei/cauza/motiv/avert/descriere/
actiune, erori afisate, email, PDF) se formateaza prin SURSE CANONICE unice: pdf_util.bani (sume, deja
existent) + pdf_util.data_ro (date, NOU - oglinda Python a dataRo din api.js). O garda noua in verificator
(BACKEND_UI_BRUT) scaneaza fisierele .py si prinde sume/date brute in aceste campuri.
TEMEI (verificat la sursa 22.07): garzile DS (BANI_NEFORMATATI, DATA_DIALECT, DATA_BRUTA) scaneaza DOAR .js
(verificator_conformitate.py:27, os.listdir(BAZA) cu endswith('.js')). Backendul emitea text formatat care
ajungea la user si scapa COMPLET (dovada: F183 arata "40800.00 lei"; inventar - control_incrucisat avea 16
situri). Sursa canonica de date lipsea in Python (fiecare modul isi facea strftime propriu).
DECIZII DE DESIGN ale garzii (ca sa nu dea fals-pozitive - lectii platite):
  - SUME: flag doar f-string ({x} lei) si %-format (%d lei) - unde valoarea e pe linie. Sabloanele
    .format() (common.CODURI) NU se flag: sunt umplute CENTRAL in common.problema(), care aplica bani() pe
    campurile din MONEDA_CAMP. Un placeholder "{gasit} lei" fara prefix f e formatat la locul umplerii, nu
    la definitie. Orice camp monetar NOU intr-un sablon se adauga in MONEDA_CAMP (altfel randeaza brut).
  - DATE: flag DOAR strftime("%d...") = zi-intai = data pentru OCHI. isoformat() si strftime("%Y...") sunt
    ISO -> DATA/XML/JSON/log, NICIODATA display uman -> NU se flag (altfel ~15 fals-pozitive: campuri JSON
    API formatate client-side, timestamp de log, valori interne).
  - "%s lei" = string DEJA compus (lectia d300.py:273: _f formateaza deja cu separator de mii; a cere
    bani() pe el crapa cu ConversionSyntax). Nu se flag.
EXCEPTII documentate in garda: XML/SAF-T (etransport_send, d406 - ISO cerut de spec ANAF), export_winmentor
(format cerut de destinatie), valori unitare :g (tichet/plafon per-unitate), comentarii/docstring.
ALTERNATIVA RESPINSA: fix doar punctual, fara garda - respins: clasa reapare tacut (cum a intrat la F183).
Garda + canonice = clasa inchisa. RESPINS si a flag TOATE isoformat/strftime - ar ineca semnalul in
fals-pozitive (JSON API e corect sa trimita ISO, se formateaza client-side).
NORMA: DESIGN_SYSTEM v2.15 cap.4 (regula backend) + verificator BACKEND_UI_BRUT (gardian) - simultan, ca
orice norma noua. LIMITA: garda nu vede sume fara "lei" ({debit} ≠ {credit}) si nici template-uri umplute
necentralizat - de aceea common.problema centralizeaza. Reparate azi: control_incrucisat (16), common/d112/
taxare_inversa/main (sume), sinteza_zilnica/scadente/main (date). d300:273 = fals-pozitiv (deja formatat).

### 22.07.2026 F183 audit ramifica pe REGIM: PFA -> doar RIP, verificarile de partida dubla NU apar  (core/audit_preluare.py audit(); test_audit_preluare.py)
DECIZIE: audit() citeste tip_firma si ruleaza doar verificarile aplicabile regimului. La partida simpla
(PFA) ruleaza DOAR coerenta registrului RIP; verificarile de partida dubla (balanta, parteneri, istoric-
vs-solduri-fiscale) NU apar deloc. La SRL, invers: partida dubla ruleaza, RIP nu (gol prin definitie).
TEMEI (diagnostic la sursa 22.07, demo injectata-in-rollback pe tenant_002): auditul rula TOATE cele 4
verificari neconditionat, fara sa citeasca tip_firma. Pe un PFA (care N-ARE balanta prin definitie -
partida simpla, registru cronologic), verifica_balanta/parteneri/istoric intorceau gri "Balanta nu a fost
importata - importa balanta de deschidere". Adica un REMEDIU IMPOSIBIL: partida simpla nu are ce balanta
sa importe. Asta incalca contractul modulului (fiecare constatare = temei + limita + remediu ACTIONABIL);
un gri cu remediu care nu se poate executa e zgomot inselator, nu informatie.
DE CE "sare" si nu "nu se aplica" (optiunea A vs B la gate): un rand "nu se aplica - partida simpla" ar
rula tot verificarea (munca inutila) si ar adauga text pe ecran pentru ceva ce omul stie deja (a preluat
un PFA). Remediul imposibil e problema, nu invizibilitatea; se elimina la sursa (nu se ruleaza), nu se
comenteaza. Un PFA vede DOAR ce are sens pentru el.
SURSA UNICA a maparii regim->straturi: migrare_api.straturi_pentru(tip_firma) / STRATURI_META (solduri/
solduri_parteneri = 'dubla', rip = 'simpla'). Auditul NU redefineste ce regim are ce strat - il citeste de
acolo (o singura sursa, zero drift). Legatura audit->strat: balanta<->solduri, parteneri<->solduri_parteneri,
istoric-fiscal<->solduri (checkul are nevoie de balanta de deschidere pentru soldurile conturilor fiscale,
deci e partida dubla desi stratul 'istoric_declaratii' e 'ambele' - stratul e despre IMPORT, checkul despre
CORELARE cu balanta), rip<->rip.
ALTERNATIVA RESPINSA: (B) "nu se aplica" vizibil - respins (mai sus). (C) lasat cum e (doar diagnostic) -
respins de Costin: primul PFA real ar vedea gri-uri "importa balanta" derutante.
LIMITA: regimul se citeste din firma_profil.tip_firma; absent/necunoscut -> tratat 'srl' (partida dubla),
ca straturi_pentru. Aparare: test_audit_preluare.py::test_pfa_ruleaza_doar_rip_zero_importa_balanta (FakeConn
PFA: doar constatari RIP, zero "balanta"/"parteneri") + non-regresie pe cele 11 teste SRL. Verificat E2E pe
tenant_002 (rollback: tip_firma='pfa' + RIP injectat -> doar RIP; SRL neschimbat).

### 22.07.2026 Config lazy: convertite 15 din 19, cele 3 JWT raman la import  (common.cfg; observare/efactura/etransport/spv_conector; DE_FACUT item 5)
DECIZIE: din cele 19 env citite la nivel de modul, se convertesc la citire-la-apel (cfg) 15 + se sterge 1
mort (REVOKE_URL); raman intentionat la import 3 legate de JWT_SECRET (auth_api.SECRET, auth_api.DURATA_TOKEN_SEC,
spv_conector.STATE_SECRET). Nu 17 cate anticipa inventarul, ci 15+1: fisierul auth_api.py nu s-a atins deloc
in acest pas, deci si DURATA_TOKEN_SEC (sigur in sine) a fost amanat impreuna cu SECRET-ul din acelasi fisier.
TEMEI: verificare la sursa a tuturor 19 (grep pe fiecare constanta + unde e folosita valoarea). (1) Env inghetat
de systemd pe durata procesului -> citire-la-import == citire-la-apel bit-cu-bit; singura diferenta reala e
sub pytest/context programatic (item 4). (2) Niciun loc nu compara valoarea cu un snapshot inghetat (URL-urile
se folosesc doar la construit request; redirect_uri se trimite identic la /authorize si /token, ANAF il compara,
nu noi). (3) Niciun consumator EXTERN nu importa bindingul (`from spv_conector import CLIENT_ID` -> zero). (4)
REVOKE_URL declarat dar nefolosit nicaieri -> cod mort (regula "reparatie reala"), eliminat nu convertit.
ALTERNATIVA RESPINSA: (A) convertim toate 19 intr-un pas - respins de Costin: cele 2 JWT (SECRET+STATE_SECRET)
sunt sigure doar prin PROPRIETATEA deployment-ului (env inghetat), nu prin cod; castig zero (nimeni nu roteste
JWT_SECRET la cald), risc de forma catastrofala (semnare/verificare = TOATE sesiunile). Se trateaza separat, cu
test dedicat + DA gate. (B) convertim si DURATA_TOKEN_SEC acum (e sigur, int) - respins: ar cere editarea
auth_api.py, exact fisierul cu SECRET-ul sensibil, contra listei explicite de 4 fisiere; amanat cu el.
LIMITA: dovada e pe env inghetat de systemd - daca vreodata env s-ar schimba la cald (nu se intampla azi),
semantica citirii-la-apel difera de cea veche. Cele 3 ramase (STATE_SECRET in plus: state generat la /authorize
si verificat la /callback, cereri diferite potential peste restart) cer analiza proprie inainte de conversie.
Aparare: suita 438 verde dupa fiecare fisier + verificator DS 0 + dovada functionala (env setat DUPA import
schimba comportamentul). Norma traieste in docstring-ul common.cfg + comentariile de la fiecare punct de citire.

### 22.07.2026 F180 model: snapshot ANAF separat + live la salvare, compara scpTVA-vs-boolean  (firma_profil 2 coloane noi; anaf_api; control_fiscal_api; main rute regim-tva/vector)
DECIZIE: avertisment la editarea manuala a platitor_tva vs ANAF + constatare rosie in Control fiscal la
divergenta. Model ales: (1) 2 coloane noi in firma_profil - platitor_tva_anaf boolean + platitor_tva_anaf_data
date (snapshot ANAF, SEPARAT de coloana editabila platitor_tva); (2) live valideaza_cui DOAR la salvarea manuala
(o firma): reimprospateaza snapshot + avertizeaza la divergenta, SIGNAL-NOT-BLOCK (omul salveaza oricum, ca F185);
(3) prefill F188 populeaza si snapshot-ul; (4) Control fiscal compara OFFLINE platitor_tva vs snapshot: verde
(coincid) / rosu (difera, remediu=investigatie) / gri (fara snapshot sau ANAF necunoscut).
TEMEI: (a) F188 suprascrie ACEEASI coloana platitor_tva (main.py ~1000/1055) -> azi nu exista valoare ANAF de
comparat; fara coloana snapshot separata comparatia e imposibila. (b) /control-fiscal itereaza TOATE firmele
cabinetului (main.py:1902) -> apel ANAF live per firma acolo = N apeluri/pagina, latenta + rate-limit ANAF (max
1 req/sec, anaf_api) -> comparatia din Control fiscal TREBUIE offline pe snapshot. (c) VERIFICAT FISCAL LA SURSA
(apel live v9 raw pe CUI 14399840, 22.07): ANAF intoarce inregistrare_scop_Tva.scpTVA = boolean "platitor la
data interogarii" (deja incorporeaza istoricul; perioade_TVA = trail, nu valoare contradictorie); TVA la incasare
(RTVAI.statusTvaIncasare) si SplitTVA sunt fatete SEPARATE. Deci platitor_tva(local, bool) vs scpTVA(ANAF, bool)
= apples-to-apples, zero fals-pozitiv din granularitate. Snapshot stocheaza scpTVA + data, nu o aplatizare.
ALTERNATIVA RESPINSA: (2) snapshot-only fara live la salvare - respins de Costin: rosu permanent pe snapshot
vechi = fals-pozitiv care normalizeaza rosul (lectia test_spv_conector). (3) live-only fara coloana - respins:
neviabil in /control-fiscal (N apeluri/pagina). Blocare la salvare - respins: firma poate avea dreptate cu ANAF
in urma (mentiune tocmai depusa); rosul persistent din Control fiscal e nag-ul durabil, nu blocajul.
LIMITA: firma NEEDITATA niciodata dar la care ANAF s-a schimbat post-onboarding -> local==snapshot==verde pana
la o reimprospatare (live-la-salvare acopera doar cazul editarii). Reimprospatare periodica (cron F184-style) =
enhancement viitor, in afara scopului. ANAF jos la salvare -> snapshot ramane vechi, fara avertisment (degradare
acceptabila, declarata in limita constatarii). Aparare: teste pe control_fiscal_api (verde/rosu/gri) + pe rutele
de salvare (divergenta -> avertisment, ANAF jos -> fara) + FUNCTIONALITATI.csv F180.

### 22.07.2026 Garda integritate FUNCTIONALITATI.csv = TEST pytest, nu verificator  (core/test_registru_functionalitati.py)
DECIZIE: integritatea structurala a registrului se apara printr-un TEST in suita (nr campuri == header +
ID = F\\d+), NU printr-o regula in verificator_conformitate.py.
TEMEI: verificat la sursa - verificatorul NU are sys.exit (iese mereu 0) => e raportor de nits DS, nu gate;
nu exista hook pre-commit/pre-push, nu e in CI/Makefile => se ruleaza pe disciplina. Suita, in schimb, e
verde-obligatoriu => un rand malformat RUPE suita inainte de commit. Integritatea registrului e un INVARIANT
(registrul e baza de cunostinte a AI-ului F152/raportari_ai.py; un rand decalat face functionalitatea invizibila
pentru AI - dovedit F183: r[7] nu mai era "LIVE" -> exclus tacit din baza), nu o conventie de stil advisory.
Testul citeste cu csv.reader (utf-8-sig) EXACT ca raportari_ai.py, ca sa valideze ce vede EL.
ALTERNATIVA RESPINSA: (a) in verificator - respins: raporteaza, nu blocheaza (exit 0); ar mosteni disciplina
manuala. (b) al treilea check "Stare in vocabular {LIVE/PLANIFICAT/PARTIAL/RESPINS/AMANAT}" - RESPINS de Costin:
cupleaza la o lista extensibila -> o stare noua legitima ar da rosu fals; nu normalizam un rosu fragil (lectia
22.07, eliminarea rosului permanent). Doar cele doua checkuri zero-mentenanta, zero fals-pozitiv.
LIMITA: testul prinde decalaje structurale (nr campuri / ID mutat), NU o eroare semantica intr-un camp corect
plasat (ex. descriere gresita). Aparare: 2 teste + mutatie negativa dovedita (reintroducerea bug-ului F183 pe o
copie -> check nr-campuri PRINDE; rand N-campuri cu ID decalat -> check ID PRINDE). Suita 449 verde.

### 22.07.2026 F165 auditor schema tenant: detecteaza + SUGEREAZA SQL, NU aplica  (core/audit_schema.py + test_audit_schema.py)
DECIZIE: auditor care compara schema fiecarui tenant cu tenant_template.sql; detecteaza driftul si
EMITE SQL-ul de reparatie (corp migrare_*), dar NU-l aplica automat. Poarta = test in suita (pica la drift
template->tenant); CLI on-demand pentru inspectie pe prod. FARA auto-ALTER, FARA ecran superadmin.
TEMEI: (1) verificat la sursa - driftul CURENT e ZERO: tenant_001/002 conforme, link_plata/sursa_externa deja
backfill-uite; cele 6 "tip-diferit" din primul diagnostic erau fals-pozitive integral (numele schemei in
nextval, normalizat acum). Valoarea e PREVENTIVA, nu cleanup. (2) tenant_provisioning aplica template-ul integral
la tenantii NOI (consistenti prin constructie); driftul loveste doar EXISTENTII cand template-ul se schimba fara
un migrare_*. Convenția migrare_* repara, dar pe DISCIPLINA - nimic nu-l PRINDE mecanic (cazul link_plata). Poarta
converteste driftul tacut in rosu la dev. (3) Motorul construieste ref din template in ROLLBACK + introspecteaza
information_schema (filosofia DUK: lucrul real e judecatorul, nu parsare SQL de mana).
ALTERNATIVA RESPINSA: (a) AUTO-ALTER (aplica ADD COLUMN automat) - RESPINS de Costin: ar repara schema dar ar lasa
gaura in procesul de migrari (fix aplicat, decizie nedocumentata, nimic in git) = incalca "reparatie reala, nu
patch". Migrarea sugerata devine un migrare_* NUMIT, cu mirror in template, revizuit de om. (b) WHITELIST pe cele
2 tabele extra (d205_beneficiari, d301_operatiuni) ca sa nu dea rosu fals - RESPINS: cupleaza la o lista
extensibila (aceeasi lectie ca vocabularul de Stari, respins azi la garda de registru). In loc: poarta e STRICT pe
directia template->tenant (lipsa/tip/nullable = clasa link_plata); directia inversa (extra in tenant) = DOAR raport
informativ, nu pica -> zero whitelist de intretinut. (c) ecran superadmin (ca F186) - RESPINS: YAGNI (superadmin=
Costin, testul enforce la dev); CLI acopera inspectia pe prod. (d) auto-ALTER pe tip/NOT-NULL/DROP - exclus prin
design chiar daca auto-ALTER s-ar alege candva: ALTER TYPE poate trunchia/lock-ui, NOT NULL fara default esueaza pe
tabela cu date, DROP pierde date. Doar ADD COLUMN nullable/cu-default ar fi vreodata "sigur".
LIMITA: poarta compara data_type + is_nullable (ce a cerut Costin), NU precizia varchar/numeric si NU default-urile
(zgomot/fals-pozitiv). Char-length change (varchar(50)->(255)) nu e prins. Suggest-ul e best-effort (revizuit de om).
Aparare: 11 teste (9 pure compara/suggest + poarta reala + mutatie negativa din ref real) + dovada E2E (DROP
link_plata real pe tenant_002 in ROLLBACK -> drift HARD + SQL sugerat corect, tenant neatins). Suita 460 verde.

### 22.07.2026 F163v2 persistarea declaratiei depuse (xml + randuri jsonb) in public.declaratii_depuse  (migrare_declaratii_depuse_randuri.py + coada_api.py + main.py)
DECIZIE: la depunere se persista si XML-ul depus si `res` (randurile calculate, jsonb), nu doar metadatele
(tenant/an/luna/tip). Prerechizit pentru control D-vs-D real (D390<->D300 etc.) fara reparsare XML.
Cinci decizii de implementare, toate verificate la sursa:
1. MIGRARE PE SCHEMA PUBLIC (nu tenant): public.declaratii_depuse e GLOBAL. migrare_* clasic bucleaza schemele
   tenant_; aici un singur ALTER pe public (ADD COLUMN IF NOT EXISTS xml text, randuri jsonb). E prima migrare
   "ca lumea" pe public (precedentul era ALTER-ul lazy asigura_coloana_sursa - workaround fiindca migrare_* nu
   acopera public; vezi DE_FACUT). Coloane NULLABLE: depunerile istorice raman fara xml/randuri (nu fabricam).
2. `res` PASTRAT INTREG IN PAYLOAD, nu doar avertismente. Verificat la sursa: la main.py:2715 payload-ul retinea
   {xml, avertismente} si ARUNCA restul lui res (docstring adauga_in_coada:63 MINTEA - zicea "xml + rezultat",
   codul pastra doar avertismente; docstring corectat). Doar call-site-ul de DEPUNERE (2712) face enqueue ->
   acolo se adauga `randuri`; celelalte doua (2925 validare DUK, 2949 preview) NU persista (returneaza raspuns),
   deci nu li se adauga res (ar fi dead data in raspuns fara consumator).
3. SERIALIZARE asdict + default=str (coada_api.randuri_din_res): dataclass-urile de rezultat contin Decimal
   (sume fiscale) -> json.dumps crapa fara default=str (acelasi truc ca la calcul_hash). Decimal->str, round-trip
   valoric (Decimal(str)==Decimal, testat).
4. d112 -> randuri NULL, cu temei in cod, FARA refactor. Verificat la sursa: d112.genereaza intoarce
   (xml, avertismente) unde al 2-lea e o LISTA, nu un dataclass cu totaluri (isi tine agregatele in variabile de
   structura XML). randuri_din_res(lista) -> None. A-l face sa intoarca totaluri = decizie de arhitectura pe
   modulul validat DUKIntegrator = F181, NU se face aici (ar risca regresie pe declaratia cu cele mai grele
   cazuri - CM/part-time). NULL onest > totaluri fabricate.
5. JURNAL APPEND-ONLY, ON CONFLICT DO NOTHING PASTRAT. Verificat la sursa: PK=(tenant_id,an,luna,tip), INSERT cu
   ON CONFLICT DO NOTHING. D710 (rectificativa D100) e tip SEPARAT -> rand nou, coexista cu d100 (fara conflict).
   DAR re-depunerea ACELUIASI tip pe aceeasi perioada -> ignorata tacit (first-write-wins), deci xml/randuri raman
   cele initiale. Non-distructiv (nu suprascrie), dar nu capteaza rectificativa de acelasi tip.
ALTERNATIVA RESPINSA: (a) refactor d112 ca sa expuna totaluri - respins (F181, risc pe modul validat). (b) ON
CONFLICT DO UPDATE (ultima depunere castiga) - NU aplicat unilateral: schimba semantica jurnalului. (c) versionare
(PK + nr_depunere, istoric append-only al rectificativelor de acelasi tip) - PROPUSA, asteapta DA (schimbare de PK
= decizie de scop; DE_FACUT). Pana la DA: comportamentul actual pastrat exact, doar imbogatit cu xml/randuri.
LIMITA: rectificativa de acelasi tip pe aceeasi perioada nu-si persista xml/randuri (ON CONFLICT DO NOTHING) pana
la decizia de versionare. Aparare: 6 teste (randuri_din_res dataclass/d112-None, round-trip Decimal prin jsonb,
d112 NULL in DB, rectificativa non-distructiva, d710 coexista) + E2E prin marcheaza_depusa real (payload->coada->
depunere->declaratii_depuse, Decimal pastrat, TID sintetic curatat). Suita 466 verde + verificator DS 0.

### 22.07.2026 F163v2 varianta A: versionarea depunerilor (nr_depunere in PK + vedere "curente")  (migrare_declaratii_depuse_versiune.py + coada_api.marcheaza_depusa + 6 cititori)
DECIZIE (rasturna "ON CONFLICT DO NOTHING pastrat" din intrarea F163v2 de mai sus, care astepta DA): PK devine
(tenant_id,an,luna,tip,nr_depunere); marcheaza_depusa insereaza nr_depunere=MAX+1 (fara ON CONFLICT); "curenta"
= vederea public.declaratii_depuse_curente (DISTINCT ON per perioada, nr_depunere DESC). Cei 6 cititori de logica
(control_fiscal_api:313, documente_api, portal_api, pachete_api, audit_preluare:189, main.py:2025) trec pe vedere;
istoricul ramane in tabel. Cititorul de bookkeeping (istoric_declaratii_import_api:142, count WHERE sursa='migrare')
RAMANE pe tabel (numara importuri dupa sursa, nu "declaratii curente").
TEMEI: de ce A (versionare) si NU B (ON CONFLICT DO UPDATE): odata ce persistam VALORI (xml+randuri), first-write-
wins (sau last-wins fara istoric) devine FALS FISCAL - rectificativa D300/D390/D394 e practica normala; controlul
D-vs-D ar compara cu actul INLOCUIT, nu cu cel in vigoare, iar depunerea inlocuita ar deveni necitibila. Varianta A
pastreaza AMBELE (audit trail al depunerilor) + expune curenta prin vedere. Verificat la sursa: FARA FK spre
declaratii_depuse (PK refacut fara efecte referentiale); ux_coada_activa e partial (exclude 'depusa') deci
rectificativa se pune in coada dupa ce prima e depusa. ON CONFLICT ELIMINAT: PK-ul (cu nr_depunere) e garda la
cursa - doua depuneri concurente care calculeaza acelasi MAX+1 -> a doua pica pe PK (conflictul NU se inghite tacut,
cerinta explicita).
ALTERNATIVA RESPINSA: (B) ON CONFLICT DO UPDATE - respins (mai sus: pierde actul inlocuit, controlul minte).
(migrare INSERT sursa='migrare' ramane nr_depunere=1 default + DELETE-then-insert idempotent; coliziune cu o
depunere iconta pe acelasi (tenant,an,luna,tip,1) = pre-existenta si azi pe PK vechi, nu regresie - istoric de
dinainte de iConta nu se suprapune in practica cu depuneri iConta).
LIMITA: vederea da ULTIMA versiune; daca cineva vrea sa vada explicit o versiune anume, interogheaza tabelul cu
nr_depunere. Aparare: test versionare prin marcheaza_depusa REAL (2 randuri nr 1/2 cu xml/randuri proprii, vederea
da valorile NOI, initiala citibila in tabel) + 5 teste F163v2 pastrate. Suita 466 verde.

### 22.07.2026 [INFRA] GRANT CREATE ON SCHEMA public TO iconta_user  (decizie de infrastructura, nu de cod)
DECIZIE: iconta_user (user-ul aplicatiei) primeste CREATE pe schema public, o data, aplicat ca postgres.
CONTEXT: F163v2-versiune cerea ADD PRIMARY KEY pe public.declaratii_depuse = creare de index in schema public.
iconta_user DETINE tabelul (putea ADD COLUMN) dar n-avea CREATE pe schema public (PG15+ revoca implicit CREATE de
la PUBLIC pe schema public) -> "permission denied for schema public". Tranzactia a dat rollback curat (nimic stricat).
TEMEI: de ce GRANT (mecanism) si NU rulare one-off privilegiata (fiecare DDL public ca postgres): fara CREATE,
FIECARE migrare pe public ar cere un pas manual de superuser -> exact de acolo a venit ALTER-ul lazy asigura_
coloana_sursa (workaround in cod fiindca nu exista un mecanism curat). Tratam CAUZA: cu GRANT, migrarile pe public
sunt first-class ca app-user (dovada: migrare_declaratii_depuse_versiune a rulat CA iconta_user, nu ca postgres),
la fel ca tenant-migrarile. Asa se poate elimina workaround-ul lazy (facut: sursa mutata in migrare normala).
CONTRAARGUMENT considerat (PG15 search_path shadowing): revocarea CREATE de la PUBLIC pe public in PG15 tinteste
atacul in care un user ne-privilegiat creeaza obiecte in public care "umbresc" (shadow) functii/tabele apelate fara
schema calificata de alti useri -> escaladare. NU se aplica material aici: iconta_user NU e un rol ne-privilegiat
oarecare - DETINE deja toate tabelele din public si CREEAZA scheme tenant (are CREATE pe baza de date); nu exista
un al doilea rol de privilegiat mai mare pe care sa-l pacaleasca (postgres nu ruleaza cod app cu search_path pe
public al lui iconta_user). Riscul de shadowing e intra-rol, nu cross-rol. In plus e REVERSIBIL: REVOKE CREATE ON
SCHEMA public FROM iconta_user il anuleaza fara pierdere de date.
ALTERNATIVA RESPINSA: rulare one-off ca postgres pentru fiecare DDL public - respins (nu rezolva cauza; perpetueaza
workaround-urile lazy). LIMITA: daca politica de securitate cere separarea rol-app de rol-migrare, se creeaza un rol
de migrare dedicat cu CREATE pe public si app-user-ul ramane fara - refactor viitor, nu azi (un singur rol acum).

### 22.07.2026 [INFRA] Ownership mixt pe schema public -> migrari imposibile pe tabelele owned de postgres  (ALTER OWNER + curatare DDL runtime)
DECIZIE: tabelele din public trebuie sa fie toate owned de iconta_user, altfel orice ALTER/migrare viitoare pe
ele pica (GRANT CREATE ON SCHEMA public da voie sa CREEZI obiecte noi, dar NU sa ALTER-uiesti un tabel al altui
owner - asta cere ownership). ALTER OWNER TO iconta_user aplicat (ca postgres) pe: audit_log, alerte_fiscale,
alerte_emise (cele 3 raportate initial). Curatare aferenta a DDL-ului runtime pe public: (1) pachete_api.ensure_tabela
STEARSA (cod mort, zero apelanti; pachet_povestea e tabel de feature VIU - 5 rute /pachete/.../poveste - creat pe
cale non-cod, ramane in prod, DDL-ul lui reproductibil merge in infra/bootstrap_public.sql); (2) alerte_control_fiscal.
DDL_JURNAL (constanta-string + pas manual superuser) -> migrare_alerte_control_emise.py (migrare publica normala,
rulata ca iconta_user; comentariul "manual superuser" retras).
TEMEI: verificat la sursa - GRANT CREATE nu acopera ALTER pe tabel de alt owner (Postgres: ALTER TABLE cere sa fii
owner sau superuser). Ownership mixt = un subset de tabele public pe care app-user-ul nu le poate migra niciodata
-> exact cauza ALTER-urilor lazy/manuale de pana acum.
CONSTATARE NOUA (verificare \dt+ dupa cele 3): ownership NU e inca uniform. Public are 28 tabele, 17 owned de
iconta_user, si INCA 11 owned de postgres, negasite prin grep (n-au DDL in cod deloc): anunturi_cabinet, api_chei,
cor_ocupatii, curs_bnr_zilnic, metrici_sanatate, reges_chei, reges_mesaje, solicitari_client, spv_cui_acoperit,
spv_token, tokene_activare. Toate par tabele de feature vii. ALTER OWNER pe ele = actiune de prod dincolo de "cele
trei" raportate -> asteapta DA (nu se ating unilateral). Pana atunci: orice migrare viitoare pe aceste 11 va pica.
LIMITA: ownership-ul e stare de prod (nu git) - la fel ca GRANT-ul, intra in itemul bootstrap (DE_FACUT). ALTER
OWNER e reversibil. Aparare: verificare \dt+ (17/28 iconta_user dupa cele 3); migrare_alerte_control_emise ruleaza
OK ca iconta_user; suita verde + verificator DS 0.

### 22.07.2026 [INFRA] cont. — DA pe cele 11: public 100% iconta_user (rezolutia intrarii de mai sus)
DECIZIE (raspuns la STOP-ul de mai sus, "cele 3 erau esantionul, nu lista inchisa; intentia era ownership uniform"):
ALTER OWNER TO iconta_user aplicat pe TOATE cele 11 tabele ramase (anunturi_cabinet, api_chei, cor_ocupatii,
curs_bnr_zilnic, metrici_sanatate, reges_chei, reges_mesaje, solicitari_client, spv_cui_acoperit, spv_token,
tokene_activare). VERIFICAT si obiectele dependente (ALTER TABLE OWNER NU propaga la secvente/vederi): secvente
18/18 iconta_user, vederi 1/1 (declaratii_depuse_curente), zero obiecte non-iconta_user de orice tip (relkind
r/S/v/m/p). STARE FINALA: public = 28 tabele + 18 secvente + 1 vedere, 100% iconta_user, 0 postgres.
TEMEI: intentia era ownership uniform pe tot public (nu doar esantionul raportat). DOVADA FUNCTIONALA (nu doar
\dt cosmetic): ALTER TABLE ... ADD COLUMN IF NOT EXISTS ca iconta_user pe curs_bnr_zilnic + spv_token (2 din
fostele postgres-owned), in tranzactie ROLLBACK -> reusit, coloana de test disparuta la rollback. Migrarile
public merg acum pe orice tabel. LIMITA: e stare de prod, intra integral in bootstrap (DE_FACUT, lista completa).

### 22.07.2026 F163 D-vs-D real (D390 vs D300 depus) — a treia comparatie, deblocat de F198  (control_incrucisat.compara_d390_vs_d300 + verifica_d390)
DECIZIE: verifica_d390 capata o A TREIA comparatie (nu inlocuieste evidenta validata): D390 baza IC (L/A)
vs D300 DEPUS randurile R1_1 (livrari) / R5_1 (achizitii), citite din public.declaratii_depuse_curente.randuri
(persistate la depunere de F198). Functie-sora compara_d390_vs_d300 (PURA) + helper _d300_depus_randuri (citeste
depunerea curenta pe fereastra TVA). Findings-urile se adauga in `constatari` -> curg automat in stare + UI +
push F164 (verificator-agnostice, zero cod nou acolo).
TEMEI: F198 (persistarea `randuri` la depunere) a inlaturat exact blocajul documentat in capul sectiunii F163
(19.07): inainte, R1_1/R5_1 erau manual-only SI nepersistate -> un D300 reconstruit dadea mereu 0 (zgomot) sau
verde trivial (aceeasi sursa). Acum se citeste D300-ul EFECTIV DEPUS -> reflecta ce a declarat real contabilul
(inclusiv randurile manuale) -> comparatie legitima. Reguli (aceeasi directie ca v1, VIES mai autoritar):
D390>0 & D300 nu declara -> ROSU sugerat; cifre diferite (sau D300>0 & D390=0) -> GRI (decalaj exigibilitate,
NICIODATA rosu pe cifre); randuri NULL (pre-F198/import) sau zero D300 depus -> GRI (absenta nu e divergenta);
ambele 0 -> tacut. GARD pe ambiguitate (contabilul vede CAUZA, nu doar cifra): cheie R1_1/R5_1 absenta din
`randuri->R` (manual-only neintrodus) -> tratata ca 0 DAR temeiul spune explicit "R1_1 absent - randurile intracom
sunt manual-only".
ALTERNATIVA RESPINSA: a inlocui evidenta validata cu D-vs-D - respins (a treia sursa, nu substitut; evidenta
valida ramane, e alt unghi). Rosu pe cifre diferite - respins (v1: decalaj exigibilitate legitim).
LIMITA DECLARATA (registru + aici): dovada functionala e pe depunere d300 FABRICATA in ROLLBACK, NU pe date reale -
ZERO D300 depus vreodata prin app (toate 5 depunerile din prod sunt sursa='migrare', import istoric fara randuri).
Deci D-vs-D e corect ca LOGICA + citire, dar nedovedit pe o depunere reala pana cand prima firma depune un D300
prin flux. Aparare: 9 teste (7 pure compara_d390_vs_d300 pe cele 5 cazuri + achizitii + tacut; 2 DB _d300_depus_
randuri pe depunere fabricata) + E2E verifica_d390 pe tenant_002 (a treia comparatie curge, verde livrari + rosu
achizitii). Suita 475 verde + verificator DS 0.

### 22.07.2026 [PROD] Primul parcurs real al fluxului de depunere D300 (tenant_002) + F163 dovedit pe date reale
DECIZIE: s-a parcurs cap-coada, PE PROD (tenant de test), fluxul de depunere care nu fusese exercitat niciodata
(coada complet goala; toate cele 5 depuneri existente = sursa='migrare'). Doua mutatii de prod (autorizate de
Costin, dupa confirmare ca tenant_002 = TEST): (1) POST /eu/competente ca user 34 -> poate_pregati/valida/depune
= True (self-serve, legitim - adminul isi activeaza competentele); (2) depunere reala D300 pe tenant_002 2026/06
(perioada cu IC real: D390 L=5000, A=2000), cu manual R1_1=5000 / R5_1=2000 coerente -> coada 25 la_senior ->
aprobata -> depusa; declaratii_depuse are acum PRIMUL d300 cu sursa='iconta' + randuri populate (nr_depunere=1).
CONFIRMARE PRE-MUTATIE (pas 0): tenant_002 = DANTE INTERNATIONAL SA (CUI 14399840 = eMAG, date PUBLICE folosite ca
test; CLAUDE.md il declara firma de test); doar 2 tenanti (celalalt = entitatea proprie a cabinetului AMZUICA);
ZERO firma "Daniela" in sistem. Nu s-a atins istoricul fiscal al vreunui client real.
SEMANTICA 'depusa' verificata la sursa: marcheaza_depusa doar UPDATE stare + INSERT jurnal; spv_index ramane NULL
(nu s-a transmis nimic la ANAF); depus_la = timestamp intern. 'depusa' = stare interna de jurnal (patru-ochi), NU
transmitere confirmata la ANAF. Deci depunerea de test nu pretinde o depunere ANAF reala.
REZULTAT F163 pe date REALE: verde pe ambele (D390 5000/2000 coincid cu D300 depus R1_1=5000/R5_1=2000) - verdict
CORECT (coerent -> verde), consistent cu logica testului fabricat. LIMITA "dovada doar pe depunere fabricata"
(registru F163) SE RIDICA -> exista acum o depunere reala prin app cu verdict corect.
LIMITA/RAMAS: verdictul verde e pe o depunere COERENTA (introdusa de mine sa se potriveasca); divergenta reala
(rosu) ramane dovedita doar pe fabricat/E2E - o va confirma prima depunere reala unde contabilul uita R1_1. Fluxul
a fost parcurs O SINGURA data; fricțiunea de permisiuni (adminul default nu poate depune) = item DE_FACUT.

### 22.07.2026 tip declaratie = CHEIE de join, canonic LOWERCASE la stocare + CHECK  (control_fiscal_api, termene_api, audit_preluare, coada_api, istoric_import, migrare_declaratii_tip_lowercase, UI)
DECIZIE: `tip` (declaratii_depuse, declaratii_coada) e CHEIE DE JOIN, nu text de afisare -> O SINGURA forma la
stocare: LOWERCASE. Forma ANAF (uppercase) traieste in duk.CHEIE_DUK si se face .upper() DOAR la randare, nu in
coloana. CHECK (tip = lower(tip)) pe ambele tabele apara cauza (nu simptomul).
TEMEI (verificat la sursa, numaratoare aratata inainte de alegere): forma cu care codul LUCREAZA efectiv e
lowercase - dispecerul declaratii_api._DISPECER ({"d300":...}), duk.CHEIE_DUK are cheie lowercase -> valoare
uppercase (dovada explicita ca lowercase=intern, uppercase=extern/ANAF), scadente.py normalizeaza .lower(),
main.py:2689 .upper() e explicit "pentru afisare". Bug prins de prima depunere reala: app stoca lowercase
('d300'), import istoric .upper() ('D300'), semafor (declaratii_datorate) producea uppercase -> match esuat ->
depunerile prin app apareau NEDEPUSE. RESPINS varianta (a) normalizare la CITIRE: lasa datele inconsistente si
obliga fiecare cititor viitor sa-si aminteasca upper(); (a) e patch, nu cauza. RESPINS "jurnal uppercase" (minim
dar contrazice: tip e cheie interna, nu forma depusa - forma ANAF sta in CHEIE_DUK, nu in coloana).
VERIFICAT INAINTE de UPDATE (cerut): tip NU e cheie de dedup persistata / link / URL care s-ar rupe -
alerte_control_emise.verificator = nume verificatori (tva/d112/d390), notificari.link = string static, ruta
/declaratii/{tip} = generare (lowercase, dispecer). declaratii_coada avea deja 1 rand lowercase (CHECK OK).
CONSECINTA (blast radius, varianta 1 aleasa de Costin): stocare lowercase peste tot (istoric_import store,
declaratii_datorate, termene_api, audit_preluare CONT_DECL, marcheaza_depusa) - VALIDAREA istoricului ramane
uppercase (contra TIPURI_CUNOSCUTE = nomenclator ANAF), doar STOCAREA e lowercase; upper la RANDARE (3 motiv-uri
backend + 4 puncte UI: control.js, termene.js, activitate_cabinet.js; pachete.js NU - rz.tip e tip-rezultat, iar
"depuse" face deja .upper()). UPDATE 5 randuri migrare uppercase->lowercase + CHECK pe ambele tabele.
F163 _d300_depus_randuri filtreaza 'd300' lowercase = corect PRIN CONSTRUCTIE (CHECK-ul garanteaza, nu accidental).
LIMITA: TIPURI_CUNOSCUTE (nomenclator ANAF, uppercase) ramane forma de validare/display - nu e coloana, e constanta.
Aparare: suita 475 verde + verificator DS 0 + TEST FUNCTIONAL care justifica tema: semaforul pe tenant_002 2026/06
arata acum "D300 iun depusa 22.07.2026, la termen" (era 'urmarit/nedepusa'). node --check ESM pe 3 ecrane + restart activ.

### 22.07.2026 [PROD] Ramura PFA a auditului F183 parcursa real + limita ramificata pe regim  (audit_preluare + tenant_003 test)
DECIZIE: (1) creat tenant PFA de test prin FLUXUL REAL (POST /tenants tip_firma='pfa', CUI cu cifra de control
valida 42000774 calculata nu inventata) -> tenant_003; + 3 operatiuni RIP prin rutele reale (rip/operatiuni +
valideaza). RAMANE pe prod ca prima dovada reala a ramurii PFA (ca depunerea tenant_002, tenant de test). (2)
limita auditului + lista NEVERIFICAT RAMIFICATE pe regim: PFA vede DOAR ce-l priveste (coerenta registrului
incasari-plati + salariati/vector neverificate), NU termeni de partida dubla (balanta/parteneri/asociati/mij.fixe).
TEMEI: auditul comunica unui PFA concepte care nu exista in partida simpla = continut FALS la adresa lui, erodeaza
increderea in raport (nu cosmetic). Mecanismul de regim EXISTA (straturi_pentru/STRATURI_META) si se REUTILIZEAZA -
dar STRATURI_META are doar (strat, regim), NU textele; deci am adaugat maparea minima text<->strat (_VERIFICAT_DESC,
_NEVERIFICAT_V1) filtrata prin `straturi` (din straturi_pentru), NU un mecanism de regim nou (semnalat inainte, cf.
directivei). Descriptorul RIP reformulat sa nu mai contina "balanta" (chiar negat: era "fara balanta" -> "sold
implicit din Sigma incasari - Sigma plati") ca PFA sa fie PUR fara termeni SRL. (3) obs3: verifica_rip cu tabel dar
0 operatiuni validate -> GRI cu temei+remediu explicit ("importa registrul sau introdu operatiuni"), NU raport gol
(regula: fiecare verdict poarta motivatia, inclusiv griul).
ALTERNATIVA RESPINSA: text hardcodat cu ambele regimuri (continut fals la PFA). LIMITA/RAMAS: obs4 (categoria
'neclasificat' nu se poate adauga manual - _valideaza o respinge - deci gri-pe-neclasificat se declanseaza doar pe
date importate) = nota de reachabilitate in DE_FACUT, NEREPARATA.
Aparare: 15 teste audit (limita PFA fara termeni SRL + SRL cu ei + rip-gol->gri; aserție pe TEXT) + suita 477 verde +
verificator DS 0 + HTTP REAL pe ambii tenanti: PFA tenant_003 verde, ZERO termeni SRL in limita; SRL tenant_002 rosu,
toti termenii SRL prezenti (neschimbat).

### 22.07.2026 [SECURITATE] Default gol pe cheie HMAC = bypass complet de auth (tokenuri forjabile) — reparat pe 3 straturi
DECIZIE: eliminat default-ul gol de pe secretele JWT + garda dura la orice nivel. auth_api.SECRET si
spv_conector.STATE_SECRET (ambele = JWT_SECRET) citeau os.environ.get("JWT_SECRET", "") - default GOL - iar
nucleu.creeaza_token/verifica_token faceau hmac.new(secret.encode(), ...) FARA garda pe secret gol. Consecinta:
daca JWT_SECRET lipseste din env, app-ul pornea TACUT si semna/verifica tokenurile cu cheie HMAC goala (publica =
"") -> oricine forjeaza un token valid pentru orice uid/rol (inclusiv superadmin) = BYPASS COMPLET de autentificare.
REPARAT PE 3 STRATURI (aparare in adancime): (1) GRANITA CRIPTO - nucleu.creeaza_token + verifica_token ridica
ValueError la secret gol/None (nu semnam/verificam NICIODATA cu cheie goala, indiferent de apelant; verificat la
sursa ca astea sunt SINGURELE 2 functii de semnare/verificare cu secret - restul hash-urilor sunt de integritate/
parola, alta clasa); (2) cfg_secret in common - citire la apel cu EXCEPTIE DURA la absenta/gol, NICIODATA default,
pentru SECRET + STATE_SECRET; (3) FAIL-FAST la pornire - main.verifica_secrete_obligatorii ridica daca JWT_SECRET
absent -> app-ul REFUZA sa porneasca (nu ruleaza nesigur tacit). JWT_SECRET acopera si SECRET si STATE_SECRET
(acelasi env). DURATA_TOKEN_SEC -> lazy prin cfg (nu-i secret).
COMPLETARE la nota DECIZII 22.07 (config lazy, "cele 3 JWT raman la import"): rationamentul de atunci era despre
TIMING-ul citirii (import vs lazy) si "forma catastrofala daca s-ar schimba la cald" - NU despre default-ul gol.
Vulnerabilitatea (default "" pe cheie HMAC) era PRE-EXISTENTA si NU era pe radar; conversia lazy planificata a
scos-o la iveala la analiza. Deci nu era tema de config, era gaura de securitate.
VERIFICARE ALTE SECRETE (cerut inainte de reparatie): SPV_FERNET_KEY avea si el default gol DAR era deja gardat
(_fernet: if not cheie: raise EroareSpv) -> fail-fast, NU vulnerabilitate, neatins. Niciun alt secret cu default
gol negardat. Semnare/verificare cu secret = DOAR nucleu.creeaza_token/verifica_token (api_public sha256=cheie API,
password-hash scrypt, hash-uri de continut = alta clasa, fara secret de server).
ALTERNATIVA RESPINSA: normalizare/patch la citire - respins (e vuln, se elimina cauza: default-ul). LIMITA: azi pe
prod era MITIGAT doar fiindca JWT_SECRET E setat (api_keys.env) - dar codul permitea boot silentios-nesigur.
Aparare: 8 teste (secret gol la semnare/verificare -> exceptie; cfg_secret absent/gol -> exceptie; boot fara
JWT_SECRET -> refuz, test pe functie) + suita 486 verde + verificator DS 0 + PROD: restart normal (JWT_SECRET setat)
+ login real (emite+verifica cu cheia reala -> ok, ruta protejata 200).

### 22.07.2026 [INFRA/CORECTITUDINE] Fus orar = invarianta de provisionare (garda boot) + verdictele de zi in azi_ro()
DECIZIE: (a) garda de boot main.verifica_fus_orar - app-ul REFUZA sa porneasca daca OS TZ SAU PG timezone !=
Europe/Bucharest (langa verifica_secrete_obligatorii, aceeasi forma ca JWT_SECRET); (b) helper unic common.azi_ro()
(data in Europe/Bucharest) folosit DOAR in cele 3 puncte VERDICT-CRITICAL: control_fiscal_api._clasifica (azi,
lipsa vs urmarit), etransport_send.fereastra_uit (acum, UIT expirat/valabil), alerte_control_fiscal cron (azi,
ce declaratii sunt datorate) + extragerea PG a data_depunere cu AT TIME ZONE 'Europe/Bucharest' (verdictul
la-termen). Callerii semaforului din main (portofoliu + detaliu) trec pe azi_ro; 4441 folosea deja default-ul.
TEMEI (verificat la sursa, numaratoare aratata): NU era bug azi - server + PG ambele Europe/Bucharest (timedatectl
+ SHOW timezone), zero utcnow(); cele 10 now(timezone.utc) sunt aware-UTC pt durate/expirari/ISO extern (corect).
Riscul era LATENT si DUBLU: (i) date.today()/datetime.now() urmeaza OS TZ -> pe un server UTC verdictele Python ar
SARI ZIUA in fereastra 00:00-02:59 ora RO (dovada: depunere 28 iul 00:30 RO = 27 iul 21:30 UTC -> fals "la termen");
(ii) data_depunere (timestamptz) urmeaza PG timezone, NU OS TZ -> o nepotrivire OS<->PG ar face semaforul-`azi` (OS)
si data_depunere (PG) sa DEZACORDE pe cele doua laturi ale aceluiasi verdict. Tratam CAUZA (invarianta impusa la
boot) + robustete in cod pe punctele verdict.
DE CE DOAR PUNCTELE VERDICT-CRITICAL, nu toate cele 46 date.today(): restul e afisare/context (an/luna, feed,
antete) unde OS-TZ = Bucharest ajunge; conversia in masa ar fi zgomot + risc de regresie. Scop strict. CANDIDAT
NECONVERTIT semnalat (nu atins): termene_api.termene_firma (azi filtreaza termenele viitoare) - la limita verdict/
afisare, de decis separat.
ALTERNATIVA RESPINSA: doar (a) garda, fara (b) - respins: garda protejeaza doar la boot; daca ar fi cumva ocolita
(rol de migrare, container), verdictele Python ar sari ziua. (b) le face corecte indiferent. LIMITA: display-ul
"cu_ora" (datetime.now() in antete) ramane ora serverului (Bucharest, corect azi + impus de garda); browser-local =
decizie de display separata, low-prio (public romanesc).
Aparare: 12 teste (azi_ro in fereastra 00:00-02:59 nu sare ziua, in afara coincide; garda boot OS-UTC/PG-UTC ->
refuz, corect -> trece) + suita 490 verde + verificator DS 0 + PROD: restart normal (OS+PG=Bucharest), semafor
inca corect (D300 iunie confirmata prin azi_ro).

### 23.07.2026 F163 fereastra D-vs-D = ultima perioada cu D300 depus  (core/control_incrucisat.py: _d300_depus_recent, verifica_d390; commit la aceasta sesiune)
DECIZIE: sub-verificarea D390-vs-D300-depus isi alege propria fereastra = cea mai recenta perioada (per
tip_decont: luna/trimestru/semestru) pentru care EXISTA un D300 depus prin aplicatie, si RECALCULEAZA baza
D390 pe ACEA perioada. Ambele laturi = aceeasi perioada. Perioada evaluata se afiseaza explicit in verdict
("perioada 06/2026"), fiind alta decat restul ecranului (luna curenta).
TEMEI: verificare la sursa. D300 pe luna N se depune in N+1 (coada_api.py: luna persistata = ultima luna a
perioadei TVA - lunar->luna, trim->trim*3). Fereastra veche = luna curenta -> D300 al lunii curente nu e
depus NICIODATA la momentul verificarii -> F163 permanent gri in exploatare (dovedit: D300 iunie depus
22.07 nu era vazut, semaforul cerea D300 iulie inexistent). Confirmat functional pe tenant_002: verdictul
iese din gri si compara 06/2026 cu 06/2026 (L=5000 vs R1_1=5000, A=2000 vs R5_1=2000, coincid).
ALTERNATIVA RESPINSA (1): "ultimul D300 depus comparat cu D390 CURENT" - respins: ar compara perioade
DIFERITE (D300 iunie vs D390 iulie), un fals-pozitiv mai rau decat gri-ul, pentru ca arata rosu/divergenta
pe o nepotrivire care e doar decalaj de perioada, nu eroare reala. Corectitudinea cere aceeasi perioada pe
ambele laturi.
ALTERNATIVA RESPINSA (2): mutarea INTREGULUI F163 pe ultima perioada depusa (inclusiv D390-vs-evidenta) -
respins: D390-vs-evidenta compara doua surse LIVE (baza D390 din facturi + evidenta contabila validata),
mereu disponibile pe luna curenta; le muta inapoi ar pierde semnalul pe luna in lucru. D-vs-D compara o
sursa PERSISTATA (D300 depus, disponibil abia luna urmatoare). Disponibilitate diferita = fereastra
separata, nu una comuna. _fereastra_tva ramane neatins (folosit de latura live); D-vs-D are calcul propriu.
LIMITA: gri legitim daca firma n-a depus niciun D300 prin aplicatie (comparatia devine posibila dupa prima
depunere). Neverificat: servicii IC (P/S, d300 nu expune R3_1_1/R7_1_1), triangulatie. Ar rasturna decizia:
daca ANAF ar schimba periodicitatea de depunere D300 fata de perioada fiscala.

### 23.07.2026 F163/B verdictele UI nu se colapseaza la string in backend  (main.py bucla portofoliu; verificator_conformitate.py: VERDICT_COLAPSAT; static/js/ecrane/control.js: randA)
DECIZIE: o constatare/verdict destinat UI-ului se transporta STRUCTURAT (stare + eticheta + mesaj + TEMEI +
remediu; contractul control_incrucisat), niciodata colapsat la un string-eticheta in backend. Frontend-ul
randeaza printr-un renderer unic de anatomie (randA), fara cale paralela (bare-label eliminat).
TEMEI: verificare la sursa. main.py (portofoliu) colapsa constatarile la string ("solduri creditoare
trezorerie", "diferente stocuri", ...) -> in detaliul firmei apareau ca eticheta seaca, fara temei, spre
deosebire de D390/TVA/D112. Engine-ul PRODUCE deja temeiul (common.problema, constatare_regim_tva); se
pierdea la colapsare. Aceeasi clasa ca BACKEND_UI_BRUT (sume brute in text de backend, inchisa 22.07 F183),
alta forma: verdict, nu suma. Cauza, nu simptom: payload-ul duce constatarile intregi.
ALTERNATIVA RESPINSA: a lasa lista compacta de portofoliu (string-uri) si a adauga o a doua sursa
structurata doar pentru detaliu - respins: doua cai de randare pentru acelasi verdict = drift. O sursa
structurata, doua vederi (sumar de lista pe .eticheta, detaliu pe randA).
GARDA: verificator_conformitate.py categoria VERDICT_COLAPSAT - regula MECANICA: intr-o lista cu nume de
verdict (contabil|constatari|probleme|verdicte|findinguri), un element string LITERAL (append sau prim
element de list-literal) = colaps. O lista de string-uri legitima nu poarta nume de verdict (lista de alerte
de sistem din _verifica_si_alerta a fost redenumita `alerte`, nu carve-out in garda). Raport: 0.
LIMITA: garda prinde numele din setul curat; o lista de verdicte cu alt nume (ex. `rezultate`) ar scapa -
setul se extinde cand apare cazul. Nu prinde asezarea, doar colapsul la string.

### 23.07.2026 Culoarea de verdict deriva din nivelul motorului, nu din literal la randare  (core/common.py: stare_din_nivel; main.py bucla portofoliu; verificator: RE_FLAG_STARE_LIT)
DECIZIE: constatarea de afisare (_flag) NU-si mai alege culoarea ca literal. Culoarea deriva din nivelul
DECLARAT de motor, printr-o mapare UNICA (common.stare_din_nivel): BLOCANT -> rosu, AVERTISMENT -> galben,
absent/necunoscut -> gri. Motoarele care produc deja verdict-color (control_incrucisat, constatare_regim_tva:
verde/rosu/gri) trec prin passthrough (`.get("stare")`), nu prin mapare. Niciun literal de culoare la locul apelului.
TEMEI: verificare la sursa. verifica_trezorerie/verifica_balanta intorc nivel=BLOCANT ("nu se poate
depune/contabiliza", common.py:59). Reparatia B (F163) colapsase trezoreria la _flag("galben",...) - un
literal ales la randare care SLABEA un BLOCANT (sold creditor pe 5121 = imposibilitate contabila certa) la
"de urmarit". Culoarea corecta deriva din nivel: BLOCANT -> rosu.
DOUA AXE, NU SE IMPRUMUTA CULORI:
 (a) SEVERITATEA CONSTATARII = nivelul motorului (BLOCANT/AVERTISMENT/absent) -> dot-ul constatarii in detaliu.
 (b) ESCALADAREA PASTILEI-FIRMA = semaforul din lista de portofoliu (verde->galben "de urmarit" pe trezorerie,
     ca o firma cu un 5121 negativ sa nu apara integral rosie in overview). Ramane neatinsa, pe axa ei.
 Consecinta acceptata: firma poate avea pastila GALBEN in lista SI o constatare cu dot ROSU in detaliu -
 granularitati diferite, corect. Galbenul e stare de PASTILA-FIRMA, nu de constatare; modelul de constatare
 ramane verde/rosu/gri (galbenul apare la constatare doar daca un motor declara explicit AVERTISMENT).
NIVEL ABSENT = GRI, NU SE INVENTEAZA (doua GAP-uri semnalate, decizie de fond inainte de a adauga nivel):
 - verificare_stocuri: {conturi, ok, nota} fara nivel; nota admite cauze legitime (note ciorna nevalidate,
   operatiuni in afara fiselor CV) -> gri ("nu pot verifica") e corect semantic. Probabil NU cere nivel.
 - intrastat_praguri: status (sub_prag|atentie|depasit) fara nivel common. status='depasit' e severitate
   REALA si neambigua (cumulat >= prag), iar pastila-firma e deja escaladata la rosu -> constatare gri langa
   firma rosie = nepotrivire care SEMNALEAZA gap-ul. Candidat serios pt nivel=AVERTISMENT in motor
   (obligatie de declarare INS, "legal dar riscant", nu BLOCANT). DE DECIS cu Costin inainte de a-l adauga.
ALTERNATIVA RESPINSA: a mapa status Intrastat->culoare la randare (depasit->rosu) - respins: ar fi exact
anti-pattern-ul reparat (constatarea isi alege culoarea la randare, printr-un map bespoke). Severitatea se
declara in MOTOR, randarea doar deriva/passthrough.
GARDA: verificator RE_FLAG_STARE_LIT (categoria verdict_colapsat, tag "stare-literal") - _flag() cu literal
"rosu"/"galben"/"verde"/"gri" ca prim arg = colaps. LIMITA: ancorat pe helperul de afisare `_flag(`. O regula
generala "orice literal de culoare in stratul de agregare" NU e exprimabila mecanic: un motor care isi
DECLARA verdictul (audit_preluare `_c("verde",...)`, control_incrucisat `stare="rosu"`) e legitim, iar sintaxa
nu separa "motor declara sursa" de "agregator recoloreaza upstream". Ancoram pe numele constructorului de afisare.

### 23.07.2026 Intrastat: nivel=AVERTISMENT (nu gri, nu BLOCANT)  (core/intrastat.py: NIVEL_STATUS; main.py: intrastat_praguri.nivel)
DECIZIE: depasirea/apropierea pragului Intrastat = constatare de nivel AVERTISMENT (galben prin
stare_din_nivel). Motorul (intrastat.analiza_flux) declara nivelul din status: depasit -> AVERTISMENT,
atentie(>=80%) -> AVERTISMENT, sub_prag -> None. Inlocuieste gri-ul interimar de la reparatia de mapare.
TEMEI: verificare la sursa (core/intrastat.py:1-6, Ordinul INS 1604/2025, MO 1022/05.11.2025). Prag 2026 =
1.000.000 lei/flux (introduceri/expedieri separat). Obligatia de declarare lunara la INS (intrastat.ro,
coduri NC8) incepe cu LUNA in care cumulatul de la inceputul anului depaseste pragul.
DE CE AVERTISMENT si NU GRI: gri inseamna "nu pot verifica" (incertitudine). Dar verificarea A DETERMINAT
ceva concret: cumulatul a depasit pragul, obligatia exista. Gri ar fi o minciuna - ascunde un fapt stabilit.
Situatie determinata, nu absenta de date.
DE CE AVERTISMENT si NU BLOCANT (rosu de severitate): BLOCANT = "nu se poate depune/contabiliza"
(common.py:59). Depasirea pragului NU impiedica nimic in iConta - contabilizarea si depunerile ANAF merg
normal. Naste o obligatie EXTERNA, la alta institutie (INS), nu la ANAF. Definitia AVERTISMENT ("legal, dar
riscant", common.py:60) se potriveste exact: legal sa continui, dar ai o obligatie de declarare de onorat.
ATENTIE (80%) tot AVERTISMENT: obligatia e iminenta, nu inca activa, dar "riscant" (esti pe cale sa o nasti).
Nu gri (85% e determinat), nu un nivel propriu (common are doar BLOCANT/AVERTISMENT).
MECANISM: nivelul se declara in MOTOR (intrastat.NIVEL_STATUS), randarea doar deriva culoarea (stare_din_nivel)
- coerent cu decizia "culoarea nu se alege la randare". Consecinta: constatarea Intrastat trece de la gri la galben.
LIMITA / DE DECIS SEPARAT: escaladarea PASTILEI-FIRMA (semafor lista) ramane pe rosu la Intrastat
(main.py: r["stare"]="rosu") - axa separata, neatinsa. Rezulta firma cu pastila ROSIE si constatarea GALBENA
(AVERTISMENT): mismatch in directia inversa fata de trezorerie (unde firma era mai putin severa). De decis cu
Costin daca pastila-firma la Intrastat ar trebui coborata la galben acum ca severitatea reala e AVERTISMENT.
Ar rasturna decizia de nivel: daca INS ar face declararea blocanta pt vreo operatiune ANAF (nu e cazul azi).

### 23.07.2026 Pastila-firma nu poate depasi severitatea maxima a constatarilor  (core/common.py: pastila_firma; main.py bucla portofoliu)
DECIZIE: pastila-firma din semaforul de lista = ESCALADARE, calculata INTR-UN SINGUR loc (common.pastila_firma)
ca severitatea MAXIMA intre starea de baza (declaratii) si constatarile firmei. Nu poate depasi max(constatari).
Inlocuieste cele 5 escaladari inline imprastiate (balanta/trezorerie/cross-checks/stocuri/Intrastat), fiecare
cu literal "rosu"/"galben". gri (necunoscut) NU escaladeaza; base 'gri' se pastreaza daca nimic confirmat nu urca.
TEMEI: rosu pe lista = "intra, e blocant". Daca inauntru e doar avertisment, lista MINTE. Un contabil care
invata ca rosul minte va ignora si rosurile reale -> supra-escaladarea erodeaza increderea in intreg semaforul.
Pastila e un rezumat al constatarilor de sub ea; nu poate spune mai mult decat spun ele.
CONSECINTE (mecanism uniform, nu doar Intrastat - cf. cererii "nu repara doar cazul Intrastat"):
 - Intrastat (AVERTISMENT) -> pastila GALBEN (era rosu literal). Cazul care a declansat.
 - Trezorerie (BLOCANT) -> pastila ROSU (era galben). Un sold creditor pe 5121 e blocant; pastila galben
   ASCUNDEA un blocant din lista (sub-escaladare la fel de nesincera ca supra-escaladarea).
 - Stocuri (gri, fara nivel) -> NU mai escaladeaza (era verde->galben). "Nu pot verifica" nu face firma
   problematica pe lista; ramane in detaliu.
RASTOARNA PARTIAL decizia "23.07 Culoarea de verdict deriva din nivel" (paragraful "DOUA AXE": acolo pastila
si constatarea erau tratate ca axe INDEPENDENTE, cu firma galben + constatare rosu acceptata). Corectie: axele
se CALCULEAZA distinct (constatarea din nivel motor; pastila din max constatari), dar sunt LEGATE prin max -
pastila nu e independenta, e marginita de constatari. Restul acelei decizii (culoarea nu se alege la randare,
mapare unica nivel->culoare) ramane.
ALTERNATIVA RESPINSA: a lasa pastila ca axa libera (escaladari per-verificator cu literal) - respins: produce
exact minciuna de mai sus si e imprastiata, imposibil de rationat unitar.
ALTA ESCALADARE CU LITERAL SEMNALATA (neatinsa, cf. cererii de a raporta, nu repara): control_fiscal_api.py:331
`stare = "rosu"` (regim TVA vs ANAF, in evalueaza_firma). NU e supra-escaladare (e conditionata de constatarea
regim rosu, deci EGALEAZA severitatea ei) si e oricum acoperita downstream de pastila_firma. Dar e un literal
in evalueaza_firma, care e folosit SI de ecranul de detaliu (unde pastila_firma nu se aplica). De decis cu
Costin daca evalueaza_firma trece si ea pe pastila_firma (unificare deplina) sau ramane sursa proprie a
starii de declaratii. LIMITA: _stare(lipsa,urmarit) din control_fiscal_api NU e vizat - acela e SURSA axei de
declaratii (lipsa=restanta=rosu), nu o escaladare peste constatari.

### 23.07.2026 evalueaza_firma escaladeaza prin pastila_firma (un singur loc pt severitate)  (core/control_fiscal_api.py:331; verificator: RE_STARE_SUBSCRIPT_LIT)
DECIZIE: escaladarea starii firmei in evalueaza_firma (regim TVA vs ANAF) trece de la literal
(`if regim=="rosu": stare="rosu"`) la common.pastila_firma(stare, [regim_tva_anaf]) - severitatea vine din
constatare, un SINGUR loc unde se decide. Inchide "poarta al saselea caz de maine": "e oricum acoperit
downstream de pastila_firma in bucla de portofoliu" era adevarat, dar lasa o escaladare literala paralela.
TEMEI: un singur loc unde se decide severitatea > redundanta corecta azi. _stare(lipsa,urmarit) NU e atins -
e SURSA axei de declaratii (lipsa=restanta=rosu), nu escaladare peste constatari (corect identificat de Costin).
GARDA: verificator RE_STARE_SUBSCRIPT_LIT (regula sora cu RE_FLAG_STARE_LIT) - prinde mutatia `x["stare"]="lit"`
(forma de agregator, ca vechea bucla). LIMITA (nu e exprimabila mecanic pt forma plain): `stare = "rosu"` simplu
e folosit LEGITIM de motoarele care isi calculeaza verdictul propriu din constatari (control_incrucisat:346/381/
720+, audit_preluare:349, forma `stare = "rosu" if any(...) else ...`), sintactic identic cu o escaladare gresita.
O regula pe forma plain = numai fals-pozitive. Se prinde doar forma subscript; forma plain ramane aparata
arhitectural (pastila_firma = singura escaladare de entitate), nu mecanic.
LIMITA / FINDING SEMNALAT (neatins, cf. cererii): ecranul de DETALIU (main.py:2021 control_fiscal_detaliu)
foloseste r["stare"] din evalueaza_firma, care vede DOAR declaratii + regim - NU constatarile contabile
(balanta/trezorerie/stocuri/Intrastat/cross-checks, calculate doar in bucla de portofoliu). Ataseaza
verificari_contabile dar NU recalculeaza r["stare"]. Consecinta: headerul de detaliu ("DANTE · la zi", plus
bannerul "Totul depus la zi" pe d.stare=="verde") poate CONTRAZICE o constatare rosie (ex. trezorerie BLOCANT)
afisata dedesubt, si poate diferi de pastila din lista (care le include). Cauza: contabilul se construieste
in bucla de portofoliu, nu intr-o functie partajata cu detaliul. Fix real = extragerea construirii contabilului
intr-o functie unica, folosita de AMBELE (lista + detaliu), apoi pastila_firma pe ea. DE DECIS cu Costin (nu reparat).

### 23.07.2026 Construirea `contabil` = functie partajata lista+detaliu; headerul de detaliu reflecta constatarile  (main.py: _construieste_contabil; control_fiscal_detaliu; control.js)
DECIZIE: constatarile contabile ale unei firme se construiesc INTR-UN SINGUR loc (main._construieste_contabil),
folosit de LISTA (portofoliu) SI de DETALIU. Ambele aplica pastila_firma pe rezultat. Headerul de detaliu
(d.stare) include acum constatarile contabile (trezorerie/stocuri/Intrastat/balanta/cross-checks), nu doar
declaratii + regim. Frontendul de detaliu foloseste d.contabil (proaspat) in loc de firma.contabil (snapshot
de lista) - header si body din ACELASI calcul, nu se pot contrazice.
TEMEI: header "la zi" + banner verde "Totul depus la zi" peste o constatare BLOCANT (trezorerie 5121 creditor)
e cea mai grava forma de minciuna - contabilul inchide ecranul multumit, cu un blocant nevazut. Severitatea se
calculeaza intr-un singur loc, din constatari reale, indiferent cine intreaba (lista sau detaliu).
COST (verificat inainte, cf. cererii): calea de detaliu rula DEJA _verificari_contabile (partea grea -
regenereaza D300/D112/D390). Functia partajata adauga pe detaliu doar verificare_stocuri (O(articole) query-uri
usoare) + intrastat_praguri (1 query). Marginal, nu incetineste detaliul.
VERIFICAT FUNCTIONAL: tenant_002 (SRL) - headerul include acum [rosu] Solduri creditoare trezorerie (BLOCANT);
tenant_003 (PFA gol: 0 articole/facturi/note) - ZERO constatari contabile, nicio scurgere SRL-only. Testul
test_header_nu_poate_fi_verde_cu_blocant_dedesubt incarneaza regula (baza verde + BLOCANT -> header rosu, nu verde).
ALTERNATIVA RESPINSA: a lasa detaliul sa recalculeze doar r["stare"] fara constatarile complete, sau a-l lasa
sa citeasca firma.contabil din lista - respins: prima nu vede stocuri/Intrastat; a doua leaga detaliul de un
snapshot de lista (staleness + doua surse). O functie, o severitate.
LIMITA: azi_ro() folosit si in detaliu (era date.today() - ora serverului), consistent cu portofoliul.
_construieste_contabil inghite exceptiile per-verificare (try/except) - un verificator picat -> constatarea lui
lipseste tacit din pastila (aceeasi filozofie ca inainte: un esec izolat nu doboara semaforul). E acceptat, dar
notat: daca un verificator ar pica sistematic, firma ar parea mai curata decat e. De monitorizat.

### 23.07.2026 Excepția înghițită pe o cale de verdict = minciună prin omisiune; gri e răspunsul corect  (main.py: _verificator_esuat, _construieste_contabil)
DECIZIE: cele 3 `except: pass` din _construieste_contabil (verificari contabile / stocuri / Intrastat) devin
constatare GRI cu temei explicit ("Nu am putut verifica X" + eroarea), nu tacere. GRI nu escaladeaza pastila_firma
(rezistenta se pastreaza - un esec izolat nu doboara semaforul), dar il anunta pe CONTABIL, care decide.
TEMEI: un verificator care CRAPA nu e "nimic de raportat" - e "nu am putut verifica", exact definitia griului.
Excepția înghițită face firma să pară mai curată decât e = minciună prin omisiune. Telemetria ma anunta pe MINE;
griul il anunta pe CONTABIL. Doua straturi, in ordine: GRI = principal (main.py _flag_constatare("gri",...));
LOG = secundar (_LOG_VERDICT "iconta.verdict".warning, sa se vada daca un verificator pica SISTEMATIC - journalctl
-u iconta-nou | grep "verificator esuat"). Telemetria dupa gri, nu in loc de.
ALTERNATIVA RESPINSA: telemetrie ca solutie principala - respins de Costin: ma anunta pe mine, nu pe cel care
vede ecranul. Contabilul trebuie sa vada "nu am putut verifica", nu sa creada ca e curat.
ALTE EXCEPTII INGHITITE PE CAI DE VERDICT (raportate, cf. cererii - NEreparate fara decizie):
 DEJA CORECTE (gri-on-except, modelul aplicat acum): control_incrucisat.py:327/364/678/714/787/801 (verificatorii
  isi intorc gri cu cauza la except) + main.py:3692 (_incrucisat wrapper -> gri). Nimic de facut.
 SILENTIOASE, DE DECIS:
  - main.py:3717 (documente_pozate) si 3734 (d205_vs_457) in _verificari_contabile: `except: pass`. Pe calea de
    verdict, dar momentan NEsurfacate in contabil/pastila (atasate la verificari_contabile, nefolosite de semafor).
    Un esec acolo omite tacit sub-rezultatul. Severitate mai mica (nu minte pastila azi), dar tot tacere.
  - audit_preluare.py:315 (_tip_firma -> None la except): ingusteaza tacit ce verificari de audit ruleaza (o firma
    cu tip_firma necitibil primeste mai putine verificari, fara gri). Cale de verdict (audit F183).
  - control_incrucisat.py:809 (`continue` pe cota_tva neparsabila): sare o LINIE de factura din verificarea cotei.
    Skip la nivel de date, severitate mica, dar o linie malformata scapa tacit de verificare.
LIMITA: log-ul depinde de configul de logging al uvicorn (propagare la root). Numele "iconta.verdict" e stabil
pentru grep. GRI nu depinde de log - e in payload, il vede contabilul indiferent de telemetrie.

### 23.07.2026 Trei forme de tacere pe cai de verdict, trei raspunsuri  (audit_preluare; main.py; control_incrucisat)
DECIZIE: tacerea pe o cale de verdict nu are un singur remediu - depinde de NATURA ei:
 (1) VERIFICARE PICATA (crapa in rulare) -> GRI cu temei. _construieste_contabil (tura anterioara) + acum
     documente_pozate (main.py:3717) si d205_vs_457 (main.py:3734) prin _constatare_esuata. Chiar nesurfacate azi
     in pastila, devin corecte cand cineva le surfaceaza - mai bine corecte acum decat descoperite atunci.
 (2) VERIFICARE CARE NU PORNESTE (regimul necitibil ingusteaza tacit setul auditat) -> GRI + CE S-A SARIT.
     audit_preluare: _tip_firma nu mai inghite orice except drept 'absenta' (ghicea SRL tacit, iar un audit care
     sare peste jumatate din verificari fara sa spuna e mai grav decat unul care crapa vizibil). Existenta
     tabel/coloana se PROBEAZA (to_regclass + information_schema) -> absenta legitima ramane None (SRL default);
     eroarea REALA propaga, iar audit() o intoarce ca gri "regim nedeterminabil - audit INCOMPLET, N straturi
     nerulate" + lista straturilor (ambele regimuri). Nedeterminarea e vizibila, nu ascunsa intr-un default.
 (3) LINIE SARITA (o linie de date neparsabila, nu verificarea) -> LIMITA DECLARATA, nu gri global. control_
     incrucisat cota TVA: linia cu cota neparsabila se CONTORIZEAZA si se declara in limita ("N linii cu cota
     neparsabila - NEVERIFICATE"), dar verdictul ramane pe ce s-a putut verifica. Gri global ar ascunde verdele
     real pe restul liniilor - o minciuna in cealalta directie.
TEMEI: gri = "nu am putut verifica". Se aplica la o VERIFICARE care nu a produs verdict (1,2), NU la o linie
dintr-o verificare care a produs verdict pe rest (3). A confunda nivelurile (linie vs verificare) ar strica
increderea in ambele sensuri: tacerea ascunde probleme, gri-ul global ascunde verdele real.
ALTERNATIVA RESPINSA: acelasi tratament (gri) pentru toate trei - respins de Costin: linia sarita nu e
verificare picata; gri global pe ea ar ascunde verdele real al celorlalte linii.
LIMITA: _tip_firma probeaza existenta coloanei (information_schema) inainte de SELECT - o eroare intre probe si
SELECT (fereastra minuscula) ar propaga -> gri, corect. Straturile sarite din (2) sunt derivate din
_VERIFICAT_DESC (ambele regimuri), nu hardcodate.

### 23.07.2026 Control fiscal ramificat pe tip_firma (PFA/partida simpla) — CORECTEAZA F189 "semafor partial acceptat"  (control_fiscal_api.py: declaratii_datorate/evalueaza_firma; control_incrucisat.py: verifica_d112)
CORECTIE la DECIZII 20.07 F189: acolo s-a scris "Control fiscal ramane vizibil la PFA (semafor partial,
acceptat)". PREMISA FALSA: semaforul nu era doar INCOMPLET, producea verdicte ACTIV GRESITE pe un PFA -
restante D406 INVENTATE, verde GOL pe D112 (0 salariati), "nu pot verifica" pe D100/D101 (declaratii de
persoana juridica ce nu se aplica). Cauza (verificat la sursa 23.07): declaratii_datorate decidea pe VECTOR
(regim_fiscal/platitor_tva/tip_decont/operatiuni_ic/salariati) si NU citea tip_firma - filtrarea pe regim
(straturi_pentru, aplicata auditului) NU se aplica aici.
DECIZIE: declaratii_datorate ramifica pe partida_simpla (PFA): D100, D101 (impozit micro/profit = persoana
juridica; PFA depune D212) si D406 (SAF-T) -> NEAPLICABILE cu temei ("nu se datoreaza"), NU datorate/gri.
verifica_d112 -> garda pe salariati: nr_sal==0 => constatari goale (absent), nu verde pe 0-vs-0.
TEMEI: D406 - OPANAF 1783/2021, Anexa nr.5 pct.4 exclude EXPLICIT persoanele care conduc contabilitatea in
partida simpla (PFA/II/PFL) [verificat la sursa: legislatie.just.ro/public/DetaliiDocument/248326]. D100/D101 -
Cod fiscal Titlul II (persoane juridice); PFA = Titlul IV, Declaratia unica D212 (rutata separat, rip_api).
RULE 1 (metadata): STRATURI_META acopera STRATURI DE MIGRARE, nu declaratii - NU exista mapare declaratie->regim.
NU am inventat un registru DECLARATII_META (over-engineering pt 3 declaratii). Am reutilizat discriminatorul
existent: partida_simpla = "rip" in straturi_pentru(tip_firma) (mecanismul F189), + ramificatie inline pt cele 3.
RULE 2 (criteriu): folosesc criteriul LEGII (partida simpla), derivat din tip_firma prin straturi_pentru. In
modelul actual tip_firma<->partida e 1:1 (srl=dubla, pfa=simpla). Un PFA care OPTEAZA pentru partida dubla (rar,
il face obligat la D406) ar cere un atribut propriu; azi nu exista in model. Daca apare -> atribut separat, nu tip_firma.
RULE 5 (care din 9 nu se aplica PFA, fiecare la sursa): NEAPLICABILE la PFA = D100/D101 (persoana juridica),
D406 (partida simpla exclus). RAMAN vector/fapt-driven (se aplica si la PFA, dupa atribut, NU dupa forma):
D300/D394 (dupa inregistrarea TVA - un PFA POATE fi platitor TVA), D390 (dupa operatiuni_ic), D112 (dupa
salariati), D205/D301 (pe fapt: dividende / operatiuni IC). Niciuna dintre acestea nu e tip_firma-gated.
RULE 4 (verde pe 0-vs-0 fara subiect - clasa raportata, NEreparata in afara de d112): verifica_tva (D300) e in
aceeasi clasa - pe tenant_003 (neplatitor) produce verde "TVA colectata/deductibila coincid" desi firma nu face
TVA, fara garda pe platitor_tva. verifica_d390 NU e in clasa (compara_d390 e tacut pe 0; D-vs-D e gri). De decis
daca verifica_tva primeste garda pe platitor_tva (analog cu d112 pe salariati).
DOVADA: tenant_003 (PFA) - zero restante, D100/D101/D406 neaplicabile cu temei, D112 absent; tenant_002 (SRL)
NEschimbat (D406 datorat, D100/D101 gri pe regim None). 96 teste (5 noi).
LIMITA: evalueaza_firma citeste tip_firma din firma_profil (adaugat universal de F189); o schema fara coloana ar
pica -> firma gri (acelasi mod ca orice coloana lipsa presupusa de SELECT).

### 23.07.2026 Verde fals pe 0-vs-0 = verificare fara subiect (clasa, nu caz)  (control_incrucisat.py: verifica_tva, verifica_d112)
DECIZIE (regula, nu caz): un verificator declarat-vs-contabil al carui SUBIECT nu exista (fara salariati,
neplatitor TVA, fara operatiuni IC, fara facturi) NU produce verdict -> absent (constatari goale), nu verde.
Verde = "am verificat si e in regula"; fara subiect n-a verificat nimic. Verdele fals pe 0-vs-0 e din aceeasi
clasa cu restantele inventate (PFA) - semaforul MINTE ACTIV, nu e doar incomplet.
TEMEI: 0-vs-0 verde afirma o coincidenta intre doua zerouri care nu inseamna "corect", ci "nimic de verificat".
Un contabil care vede verde crede ca s-a verificat ceva. Nuanta: subiect care EXISTA dar e gol legitim (platitor
TVA cu luna nula -> decont nul coincide) RAMANE verde - acolo verificarea A avut subiect.
TRATAREA CLASEI (toti verificatorii declarat-vs-contabil, verificat 23.07):
 - verifica_tva (D300): garda pe platitor_tva==False -> absent (REPARAT). platitor_tva==True gol = verde legitim;
   None (vector incomplet) lasat sa ruleze (D300-declaratie e deja gri la nivel de semafor).
 - verifica_d112 (salarii): garda pe nr_sal==0 -> absent (reparat anterior azi).
 - verifica_d390 (IC): compara_d390 TACUT pe 0=0, D-vs-D gri -> deja corect, lasat.
 - verifica_cota_tva (facturi emise): verificate==0 -> constatari=[] (absent) -> deja se auto-garda pe subiect
   (linii la cota standard), lasat.
 - verifica_d394 / verifica_d205 / verifica_d301: NU EXISTA ca verificatori cross-check (sunt declaratii in
   declaratii_datorate/declaratii_fapt, nu comparatii declarat-vs-contabil). Nimic de gardat.
 - NU sunt in clasa: coerenta_tva (r.tva, randat pct-INFO neutru, nu verde); documente_pozate (verificare de
   lucru-in-asteptare, nu declarat-vs-contabil); echilibru/trezorerie (afisate DOAR pe problema, nu pe 0).
AMBIGUU - RAPORTAT, NEDECIS (cf. regulii "nu decide singur"): d205_vs_457 (coerenta_d205_457, surfacat VIZIBIL in
firme.js cu pct-VERDE pe coerent). Subiectul = dividende distribuite (EVENIMENT, nu proprietate structurala).
0-vs-0 poate fi: (a) confirmare legitima ca AMBELE surse arata zero dividende, sau (b) verde fara subiect (nu s-au
distribuit dividende). Nu decid intre a si b - o firma cu profit care n-a distribuit e "subiect capabil dar gol",
o firma fara profit e "fara subiect". De decis cu Costin daca coerenta_d205_457 primeste garda (absent cand ambele
0) sau ramane verde (confirmare de coerenta).
DOVADA: verifica_tva(tenant_003 neplatitor)=absent; verifica_tva(tenant_002 platitor)=ruleaza normal. 97 teste
(1 nou: verifica_tva neplatitor absent; d112 deja acoperit).

### 23.07.2026 Criteriul clasei "verde fals pe 0-vs-0": proprietate structurala vs eveniment (inchide clasa)
DECIZIE: d205_vs_457 RAMANE verde pe 0-vs-0 (raspuns la intrebarea deschisa din intrarea anterioara). Criteriul
care separa clasa "verde fals pe 0-vs-0 = verificare fara subiect":
 - SUBIECT ca PROPRIETATE STRUCTURALA (firma ARE sau NU salariati; ESTE sau NU platitor TVA): daca proprietatea
   lipseste, verificatorul n-are OBIECT -> nu produce verdict -> ABSENT. (verifica_d112, verifica_tva).
 - SUBIECT ca EVENIMENT (orice firma POATE distribui dividende / face o operatiune): 0-vs-0 e o CONSTATARE
   VALIDA - verificarea are obiect si face munca reala, confirma ca cele doua surse (declaratie D205 vs cont 457)
   sunt de acord ca evenimentul n-a avut loc. -> VERDE. (d205_vs_457).
TEMEI: la un eveniment, 0-vs-0 nu inseamna "n-am verificat nimic", inseamna "am verificat si ambele surse
confirma ca n-au fost dividende". Daca dividendele apareau intr-o singura sursa (D205 fara 457, sau invers),
dif != 0 -> coerent=False -> ROSU (verificat: coerenta_d205_457 intoarce coerent = (dif==0); firme.js randeaza
pct-rosu pe !coerent). Deci verificarea discrimineaza real - nu e un verde care minte, e un verde castigat.
Diferenta de d112/tva: acolo, fara subiectul structural, generatorul compara doua zerouri care nu POT fi
altceva (un neplatitor n-are cum sa aiba D300 nenul) - 0-vs-0 e tautologic, nu constatare.
CLASA INCHISA: verifica_tva + verifica_d112 = structural, garda -> absent (reparate). verifica_d390/cota_tva =
deja corecte. d205_vs_457 = eveniment -> verde ramane. Nimic altceva de reparat pe aceasta clasa.

### 23.07.2026 regim_efectiv — primitiva unica pt regimul CIT; ramificare termene + salveaza pe partida simpla  (migrare_api: regim_contabil/regim_efectiv; termene_api; vector_fiscal_api; main.py VectorIn)
CONTEXT: dupa corectia de date pe tenant_001 (tip_firma pfa, regim_fiscal NULL), doua cai FABRICAU inca gresit:
termene_api (regim None->"micro"->emitea D100) si vector_fiscal_api.salveaza (respingea NULL -> P0: salvarea
vectorului PFA rupta, 400/422). Regresie expusa de UPDATE-ul de azi, reparata in acelasi commit.
DECIZIE: o SINGURA primitiva, langa STRATURI_META (unde traia deja faptul tip_firma->partida, inline in
straturi_pentru):
 - regim_contabil(tip_firma) -> 'dubla' | 'simpla' — UN SINGUR loc unde scrie faptul (srl=dubla, pfa=simpla).
   straturi_pentru refactorizat sa-l foloseasca (nu mai recopiaza regula).
 - regim_efectiv(profil) -> 'micro' | 'profit' | None. Partida simpla (pfa) => None NECONDITIONAT (impozit pe
   venit prin D212, nu regim CIT). Contract STRICT: profil TREBUIE sa aiba tip_firma + regim_fiscal, altfel
   KeyError (fara .get, fara fallback - callerul da profil complet).
ADOPTIE (doar cei doi care FABRICA obligatii; NU d100.py/migrare.js/declaratii_fapt in acest commit):
 - termene_api.termene_firma: regim = regim_efectiv(vector) -> None nu emite D100/D101. main.py:2107 adauga
   tip_firma la SELECT + vector (contractul strict cere cheia).
 - vector_fiscal_api.salveaza: citeste tip_firma SERVER-SIDE din firma_profil (NU din client). Partida simpla
   => regim_fiscal gol -> NULL valid; valoare ne-goala -> eroare explicita (REGIM_LA_PARTIDA_SIMPLA). Altfel =>
   micro/profit obligatoriu. VectorIn.regim_fiscal: Optional[str]=None DOAR ca sa nu pice la boundary (Pydantic).
TEMEI: partida simpla n-are regim CIT (OMFP 170/2015 + Art.68 Cod fiscal; profesie liberala/PFA -> D212). Faptul
tip_firma->partida traia inline in straturi_pentru; o a treia copie in termene/salveaza ar fi drift. O primitiva,
langa fapt, importata de consumatori.
ALTERNATIVA RESPINSA (corectii Costin fata de prima propunere): (a) "rip" in straturi_pentru() ca test de partida
- respins, indirect; extras ca regim_contabil, fapt explicit. (b) regim_efectiv cu .get()/fallback - respins;
contract strict, KeyError pe cheie absenta (o cale care uita tip_firma trebuie sa CRAPE, nu sa presupuna srl).
(c) tip_firma in VectorIn - respins; se citeste server-side, clientul nu decide forma juridica.
DOVADA: P3 - curl salveaza regim='' pe tenant_001 -> 200, NULL stocat; curl regim='micro' -> 400 eroare explicita;
termene tenant_001 -> D112 iun/iul, FARA D100; pytest 518 verde (3 noi: contract regim_efectiv), verificator TOTAL 0.
LIMITA: PFA in partida dubla (rar, dar legal -> datoreaza D406) ramane netratat - cere atribut propriu de mod de
contabilitate, decuplat de tip_firma (intrebare deschisa, vezi raport 23.07). regim_contabil ramane 1:1 tip<->partida.

### 23.07.2026 D406 la PFA in partida DUBLA: RESPINS (nu se datoreaza) + fapt fiscal intr-un singur loc + garda DEFAULT_FISCAL_TACIT  (control_fiscal_api; migrare_api; verificator; DESIGN_SYSTEM cap.17)
RASTOARNA limita deschisa din "23.07 regim_efectiv" ("PFA in partida dubla -> datoreaza D406, ramane netratat,
cere atribut propriu de mod de contabilitate"). CORECTIE, verificat la sursa (OPANAF 407/2025, MO 310/08.04.2025,
care modifica Anexa 5 la OPANAF 1783/2021 - [legislatie.just.ro/Public/DetaliiDocument/296490]):
DECIZIE: PFA / II / profesii liberale sunt excluse de la D406 NECONDITIONAT - deci nici PFA in partida dubla NU
datoreaza. NU se construieste atributul de mod de organizare a contabilitatii.
TEMEI: Anexa 5 pct.4 lit.a) = enumerare NECONDITIONATA a persoanelor fizice; conditia de partida dubla apare
DOAR la lit.n) (asociatii/persoane fara scop patrimonial); pct.3 lit.s) vizeaza doar persoane juridice. Deci
optiunea pentru partida dubla NU muta PFA-ul in obligatie. Stringul temei din cod: "OPANAF 1783/2021 Anexa 5
pct.4" -> "OPANAF 407/2025, Anexa 5 pct.4 lit.q)".
CONSECINTA: tip_firma<->partida ramane 1:1 in model (regim_contabil); nu mai e nevoie de decuplare. Limita
deschisa se INCHIDE (respinsa cu temei, nu amanata).
FAPT INTR-UN SINGUR LOC (consolidare): control_fiscal_api deriva partida_simpla prin migrare_api.regim_contabil
(nu mai "rip" in straturi_pentru inline). Default-ul 'srl' + normalizarea tip_firma traiesc in tip_firma_nrm
(migrare_api) - auth_api / tenant_provisioning / vector_fiscal_api il refolosesc, nu redau `or "srl"` inline.
GARDA: DEFAULT_FISCAL_TACIT (verificator + DESIGN_SYSTEM cap.17) - interzice fallback pe literal (or/||/else
"micro"/"profit"/"srl"/"pfa") pe regim_fiscal/tip_firma/platitor_tva, exceptat migrare_api.py (primitivele).
Prinde forma or/||/else (fallback pe CITIRE, ca bug-ul termene); atribuirea simpla `x="srl"` NU (declaratie).
LIMITA garda: scaneaza `.py`; fallback-urile de AFISARE din frontend (migrare.js/firme.js: `tip_firma || "srl"`,
`regim_fiscal || "micro"`) raman follow-up separat (nu s-a atins frontend in acest commit).
DOVADA: pytest complet verde + verificator TOTAL 0 (DEFAULT_FISCAL_TACIT 0). Reparate: termene_api, vector_fiscal_api,
auth_api, tenant_provisioning, control_fiscal_api.

### 23.07.2026 Blocaj real: PFA nu putea trece pasul Vector fiscal la migrare (formularul forta un regim)  (auth_api; main.py /migrare/vector; migrare.js; firme.js)
CONSTATARE (nu cosmetic, cum banuiam initial): butoanele vf-opt din migrare.js NU au deselect (handlerul `grup`
scoate vf-on de la toate si-l pune pe cel apasat) -> "micro" pre-selectat la un PFA (fallback `|| "micro"`) nu
putea fi scos -> getRegim() intorcea mereu un regim ne-gol -> POST /tenants/{id}/vector -> salveaza (gardat P2b)
respingea cu 400 NECONDITIONAT. Deci un PFA nu putea completa vectorul deloc.
DECIZIE: frontendul ramifica pe FAPTUL expus de backend, nu ghiceste. auth_api.tenantii_userului adauga
regim_contabil (derivat din tip_firma prin migrare_api.regim_contabil - expunere, nicio regula noua);
/migrare/vector il propaga. migrare.js: sterge `|| "micro"`; partida simpla -> ascunde intrebarea de regim
si trimite regim_fiscal=null (salveaza accepta -> NULL); lista afiseaza regim null ca "—", nu "micro".
firme.js: sterge `|| "srl"` (fallback mort - backendul garanteaza tip_firma); eticheta selector la creare
include "profesii liberale" (PFA/II/IF/profesii liberale - partida simpla).
DOVADA: /migrare/vector expune regim_contabil (tenant_001=simpla); POST vector cu regim_fiscal=null -> 200 (era
400); pytest 518 verde; verificator TOTAL 0; node --check pe migrare.js/firme.js OK.
LIMITA: garda DEFAULT_FISCAL_TACIT ramane pe `.py` - dar fallback-urile frontend vizate sunt acum sterse;
follow-up-ul din commit-ul precedent e INCHIS.

### 23.07.2026 DEFAULT_FISCAL_TACIT extins pe .js + filtrarea pasilor de migrare nu ghiceste la eroare  (verificator; migrare.js; DESIGN_SYSTEM cap.17 v2.17)
DECIZIE: garda DEFAULT_FISCAL_TACIT scaneaza acum si `.js` (aceleasi 3 campuri regim_fiscal/tip_firma/platitor_tva;
formele `field || "lit"` si ternar `? ... : "lit"` cu literalul fiscal in ramura ELSE = default). NU prinde maparea
valoare->eticheta (`=== "profit" ? "profit" : ...`, literal in THEN). Curatate: migrare.js:1370 (`tip_firma || "srl"`
sters). Filtrarea pasilor de migrare: la eroare `/migrare/straturi` (aplicabile null/gol) NU se mai afiseaza toti
pasii ("arata tot" gratios) - un PFA ar fi vazut pasii de partida dubla; se afiseaza stare-goala canonica +
reincercare. straturi_pentru ramane SURSA UNICA a filtrarii (nu se deriva in JS din regim_contabil).
TEMEI: fallback-ul tacit pe frontend ajunge la fel de rau ca pe backend (dovedit: regim || "micro" fabrica D100).
"Arata tot" la eroare inseamna un PFA vede intrebari de partida dubla = nonsens. Necunoscut -> stare-goala, nu ghicit.
T4 RAPORTAT (decizie Costin): `tip_decont || "trimestrial"` (migrare.js) NU se poate citi din ANAF v9 - parserul
(anaf_api.py:98-117) extrage doar platitor_tva/stare/inactiv/denumire, NU periodicitatea decontului (e din prag/
optiune D010, nu din snapshot scpTVA). Deci nu e "citeste in loc de default"; ramane default. De decis daca se
elimina (intreaba mereu) sau se pastreaza (trimestrial = default rezonabil pt firma mica). NEatins.
DOVADA: pytest 518 verde; verificator TOTAL 0 (DEFAULT_FISCAL_TACIT 0 pe .py+.js); node --check migrare.js OK;
simulare eroare /migrare/straturi -> stare-goala, zero pasi (raspuns OK -> 5 straturi la PFA).

### 23.07.2026 tip_decont: al 4-lea camp fiscal in DEFAULT_FISCAL_TACIT; obligatoriu la migrare, fara default  (migrare.js; termene_api; verificator; DESIGN_SYSTEM cap.17 v2.18)
DECIZIE: tip_decont (periodicitatea decontului TVA) e camp care DECIDE obligatii (periodicitatea D300/D394/D406)
-> intra in garda DEFAULT_FISCAL_TACIT (al 4-lea camp; literale lunar/trimestrial), .py+.js. Eliminat defaultul
tacit: migrare.js `|| "trimestrial"` (pre-selectie) si termene_api `or "lunar"`. La migrare, pentru platitorii
TVA e OBLIGATORIU, fara preselectie (submit fara el -> 400); non-platitor -> null, intrebarea nu apare.
TEMEI (langa intrebare, prin .camp-ajutor - forma DS canonica de ghidaj camp neautocompletabil, NU caseta-atentie
care e rosu/distructiv): "Lunar (regula, art. 322 alin. 1 Cod fiscal); trimestrial doar daca in anul precedent
cifra de afaceri < 100.000 euro (curs BNR 31.12) SI fara achizitii intracomunitare de bunuri - art. 322 alin. 2".
DE CE fara default: periodicitatea NU vine din ANAF v9 (parserul anaf_api.py aduce doar scpTVA/stare/inactiv, nu
decontul; e din prag cifra afaceri / optiune D010) -> a o ghici "trimestrial" ar fabrica termene D300 gresite.
termene_api: decont necompletat -> NU emite termene D300 (nu ghiceste; semaforul o marcheaza deja gri).
FIRME EXISTENTE (raportat, neatins): 1 firma are tip_decont setat (tenant_002 = DANTE, platitor TVA, 'lunar' -
valoare EXPLICITA corecta, nu default); cei 2 PFA au null (corect). Migrata (migrare_status vector_fiscal gata).
Niciuna cu 'trimestrial' suspect din default -> nimic de curatat.
DOVADA: pytest 518; verificator TOTAL 0 (DEFAULT_FISCAL_TACIT 0, tip_decont inclus, .py+.js); curl platitor TVA
fara tip_decont -> 400; cu 'lunar' -> 200 (tenant_002 nemodificat).

### 23.07.2026 Pasul B: D300/D394 marginite la inregistrarea TVA (fapt ANAF) + D390 la neplatitor = gri, nu tacere
B1 — VERIFICAT LA SURSA (LIVE, nu din parser): raspunsul ANAF v9 (webservicesp.anaf.ro/.../v9/tva) contine
`inregistrare_scop_Tva.perioade_TVA[]` cu `data_inceput_ScpTVA` / `data_sfarsit_ScpTVA` (DANTE: 2002-02-01, activ;
cabinet AMZUICA: 2023-11-01 -> 2024-02-08, anulat). DECIZIE: se parseaza data inceperii inregistrarii ACTIVE
(perioada fara data_sfarsit) ca FAPT ANAF, se stocheaza snapshot (firma_profil.platitor_tva_anaf_inceput, langa
platitor_tva_anaf), si declaratii_datorate MARGINESTE fereastra D300/D394 la perioadele DE DUPA inregistrare -
perioadele anterioare NU sunt restante, nu apar deloc (emite_tva(marginit=True)). D406 NU e marginit (obligatie
SAF-T, nu perioada TVA). Firma fara snapshot (inceput NULL) -> fara margine (fereastra completa, gratios).
Lant: anaf_api._tva_inceput_activ -> _anaf_tva_check (3-tuplu) -> seteaza_snapshot_tva(data) -> coloana ->
evalueaza_firma vector.tva_data_inceput -> emite_tva. Proba e2e: POST vector DANTE -> platitor_tva_anaf_inceput=2002-02-01.
B2 — D390 la NEPLATITOR cu operatiuni IC: nu emite tacut, nu omite tacut. Fara faptul inregistrarii art. 317 ->
GRI cu temei: "D390 se depune de persoanele inregistrate conform art. 316 sau art. 317 (OPANAF 705/2020, pct.1.1).
Nu avem inregistrata calitatea art. 317 pentru aceasta firma." (platitor art.316 -> D390 datorat, ca inainte.)
RETRAGE aserția "neplatitor => zero D390" din matrice: era prea stricta (art. 317 exista); corect e gri.
B3 — matricea extinsa la 64 config (6 dimensiuni: + operatiuni_ic, + depuse). Calea VERDE (confirmate) testata
prin _clasifica cu `depuse` -> aserția "fiecare verdict are temei" exercitata SI pe verde (motiv din _clasifica).
DOVADA: 582 teste verde (matrice 64), verificator TOTAL 0, snapshot e2e (DANTE 2002-02-01), D300 marginit
(inreg. aprilie -> doar apr/mai/iun), D390 neplatitor+IC -> gri cu temei.
LIMITA: art. 317 (inregistrare speciala pt IC) NU e un camp in vector -> un neplatitor cu IC ramane GRI (corect:
nu stim). Daca se aduce art. 317 din ANAF (alt camp v9) -> se poate rezolva verde/rosu. Nedecis.

### 23.07.2026 Pasul C — prezentare Control fiscal (C1-C5)
C1 (CAUZA, nu afisarea): temeiul duplicat pe restante = _clasifica genera un motiv AUTO-CONTINUT ("D300 dec
nedepusa, termen 26.01.2026 depasit") care repeta tip/perioada/termen randate DEJA structurat in antet
(cf-rand-decl). Verificat la sursa: NU e double-render, NU e dedup alerte_control_emise (alertele lucreaza pe
(tenant, verificator, perioada), nu consuma motiv). Reparat la CAUZA: motiv = doar ADITIV - confirmate: data
depunerii + la/dupa termen; lipsa/urmarit: DOAR faptul (D205/D301 "de ce e datorat"), statusul e implicit din
sectiune (Restante) + termenul rosu. Restanta simpla -> motiv "" (temei structurat). Rastoarna partial DECIZII
18.07 B ("fiecare declaratie poarta motiv"): temeiul restantei e STRUCTURAT, nu prose duplicat.
C2: antetul acoperea doar axa declaratiilor; rescris sa acopere axele LIVE ale semaforului (verificat in
FUNCTIONALITATI.csv): declaratii datorate vs depuse + coerenta cu contabilitatea (F163 TVA/salarii/IC, F184 cota
facturi emise, echilibru/trezorerie). F185 (coliziune CUI) NU intra - e la register/landing, nu in semafor.
C3: ordinea sectiunilor dupa utilitate decizionala: Restante -> De urmarit -> Nu pot verifica (gri) -> Nu se
datoreaza (inchis, cu temei) -> La zi (confirmate) ultima.
C4: ordonare restante dupa vechimea depasirii (cel mai vechi intai) - FACUT. Grupare vizuala pe tip cu separator
canonic - NEFACUT: separatorul nu exista in DS -> STOP (nu inventez). Vezi DE_FACUT.
C5 (raportat, neatins): "Firmă activă: Nicio firmă selectată" (navigator.js:100, .subbara-gol) = stare legitima de
SUB-BARA (contextul firmei active), afisata DOAR cand nu e firma in lucru (conditional corect, nu bug). NU e
lista goala -> .stare-goala (cap.6) nu se aplica (context de bara, nu de continut). Lasat.
DOVADA: 582 teste (2 actualizate la C1 + matrice A1 pe temei structurat), verificator TOTAL 0, captura de date
(structura ecranului) pe tenant_001 PFA + tenant_002 SRL. Capturi PIXEL = pasul de audit browser al lui Costin
(fara browser headless in mediul de dezvoltare).

### 23.07.2026 C4 restante: lista plata, fara grupare pe tip (fara primitiva DS noua)
DECIZIE: restantele raman LISTA PLATA ordonata dupa vechimea depasirii termenului (cel mai vechi intai). NU se
grupeaza pe tip si NU se adauga un separator/primitiva vizuala noua in DESIGN_SYSTEM.
TEMEI: gruparea pe tip FRAGMENTEAZA semnalul de urgenta, care e SINGURUL criteriu decizional la restante (ce a
depasit cel mai mult termenul se plateste intai, indiferent de tip). O primitiva DS pentru un singur ecran = cod
mort (regula noua intretinuta pentru un consumator). Se reconsidera daca apar 3+ ecrane cu aceeasi nevoie de
sub-grupare vizuala. Inchide flag-ul C4 din raportul precedent.

### 23.07.2026 Termene poz.3 — D390 pe FAPT lunar, o primitivă / două comportamente  (d390.py; control_fiscal_api; termene_api; main.py)
PROBLEMA: obligatii_datorate emitea D390 pentru FIECARE lună cât timp bifa statică operatiuni_ic=True
(obligație lunară fixă) — contrar instr. completare D390 (anexa OPANAF 705/2020; principiu identic OPANAF 705/2020 anexa 2 pct.1.2 (anterior OPANAF 394/2017, abrogat) la D394): D390 se depune NUMAI pentru lunile în care ia naștere exigibilitatea operațiunilor IC.
DECIZIE: primitivă unică `d390.d390_are_operatiuni(conn, schema, an, luna, azi) -> bool|None` (unde stă deja
cunoașterea per-lună): True/False = perioadă ÎNCHISĂ (fapt din facturi IC + d390_manual + d301_operatiuni),
None = perioadă DESCHISĂ (exigibilitatea nu se poate stabili încă). `obligatii_datorate` primește callback
`d390_fapt` (default None = comportament vechi pe bifă → apără matricea de 64) și îl consultă:
  - False => D390 NU se datorează acea lună.
  - True  => datorat.
  - None  => apelantul decide după DIRECȚIE (parametrul `jos`).
TEMEI — COST ASIMETRIC: o restanță D390 falsă = acuzație nefondată; un termen ascuns care se materializează =
amendă. Deci ÎNAPOI (semafor, jos=None) decidem pe FAPT — luna închisă fără operațiuni nu e restanță (confirmare
cu temei doar pe ultima lună închisă, nu tot istoricul); ÎNAINTE (termene, jos=dată) AFIȘĂM pe incertitudine —
luna deschisă (None) apare, fiindcă nu putem exclude operațiuni până la finalul ei.
Flag-ul operatiuni_ic RĂMÂNE în vector (indicator de profil: dacă e False/None nu se ajunge la fapt), dar NU mai
decide singur obligația lunară. Semaforul (evalueaza_firma) construiește closure-ul (are conn_schema); termene
(ruta /termene) la fel, cât timp `cs` e deschis.
DOVADĂ: pytest 921 (matrice 64 + test_control_fiscal NESCHIMBATE, d390_fapt=None); verificator TOTAL 0; verificare
funcțională pe DANTE real (mai închisă=False, iunie închisă cu facturi IC=True, iulie/aug deschise=None → semafor:
iunie datorat, mai NU e restanță; termene: iunie+iulie).
LIMITĂ (raportată, follow-up): primitiva face ~4 interogări/lună/firmă; la portofolii mari s-ar batch-ui pe an.
Azi (3 firme) e neglijabil. Marcaj `tip_d390` pe factură (F125 open) ar înlocui derivarea per-lună cu citire directă.

### 23.07.2026 §4 Termene — marginirea la inregistrarea TVA (inchide asimetria cu semaforul)  (main.py /termene; test_termene)
CONTEXT: la consolidarea T2 s-a lasat deliberat termene FARA marginire (ruta nu aducea platitor_tva_anaf_inceput),
pentru proba vizuala. DECIZIE: ruta /termene aduce acum platitor_tva_anaf_inceput in vector (tva_data_inceput) si
motorul (obligatii_datorate.emite_tva marginit=True) margineste D300/D394/D406 la perioadele DE DUPA inregistrare -
exact ca semaforul. Motorul stia deja sa margineasca (B1, DECIZII 23.07); ii lipsea doar coloana.
TEMEI: asimetrie intre ecrane = bug latent. O firma inregistrata TVA in interiorul ferestrei de 60z ar fi vazut in
Termene scadente D300/D394 pe perioade DINAINTE de inregistrare (perioade care nu se datoreaza). Semaforul le
excludea, termene nu -> acelasi fapt, doua verdicte. Acum unificat.
DOVADA: pytest 922 (test nou: inreg. 01.08 -> iunie/iulie dispar din termene; fara margine iunie apare); verificator
TOTAL 0. LIMITA: firmele fara snapshot (tva_data_inceput NULL) raman nemarginit (fereastra completa) - corect,
faptul ANAF lipseste.

### 23.07.2026 D390 — faptul PRIMEAZA peste bifa + contradictie profil-vs-facturi semnalata  (control_fiscal_api obligatii_datorate)
CONSTATARE (item 1): dupa consolidare, operatiuni_ic=False ramasese POARTA TARE (`elif operatiuni_ic:`) - un
platitor cu bifa False dar cu facturi IC reale nu primea D390 si faptul nu se consulta deloc. Contrar naturii
D390 (obligatie pe FAPT, nu pe declaratia de profil).
DECIZIE (item 1): INVERSAT - faptul primeaza. Ramura D390 pentru platitor consulta d390_fapt pentru FIECARE luna
din fereastra, indiferent de bifa. fapt=True -> D390 datorat (indiferent de operatiuni_ic). Bifa conteaza DOAR
cand faptul e None (luna deschisa): profil IC -> afisam/gri; profil fara IC -> nu emitem; profil None -> gri
necompletat. Compat: d390_fapt=None (matrice/teste pure) pastreaza comportamentul istoric pe bifa (ramura separata).
DECIZIE (item 2): contradictie operatiuni_ic=False DAR facturi IC reale (fapt True pe o luna) -> SEMNAL gri cu
temei ("profilul firmei declara FARA operatiuni intracomunitare, dar exista facturi intracomunitare in perioada X"),
NU blocare - ca F185. La platitor: D390 se datoreaza oricum (fapt) + semnalul. La neplatitor: gri (art.317 /
contradictie) in loc de tacere. Semnalul intra in `neclar` -> Control fiscal il arata gri; termene il ignora
(privire inainte), dar D390 datorat (fapt) apare si acolo.
TEMEI: D390 se depune pe exigibilitatea operatiunilor IN LUNA (instr. completare D390, anexa OPANAF 705/2020 anexa 2 pct.1.2 (anterior OPANAF 394/2017, abrogat)). Bifa de profil e un indicator, nu adevarul lunar; cand contrazice faptul, faptul castiga si divergenta
se semnaleaza (nu se ascunde, nu se blocheaza).
DOVADA: pytest 927 (matrice 64 NESCHIMBATA, d390_fapt=None); verificator TOTAL 0; functional pe DANTE (semafor):
D390 iunie = restanta reala (avea IC, nedepusa), mai NU e restanta falsa.

### 23.07.2026 operatiuni_ic obligatoriu la migrare (al 5-lea camp DEFAULT_FISCAL_TACIT)  (vector_fiscal_api; main VectorIn; migrare.js; verificator; DESIGN_SYSTEM cap.17 v2.19)
CONSTATARE (§3, raportata anterior): in formularul de migrare `tip_decont` era obligatoriu (.oblig *), dar
`Operatiuni intracomunitare?` NU — cu "Nu" preselectat implicit; iar `salveaza` facea `ic = bool(operatiuni_ic)`
-> o firma prin formular primea mereu True/False, niciodata None. Gap: default tacit False pe un camp care DECIDE
obligatia D390 (o firma cu operatiuni IC unde contabilul nu schimba "Nu" -> D390 ratat).
DECIZIE: operatiuni_ic devine obligatoriu la migrare, ca tip_decont, fara default tacit.
- VectorIn.operatiuni_ic: Optional[bool]=None (nu bool=False); salveaza respinge None -> 400 IC_LIPSA (verificat prin
  proba HTTP: POST /vector fara operatiuni_ic -> 400 "alege Da sau Nu"; check-ul fireste PRIMUL, inainte de regim).
- citeste intoarce operatiuni_ic None cand e None (nu False tacit) - simetric cu platitor_tva - ca frontendul sa
  distinga "nesetat" de "Nu".
- migrare.js: fara preselectie (valoare raw true/false/null: `ic===true`/`ic===false`), trimite null cand nu e ales,
  .camp-ajutor cu temeiul (instr. D390, anexa OPANAF 705/2020 anexa 2 pct.1.2 (anterior OPANAF 394/2017, abrogat)).
- DEFAULT_FISCAL_TACIT extins la al 5-lea camp (boolean: True/False/false + "da"/"nu"), .py+.js, regula in
  DESIGN_SYSTEM cap.17 v2.19 SIMULTAN cu verificatorul (norma + gardian mecanic in acelasi loc).
TEMEI: acelasi principiu ca tip_decont (23.07) - un camp care decide obligatii, care nu se poate autocompleta din
ANAF, se cere EXPLICIT. operatiuni_ic e declarat de contabil (profil), nu vine din ANAF v9. Combinat cu item 1+2
(faptul lunar primeaza), bifa gresita nu mai ascunde D390: faptul o contrazice + se semnaleaza.
DOVADA: pytest 927; verificator TOTAL 0 (DEFAULT_FISCAL_TACIT 0, fara fals-pozitive pe payload-ul nou); proba HTTP
400 pe operatiuni_ic lipsa; tenant_001 intact (400 inainte de write).
LIMITA: firmele EXISTENTE cu operatiuni_ic deja setat (True/False explicit) raman valide; cele cu None (create in
afara fluxului de migrare, ex. audit-preluare) vor cere completarea la prima editare a vectorului.

### 23.07.2026 Regresie termene (UndefinedTable) — poarta D390 pe fapt = platitor; d301 scos din primitiva
CONSTATARE: dupa 01b353b, /termene crapa pe tenant_001 (PFA partida simpla, neplatitor) cu
"relation tenant_001.d301_operatiuni does not exist" -> firma cadea in neevaluate, iar 27.07 arata 1 firma in
loc de 2. Cauza: bucla de verificare a contradictiei la NEplatitor (item 2) apela d390_fapt -> d390_are_operatiuni
-> SELECT pe d301_operatiuni, tabela care lipseste la scheme vechi de partida simpla.
DECIZIE (nu try/except - poarta prin forma):
- POARTA = platitor_tva: faptul D390 (d390_fapt, atinge DB per luna) se consulta DOAR la platitori (art. 316).
  Un neplatitor nu are D390 pe fapt - obligatia lui depinde de inregistrarea art. 317, pe care n-o urmarim
  (facturile IC nu o dovedesc). Neplatitor -> decizie pe FLAG (True=art.317 gri; False=nimic; None=gri necompletat),
  fara DB. Cade si semnalul de contradictie la neplatitor (corect: la un neplatitor facturile IC nu implica D390).
- d301_operatiuni SCOS din d390_are_operatiuni: e artefact D301 / NEplatitori, irelevant pentru D390 al unui
  platitor (singurii apelanti ramasi dupa poarta) - cod mort + fragil. Raman sursele reale: facturi IC + d390_manual.
- Mesaj (item 4): neevaluate nu mai scurge type(e).__name__ ("UndefinedTable") pe ecran; numele tehnic ramane in
  log (_LOG_VERDICT.warning %r), pe ecran temei citibil (DS cap.6).
- Aserție de regresie (item 5): test_matrice.test_d390_fapt_consultat_doar_la_platitor - pentru fiecare config,
  d390_fapt invocat DOAR la platitor (stub care inregistreaza; neplatitor = zero apeluri). Ar fi prins bug-ul.
DOVADA: pytest 945 (matrice 64 intacta + 18 cazuri de poarta); verificator TOTAL 0; functional: tenant_001 reapare
cu D112 (iun 27.07 + iul 25.08), 27.07 = 2 firme (AMZUICA+DANTE), neevaluate=[].

### 23.07.2026 [RAPORT, nereparat] Drift de schema: d301_operatiuni + d205_beneficiari lipsesc din template
Comparatie schema-tenant vs tenant_template.sql (43 tabele): tenant_001, tenant_002, tenant_003 - ZERO tabele
lipsa fata de template. DAR tenant_002 are 2 tabele EXTRA care NU sunt in template: d301_operatiuni si
d205_beneficiari (create ad-hoc doar pe tenant_002, netrecute in template). Inversul ipotezei initiale ("tenant_001
are drift") - de fapt TEMPLATE-ul e incomplet, iar tenant_002 e outlier-ul.
CONSECINTA: orice tenant provizionat din template (tenant_001, tenant_003, viitoarele) NU are aceste tabele.
Generarea D301 (decont special TVA neplatitori) si functiile pe d205_beneficiari sunt rupte pentru toti in afara de
tenant_002. NEREPARAT (cerut doar raport). De reparat separat: adauga cele 2 tabele in tenant_template.sql (din
DDL-ul real de pe tenant_002) + backfill tenant_001/003 + poarta F165 (care compara si coloane, nu doar tabele).
Vezi DE_FACUT.

### 23.07.2026 CORECTIE + rezolvare: d301 canonizat, d205 legacy eliminat (raportul anterior de "drift" era gresit)
CORECTIE la DECIZII/DE_FACUT din 91b9051: afirmatia "generarea D301 e rupta pentru toti tenantii in afara de
tenant_002" e FALSA. Verificat la sursa: d301.py:ensure_tabel facea CREATE TABLE IF NOT EXISTS lazy (gardat), deci
D301 se auto-vindeca la prima folosire - dovedit functional pe tenant_001 (pull creeaza tabela, 0 crash). Cauza reala
a crash-ului din termene: d390_are_operatiuni interoga d301_operatiuni FARA garda pe care d301.py si control_incrucisat
o au. Deja reparat (91b9051, d301 scos din primitiva).
DECIZIE (Costin, optiunea 1 pt d301 / optiunea 3 pt d205):
- d301_operatiuni CANONIZAT: mutat din CREATE lazy (ensure_tabel ELIMINAT din d301.py) in tenant_template.sql
  (o singura sursa de adevar, aliniat cu decizia 22.07 anti-lazy). id SERIAL (ca sa coincida cu tabelele deja
  create lazy pe tenantii existenti -> zero drift F165). Backfill idempotent tenant_003 (001/002 aveau deja).
  F165: d301 scos din _EXTRA_CUNOSCUTE (nu mai e extra - e in template; test_toti_tenantii_conform il verifica HARD).
- d205_beneficiari: cod mort ELIMINAT (reparatie reala, nu petic). Zero writeri in tot codul; unicul consumator era
  verificarea d205_vs_457 din _verificari_contabile care citea suma_bruta din tabela mereu goala -> rosu fals pe
  orice firma cu dividende (1171->457). Sters: citirea (main.py), coerenta_d205_457 (verificatoare.py), randarea
  (firme.js), din whitelist F165. D205-vs-457 pe FAPT traieste deja in semafor (control_incrucisat.dividende_
  distribuite via declaratii_fapt). Tabela ramane pe tenant_002 NEATINSA (fara DROP - nu inspectam date necunoscute),
  fara consumatori -> extra informativ in F165.
CONSTATARE (raportata, nereparata): d301_operatiuni NU are writer nicaieri in cod (nici INSERT, nici ruta, nici UI) -
D301 genereaza XML dintr-o tabela care se populeaza doar manual/extern. Feature-completeness gap (D301 n-are UI de
introducere operatiuni IC), NU blocant - generarea + semaforul citesc corect. De decis daca merita UI/import D301.
ITEM 4 (F165 tabele lipsa = eroare): era DEJA implementat - compara() marcheaza tabele_lipsa (template->tenant) HARD
si are_drift_hard il include (test_audit_schema linia 44-45 + test real toti_tenantii_conform). Nimic de construit.
DOVADA: pytest 945 (test real tenant-vs-template cu d301 nou verde); verificator TOTAL 0; backfill dovedit
inainte/dupa (tenant_003 creat, 001/002 idempotent skip).

### 23.07.2026 Termene poz.3 — prezentare (P1-P4), decizii de conținut  (termene.js; api.js dataRo; verificator; stil.css; DS cap.4/8 v2.20)
Pas de prezentare pe Termene (poziția 3 DESCHISĂ, recaptura la Costin). Patru puncte, un commit UI:
- P1a: eliminat formatorul LOCAL `dataLunga` din termene.js -> `dataRo(d,'lung')` = "27 iulie 2026" (anul inclus,
  rezolvă ambiguitatea din fereastra care traversează anul, introdusă de noi la T4). cap.4 (DATA_DIALECT).
- P1b: gard DATA_DIALECT avea gaură (prindea `toLocaleDateString`/`const fmt=...split`, NU forma `dataLunga` =
  array de luni indexat prin parseInt). Extins (precis pe UTILIZARE `luni[parseInt(...)]`, nu pe declarație -> nu
  atinge pickerele `LUNI.map`). Rulat pe tot frontendul: 5 formatoare locale (termene/cabinet/portal = formatoare
  reale -> convertite la dataRo; declaratii/pachete = pickere legitime, neatinse). Stil nou `luna_an` ("iulie 2026")
  pentru portal (balanțe lunare, from `to_char YYYY-MM`). Regula în DS v2.20 simultan.
- P1c [DECIZIE DE CONȚINUT, nu format DS]: eticheta de perioadă afișează anul din `d.an` DOAR când diferă de anul
  curent ("iun" / "iun 2027"). Motiv: în fereastra normală (an curent) anul e redundant; devine necesar doar când
  fereastra de 60z trece în an+1 (dec). `dataRo` e pentru DATE, nu pentru etichete de perioadă (string backend
  `_LUNI_NUME[m]`) -> decizia trăiește în UI (etichetaPerioada în termene.js), consemnată aici. Backend: `an` +
  `incert` propagate prin portofoliu (un grup termen+tip = o perioadă -> egale pe toate firmele).
- P2: rândurile de firmă din detaliu nu mai sunt fundătură (cursor:default) -> `deschideFirma(t,nav)` (firme.js:146,
  exportat), cursor:pointer. Calea EXISTA, lipsea `cui` în datele /termene (adăugat) + maparea `tenant_id`->`id`.
  Fără rută nouă.
- P3: nimic de schimbat — cap.2a interzice non-modal, cap.9 scroll intern = pattern sancționat pentru liste lungi.
  Confirmat că modalul folosește `max-height: calc(100vh - 48px)` (stil.css:253) + `.fereastra-corp{overflow-y:auto}`.
- P4: D390 pe perioadă DESCHISĂ = incertitudine -> bulină `.pct-gri` (var(--gri-semafor), cap.8) + etichetă "posibil"
  (10px, cap.8 buline+text). Aliniat 1:1 cu semaforul (același caz e deja gri acolo). Perioadă închisă = obligație
  cunoscută, fără bulină. Backend: flag `incert` pe itemul D390 emis pe lună deschisă (obligatii_datorate, doar
  termene jos!=None) -> matricea intactă (d390_fapt=None nu-l setează).

### 23.07.2026 Declaratii poz.1 — G2/G3/G4 (prezentare); G4-garda raportata, nu extinsa
G2: pas2 din declaratii.js ignora eroarea (catch(e) -> mesaj generic). Aliniat la pas3: afiseaza e.mesaj (422 cu
temei / gri cu limita) - exact unde contabilul are nevoie. api.js arunca {cod, mesaj}.
G3: eticheta de perioada folosea formator local (LUNI[S.luna-1] ${S.an}) in loc de dataRo("luna_an"). Reparat in
etPerioada (LUNI ramane pentru picker). Garda DATA_DIALECT extinsa PRECIS: prinde array-lună folosit ca ETICHETA
luna-an (indexare urmata de ${...an}), NU luna-doar (fara echivalent dataRo) si NU pickerul (.map). Rulata pe tot
frontendul -> 6 etichete locale (declaratii/cabinet:504/pachete:106,134/portal:387,403,665) reparate la dataRo;
3 array-uri moarte sterse (cabinet, 2x portal). TRIM (trimestru) ramane local - fara echivalent dataRo.
G4: panoul de clasificare D390 (F125) avea style inline display/flex/gap/color (contra cap.0). Reparat: clase
.dec-recl-rand/.dec-recl-desc/.dec-recl-suma/.dec-recl/.dec-man-rand/.dec-man-form/.dec-clasif-gol; width/margin
raman inline (pozitionare permisa cap.0). GARDA NU extinsa: display/flex/gap/color inline = 217 aparitii pe tot
frontendul (firme.js 80, facturi 18...) = DATORIE ACCEPTATA explicit (v2.11, DE_FACUT §3.2 "spacing/padding inline
inchis ca datorie acceptata"). NU e gaura accidentala, e decizie. Extinderea gardei = 217 flag-uri = curatenie
frontend-wide (revenire pe decizia v2.11), workstream separat - RAPORTAT, nu facut orb. Vezi G1 (STOP separat).
DOVADA: pytest 945; verificator TOTAL 0; node --check pe declaratii/cabinet/pachete/portal.

### 23.07.2026 Declaratii poz.1 — G1 filtrare tip_firma (o mapare, trei consumatori) + poarta backend
G1: ecranul Declaratii arata toate cele 9 tipuri indiferent de firma -> un PFA vedea D101/D406 (persoana juridica).
VERIFICAT: NU exista primitiva separata "aplicabil prin forma"; excluderea era inline in obligatii_datorate.
DECIZIE (Costin): EXTRAG, nu scriu a treia mapare.
- control_fiscal_api._NEAP_FORMA_SIMPLA (constanta) + neaplicabile_forma(tip_firma) -> {tip: temei} (partida
  simpla=pfa -> D100/D101/D406; {} juridic). SURSA UNICA: obligatii_datorate o foloseste (temei nedupli­cat, pe
  partida_simpla, NU re-derivat din tip_firma - altfel crapa cand vectorul de test are partida_simpla fara tip_firma),
  declaratii_api o foloseste (poarta), ruta o expune (selector). Trei consumatori, o mapare.
- Ruta GET /declaratii/tipuri CERE tenant_id (fara -> 400, NU {} tacit - "nimic exclus" implicit = tiparul eliminat
  de 5 ori azi). Include neaplicabile: {tip: temei}. Standalone: dropdown gol/"alege firma" pana la firma; re-cerut
  la fiecare schimbare de firma (refresh async).
- POARTA BACKEND: declaratii_api.genereaza citeste tip_firma si respinge cu ValueError->422+temei daca tipul e
  neaplicabil prin forma (POST /declaratii/{tip} SI /valideaza). UI dezactiveaza, backend decide. Dovada: POST d101
  pe tenant_001 (PFA) -> 422 cu temei D101/D212, nu XML gol.
- UI forma A (Costin): <select> pastrat, <option disabled title="<temei complet>">TIP · per — nu se aplica (partida
  simpla)</option>. B (carduri cap.2b) = reorganizare de anatomie, NU acum. Motiv: temeiul esential ("nu se aplica,
  partida simpla") incape in optiune, complet in title; se reconsidera daca ecranul se rescrie.
FINDING (nereparat): regim_contabil trateaza ca 'simpla' DOAR 'pfa'; 'ii'/'if'/'pfl' -> 'dubla'. OK daca DB
stocheaza 'pfa' pt toate entitatile de partida simpla; de verificat separat daca II/IF pot avea tip_firma propriu.

### 23.07.2026 G4-garda style inline (display/flex/gap/color) — MASURAT, decizie ceruta
Masurat exact: 136 aparitii display:/flex/gap/color inline in ~15 fisiere (firme.js 53, cabinet 14, asistenti 10,
portal 7...). NU doar panoul D390 (reparat). Extinderea gardii = 136 flag-uri = verificator TOTAL 0 IMPOSIBIL fara
curatarea celor 136 (reveni pe decizia v2.11 "spacing inline = datorie acceptata", pt display/flex/color; spacing
gap/margin ramane acceptat). E workstream dedicat (15 fisiere, risc de eroare), NU un fix de ecran. RAPORTAT, garda
NEextinsa in acest commit (ar rupe TOTAL 0). De decis: curatare frontend-wide programata vs ramane datorie.

### 23.07.2026 Declaratii poz.1 — DOAR_SRL prea grosier pe cardul Declaratii (fals negativ, oglinda dimineata)
CONSTATARE: cardul "Declaratii" din fisa firmei (meniuFirma) era in DOAR_SRL -> ascuns COMPLET la PFA. Dar un PFA
datoreaza D112/D300/D394/D301/D390 -> contabilul nu le putea genera din fisa. Aceeasi clasa cu bug-ul de dimineata,
in OGLINDA: acolo fals POZITIV (PFA primea D101 ca restanta), aici fals NEGATIV (PFA nu putea genera D112).
DECIZIE: 'declaratii' SCOS din DOAR_SRL (firme.js:242). Cardul apare la orice tip_firma. Filtrarea FINA (D100/D101/
D406 dezactivate cu temei la partida simpla, restul selectabile) o face deja G1 in dropdown, prin neaplicabile_forma
- declaratiiPerFirma o cere o data la deschidere (firma fixa), aceeasi primitiva ca standalone, fara logica separata.
DOVADA: node --check; pytest 946; verificator TOTAL 0; functional PFA(tenant_001) -> selectabile d112/d205/d300/d301/
d390/d394, dezactivate d100/d101/d406.
RESTUL DOAR_SRL nemodificat (verificat justificat): jurnal/balanta/bilant/operatiuni = concepte de partida dubla.

### 23.07.2026 [RAPORT] Filtrarea cardurilor fisei = DOAR_SRL/DOAR_PFA hardcodat (firme.js), NU STRATURI_META
Constatare ceruta separat: cardurile Stocuri/Produse/Banca/Magazin/Centre de cost apar la PFA. Cauza: vizibilitatea
cardurilor din meniuFirma e guvernata de listele HARDCODATE DOAR_SRL/DOAR_PFA (firme.js:242-243), NU de STRATURI_META
(aceea guverneaza STRATURILE DE MIGRARE - straturi_pentru in migrare_api, alta filtrare). Apar la PFA fiindca NU sunt
in DOAR_SRL. Analiza: Stocuri (NIR/descarcare gestiune 371/607) + Centre de cost (analitic pe conturi) = concepte de
PARTIDA DUBLA -> filtrare INCOMPLETA (ar trebui DOAR_SRL, ca jurnal/balanta). Produse (nomenclator TVA), Magazin
(WooCommerce->facturi), Banca (import extras -> si RIP la PFA) = plauzibil aplicabile unui PFA platitor TVA/e-commerce.
Casa (5311) - la fel partida dubla, nementionat dar aceeasi categorie. NU e "ambele intentionat" - lista hardcodata
nu le include. NEREPARAT (raport). De decis daca Stocuri/Centre de cost/Casa intra in DOAR_SRL.

### 23.07.2026 Carduri pe firma — regim obligatoriu + filtrare prin regim_contabil (a 4-a sursa paralela eliminata)
DOAR_SRL/DOAR_PFA (firme.js) = liste hardcodate pe tip_firma = a 4-a sursa la aceeasi intrebare ("ce se aplica unei
firme de regim X"), dupa termene/semafor/neaplicabile_forma. Unificat prin regim_contabil (fapt UNIC).
DECIZIE (Costin, confirmat):
1. Fiecare card din meniuFirma.optiuni declara `regim` (ambele/simpla/dubla) OBLIGATORIU, fara default tacit
   (aceeasi clasa cu DEFAULT 'srl'/or "micro" eliminate azi). Garda CARD_REGIM in verificator (card fara regim =
   eroare) + DS cap.18, simultan. Dovada mutatie: scot regim de pe un card -> CARD_REGIM prinde.
2. Vizibilitate: optiuni.filter(o => o.regim==="ambele" || o.regim===t.regim_contabil). t.regim_contabil cu
   CONTRACT STRICT (throw daca lipseste, NU degradare tacita la "doar ambele" - doctrina P2). Calea termene->fisa
   propaga acum regim_contabil (ca tip_firma la P2): main.py /termene + portofoliu + termene.js.
3. Mapare: jurnal/balanta/bilant/operatiuni/stocuri/centrecost -> dubla; rip -> simpla; casa -> ambele (A, Legea
   70/2015 plafon PFA); declaratii -> ambele (fix); restul explicit ambele.
4. DOAR_SRL/DOAR_PFA STERSE.
DOVADA: pytest 946; verificator TOTAL 0 (CARD_REGIM 0, mutatie prinde); node --check firme/termene; functional
PFA(simpla) ascunde [jurnal,stocuri,balanta,bilant,operatiuni,centrecost], arata rip/declaratii/casa; SRL(dubla)
ascunde doar rip.
A (raport, DECIS ambele): Casa NU e partida dubla curata - face contare 5311 (partida dubla) SI verificare plafoane
(Legea 70/2015 art.1, se aplica PFA/II/IF fara exceptie). Vizibil la PFA. Filtrarea fina a operatiunilor 5311 din
interior = DE_FACUT (ca declaratii). Vezi DE_FACUT + DESIGN_SYSTEM cap.18.

### 24.07.2026 ecranVerificari ramane scoped pe coerenta bruta-lunara  (firme.js VC_VERIFICARI + verificator VERDICT_PARITATE + DS cap.20; commit ac7e135)
DECIZIE: ecranul „Verificari" (firme.js/ecranVerificari, endpoint /firme/{id}/verificari, vc BRUT pe luna) randeaza
DOAR coerenta bruta lunara — echilibru, trezorerie, documente_pozate, tva, note (+ stocuri, Intrastat din endpoint-uri
proprii). Cross-check-urile declaratie-vs-contabilitate (tva_incrucisat, d112_incrucisat, d390_incrucisat,
cota_tva_conformitate) sunt EXCLUSE explicit prin inventarul VC_VERIFICARI (marcate IGNORAT cu motiv) — apartin
exclusiv verdictului din Control fiscal (control_verdict.js).
TEMEI: acelasi endpoint trimite tot vc, deci cross-check-urile ajung si aici; dar „Verificari" e alt SCOP (coerenta
bruta pe o luna aleasa, navigabila prev/next) si alta interactiune decat verdictul „starea acum". A le randa ar dubla
constatarile verdictului pe un ecran cu alta intentie. Declaratia (nu omisiunea tacuta) le tine sub garda:
VERDICT_PARITATE (paritate randare) cere fiecare cheie vc ori randata, ori declarata aici — al doilea consumator pe
acelasi mecanism ca VC_RANDATE (control_verdict.js).
ALTERNATIVA RESPINSA: (a) consolidarea lui ecranVerificari in renderer-ul verdictului — ar reorganiza un ecran
distinct si ar aduce cross-check-uri nedorite acolo; (b) lasat necuprins de garda — ar ramane aceeasi omisiune tacuta
(clasa DANTE), doar nedeclarata. Ambele respinse: se DECLARA cu motiv, sub garda. Fara randare noua (nimic vizual nu
se schimba pe ecran).
LIMITA: garda garanteaza ca fiecare cheie e DECLARATA (randat/ignorat), nu ca directiva chiar randeaza. Daca decizia
de scop se schimba (cross-check-urile devin dorite in „Verificari"), se muta din IGNORAT in randat + se adauga
randarea. Colateral neatins: formatorul de data local din antet (padStart(luna)/${an}) ocoleste DATA_DIALECT —
DE_FACUT CARENTE 5.

### 24.07.2026 Recomanda cabinet vs client = doua features separate, nu divergenta  (recomanda.js + portal.js:ecranRecomanda; raport poz.5 CHECKLIST_BROWSER)
DECIZIE: „Recomanda" e implementat de DOUA renderere separate, ACCEPTAT ca separare legitima — NU de urmarit spre consolidare:
 - recomanda.js/randeazaRecomanda (cabinet + asistent) -> invita un CABINET; endpoint /recomanda + /recomanda/preview (cere_cabinet), max 20 adrese.
 - portal.js/ecranRecomanda (client) -> invita un ANTREPRENOR; endpoint /portal/recomanda + preview (cere_client), max 10 adrese.
TEMEI: audienta, endpoint, auth si limita DIFERITE. NU e clasa poziției 2 (un payload partajat randat divergent) — sunt
doua fluxuri distincte care doar poarta acelasi nume. Trimiterea efectiva e deja PARTAJATA pe backend
(_trimite_recomandari + _mesaj_recomanda_client_html), deci logica de trimitere are o singura sursa; doar prezentarea si
audienta difera.
ALTERNATIVA RESPINSA: consolidarea celor doua renderere intr-o primitiva UI comuna — ar cupla doua fluxuri separate pe rol
(cere_cabinet vs cere_client), cu texte/limite/endpoint diferite, pentru un castig mic. Duplicarea de prezentare
(textarea + preview + trimite + rezultate) e acceptata ca pret al separarii pe rol.
LIMITA: daca cele doua diverg in comportament de TRIMITERE (nu doar prezentare), se reconsidera. Backend-ul e deja unificat
pe trimitere, deci riscul e mic. Colateral reparat 24.07: recomanda.js:35 sanitizare inline (.replace(/[<>&]/g,"")) -> esc canonic.

### 24.07.2026 Editare produs — endpoint PUT pastrat (main.py:2224 PUT /produse/{produs_id}; produse_ecran.js)
DECIZIE: PUT /tenants/{id}/produse/{produs_id} NU se sterge ca endpoint mort; se construieste UI de editare (restanta).
TEMEI (corectat 24.07, dupa verificare la sursa): stergerea+recrearea unui produs pierde metadata cotei — `justificare`,
`categorie`, `sursa`, `confirmat` (produse L969) — care e rezultatul potrivirii AI si e argumentul in fata unui control
fiscal. Editarea (denumire, pret de lista, cota TVA) e operatiune legitima care trebuie sa pastreze aceasta metadata.
CORECTIE: temeiul initial invoca `articol_id` in podul factura->stoc si F144. FALS, verificat la sursa: `produse` si
`articole` sunt tabele complet separate, fara FK in niciun sens (produse n-are articol_id, articole n-are produs_id);
`articol_id` din factura_linii/miscari_stoc/retete_linii refera `articole`. DELETE FROM produse nu atinge niciun istoric.
Temeiul initial a fost formulat din memorie, nu verificat — incalcare a regulii 7 (verificare la sursa). Decizia (pastram
endpoint-ul) ramane, temeiul e altul.
ALTERNATIVA RESPINSA: stergerea endpoint-ului pe regula „fara cod mort" — respinsa pentru ca absenta UI nu dovedeste ca
functionalitatea e nedorita, iar marcatorul [p123_scot_butoane] e nedocumentat (istoric pierdut la snapshot cbf24ce;
verificat in DECIZII/ISTORIC/DE_FACUT/CHECKLIST si in build-ul vechi /opt/iconta — absent peste tot).
LIMITA: motivul scoaterii butoanelor ramane nerecuperabil din git/documente. Detalii + restanta UI: DE_FACUT.md, sectiunea
„Editare produs — UI lipsa (24.07)".

### 24.07.2026 Roluri pe /produse
DECIZIE: asistent = CRUD complet (confirma comportamentul actual); client = DOAR CITIRE (GET lista + POST potriveste).
Fara POST creeaza / PUT / DELETE pentru rol client.
TEMEI: nomenclatorul de produse e al cabinetului si alimenteaza cota TVA de pe facturi (produse.justificare/categorie/sursa
= argument la control fiscal). Asistentul e personal al cabinetului, lucreaza pe firmele alocate — acces legitim. Contul
gratuit de facturare (rol client, accounting_firm_id NULL) nu trebuie sa poata altera nomenclatorul cabinetului.
VERIFICAT LA SURSA 24.07: toate rutele /produse sunt pe cere_context (orice user autentificat, inclusiv client), cu garda
inline _schema_sau_404(ctx, tenant_id) → fara cross-tenant. Confirmat vizual pe rol asistent (DANTE): vede lista, are
„+ Adauga produs" si stergere — identic cu contul principal.
LIMITA: portalul client nu expune azi butoanele prin UI, deci nu e gaura activa, ci poarta deschisa. Implementarea
restrictiei e restanta (DE_FACUT.md).

### 24.07.2026 Delegarea validarii in coada — REPARAT  (main.py rute /coada/{id}/aproba|respinge|depune; commit c4cb8da)
DECIZIE: /coada/{id}/aproba, /respinge, /depune trec de la cere_rol("admin_firma") la cere_rol("admin_firma","angajat");
_are_permisiune(ctx, flag) din corp ramane poarta fina. /respinge primeste in plus check-ul _are_permisiune (nu avea niciunul).
TEMEI: dependenta prea stricta bloca angajatul cu 403 „rol insuficient" INAINTE ca poarta fina sa conteze, facand
_are_permisiune cod mort pentru asistenti. Frontendul (validat.js L76-92) randeaza butoanele pe FLAG → apareau si esuau.
Consecinta de produs: flagul „Poate valida" era decorativ, iar modelul patru-ochi promis pe banner („nimeni nu depune ce a
pregatit singur") era neindeplinibil prin asistenti — patronul valida ce pregatea tot el.
VERIFICAT: la sursa (3 straturi: buton validat.js L76-92, dependenta, helper main.py:5061), apoi curl real (asistent cu flag
200 „aprobata"; fara flag 403 „nu ai permisiunea de a valida", NU „rol insuficient"; patron fara regresie), apoi vizual pe
DANTE (asistentul aproba, randul trece in „APROBATE, DE DEPUS", apare corect „nu ai dreptul de depunere" — flagurile
valida/depune sunt independente). Commit fix: c4cb8da.
ALTERNATIVA RESPINSA: a lasa dependenta stricta si a filtra doar in frontend — ar fi pastrat _are_permisiune cod mort si
n-ar fi rezolvat delegarea reala; slabirea dependentei FARA _are_permisiune pe /respinge ar fi deschis o gaura (respingere
de catre orice angajat).
LIMITA: —

### 24.07.2026 Declaratie cu erori DUK in coada — AMANATA  (nedecis; DE_FACUT.md „Coada de validare")
DECIZIE: nedecisa (amanata). Fapt verificat vizual: o declaratie cu „Validatorul ANAF a gasit erori" poate fi trimisa in
coada (buton nerestrictionat) si primeste ecran de confirmare cu bifa verde „Trimisa in coada de validare", fara urma a
erorii. Backendul re-genereaza server-side dar NU re-valideaza DUK.
PROPUNERE (de confirmat): transparenta, nu blocaj. Butonul ramane activ (contabilul poate sti ca eroarea e falsa), dar
confirmarea nu mai afirma succes curat — arata „trimisa cu N erori de validare", iar coada evidentiaza randul. Atenuant
existent: badge „neverificat" apare pe rand si persista dupa aprobare.
ALTERNATIVA RESPINSA (provizoriu): poarta hard pe stare==="valid" — blocheaza cazurile in care eroarea DUK e fals-pozitiva.
LIMITA: decizia finala nu e luata; pana atunci ecranul de succes ramane inselator pe declaratiile cu erori. Colateral de
investigat separat: bug generare D300 iulie (atribut `cont` vid); etichetare perioada vs termen in coada (minor).

### 24.07.2026 Povestea lunara — conformitate afirmata pe date incomplete (REPARAT)
DECIZIE: promptul primeste restantele reale (datorate/lipsa din evalueaza_firma), nu doar
lista celor depuse; instructiunea hardcodata de reasigurare e eliminata; interdictie
explicita de a afirma "la zi / fara restante" cand lista de lipsa e nevida.
TEMEI: raportul lunar pleaca la client in numele cabinetului. Promptul impunea o afirmatie
de conformitate pe care sistemul nu o putea verifica — incalca principiul "verde se castiga
prin adevar, nu prin ajustare". Doua ecrane ale aceluiasi produs se contraziceau.
ALTERNATIVA RESPINSA: doar interdictie de ton, fara alimentarea cu date — modelul tot nu ar
fi stiut ce lipseste; testat efectiv, a extrapolat singur "firma este la zi", deci
interdictia fara date e insuficienta.
VERIFICAT: la sursa (prompt L78-86, _declaratii_depuse, evalueaza_firma), apoi vizual pe
DANTE (26 restante identificate corect, mentionate pe tipuri si perioade).

### 24.07.2026 Capacitate — pct_acceptare pe cohortă + etichete de perioadă (REPARAT); încărcarea per-asistent (AMÂNAT, decizie fondator)
REPARAT: pct_acceptare (capacitate_api.py, secțiunea "pe asistent") folosea `respinse` pe `respins_la>=luna` și
`pregatite` pe `creat_la>=luna` — ferestre diferite, deci `acceptate=pregatite-respinse` putea ieși NEGATIV
(respingeri în luna curentă ale unor declarații pregătite luna trecută → pct sub 0%). Fix: `respinse` numărat pe
ACEEAȘI cohortă (`creat_la>=luna AND respins_la IS NOT NULL`) → subset al `pregatite` → `acceptate>=0` prin
CONSTRUCȚIE, nu prin max(0). Plus etichete de perioadă în ecran (capacitate.js): "Pe asistent" = luna curentă,
"Timp mediu pe tip" = istoric complet (clasa `.cap-rol` existentă, fără hex).
AMÂNAT (întrebări de fond, de decis de fondator):
- `in_lucru` se atribuie pe `creat_de_id` → un asistent care DOAR validează/depune apare cu încărcare 0.
  Întrebare: "capacitate" = doar pregătire, sau tot fluxul (pregătire+validare+depunere)?
- `in_lucru` include starea `la_senior` → declarația așteaptă la senior, dar se numără la PREGĂTITOR.
  Întrebare: a cui e încărcarea când mingea e la senior? Opțiuni + implicații: (a) rămâne la pregătitor (owner-ul
  livrării) — subestimează seniorul; (b) trece la senior cât e `la_senior` (cine are acțiunea acum) — subestimează
  pregătitorul între timp; (c) se numără la ambii cu etichetă — dublă-numărare vizibilă.
TEMEI: semantica "încărcării" depinde de fluxul REAL de lucru al cabinetelor (cine e responsabil în fiecare stare),
necunoscut din cod — de decis de fondator pe baza modului real de lucru, nu unilateral din cod.
VERIFICAT: la sursă (capacitate_api.capacitate integral, query-urile per-asistent + timp); fix pct pe cohortă
verificat logic (respinse ⊆ pregatite).
VERIFICAT LA SURSĂ 24.07 — modelul de atribuire firmă↔asistent:
- Atribuirea firmă↔asistent EXISTĂ și e completă: `public.user_tenants` + `asistenti_api.py`
  (`atribuie_firma`/`elimina_firma`, bife în ecranul Asistenți, regula zero-firme). Populat real pe DANTE
  (user 34 admin_firma + 43 angajat au rânduri pe tenant_002). NU e de construit.
- Cele două axe există în date, dar Capacitate le confundă: `user_tenants` = cine RĂSPUNDE (atribuire),
  `creat_de_id` = cine A LUCRAT. Panoul grupează pe `creat_de_id`. Stadiul 1 = re-JOIN pe `user_tenants`,
  FĂRĂ schemă nouă → cost redus dramatic (reorientare de query, nu sprint).
- DECIZIE DESCHISĂ (fondator): "răspunde de firmă" = SET de asistenți (many-to-many, cum e acum, zero cod)
  sau RESPONSABIL PRINCIPAL unic (coloană/flag nou)? Setul e flexibil dar ambiguu pentru reputație/selecție
  (stadiul 2); responsabilul unic e clar dar impune un model care poate nu se potrivește cabinetelor ce împart
  o firmă. De decis ÎNAINTE de stadiul 2.
  DECIS 24.07: SET many-to-many (rămâne modelul actual, zero schemă nouă). Temei: reflectă realitatea cabinetului
  care crește (firmă complexă = mai mulți asistenți pe ea); owner unic ar fi rigid. Stadiul 2 va deriva contribuția
  per asistent din creat_de_id ÎN CADRUL setului, fără owner impus.
POZIȚIONARE STRATEGICĂ (fondator, 24.07 — apreciere a FONDATORULUI, marcată ca atare; NU verificare independentă în cod):
Capacitate e poziționat ca INSTRUMENT DE CREȘTERE a cabinetului, nu doar raportare internă. Fondatorul consideră un
GOL DE PIAȚĂ față de SAGA/Keez (evaluarea fondatorului, NEverificată în cod în această sesiune). Cererea e încă
NEVALIDATĂ — nu s-a confirmat cu cabinete reale că folosesc/plătesc pentru acest instrument; riscul principal înainte
de stadiul 2 = cererea nevalidată. Cele două stadii rămân cum sunt descrise mai sus (stadiul 1 = re-JOIN user_tenants
fără schemă nouă; stadiul 2 = contribuție per asistent din creat_de_id în cadrul setului).

### 25.07.2026 SPV mesaje (F128) — concluzia strategica corectata, blocaj tehnic neschimbat  (ARHITECTURA_SPV.md:77; CONCURENTA.csv iSpv.ro)
VERIFICAT azi (firul SPV):
- Keez NU transmite declaratii; are monitorizare mesaje SPV prin EXPERTI CECCAR cu certificate proprii (model de SERVICIU uman, nu tehnic cloud). Sursa: blog public Keez.
- Cele trei randuri din CONCURENTA erau capabilitati DIFERITE confundate intr-una: SAGA = transmitere directa (desktop+certificat); Keez = monitorizare SPV (serviciu/certificat); SmartBill = depunere + vector fiscal.
- F128 (monitorizare mesaje SPV) ramane AMANAT, motiv tehnic VALID: SPVWS2 cere mTLS/PKCS#11 certificat LOCAL, incompatibil OAuth (ARHITECTURA:21-22, :74). Reevaluare 17.08.2026.
- CORECTAT ARHITECTURA:77: premisa "niciun jucator cloud nu poate" era prea absoluta. Limita e pentru cloud FARA acces la certificat; cei care au mesaje SPV o fac pe cale de certificat (om sau agent), nu prin API cloud.
- CALE A TREIA identificata, NEDECISA: agent local / extensie browser care ruleaza unde e tokenul cabinetului -> ar ocoli mTLS FARA ca iConta sa detina certificate (pastreaza ARHITECTURA:6 "iConta NU detine certificat"). NU e decis, NU e planificat.
- DESCHIS: de investigat cum face iSpv.ro (ispv.ro/mesaje-spv) - mecanism neverificat.

ACTUALIZARE 25.07.2026 (mecanism iSpv VERIFICAT + decizii fondator) — la intrarea SPV mesaje (F128) de mai sus:
- iSpv Connector VERIFICAT (ispv.ro/termeni-si-conditii): componenta LOCALA preia sesiunea SPV autentificata cu certificatul PROPRIU al utilizatorului -> serverele iSpv sincronizeaza mesajele si depun declaratii. Cauza reala = CUSTODIA certificatului, NU cloud-vs-desktop, NU drepturi.
- F127 (depunere declaratii): "nu exista API" e ADEVARAT despre API, dar FALS ca imposibilitate - iSpv depune prin sesiune autentificata pe portal. De reconsiderat impreuna cu F128.
- GDPR: NU e blocant. Delegarea de sesiune e permisa cu temei + informare + masuri tehnice + contract de imputernicire -> trece in CERINTE DE PROIECTARE. Consecintele juridice sunt identice pentru noi si pentru iSpv si NU depind de numarul de firme din portofoliu.
- DECIZIE (fondator): agent local RESPINS in AMBELE variante (delegare de sesiune SAU descarcare locala). Motiv: cost permanent de distributie+suport pe statii necontrolate, fragilitate la schimbari de portal ANAF, contrazice pozitionarea "cloud" din MARKETING.md. NU e respingere tehnica - calea functioneaza, dar nu e a noastra.
- DECIZIE (fondator): iConta ofera PRELUCRAREA mesajelor SPV (clasificare, legare la firma, termen, alerta in semafor, arhivare la dosar), cu INCARCARE de catre cabinet. Descarcarea ramane alegerea cabinetului: manual din SPV, sau prin unealta terta procurata singur (ex. iSpv, care are API de integrare). iConta indruma NEUTRU, nu recomanda si nu garanteaza un furnizor anume.
- REZULTAT: daca ANAF deschide vreodata OAuth pe SPVWS2, se schimba doar SURSA DE ALIMENTARE - prelucrarea e deja construita.
- STATUT: prelucrarea = POSIBILITATE DESCHISA, neplanificata. NU se construieste fara DA explicit si fara verificarea de fezabilitate.

FEZABILITATE (verificat la sursa 25.07.2026) — REZULTAT NEGATIV pe punctul critic:
- Descarcare SPV = UNUL CATE UNUL (/listaMesaje listeaza in bloc, /descarcare?id ia cate unul — ARHITECTURA:56,58) -> incarcare MANUALA = FRICTIUNE REALA la volum.
- ZERO exemplare SPV reale pe server (find gol; declaratii_coada 0 transmise / spv_index NULL; doar mock-uri in teste) -> extractibilitatea textului NEestimabila fara un mesaj real procurat.
- F152 (raportari_ai = triaj sesizari), F164 (semafor pe verificatori FIXI), F042 (arhiva = bonuri OCR) sunt SPECIALIZATE, NU refolosibile generic pentru prelucrarea mesajelor SPV.
- CONSECINTA: "prelucrare cu INCARCARE MANUALA" NU e viabila in forma discutata. Ramane posibila DOAR daca alimentarea vine AUTOMAT (unealta terta cu API, sau OAuth pe SPVWS2 daca ANAF deschide).
- STATUT F128: ramane AMANAT. Nu mai exista cale de ocolire ieftina.

### 25.07.2026 Landing — card „Funcționalități" înlocuiește „Facturare gratuită"; pâlnie gratuită publică ÎNCHISĂ temporar  (login.js + stil.css; F203)
DECIZIE (pilot): cardul mare landing „Facturare gratuită" (SINGURUL punct de intrare UI spre înregistrarea gratuită self-service) e ÎNLOCUIT cu „Funcționalități" — deschide client-side cele 7 grupe. Fără URL nou (SPA fără rutare pe path); nav.deschide e shell autentificat, deci fereastra e replică VIZUALĂ a modalului DS.
CONSECINȚĂ: pâlnia de înscriere gratuită PUBLICĂ e ÎNCHISĂ temporar — DECIZIE DE PILOT, NU abandonare. Backend F153-F160 INTACT; doar intrarea de pe landing e scoasă. Reactivabilă oricând.
PRECIZARE: „cont gratuit" (firmă FĂRĂ cabinet) NU e „portal client" (client al unui cabinet). Portalul client e neschimbat; închiderea vizează DOAR pâlnia publică de cont gratuit.
LISTĂ (F203, actualizare azi): din pagina Funcționalități s-au scos F153 (Cont de facturare gratuită) + F160 (e-Factura SPV pentru contul gratuit) — nu afișăm funcții inaccesibile cât pâlnia gratuită e închisă; se readaugă la redeschiderea înscrierii (F154-F159 erau deja excluse). Corecție grupare: F187 (Export facturi WinMENTOR) mutat din Stocuri în Facturare — căzuse pe keyword-ul „articol" (perechea lui, F171 SAGA, era deja corect la Facturare).

### 25.07.2026 AWS Bedrock EU pentru Claude — DECIS: se migrează, dar DUPĂ pilot  (core/ai_client.py; nefacut)
DECIS (Costin): apelurile Claude se migrează de pe api.anthropic.com (SUA) pe AWS Bedrock cu profil de inferență EU. NU acum — prioritate DUPĂ lansarea pilotului.
MOTIV: elimină complet transferul extra-UE (imaginile de bonuri + datele financiare rămân în UE) → secțiunea SCC/DPF din documentația GDPR DISPARE.
EFORT: cod MIC — un singur punct de intrare (core/ai_client.py; toate cele 6 apeluri trec prin el, zero anthropic direct în afară). Se schimbă doar: clasa clientului (Anthropic → AnthropicBedrock, ~3 constructori de centralizat), ID-urile de model (claude-sonnet-4-6 → profil EU eu.anthropic.claude-...), credențialele (AWS key/secret + regiune în loc de ANTHROPIC_API_KEY). ACELAȘI SDK anthropic, ACELAȘI format messages.create. Efort REAL = operațional: cont AWS + acces Bedrock EU + activare model în regiunea EU + IAM + testare (OCR imagine + text) + comparație cost/latență.
PRERECHIZITE de verificat la implementare: (1) AnthropicBedrock există în SDK-ul instalat; (2) boto3 prezent (extra anthropic[bedrock]); (3) modelul dorit ARE profil de inferență EU pe Bedrock.
PÂNĂ ATUNCI: rămâne api.anthropic.com, acoperit de DPF + clauze standard (Anthropic e certificat EU-US Data Privacy Framework; DPA încorporat automat în termenii comerciali).

### 25.07.2026 Criptare la nivel de disc (LUKS) — DECIS: NU se implementează; risc asumat  (infra Hetzner)
DECIS (Costin): NU se implementează criptare de disc. Risc ASUMAT, documentat.
STARE (verificat la sursă): root sda1 = ext4 NEcriptat; PostgreSQL (/var/lib/postgresql/16/main) pe el; niciun crypto_LUKS / crypttab / dm-crypt. Deci CNP / IBAN / nume — pe disc ÎN CLAR.
MOTIV: vectorul pe care LUKS îl acoperă = accesul FIZIC la disc într-un centru de date Hetzner — probabilitate foarte mică. Costul = migrare de infrastructură pe sistem VIU (reinstalare sau volum criptat separat pentru directorul DB), cu risc operațional real.
COMPENSARE (documentată pentru art. 32): acces fizic controlat de Hetzner; criptare în tranzit (HTTPS/Let's Encrypt); control acces pe roluri; jurnal de audit; parole scrypt (OWASP); tokenuri SPV criptate Fernet; alertă pe acces anormal (F202).
DE REEVALUAT: dacă apare oricum o migrare de server, LUKS se face ATUNCI (efort suplimentar zero).
DE RIDICAT LA AVOCAT: dacă art. 32 GDPR + Legea 190/2018 cer explicit criptare la DEPOZITARE pentru CNP, decizia se schimbă.

### 25.07.2026 Retenție 1 an inactivitate — CLARIFICARE scop + problemă tehnică  (DECIZII:447; nefacut)
CLARIFICARE la decizia din 18.07 (Retenție cont gratuit inactiv): acoperă DOAR conturile GRATUITE (tenants.accounting_firm_id IS NULL, self-service fără cabinet). Conturile de CABINET (clienții contabilului) NU intră.
CONTEXT: pâlnia gratuită publică e ÎNCHISĂ azi (F203) → zero conturi vizate → NU e presantă tehnic.
DECIS: rămâne decizie VALIDĂ; se implementează ODATĂ cu redeschiderea înscrierii gratuite. NU intră în T&C ca promisiune ACTIVĂ până nu e implementată (altfel = promisiune nerespectată).
PROBLEMĂ TEHNICĂ (de rezolvat la implementare): users NU are coloană last_login (doar activ, creat_la). A deriva inactivitatea din audit_log e NESIGUR — audit_log are retenție 12 luni (F201), exact fereastra de inactivitate, deci s-ar șterge CHIAR înregistrarea de login necesară. SOLUȚIA corectă: coloană dedicată users.ultima_logare timestamptz, actualizată la fiecare login (fiabilă, supraviețuiește retenției audit_log).

### 26.07.2026 Marca „iConta.eu" — gardă BRAND_EU; SAF-T exclus; „Admin iConta" rămâne  (verificator_conformitate.py BRAND_EU; DESIGN_SYSTEM.md cap.21; MARKETING.md cap. BRAND)
Regula de brand (MARKETING.md: marca se scrie PESTE TOT „iConta.eu", fără excepții în material public) a primit gardă mecanică **BRAND_EU** în verificator + capitol în DS (cap.21). Scop scanat: frontend (`static/**/*.{js,mjs,html}`) + literalele publice de email din backend (`main.py`, `notificari_scadenta.py`, `observare.py`). Semnalează `iConta` neurmat de `.eu`; al doilea assert `iConta.eu.eu`=0.

Două decizii de EXCLUDERE (listă albă, cu motiv în cod):
- **SAF-T `<SoftwareCompanyName>` / `<SoftwareID>` (core/d406.py:418-419) NU se ating.** Nu-i cosmetică: e identificarea softului emitent către ANAF în header-ul SAF-T (D406). „iConta" acolo e identitatea tehnică declarată, nu marca de marketing; schimbarea ar fi o decizie fiscală separată (se verifică contra structurii SAF-T, nu se presupune). `d406.py` e ținut ÎN AFARA scopului scanat; garda `<SoftwareCompanyName>` rămâne defensivă în listă albă dacă fișierul intră vreodată în scop.
- **„Admin iConta" rămâne „Admin iConta", nu „Admin iConta.eu".** E numele propriu al panoului de administrare (breadcrumb, antet, mesaje 403 „Doar Admin iConta"), tratat ca substantiv de produs, nu ca apariție a mărcii. „Admin iConta.eu" ar citi ciudat și dublează sufixul într-un nume compus. Garda îl sare per-apariție.

Restul materialului public — inclusiv alertele INTERNE (`[iConta]` prefix subiect, „iConta Alerte" nume expeditor), emailurile ops „Alerta iConta – sanatate server" și titlul tehnic FastAPI „iConta API" — a fost normalizat la „iConta.eu". Verificat ÎNAINTE la sursă că nu depinde nimic funcțional de aceste string-uri: cheia de dedup a alertelor e pe câmpuri structurate (`alerte_emise(alerta_id,prag)`, `alerte_acces_dedup.cheie=user_id`, `observare.trebuie_trimisa(cheie)`), NU pe subiect; niciun test nu asertează pe ele; titlul API nu e consumat de clienți generați (nicun SDK/swagger în repo). Normalizate 21 de literale rămase în main.py+observare.py (welcome, magic-link, portal-body, asistent, recomandare — scăpări de la corecția precedentă — plus internele de mai sus).

### 26.07.2026 Contul de facturare gratuită — ELIMINAT DEFINITIV din produs (portalul clientului INTACT)
Contul de facturare gratuită (F153-F160 + gărzile de coliziune F185/F186) a fost scos definitiv. Pâlnia
publică era deja închisă pe 25.07 (cardul de landing înlocuit cu Funcționalități, F203); acum se scoate și
CODUL, nu doar poarta de intrare.

DE CE: produsul se vinde CABINETELOR de contabilitate. Contul gratuit era o firmă FĂRĂ cabinet
(`accounting_firm_id NULL`, user rol `client`, tenant propriu) care emitea singură — nu are consumator în
modelul de preț (cabinetul e clientul plătitor; o firmă fără cabinet nu intră în ofertă). 0 conturi gratuite
reale în DB la momentul eliminării (0 tenanți `accounting_firm_id NULL`, 0 useri client fără cabinet) → zero
migrare, zero date pierdute.

CE S-A SCOS (verificat la sursă întâi, hartă arătată înainte de a atinge): rutele `/public/register-gratuit`,
`/admin/activitate/conturi-gratuite`, `/admin/conturi-gratuite/{id}/suspenda|reactiveaza`, `/admin/coliziuni-cui`
(F186); `auth_api.inregistreaza_cont_gratuit` (cu gardul invers F185); sub-logica `coliziune_gratuit_v1` din
`tenant_provisioning` (F092); ramura gratuit din `spv_principal` (XOR → o singură cale: cabinetul); ramurile
`_eGratuit()`/`e_gratuit`/`opt.gratuit` din portal.js/emitere/facturi_ecran; segmentul „gratuit" din anunțuri
(admin); ecranul de înregistrare `randeazaInregistrareGratuita` (login.js, deja orfan); `admin_gratuite.js`
(șters); breadcrumb-ul gratuit din navigator.

VOCABULARUL NOU (ca să nu se confunde la o eventuală revenire): NU mai există „cont gratuit" ca produs.
Rolul `client` înseamnă de-acum EXCLUSIV **portalul clientului** = o firmă gestionată DE un cabinet, care
intră la `/portal/bon` să vadă/emită/pozeze. Distincția istorică „gratuit vs. client de cabinet" (ambele rol
`client`, DECIZII 18.07 F161) dispare: orice `client` are cabinet.

CE NU S-A ATINS (dovedit funcțional): **portalul clientului** — `/portal/bon` testat real după modificare;
provisioning-ul de cabinet (F092 core) și pre-completarea ANAF la „Adaugă firmă" (F188) rămân, doar cu calea
gratuit scoasă din ele; `woo_ecran.js` (WooCommerce) rămâne, folosit de cabinet din firme.js. SPV: singura
atingere pe subsistem = ramura gratuit din `spv_principal` (acceptată explicit ca simplificare a XOR-ului),
dovedită cu cele 23 de teste SPV + probă reală pe conector (`apel_anaf` TestOauth/hello).

FUNCTIONALITATI.csv: F153-F160 + F185/F186 marcate `ELIMINAT 26.07.2026` cu motiv (rândurile RĂMÂN, istoricul
nu se pierde); F092/F188 rămân LIVE cu notă „sub-logica gratuit scoasă". Pagina publică Funcționalități:
număr NESCHIMBAT (141) — pozițiile gratuit erau deja excluse din pagină (F203).

### 27.07.2026 [EROARE PROPRIE + REVOCARE] d205_beneficiari readus gresit in template

Am declarat "D205 rupt pentru 2 din 3 firme" pornind DOAR de la structura DB (tabelul
exista doar in tenant_002), fara sa verific consumatorii in cod. Am adaugat tabelul in
tenant_template.sql si l-am creat pe tenant_001/003 (commit 74e87fe). Am acuzat pe nedrept
gardul F165 de "blind spot".

FAPT: tabelul are ZERO consumatori. core/d205.py citeste din `asociati` + rulaj 457 pe
inregistrari_linii. Decizia din 23.07 (cod mort eliminat, tabelul ramane extra informativ
pe tenant_002) era CORECTA, iar gardul si-a facut treaba.

REVOCAT: git revert 74e87fe + DROP pe tenant_001/003. Starea dinainte restaurata.

LECTIE: absenta unui tabel dintr-un tenant NU dovedeste ca ceva e rupt. Ipoteza "lipseste
deci e defect" cere verificarea consumatorilor INAINTE de orice reparatie - aceeasi regula
de verificare-la-sursa, aplicata si structurii de date, nu doar valorilor fiscale.

### 27.07.2026 D406 SourceDocuments: linii REALE + masti scoase din pull()

CONTEXT: commitul efe73d7 ("D406 nedepunabil: corectez claim-ul + notez gap-ul") a scris
in d406.py "Vezi DECIZII 27.07" DAR nu a scris intrarea in registru. Referinta era moarta;
DECIZII.md e citit de raportari_ai.py ca baza de cunostinte. Se repara aici.

DEFECT DOVEDIT pe date reale (tenant_002, iunie 2026): SourceDocuments emitea o singura
linie SINTETICA per factura - cantitate=1, pret_unitar=net, um=H87, descriere=numele
partenerului, cota dedusa din antet. Factura 7 "Deseuri fier vechi": in DB 1000 kg x 5,00
lei; in SAF-T iesea 1 buc x 5000 lei. Cantitate, UM si descriere FALSE catre ANAF. Pe
deseuri (taxare inversa) cantitatea nu e detaliu decorativ.

Al doilea defect, latent: cota dedusa din antet (tva/net*100) da o cota MEDIE pe factura
cu cote mixte (21%+11%) -> TaxCode care nu corespunde niciunei linii. Invizibil azi (toate
facturile au o linie), real la prima factura cu doua cote.

REPARAT: pull() citeste factura_linii (descriere/um/cantitate/pret_unitar/cota_tva), o
linie SAF-T per linie de factura, TaxCode pe cota liniei. uom_unece() exista din 16.07 si
era SCRISA SI NEAPELATA aici - 'buc'/'kg' din DB nu sunt coduri UN/ECE, se mapeaza.

MASTI SCOASE: cele doua `except: pass` din pull() (note + facturi) devin re-ridicare cu
context. Fara asta, reconcilierea adaugata mai jos ar fi fost inghitita - orice garda pusa
deasupra unei masti e decorativa.

GARDA NOUA: liniile trebuie sa reconcilieze cu antetul (toleranta 0,01). Divergenta tacuta
intre doua surse ale aceleiasi facturi = eroare, nu detaliu. Factura fara linii primeste
descrierea "Factura fara detaliu de linii" - semnal in XML, nu mimare de detaliu real.

NEATINS: Payments ramane gol. Nu e ascundere - chitante si casa_operatiuni au ZERO randuri
in toti tenantii; nu exista date de plati de raportat. XSD nu pune minOccurs pe Payments
(deci implicit obligatoriu), dar experimentul pe DUK din 16.07 arata ca sectiunea goala e
RESPINSA si absenta e ACCEPTATA. Se reia cand exista prima plata reala.

### 27.07.2026 D406 nu s-a validat NICIODATA din aplicatie (an/luna nepasate la duk.valideaza)

FAPT: main.py chema _duk.valideaza(xml, tip) FARA an/luna. D406 e SAF-T, se valideaza cu
DUKIntegrator_AnLunaUI.jar care le cere ca parametri; fara ele _valideaza_saft intoarce GRI
intotdeauna. Butonul de validare D406 n-a validat nimic vreodata - desi jar-ul, jre8
(1.8.0_492) si calea sunt corecte si functionale.

DE CE N-A PRINS NIMENI: verdictul gri e ONEST ("XML generat, dar NU validat la ANAF", cu
temei). Nu a mintit niciodata cu verde. Un gri permanent arata insa ca validator lipsa, nu
ca apel gresit - si nu exista test care sa lege ruta de semnatura ceruta de validator.

DOVADA ca XML-ul e bun: DUKIntegrator_AnLunaUI -v D406 pe tenant_002/iunie 2026 ->
"Validare fara erori", r.txt=ok. Inclusiv cu structura noua (linii reale, commit 426fe97)
SI cu o factura sparta in doua linii (InvoiceLine=2, DUK valid) - probata pe date fabricate
in tranzactie cu rollback, pentru ca in datele reale TOATE facturile au exact o linie:
ramura multi-linie era scrisa si niciodata executata.

REPARAT: an/luna se paseaza din body. GARDA: test_ruta_valideaza_trimite_an_si_luna citeste
main.py si cere an=/luna= pe fiecare apel _duk.valideaza, cu extragere pe paranteze
ECHILIBRATE.

TREI LECTII DESPRE GARZI, toate traite azi la ACEEASI garda:
1. Prima versiune folosea regex [^)]* si pica pe cod CORECT - se oprea la prima paranteza
   inchisa din body.get("an"). Garda cu fals-pozitiv e la fel de inutila ca una cu
   fals-negativ.
2. A doua crapa cu NameError (re neimportat) - deci "pica" pe orice, inclusiv pe mutant.
   Testul de mutatie a trecut FALS. Un test care eroreaza nu dovedeste nimic: mutatia
   trebuie sa verifice MOTIVUL esecului, nu doar ca a esuat.
3. A treia data mutatia a raportat FAIL desi garda functiona: verificarea citea
   `pytest -q | tail -3`, unde mesajul e trunchiat la "AssertionEr...". Verificarea unei
   garzi trebuie sa citeasca output COMPLET (--tb=long in fisier), nu coada trunchiata.

### 27.07.2026 D406: ultimele 4 masti din pull() (nomenclatoare) - si de ce le ratasem

Dimineata am scos 2 masti din pull() (note + facturi) si am declarat fisierul curat. Erau
6. Cele 4 ramase acopereau plan_conturi, clienti, furnizori si derivarea partenerilor din
facturi - la cateva linii distanta de cele reparate.

DE CE PROBA INITIALA A PARUT SA LE ABSOLVE: redenumind plan_conturi, generarea a esuat
zgomotos - deci "pare reparat". De fapt masca inghitise eroarea ca de obicei; in PostgreSQL
un query esuat OTRAVESTE tranzactia, asa ca a crapat blocul URMATOR (cel reparat dimineata),
cu mesajul "citirea notelor a esuat". Cauza reala ascunsa sub un mesaj gresit - exact clasa
reparata azi cu ValueError neinvelit. Inainte de reparatia din amonte, toate 4 ar fi inghitit
tacut -> registru de conturi GOL intr-un XML valid structural.

REPARAT: fiecare masca devine RuntimeError cu cauza proprie. Dovedit prin mutatie pe date
reale (rename tabela in tranzactie cu rollback): plan_conturi -> "citirea planului de conturi
a esuat"; clienti -> mesajul lui. Generarea normala: 182 conturi, DUK valid.

LECTIE: "am scos mastile din fisierul X" nu e o afirmatie verificabila fara numarat. Numarul
de masti ramase se tipareste in aceeasi comanda cu reparatia.

### 27.07.2026 Joburile de fundal esuau TACIT — ambalaj comun `core/cron.py`

FAPT: crontab-ul nu are MAILTO si serverul n-are MTA local (verificat: `which sendmail mail`
-> nimic). Cele 7 joburi cron scriau in fisiere de log pe care nu le citeste nimeni. Un job
mort arata identic cu unul care n-a avut nimic de facut - dovedit chiar azi: woocommerce.log
tacea de 12 zile si a fost nevoie de investigatie ca sa se stabileasca daca e defect (nu era:
wc_url e NULL in toti tenantii).

GRAVITATE: joburile emit facturi recurente, trimit notificari de scadenta, detecteaza acces
anormal (securitate, la 15 min) si aplica retentia GDPR. `facturi_recurente._main` n-avea
niciun try/except: un esec la primul tenant oprea jobul pentru TOATE firmele.

DOCTRINA EXISTA DEJA, scrisa in iconta-backup.sh: "Off-site care esueaza TACIT e mai rau
decat lipsa lui -> se logheaza + alerteaza" (FAIL_PRAG=2, email Brevo). Singurul job pe
systemd o respecta; cele pe cron, nu.

DECIZIE: ambalaj Python unic `core/cron.py` (`ruleaza(nume, fn)`), NU wrapper shell si NU
migrare la systemd timers. Motive: (a) canalul de alertare + throttling traiesc deja in
observare.alerteaza, iar shell-ul n-ar avea acces la ele - regula "nu construi canal paralel"
(gdpr_cerere.py); (b) migrarea cron->systemd e schimbare de infrastructura, se decide separat.
Ambalajul: traceback in log + alerta cu throttling pe cheie + exit 1. Pe succes tipareste
marca de timp si durata, ca tacerea sa nu se mai confunde cu moartea.

ALERTA NU MASCHEAZA ESECUL: daca trimiterea alertei crapa, se tipareste "ALERTA NETRIMISA"
si se iese TOT cu 1. Un canal care inghite eroarea pe care trebuia s-o semnaleze ar fi
aceeasi clasa cu `except: pass`.

GARDA: `core/test_cron.py` - patru teste, dintre care unul mecanic verifica sa fiecare din
cele 7 module din crontab CHEAMA cron.ruleaza. Un job nou nesupravegheat pica suita.

LIMITA DECLARATA: nu prinde jobul care nu porneste deloc (cron oprit, reboot, crontab
stricat). Heartbeat/deadman = task deschis in DE_FACUT.

### 27.07.2026 Valori fiscale stricate deveneau tacit ZERO (d112/d300/d390)

FAPT: `_d112int`, `d300._int` si `d390._int` aveau `except: return 0`. Orice valoare
neconvertibila devenea 0 lei intr-o declaratie depusa la ANAF, fara niciun semnal.

CEL MAI PERICULOS CAZ nu e textul evident gresit, ci `"12,5"` - un numar scris cu VIRGULA
zecimala romaneasca, plauzibil intr-un import sau intr-un camp completat de om. Iesea 0.
La fel: nan, infinit, lista, dict. Iar in d300 o `pro_rata` prezenta dar invalida devenea
100% - deducere INTEGRALA declarata acolo unde firma are drept partial.

TIPARUL CORECT EXISTA DEJA: `d205._i` si `d101._i` fac aceeasi conversie FARA masca. Nu s-a
inventat o regula - s-au aliniat trei functii la cea deja folosita.

REGULA: ABSENTA e legitima, INVALIDUL e eroare. None/"" -> 0 (un camp optional negol nu e
greseala; `s.get("motiv_exceptare")` lipseste normal). Orice altceva neconvertibil ->
ValueError cu campul si valoarea in mesaj.

LOC: `core/numere.py`, langa `numar()`. Prima varianta o pusesem in `common.py` fara sa
verific ca `numere.py` exista - iar acel fisier se declara explicit "sursa UNICA pentru
parsarea numerelor" si poarta in docstring chiar lecția asta (extras din 9 copii pe 15.07,
dintre care 6 transformau "(200)" in 0.0 tacut). Mutata.

DE CE NU SE CONTOPESC cu `numar()`: numar() parseaza INTRARE UMANA (formate RO/EN, paranteze
contabile, sufixe "lei") si intoarce float; numar_fiscal() primeste o valoare care INTRA
INTR-O DECLARATIE, intoarce Decimal (float pe bani pierde precizie la insumare) si respinge
nan/inf/bool, pe care numar() le lasa sa treaca. "12,5" e VALID la import si INVALID la
generare. Doua roluri, doua reguli, acelasi fisier.

DOVADA ZERO REGRESIE: D112/D300/D390 pe tenant_001 si tenant_002 (iunie 2026), inainte si
dupa, comparate prin SHA256 + diff pe continut - identice. Plus test de regresie ca
rotunjirea aritmetica din D112 (112.5 -> 113) e neatinsa.

LECTIE DE METODA: prima verificare a "zero regresie" folosea `hash()` pe string - randomizat
per proces in Python, deci compara doua procese diferite si a raportat 6 diferente FALSE
(lungimile erau identice, ceea ce trebuia sa ma puna pe ganduri). Poarta a blocat corect
commitul. Comparatia de artefacte se face pe SHA256 sau diff, niciodata pe hash().

NEATINS DELIBERAT: rotunjirea din D390 foloseste `round()` (bancara). Daca ANAF cere
aritmetica si acolo, e schimbare FISCALA - se verifica la sursa. Task in DE_FACUT.

### 27.07.2026 Gard mecanic pe autentificarea rutelor (`core/test_rute_autentificate.py`)

CONTEXT: auditul manual din aceeasi zi a gasit 375 de rute in main.py, 17 fara `Depends` -
toate public legitim. Curat, dar nimic nu impiedica o ruta noua nepazita sa treaca
neobservata: nu se vede in UI, nu strica niciun test, nu apare in niciun log.

CE A RATAT AUDITUL MANUAL: 3 rute din `core/spv_rute.py`, declarate cu `@app.get` in
INTERIORUL functiei `monteaza(app, ...)` - proiectul nu foloseste APIRouter, deci rutele
nu sunt toate la nivel de modul. Garda scaneaza ambele fisiere.

DECIZIE: lista `PUBLICE` e o lista de HOTARARI, nu de constatari - fiecare intrare poarta
motivul pe linie (de ce ruta aceea NU poate avea auth). Verificata si invers: o intrare
care nu mai corespunde unei rute fara auth PICA, ca lista sa nu acumuleze acoperire moarta.

`/anaf/oauth/callback` ramane public prin necesitate: ANAF redirecteaza acolo si nu are cum
sa poarte sesiunea noastra; e aparat de `state` semnat.

IMPLEMENTARE PE AST, NU REGEX: un regex pe semnatura se opreste la prima paranteza inchisa
si rateaza `Depends(cere_rol("a","b"))` dupa un `Body(...)` - exact greseala facuta de trei
ori azi. Exista test de regresie dedicat pentru cazul asta.

LIMITA DECLARATA (scrisa in docstring si in GARZI.md): verifica PREZENTA dependentei, nu
CORECTITUDINEA ei. O ruta de cabinet care cere din greseala `cere_client` trece. Nu acopera
IDOR. Ambele raman in lista de garduri lipsa.

DOVADA: mutatie pe cod REAL - ruta `/mutant/scurgere` adaugata in main.py, garda a picat cu
calea si linia in mesaj; main.py restaurat dupa.

### 27.07.2026 Măști peste query: `except: pass` -> înghițit, dar NU tăcut + gard mecanic

FAPT: 63 de handlere `except` cu corp mut in tot repo-ul, dintre care 15 peste un QUERY.
Un query rupt sub o masca produce zero randuri, iar generatorul scoate o declaratie VALIDA
STRUCTURAL si GOALA - clasa de defect care a produs aproape tot ce s-a gasit in iulie
(d406 GeneralLedgerEntries gol pentru orice firma; d406 SourceDocuments fara facturi desi
existau 5 reale).

JUDECATA PE FIECARE: toate cele 15 sunt "efect secundar care nu trebuie sa opreasca operatia
principala" - alegere CORECTA. Un audit_log care crapa nu trebuie sa impiedice login-ul.
Problema nu era inghitirea, era TACEREA: nimic, nicaieri, nu spunea ca s-a intamplat.

CAZUL CARE SCHIMBA GRAVITATEA: 5 dintre masti sunt pe scrierea in `public.audit_log` - chiar
sursa pe care o citeste `core/alerta_acces.py` ca sa detecteze acces anormal. Daca scrierea
esueaza tacit, gardul de securitate raporteaza linistit "0 verificati" pe o baza care nu se
scrie. O masca tacuta poate dezactiva un gard fara ca nimeni sa afle.

DECIZIE: nu se scot mastile, se fac ZGOMOTOASE. `observare.esec_secundar(eticheta, e,
alerta=False)` - log intotdeauna, alerta doar unde tacerea are cost legal sau de securitate
(evidenta prelucrarilor GDPR, provisionare esuata). Alerta pe orice ar produce zgomot, iar
un canal zgomotos se ignora - alt fel de tacere. Corpul original al handlerului e PASTRAT
(inclusiv `return None`), logul se adauga ca prim rand: zero schimbare de comportament.

GARD: `core/test_masti.py` - scan AST pe tot repo-ul. Orice `except` mut peste un query pica.
Escape hatch explicit: marcajul `# MASCA MOTIVATA: <motiv>`, pentru cazurile unde tacerea
chiar e decizia corecta. Patru teste, dintre care unul de mutatie pe cod real si doua care
verifica exact granita (marcajul scuteste; un handler care logheaza nu e masca).

LIMITA DECLARATA: acopera doar mastile peste QUERY. Cele peste conversii numerice au fost
tratate separat (core/numere.numar_fiscal). Nu verifica daca eticheta e corecta, doar ca
handlerul spune ceva.

RIDICAT, NEREZOLVAT: `main.py:1063` inghite `provision_tenant` in `register`. Daca
provisionarea crapa, raspunsul e SUCCES si userul ramane cu cont fara firma. Facut zgomotos
+ alerta, comportamentul NESCHIMBAT - e decizie de produs, in DE_FACUT.

### 27.07.2026 `SELECT *` + absență tratată ca zero = D112 cu salarii ZERO, tăcut

CUM A IESIT LA IVEALA: construind teste pe `pull()` - granita cod<->baza, netestata pana azi.
Cele ~175 de teste pe generatoare sunt toate PURE (cheama calcul_dXXX/build_xml cu fixturi in
memorie) si nu ating schema. Un test de mutatie a picat: `d112.pull` NU crapa cand o coloana
disparea.

FAPT DOVEDIT pe schema temporara cu ROLLBACK: cu `salariu_brut` redenumita, D112 a emis 1333
caractere cu suma 0, in loc de 1890 cu 5000. Declaratie depusa la ANAF cu salarii ZERO, fara
niciun semnal.

MECANISMUL, si de ce e insidios: `SELECT *` NU crapa la coloana lipsa - query-ul reuseste si
randul iese pur si simplu fara cheia aceea. Apoi `s.get("salariu_brut")` da None, iar
`numar_fiscal(None)` intoarce legitim 0 (regula de azi: absenta e legitima, invalidul e
eroare). Gaura apare EXACT INTRE DOUA COMPORTAMENTE CORECTE: SELECT * tolerant si absenta
tratata ca zero. Niciuna dintre reguli nu e gresita separat.

REPARAT: `common.cere_coloane(rand, chei, unde)` - verifica PREZENTA cheii, nu valoarea.
`salariu_brut = 0` ramane legitim (salariat in concediu medical toata luna); `salariu_brut`
INEXISTENT nu e. Aplicata in `d112.pull` cu `_COLOANE_SALARIAT` = contract explicit cu schema.
Dovedita prin mutatie in ambele sensuri: cu garda -> ValueError care numeste coloana; fara
garda -> testul pica.

LIMITA DECLARATA: garda verifica randurile CITITE, deci pe o tabela GOALA trece - o coloana
disparuta pe o firma fara salariati nu se semnaleaza. Prima versiune a testului de mutatie
picase exact asa (fixtura nu insera niciun salariat), ceea ce a scos limita la iveala.

CE NU S-A FACUT si de ce: (a) nu s-a atins `numar_fiscal` - absenta chiar e legitima pentru
campuri optionale (`motiv_exceptare` lipseste normal); (b) nu s-a inlocuit `SELECT *` cu lista
de coloane - ar fi insemnat sa ghicesc lista completa fara sa citesc tot modulul.

DOUA ARTEFACTE PROPRII, consemnate: in prima proba am citit `sal[0].get("salariu_brut")` si am
raportat `brut=None` - dar `pull` intoarce dicturi TRANSFORMATE, cu cheia `brut`. Concluzia a
stat in picioare pentru ca dovada reala era DIFERENTA DE XML, nu print-urile.

ZERO REGRESIE: D112 pe tenant_001 si tenant_002, SHA256 identic cu referinta.

RAMAS DESCHIS: aceeasi constructie `SELECT *` in d394, bilant_api, rip_api, stocuri_cv_api,
reconciliere_api, jurnal_api, salariati_api. Vezi DE_FACUT.

### 27.07.2026 Poarta pe declaratia GOALA (DA Costin) — `.caseta-poarta` inainte de depunere

PROBLEMA: o declaratie goala LEGITIMA (firma fara activitate in perioada) si una golita de un
query rupt arata IDENTIC - acelasi XML valid structural, aceleasi zero randuri. DUKIntegrator
nu poate face diferenta: un D390 cu zero operatiuni e corect structural. Toata ziua de 27.07
a fost despre exact clasa asta (d406 cu registru gol, D112 cu salarii zero).

DECIZIE DE CONTINUT — poarta INTREABA, nu sfatuieste: mesajul NU spune care declaratie se
depune pe zero si care nu. Aia e afirmatie FISCALA si cere verificare la sursa oficiala
(regula valorilor fiscale). Poarta cere omului sa confirme FAPTUL ("firma n-a avut activitate
in perioada"), nu regula. Nu blocheaza depunerea pe zero - e obligatie reala pentru multe
declaratii - dar nu o mai lasa sa treaca tacut.

DS cap.5, alegerea tiparului: `.caseta-poarta` (v2.14, chihlimbar #fbf7ee), NU `.caseta-atentie`.
DS spune explicit ca "rosul ramane EXCLUSIV pentru atentionare/actiune distructiva" - o
declaratie goala nu e distructiva. Poarta e definita ca "intrebare OBLIGATORIE inainte de o
actiune consecventa... raspunsul e cerut INAINTE de actiune si NU se poate sari" - exact cazul.
Butonul "Trimite in coada" e INLOCUIT de poarta cand e gol, nu adaugat langa (nu se poate sari).

NUMARATOAREA, intr-un singur loc: `declaratii_api.numar_operatiuni(tip, res)`. Nu s-a atins
niciun generator si niciun dataclass - functia citeste ce exista deja (nr_opi la d390,
op_efectuate la d394, listele la d301/d205/d100/d710/d406, randurile nenule la d300).

ONESTITATE: None, NU zero, pentru ce nu se poate numara. `d112.genereaza` intoarce o LISTA de
avertismente (nu dataclass); `d101` lucreaza pe solduri si n-are notiunea de operatiuni. Un tip
nou nemapat da tot None. "Nu stiu" nu se falsifica in "zero" - aceeasi regula ca verdictul GRI
de la validator. Altfel poarta ar aparea la fiecare D112 si ar deveni reflex, adica inutila.

LIMITA DECLARATA: poarta se vede doar in ecranul de declaratii (pas 2 -> pas 3). Ruta POST
/coada genereaza din nou declaratia si NU are poarta - un apel direct de API trimite pe zero
fara intrebare. Acceptat: poarta e ajutor pentru om, nu control de integritate; controlul e
gardul din cod.

### 27.07.2026 Consolidare: o singura aplicatie, un singur venv, un singur domeniu

CERUTA de Costin: "vreau sa inceteze asta, vreau sa fie ordine". Traiau in paralel: buildul
vechi /opt/iconta (port 8000, serviciu inactiv) SI buildul viu ~/iconta_nou (8010), doua
domenii, doua servicii systemd, configuri nginx duplicate, .bak-uri risipite.

CAPCANA care a impus ordinea pasilor: /opt/iconta NU era doar buildul vechi - acolo traia
VENV-UL din care rula aplicatia VIE (ExecStart=/opt/iconta/venv/bin/uvicorn, plus toate cele
8 joburi cron). Un `rm -rf /opt/iconta` ar fi oprit productia instant, iar backupul nu l-ar
fi adus inapoi: backupul e pg_dump pe baza, nu pe fisiere.

ORDINEA: venv nou in ~/iconta_nou (pachete identice, dovedit prin diff pe pip freeze) ->
POARTA 1 (aplicatia se importa + suita verde pe venv-ul nou) -> mutat systemd + crontab ->
POARTA 2 (site-ul raspunde 200, poarta de azi prezenta in JS-ul servit) -> ARHIVAT buildul
vechi ca tar.gz in /var/backups/iconta/arhiva (regula "buildul vechi e sursa de adevar
istorica" din 15.07 - nu se pierde, doar nu mai sta in cale) -> STERS.

SCOS: /opt/iconta, serviciul iconta.service, /etc/nginx/sites-available/nou-iconta si toate
.bak-urile de acolo, .bak-urile din repo, BRIEF_CODE_*.md (mutate in _arhiva_briefuri).
RAMAS INTENTIONAT: /opt/duk (validatorul oficial ANAF, folosit de core/duk.py) si ~/duk.

BACKUP EXTINS: `iconta-config-backup.sh` (zilnic 03:15) salveaza ce NU e nici in git, nici
in pg_dump: ~/.iconta/*.env (secrete), unitatile systemd, configurarile nginx, crontab-ul,
scripturile din /usr/local/bin. Fara ele, un server nou se reconstruia din memorie. Costin
ceruse un al doilea server la Hetzner pentru asta; raspuns: un al doilea server ar fi exact
dublura de eliminat (inca o masina de actualizat si tinut in sincron), iar problema reala -
configurarile nesalvate - se rezolva extinzand backupul care exista deja.

### 27.07.2026 D300/D301: verificarea de profil era scrisa dar NU era poarta

GASIT prin verificarea VIZUALA a portii de declaratie goala (Costin, pe iconta.eu): D300 pe
PFA TEST a trecut de poarta, dar validatorul ANAF l-a respins cu "eroare atribut: banca:
atribut prezent dar vid nepermis".

FAPT: `d300.valideaza(res)` verifica banca/cont/CAEN/CUI si intoarce mesaje CLARE ("LIPSĂ
bancă — obligatorie la D300") - dar NU era chemata niciodata din `genereaza()`. La fel
`d301.valideaza`. In schimb d100/d101/d205/d710 cheama `erori_generare(prof)` si BLOCHEAZA.
Deci verificarea exista, era corecta, si nu apara nimic: XML-ul iesea cu banca="" si cont="",
iar contabilul primea eroarea criptica a validatorului in loc de "completeaza IBAN-ul".

AMPLOARE: 2 din 3 firme reale (tenant_002 fara iban, tenant_003 fara banca si iban). Adica
D300 si D301 erau nedepunabile pentru majoritatea firmelor, fara ca nimic sa spuna de ce.

REPARAT prin ALINIERE la tiparul existent, nu prin invenite: `erori_generare(prof)` in d300 si
d301, acelasi nume si aceeasi semnatura ca la celelalte patru generatoare (aceeasi situatie =
aceeasi rezolvare). Chemata din `genereaza()`, ridica ValueError -> ruta o transforma in 422 ->
ecranul o arata in `.dec-eroare`. `valideaza(res)` cheama tot functia asta si nu-si mai repeta
verificarile (sursa unica, fara constructie paralela).

GARD: `core/test_poarta_profil.py` - daca un generator DEFINESTE erori_generare, `genereaza()`
trebuie s-o CHEME. Un gard scris care nu e poarta nu apara nimic; asta e clasa de defect
vanata toata ziua (verificator de schema care raporta fara sa blocheze, masti peste query,
validare D406 care nu rula).

NOTA DE PROCES: defectul a iesit la iveala prin verificare cu OCHII, nu prin suita. Cele 1008
teste erau verzi peste el, iar verificatorul de conformitate la fel. DE_FACUT are deja notata
limita: verificatorul prinde semnatura textuala, nu randarea si nu comportamentul.

### 27.07.2026 Registrul de datorie devine TEST, nu listă (cerut de Costin)

CONSTATAREA lui Costin: "mereu lasam cate ceva in urma de care nu mai stim si de care nu ne
mai amintim decat cand crapa ceva". Corecta, si cu dovada in aceeasi zi: aproape tot ce am
reparat pe 27.07 era DEJA consemnat ca amanat in DE_FACUT.md (80.000 de caractere, 33 de
sectiuni). Registrul exista, disciplina de a scrie exista - lipsea mecanismul care sa-l faca
imposibil de uitat.

MAI RAU: un registru neverificat se DESINCRONIZEAZA. `LANSARE.md` declara "Un singur
deployment activ | REZOLVAT (25.07)" - dar pe 27.07 `/opt/iconta` era viu, cu chiar venv-ul
din care rula aplicatia. Nimeni nu mintise; nimic nu verifica afirmatia.

MECANISM: `core/test_datorie.py`. Fiecare item amanat = un test care afirma comportamentul
CORECT, marcat `xfail(strict=True)` cu motivul si data. Consecinte: (1) suita ARATA datoria
la fiecare rulare (`-rxX`), nu o ascunde; (2) cand cineva repara defectul, testul TRECE si
`strict=True` il face sa PICE - semnal ca e timpul sa se inchida itemul. Datoria devine
zgomotoasa, ca mastile reparate azi.

DOUA TESTE DE IGIENA A REGISTRULUI: fiecare item are eticheta DATORIE + data + motiv de peste
60 de caractere (un motiv scurt e inutil peste trei luni); si niciun item mai vechi de 90 de
zile - la trei luni se repara sau se RESPINGE explicit in DECIZII, nu se cara mai departe.

CE RAMANE IN DE_FACUT/LANSARE: doar ce NU se poate automatiza - decizii de produs, verificari
vizuale, sarcini juridice, dependente de terti. Daca un item e verificabil mecanic si e tot
acolo, e in locul gresit.

PRIMII 7 ITEMI: limita 75 caractere pe campurile de declarant (D300/D394 respinse de ANAF);
D390 pica structural la DUK; rotunjirea D390 (bancara vs aritmetica, cere sursa oficiala);
numere.numar() intoarce float pe sume; cere_coloane nu prinde tabela goala; SELECT * fara
garda in 5 module; lipsa heartbeat pentru joburi.

CORECTIE PROPRIE, consemnata: in GARZI.md scrisesem "LIPSA: test de restaurare" - FALS.
Restaurarea din off-site a fost testata cap-coada pe 18.07 (pg_restore exit 0, scheme
identice, tenant_002.facturi=5). Corectat: ce lipseste e REPETAREA automata, nu proba.
A zecea oara azi cand o afirmatie de-a mea despre stare s-a dovedit gresita la verificare -
si al doilea registru gasit desincronizat in aceeasi zi, ceea ce intareste decizia de mai sus.

### 27.07.2026 Limita ANAF de 75 caractere: reparata la SURSA, in toate declaratiile

GASIT prin verificarea vizuala de catre Costin (poarta de declaratie goala pe iconta.eu),
apoi extins prin masurare pe toate declaratiile: pe tenant_001 (denumire reala de 115
caractere - nume + titulaturi profesionale), D300/D301/D390/D394/D112 erau TOATE respinse de
ANAF cu "sir mai lung de 75 caractere". Campurile: `den`, `adresa`, `adresaR`, `den_intocmit`,
`nume_declar`, `denumire`.

CE ERA INAINTE, si de ce conteaza: trunchierea `[:74]` EXISTA deja in 6 din 11 locuri unde se
emite `declarant_nume`, din 15.07 - cu un comentariu care descrie exact acest defect. Regula
era cunoscuta si aplicata pe jumatate, doar pe campul care crapase atunci. Celelalte campuri
au ramas neatinse pana au crapat si ele. Tiparul: se repara SIMPTOMUL vazut, nu CLASA.

REPARAT: `common.text_anaf(v)` - sursa unica, normalizeaza spatiile multiple si trunchiaza la
74 (marja sub pragul ANAF). Aplicata in toate cele 9 generatoare; cele 6 `[:74]` locale au fost
inlocuite cu apelul comun, ca regula sa nu mai poata diverge.

TRUNCHIEREA E LEGITIMA aici, nu o ascundere: forma scurta a denumirii e acceptata de ANAF, iar
CUI-ul identifica firma. Nu se pierde informatie fiscala.

DOVADA: D300/D301/D394/D112 pe tenant_001 -> validator ANAF "valid, fara erori" (erau respinse
inainte). Zero regresie pe tenant_002 (denumire scurta): SHA256 identic pe toate cele 8
declaratii. D390 ramane respins, dar din ALT motiv (structura, sectiune lipsa la zero
operatiuni) - ramane in registrul de datorie.

MECANISMUL DE DATORIE S-A DECLANSAT PENTRU PRIMA DATA: itemul era `xfail(strict=True)` in
`test_datorie.py`; dupa reparatie testul a inceput sa TREACA, iar `strict` l-a facut sa PICE -
semnal automat ca e timpul sa se inchida. Asa se inchide un item: nu se sterge, se MUTA ca
gard permanent (`core/test_limita_text_anaf.py`), cu test de mutatie propriu.

### 27.07.2026 D390 nu se depune pe zero — regula FISCALA, nu defect de structura

SIMPTOM: D390 pe tenant_001 (zero operatiuni IC) respins de ANAF cu "lipsa sectiune
obligatorie". Il consemnasem ca "defect structural, cauza neinvestigata".

VERIFICAT LA SURSA: OPANAF 705/2020, Instructiuni pct. 1.2 - "Persoanele impozabile
inregistrate in scopuri de TVA depun declaratia recapitulativa NUMAI pentru lunile
calendaristice in care ia nastere exigibilitatea taxei", art. 325 Cod fiscal (Legea 227/2015).
O luna fara operatiuni intracomunitare NU produce obligatie de depunere.

DECI validatorul avea dreptate, iar generatorul gresea: emitea un XML pe care ANAF il respinge
corect. Structura oglindeste regula fiscala (<operatie> minOccurs=1). Dovedit prin mutatie:
acelasi XML cu o operatiune fabricata (in ROLLBACK) trece "valid".

LECTIA: o eroare de STRUCTURA de la validator poate fi o regula FISCALA codificata in schema.
Daca as fi "reparat structura" - emitand o sectiune goala ca sa treaca validatorul - as fi
produs o declaratie care nu trebuia sa existe. A doua oara azi cand verificarea la sursa a
schimbat complet diagnosticul (prima: d205_beneficiari).

REGRESIE PROPRIE, prinsa imediat de suita: poarta pusa in `genereaza` a rupt
`control_incrucisat.verifica_d390`, care chema generatorul doar ca sa AFLE bazele IC. Acolo
zero operatiuni e un raspuns legitim (baza 0), nu o eroare - iar exceptia facea intreg
verificatorul GRI si ascundea sub-verificarea D-vs-D.

REPARAT PRIN SEPARARE: `d390.calculeaza()` (pull + calcul, fara poarta) si `d390.genereaza()`
(calculeaza + poarta fiscala + XML). Verificatorii folosesc calculul, emiterea are poarta.
Aceeasi distinctie ca in restul zilei: a SOCOTI nu e acelasi lucru cu a DEPUNE.

TOATE cele 5 declaratii pe tenant_001: D300 valid, D301 valid, D394 valid, D112 valid,
D390 refuzat corect cu temei legal in mesaj.

### 27.07.2026 Rotunjirea D390: bancara -> aritmetica (aliniere, cu rationament)

INTREBAREA din registrul de datorie: `d390._int` folosea `round()` = rotunjire BANCARA
(112.5 -> 112), in timp ce D112 documenteaza ca ANAF cere ARITMETICA si ca cea bancara a fost
RESPINSA de validator (regula A91b: CAM calculat 112, cerut 113).

VERIFICAT LA SURSA: OPANAF 705/2020 si instructiunile formularului 390 VIES NU prevad o regula
de rotunjire. Sursa nu confirma, dar nici nu interzice cea aritmetica.

DECIZIE luata pe RATIONAMENT (consemnat ca atare, nu pe temei direct):
  (a) CONSECVENTA: d390 era SINGURUL din 10 generatoare cu rotunjire bancara pe sume.
  (b) RISC ASIMETRIC: daca ANAF asteapta aritmetica si la D390 - cum o cere explicit la D112 -
      bancara produce declaratii gresite; invers, aritmetica nu strica nimic.
  (c) Rotunjirea aritmetica e norma in fiscalitatea romaneasca.

IMPACT MASURAT: diferenta apare doar la .5 exact (7 din 10 valori de test difera). Pe datele
actuale NU se manifesta - toate bazele sunt rotunde - dar asta e noroc, nu garantie.
Zero regresie dovedita: nr_opi/rezumat/total identice pe tenant_002 lunile 5/6/7; D390 iunie
validat ANAF "valid".

GARDUL A GASIT CEVA NEASTEPTAT: d300 avea 3 `int(round(...))` - dar pe COTE, nu pe sume
(21.0 -> 21; 0.21*100 -> 21; deducerea cotei din raportul tva/baza). Cotele fiscale RO sunt
intregi (21/11/9/5/0), deci bancar == aritmetic acolo. Gardul initial era prea larg.
RESTRANS cu escape hatch adnotat - marcajul `# ROTUNJIRE PE COTA`, acelasi tipar ca
`# MASCA MOTIVATA` de la masti: exceptia e permisa, dar trebuie DECLARATA pe linie.

### 27.07.2026 Garda de coloane pe CURSOR — inchide si cazul "tabela goala"

DOUA DATORII inchise deodata, pentru ca aveau aceeasi solutie.

(1) `cere_coloane` verifica randurile CITITE, deci pe o tabela GOALA n-avea ce verifica si
trecea - o coloana disparuta pe o firma fara salariati ramanea tacuta. Limita fusese
consemnata onest cand a fost gasita, in aceeasi zi.

(2) `SELECT *` fara garda in mai multe module.

SOLUTIA: `common.cere_coloane_cursor(cur, chei, unde)` - verifica pe `cur.description`, care
descrie ce a intors query-ul INDIFERENT cate randuri sunt. Dovedit pe tenant_003.salariati:
0 randuri, 20 de coloane in description. Zero cost - nu e query in plus, e metadata pe care
driverul o are deja. Se cheama imediat dupa execute, inainte de fetch.

PRIORITIZARE PE DOVADA, nu pe lista: masurat care module hranesc efectiv o declaratie -
`grep` pe core/d*.py arata ca NICIUN generator nu importa stocuri_cv_api/casa_api/rip_api/
retete_api/reconciliere_api/jurnal_api. Acelea sunt UI. Gardate: d112 (salariati), d394 si
bilant_api (firma_profil) - singurele SELECT * care ajung intr-o depunere la ANAF.

TREI GRESELI PROPRII, consemnate: (a) am pus importul in d112 cu un regex `(.+)$` care a
inghitit si comentariul de pe linie, asa ca numele a ajuns IN comentariu, nu in import;
(b) verificarea mea a raportat "deja prezent" fiindca cauta textul oriunde in fisier, nu in
lista de importuri - o verificare care se pacaleste singura; (c) a fost nevoie de doua
incercari pentru ca prima "verificare" nu verifica nimic. Suita a prins toate trei.

### 27.07.2026 `numere.numar()` intoarce float — RESPINS trecerea pe Decimal (masurat, nu presupus)

ITEMUL din registrul de datorie: float pe bani pierde precizie la insumare (0.1+0.2), iar
importurile de solduri/parteneri/salariati/articole/retete/mijloace fixe trec prin `numar()`.
Propunerea era trecerea pe Decimal.

MASURAT INAINTE DE A DECIDE:
  - 5000 de valori aleatoare cu 2 zecimale: ZERO pierd precizie la round-trip prin float64
    (repr-ul unui float cu 2 zecimale reconstruieste exact valoarea);
  - insumarea a 5000 de randuri: eroarea ramane cu ordine de marime sub toleranta de 0.01
    folosita la verificarea echilibrului balantei;
  - `solduri_api` face deja `round(..., 2)` inainte de comparatie, cu toleranta 0.01;
  - destinatia e coloana `numeric` in PostgreSQL - psycopg2 converteste prin repr, exact.

DECIZIE: NU se trece pe Decimal. O schimbare in 6 module si 12 apeluri, pe cai de import
folosite in productie, pentru un risc care NU se manifesta, ar fi mai riscanta decat problema.
Aceasta e o INCHIDERE, nu o amanare: itemul iese din registru cu motiv masurat.

CONDITIA in care decizia ramane valabila e ea insasi un gard: `core/test_precizie_import.py`
verifica exact premisele - valorile de import au 2 zecimale si sunt exacte in float; insumarea
unei balante de 5000 de randuri ramane sub toleranta; verdictul de echilibru e identic cu cel
calculat in Decimal (inclusiv detectarea unei diferente reale de 2 bani). Daca vreodata
importurile primesc mai multe zecimale sau toleranta scade, testul pica si decizia se reia.

LECTIE DE METODA: "float pe bani e gresit" e adevarat ca principiu general si FALS ca diagnostic
aici. Diferenta se vede doar masurand. O reparatie facuta pe principiu, fara masuratoare, ar fi
atins sase module de import in productie fara sa rezolve nimic.

### 27.07.2026 Heartbeat pentru joburile de fundal — ULTIMUL item din registrul de datorie

`cron.ruleaza` (construit tot azi) prinde jobul care CRAPA. Nu prinde jobul care nu porneste
DELOC: cron oprit, reboot fara restaurarea crontab-ului, linie stearsa, server jos la ora
rularii. Dovada ca problema e reala, din aceeasi zi: woocommerce.log tacea de 12 zile si a
fost nevoie de investigatie ca sa se stabileasca daca e defect (nu era - wc_url NULL).

MECANISM: `public.cron_batai` (nume, ultima_reusita, durata, rulari). `cron.ruleaza` scrie o
bataie DOAR la rulare reusita - un job care crapa mereu nu trebuie sa para sanatos.
`verifica_batai` compara cu pragul PER JOB: ritm x2 + marja, pentru ca ritmurile difera de la
15 minute (alerta_acces) la 96 de ore (sinteza_zilnica, care ruleaza luni-vineri: vineri 19:00
-> luni 19:00 sunt 72h normale).

RULEAZA PE SYSTEMD TIMER, nu pe cron (iconta-heartbeat.timer, la 6 ore): un verificator de
cron-uri pornit tot din cron ar muri odata cu ele. Acelasi rationament ca la backup.

EXIT 0 CHIAR CU CONSTATARI: semnalul e ALERTA, nu codul de iesire. Cu exit 1, systemd marca
serviciul "failed" la fiecare rulare cu intarzieri - si atunci un esec REAL al heartbeat-ului
(DB jos, cod stricat) ar arata identic cu functionarea normala. Exit 1 ramane doar cand
verificarea INSASI n-a putut rula. Un semnal care se aprinde mereu nu mai e semnal.

BOOTSTRAP: la instalare, joburile fara nicio bataie primesc una initiala. Fara asta,
sinteza_zilnica aparea "intarziata" din prima secunda desi doar nu-i venise randul - iar un
fals-pozitiv la instalare invata omul sa ignore alerta.

LIMITA DECLARATA: verificatorul ruleaza pe ACELASI server. Server jos = nici el nu ruleaza.
Un deadman EXTERN ar acoperi si asta; nu s-a construit.

REGISTRUL DE DATORIE E GOL. Cele 7 itemuri deschise dimineata: 5 reparate, 1 respins cu
masuratoare (float in numar()), 1 inchis prin verificare la sursa (D390 pe zero era regula
fiscala, nu defect). Testul de igiena a fost corectat: registrul GOL e starea DORITA, nu o
eroare - prima zi cand s-a intamplat.

### 27.07.2026 Inventarul a ceea ce a fost amanat — si un symlink care ar fi doborat site-ul

Cerut de Costin la finalul zilei: "inventariaza tot ce ai zis nu acum / e minor".

GASIT, GRAV: `/etc/nginx/sites-enabled/nou-iconta` era SYMLINK MORT - fisierul din
sites-available fusese sters la curatenie, symlink-ul nu. Nginx mergea din configul incarcat
in MEMORIE, deci site-ul parea perfect sanatos. La primul `reload` sau `reboot`, nginx NU ar
mai fi pornit si site-ul ar fi cazut.

CAUZA: comanda de reparare a symlink-ului NU A RULAT NICIODATA - output-ul ei s-a pierdut in
conversatie, iar eu am presupus ca s-a executat. Exact clasa de defect vanata toata ziua:
starea presupusa, nu verificata. REPARAT + dovedit prin `systemctl restart nginx` complet, nu
doar reload.

GASIT, MEDIU: `DE_FACUT.md` marca drept DESCHIS cinci lucruri REZOLVATE in aceeasi zi
(heartbeat, rotunjire D390, numar() float, SELECT *, cere_coloane pe tabela goala). Aceeasi
desincronizare diagnosticata dimineata la LANSARE.md. Inchise cu starea reala.

GASIT, MIC: 12 `pass` inerte sub `esec_secundar` (pastrate deliberat ca sa nu schimb
comportamentul, apoi nerevenite); cod mort intr-un test scris de mine (`if False` placeholder);
`_arhiva_briefuri/` - 9 fisiere pe disc, scoase din git, nesalvate de niciun backup (nici
pg_dump, nici config backup). Cea mai proasta stare posibila: nici urmarite, nici sterse.
Puse in git.

RAMAN DESCHISE, cu decizie: poarta pe declaratia goala e doar in ecran (POST /coada n-are);
Payments D406 gol (zero date de plati in model); 16 `SELECT *` in module de UI; deadman extern
pentru heartbeat; subdomeniul nou.iconta.eu (redirect inainte de stergere).

### 27.07.2026 `register` nu mai minte cand prima firma nu se creeaza (varianta (c))

PROBLEMA consemnata mai devreme azi: blocul `try` din `register` acoperea `provision_tenant`.
La esec, raspunsul spunea SUCCES, iar userul intra in aplicatie cu cont valid si ZERO firme,
fara nicio explicatie. Facut zgomotos (alerta), dar comportamentul ramasese neschimbat -
era decizie de produs.

DECIZIE (varianta c din cele trei propuse): contul se creeaza si RAMANE valid - e util,
userul se poate loga si adauga firma manual. Dar raspunsul poarta `firma_creata: false` +
un avertisment citibil, iar ecranul il arata dupa logare.

De ce nu (a) "ramane asa": o minciuna tacuta e exact clasa vanata toata ziua.
De ce nu (b) "register esueaza": s-ar pierde un cont valid pentru un esec la un pas
secundar, iar userul ar trebui sa reia totul.

LEGAT SI IN UI, altfel n-ar fi servit la nimic: `login.js` facea `await api.post(...)` si
ARUNCA raspunsul. Acum il citeste; la esec pastreaza avertismentul si il arata prin
`arataMesaj(..., "info")` DUPA intrarea in aplicatie - mesaj de stare, nu caseta permanenta,
pentru ca situatia e temporara (firma se adauga din ecranul Firme). DS cap.5/cap.6.

Nota de metoda: backend-ul singur ar fi fost o reparatie invizibila. Cand raspunsul unei rute
capata un camp nou, trebuie verificat CINE il consuma - altfel adevarul se opreste la HTTP.

### 27.07.2026 [CORECTIE] Reparatia `register` fusese pe jumatate — UI-ul tot arunca raspunsul

Commitul e0e05f7 a intrat cu backend-ul reparat si UI-ul NEatins: patch-ul pe `login.js`
picase pe a doua ancora (`sesiune.intra` avea alta indentare decat presupusesem), dar comanda
a CONTINUAT - a scos itemul din DE_FACUT si a comis. Deci: backend trimitea `firma_creata`,
UI-ul il arunca, iar registrul spunea "rezolvat".

Aceeasi clasa vanata toata ziua, produsa de mine in ultima runda: POARTA LIPSEA DIN COMANDA.
A doua oara azi (prima: commit cu suita rosie la heartbeat).

REPARAT ACUM, cu ancora luata din fisier (nu scrisa din memorie) si cu verificare in trei
puncte dupa scriere: captarea raspunsului, testul `firma_creata === false`, afisarea. Plus
proba ca fisierul SERVIT de pe iconta.eu contine codul nou - nu doar cel de pe disc.

Tipul mesajului: `avert` (galben), nu `info` (gri) - DS cap.6. Situatia cere actiune din
partea omului (sa adauge firma), nu e o simpla informare.

### 27.07.2026 Perioada luna/an in antete: ramane NUMERICA (07/2026) — decizie Costin

CONSTATARE: perioada era compusa manual cu `${String(luna).padStart(2,"0")}/${an}`, incalcand
DS cap.4 (dataRo = singura functie de formatare). Garda DATA_DIALECT nu prindea forma asta.

INTREBAREA PUSA: se converteste la `dataRo(..., "luna_an")`? Ar fi respectat regula, DAR ar fi
schimbat textul afisat: "Luna 07/2026" -> "Luna iulie 2026".

DECIZIA COSTIN: ramane forma NUMERICA. Deci nu codul se aliniaza la regula, ci REGULA capata
forma folosita efectiv: `dataRo` primeste stilul `luna_an_numeric` (07/2026), consemnat in DS
cap.4 (v2.21) alaturi de `luna_an` ("iulie 2026", pentru titluri narative).

REZULTAT: textul afisat e NESCHIMBAT pentru utilizator; se schimba doar CINE il produce -
formatarea trece prin functia unica, `padStart` local ramane interzis. Garda DATA_LUNA_AN
intra in verificator ODATA cu regula (DS + verificator simultan).

CATE ERAU DE FAPT: nota din DE_FACUT vorbea de UN caz, in firme.js. Masuratoarea a gasit 15,
in PATRU fisiere (firme.js 12, facturi_ecran.js 1, rip_ecran.js 1, portal.js 1). Si aici
registrul descria simptomul vazut, nu clasa - al treilea caz azi.

### 27.07.2026 Catch-uri goale pe SCRIERE (3) — restul sunt degradare gratioasa, nu tacere

MASURAT: 16 `catch {}` in frontend. Citite toate, nu reparate in bloc:
  - 13 sunt pe CITIRE, cu fallback pe lista goala (`try { lista = await get() } catch {}`).
    Ecranul arata stare goala in loc sa crape. E degradare gratioasa, nu tacere periculoasa -
    NU se ating.
  - 3 sunt pe SCRIERE, unde esecul parea succes: firme.js (mesaj catre client netrimis),
    cabinet.js (setarea patru-ochi nesalvata, dar elementul disparea), navigator.js
    (confirmarea unui anunt - disparea de pe ecran si reaparea la reincarcare).
    REPARATE: mesaj de eroare in loc de tacere.

ASTERISC FARA VALIDARE: raportul initial spunea 3 ecrane (date_firma, flux_concediu, validat).
FALS - toate trei AU validare; masuratoarea mea cauta doar `arataMesaj(..., "eroare")`, iar
ecranele folosesc si alte forme canonice (`msg-eroare` prin innerHTML in flux_concediu:136-139,
`er.textContent` + flag `obligatoriu` in validat.js:171). Am apucat sa adaug o validare DUBLA
in flux_concediu, cu nume de campuri ghicite (`zile` in loc de `zile_cm`) si asezata INAUNTRUL
try-ului, dupa `btn.disabled = true` - ar fi blocat butonul pe "Se salveaza..." la orice
validare picata. SCOASA. Verificarea corecta: zero ecrane cu asterisc fara validare.

LECTIE: un criteriu de masurare prea ingust produce fals-pozitive care duc la reparatii
inutile pe cod care functiona. A patra oara azi cand masuratoarea mea a fost gresita, nu codul.

### 27.07.2026 SEO: Search Console verificat + sitemap trimis + meta social pe landing

Search Console: proprietate de tip DOMENIU (`sc-domain:iconta.eu`, acopera si subdomeniile),
verificata prin TXT DNS pus de Claus Web. Sitemap trimis: `https://iconta.eu/sitemap.xml`
(la proprietatile de tip domeniu se cere URL complet, nu doar numele fisierului). 6 URL-uri:
landing, /ghid, 3 pagini de ghid, /public/termeni.

GASIT PE DRUM: landingul (`static/index.html`) n-avea NICIUN meta social - nici og:image, nici
og:title, nici description. Paginile de ghid le aveau toate (main.py:8463). Deci un link catre
iconta.eu dat pe WhatsApp sau Facebook aparea fara titlu, descriere si imagine - exact pagina
data cel mai des. Reparat, text din MARKETING.md (lista PERMISE: "control fiscal automat", NU
"oferim contabilitate" - zidul CECCAR; D406 absent, e pe INTERZISE pana la reparare).

RAMAS: `og:image` foloseste `logo_login.png` (337 KB, logo, nu imagine sociala). Formatul
potrivit pentru preview e 1200x630. Aceeasi limita ca la ghiduri (main.py:8321 o noteaza ca
provizorie) - acum se aplica si landingului.

### 27.07.2026 Reboot dupa 9 saptamani + un bug gasit de el (init_pool mascat)

Serverul rula din 26.05 pe kernel 6.8.0-117, cu TREI actualizari de securitate instalate si
neactivate (124, 134, 136). Repornit: kernel 6.8.0-136 activ, toate serviciile revenite singure
(systemd enabled), crontab intact (9 linii), timere active, site 200.

BUG GASIT DE REBOOT: rulind `core.cron` prin `ssh host 'comanda'` (care NU incarca .env),
heartbeat-ul a crapat cu "pool neinitializat - cheama init_pool() la startup". Cauza reala:
`init_pool()` era invelit in `try/except: pass`, deci esecul lui (variabile de mediu lipsa)
disparea, iar eroarea aparea mai jos, cu alt mesaj, in get_conn. Aceeasi clasa vanata toata
ziua - in cod scris de mine cu doua ore inainte.

Serviciul systemd are EnvironmentFile, deci in productie ruleaza corect (dovedit: timerul de
la 18:20). Dar daca DB-ul chiar ar fi jos, heartbeat-ul ar fi crapat cu un mesaj care ascunde
cauza. REPARAT: init_pool nemascat in ambele locuri (bate + verifica_batai).

### 27.07.2026 Reboot dupa 9 saptamani + un bug gasit de el (init_pool mascat)

Serverul rula din 26.05 pe kernel 6.8.0-117, cu TREI actualizari de securitate instalate si
neactivate (124, 134, 136). Repornit: kernel 6.8.0-136 activ, toate serviciile revenite singure
(systemd enabled), crontab intact (9 linii), timere active, site 200.

BUG GASIT DE REBOOT: rulind `core.cron` prin `ssh host 'comanda'` (care NU incarca .env),
heartbeat-ul a crapat cu "pool neinitializat - cheama init_pool() la startup". Cauza reala:
`init_pool()` era invelit in `try/except: pass`, deci esecul lui (variabile de mediu lipsa)
disparea, iar eroarea aparea mai jos, cu alt mesaj, in get_conn. Aceeasi clasa vanata toata
ziua - in cod scris de mine cu doua ore inainte.

Serviciul systemd are EnvironmentFile, deci in productie ruleaza corect (dovedit: timerul de
la 18:20). Dar daca DB-ul chiar ar fi jos, heartbeat-ul ar fi crapat cu un mesaj care ascunde
cauza. REPARAT: init_pool nemascat in ambele locuri (bate + verifica_batai).

### 27.07.2026 Sterse trei copii moarte langa sursa canonica

`INVENTAR_LIVE.md` (25.07) si `PLANIFICATE_export.md` (16.07) erau EXPORTURI din
`FUNCTIONALITATI.csv` - copii inghetate langa sursa vie, deja divergente. Exact tiparul care
a costat ziua de azi: cineva citeste copia si crede ca e adevarul (vezi DE_FACUT.md, LANSARE.md
care declara "un singur deployment REZOLVAT" cand /opt/iconta era viu). Daca e nevoie de o
lista de pozitii LIVE, se genereaza din CSV pe loc, nu se pastreaza.

`CHECKLIST_BROWSER.md` (16.07) - verificarile care cer ochi/telefon. Facute (confirmat de
Costin 27.07). Fisierul si-a consumat rostul.

Fisiere normative ramase (9): CLAUDE.md, DESIGN_SYSTEM.md, DECIZII.md, ISTORIC.md, LANSARE.md,
GARZI.md, MARKETING.md, ARHITECTURA_SPV.md, TERMENI_SI_CONDITII.md + FUNCTIONALITATI.csv si
CONCURENTA.csv. Fiecare are un rost distinct; niciunul nu e copie a altuia.

### 27.07.2026 nou.iconta.eu inchis + symlink nginx reparat (a doua oara)

SUBDOMENIU: nu mai raspunde (HTTP 000), zero dependente in cod/.env/systemd. Certificatul
Let's Encrypt (expira 07.10) a fost STERS din certbot - altfel reinnoirea automata ar fi
esuat in octombrie pe un domeniu care nu mai serveste nimic, generand alerte inutile. DNS-ul
ramane, e inofensiv.

GASIT PE DRUM, mai important: `/etc/nginx/sites-enabled/iconta` era FISIER NORMAL (2018 octeti),
nu symlink, iar `sites-available/iconta` avea alta versiune (1120 octeti). Deci o editare in
sites-available - locul unde se editeaza in mod normal - N-AR FI AVUT NICIUN EFECT, iar
diferenta ar fi aparut abia la un reload. Probabil ramas de la repararea symlink-ului mort de
mai devreme in aceeasi zi. REPARAT: versiunea VIE copiata in sites-available, enabled redevenit
symlink. Dovedit prin `systemctl restart nginx` complet, nu doar reload.

A doua oara azi cand configurarea nginx era rupta fara sa se vada: prima data un symlink orfan
(ar fi doborat site-ul la reboot), acum un fisier care ocolea sursa. Ambele invizibile cat timp
nginx rula din memorie.

### 29.07.2026 Faza 0: scan după SIMPTOM vs după CLASĂ STRUCTURALĂ

Decuplarea suitei de firmele persistente (tenant_001/002/003) a fost făcută în TREI runde de
scan parțial în aceeași zi: întâi 2 teste, apoi încă 4, apoi încă 7 după wipe — fiecare rundă
PĂREA completă. De fiecare dată scanul fusese după SIMPTOM (grep pe „tenant_00X"), iar simptomul
apărea și acolo unde NU era cuplare (numele pasat ca string unei funcții pure de audit de schemă)
și lipsea acolo unde cuplarea era mascată (scriitor cu `INSERT INTO tenant_002.<tabelă>` într-o
fixtură, nu `get_conn`).

REGULA: nu scanezi după simptomul-string, ci după CLASA STRUCTURALĂ a cuplării — ce anume face un
test să depindă de o firmă din baza. Clasa are exact două semnături: (a) `get_conn("tenant_00X")` —
sesiune legată de schema persistentă; (b) SQL `FROM/INTO/JOIN/UPDATE/DELETE FROM tenant_00X.<tabelă>`
— interogare pe datele persistente. Numele efemere (`ztest_*`) și argumentele-string către funcții
pure NU sunt cuplare. Ambele semnături sunt acum într-o gardă mecanică permanentă
(`core/test_teste_decuplate.py`), cu un test-mutație care dovedește că regex-ul chiar prinde cuplarea
și nu dă fals-pozitiv — altfel o gardă care nu prinde nimic ar da o falsă siguranță.

Consecință generală: un scan care „iese gol" nu e dovadă până nu arăți că gardul ar fi PRINS cazul
pozitiv. „Se pare că le-am găsit pe toate" a fost greșit de trei ori azi.

### 29.07.2026 `d112._sal_minim` era a doua sursa de adevar — si dadea gresit pe 2025

FAPT: salariul minim era hardcodat in d112 (4050 pentru <=2026/06, 4325 dupa, fallback 4325
pentru 2027+), desi `common.COTE` il tine cu perioada si temei. Comentariul de deasupra
recunostea problema: "a doua sursa de adevar + drift pe 2027+".

BUG ASCUNS, gasit la inlocuire: pentru 2025 dadea 4050. Valoarea reala e 3700 (HG 1006/2024).
Deci D112 pe 2025 folosea un salariu minim cu 350 lei mai mare la calculul facilitatilor si
al plafoanelor. Nu era vizibil pentru ca nu s-a generat D112 pe 2025 - ar fi aparut la prima
declaratie rectificativa.

REPARAT: citeste din registru. Verificat: 2026/06 -> 4050, 2026/07 -> 4325, 2025/03 -> 3700.

LECTIE: o valoare copiata din registru intr-un modul nu ramane sincronizata. Nu se strica
zgomotos - ramane plauzibila si devine gresita cand legea se schimba. Cautati "a doua sursa
de adevar" ca tipar, nu ca eroare izolata: registrul de cote exista din iunie, dar 7 module
il folosesc si restul au copii.

RAMAS DESCHIS (xfail in test_datorie): cota() intoarce TACIT ultima valoare cunoscuta pentru
o data viitoare. In ianuarie 2027 salariul minim va fi cel din iulie 2026, fara semnal.
Cotele au "de cand", n-au "pana cand" - iar pentru valorile actualizate anual prin HG, lipsa
unei valori noi nu inseamna ca cea veche ramane, ci ca nimeni n-a actualizat registrul.

### 29.07.2026 Valorile fiscale expira — `cota()` nu mai intoarce tacit valoarea veche

FAPT: `cota(nume, la_data)` intorcea ultima valoare cunoscuta pentru ORICE data viitoare.
In ianuarie 2027, D112 ar fi generat cu salariul minim din iulie 2026 (4325) - o cifra
plauzibila si gresita intr-o declaratie depusa la ANAF, fara niciun semnal.

CAUZA, ca tipar: cotele au "de cand", n-au "pana cand". Pentru valorile actualizate periodic
prin act normativ nou (HG anuala la salariul minim, OUG la facilitati), lipsa unei valori
pentru anul urmator NU inseamna ca cea veche ramane - inseamna ca nimeni n-a actualizat
registrul. Prima interpretare produce declaratii gresite IN TACERE.

[SUPERSEDAT 01.08 - blocaj la calcul DOAR pt data_out real (derivat din succesor); EXPIRA pe luni -> alerta interna de vechime; vezi Modelul de temei] REPARAT: `EXPIRA_DUPA_LUNI` marcheaza valorile cu termen; `cota()` RIDICA daca data ceruta
depaseste valabilitatea ultimei intrari, cu mesaj care spune din cand e valoarea, pana cand
era valabila, si ce trebuie facut. `strict=False` pentru rapoarte istorice, EXPLICIT.
Adaugat `cote_care_expira(in_zile)` - baza jobului lunar de avertizare.

DE CE "SEMNAL, NU DECIZIE": nimic nu scrie automat in COTE si nu se va scrie. O valoare
fiscala citita automat dintr-o pagina si pusa in registru ar fi exact tiparul vanat de trei
zile - o cifra plauzibila fara temei verificat. Sistemul spune CE sa verifici si CAND;
verificarea la sursa si actualizarea raman manuale.

SURSELE, in ordinea autoritatii (stabilit 29.07): (1) Monitorul Oficial - norma: legi, OUG,
HG, ordine. Din 12 temeiuri din registru, majoritatea NU sunt ANAF, ci acte ale
Parlamentului/Guvernului. (2) ANAF - procedura: formulare, structuri XML, validator,
instructiuni de completare. Publica TARZIU: legea intra in vigoare la 1 ianuarie,
instructiunile apar in februarie. (3) Presa fiscala - semnal ca s-a intamplat ceva, niciodata
temei. Cand ghidul ANAF difera de lege, legea castiga.

### 29.07.2026 Doua reguli dintr-un bug de facilitate salariala expus de o aliniere

Bug (verificat la sursa OUG 156/2024 art.LXVI lit.a): facilitatea salariala se pierdea complet pe
lunile cu concediu medical pentru un salariat pe salariul minim. Cauza: egalitatea din conditia
facilitatii (calcul_salariu) rula pe brutul LUCRAT (proratat cu zilele), nu pe cel CONTRACTUAL.
Reparat: egalitatea pe vbt (contractual). Doua reguli generale:

1. **O aliniere care repara ceva poate EXPUNE un defect latent.** Pe 15.07 s-a mutat primul argument
al lui calcul_salariu din brut_intreg in brut_lucrat, ca sa alinieze plafonul si deducerea cu statul
de plata - corect. Dar conditia (c) a facilitatii folosea acelasi argument si era corecta din
INTAMPLARE (brut_intreg = contractual). Dupa aliniere a devenit gresita pe lunile cu CM. Cand se
schimba ce INSEAMNA un argument, se verifica TOTI consumatorii lui, nu doar cei pe care ii repari.

2. **Un control incrucisat prinde DIVERGENTA, nu eroarea comuna.** Garda de coerenta nota-vs-D112 n-a
prins bug-ul pentru ca ambele laturi (salarii_contare si d112.pull) foloseau brut_lucrat - gresite
identic, deci zero divergenta. Un control care compara doua cai ce impartasesc aceeasi sursa gresita
raporteaza verde. Se verifica ce ACOPERA controlul, nu doar ca exista.

### 29.07.2026 Garda sterge_salariat: limita cunoscuta pe "D112 depus"

Hard-delete-ul unui salariat (redefinit ca DOAR pentru greseala de introducere - un salariat creat
din eroare, fara nicio luna declarata; vezi PASUL 1 data_incetare) refuza daca salariatul are concedii
medicale SAU daca tenantul are vreun D112 depus pentru o luna >= luna angajarii.

LIMITA: `public.declaratii_depuse` e la nivel de tenant+luna, cu XML - NU per-salariat. Deci verificarea
"e salariatul asta intr-un D112 depus" e GROSIERA: refuza pentru orice D112 depus care i-ar acoperi
perioada activa, chiar daca salariatul nu era efectiv in acel D112. Nu se poate mai fin fara sa parsezi
XML-ul depus. E intentionat err-on-refuse: asimetria justifica prudenta - un refuz gresit inseamna ca omul
pune data_incetare (varianta buna oricum), o permitere gresita inseamna pierderea istoricului care sustine
o declaratie deja depusa. A nu se prezenta garda ca fiind mai fina decat e. Vezi si datoria state_plata
(tabel mort, test_datorie).

### 29.07.2026 Agenda: surse PAZITE MECANIC (nu "surse care nu pot minti")

Agenda nu e derivata din surse care nu pot minti - e derivata din surse PAZITE MECANIC. Diferenta:
DE_FACUT.md a murit pentru ca nimic nu-l verifica (806 linii necitite, 5 itemi "DESCHIS" de fapt
rezolvati); TESTE.md si GARZI.md sunt tot scrise de mana, dar garda anti-stale (core/test_agenda.py) pica
suita cand raman in urma codului. Partea manuala trebuie tinuta MINIMA tocmai de aceea - fiecare camp scris
de om e o sursa care poate diverge.

REGULA DE REDIRECTIONARE (Costin, 29.07.2026): "Daca apare ceva ce nu stim acum si vrem sa schimbam
directia, MODIFICAM AGENDA INTAI, apoi ne tinem de ea." Practic: agenda (TESTE.md + test_datorie.py) e
sursa; ce nu e acolo nu se lucreaza. Un lucru nou se adauga in TESTE.md sau ca xfail INAINTE de a incepe.
Claude semnaleaza cand i se cere ceva din afara agendei - nu refuza, intreaba, asteapta decizia. Context:
pe 27.07 s-a lucrat o zi intreaga la reparatii deja consemnate ca amanate intr-un registru necitit.

## 30.07.2026 — Procedura de lucru scrisa in CLAUDE.md (roluri Code/arhitect, bucla pe pasi, temei, porti)

De ce. In 27-30.07.2026 s-au pierdut ore repetat din trei cauze de PROCEDURA, nu de cod:
(1) o sesiune a lucrat pe o copie locala in loc de server — defectele raportate ("confirmate")
nu existau pe productie; (2) instructiuni detaliate au trait doar in conversatie si la /clear
s-au pierdut, desi agenda arata corect ce urmeaza; (3) arhitectul a formulat brief-uri pe
presupuneri marcate ca fapte si a modificat direct cod — deci nimeni nu-l putea corecta.

Decizia. S-a fixat, de comun acord cu Costin, procedura completa de lucru: rolurile (Code
executa si cauta temeiul; arhitectul valideaza independent si NU modifica NIMIC — doar comenzi
de citire; Costin decide lansarea), bucla pe pasi cu commit+push la fiecare pas, pasii traiesc
in TESTE.md la "In lucru acum" (nu in chat) cu format obligatoriu, temeiul = actul normativ
citat cu ierarhia Monitorul Oficial > ANAF > comentarii (legea castiga peste ghid), cele cinci
porti de validare cu proba functionala obligatorie si output vizibil, ritualul de inceput,
opririle obligatorii si regula "agenda se modifica intai". Textul normativ traieste in CLAUDE.md
(sectiunea "PROCEDURA DE LUCRU (30.07.2026)"), unde se aplica si se citeste la fiecare sesiune —
aici e doar decizia si motivul.

Alternativa respinsa. Un registru-nota separat, de tip DE_FACUT.md — respins: exact tiparul care
a murit necitit (sters pe 27.07, 806 linii pe care nimeni nu le citea integral). Norma sta unde
se aplica (CLAUDE.md) si e pazita mecanic unde se poate (garda anti-stale core/test_agenda.py,
datoria din core/test_datorie.py); DECIZII.md trimite acolo, nu dubleaza. Doua surse de adevar
= drift.

Ce a inlocuit. Sectiunea "LOCUL DE LUCRU — verificare obligatorie la fiecare sesiune (29.07.2026)"
din CLAUDE.md — versiune mai veche a aceluiasi ritual + regula de redirectionare, superseded de
sectiunile 5 si 7 ale noii proceduri (ritualul adauga acum `git rev-parse`). Faptul ei unic —
serverul are un singur arbore `core/`, fara `declaratii/` si fara `motor/` — a fost PASTRAT ca
nota separata, ca sa nu se piarda la stergere.

Limita. Procedura e disciplina scrisa, mecanica doar partial: automate sunt doar ritualul
(`core.agenda`) si garda anti-stale. "Arhitectul nu modifica" si "proba functionala a rulat" se
tin prin conventie — inca nu exista un gardian care sa le forteze. De reconfirmat daca apare
unul.

## 30.07.2026 -- Coliziune de token la citarea regulilor de validator (rand vs regula)

Context: firul "temeiuri citabile mecanic" (format in CLAUDE.md §3.1). La normalizarea citarilor
de regula de validator (PASUL 3) s-a descoperit ca acelasi token are sensuri diferite in module
diferite: R28 e RAND de declaratie in D300 (d300.py: "R32 = TOTAL TAXA DEDUSA (rd.31+...)"), dar
REGULA DUK in D301 (checksum-ul care respinge orice alta valoare). La fel R17, R15, R11b.

Regula (optiunea A, decisa cu Costin):
Un token poate avea sensuri diferite in module diferite (R28 = rand in D300, regula DUK in
D301). Un gard care deduce sensul din FORMA tokenului va gresi intr-unul din sensuri. Corect e
sa ceara MARCARE explicita: gardul prinde ce e insotit de 'regula'/'validator'/'DUKIntegrator',
nu orice token care seamana cu un cod. Pretul - o mentiune complet bare nu e prinsa - e acceptat:
nici omul n-ar putea s-o deosebeasca.

Respinsa optiunea B (dezambiguizare prin rescrierea randurilor D300 in 'rd.28'): ar rescrie
referinte de rand corecte azi doar pentru comoditatea unui gard. Nu se rescrie cod corect pentru
un gard.

Aplicare: gardul (core/test_temeiuri.py, PASUL 4) cere forma canonica DOAR pe liniile cu marker
de regula; codurile R bare (randuri) raman neatinse. Norma de format traieste in CLAUDE.md §3.1.

## 31.07.2026 — Salariu minim 2025 corectat: 4050 lei (HG 1506/2024), nu 3700

Verificat la sursa: legislatie.just.ro (HOTARARE 1506 din 27/11/2024, Public/DetaliiDocument/291450,
MO 1185/28.11.2024), coroborat ANAF si portalcodulfiscal. Salariul de baza minim brut pe tara garantat
in plata = 4050 lei de la 1 ianuarie 2025; HG 1506/2024 ABROGA HG 598/2024 (care stabilise 3700 lei in
2024 H2) de la 1 ian 2025.

BUG: core/common.py COTE["salariu_minim"] avea (2025-01-01, 3700, "HG 1006/2024") - valoarea VECHE
(2024 H2) pusa pe 2025, cu act gresit; iar 4050 era mis-datat la 2026-01-01 cu "HG 1510/2024".
cota("salariu_minim", <data 2025>) intorcea 3700 -> orice calcul de salariu pe 2025 iesea gresit, in
tacere (salariul minim e reper pentru suprataxare CF art.146/168 si pentru baze). d212_engine.py avea
deja dreptate (4050, HG 1506/2024, verificat la sursa 11.07.2026).

CORECTIE: tabelul devine doua intrari - (2026-07-01, 4325, HG 146/2026) si (2025-01-01, 4050,
HG 1506/2024). Intrarea fantoma 2026-01-01 e ELIMINATA: pe 1 ian 2026 salariul minim NU s-a schimbat
(a ramas 4050); cota() intoarce valoarea in vigoare la la_data, deci intrarea 2025-01-01 acopera atat
2025 cat si 2026 H1, pana la majorarea din 01.07.2026.

ALTERNATIVA RESPINSA: a pastra o intrare la 2026-01-01 cu temei corectat. Respinsa - ar fi fictiva
(nicio majorare la acea data), iar tabelul codeaza SCHIMBARI de valoare prin act, nu ancore anuale.

LIMITA: 2024 si anterior NU sunt in tabel (nici nu erau corect) - aplicatia opereaza pe 2025-2026;
3700 (2024 H2, HG 598/2024) si valorile mai vechi nu se folosesc nicaieri (grep confirmat).

Norma traieste unde se aplica si se verifica mecanic: core/common.py (tabelul + temeiul pe linie) si
core/test_expirare_cote_de_baza.py::test_salariu_minim_2025_este_4050_hg_1506 (golden pe 4050 + HG 1506).
Datoria xfail test_datorie_salariu_minim_2025_gresit_in_common e INCHISA si stearsa din test_datorie.py.
Marker: salariu minim 2025 corectat 4050 hg 1506.

ADDENDUM 31.07.2026 (verificare la sursa ceruta de arhitect, runda 4):
- 2026 H1 = 4050 CONFIRMAT LA SURSA (nu mai e "dedus din absenta"): textul oficial al HG
  salariului minim 2026 (mmuncii.gov.ro/.../2025/12/HG_Salariul_minim_2026.pdf) - ART.1
  stabileste 4325 lei de la 1 IULIE 2026, iar ART.2 abroga HG 1506/2024 (MO 1185/28.11.2024)
  EXACT la 1 iulie 2026. Deci HG 1506/2024 (4050) a fost in vigoare CONTINUU de la 1 ian 2025
  pana la 1 iul 2026, acoperind tot semestrul 1 din 2026. cota() intoarce corect 4050 pt orice
  data 2025-01-01..2026-06-30.
- HG 598/2024 = 3700 lei de la 1 iul 2024 CONFIRMAT la legislatie.just.ro
  (Public/DetaliiDocument/283807). "HG 1006/2024" (atribuit gresit lui 3700 in tabelul vechi)
  NU e actul salariului minim - eroare de atribuire, deja scoasa din cod (grep 1006 in *.py: 0).
- SUPERSEDA intrarea din 29.07.2026 "d112._sal_minim era a doua sursa de adevar" (mai sus in
  acest registru): acolo se afirma "valoarea reala e 3700 (HG 1006/2024)" si se raporteaza
  "2025/03 -> 3700" ca reparatie - GRESIT pe ambele. Valoarea reala 2025 = 4050 (HG 1506/2024).
  Aceea a fost sursa credintei gresite care a bagat 3700 in tabel. d112 citeste din registru,
  deci urmeaza automat corectia: 2025/03 -> 4050 acum.

## 31.07.2026 — Numar tichete de masa: divergenta fata de sursa (zile efectiv lucrate), datorie deschisa

Verificat la sursa (runda 2 tichete): HG 1045/2018 (norme la Legea 165/2018) art.10 alin.(3):
"Salariatii beneficiaza lunar de un numar de tichete de masa cel mult egal cu numarul de zile
lucrate, iar acest numar nu poate depasi numarul de zile lucratoare din luna...". Zile care NU dau
tichet: concediul de odihna, delegatia/detasarea cu indemnizatie, invoirea, absenta (motivata sau
nu), concediul medical, sarbatorile legale.

DIVERGENTA: codul foloseste tichet_zile = zile_lucratoare_luna - concediu_medical (stat_plata_api.py,
d112.py). Scade doar CM (sarbatorile sunt deja excluse din zile_lucratoare), dar NU scade concediul
de odihna, delegatia, absentele -> ACORDA tichete pe acele zile -> nominal supra-declarat -> baza
CASS+impozit gresita in D112 (in plus, in favoarea salariatului).

RAFINEAZA limita declarata la 20.07.2026 (F133 step 3, opt.A): acolo limita mentiona doar
"absentele nemotivate nu reduc tichetele"; sursa arata ca si CONCEDIUL DE ODIHNA (frecvent) si
delegatia sunt excluse - deci divergenta e mai larga decat s-a declarat atunci.

DE CE NU E O LINIE: datele brute exista in pontaj (F135, stari concediu_odihna/absent_*/delegatie),
dar (a) modelul de prezenta nu distinge "pontaj neintrodus" de "tot prezent" (ambele = 0 randuri,
pontaj.py:6-7) -> nu se poate baza tacit tichetele pe el; (b) F135 (17.07) + opt.A (20.07) l-au
decuplat DELIBERAT de payroll. Fixul cere una din: (i) a face pontajul autoritativ pentru tichete
(reversare F135 + o notiune de "luna de pontaj inchisa" care sa rezolve ambiguitatea prezentei),
sau (ii) tracking documentat separat al zilelor de CO/delegatie/absenta care reduc tichet_zile,
la fel cum CM reduce azi. Ambele = feature pe stat_plata + d112 + re-validare DUK, plus o decizie
de scop (Costin) de a rasturna/rafina F135. Pana atunci: DATORIE xfail
(test_datorie_tichete_masa_zile_efectiv_lucrate), vizibila in agenda la fiecare sesiune.

ALTERNATIVA RESPINSA acum: a improviza scaderea din pontaj fara a rezolva ambiguitatea "neintrodus
vs tot prezent" -> ar zero-iza tichetele oricui n-are pontaj introdus -> regresie mai rea decat
supra-acordarea. Nu se aplica fara decizia de scop.

## 31.07.2026 — CAS peste plafonul voucherelor de vacanta: interpretare, NEAPLICATA (DUK respinge)

INTREBARE: voucherele de vacanta peste plafonul anual (6 salarii minime, OUG 8/2009 art.1) datoreaza CAS?

INTERPRETARE (temei): CF art.142 lit.r excepteaza de la CAS "biletele de valoare ... acordate POTRIVIT
LEGII". Peste plafonul legal, voucherul nu mai e "acordat potrivit legii" -> excesul pierde exceptia ->
ar datora CAS 25% (ca orice avantaj salarial). Directia e conservatoare (sub-taxarea aduce control,
supra-taxarea nu). NU exista text ANAF explicit pe acest caz - e INTERPRETARE, nu certitudine.

OBSTACOL LA DECLARATIE (dovedit pe DUK, 31.07.2026): incercarea de a declara CAS-ul pe exces prin
inflatarea bazei CAS B4_7 (salariu + exces) e RESPINSA de validatorul oficial (proba: salariat brut
5000 + vacanta 30000, iun 2026):
  - S731 (eroare): "Baza cas B4_7(10700) diferit de suma calculata(5000)" - DUK RECALCULEAZA B4_7 din
    baza salariala (B1/B2) si respinge orice adaos non-salarial;
  - S74 (atentionare): B4_8 trebuie = B4_7_calculat x 25%.
Deci sectiunea B4 din D112 NU are slot pentru CAS pe un element non-salarial. Singura cale DUK-valida ar
fi sa tratezi excesul ca VENIT SALARIAL (adaugat in baza B1/bazac), ca sa curga corect prin B4_7 - DAR
asta e o A DOUA interpretare, mai grea: excesul ar reduce si deducerea personala (art.77, degresiva pe
brut) si ar schimba tratamentul impozitului (salariu cu deducere vs tichet fara). Doua interpretari
stivuite pe un caz fara text ANAF = fragil la control.

ALTERNATIVA PASTRATA (singura DUK-valida azi): excesul ramane tratat ca restul voucherelor - CASS 10% +
impozit 10%, FARA CAS (comportamentul actual). E sub-taxare in cazul extrem (>6 sal.minime/an vacanta =
>25.950 lei in S2 2026), dar produce o declaratie VALIDA. A aplica CAS pe exces prin inflatarea B4_7 ar
fi transformat o declaratie valida intr-una respinsa de DUK - regresie (valid -> invalid).

LIMITA DECLARATA: (a) nu exista text ANAF explicit pe taxarea excesului; (b) chiar corecta fiind
interpretarea CAS, D112 nu o poate exprima fara a trata excesul ca salariu (cu efecte pe deducere).
DECIZIE DE SCOP necesara (Costin): (i) se trateaza excesul ca venit salarial in D112, cu efectele pe
deducere, sau (ii) se lasa sub-taxarea documentata pana la un text ANAF care transeaza. Pana atunci:
DATORIE xfail (test_datorie_cas_peste_plafon_vacanta), vizibila in agenda. Cazul e RAR. De reconfirmat
daca apare o norma/instructiune ANAF care transeaza.

## 31.07.2026 — DECIZIE DE SCOP D3: excesul de vacanta = avantaj salarial integral (var i, AMANAT)

Completeaza intrarea de mai sus ("CAS peste plafonul voucherelor de vacanta ... NEAPLICATA"). Costin a
ales varianta (i), cu amanarea implementarii.

Decizie de scop (Costin): excesul de vacanta = avantaj salarial integral. RATIONAMENT (miezul deciziei):
starea actuala NU e conservatoare, e INCOERENTA - codul taxeaza excesul cu CASS + impozit dar NU cu CAS.
Cele trei scutiri (CF art.76 alin.(3) lit.h impozit, art.142 lit.r CAS, art.157 alin.(2) CASS) sunt
conditionate de ACEEASI formula - "acordate potrivit legii". Nu exista citire care sa piarda doua si sa
pastreze a treia. Deci excesul peste 6 salarii minime = avantaj salarial INTEGRAL: CAS + CASS + impozit,
si intra in baza salariala.

NU se implementeaza acum: baza salariala atinge clusterul DEDUCERE PERSONALA (bifat 31.07). Un exces care
mareste brutul misca deducerea (art.77, degresiva pe venit). Se face la clusterul D112, cu tot lantul sub
ochi (calcul -> pull -> _d112_genereaza -> DUK), nu acum, izolat.

ALTERNATIVA RESPINSA: (ii) sub-taxare documentata pana la un text ANAF - respinsa pentru ca lasa in cod o
impartire ARBITRARA a scutirilor (pierzi CASS+impozit dar pastrezi CAS scutit), nu o pozitie fiscala.

LIMITA DECLARATA: (a) nu exista text ANAF explicit pe tratamentul excesului; (b) DUK nu accepta CAS pe
exces decat prin baza salariala (S731/S74, dovedit 31.07). Caz RAR (>25.950 lei/an vacanta la sm 4325).

## 31.07.2026 — Concedii medicale: verificare la sursa primara (runda 2) + rationament unificare

Etapa SURSA, FARA fix. Rezultate:

CAS PE INDEMNIZATIA CM: se retine 25%, pe indemnizatia INTEGRALA (NEplafonata la 12 sm). Temei: Cod
fiscal art. 144 ("baza lunara de calcul al contributiei de asigurari sociale ... este suma reprezentand
indemnizatia de asigurari sociale de sanatate ... iar contributia de asigurari sociale se suporta la
nivelul cotei prevazute la art. 138 lit. a) [25%] si se retine din indemnizatia") + art. 139 alin.(1)
lit. o) (indemnizatia CM e in castigul brut CAS) + OUG 3/2018 (a inlocuit vechea baza de 35% cu
indemnizatia insasi). PROVENIENTA: textul VERBATIM al art. 144 NU s-a obtinut de la sursa PRIMARA
(legislatie.just.ro/MO randeaza doar cuprinsul documentului consolidat urias; portalcodulfiscal 403;
ANAF doar Titlul I). Substanta e puternic coroborata (documente oficiale ANAF pe concedii medicale +
reproducere Wolters Kluwer verbatim + fiscalitatea.ro), dar litera primara ramane de reconfirmat pe
MO/just.ro. Deci comentariul din taxe_cm ("CAS NU se retine niciodata") e foarte probabil GRESIT, dar
NU se aplica fix pe baza secundara - se reconfirma primara intai.

CASS PE CM: doar codurile 01/07/10 (OUG 34/2024 art.155(1)(i)/157(1)(v), 12.04.2024) - CONFIRMAT.
CARANTINA (cod 07): 100%, NU 75% (art. 20 alin.(3) OUG 158/2005, majorat permanent prin Legea 136/2020).
Codul are 75% - divergenta reala.
PLAFON BAZA: 12 salarii minime/luna (art. 10 alin.(1)).
DEDUCERE PE INDEMNIZATIE: NEconfirmat prin text explicit (practica/interpretare art.78) -> GRI, nu bifa.

RATIONAMENT PENTRU ETAPA URMATOARE (de executat separat, dupa reconfirmarea primara a art.144):
CM1 (CAS)/CM2 (CASS pe cod)/CM4 (plafon 12 sm) NU sunt trei bug-uri independente - sunt un SIMPTOM: doua
surse de adevar pe acelasi calcul. Contributiile pe indemnizatia CM se calculeaza in DOUA locuri care
deviaza: (1) salarizare.taxe_cm (CAS=0, CASS cod-filtrat) - apelat la salvarea CM, STOCAT in
concedii_medicale, alimenteaza fluturasul/statul de plata; (2) d112 ramura CM (CAS=25% pe total_base,
CASS uniform pe tot cm_base) - alimenteaza DECLARATIA, ignora stocatul. Similar pe baza: calcul_cm (fara
plafon) vs _cm_media6 (cu plafon 12 sm). Fixul NU e schimbarea unei cote - e UNIFICAREA intr-o singura
functie apelata de fluturas SI de D112; altfel deviaza din nou dupa prima corectie. Cotele (carantina
75->100, CAS 0->25) se decid dupa reconfirmarea art.144 la primara; unificarea se face oricum. Datorie
mecanica: test_datorie_concedii_medicale_doua_surse.

## 31.07.2026 — CORECTIE TEMEI CAS pe CM + verdict CAS uniform pe coduri (deblocheaza unificarea)

Corecteaza intrarea "Concedii medicale: verificare la sursa primara (runda 2)", care atribuia CAS-ul
pe indemnizatia de CM articolului 144. GRESIT (a prins-o Costin: art.144 trimite la art.1 alin.(2)/
23(2)/32 OUG 158 - ALTE categorii, nu salariatul activ).

TEMEI CORECT: CAS 25% pe indemnizatia de CM a SALARIATULUI IN ACTIVITATE (art.1 alin.(1) lit.A OUG
158) = Cod fiscal art. 139 alin.(1) lit. o) (include indemnizatia in castigul brut) + art. 140 (baza
CAS = suma castigurilor brute). art. 142 NU o excepteaza (text integral verificat). art. 144 = traseul
paralel pentru alte categorii. Concluzia (CAS se retine) neschimbata; doar ARTICOLUL s-a corectat.
Reversarea "CAS=0 corect" s-a INFIRMAT.

VERDICT CAS PE COD (verificarea care bloca unificarea): CAS 25% se aplica UNIFORM pe TOATE codurile de
CM, INCLUSIV maternitate (08) si ingrijire copil (09). NU exista regula pe cod ca la CASS. Temei:
(a) art.139(1)(o) e GENERIC ("indemnizatiile de asigurari sociale de sanatate", nu doar incapacitate
temporara); (b) art.142 nu excepteaza niciun cod; (c) GHID ANAF concedii medicale (static.anaf.ro,
text citabil) transeaza explicit - Sectiunea A (boala) si Sectiunea B (maternitate/copil) datoreaza
AMANDOUA CAS via art.139(1)(o); pe lista "Nu se datoreaza" de la Sectiunea B apar CASS/somaj/etc DAR
NU CAS. Prin contrast, accidentele de munca (Legea 346/2002) au CAS EXPRES exceptat in ghid.

CONSECINTA PENTRU COD: d112 (CAS 25% uniform pe bazac+cm_base) e CORECT pe CAS. taxe_cm (cas=0) e
GRESIT. d112 ramane GRESIT pe CASS (aplica uniform, trebuie doar 01/07/10). Unificarea NU mai e blocata
de o regula CAS-pe-cod necunoscuta: functia canonica = CAS 25% UNIFORM + CASS doar 01/07/10 + plafon
12 sm. Ghidul ANAF e acum sursa PRIMARA citabila -> CM1 iese din "gri total"; ramane de reconfirmat
doar litera art.139(1)(o) pe just.ro (tier-1), reprodusa fidel de noulcodfiscal/Wolters Kluwer.

DE CE SE CONSEMNEAZA: un temei gresit intr-un registru se propaga - exact ca HG 1006/2024 atribuit
gresit lui 3700. Cine citeste "art.144" construieste pe categoria gresita.

## 31.07.2026 — UNIFICARE contributii CM intr-o functie canonica (livrat)

Inchide datoria "concedii medicale: doua surse de adevar". Pana acum contributiile pe indemnizatia de
CM se calculau in DOUA locuri care deviau: salarizare.taxe_cm (fluturas, cas=0 GRESIT) vs d112 ramura
CM (recalcul, cas=25% pe total, CASS uniform). Divergenta putea da cifre diferite pe fluturas vs D112,
fara semnal - prima instanta CONCRETA a categoriei GARZI "Integritate cod - arbori paraleli".

UNIFICAT: salarizare.taxe_cm e acum FUNCTIA CANONICA - CAS 25% UNIFORM pe toate codurile (CF
art.139(1)(o)+140), CASS doar 01/07/10 (OUG 34/2024), impozit 10% pe (brut-cas-cass). d112 ramura CM
o APELEAZA per certificat (nu mai recalculeaza cu formula proprie). Ambele lanturi consuma aceeasi
functie.

PROBA:
- test arbori paraleli (core/test_pull_declaratii.py::test_cm_arbori_paraleli_acelasi_rezultat):
  pe cod 08 (CASS-scutit), d112 exclude indemnizatia din baza CASS (B4_7-B4_5=cm_base) <=> taxe_cm
  cass=0. Trece VERDE dupa unificare.
- MUTATIE pe functia canonica (_CM_COD_CU_CASS + '08'): AMBELE teste cad impreuna
  (test_cm_arbori_paraleli SI test_cass_doar_pe_01_07_10) - unificarea a tinut.
- PROBA DUK: D112 cu CM cod 01 -> stare VALID (B4_5=10000 B4_6=1000 B4_7=10000 B4_8=2500). Schimbarea
  B4 CASS nu rupe cazul functional.

LIMITA (datorie separata, test_datorie_cm_dfield_coduri_speciale): codurile CM speciale (08 maternitate,
06 urgente) au gap-uri PRE-EXISTENTE in d112 pe D-field/C2 (C2_32/34/36 maternitate; D_11 urgente),
independente de contributii - un D112 cu cod 08/06 e respins de DUK pe acele campuri, nu pe B4. De
tratat separat (se inchide cand acele coduri trec validatorul; vezi test_datorie_cm_dfield_coduri_speciale).

## 31.07.2026 — D112 maternitate (cod 08): agregate C2 pe Rd.3 + split 100% FNUASS (blocaj rezolvat)

Blocaj REAL: orice firma cu o angajata in concediu de maternitate NU putea depune D112 - DUK respingea
(C2_32 lipsa; C2_11 calculat 0; D_20 trebuie 0). Cauza: d112 punea TOATE codurile CM in randul Rd.1
(C2_11-16), iar calcul_cm dadea maternitatii portie de angajator (primele 5 zile).

Verificat la SURSA OFICIALA (anaf_surse/d112_struct_anaf.txt, NU dedus din eroare):
- angajatorC2 e pe RANDURI per categorie: Rd.1 (C2_11-16) = D_9 in (01,02,03,04,05,06,12,13,14,16,51);
  Rd.3 (C2_31/32/34/36) = D_9=08 sarcina/lauzie (DOAR FNUASS, fara C2_33/35); Rd.4 = 09/91/92;
  Rd.4.1 = 17; Rd.5 = 15; Rd.2 = 10/11. C2_T6=Σ(C2_16+26+36+46+56).
- D-field (spec linia 5664): daca D_9 in (08,09,91,92,10,15,17) atunci D_20=0 (100% FNUASS).

REPARAT: calcul_cm - codurile 100% FNUASS au zile_ang=0/brut_ang=0. d112._d112_genereaza - C2 se
agrega PE RAND per cod (rutare), emitand atributele unui rand doar cand acel rand are date.

PROBA DUK: cod 08 -> VALID (C2_31=1/C2_32=10/C2_34=10/C2_36=4000; C2_11-16=0); cod 01 -> VALID
(regresie). MUTATIE: spart rutarea Rd.3 -> DUK respinge iar (A50 C2_31 lipsa, A51 C2_32 lipsa).

RAMAS (datorie, test_datorie_cm_dfield_coduri_speciale): (a) cod 06 (urgente medico-chirurgicale) cere
D_11 (cod urgenta din nomenclatorul HG 423/2020, C(3)) - concedii_medicale NU are campul; cere camp de
date nou + UI de introducere + emisie. OPRIT (nu se inventeaza formatul unui camp de declaratie).
(b) sub-randurile C2 infectocontagioase (Rd.1.1-1.4, cod 05 cu conditii D_12/data) nu sunt inca
defalcate - emise implicit 0 (corect cat timp nu exista cod 05 in luna).

## 31.07.2026 — PROPUNERE (nevalidata): temei fiscal structurat + garda de deriva + TIPAR RATCHET

PROPUNERE de arhitectura, NU decizie. Nicio implementare inainte de validarea lui Costin. Raspunde la
cele 6 puncte cerute.

### TIPAR REUTILIZABIL: gardul RATCHET (datorie mare, fara blocaj total)
Pentru o datorie MARE (multe restante) nu poti nici bloca tot (n-ai mai comite nimic) nici ignora
(creste la loc). Gard RATCHET: un BASELINE = numarul curent masurat, + regula pe doua stari:
  - count <= BASELINE -> AVERTISMENT (raporteaza cifra, NU intra in TOTAL/nu blocheaza);
  - count >  BASELINE -> BLOCHEAZA (intra in TOTAL) - s-a introdus o restanta noua.
Baseline COBOARA pe masura ce se repara (nu urca niciodata); la 0, orice violare blocheaza. Distinctia
de stari = daca intra in TOTAL (blocant) sau se printeaza separat (avertisment). Livrat pe cotele TVA
(b756af1). SE APLICA IDENTIC celor 82 de teste fara temei si oricarei datorii masurabile mari.

### 1. Formatul temeiului structurat
Reutilizeaza formatul canonic din CLAUDE.md §3.1 (deja definit: <TIP> <nr>/<an> [art.] [alin.()] [lit.]),
extins in registrul de cote (common.COTE) de la string liber la tuplu structurat:
  (tip, nr, an, art, alin, lit, data_in, data_out, url)
citibil mecanic (grep pe act la o schimbare de lege gaseste TOATE locurile). 3 exemple concrete:
  - salariu minim 4325:  ("HG", 146, 2026, None, None, None, "2026-07-01", None, "just.ro/.../DetaliiDocument/<id>")
  - deducere 45% (4+ pers): ("CF", None, None, "77", "4", None, "2018-01-01", None, "just.ro/.../171282")
  - carantina 100%:       ("OUG", 158, 2005, "20", "3", None, "2020-05-30", None, "just.ro/.../66305")
                          (+ ("Legea", 136, 2020, ...) actul care a majorat de la 75%)
data_out=None = inca in vigoare. La expirare, EXPIRA_DUPA_LUNI (deja existent) ridica.  [EXPIRARE SUPERSEDATA 01.08 - data_out=None ramane corect; semnalul devine VECHIMEA CONFIRMARII, nu EXPIRA_DUPA_LUNI; vezi "MODELUL DE TEMEI" 01.08 pct.1/2]

### 2. Adnotarea formulelor care NU sunt cote (o singura propunere)
Scara degresiva, plafon 12 sm, proratare, split zi 5-6 NU sunt o cota, sunt ALGORITMI. Propunere:
NU se structureaza formula (ar fi cod dublat in date), ci se adnoteaza FUNCTIA cu temeiul la nivel de
functie - un marker citabil in docstring: TEMEI: <act §3.1>. Verificatorul cere ca orice functie care
implementeaza o regula fiscala sa aiba markerul TEMEI. Argument: formula traieste in cod (se verifica
prin teste golden pe exemplul oficial); temeiul spune DE UNDE vine regula, la nivelul unde se aplica -
nu se atomizeaza in cote false.

### 3. Generarea Inventarului A din cod (TESTE.md -> raport)
Fiecare test care verifica o constanta fiscala poarta o adnotare de temei (decorator @temei sau comentariu
structurat). Un generator scaneaza testele + adnotarile si produce coloanele Cluster/Modul/Teste/Temeiuri/
Functie ca RAPORT (ca ISTORIC, regenerat).
CE NU ARE CORESPONDENT IN COD (s-ar PIERDE tacit la auto-generare - de pastrat intr-un strat separat):
  - coloana RISC (FISCAL/STRUCTURA) = judecata umana, nu derivabila din cod;
  - bifa "Verificat la sursa DD.MM" = un ACT de verificare umana (+ motivul de bump);
  - marcajele PARTIAL / deschis / gri / co-locatie.
Deci Inventarul se genereaza PARTIAL (structura cluster->temei->functie); judecatile umane (risc, bifa,
partial) raman intr-un overlay persistent (nu se pierd). Fara asta, auto-generarea ar sterge tocmai
informatia care nu e in cod.

### 4. Ce verifica verificatorul dupa adoptare (RATCHET)  [TIMING SUPERSEDAT 01.08 - ratchet->prag; vezi corectia 01.08]
Verifica: orice test care asertaza o constanta fiscala are adnotare de temei structurata. Tranzitie prin
RATCHET (tiparul TVA, refolosit): baseline = 82 (fara temei azi); test nou fara temei -> blocheaza; pe
masura ce se adauga temei, baseline coboara; la 0, fiecare test fiscal are temei obligatoriu. Zero
blocaj imediat, crestere imposibila.

### 5. Garda de deriva legislativa (GARZI cat.3) - LIMITA CARE SCHIMBA VALOAREA  [MECANISM SUPERSEDAT 01.08 - proxy EXPIRA inlocuit de vechimea confirmarii; limita "fara API legislativ" RAMANE; vezi Modelul de temei pct.2/3]
Cu act+nr+an+data structurate, un job AR PUTEA intreba: "actul X s-a modificat dupa data D?" - DACA
exista o sursa interogabila mecanic. RASPUNS ONEST: NU exista un API/feed public fiabil pentru
legislatia romaneasca. legislatie.just.ro randeaza dinamic, fara API (dovedit repetat in aceasta
sesiune: portalul serveste doar CUPRINSUL pentru Codul fiscal consolidat - art.144/78/139 n-au putut fi
extrase); Monitorul Oficial n-are feed structurat. Consecinta: garda de deriva NU se poate automatiza din
sursa autoritativa. Se degradeaza la: (a) REVIZUIRE MANUALA periodica ghidata de registru (registrul iti
spune CE acte sa verifici) - valoare reala; (b) scraping fragil - nu se poate baza pe el. Deci valoarea
temeiului structurat sta in: (i) grep-abilitate la o schimbare de lege CUNOSCUTA (gasesti locurile
afectate) + (ii) garda de EXPIRARE (EXPIRA_DUPA_LUNI, deja existenta) care semnaleaza cand o valoare a
trecut de valabilitatea declarata - un PROXY de deriva fara a interoga sursa. Garda "auto-detecteaza
schimbarea legii" NU e fezabila fara API legislativ. Asta reduce ambitia propunerii - onest.

### 6. Costul  [TIMING SUPERSEDAT 01.08 - nu per-cluster, ci ACUM; vezi corectia 01.08]
~82 teste (a) au nevoie de temei (clasificat 31.07) + ~80 cote TVA literale in cod (ratchet). Adoptare
INCREMENTALA prin ratchet, NU in bloc: 82 comentarii puse mecanic = cosmetica, nu garda (avertismentul
lui Costin). Se face pe CLUSTERE, fiecare cu verificare reala la sursa, in ordinea riscului. Gardul
(instalat deja pt TVA) impiedica cresterea intre etape. Cost per cluster mic; total distribuit pe sesiuni.

## 31.07.2026 — Regula ETALON: valoarea-martor a unui test nu se derivă din sursa pe care testul o verifică  (generala, toate clusterele)

DECIZIE: o valoare-etalon (golden) dintr-un test se scrie ca LITERAL, niciodata derivata din functia/registrul
pe care testul il verifica. Un test care asertaza `cota_standard(2025,8) == 21` are nevoie de `21` scris de
mana ca martor independent; inlocuit cu `cota_standard(...)` sau `common.cota("tva_standard", ...)` devine
tautologic (compara sursa cu ea insasi, dovedeste nimic). Consecinta masurata 31.07: din cele 80 de cote TVA
"fara temei", ~30 sunt exact astfel de etaloane legitime — NU se ataseaza la common.cota, s-ar transforma 30
de teste reale in 30 care nu verifica nimic. Regula e generala, nu doar TVA: se aplica oricarui golden fiscal.
Corolar pentru ratchet: etaloanele + fixture-urile + parametrii de generator (prin design) se marcheaza
ACCEPTATE, nu datorie — altfel gardul le urmareste la infinit pentru nimic.

## 31.07.2026 — Granite API: cota TVA lipsa = intrare incompleta -> EROARE, nu default ghicit  (main.py + facturi_api + produse_api + stocuri_api + reconciliere_api)

DECIZIE (corectie de directie, Costin): la granita, un default de cota (`corp.get("cota", 21)`,
`l.get("cota_tva", 21)`) NU se inlocuieste cu `common.cota()`, se ELIMINA. O factura/linie fara cota e o
intrare INCOMPLETA, nu o factura cu cota standard — regula bazei nule: se ridica eroare, nu se ghiceste nici
macar corect. Un default cu common.cota() ar fi tot o valoare inventata, doar actualizata. Unde eliminarea
rupe apelanti, se repara apelantii (sa trimita cota explicit), nu se pune default inapoi.

Trei distinctii care fixeaza scopul:
1. Auto-match care REUSESTE (nomenclator/AI intoarce 11/21 cu sursa+incredere) = propunere transparenta,
   corectabila — se PASTREAZA. Auto-match care ESUEAZA (AI indisponibil/nedeterminat) = intrare incompleta:
   `potriveste_cota` intoarce NEDETERMINAT (fara cota), NU 21 marcat "fallback". Marcajul protejeaza doar
   daca cineva il citeste; daca factura se emite oricum, 21 ajunge in decont exact ca inainte. Deci linia
   ramane fara cota -> emiterea e BLOCATA cu mesaj clar.
2. Cota 0 (scutit/neplatitor) e VALOARE VALIDA, nu absenta. `float(out["cota_tva"] or 21)` transforma 0 in
   21 (bug activ produse_api:46) — se distinge None (incomplet -> eroare) de 0 (scutit -> se pastreaza).
3. Parametrii de cota din note-generatoarele pure (`def nir_gv(..., cota_tva_implicita=21)`, avansuri,
   leasing etc.) raman prin design; granita (apelantul din main.py/*_api) e cea care cere cota explicit.

Masurare (fara reparatii) inainte de plan: cele 80 "cote fara temei" = 79 cote TVA reale (1 fals-pozitiv:
"alin. 11" docstring), 3 valori distincte (21/11/19), toate clusterul TVA VERIFICAT (Legea 141/2025 in
common.COTE, period-aware, golden test_d394) -> 0 de cercetat, ~20 granite de reparat, restul etaloane/
fixtures/parametri (ACCEPTATE). Baseline-ul 80 supraevalua riscul: o singura valoare imprastiata, nu 80 de
decizii nesustinute.

## 31.07.2026 — d300 vs d394 pe reverse charge: divergenta de clasificare e CERINTA, nu bug  (core/d300.py, core/d394.py, test_d300_d394_paritate.py)

CONSTATARE (verificat la sursa: structura D300 + structD394 pct.217): taxarea inversa PRIMITA fara
linii (tva=0) e clasificata DIFERIT de cele doua declaratii - si e corect asa, structuri diferite:
- D300 (decont): NU auto-proceseaza reverse charge din facturi (d300.pull nici nu citeste
  taxare_inversa). Randurile rd.12 (achizitii cu taxare inversa) se introduc MANUAL de contabil,
  care stie cota bunului. Calea auto pune o achizitie primita cu tva=0 neclasificabila in "alte".
- D394 (informativ): auto-clasifica reverse charge ca tip C (d394.tip_operatiune), la cota
  STANDARD a perioadei cand lipsesc liniile - semnalata explicit ca PRESUPUNERE in avertismente
  (pct.217: tip C nu accepta cota 0, cere cota bunului; fara linii nu e pe document).
Deci NU se aliniaza fortat: ar cere ca d300 sa auto-faca reverse charge (feature) si tot ar avea
nevoie de cota bunului (absenta pe factura fara linii). Reparatia reala e la DATE (factura de
reverse charge SA aiba linii cu cota bunului) - atunci ambele clasifica corect. Gardul de paritate
acopera clasificarea pe date COMPLETE (cu linii); cazul reverse-charge-fara-linii e limita
documentata, nu bug. Pe sume ambele dau 0 (tva=0), deci nu afecteaza cifrele, doar incadrarea. VERDICT GRI (provizoriu, NU verde): sta pe DEDUCTIE din cod (d300.pull nu citeste taxare_inversa) + practica, NEreconfirmat pe text MO. Datorie deschisa (test_datorie_d300_reverse_charge_manual_reconfirmat_mo): de reconfirmat la sursa primara (structura oficiala D300/OPANAF) ca reverse charge se trateaza DOAR manual (rd.12).

## 01.08.2026 — Audit semantic al declaratiilor (Conditia 2 Costin): "trece DUK" != "campuri corecte"

Context: D101 s-a dovedit respins de DUK (P ca elemente) SI cu numerotare P inventata in calcul_d101
(p11=impozit, nu formularul oficial OPANAF 206/2025). Lectia: DUK valideaza STRUCTURA (nume de campuri
cunoscute + reguli de formula), NU semantica -> orice validare istorica "trece DUK" e SUSPECTA pana la
verificarea numelor de campuri contra structurii oficiale (anaf_surse/). Aceasta e datoria ceruta de
Costin de inregistrat.

Cerinta Costin INAINTE de reconstructia d101: verifica daca vreo alta declaratie "valida" are aceeasi
clasa (numerotare proprie). Daca da, reconstructia d101 nu e singura -> vreau ordinea completa.

METODA: pentru fiecare din cele 8 valide DUK (d100,d112,d205,d300,d301,d390,d394,d406) - generat pe
schema efemera cu date minime, extras numele atributelor emise de build_xml, cautate in
anaf_surse/<tip>_struct_anaf.txt (structura oficiala).

REZULTAT: TOATE cele 8 emit doar campuri OFICIALE, inclusiv randurile numerotate (d300 R-uri, d112 96
atribute B1/B4/E1/E3, d394 sectiuni). Trei atribute lipseau din struct.txt (versiune veche) dar sunt
CONFIRMATE in constant pool-ul validatorului (unzip+strings pe jar): d301 temei (D301Validator, regula
d_rec), d394 tvaDedAI11/tvaDedAI21 (D394Validator v5, TVA dedus achizitii intracomunitare). Restul
negasite = boilerplate XML (encoding/xmlns/xsi/version/schemaLocation).

CONCLUZIE: d101 e SINGURA declaratie cu numerotare proprie -> ordinea de reconstructie = DOAR d101.

GARD (verificabil mecanic, nu nota): core/test_audit_campuri_oficiale.py - fiecare atribut emis trebuie
sa fie oficial (struct.txt) / boilerplate / allowlist confirmat-in-validator; un atribut inventat viitor
PICA. Mutatie dovedita: INVENTATxyz injectat in d300.build_xml -> testul PICA.

LIMITA declarata: gardul verifica NUMELE campurilor, nu VALORILE. Un camp cu nume oficial dar valoare
semantic gresita (cazul intern al d101: p11 pus in campul oficial P11) NU e prins de acest gard - pentru
asta e nevoie de golden tests pe cifre calculate de mana (Conditia 1, aplicata la reconstructia d101).
Deci "campuri oficiale" e conditie NECESARA, nu suficienta. d406 emite campuri oficiale dar are limita
cunoscuta separata (linii sintetice, DECIZII 27.07) - alt tip de incompletitudine, nu nume de campuri.

## 01.08.2026 — Reconstructia D101 pe formularul oficial (GREENLIGHT Costin, temei OPANAF 206/2025)

Context: D101 era respins de DUK (P ca elemente) SI avea numerotare P INVENTATA in calcul_d101
(p11=impozit, p9=baza) - nu corespundea formularului oficial. Greenlight Costin cu 2 conditii:
(1) proba nu e "DUK valid" (trecea si cu numerotare inventata) ci corespondenta camp/formula + golden
calculat de mana; (2) audit semantic al celorlalte 8 INAINTE (facut, DECIZII 01.08 - d101 e singura).

Temei APROBAT: OPANAF 206/2025, D101_A600 v10, anaf_surse/d101_struct_anaf.txt. Numerotarea inventata
a DISPARUT complet (fara adaptor). P-urile sunt acum ATRIBUTE pe <declaratie101> (nu elemente).

TABEL CORESPONDENTA (Conditia 1) - fiecare P emis, nume oficial, formula, sursa (rd. in doc):
  P1  Venituri din exploatare        intrare pull (cont 70-75)     rd.34
  P2  Cheltuieli de exploatare       intrare pull (cont 60-65)     rd.35
  P3  Rezultat din exploatare        P1-P2                         rd.36
  P4  Venituri financiare            intrare pull (cont 76)        rd.37
  P5  Cheltuieli financiare          intrare pull (cont 66)        rd.38
  P6  Rezultat financiar             P4-P5                         rd.39
  P7  Rezultat brut                  P3+P6                         rd.40 (DUK R38)
  P8/P9 Elemente similare ven/chelt  intrare manual                rd.41/45
  P10 Rezultat dupa elem. similare   P7+P8-P9                      rd.47
  P16 Total deduceri                 P11+P12+P13+P14+P15           rd.60
  P21 Total venituri neimpozabile    P17+P18+P19+P20               rd.68
  P22 Profit/pierdere                P10-P16-P21                   rd.69
  P34 Total cheltuieli nedeductibile P23+...+P33                   rd.82
  P35 Profit impozabil pre-ajustari  P22+P34                       rd.83
  P38a Profit/pierdere pre-reportare P35+P36+P37-P38               rd.86a
  P40 Profit impozabil               P38a-P39a (daca >0, altfel 0) rd.88
  P411 Impozit 16%                   16% x P40                     rd.90
  P41 Total impozit pe profit        P411+P412                     rd.89 (DUK R41)
  P42 Total credit fiscal            P421+P422+P423                rd.92
  P43 Sponsorizare (in limita)       P431+P432                     rd.99
  P48 Impozit anual datorat          P481+P482; P481=P41-P42-P43-P44-P45  rd.105/106
  P52 Diferenta de plata             (P48+P51)-(P49+P50) daca >=0   rd.110
  P53 Diferenta de recuperat         (P49+P50)-(P48+P51) daca >=0   rd.111
  totalPlata_A  Suma de control      suma(P1..P53), fara sub-randuri 'din care'  rd.20
  Grup (d_grup=1): P412/P48/P50/P51/P52/P53 = 0 (rd.89-111).
  Scadenta (DUK R17): an Data_S>2025 -> LL+3 (250327); an in [2022,2025] -> LL+6 (250626).

GOLDEN calculat de mana (test_d101.test_golden_lant_formule_oficiale): venituri exploatare 100000,
cheltuieli 60000, fara ajustari -> P3=P7=P10=P22=P35=P38a=P40=40000, P411=P41=P48=P52=6400,
totalPlata_A=419200. Proba pe DUK: valid.

DE CE golden si nu doar DUK (lectia platita): mutatie P411 = 16%->cota/50 (impozit dublat, 12800) ->
DUK VALID (nu verifica rata!) dar golden-ul PICA. "Trece DUK" e conditie necesara, nu suficienta -
exact clasa care a ascuns numerotarea inventata luni de zile. Vezi si test_audit_campuri_oficiale.

LIMITA declarata: aplicatia deriva doar P1/P2/P4/P5 din contabilitate (split pe clasa de cont);
ajustarile fiscale detaliate (P11 amortizare, P17-P20 neimpozabile, P23-P33 nedeductibile, P42 credit,
P43 sponsorizare etc.) vin din `manual` (le introduce contabilul) sau raman 0. Pentru o firma fara
ajustari, impozitul = 16% pe (venituri-cheltuieli). Cazurile cu ajustari cer intrarile respective.

## 01.08.2026 — CORECTIE DE REGULA (Costin): temeiul se completeaza ACUM, nu per-cluster (ciclul > ratchet)

Conflict prins de Costin intre doua reguli scrise pe 31.07:
- ### 4/### 6 de mai sus (campania temei): temeiurile lipsa "se completeaza pe CLUSTERE, in ordinea
  riscului, distribuit pe sesiuni" - amanare pe termen nedefinit prin ratchet.
- CICLUL DE NECONFORMITATE (CLAUDE.md): corectare peste TOATA aplicatia ACUM, apoi gard.
Ciclul e regula SUPERIOARA. ### 4 si ### 6 sunt SUPERSEDATE de aceasta intrare in partea de TIMING.

REGULA CORECTA: temeiul se completeaza ACUM pentru TOATE datele existente. Ce nu se poate verifica la
sursa ramane GRI DECLARAT (localizat, cu motiv), NU absent tacut. Gardul trece din RATCHET (baseline
care coboara la infinit = amanare institutionalizata) in PRAG (fix la 0; orice regresie blocheaza)
imediat ce baseline-ul ajunge la 0. Un ratchet care ramane >0 la infinit e amanarea cu alta forma.

CE RAMANE VALID din ### 1-6: formatul structurat (### 1), regula etalon/ACCEPTATE (nu se atomizeaza
etaloanele), clasificarea GRI/ROSU/ACCEPTAT, limita reala a garzii de deriva (### 5, nu exista API
legislativ - data_out e proxy-ul). Se schimba DOAR cadenta: nu "pe masura ce ajungem la cluster", ci ACUM.

MASURAT 01.08 inainte de completare: COTE 12/12 cu temei structurat (TEMEI_BASELINE deja 0); GRI=2
(main.py:4045/4046, bucketing OCR bon pe cota 11/21, cluster TVA verificat - categoria a, atasabile);
7 valori curente cu data_out=None (tva_standard, cas, cass, impozit_venit, cam, plafon_sold_casa,
plafon_avans_decontare) - protejate aparent, garda de expirare TACE la infinit. Restul = etaloane/
fixtures/parametri (ACCEPTATE, nu datorie). Categoria (b) - cluster neverificat: ZERO. Deci se poate
completa tot ACUM, fara amanare. Etapele urmatoare (commit-uri separate): (2) data_out pe cele 7;
(3) atasarea celor 2 GRI + gard GRI din RATCHET in PRAG.

## 01.08.2026 — Gard markeri TEMEI pe functii: criteriu structural EVALUAT si RESPINS, lista explicita

Costin a cerut un gard pe markerii TEMEI de functie, cu CRITERIU INVERSAT enumerabil (nu "e functie
fiscala?" - semantic, ci "produce/consuma o valoare fiscala fara temei?" - structural): o functie intra
sub gard daca (a) contine literal de rata fiscala Decimal("0.NN"), (b) cheama cota() + transforma
rezultatul, sau (c) e apelata de un generator si intoarce o suma. Cu instructiunea: EVALUEAZA inainte de
a implementa; daca acopera lista reala cu putine fals-poz -> implementeaza; daca rateaza mai mult de
cateva -> OPRESTE si treci la lista explicita.

EVALUARE (masurat mecanic, AST pe core/*.py, criteriu a=Decimal 0.NN | b=cota()):
- 57 functii prinse; acoperire lista reala 5/7 (deducere_personala, calcul_salariu, procent_cm, taxe_cm,
  calcul_cm_cod10 PRINSE; calcul_cm si plafon_diurna RATATE - fals-negative).
- ~18 FALS-POZITIVE: helper-e de rotunjire/formatare (_q, _q2, _q4, bani, _bani, _dec, _cant folosesc
  Decimal("0.01")) + cititori subtiri de cota (d394.cota_standard, d301.cote_perioada, facturi.calcul_tva).
VERDICT: proxy-ul sintactic minte in ambele sensuri (exact avertismentul lui Costin) - Decimal("0.NN") nu
distinge rata fiscala (0.55, 0.25) de constanta de rotunjire (0.01, 0.5); "cheama cota()" nu distinge
transformarea de citirea subtire. Criteriul NU e curat.

DECIZIE: NU se implementeaza criteriul structural. Solutia (pre-autorizata de Costin) = LISTA EXPLICITA
intretinuta manual a functiilor care APLICA o regula fiscala cu logica proprie; gardul cere marker DOAR pe
ele. Lista initiala = clusterul salariu/CM (lista reala): salarizare.{deducere_personala, calcul_salariu,
procent_cm, taxe_cm, calcul_cm, calcul_cm_cod10}. Markerii completati ACUM pe toate 6 (3 aveau deja; +3:
calcul_salariu, calcul_cm, calcul_cm_cod10). Gard in verificator: PRAG 0 (orice functie din lista fara
marker BLOCHEAZA). Mutatie: marker scos -> TOTAL 1, BLOCHEAZA.

LIMITA DECLARATA (onesta, mai putin eleganta): gardul NU auto-detecteaza. O functie fiscala noua se ADAUGA
in _TEMEI_FUNCTII + primeste marker - dar asta NU e "cand vine clusterul" (amanarea interzisa): lista reala
CUNOSCUTA e completa ACUM. Functii fiscale din ALTE clustere neincluse inca (plafon_diurna/deconturi,
sponsorizari.plafon_credit, motor.rezerva_legala, tva_incasare, tva_marja) nu sunt in lista reala pe care
Costin a enumerat-o; se adauga cand sunt CONFIRMATE la sursa (identificare, nu amanare - nu exista proxy
automat care sa le enumere corect, dovedit mai sus).

## 01.08.2026 — MODELUL DE TEMEI: corectii si extinderi (DECIZIE luata, nu propunere; IMPLEMENTARE in ture urmatoare)

Costin, 7 puncte. NICIO implementare in aceasta tura - doar registru. Ce se atinge in cod urmeaza separat.

1. **data_out NU se estimeaza (corectie la 31.07/01.08).** O lege spune de CAND intra in vigoare, nu PANA
   cand. data_out nu exista in actul care instituie valoarea - se DERIVA din actul URMATOR: ziua dinaintea
   intrarii in vigoare a succesorului. Valoare CURENTA = data_out None (in vigoare pana apare succesorul;
   termen inventat = falsificare). Valoare ISTORICA = data_out exact, derivat AUTOMAT cand se adauga
   succesorul, nu scris de mana. Cele 7 valori marcate data_out="2026-12-31" estimat=True (Etapa 2, 01.08)
   se CORECTEAZA: data_out -> None; semnalul se muta pe vechimea confirmarii (pct.2). Idem estimat de la
   salariu_minim/facilitate/plafon_facilitate/tichet.

2. **VECHIMEA CONFIRMARII inlocuieste expirarea inventata.** Fiecare temei poarta verificat_la + de_cine.
   Semnalul util nu e "valoarea a expirat" (fals - legea n-a spus asta), ci "n-a mai fost confirmata de N
   luni" -> ALERTA INTERNA catre dezvoltator, NU in interfata contabilului (contabilul plateste tocmai ca
   sa nu urmareasca legislatia). Blocaj la calcul ramane DOAR pentru data_out REAL (derivat din succesor),
   unde valoarea chiar nu mai e valabila. EXPIRA_DUPA_LUNI + cota() RIDICA pe luni (29.07) = expirare
   inventata -> inlocuita.

3. **GRAF DE DEPENDENTE, EXTRAS DIN COD.** Scop: cand o lege modifica ceva, lista locurilor de actualizat.
   Doua cazuri: (a) modificare DIRECTA (art.77 alin.4) -> cauta articolul in registru; (b) modificare PRIN
   EFECT - se schimba salariul minim, nimic nu citeaza HG-ul nou, dar sm intra in deducere/facilitate/
   plafon 12sm/suprataxare part-time/prag tineri -> intrebarea e "cine FOLOSESTE valoarea". Mecanism:
   analizor care gaseste apelurile cota("x") in corpul fiecarei functii fiscale + inchidere tranzitiva.
   Interogare pe graf, NU lista manuala (o lista de mana devine stale la prima refactorizare - tiparul
   pentru care s-a despartit ISTORIC.md si s-a sters DE_FACUT.md). Dependenta sta pe FUNCTIE, nu pe intrarea
   COTE. Suplimentare manuala doar unde extractia nu vede, cu gard ca declaratul nu contrazice codul.
   Limita: o valoare hardcodata care ocoleste cota() nu apare in graf -> gardul de literale fiscale (azi 0)
   e CONDITIA ca graful sa fie complet. Cazul (c) - lege care creeaza obligatie NOUA (IMCA, e-Transport) -
   NU e acoperit de niciun mecanism (nimic nu poate cita un act inexistent): e produs, nu intretinere. Limita.

4. **TEMEIUL PASTREAZA TEXTUL CITAT, nu doar adresa.** "art.77 alin.(4)" e pointer; fraza e continutul. La
   reverificare, comparatie directa: textul din registru vs textul de azi. E si PROBA ca verificarea s-a
   facut, nu ca cineva a scris o referinta plauzibila.

5. **NIVELUL SURSEI, dimensiune a temeiului:** MO/legislatie.just.ro (autoritativ) - redare secundara
   (noulcodfiscal/lege5) - interpretare oficiala (pliant/ghid ANAF) - practica. Motiv: 45% pentru 4+ persoane
   sta pe sursa SECUNDARA si registrul nu spune asta. Un temei verificat la MO si unul dedus dintr-un pliant
   arata identic azi. Gri-ul trebuie sa incapa in STRUCTURA, nu intr-un comentariu.

6. **LANTUL DE ACTE.** Temeiul retine si actul modificator/abrogat. Ex: 4050 are temei HG 1506/2024, dar
   informatia care conteaza e ca HG 1506 ABROGA HG 598/2024 si ca art.2 a fost abrogat la 1 iulie 2026 - de
   acolo se stie ca 4050 a fost in vigoare CONTINUU. (Se practica deja ad-hoc in comentarii COTE; se
   formalizeaza in structura temeiului.)

7. **ZONA I (plan de arhitectura, NEATINSA): FORMULELE NU SUNT VERSIONATE IN TIMP.** Cotele sunt period-aware
   (cota("x", la_data)); formulele nu - deducere_personala() are un singur corp. Daca se schimba scara
   degresiva, ori pierzi trecutul (rectificative/adeverinte/revizuiri calculate gresit), ori acumulezi
   "if data < X". Directie propusa, NEDECISA: fiecare functie fiscala cu variante datate + dispecer pe
   la_data (tiparul cota() pe cod). De masurat intai cate functii ar fi afectate.

### CONTRADICTII cu ce e deja scris (cerut de Costin - "ca la punctul 4/6 de ieri")
- **Pct.1 CONTRAZICE:** (i) Etapa 2 (01.08, commit 4c23994) care a SETAT data_out="2026-12-31" estimat=True
  pe 7 valori - se REVERSEAZA (data_out -> None). (ii) Intrarile estimat de la salariu_minim/facilitate/
  plafon_facilitate/tichet (31.07) - estimat "eroare devreme > cifra moarta" e inlocuit. (iii) GARDUL
  test_nicio_cota_curenta_nu_ramane_fara_data_out (Etapa 2) - cere ca valorile CURENTE sa AIBA data_out;
  pct.1 spune invers (curent = None) -> gardul se INVERSEAZA la implementare (cere verificat_la, nu data_out).
  (iv) comentariul COTE "data_out ESTIMAT ... re-verificare anuala".
- **Pct.2 CONTRAZICE:** decizia 29.07 (EXPIRA_DUPA_LUNI + cota() RIDICA pe luni ca blocaj la calcul) si
  ### 5 din campania temei ("(ii) garda de EXPIRARE ... PROXY de deriva"). Blocaj la calcul ramane DOAR pt
  data_out real; expirarea pe luni devine alerta INTERNA de vechime a confirmarii.
- **Pct.3 TENSIUNE (nu contradictie) cu _TEMEI_FUNCTII (commit cd67271, lista MANUALA):** pct.3 prefera
  extractia. Nuanta care le impaca: "e functie fiscala?" (nevoia de MARKER) e semantic -> manual (masurat:
  proxy sintactic minte); "cine foloseste cota('x')" (GRAFUL de dependente) e sintactic -> extractabil.
  Artefacte diferite, complementare: marker-lista ramane manuala, graful se extrage separat.
- Pct.4/5/6 = EXTINDERI, nu contradictii (pct.6 formalizeaza practica ad-hoc HG 1506 abroga HG 598 deja in
  COTE). Pct.7 = directie noua deschisa, nedecisa - nu contrazice nimic.
- STARE IMPLEMENTARE: ETAPA 1 FACUTA (pct.1+2): estimat SCOS din model; cele 7 data_out=None; data_out se
  DERIVA din succesor (_deriva_data_out); EXPIRA_DUPA_LUNI SCOS; cota() ridica doar pe data_out real (gol);
  verificat_la/de_cine adaugate; gard data_out INVERSAT (curent=None, istoric=derivat); raport intern
  cote_neconfirmate (fost expirare_cote, reformulat: "n-a mai fost confirmata de N luni", fara expira/REFUZA).
  Clasa "expira pe valori curente" cautata: doar expirare_cote (reparat); UIT/token OAuth expira real (nu clasa).
  RAMAS: ETAPA 2 (text_citat/nivel_sursa/lant_acte) + ETAPA 3 (graf dependente). Pct.7 nedecis.

## 01.08.2026 — MASURARE pct.7 (formule versionate in timp) - CIFRA, zero implementare

Cerut de Costin: cate functii ar fi afectate, ce se intampla azi la o schimbare de regula, ce petice
ad-hoc exista deja, ce consumatori retroactivi s-ar rupe, estimare de efort. NU se propune implementarea.

CRITERIU: functie care APLICA o regula (scara, prorata, plafonare, split, procent pe conditie), nu doar
citeste o cota (calcul_tva/cota_standard/cote_perioada/_sal_minim = cititori subtiri, EXCLUSI).

FUNCTII DE REGULA FISCALA (13), cu tip regula + corp:
  salarizare.deducere_personala   scara degresiva 20-45% + step + prag tineri   SINGLE BODY
  salarizare.calcul_salariu       prorata + plafonare + suprataxare + split zi5-6 + facilitate  SINGLE BODY
  salarizare.procent_cm           procent pe cod/zile (55/65/75 progresiv)       SINGLE BODY
  salarizare.taxe_cm              CAS uniform / CASS pe cod / impozit            SINGLE BODY
  salarizare.calcul_cm            formula + split angajator/FNUASS + diminuare   **DATE-BRANCH** (if 2026-02-01<=ref<=2027-12-31)
  salarizare.calcul_cm_cod10      plafonare 25% din baza                         SINGLE BODY
  deconturi.plafon_diurna         plafonare diurna (2.5x, HG 518/1995)           SINGLE BODY
  sponsorizari.plafon_credit      min(0.75%CA; 20% impozit)                      SINGLE BODY
  sponsorizari.credit_sponsorizare credit fiscal + conditii micro/profit         SINGLE BODY
  motor.rezerva_legala            5% profit, cumulat <= 20% capital              SINGLE BODY
  contracte_speciale.calcul_zilier taxe zilier                                   SINGLE BODY
  tva_marja.vanzare_marja         TVA pe marja                                   SINGLE BODY
  tva_marja_turism.marja_turism_special marja + scutire proportionala non-UE     SINGLE BODY

PETICE AD-HOC "if pe data" DEJA EXISTENTE (6) - dovada ca problema a fost intampinata si peticita:
  salarizare.calcul_cm:357        diminuare 1 zi doar pt certificate 2026-02..2027-12 (regula pe interval)
  d101._scadenta:98               scadenta LL+6 (an 2022-2025) / LL+3 (>2025) - regula de structura pe an
  d710:143                        d_recN="1" incepand cu perioada 12.2025 - regula de structura pe perioada
  decontari_asociati.cota_dividend:21  16% (>=2026) / 10% (vechi) - RATA (ar trebui in COTE period-aware)
  lichidare:24                    impozit 16% (>=2026) / 10% - RATA (ar trebui in COTE)
  tva_incasare.plafon_la:31       plafon TVA incasare, schimbare la 2027-01-01 - PRAG pe data

CIFRA: 13 functii de regula fiscala; 12 SINGLE BODY (pierd trecutul la o schimbare de regula), 1 deja
date-branched. + 5 reguli/rate/praguri deja peticite ad-hoc cu if-pe-data (2 rate ar trebui de fapt in
COTE period-aware, nu formule). TOTAL locuri care ar cere versionare in timp: ~18.

CE SE INTAMPLA AZI la o schimbare de regula (single body): se recalculeaza o perioada TRECUTA cu regula
de AZI -> gresit pentru trecut. Nu exista cale de a calcula corect o perioada anterioara; alternativa =
acumulezi if-pe-data (ca la calcul_cm/d101/d710), care se inmulteste si devine ilizibil.

CONSUMATORI RETROACTIVI care s-ar rupe (primesc o perioada trecuta si RECALCULEAZA):
  adeverinta.py:50        calcul_salariu(..., la_data=date(an,luna,1)) - adeverinta de venit pt luna TRECUTA
  stat_plata_api.py:60,145 calcul_salariu(..., la_data=ref) - stat de plata regenerat pt o perioada
  d112.py:443             calcul_salariu(...) - D112 (rectificativa = luna trecuta)
  salarii_contare.py:55   calcul_salariu(...) - note lunare re-postate
  salariati_api.py:339 + main.py:6667  calcul_cm(...) - concediu medical
Toate paseaza deja la_data -> COTELE (ratele) ies period-correct; dar CORPUL formulei e single-body ->
foloseste logica de azi pentru trecut. Aici e ruptura (ex: adeverinta 2025 cu scara deducerii din 2026).

ESTIMARE EFORT (varianta dispecer pe la_data, tiparul cota() pe cod):
- 12 functii single-body -> variante datate + dispecer. Unde regula NU s-a schimbat istoric (majoritatea):
  dispecer cu O SINGURA versiune = refactor structural MECANIC, fara cercetare istorica (~low/functie x 12).
- 6 petice ad-hoc -> consolidare if-pe-data in dispecer (cunosc deja punctele de schimbare).
- 2 rate (cota_dividend, lichidare) -> mutate in COTE period-aware, NU dispecer de formula (mai simplu).
- ~6 consumatori -> deja paseaza la_data, dar trebuie sa respecte VERSIUNEA de formula la acea data.
- 1 gard (functie de regula versionata) - ca gardul de markeri.
COST DOMINANT: cercetarea istorica a regulii DOAR unde s-a schimbat (limitat - cele 6 petice au puncte
cunoscute; restul sunt stabile -> 1 versiune, mecanic). Estimare: campanie MEDIE, comparabila cu
uniformizarea contractului (1 functie/pas). Ordin de marime: ~18 locuri + 6 consumatori + 1 gard,
distribuit pe cateva sesiuni; partea riscanta (istoric) e mica.

NEDECIS - se livreaza cifra, nu implementarea (cerut explicit).

## 01.08.2026 — REGULA COMENZII CUPRINZATOARE: o comanda = o campanie intreaga, nu o etapa

DE CE (cerut de Costin dupa incalcari repetate in aceasta sesiune): Costin nu tasteaza comenzile, le da
prin copy-paste. Fiecare tur de conversatie ii costa timp. Fragmentarea unei campanii deja decise in
etape date pe rand transforma o decizie luata in N runde de asteptare - pierdere directa de timp al lui.

REGULA: o comanda contine TOTI pasii pana la capatul campaniei - de la masurare pana la gard - cu
ramificatiile scrise INAUNTRU: "daca masurarea arata X, faci Y; daca arata Z, opreste-te si spune".

INTERZIS:
- masurarea data separat de implementare CAND rezultatul masurarii nu schimba decizia (masori si implementezi
  in aceeasi comanda; masurarea separata are sens doar cand cifra chiar decide alt drum);
- etape date pe rand cand pot merge impreuna;
- "livreaza X, apoi iti dau Y" cand Y era deja decis.

SINGURA OPRIRE LEGITIMA: o neconformitate care NU putea fi anticipata - cod care se dovedeste altfel decat
parea (ex. d390, unde cele 3 pull-uri erau impletite cu semantica de override), sau o decizie de PRODUS
care cere Costin. Aia nu e fragmentare, e ciclul de neconformitate (CLAUDE.md).

NU e oprire legitima: "am terminat etapa 1, astept confirmarea pentru etapa 2" cand etapa 2 era deja decisa
in aceeasi comanda.

SE APLICA la ambele roluri: arhitectul (Claude) care COMPUNE comenzile - le scrie cuprinzatoare, cu
ramificatii, nu pe felii; executantul (Claude Code) care NU se opreste intre pasii unei campanii aprobate.

RAPORT: la capatul campaniei, nu la capatul fiecarei etape. Etapele raman commit-uri separate (trasabilitate),
dar rularea nu se intrerupe pentru confirmare intre ele.

RELATIA CU ALTE REGULI: intareste si EXTINDE "Metoda 4 comenzi per tema" (CLAUDE.md, 27.07: max 2 citiri ->
1 implementare -> 1 verificare+commit) - de la nivelul COMENZII la nivelul CAMPANIEI. Cele doua nu se bat:
in interiorul unei campanii, fiecare TEMA respecta cele 4 comenzi; campania le inlantuie fara asteptare.
Consecinta acceptata din CICLUL DE NECONFORMITATE (ritmul scade, fiecare neconformitate devine campanie)
ramane - dar campania se DUCE PANA LA CAPAT intr-o comanda, nu se toaca in confirmari.

APLICABIL RETROACTIV LA ACEASTA SESIUNE: sweep DUK -> reconstructie, C -> D, model de temei etapa1 -> 2 -> 3,
pct.7 masurare -> (ar fi trebuit) implementare - toate au fost fragmentate in comenzi separate cand puteau fi
o singura comanda cu ramificatii. Exact tiparul pe care regula il interzice.

### CORECTIE 01.08.2026 (Costin) - componenta comenzii + verificare inainte de executie

Regula de mai sus era scrisa dar INERTA: lipsea definitia componentei unei comenzi conforme si obligatia
de a o verifica INAINTE de executie. Fara ele, exceptia "oprire legitima" a fost folosita pentru a valida
fragmentarea (vezi Partea D). Se completeaza cu:

PARTEA A - DIN CE SE COMPUNE O COMANDA CONFORMA
O comanda acopera o CAMPANIE INTREAGA si contine OBLIGATORIU:
  1. SCOPUL - ce se rezolva si de ce (motivul, nu doar sarcina).
  2. TOTI PASII, de la masurare pana la gard, in ordine. Nu o etapa din mai multe.
  3. RAMIFICATIILE scrise inauntru - "daca masurarea arata X, faci Y; daca arata Z, opreste-te si spune".
     Deciziile previzibile se iau in AVANS, nu se amana pentru tura urmatoare.
  4. CONDITIILE DE OPRIRE - ce anume justifica intreruperea (neconformitate neanticipata sau decizie de
     produs), explicit.
  5. PROBA CERUTA - rosu inainte, mutatie dupa, ce output brut se asteapta.
  6. PORTILE - pytest, verificator, git status, git log.

PARTEA B - VERIFICAREA COMPONENTEI, INAINTE DE EXECUTIE
Inainte de a executa orice comanda, Code verifica daca are componenta de la Partea A. Daca NU e conforma,
NU EXECUTA - raspunde ce lipseste si cere comanda completa. Semne de comanda neconforma, vizibile in text:
  - anunta o etapa ulterioara ("dupa ce raportezi, iti dau urmatoarea etapa", "apoi continuam cu");
  - cere o masurare care nu schimba nicio decizie (test: daca raspunsul e "campania se face oricum,
    indiferent ce arata cifra", masurarea nu justifica o comanda separata);
  - taie in bucati o campanie deja aprobata in conversatie;
  - lipsesc ramificatiile, deci executantul va trebui sa intrebe la primul caz neprevazut.
Verificarea NU e optionala si nu se ocoleste prin justificare. Exceptia "oprire legitima" se aplica DOAR
cand rezultatul poate produce DECIZII DIFERITE, nu doar cifre diferite.

PARTEA C - RESPONSABILITATE DUBLA
Arhitectul raspunde de compunerea comenzii conforme. Executantul raspunde de REFUZUL celei neconforme.
Niciunul nu e scuzat de celalalt.

PARTEA D - DOVADA (01.08.2026)
Comanda "masoara cate din cele 11 functii sunt in salarizare.py si cate in alte module; dupa ce raportezi,
iti dau urmatoarea etapa" a fost executata fara obiectie si justificata de executant ca "masurare pura,
oprire legitima". Cifra 6-vs-7 nu schimba nimic - campania era deja aprobata. Exceptia a fost folosita
pentru a VALIDA fragmentarea. Regula era scrisa dar inerta: lipsea definitia componentei si obligatia de
verificare inainte de executie (reparate de Partile A-B).

## 02.08.2026 — Familia salarizare = GRUP CO-LOCAT; departajare FISCAL ca proxy; tichete D2/D3/#3

DECIZIE 1 (Costin) - CICLUL facilitate<->deducere: familia salarizare (facilitate, deducere personala,
suprataxare part-time, proratare, + calcul_salariu) se trateaza ca GRUP CO-LOCAT, verificat IMPREUNA, bifa
pe GRUP nu pe membri individuali. Motiv: garda anti-stale le co-loca deja (test_facilitate_prorata_luna_angajare);
ciclul e REAL (deducerea foloseste salariul minim prin facilitate; facilitatea foloseste pragul deducerii) - nu
se rupe artificial o legatura care exista in lege. NU se schimba bifele existente.

DECIZIE 2 (Costin) - DEPARTAJAREA secventei: Risc=FISCAL ca proxy pentru "intra intr-o declaratie ANAF" e
APROXIMATIE DECLARATA, nu echivalenta: un cluster FISCAL care produce doar afisare interna nu intra intr-o
declaratie. Acceptabil (departajarea conteaza putin la adancime 2), consemnat ca aproximatie.

CLUSTER tichete masa/vacanta - cele trei deschideri (31.07):
- D2 (nr tichete pe zile EFECTIV lucrate, HG 1045/2018 art.10 alin.3): datele CO/delegatie/absente EXISTA in
  pontaj (F135) DAR modelul "fara rand = prezent" (pontaj.py:31) + decuplarea deliberata 17.07/20.07 fac ca
  alimentarea tichet_zile din pontaj sa functioneze DOAR daca firma completeaza pontajul. Firma care are CO dar
  nu-l inregistreaza -> supra-acordare tacuta. DECIZIE DE PRODUS (pontaj autoritativ pentru payroll, reversarea
  decuplarii 20.07), NU cod. RAMANE xfail (test_datorie_tichete_masa_zile_efectiv_lucrate). Nu s-a improvizat.
- #3 (baza CASS pe tichete, art.78): FONDUL confirmat prin DERIVARE (art.157 face CASS obligatorie din 2024 ->
  art.78 deduce contributiile obligatorii din baza impozitului). Litera verbatim (art.78 alin.2 lit.a) NEconfirmabila
  pe legislatie.just.ro (portal dinamic, fara API - documentat in test_datorie_citate_literale_tichete_portal).
  VERDICT GRI DECLARAT: fond corect prin derivare, verbatim de reconfirmat pe PDF MO. NU verde.
- D3 (CAS pe excesul de vacanta peste 6 sm): deferrarea (atingea baza salariala = clusterul deducere) a DISPARUT
  odata cu grupul co-locat. DE IMPLEMENTAT: excesul = beneficiu salarial integral (CAS+CASS+impozit) in BAZA
  salariala. Proba DUK obligatorie (31.07: DUK a respins CAS pe exces ca linie separata via B4_7 - baza recalc
  din salariu S731/S74) -> excesul intra in baza_contrib, nu ca linie de tichet. Vezi urmatorul commit.


## 02.08.2026 — D3 INCHIS: CAS peste plafon vacanta declarat in D112 validat DUK (exces in brutul declarat)

Decizie Costin: excesul de tichete de vacanta peste plafonul ANUAL (6 sal.minime, OUG 8/2009 art.1) intra in
VENITUL BRUT DECLARAT (S731/build_xml d112), nu doar in baza de contributii. Motiv: DUK are dreptate - regula
S74 recalculeaza B4 din brutul declarat; excesul e avantaj salarial (CF art.138/156), deci face parte din brut
prin natura lui. Cablarea 31.07 punea excesul in baza fara sa-l puna in brut -> INCOERENT, respins de DUK.

IMPLEMENTAT: calcul_salariu.b_imp = brut + exces (gross impozabil); atinge deducere/CAM/contributii/brut declarat;
NET-ul ramane pe CASH (excesul e voucher, nu numerar). d112: excesul intra in brut (bazac = brut+exces-facil),
cumulat ANUAL (beneficii_api.exces_vacanta_luna). Plafonul e anual, pe cumulat.

SCHIMBARI DERIVATE (corectie, nu regresie - aratate): brut 5000 + exces 4000 -> brut declarat 9000; deducere
personala 800.13 -> 0.00 (excesul urca brutul peste plafonul sm+2000); CAS 1250 -> 2250, CASS 500 -> 900, CAM
112.50 -> 202.50; net cash 3005 -> 1265. FACILITATEA la salariul minim NESCHIMBATA (200 -> 200): eligibilitatea
sta pe venitul brut CONTRACTUAL (vbt), iar excesul e one-off, nu contractual -> nu intra in vbt.

PROBA: D112 cu exces 5700 (grant 30000 - plafon 24300) -> DUK VALID; regresie D112 fara exces -> tot VALID
(core/test_exces_vacanta_d112.py). "cas peste plafon vacanta declarat in d112 validat duk" - marker de inchidere.

## 02.08.2026 — Perioada confirmata (cap.23): doua datorii de PRODUS (rol + escape manual)

DATORIE (rol): confirmarea pontajului cere rolul admin_firma. In practica salarizarea o pregateste asistentul
SENIOR, deci blocajul risca sa fie ocolit prin partajarea contului admin_firma. RBAC nu distinge azi senior/junior
la nivel de operatiune (poate_valida). De REEVALUAT cand RBAC distinge poate_valida la nivel de operatiune - atunci
confirmarea se leaga de dreptul granular, nu de rolul larg.

DATORIE (escape manual): NU se adauga un camp "numar manual de tichete cu justificare" ca alternativa la
confirmarea pontajului. Motiv: odata ce exista, devine calea IMPLICITA (se completeaza manual in loc sa se confirme
pontajul), iar controlul legal (zile efectiv lucrate, HG 1045/2018 art.10(3)) devine decorativ. Se adauga DOAR daca
pilotul arata cazuri reale in care confirmarea pontajului e imposibila. Pana atunci, escape-ul primar = confirmarea.

NOTA reversibilitate: fluxul de rectificativa EXISTA (coada_api nr_depunere, d710) -> blocarea editarii pontajului
dupa depunerea D112 trimite la un flux real, NU e blocaj final. (Nu e limita GARZI.)


## 02.08.2026 — D2 INCHIS: tichete masa zile efectiv lucrate din pontaj implementat (cap.23 perioada confirmata)

Numarul de tichete de masa = zile EFECTIV lucrate (HG 1045/2018 art.10(3)): zile lucratoare - CM - CO/delegatie/
absente/invoire din pontaj. Reversarea decuplarii 20.07 pe partea de calcul (stat_plata + d112). Ambiguitatea
"prezent = fara rand" rezolvata prin CONFIRMAREA perioadei (cap.23): fara pontaj CONFIRMAT, calculul tichetelor
BLOCHEAZA (blocaj motivat); dupa confirmare (admin_firma), autoritativ. Reversibilitate: de-confirmare automata la
editare, blocare dupa depunere D112 (-> rectificativa). UI pe ecranul pontaj (semafor gri/verde + caseta-info +
buton-verde). Gard verificator (GARD PERIOADA CONFIRMATA). Marker: tichete masa zile efectiv lucrate din pontaj implementat.


## 02.08.2026 — CONCEDII MEDICALE: cod 06 D_11 (urgenta) implementat; cod 02 GRI; taxe_cm↔d112 fara divergenta

**Cod 06 (urgenta medico-chirurgicala) — campul D_11 implementat.** Structura oficiala D112
(anaf_surse/d112_struct_anaf.txt:5504-5525): D_11 = "Cod urgenta medico-chirurgicala", C(3), OBLIGATORIU daca
D_9=06 ("Daca D_9=06 si D_11 is null → Nu s-a completat codul de urgenta medico-chirurgicala"), <=177 daca
data_acordare>29.05.2020 (altfel <=175), mutex cu D_12 (cod 05 infectocontagios). Nomenclatorul HG 423/2020
(cele ~177 etichete de urgenta) NU e in sursa (doar headerul la :7990) — NU s-au inventat etichete; campul e un
**input numeric validat 1..177**, nu un dropdown cu denumiri. Implementat: coloana `cod_urgenta` pe
concedii_medicale (tenant_template.sql + core/migrare_cod_urgenta_cm.py, idempotent); validare API
(salariati_api.salveaza_concediu: la cod 06 D_11 obligatoriu 1..maxu); emisie d112 (asiguratD D_11 cand cod=06);
UI conditionat pe ecranul de concedii (flux_concediu.js: camp .camp-input + .camp-ajutor citand HG 423/2020 +
validare .msg-eroare — DS cap.4/cap.6, zero pattern nou). **Proba DUK VALID** (raw): cod 01 valid, cod 06
(D_11=123) valid, cod 08 valid — test_d112_cod06_urgenta_valid_duk (gated DUK), test_d112_urgenta_cod06_emite_d11
(emisie, RED->GREEN->mutatie). Lectie DUK: cod 06 ambulatoriu (loc_prescriere=1) <=5 zile (regula S96.2); serie+numar
(D_1/D_2) obligatorii — prima proba a picat pe date de test invalide, nu pe D_11.

**Cod 02 (accident de traseu) — GRI, fara reparatie de formula.** Codul trateaza cod 02 ca accident FAAMBP
(procent_accident/100 = 80/100), corect: accidentul de traseu recunoscut de ITM E accident de munca (Legea
346/2002). Scenariul "75% boala obisnuita" = cazul in care accidentul NU e recunoscut → operatorul recodifica la
01, NU e o ramura de formula pe cod 02. Deci fara divergenta de reparat. Verbatim OUG 158/2005 art.17-18 + regula
recunoasterii ITM = neobtinut la MO → nivel_sursa GRI (REDARE, sursa secundara).

**taxe_cm ↔ d112 — fara divergenta.** d112.py:186 apeleaza functia canonica salarizare.taxe_cm PER CERTIFICAT
(cod): CAS 25% uniform, CASS 10% doar 01/07/10. Unificarea din 31.07 confirmata la sursa; nicio a doua instanta
de calcul CM in d112 (cautat in tot codul, nu doar instanta).

Marker: cm d112 cod 06 urgenta d_11 validat duk.

## 02.08.2026 — PAS 7 (inchidere procedura): trei decizii de sesiune consemnate

Trei decizii luate in sesiunea 02.08 care traiau doar in chat, scrise la INCHIDEREA campaniei (nu la sfarsitul zilei, cf. ARHITECT.md pct.5). Secventa de clustere NU se schimba (ramane 62): niciun cluster nu s-a inchis la acest pas — CM4 si D_11 sunt datorii pe clustere DEJA inchise (concedii medicale, PAS 6), iar tichete culturale ramane neverificat in secventa (fara test/temei). Verificat inainte de a scrie: secventa persistata la 62, toate clusterele √ deja scoase din lista.

**(a) CM4 — plafonul de 12 salarii minime pe baza de calcul CM SE IMPLEMENTEAZA, nu ramane datorie permanenta.**
> ERATA 02.08.2026 (decizia f): temeiul citat mai jos ca "art.10 alin.(2)" e GRESIT — plafonul de 12 sm pentru SALARIATUL in activitate (art.1(1) lit.A) e la **art.10 alin.(1)** (verdict 1, verbatim in anaf_surse/oug_158_2005_consolidat.html); alin.(2) priveste lit.C (indemnizatie de somaj). Sursa a fost obtinuta si plafonul IMPLEMENTAT — vezi intrarea 02.08 "CM4 plafon implementat" de mai jos.
DECIZIE: media zilnica de calcul (Mzbci) se capata la (12*sm)/nzl in `_calcul_cm_core` (OUG 158/2005 art.10) — plafonul se aplica, nu se lasa datorie la nesfarsit. CONDITIE: verbatim OUG 158/2005 **art.10 alin.(2)** la nivel Monitorul Oficial. Fara verbatim: BLOCAJ MOTIVAT, nu implementare din memorie.
REZULTAT EFECTIV PAS 1 (consemnat aici, cerut de comanda): verbatim art.10(2) NEOBTINUT la MO — `anaf_surse/` nu contine OUG 158/2005 (doar `d112_struct_anaf.txt`, care da structura campurilor D112, nu textul art.10(2)). Deci: NEIMPLEMENTAT la acest pas, ramane BLOCAJ MOTIVAT. Datoria ramane deschisa: xfail strict `test_datorie_cm_plafon_12sm` (reason cu marker). Se inchide cand plafonul e aplicat + probat (media capata pe un caz peste plafon) + consemnat cu marker aici.
ALTERNATIVA RESPINSA: implementarea plafonului din derivare/memorie fara textul art.10(2) — respinsa (proxy sintactic minte in ambele sensuri; plafonul e VERDICT-critical pe indemnizatie).
LIMITA: art.10 alin.(1) (12 sm/luna) e confirmat (vezi intrarea 30.07 concedii medicale); alin.(2), care defineste APLICAREA pe baza de calcul zilnica, e cel neobtinut.

**(b) Etichetele HG 423/2020 pentru campul D_11 — NU se implementeaza (dropdown cu denumiri).**
DECIZIE: campul D_11 (cod urgenta medico-chirurgicala) ramane input NUMERIC validat 1..177, conform structurii oficiale D112 — NU se adauga dropdown cu denumirile celor ~177 etichete. Mecanica implementarii numerice e scrisa o singura data la intrarea 02.08 „CONCEDII MEDICALE: cod 06 D_11 (urgenta) implementat" (mai sus in acest registru) — NU se rescrie aici (sursa unica).
MOTIV: numericul 1..177 e conform (`anaf_surse/d112_struct_anaf.txt`: C(3), obligatoriu daca D_9=06); dropdown-ul cu denumiri ar cere INVENTAREA etichetelor, iar nomenclatorul HG 423/2020 NU e in `anaf_surse/` (doar headerul).
STATUT: DATORIE DESCHISA pana la obtinerea nomenclatorului oficial. A NU se trata ca lipsa (campul functioneaza si e DUK-valid) si a NU se „repara" prin inventarea etichetelor.
ALTERNATIVA RESPINSA: dropdown cu etichete compuse din memorie/internet — respins (nu se inventeaza continutul unui nomenclator oficial).

**(c) Push pe main — decizie exclusiva a lui Costin.**
DECIZIE: executorul COMITE LOCAL si se opreste; NU impinge pe main din proprie initiativa, INDIFERENT de formularea comenzii. Push-ul il decide Costin, separat.
INLOCUIESTE partea de push automat din decizia 30.07 („bucla pe pasi cu commit+push la fiecare pas", intrarea „PROCEDURA DE LUCRU"): commit-ul per pas ramane, push-ul automat se ABROGA. (In CLAUDE.md nu exista norma activa de push per pas — deci fara drift de actualizat acolo.)
MOTIV: main e partajat cu Costin; publicarea e decizie de produs, nu de executie (ARHITECT.md pct.4). Un push din initiativa executorului scoate din mainile lui Costin momentul publicarii.
LIMITA: nu schimba igiena locala — `git pull --rebase` inainte de commit ramane.

SIGURANTA (adaugat 03.08.2026, cerut de Costin) — OBLIGATIE a executorului, nu optiune: la finalul FIECAREI rulari,
dupa poarta verde si tree curat, executorul face push pe ramura de SIGURANTA `backup/lant-<data>`. Ramura de
siguranta NU e main, NU publica nimic, NU se merge-uieste - e doar a doua copie a muncii, in afara serverului.
Push-ul de siguranta NU cere aprobare (spre deosebire de push-ul pe main): absenta lui e o DEFECTIUNE, nu o alegere.
Un raport care nu declara `BACKUP: <ramura> — <n> commituri` e INCOMPLET. Regula push-main de mai sus ramane
NESCHIMBATA: main tot decizia exclusiva a lui Costin.


## 02.08.2026 — CM4 plafon implementat; ziua 15; decizii de sesiune (d, f, g, i)

Campania CM4 (prioritate confirmata Costin 02.08). Temeiuri verificate la sursa (anaf_surse/RAPORT_verificare_temeiuri.md).

**CM4 — plafon 12 salarii minime, IMPLEMENTAT in calcul_cm.**
TEMEI: OUG 158/2005 **art.10 alin.(1)** (verdict 1 VERDE, verbatim anaf_surse/oug_158_2005_consolidat.html): baza de calcul = media veniturilor lunare din ultimele 6 luni "pana la limita a 12 salarii minime brute pe tara lunar". OMS 15/2018 ART.61 + Exemplul nr.5 (verdict 4 VERDE): plafonul se aplica LUNAR, pe fiecare din cele 6 venituri, INAINTE de mediere (coloana vplaf capeaza lunile care depasesc 12*sm).
IMPLEMENTARE: `_calcul_cm_core` primeste optional `venituri_lunare = [(venit, zile, data_luna), ...]`; fiecare venit se capeaza la `12 * cota("salariu_minim", data_luna)` inainte de suma. Apelantii pe suma (fara defalcare) pastreaza comportamentul vechi (fara plafon). Teste: test_cm_plafon_* (toate sub / o luna peste / toate peste / traverseaza schimbarea de sm 4050->4325 / luni asimilate). **Marker de inchidere datorie: cm plafon 12 salarii minime aplicat in calcul_cm** (xfail test_datorie_cm_plafon_12sm ELIMINAT, sold datorii 20 -> 19).
BLOCAJ MOTIVAT (regula "sm in luna"): valoarea plafonului lunar foloseste salariul minim IN VIGOARE IN LUNA al carei venit se plafoneaza. Norma (OMS Exemplul 5) exemplifica cu sm ANUAL ("pentru anul 2017/2018 = 12 x sm"), din era cu un singur sm/an — claim 5 GRI, neconfirmat verbatim pentru era cu doua sm/an. Decizie arhitect 02.08: se aplica sm-pe-luna (interpretarea coerenta cu "12 sm lunar" din art.10(1)); consemnat ca blocaj motivat in GARZI.md, de reconfirmat la sursa (ordin/circulara MS/CNAS pe era cu doua sm/an).
Salarii minime confirmate la sursa (Faza 0): HG 1506/2024 (4.050 lei de la 01.01.2025, anaf_surse/hg_1506_2024_salariu_minim.html) si HG 146/2026 (4.325 lei de la 01.07.2026, anaf_surse/hg_146_2026_salariu_minim.html).

**(i) Ziua 15 la 75%.**
CE: art.17(1) lit.b = "intre 8 si 14 zile" (65%), lit.c = "peste 15 zile" (75%); ziua 15 nu e acoperita explicit de text (gol de redactare). DE CE: interpretare favorabila asiguratului (progresia 55->65->75 pe durata; ziua 15 apartine palierului superior). CUM: `_procent_cm_l141_2025` cod 01 mapeaza `zile_episod >= 15 -> 75%`, explicit (nu in `else`), cu comentariu care citeaza golul. GARD: test_cm_ziua15_este_75pct (pica daca cineva o muta tacit la 65%). CINE DECIDE: arhitect (Costin), 02.08.2026.

**Rename `_procent_cm_2018` -> `_procent_cm_l141_2025`.** Numele vechi era capcana: functia implementeaza forma din 01.08.2025 (Legea 141/2025 art.IX), nu forma 2018. Varianta ramane inregistrata la data_in 2018-01-01 (o singura varianta acopera toate datele) — dar forma L141/2025 aplicata inclusiv inainte de 01.08.2025 e o DATORIE deschisa (art.XI, vezi mai jos), fiindca procentele pre-141 nu-s verificate la sursa.

**(f) Temeiul CM4 = art.10 alin.(1), nu alin.(2).** Datoria CM4 (test_datorie) si decizia (a) citau art.10 alin.(2); corect e alin.(1) (salariat lit.A). alin.(2) = lit.C (indemnizatie somaj). Decizia (a) adnotata cu erata. Gasit prin verificarea la sursa (verdict 1/2).

**(d) Cautare la sursa oficiala autorizata.** Cand `anaf_surse/` nu contine actul necesar unui verdict, executorul e autorizat sa il caute la sursa OFICIALA (Monitorul Oficial / legislatie.just.ro / static.anaf.ro / site-ul ministerului emitent) si TREBUIE sa salveze ce descarca in `anaf_surse/` (cu sha256, cod HTTP). Sursa secundara NU inlocuieste primarul; daca primarul nu se obtine, verdictul ramane GRI. (Decizie luata implicit la campania de verificare 02.08, nescrisa pana acum.)

**(g) Deriva legislativa pe procentele CM = GATE inaintea constructiei de functionalitate noua.** Inainte de a construi feature nou pe salarizare, procentele CM (art.17, forma in vigoare) se confrunta cu sursa (RAPORT verificare). Motivul: o functionalitate noua asezata peste procente derivate ar propaga eroarea. La aceasta campanie gate-ul a trecut (procentele 55/65/75 confirmate, cod aliniat).

DATORIE NOUA deschisa (art.XI L141/2025): selectia de regim dupa data certificatului INITIAL al episodului (forma veche pentru episoade cu certificat initial < 01.08.2025) NU e implementata — `_VARIANTE_PROCENT_CM` are o singura varianta (forma L141/2025). Procentele pre-141 nu-s verificate la sursa (nu-s in anaf_surse/) -> BLOCAJ MOTIVAT, nu se inventeaza. Urmarita de xfail strict test_datorie_cm_art_xi_regim_initial (se inchide cand forma pre-141 e obtinuta verbatim la MO + varianta datata adaugata + teste pe ambele parti ale lui 01.08.2025). SOLD DATORII: intrare 20; CM4 inchisa (-1); art.XI desurfatata (+1, gap latent care exista deja in cod, acum urmarit) => sold la iesire 20. Nu 19: onestitatea peste cifra (art.XI e un bug real de procent pe CM pre-2025, nu se ascunde).

## 02.08.2026 — Tichete culturale: functionalitate noua LIVRATA (Legea 165/2018 cap.V)

Feature nou end-to-end (prioritate confirmata Costin, dupa CM4). Temeiuri toate VERDE la sursa
(anaf_surse/RAPORT_verificare_temeiuri.md). Increments testate A-F (commit-uri separate).

**(e) Tichetele culturale = FUNCTIONALITATE NOUA, nu cluster de verificat.** In inventar figura ca pozitia 1
in secventa (placeholder fara cod). Nu e cod existent de aliniat la lege (Sesiunea A) - e feature construit de
la zero cu temeiuri verificate la sursa din start. Iese din secventa ca "implementat cu temei", nu ca "aliniat".

**(h) Regula etalonului: se urmeaza STRUCTURA, nu tratamentul fiscal.** Etalon = tichete masa/vacanta pe
STRUCTURA (beneficii_lunare one-off, calcul_salariu, stat, d112, UI din firme.js). DAR tratamentul fiscal e cel
al CULTURALULUI, care DIFERA de masa/vacanta pe CASS: culturalul NU intra in CASS (CF art.157(2) excepteaza
NUMAI masa+vacanta, verdict 11); masa/vacanta AU CASS. Gardul BILETE_VALOARE_TRATAMENT (test_bilete_valoare_
declara_toate_tratamentele) impiedica copierea tacita a tratamentului de la un bilet la altul.

TRATAMENT FISCAL (verdicte, verbatim in anaf_surse/): impozit 10% pe valoarea nominala INTEGRALA (CF art.76(3)h,
verdict 13); CAS NU (art.142 lit.r, verdict 10); CASS NU (art.157(2), verdict 11); CAM NU (art.220^4(2), verdict
12); nu intra in plafonul 33% (verdict 14); angajator: cheltuiala sociala deductibila 5% (art.25(3)b pct.3).
VALOARE NOMINALA: 10 lei sau multiplu de 10, max 50 (art.22(2), verdict 15). PLAFON: lunar/eveniment indexat
semestrial prin ordine MF/MC - `common.plafon_cultural()`: 220/450 (apr-sep 2025, ord.361/2680/2025) si 250/490
(apr-sep 2026, ord.369/2624/2026), CONFIRMATE primar; fereastra oct.2025-mar.2026 (S2 2025 = 240/470) e GRI
(ordinul de mijloc stub pe just.ro) -> BLOCATA motivat (nu se calculeaza tacit), GARD in beneficii_api.seteaza.

IMPLEMENTARE: DB beneficii_lunare (tip 'cultural', eveniment ''=lunar/'ocazional'; template + migrare idempotenta);
calcul_salariu (param tichet_cultural, impozit only); wiring stat_plata_api + d112 (impozit declarat, NU in baza
CASS); UI firme.js (buton + cultural lunar/ocazional); teste unit + DB + GARD.

**D112 - camp identificat, emisie la nivel ETALON.** Campul oficial = E3_74 "8.3.1.3 Contravaloarea tichetelor
culturale" (d112_struct_anaf.txt:6318), parte din suma E3_60 (avantaje 8.3). Generatorul d112 NU emite sectiunea
8.3 (avantaje detaliate: E3_10 masa / E3_75 vacanta / E3_74 cultural) pentru NICIUN bilet - le raporteaza prin
baza CASS (masa/vacanta) si impozit. Culturalul se raporteaza IDENTIC cu etalonul: prin IMPOZIT (nu in baza CASS,
neavand CASS). LIMITA CUNOSCUTA (generator-wide, NU specifica culturalului): sectiunea 8.3 avantaje (E3_10/74/75)
nu e emisa - candidat de campanie separata; masa/vacanta au aceeasi limita si sunt bifate.

INCHIDERE CLUSTER: "tichete culturale | salarizare" bifat √ 02.08 (implementat + temeiuri VERDE + teste + D112 la
nivel etalon). Secventa 62 -> 61. Marker: tichete culturale livrat functionalitate noua cu temei verificat.

DATORIE NOUA (candidat, NU al acestei campanii): emisia sectiunii 8.3 avantaje in D112 (E3_10/72/73/74/75) pentru
TOATE biletele de valoare - generator-wide, informativ. Neurmarita ca xfail aici (nu blocheaza declaratia; DUK
valideaza fara ea).

## 02.08.2026 — Tichete de cresa: functionalitate noua LIVRATA (Legea 165/2018 art.19)

Feature nou end-to-end (lant nesupravegheat, clusterul urmator dupa tichete culturale). Tratament fiscal
IDENTIC cu tichetul cultural (impozit 10%, FARA CAS/CASS/CAM). Increments testate 1-3.

TRATAMENT FISCAL (VERDE, anaf_surse/RAPORT_verificare_temeiuri.md): impozit 10% pe valoarea nominala INTEGRALA
(CF art.76(3)h, verdict 13); CAS NU (art.142 lit.r enumera "tichetelor de cresa", verdict 10); **CASS NU**
(art.157(2) excepteaza NUMAI masa+vacanta, verdict 11 - DIVERGENTA vs etalon, ca la cultural); CAM NU (art.220^4
(2), verdict 12). Valoare nominala: 10 lei sau multiplu de 10, max 100 (L165 art.19(2)).

**PLAFON: 450 lei/luna/COPIL (L165 art.19(1)), BAZA legala confirmata la primar.** Valoarea se indexeaza
semestrial prin ordine MF/MMSS - NEconfirmate la sursa primara (verdict 17 GRI: ordinul 368/179/2026 = 740 lei
apare doar in surse secundare; mmuncii.gov.ro HTTP 503 persistent). REGULA DE LANT (§2.3 pct.3): GRI = blocheaza
si merge mai departe. `common.plafon_cresa(la_data, nr_copii)` = 450*nr_copii (baza); grant-urile care depind de
indexarea neconfirmata (>450/copil) sunt BLOCATE cu mesaj (GARD in beneficii_api.seteaza). Cap conservator: nu se
aplica 740 tacit. Cand un ordin de indexare e confirmat la MO, se adauga o fereastra (ca la cultural).

IMPLEMENTARE: DB beneficii_lunare (tip 'cresa'; template + migrare idempotenta migrare_tichet_cresa.py);
calcul_salariu (param tichet_cresa, impozit only, acelasi tratament ca cultural); wiring stat_plata_api + d112
(impozit declarat, NU in baza CASS); UI firme.js (buton + cresa, nr copii + valoare); nr_copii pt validare
(nepersistat, default 1). Registru BILETE_VALOARE_TRATAMENT[cresa]. Teste unit + DB + GARD.

D112: camp oficial E3_72 "8.3.1.1 Contravaloarea tichetelor de cresa" (d112_struct_anaf.txt:6306), parte din E3_60.
Ca la cultural: generatorul NU emite sectiunea 8.3 avantaje pentru NICIUN bilet -> cresa se declara la nivel etalon
prin IMPOZIT (nu in baza CASS). Limita generator-wide (8.3 neemisa), nu specifica.

INCHIDERE CLUSTER: "tichete cresa | salarizare" bifat √ 02.08 (implementat + temeiuri VERDE + teste + D112 etalon;
plafon = baza 450 confirmata, indexarea GRI blocata cf. regula de lant). Secventa 61 -> 60.

BLOCAJ CONSEMNAT (nu xfail, cf. §2.3 pct.3 - GRI merge mai departe): valoarea indexata a plafonului de cresa
(>450/copil, ex. 740 din 2026) - neconfirmata la primar. Se deblocheaza cand un ordin MF/MMSS e obtinut la MO si
adaugat in plafon_cresa (fereastra datata). Pana atunci, cap conservator la baza 450/copil.

## 02.08.2026 — Cluster cota profit 16% + IMCA (d101): cota VERIFICATA, IMCA = datorie noua

Clusterul urmator din agenda dupa tichete cresa (lant nesupravegheat). Sesiunea A = aliniere cod existent la lege.

**Cota impozit pe profit 16% - VERIFICATA la sursa.** CF art.17 (verbatim anaf_surse/cod_fiscal_227_2015_consolidat.html):
"Cota de impozit pe profit care se aplica asupra profitului impozabil este de 16%" (stabila din 2005). Valoarea e in
common.COTE (impozit_profit, CF art.17, verificat 02.08). d101 o aplica P411 = 16% x P40. Test cu temei:
test_cota_profit_16pct_din_cota_cu_temei. GAP MINOR (nu blocheaza): d101 foloseste literalul COTA_STANDARD=16
(default + override manual din `manual`), NU cota("impozit_profit") period-aware - valoarea e corecta si stabila,
dar rutarea prin COTE (disciplina "fara cote literale") ramane de facut (follow-up, low-risk).

**IMCA (impozit minim pe cifra de afaceri, CF art.18^1) - NEIMPLEMENTAT = DATORIE NOUA.** graf_temei.py il
recunoaste ca obligatie NOUA neacoperita. Verificat la sursa (art.18^1): contribuabili (altii decat art.15) cu
cifra de afaceri > 50 mil. euro anul precedent, care determina impozit pe profit mai mic decat IMCA, platesc la
nivelul IMCA. IMCA = 1% x (VT - Vs - I - A): VT=venituri totale; Vs=venituri scazute (neimpozabile art.23/24 +
costuri stocuri/servicii in curs + productie imobilizari); I=investitii; A=amortizare. Comparatie max(impozit
profit, IMCA); reguli de grup (alin.8, cifra insumata) si trimestriale (alin.6); modificat de OUG 8/2026 (din anul
fiscal 2026). xfail strict test_datorie_d101_imca. SOLD DATORII 20 -> 21.

CLUSTER: NU se inchide (IMCA, in numele clusterului, e neimplementat). Cota 16% verificata (progres); IMCA = feature
substantial care schimba ce declara firmele > 50 mil euro in D101 - se implementeaza dedicat, NU pe jumatate
(corectitudine fiscala pe declaratii reale). Secventa ramane 60. OPRIRE LANT cu predare: IMCA e blocajul care cere
o campanie dedicata.

## 02.08.2026 — IMCA implementat (CF art.18^1): cluster cota profit + IMCA INCHIS

Continuarea clusterului cota profit + IMCA (decizie Costin: implementez IMCA acum). Structura D101 (P46/P47/P48,
comparatia alin.5) exista deja; lipsea CALCULUL IMCA (P47) + eligibilitatea - acum implementate si verificate
verbatim la sursa (anaf_surse/cod_fiscal_227_2015_consolidat.html, art.18^1).

IMPLEMENTARE (core/d101.py): `impozit_minim_cifra_afaceri(vt, vs, i, a)` = 1% x (VT-Vs-I-A), negativ -> 0
(art.18^1 alin.3-4); `datoreaza_imca(vt, vs, curs)` = cifra de afaceri (VT-Vs) > 50.000.000 euro (alin.1). Wiring
in calcul_d101 (param `imca={vt,vs,i,a,curs}`): cand eligibil, P47 = IMCA computat; sub prag, P47=0. Comparatia
existenta (P46 vs P47 -> P48=P481 profit / P482 IMCA) neschimbata. I si A (investitii/amortizare, alin.3) sunt
determinate de contabil si primite ca intrari. Teste: test_imca_formula_1pct, test_datoreaza_imca_prag_50mil_euro,
test_imca_wiring_p47_si_comparatie_p48, test_imca_sub_prag_p47_zero. **PROBA DUK: test_imca_d101_duk_valid** -
d101 cu IMCA (P47=2.720.000, P48=P482) trece DUKIntegrator (structura P47/P48 neschimbata).

Marker inchidere datorie: **d101 imca impozit minim cifra de afaceri implementat si probat duk**. xfail
test_datorie_d101_imca ELIMINAT. SOLD DATORII 21 -> 20.

Cota 16% (CF art.17) verificata + IMCA implementat + probat DUK -> CLUSTER "cota profit 16% + IMCA | d101"
INCHIS √ 02.08. Secventa 60 -> 59. GAP MINOR ramas (nu blocheaza, nu e datorie): d101 foloseste literalul
COTA_STANDARD=16 in loc de cota("impozit_profit") period-aware - valoarea corecta, rutarea prin COTE = follow-up.

## 03.08.2026 — Cluster amortizare | d101: VERIFICAT (ajustarea fiscala art.28), cu datorie MF pe metode

Clusterul urmator din lant dupa cota profit + IMCA. Sesiunea A = aliniere cod existent la lege. Verificat la
sursa (anaf_surse/cod_fiscal_227_2015_consolidat.html, art.28 Amortizarea fiscala).

**d101 trateaza CORECT amortizarea (art.28) - VERIFICAT.** d101 ia amortizarea ca INPUT (P-fields): P11
"Amortizare fiscala" (deducere, in P16 total deduceri -> reduce profitul impozabil); P28 "Cheltuieli cu
amortizarea contabila" (in rollup-ul P34 -> se ADAUGA inapoi la baza). Ajustarea fiscal-contabil (art.28 alin.1:
recuperarea costului MF prin deducerea amortizarii fiscale) e implementata corect. Golden cu temei:
test_amortizare_ajustare_fiscala_art28 (venituri 100000, cheltuieli 60000 incl. 10000 amort contabila, amort
fiscala 12000 -> impozabil 38000, impozit 6080). Pragul MF amortizabil: PLAFON_MF_2026=5000 lei
(mijloace_fixe_import_api.py) = CF art.28 alin.(2) lit.b (5.000 lei, actualizat OUG 8/2026) - test_mf_prag_
amortizabil_5000_art28.

**DATORIE (subsistem MF, NU d101): metode degresiva/accelerata necalculate.** Modulul MF calculeaza DOAR liniara
(rata = amortizabil/dnf); metoda activului (degresiva/accelerata, CF art.28 alin.5) e mapata dar ignorata in
calcul. Impact limitat: d101 ia amortizarea fiscala ca input (contabilul o calculeaza extern), deci d101 nu e
gresit; gapul e pe amortizarea contabila/SAF-T (D406) pt active cu metoda ne-liniara. xfail strict
test_datorie_mf_metode_amortizare. SOLD DATORII 20 -> 21. Apartine unui cluster MF/D406 viitor, NU clusterului
amortizare|d101 (care e despre tratamentul in d101, aliniat).

INCHIDERE CLUSTER: "amortizare | d101" √ 03.08 (tratamentul amortizarii in d101 aliniat la art.28: deducere
fiscala P11 + addback contabil P28 + prag 5000). Secventa 59 -> 58.


## 03.08.2026 — Cluster baze contributii (CAS/CASS/imp/CAM) | d112: ALINIAT (cotele rutate period-aware)

Clusterul urmator din lant dupa amortizare|d101. Sesiunea A = aliniere cod existent la lege. VERDICT: cotele
salariale erau CORECTE ca valoare, dar HARDCODATE ca literale in d112.py (0.25 / 0.10 / 0.0225) - contrazice
principiul COTE (sursa unica period-aware prin cota(nume, la_data), ca la GARZI cat.3). Rutate acum prin cota().

TEMEIURI verificate VERBATIM la sursa (anaf_surse/cod_fiscal_227_2015_consolidat.html):
- **CAS 25%** - CF art.138 lit.a: "Cotele de contributii de asigurari sociale sunt urmatoarele: a) 25% datorata
  de catre persoanele fizice care au calitatea de angajati...".
- **CASS 10%** - CF art.156: "Cota de contributie de asigurari sociale de sanatate este de 10%".
- **impozit pe venit 10%** - CF art.78 alin.(2): aplicarea "cotei de 10% asupra bazei de calcul".
- **CAM 2,25%** - CF art.220^3 alin.(1): "Cota contributiei asiguratorii pentru munca este de 2,25%".
Toate 4 exista deja in COTE (core/common.py: cas / cass / impozit_venit / cam) cu temei, aliniate la aceste valori.

RUTARE (core/d112.py): in `_d112_genereaza` cotele se citesc o data dupa `ref` (data lunii) - `_cota_cas/_cass/
_imp/_cam = float(cota("...", ref)[0])` - si inlocuiesc literalele la CAS (bazac*_cota_cas), CASS (bazac*_cota_cass),
impozit (bimp*_cota_imp), CAM (sum_bazac*_cota_cam). In `pull`, pragurile minime part-time (cas_min_pt/cass_min_pt)
rutate prin `_cm.cota("cas"/"cass", ref)`. VALUE-PRESERVING: cota() intoarce exact vechile literale la orice data
din 2025-2026 -> golden D112 + proba DUK NESCHIMBATE (suita verde, 1267 passed). GARD anti-hardcode: teste care
inspecteaza sursa functiilor si pica daca literalul 0.25/0.10/0.0225 reapare (test_d112_ruteaza_cotele_prin_cote_
nu_literale) + test de valoare cu temei (test_cotele_contributii_din_cote_cu_temei).

Beneficiu period-aware: daca o cota se schimba pe viitor (ex. OUG), se modifica intr-un singur loc (COTE) cu
fereastra de data, si d112 o preia automat - nu mai exista literal ascuns care sa ramana in urma legii.

INCHIDERE CLUSTER: "baze contributii (CAS/CASS/imp/CAM) | d112" √ 03.08 (aliniere Sesiunea A, fara datorie,
fara xfail nou). Secventa 58 -> 57.


## 03.08.2026 — Cluster rotunjire aritmetica (A91b) | d112: VERIFICAT + REPARATIE (minim part-time rotunjea bancar)

Clusterul urmator din lant dupa baze contributii|d112. Sesiunea A = aliniere cod la lege. Temei: ANAF structura
D112 0126_030226 "Contributiile se rotunjesc aritmetic"; validator DUK regula A91b (CAM calculat 112, cerut 113).
`round()` din Python e BANCARA (half-to-even), nu aritmetica.

VERIFICAT CORECT: contributiile principale (CAS/CASS/impozit/CAM, media CM d17) trec prin `_d112int` =
numar_fiscal(...).quantize(ROUND_HALF_UP) = aritmetic. Acoperit de test_rotunjire_aritmetica_nu_bancara (112.5->113),
test_toate_generatoarele_rotunjesc_aritmetic (gard cross-generator pe int(round(...))), test_d112_pastreaza_
rotunjirea_aritmetica.

REPARATIE (proba pe date reale, NU pe suspiciune): minimul PART-TIME (art.146(5^6)/168(6^1) CF - supra-taxare sub
salariul minim) calcula `prag_zile`, `cas_min_pt`, `cass_min_pt` cu `round()` BANCAR. `_d112int` aplicat ulterior
(liniile b4_5p/6p/8p) era NO-OP: valoarea era deja intreaga din round(), deci rotunjirea BANCARA ajungea neatinsa
in campurile B4_5P/B4_6P/B4_8P DECLARATE. Divergenta dovedita pe prag real: prag_zile=1226 -> CAS = 1226x0.25 =
306.5 -> bancar 306 (par), ANAF cere 307; prag_zile=1225 -> CASS = 122.5 -> bancar 122, cerut 123. FIX: cele trei
sume trec acum prin `_d112int` (half-up) direct, ca restul D112. Value-changing DOAR la granita .5 (rar dar real);
golden D112 + DUK neschimbate (nu ating .5). Proba: test_partime_minim_rotunjeste_aritmetic_nu_bancar (306->307,
122->123) + gard pe sursa test_partime_minim_foloseste_d112int_nu_round_bancar.

INCHIDERE CLUSTER: "rotunjire aritmetica (A91b) | d112" √ 03.08 (contributii aritmetice verificate + reparatie
minim part-time). Fara xfail nou (reparat, nu amanat). Secventa 57 -> 56.


## 03.08.2026 — Cluster sect_II tip_venit (impozit retinut) | d205: VERIFICAT + REPARATIE (impozit dividende period-aware)

Clusterul urmator din lant dupa rotunjire A91b|d112. Sesiunea A. Sursa: anaf_surse/d205_struct_anaf.txt, acum
IDENTIFICATA ca OPANAF 102/2025 (comentariile "VERSIUNE NECUNOSCUTA" din d205.py inlocuite cu OPANAF 102/2025).

VERIFICAT CORECT (structura sect_II + tip_venit): tip_venit="08" = "1.a) venituri din dividende", tip_plata=2, cu
divid_D/divid_P + baza1/imp1 (la 08, spre deosebire de 25/29 unde baza1/imp1 sunt interzise - R44/R45). sect_II se
inchide inainte de <benef> (elemente FRATI). totalPlata_A = nrben+Tcastig+Tpierd+T_VB+T_GAR+Tbaza+Timp (nu doar
Timp). Toate confirmate la sursa (d205_struct_anaf.txt). Acoperit de test_dividende_valid,
test_totalPlata_A_e_suma_tuturor_campurilor_sect_II + proba DUK valida.

REPARATIE (proba pe date reale, NU pe suspiciune): impozitul retinut pe dividende in calea AUTO era HARDCODAT
10% (`Decimal("10")/Decimal(100)`), gresit pentru 2026. CF art.97 (verbatim, /tmp/cf.txt): "impozitul pe dividende
se stabileste prin aplicarea unei cote de impozit de 16% asupra dividendului brut" de la 01.01.2026 (Legea 141/2025,
MO 699/25.07.2025). COTE avea deja `impozit_dividend` = 16% (2026) / 10% (2024). FIX: rata rutata prin
cota("impozit_dividend", date(perioada.an, 12, 31)) - period-aware. Proba DB REALA (test_d205_contract_pull_
genereaza_perioada): 50000 dividende platite in 2026 -> impozit 8000 (16%), nu 5000 (10%); total_plata_a=8000.
Testul incapsula valoarea GRESITA (5000) - aliniat la lege cu temei. Proba pana la declaratie: test_d205_contract_
proba_duk_valid (D205 cu 16% trece DUKIntegrator). Gard anti-hardcode: test_d205_rata_dividend_din_cota_nu_hardcodat.

Impact: fara fix, o firma care distribuie dividende in 2026 ar declara in D205 impozit retinut la 10% in loc de
16% - sub-declarare directa a impozitului retinut la sursa.

INCHIDERE CLUSTER: "sect_II tip_venit (impozit retinut) | d205" √ 03.08 (structura verificata OPANAF 102/2025 +
reparatie rata dividende period-aware). Fara xfail nou. Secventa 56 -> 55.


## 03.08.2026 — Cluster rotunjire | d205: VERIFICAT (aritmetic, deja corect) + gardat

Clusterul urmator din lant dupa sect_II tip_venit|d205. Sesiunea A. Temei: aceeasi regula ANAF ca la D112 -
sumele fiscale se rotunjesc ARITMETIC (half-up), nu bancar (validator A91b: "Contributiile se rotunjesc aritmetic").

VERIFICAT CORECT: toate sumele D205 (baza1, imp1, castig1, pierdere1, total_div, parte, impozit) trec prin `_i` =
`int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))` = aritmetic. NU exista niciun `round()` bancar
in d205.py. Corect prin constructie.

GAP DE ACOPERIRE (inchis, fara schimbare de comportament): `_i` din d205 NU era in gardul de identitate
cross-generator (test_rotunjirea_e_identica_intre_generatoare acoperea doar d390/d300/d112) si nu avea proba
d205-specifica. Adaugat: `_i` in gardul de identitate (a==b==c==d pe 112.5/0.5/2.5/...) + test_d205_rotunjeste_
aritmetic_nu_bancar (_i(2.5)=3, _i(0.5)=1 - aritmetic, bancarul ar da 2/0). Daca cineva schimba _i pe bancar, pica.

INCHIDERE CLUSTER: "rotunjire | d205" √ 03.08 (rotunjire aritmetica verificata + gardata). Fara xfail nou, fara
schimbare de valoare. Secventa 55 -> 54.


## 03.08.2026 — Cluster cote TVA -> randuri | d300: VERIFICAT (livrari) + REPARATIE MARE (achizitii deductibile 11%/9%)

Clusterul urmator din lant dupa rotunjire|d205. Sesiunea A. Sursa: anaf_surse/d300_struct_anaf.txt
(structura_D300_v12.0.0_10022026), maparea confirmata prin MARJA validatorului DUK (arbitrul: un swap cota<->rand
pica marja) + proba DUK reala.

VERIFICAT CORECT - LIVRARI (colectata): 21% -> Rd.9 (R9, marja 20-22%), 11% -> Rd.10 (R10, marja 10-12%),
9% art.III Legea 141/2025 -> Rd.11 (R11, marja 8-10%). Toate acceptate de DUK.

REPARATIE (proba pana la declaratie - DUK respingea vechea mapare) - ACHIZITII DEDUCTIBILE:
- **11% era pus la R74** (`_ACHIZ_RAND`/setr). R74 = Rd.24.1 = cota **19%** (legacy), marja 18-20% (regula
  R84.1) - DUK respingea ("R74 nu se incadreaza in 19%"). CORECT: 11% -> **R23** (Rd.25, marja 10-12%). Reparat,
  DUK valid.
- **9% era pus la R76**. R76 = Rd.27.4 = **taxare inversa** (legat de R72 prin R96.2/R96.3: R72_1==R76_1); nu e
  achizitie deductibila normala. In plus R76 NU e in formula totalului R27 -> 9% deductibil se PIERDEA din totalul
  taxei deductibile (TVA de plata supraevaluata) SI declaratia era respinsa de DUK. Structura v12 pune 9% deductibil
  la Rd.25.1 (R75), dar validatorul DUK INSTALAT respinge si R75 ("nu trebuie sa exista aici") - discrepanta intre
  documentul v12 si validatorul instalat. SOLUTIE onesta: 9% deductibil scos din auto (nu emitem un atribut care
  invalideaza declaratia) + AVERTISMENT explicit de declarare manuala (altfel TVA de plata supraevaluata).

PROBA: test_cote_tva_maparea_pe_randuri_d300 (R9/R10/R11 + R22/R23, gard 11% NU la R74) + test_cote_tva_d300_
proba_duk_valid (D300 21/11/9 livrari + 21/11 achizitii trece DUKIntegrator - vechea mapare pica) + test_9pct_
deductibil_nu_emite_rand_invalid_si_avertizeaza. `_ACHIZ_RAND` corectat la {21:R22, 11:R23}.

DATORIE DESCHISA (xfail test_datorie_d300_9pct_deductibil_auto, SOLD +1): declararea automata a 9% deductibil pe
un rand acceptat de validatorul instalat. Se inchide cand validatorul DUK instalat accepta randul deductibil 9%
(sau se identifica randul corect la sursa) si 9% trece pe auto cu proba DUK.

INCHIDERE CLUSTER: "cote TVA -> randuri | d300" √ 03.08 (livrari verificate + reparatie achizitii deductibile
11%/9%). Secventa 54 -> 53.


## 03.08.2026 — Cluster exigibilitate / TVA la incasare | d300: GAP VERIFICAT (feature, decizie de produs) — NEINCHIS

Clusterul urmator dupa cote TVA->randuri|d300. La verificare (Sesiunea A) am gasit un GAP de fond, nu o aliniere:
**D300 ignora complet regimul TVA la incasare** (CF art.282, sistemul TVA la incasare).

CONSTATARE (verificata in cod): `d300.pull` selecteaza facturile cu `WHERE f.data_emitere >= inceput AND < sfarsit`
si SELECT-ul de profil nu citeste `tva_la_incasare`. Deci D300 declara TVA pe toate facturile EMISE in perioada,
indiferent de incasare. Pentru o firma in sistemul TVA la incasare, art.282 cere: exigibilitatea TVA colectate la
data INCASARII (cap 90 zile de la emitere), iar TVA deductibila la data PLATII achizitiei. => exigibilitate gresita
pentru aceste firme (declara prea devreme colectata, prea devreme/tarziu deductibila).

FEZABILITATE: datele exista in schema — `firma_profil.tva_la_incasare` (bool) + `facturi.platita_la` (timestamp) +
`data_scadenta`. Deci se poate implementa fara plumbing nou major.

DE CE NEINCHIS: e o FUNCTIONALITATE care schimba substantial sumele declarate (nu o corectie de rotunjire/mapare),
cu reguli de temei de verificat verbatim la sursa (art.282 alin.3-6, capul de 90 zile, tratamentul deductibilei).
Per §2.3 pct.2 = decizie de produs (domeniu: doar firmele pe regim; abordare: filtrare la pull dupa platita_la vs.
rand de exigibilitate). Nu se face pe jumatate la finalul unei rulari. Datorie deschisa: xfail
test_datorie_d300_exigibilitate_tva_la_incasare (SOLD +1). Clusterul RAMANE in secventa (nebifat) pentru o campanie
dedicata, cu greenlight Costin pe temei + domeniu.

Oprire rulare: limita de 6 clustere/rulare atinsa (§2.3 pct.5) + acest gap cere decizie de produs. Predare pe disc
(PREDARE_LANT.md).


## 03.08.2026 — Cluster exigibilitate / TVA la incasare | d300: IMPLEMENTAT (feature, greenlight Costin)

Lant nou, cluster #6, cu decizie de produs Costin: ambele laturi (colectata+deductibila), proportional pe plati
partiale. Temei verificat VERBATIM la sursa (/tmp/cf.txt, cod_fiscal_227_2015_consolidat):
- **art.282 alin.(3)** (modificat de OUG 8/2026, in vigoare 01.03.2026): pentru firmele care aplica sistemul TVA
  la incasare, exigibilitatea TVA COLECTATE intervine la data INCASARII contravalorii integrale sau PARTIALE.
  Plafon 5.000.000 lei (2026) / 5.500.000 (2027). **NB: OUG 8/2026 a ELIMINAT capul de 90 de zile** din vechea
  reglementare - textul actual e pur pe incasare, fara termen limita. (Datoria initiala presupunea gresit un cap
  de 90 zile - corectat la verificarea sursei; nu s-a implementat cap.)
- **art.282 alin.(8)**: fiecare incasare include TVA (suta marita): TVA = suma x cota/(100+cota).
- **art.297 alin.(2)-(3)**: dreptul de deducere a TVA se AMANA pana la PLATA furnizorului (pentru firma pe sistem,
  respectiv pentru cumparaturi de la un furnizor pe sistem). Exceptii: achizitii intracom, importuri, taxare
  inversa (art.307/331) - regim general.
- **art.282 alin.(6)**: operatiunile sub reguli generale (taxare inversa etc.) NU intra in sistem.

IMPLEMENTARE (core/d300.py):
- `calcul_d300`: pentru `prof.tva_la_incasare`, exigibilitatea se calculeaza din `decontari=[{suma,cota}]` prin
  suta marita (`tva_incasare.tva_din_incasare`), proportional cu suma decontata; altfel comportament neschimbat
  (exigibilitate la faptul generator/emitere).
- `pull` + `_pull_incasare`: pentru firma pe sistem, se citesc DECONTARILE (incasari cont 4111 pt emise / plati
  cont 401 pt primite) din notele contabile VALIDATE cu `factura_id`, cu `i.data` in perioada - NU emiterea si NU
  `platita_la` (care prinde doar platile online). Suma decontata pe factura se aloca pe cotele facturii proportional
  (`_aloca_pe_cote`) - corecteaza limita multi-cota a postarilor din reconciliere (care foloseau prima cota).
- Excludere taxare inversa (`AND COALESCE(f.taxare_inversa,false)=false`) - art.282(6)/297(3).

PROBA: pe date reale (DB) - factura emisa in luna 5 dar INCASATA luna 6 e exigibila in luna 6, nu 5; latura
colectata (R9 21%) + deductibila (R23 11%); taxare inversa exclusa (gard F3); proportional pe incasare partiala
(test_tva_la_incasare_partial_proportional); PROBA DUK valida (test_tva_incasare_d300_proba_duk_valid).

LIMITE CUNOSCUTE (documentate, in afara scopului acestui cluster): (a) cazul art.297(2) - firma NEpe-sistem care
cumpara de la un furnizor pe sistem isi amana deducerea - nu se poate trata in D300 fara statusul furnizorului
(nu-l avem); ramane pe seama contabilului via manual. (b) verificarea plafonului/eligibilitatii (art.282 alin.3^1/4)
nu se face in D300 - se bazeaza pe flagul `tva_la_incasare` setat la inregistrare.

Marker inchidere datorie: **d300 aplica exigibilitatea tva la incasare pentru firme pe regim**. xfail
test_datorie_d300_exigibilitate_tva_la_incasare ELIMINAT. SOLD DATORII 23 -> 22.

INCHIDERE CLUSTER: "exigibilitate / TVA la incasare | d300" √ 03.08. Secventa 53 -> 52.


## 03.08.2026 — Cluster taxare inversa | d300: REPARAT (rd.12 nu se declara) + GRI reverse charge INCHIS

Lant #2. Sesiunea A. Temei reconfirmat VERBATIM la SURSA PRIMARA:
- **CF art.331 alin.(1)** (/tmp/cf.txt): "in cazul operatiunilor taxabile, persoana obligata la plata taxei este
  BENEFICIARUL" pentru operatiunile de la alin.(2) (deseuri, masa lemnoasa, cereale, constructii, aur, telefoane
  etc.); conditia: furnizor SI beneficiar inregistrati TVA (art.316). => auto-taxare: beneficiarul declara.
- **Structura D300 (anaf_surse/d300_struct_anaf.txt), Rd.12**: "Achizitii... pentru care beneficiarul este obligat
  la plata TVA (taxare inversa)", cu sub-randuri 12.1/12.2/12.3 pe cote 21/11/9 (ERR: R12_1 >= R12_1_1+R12_2_1+
  R12_3_1). Declarata MANUAL (contabilul), nu derivata din facturi - design consemnat in docstring-ul d300.py.

REPARATIE (bug real, proba pe date reale): mecanismul manual pt rd.12 era RUPT. Allow-list-ul din calcul_d300 pt
randurile colectate NU includea prefixul `R12_` -> orice cheie manual R12_* (R12_1, R12_2, sub-randuri) era
SILENTIOS ignorata (dovada: calcul_d300 cu manual R12_1=1000 -> R12_1 None). Contabilul care introducea taxarea
inversa in rd.12 o avea aruncata -> auto-taxarea colectata NEDECLARATA (sub-declarare TVA). FIX: adaugat `R12_` in
allow-list. Latura deductibila (rd.27/R25) era deja settabila. PROBA: decont echilibrat rd.12=rd.27 (R25_x==R12_x,
regulile validator V_19/V_21) trece DUKIntegrator (test_taxare_inversa_d300_proba_duk_valid) + gard anti-drop
(test_taxare_inversa_r12_fara_fix_ar_fi_dropped) + R12 intra in R17 colectata.

GRI INCHIS (reverse charge divergenta D300/D394 = cerinta ANAF, nu bug): verdictul statea pe deductie din cod, nu
pe text oficial. Reconfirmat acum la SURSA OFICIALA ambele laturi: (a) D300 - CF art.331 + structura Rd.12 (manual);
(b) D394 - structura d394_struct_anaf.txt campurile 64 `bun` (Nomenclator N1, obligatoriu pt taxare inversa) +
68-70 nrLivV/bazaLivV/tvaLivV "defalcate pe tip bun pt taxare inversa" cu reguli ERR. Deci reverse-charge se declara
in D300 manual (rd.12) SI in D394 defalcat pe tipul bunului - cerinte structurale ANAF, nu optiuni de implementare;
divergenta e reala si ceruta. **d300 reverse charge doar manual reconfirmat la sursa oficiala.** xfail
test_datorie_d300_reverse_charge_manual_reconfirmat_mo ELIMINAT. SOLD DATORII 22 -> 21.

INCHIDERE CLUSTER: "taxare inversa | d300" √ 03.08 (rd.12 reparat + reverse charge reconfirmat la sursa + DUK).
Secventa 52 -> 51.


## 03.08.2026 — Cluster pro-rata deducere | d300: VERIFICAT (corect) + gap de acoperire inchis

Lant #2. Sesiunea A. Temei la sursa: CF art.300 (Deducerea taxei pentru persoana impozabila cu REGIM MIXT -
deducere pe baza de pro rata cand nu poate tine evidente separate). Structura D300 v12: field 19 `pro_rata` in
[0,100]; R31_2 = Rd.33 = "Ajustari conform pro-rata".

VERIFICAT CORECT: d300 aplica pro-rata ca AJUSTARE (R31_2), nu ca scalare directa a deductibilei (modulul vechi o
scala direct - gresit). R28_2 (subtotal dedusa) ramane integral; R31_2 = -(R28_2 x (100-pro_rata)/100) scade
fractia nedeductibila; R32_2 (total dedusa) = R28+R29+R30+R31 = R28 x pro_rata/100. La pro_rata=100 (uzual)
ajustarea e 0. Proba: pro_rata=80%, achizitie 210 TVA -> R28=210, R31=-42, R32=168 (=210x80%); DUK valid.

GAP DE ACOPERIRE inchis (fara schimbare de comportament): nu exista test cu pro_rata<100 - ajustarea R31 era
neprobata. Adaugat test_pro_rata_ajustare_deductibila_art300 (valori + temei) + test_pro_rata_100_fara_ajustare
(gard) + test_pro_rata_d300_proba_duk_valid.

INCHIDERE CLUSTER: "pro-rata deducere | d300" √ 03.08. Fara datorie, fara schimbare de valoare. Secventa 51 -> 50.


## 03.08.2026 — Cluster rotunjire aritmetica | d300: VERIFICAT (aritmetic) + proba d300-specifica

Lant #2. Sesiunea A. Regula A91b (ANAF: sumele fiscale se rotunjesc aritmetic/half-up, nu bancar). D300 folosea
deja `_int = numar_fiscal(...).quantize(ROUND_HALF_UP)` pe toate sumele si era DEJA in gardul de identitate
cross-generator (test_rotunjirea_e_identica_intre_generatoare: a==b==c==d cu d390/d112/d205). Adaugat proba
d300-specifica test_d300_rotunjeste_aritmetic_nu_bancar (_int(2.5)=3, _int(0.5)=1 - bancarul ar da 2/0). Fara
schimbare de comportament - inchidere gap de acoperire.

INCHIDERE CLUSTER: "rotunjire aritmetica | d300" √ 03.08. Secventa 50 -> 49.


## 03.08.2026 — Cluster ajustari | d300: REPARAT (ajustari/regularizari aruncate din allow-list)

Lant #2. Sesiunea A. Temei: CF art.304 (regularizarea taxei) + art.305 (ajustarea taxei deductibile pt bunuri de
capital). Structura D300: R29=Rd.31 "TVA efectiv restituita cumparatorilor straini", R30=Rd.32 "Regularizari taxa
dedusa", R35=sold reportat neachitat, R36=Rd.38 "Diferente de TVA de plata" (inspectie).

REPARATIE (bug real, aceeasi clasa ca R12 taxare inversa): allow-list-ul manual pt randurile deductibile NU
includea R29_/R30_ (feed R32 total dedusa) si nici R35_/R36_ (feed R37 TVA cumulat) -> orice ajustare/regularizare
introdusa de contabil era SILENTIOS aruncata (dovada: calcul_d300 cu manual R30_2=200 -> R30_2 None). Rezultat:
regularizarile de taxa dedusa, restituirile catre cumparatori straini, soldul reportat si diferentele de inspectie
NU se puteau declara in D300. FIX: adaugate R29_/R30_/R35_/R36_ in allow-list. Randurile COMPUTATE (R32/R33/R34/R37
= totaluri/rezultat) raman corect neschimbate de manual. PROBA: R30 regularizare 50 -> R32 dedusa 210->260/281;
R36 inspectie 100 -> R37 cumulat = R34 + 100; DUK valid (test_ajustari_d300_proba_duk_valid) + gard anti-drop.

INCHIDERE CLUSTER: "ajustari | d300" √ 03.08. Fara datorie. Secventa 49 -> 48.


## 03.08.2026 — Cluster tipuri operatiune 1-5 | d301: VERIFICAT (mapare corecta) + gap de acoperire inchis

Lant #2, cluster #6 (limita rularii). Sesiunea A. D301 = decont special de TVA. Temei: OPANAF 592/2016. Maparea
tip->sectiune verificata la sursa (anaf_surse/d301_struct_anaf.txt): tip 1 = Sectiunea 1 (achizitii intracom de
bunuri, altele decat mijloace transport noi/accize); tip 2 = Sectiunea 2 (mijloace de transport noi, seteaza bifa
mij_transp); tip 3 = Sectiunea 3 (produse accizabile); tip 4 = Sectiunea 4 (servicii, total); tip 5 = Sectiunea
4.1 (servicii intracom art.150 pt care beneficiarul e obligat la plata TVA) - SUBSET al S4 (se preia si in S4).

VERIFICAT CORECT: rollup-ul S4.1->S4 (partea subtila, impusa de DUK) era deja testat (test_tip5_se_preia_in_
sectiunea_4 etc.). Gap de acoperire inchis (fara schimbare de comportament): tipurile 1/2/3 nu aveau gard
individual. Adaugat test_tipuri_1_2_3_pe_sectiuni_proprii (fiecare pe sectiunea proprie, tip 2 -> mij_transp, si
NU se preiau in S4) + test_toate_tipurile_1_5_proba_duk_valid (decont cu toate cele 5 tipuri trece DUKIntegrator -
confirma maparea end-to-end).

INCHIDERE CLUSTER: "tipuri operatiune 1-5 | d301" √ 03.08. Fara datorie. Secventa 48 -> 47.


## 03.08.2026 — Cluster rollup S4.1->S4 | d301: VERIFICAT COMPLET (deja acoperit)

Lant #2, cluster #6 final. Sesiunea A. Temei: OPANAF 592/2016, instructiunile formularului 301: "In sectiunea 4.1
se preiau DIN sectiunea 4 achizitiile de servicii intracomunitare pentru care beneficiarul e obligat la plata TVA
cf. art.307 alin.(2)". Deci S4.1 (tip 5) e SUBSET al S4 - fiecare operatiune tip 5 se preia SI in totalul S4.

VERIFICAT CORECT (deja acoperit integral de test_d301_rollup.py - fisier dedicat acestei regresii): S4 contine
S4.1 (test_tip5_se_preia_in_sectiunea_4); S4 = S4.2 (tip 4) + S4.1 (tip 5) (test_tip5_plus_tip4_cumuleaza); TVA
DATORAT nu se dubleaza - serviciul o singura data prin rollup, iar totalPlata_A e CHECKSUM (baza1..5+tva1..5) care
include 4.1 prin definitie, impus de DUK (test_tva_datorat_o_singura_data_desi_checksum_include_4_1); fara tip 5 nu
se inventeaza rollup (test_fara_tip5_sectiunea_4_ramane_pe_tip4). Proba DUK end-to-end cu toate cele 5 tipuri
(test_toate_tipurile_1_5_proba_duk_valid) - validatorul IMPUNE rollup-ul (respinge "4.1 fara 4").

INCHIDERE CLUSTER: "rollup S4.1->S4 | d301" √ 03.08. Fara datorie, fara cod nou (acoperire preexistenta +
proba DUK adaugata la clusterul tipuri). Secventa 47 -> 46.


## 03.08.2026 — GARD PE CLASA: allow-list manual incompleta -> eroare vizibila, nu drop tacit (cerut de Costin)

La clusterele 1 (taxare inversa, R12) si 4 (ajustari, R29/R30/R35/R36) din lantul #2 s-au reparat doar
INSTANTELE, nu clasa. Costin (03.08): un rand introdus de contabil care nu e in lista trebuie sa produca eroare
VIZIBILA, nu sa dispara. Corectat acum pe clasa.

RADACINA: generatoarele cu 'manual' filtrau cheile printr-un allow-list prefix (startswith) si ARUNCAU TACUT ce nu
se potrivea. `_bad` prindea doar cheile ne-R; o cheie R care nu era in lista disparea fara urma. Asa s-au strecurat
R12, apoi R29/R30/R35/R36, si (descoperit acum, tot aruncate tacit) R38/R39 (sold negativ reportat / diferente
negative inspectie, feed R40) + R43/R44 (ajustari deductibila in rollup-ul R27).

INVENTAR (cate randuri accepta fiecare generator vs. mecanismul de esec):
- **d300**: allow-list R-key pe prefixe. Colectata 15 prefixe (R1-R8, R12-R16, R64, R65), deductibila/rezultat 18
  prefixe (R18-R21, R23, R25-R26, R29-R30, R35-R36, R38-R39, R43-R44, R72-R73, R75). Structura oficiala = 119
  campuri R distincte (multe COMPUTATE: R17/R27/R28/R32/R33/R34/R37/R40/R41/R42 - nu se seteaza manual). Inainte:
  R-key neacoperit = drop tacit. ACUM: gard aplicate-sau-eroare (orice cheie manual neaplicata -> ValueError).
- **d301**: `if manual: raise` - respinge TOT manual explicit. Sigur (0 acceptate, eroare vizibila).
- **d112**, **d406**: fara parametru 'manual'. Nu exista mecanismul.
- **d390**: manual = lista de operatiuni; `if tip not in TIPURI: continue` -> skip TACIT. ACUM: raise.
- **d394**: manual = lista de operatiuni; cota gresita deja AVERTIZA (factura ignorata), dar tip gresit era skip
  TACIT (`continue`). ACUM: raise.

FIX: (a) d300 - allow-list completat cu R38/R39/R43/R44 + GARD CLASA: se urmareste multimea cheilor chiar aplicate;
orice cheie manual neaplicata -> ValueError explicit (typo sau rand computat). Self-maintaining: urmatoarea
allow-list incompleta STRIGA la prima folosire, nu inghite. (b) d390/d394 - tip necunoscut -> ValueError, nu
continue. GARDURI: test_d300_manual_rand_necunoscut_ridica_nu_dispare, test_d390_manual_tip_necunoscut_ridica_nu_
dispare, test_d394_manual_tip_necunoscut_ridica_nu_dispare (R99/tip ZZZ -> eroare vizibila).

Efect pe produs: un contabil care tasteaza gresit un rand/tip in D300/D390/D394 primeste eroare clara, nu o
declaratie tacit incompleta (sub-declarare invizibila). CLAUDE.md §2.3 pct.7 (RAPORTUL IN LANT) adaugat: sectiunea
9 (garduri) e obligatorie la inchidere - un cluster fara gard nu se declara inchis.

## 03.08.2026 — Cluster "baza = val x curs" (D301) INCHIS. Temei CF art.290 alin.(2).

Verificare formula bazei D301: baza = round(val_valuta x curs, 0). Formula si rotunjirea (ROUND_HALF_UP
la leu intreg, ca structura ANAF cu baza integer) = CORECTE fata de art.290 alin.(2). Cursul e alegerea
contabilului (§8) — codul il primeste ca input, corect.

NECONFORMITATE gasita si reparata (clasa "valoare gresita tacuta", frate cu drop-ul tacit din D300/D390/D394):
generatorul (d301.py) si reader-ul grilei (d301_operatiuni_api.lista) faceau . Un
curs absent/0 pe o operatiune in EUR (moneda default) devenea TACIT curs=1 -> baza = valoarea in valuta,
subevaluata, trimisa la ANAF fara eroare. In plus schema avea "curs numeric DEFAULT 1" (fabricare la nivel DB).

FIX (gard pe clasa): (a) calc_baza ridica ValueError pe curs None/<=0 — chokepoint prin care trec toate cele 3
call-uri (generator, lista, adauga via _tva_din). (b) scos "or 1"/"or 0" din generator si reader. (c) scos
DEFAULT 1 de pe coloana curs in tenant_template (tenant nou = fail-loud). Poarta de intrare adauga() valida deja
curs>0 — neatinsa.

GENERALIZARE: d301 e SINGURUL generator cu valuta/curs (grep: d100/d101/d112/d300/d390/d394/d406 fara
val_valuta/curs de schimb). Clasa complet acoperita.

MIGRARE (nefacuta, decizie deployment §2.3 pct.3): tenantii EXISTENTI pastreaza "curs numeric DEFAULT 1" pana la
un ALTER COLUMN ... DROP DEFAULT la deploy. Pe ei, un insert care ocoleste adauga() si omite cursul inca ar primi
1 din DB (calc_baza nu poate distinge de RON=1). Consemnat.


## 03.08.2026 — Cluster "cota TVA" (D301) INCHIS. Temei CF art.291 + Legea 141/2025.

Cota STANDARD in D301 = period-aware corect (common.cota tva_standard: 21% de la 01.08.2025, 19% inainte).
NECONFORMITATE reparata: cota REDUSA era literal 11 in cote_perioada, indiferent de perioada. Pt o luna D301
< 01.08.2025 (rectificativa) oferea "11% redusa" gresit - atunci reducerile erau 9%/5% (Legea 141/2025 le-a
comasat in 11% de la 01.08.2025; art.291 alin.2 rescris, alin.3 abrogat). art.291 alin.(8) confirma ca redusa
se aplica in D301 (cota achizitiei intracom = cota livrarii interne a aceluiasi bun). Harm: adauga persista un
tva eronat (fals-verde) - dovedit: adauga(2025-06, cota=11) -> tva=55 stocat inainte de fix.

FIX: cota redusa din common.cota("tva_redusa", data); cand neconfigurata pt perioada (PerioadaIndisponibila) ->
optiunea se OMITE (nu 11% fals). adauga valideaza cota contra listei cote_perioada, deci un 11% pe luna veche e
respins la sursa. 2026 neschimbat [21,11,0]; 2025-06 -> [19,0].

DECIZIE DE PRODUS CERUTA (§2.3 pct.2, NEREZOLVATA): pentru a permite corect cota redusa pe perioade < 01.08.2025,
COTE trebuie sa reprezinte DOUA cote reduse coexistente (9% SI 5%) - modelul actual (o cheie = serie temporala cu
o valoare la un moment) nu le tine simultan. Optiuni: doua chei (tva_redusa_9 / tva_redusa_5) sau valoare-lista.
Schimba CE optiuni vede contabilul -> decizia lui Costin. Pana atunci: pre-08.2025 fara redusa (omitere fail-loud).


## 03.08.2026 — Cluster "tipuri operatiune IC (L/A/P/S)" (D390) INCHIS prin VERIFICARE. Temei OPANAF 705/2020.

Maparea tip operatiune -> simbol D390 CORECTA si COMPLETA. TIPURI=(L,T,A,P,S,R) (d390.py:50) = exact nomenclatorul
oficial (anaf_surse/d390_struct_anaf.txt, OPANAF 705/2020 v3): L livrari IC bunuri, T triunghiulare, A achizitii IC
bunuri, P prestari IC servicii, S achizitii IC servicii, R livrari regim special agricultori. Regula codO obligatoriu
L/T/P/R (d390.py:206), formula totalPlata_A (:177), gard anti-drop manual (:159 raise) - toate conforme/prezente.
FARA fix necesar. Adaugat gard-pin: TIPURI == lista oficiala (drift de sursa -> rosu; mutant probat in-process).

Observatii tangentiale (NEreparate, in afara acestui cluster):
- Reclasificare (d390.py:151-152): tip invalid din tabela d390_reclasificare -> fallback tacit la L/A default (NU
  drop - operatiunea ramane declarata si numarata; misclasificare posibila, nu disparitie). Acoperit de
  test_reclasificare_ignora_tip_invalid; valorile vin din dropdown UI. Risc practic mic; de decis daca se
  uniformizeaza cu calea manuala (raise pe tip invalid).
- Nomenclator tari (d390.py:45): include XI (Irlanda de Nord, VIES post-Brexit) care NU apare in Nomenclator Tari
  2020 (listeaza doar GB). Tine de clusterul "nomenclator tari (HR->CR) | d390" (inca deschis in agenda), nu de acesta.


## 03.08.2026 — DECIZIE PRODUS REZOLVATA: cote reduse TVA istorice 9%/5% (urmare cluster "cota TVA").

Costin a decis: DOUA CHEI SEPARATE tva_redusa_9 si tva_redusa_5, fiecare cu temeiul ei la sursa (articolele care
definesc ce operatiuni intra in fiecare cota). IMPLEMENTAT in COTE (common.py):
- tva_redusa_9 = 0.09, CF art.291 alin.(2) lit.a-n (medicamente, alimente, apa/canalizare, irigatii, ingrasaminte/
  pesticide, carti/manuale/ziare, acces cultural, lemn de foc, energie termica, locuinte sociale, cazare, restaurant/catering).
- tva_redusa_5 = 0.05, CF art.291 alin.(3) (locuinte sociale sub 600.000 lei lit.c pct.3, carti, acces evenimente culturale/sportive).
- Ambele comasate in 11% de la 01.08.2025 (intrare terminala 0.11: Legea 141/2025 pct.42 pt 9%, pct.43 abroga 5%).
  Intrarea terminala impiedica cota() sa intoarca 9/5 ca "in vigoare azi" (altfel ultima intrare = data_out None).
cote_perioada (d301) interogheaza tva_redusa/_9/_5 si DEDUP pe valoare: 2026 -> [21,11,0] (neschimbat);
pre-08.2025 -> [19,9,5,0]. Etichete adaugate in expirare_cote.py (gard acoperire ETICHETE==chei COTE).

LIMITA DE TEMEI (§3, onest): datele de INCEPUT ale cotelor 9%/5% NU sunt in codul fiscal consolidat (/tmp/cf.txt;
nota istorica de introducere nu e pastrata, iar fostul alin.(3) apare doar ca "Abrogat"). Ancorate la 2017-01-01
(inceputul erei standard 19%), nivel_sursa REDARE, cu caveat "de reconfirmat la MO" in temei (INTERPRETARE CU
TEMEI). Pt perioade < 2017 cota() REFUZA (PerioadaIndisponibila, fail-loud) - nu se presupune. Textul verbatim al
fostului alin.(3) la 5% de reconfirmat cand apare o sursa istorica. Ce e SIGUR: articolele (alin.2=9%, alin.3=5%)
si sfarsitul (31.07.2025, comasare Legea 141/2025).


## 03.08.2026 — Cluster "rotunjire aritmetica (A91b)" (D390) INCHIS prin VERIFICARE. Referinta DUK regula A91b.

d390._int (d390.py:59) foloseste ROUND_HALF_UP (schimbat de la round() bancar pe 27.07.2026). ANAF cere rotunjire
ARITMETICA (half-up), nu bancara - validator DUK regula A91b (referinta de structura, NU temei normativ, §3.1).
Deja gardat DUBLU: identitate cross-generator (d390._int == d300 == d112 == d205) + scan anti-round() bancar pe
toate generatoarele. Adaugat proba d390-specifica pe VALOARE (paritate cu d300/d112/d205): _int(0.5)=1, _int(2.5)=3,
_int(112.5)=113 (mutant bancar: 0/2/112). FARA fix necesar.


## 03.08.2026 — Cluster "reclasificari manuale" (D390) INCHIS. Temei DECIZII 21.07 + OPANAF 705/2020.

ASIMETRIE reparata: calea de SCRIERE (salveaza_reclasificare) valida tip+DIRECTIE (emisa:L/T/P/R, primita:A/S),
dar calea de CITIRE (calcul_d390 + operatiuni_auto) facea fallback TACIT la default doar pe tip not in TIPURI, fara
verificare de directie. Un override invalid care ocolea API-ul (migrare / DB direct / o a doua cale de scriere) ->
misclasificare tacuta (intentia contabilului, ex. P, inlocuita tacut cu L default), declaratie gresita la ANAF.
Contrazicea principiul propriu al gardului liniilor manuale (tip contabil invalid -> eroare vizibila, nu disparitie
/schimbare tacuta).

FIX: TIPURI_DIRECTIE mutat in d390.py (sursa unica; importat de d390_clasificare_api - elimina si riscul de import
circular). Helper _reclasificare_tip valideaza direciția (ca write-side) si RIDICA pe override nelegal, in AMBELE
cai de citire (calcul + preview). Pe date valide: 0 schimbare (scrierea garanteaza validitatea, deci raise-ul nu se
declanseaza pe fluxul UI). GENERALIZARE: acum toate cele 3 cai (scriere, citire-calcul, citire-preview) + liniile
manuale trateaza identic un tip invalid = eroare vizibila. Clasa "input contabil invalid -> fail-loud" completa pe D390.


## 03.08.2026 — Cluster "exigibilitate / prag" (D390) INCHIS prin VERIFICARE. Temei CF art.283/284/325.

INCADRARE TEMPORALA: D390 incadreaza operatiunea pe data_emitere a facturii (pull d390.py, fereastra
[M-01,(M+1)-01)). CF art.283 (livrari IC) / art.284 (achizitii IC): exigibilitatea intracom intervine la DATA
EMITERII facturii; CF art.325 alin.(1)/(4): declaratia se face pentru luna in care ia nastere exigibilitatea. In
cazul normal (factura emisa prompt) data_emitere = exigibilitate -> CONFORM. Adaugat gard temporal pe fereastra pull
(golul de acoperire: testele calcul ocoleau pull).

PRAG: fara prag valoric (CF art.325 alin.(4): se depune doar pt lunile cu exigibilitate - criteriu de EXISTENTA a
operatiunii, nu de valoare, spre deosebire de Intrastat). d390_are_operatiuni + genereaza refuza pe zero cu temei
citat (art.325 + OPANAF 705/2020 pct.1.2) = CONFORM. Codul nu are logica de prag.

EDGE-CASE consemnat (NEreparat, DECIZIE DE SCHEMA/PRODUS deschisa): art.284/283 mai au o regula alternativa -
exigibilitatea intervine "in a 15-a zi a lunii urmatoare celei in care a intervenit faptul generator, DACA nu s-a
emis factura pana atunci". Cand factura intarzie (ex. fapt generator august, factura 20 oct), legal exigibilitatea
= 15 sept -> D390 septembrie, dar codul incadreaza pe oct (data_emitere). NU e implementabil azi: tabela facturi nu
stocheaza data faptului generator (data livrarii/receptiei bunurilor). Cauza = limitare de SCHEMA, nu bug de logica
in d390.py. Impact practic mic (facturile intracom se emit prompt, sub ziua 15); supapa existenta = linii manuale
(d390_manual forteaza luna). FIX-ul cere intai un camp data_faptului_generator in facturi (+ ce introduce
contabilul la receptie) = decizia lui Costin. Consemnat, lantul continua (inchiderea acestui cluster nu-l cere).


## 03.08.2026 — CLAUDE.md §2.3 pct.5: limita de 6 clustere/rulare ELIMINATA (decizia lui Costin).

Limita de 6 clustere/rulare (introdusa 02.08 ca prudenta la prima rulare nesupravegheata) se elimina - nu mai e
justificata dupa 15 clustere inchise cu poarta verde si zero regresii. Executorul continua lantul pana la unul din
criteriile de oprire RAMASE: (a) urmatorul blocat si toate cele de dupa blocate; (b) decizie de produs (scop, push,
migrare pe date reale, schimbare de schema); (c) neconformitate care cere oprire (CICLUL); (d) poarta rosie/tree
murdar (pct.4); (e) context efectiv epuizat (pct.6, predare scrisa). Oprirea "ca sa decida Costin ordinea" NU e
criteriu - ordinea o da agenda. Modificare pur ADITIVA la istoric (pct.5 pastreaza data introducerii + eliminarii).


## 03.08.2026 — Cluster "cote acceptate" (D394) INCHIS prin VERIFICARE. Temei OPANAF 2194/2025 + structura D394.

D394 e CONFORM si e chiar MODELUL-TINTA la care a fost adus d301: cota_standard (d394.py:258) period-aware din
common.cota (documenteaza evitarea bugului int(0.21)=0); cotele operatiunilor validate contra unui set FIX
d394.COTE=(0,5,9,11,19,20,21,24) ce oglindeste validatorul ANAF v5 (OPANAF 2194/2025: 21/11 de la 01.08.2025) peste
structura 2020 (0,5,9,19,20,24); agregarea pe cota REALA a fiecarei operatiuni (rectificativele pe luni vechi se
grupeaza corect sub 19/9/5). NICIUN literal de cota hardcodat (bugul d301 nu se regaseste). FARA fix.

Setul fix (nu period-aware) e CORECT aici: validatorul ANAF proceseaza cu acelasi set indiferent de perioada
(inclusiv rectificative), deci d394.COTE e superset istoric+curent, nu se restrange pe luna.

Garduri adaugate: (a) pin d394.COTE == setul v5 (anti-drift); (b) CROSS-MODUL: orice cota tva_* din common.COTE
subseteaza d394.COTE - o cota noua adaugata candva in common care nu e in d394.COTE ar fi ignorata tacit de D394.
Leaga sursa unica de cote (common) de setul acceptat de D394.


## 03.08.2026 — Cluster "taxare inversa" (D394): NECONFORMITATE gasita (lit.l gaze), CORECTARE blocata pe codPR.

CICLUL DE NECONFORMITATE parcurs:
- OPRIRE: firul "cote/taxare" suspendat, tratata acum.
- GENERALIZARE: clasa = enumerarea celor 12 categorii art.331 alin.(2) lit.a-l. Codul implementeaza 11 (a-k).
  LIT.L GAZE NATURALE (livrarea de gaze naturale catre comerciant persoana impozabila, art.331 alin.2 lit.l, in
  vigoare pana 31.12.2026 cf. alin.6) lipseste din DOUA situri: taxare_inversa.CATEGORII (motor) + d394.CODPR
  (mapare D394). Header-ul taxare_inversa.py mentioneaza chiar "lit.c-f, i-l" -> omisiune dovedita, nu excludere.
  Restul enumerarilor (rip_api/casa_api/cote_tva) = categorii nelegate de art.331.
- CORECTARE: BLOCATA. Partea legala e verificata (art.331 lit.l + expira 31.12.2026 alin.6), DAR codPR-ul D394
  pentru gaze naturale NU e in nicio sursa ANAF din repo: nomenclatorul e Ghid_D394_2016 (anterior Legii 296/2020
  care a introdus gazele); tip_partener=1 = codurile 21-31, 32-35 REZERVATE tip_partener=2. §3: nu se inventeaza.
  Adaugarea doar in CATEGORII (fara codPR) ar REGRESA: factura recunoscuta dar dropata din op11 obligatoriu.
- GARD: (a) anti-regresie cross-modul - orice categorie din CATEGORII trebuie sa aiba codPR (previne fixul pe
  jumatate); (b) datorie xfail(strict) gaze naturale in test_datorie.py.

DECIZIE / INPUT CERUT LUI COSTIN: pentru a completa fixul e nevoie de codPR-ul D394 pentru gaze naturale dintr-o
structura/ghid D394 ANAF post-2021 (post Legea 296/2020). Pana atunci: gaze reverse-charge NU se poate depune in
D394 (motorul refuza, fail-loud). Datorie tracked, lantul continua (11/12 conform, gardat).


## 03.08.2026 — Cluster "SourceDocuments (facturi reale, PARTIAL)" (D406) — FIX period-awareness + observatii.

Partea solida (reparata 27.07): SalesInvoices/PurchaseInvoices cu LINII REALE pe produs din factura_linii,
reconciliate obligatoriu cu antetul, DUK-validate structural.

FIX (03.08): TaxCode livrari PERIOD-AWARE. TAXCODE_LIVRARI_PRE_2025_08 (coduri 19/9/5 pre-01.08.2025) era DEFINIT
dar NEFOLOSIT; pull() folosea mereu TAXCODE_LIVRARI (post) indiferent de data facturii -> o rectificativa pe luna
< 08.2025 emitea coduri gresite (19% negasit -> default 310312 taxare inversa; 9% pre confundat cu 9% post = alt
cod). Helper _taxcode_livrari(cota, data) selecteaza tabela pe data_emitere; folosit la AMBELE situri livrari
(per-linie + fallback fara linii). Gard test_taxcode_livrari_period_aware. Docstring STADIU actualizat (era stale -
descria linia sintetica veche, deja reparata 27.07).

OBSERVATII documentate (NEfacute, pentru clustere/decizii viitoare):
- Payments = gol: cod de emitere complet, dar ZERO date de plati in model (chitante/casa_operatiuni goale in toti
  tenantii). Datorie legitima BLOCATA PE DATE (DECIZII 27.07); se reia la prima plata reala + populare pull().
- TaxCode ACHIZITII grosier: pull() emite mereu 300501 pt achizitie cota>0 (300101 doar taxare inversa/cota 0),
  fara sa diferentieze deductibilitate 100%/50%/nedeductibil (schema are coduri distincte). Necesita modelul de
  deductibilitate per factura + codurile exacte din schema -> investigatie separata (posibila datorie).
- BillingAddress placeholder: _factura_xml hardcodeaza City gol / Country=RO; adresa partenerului nu e trasa din
  nomenclatorul clienti/furnizori. Trece XSD (permisiv) dar e date fictive.
- AssetTransactions: absent, XSD minOccurs=0 (optional) - nu e datorie.
- Lipsa test GOLDEN pe _factura_xml/_source_documents (reparatia 27.07 n-are gard de regresie pe continutul XML) -
  de adaugat un golden pe fluxul complet construieste->build_xml.


## 03.08.2026 — Cluster "plafon diurna neimpozabila" (deconturi) — calcul curent CONFORM + datorie istorica.

Motorul deconturi.py calculeaza plafonul neimpozabil = min(2,5 x diurna bugetara; 3 salarii/zile lucratoare) x
zile deplasare, excedentul = venit salarial (D112). Formula = CONFORM CF art.76 alin.(4^1) (text verificat la
sursa de subagent) pentru perioada CURENTA (2023+). Adaugat gard golden (core/test_deconturi.py) - lipsea (era
doar test de dispecer versionare in test_versionare_formule.py).

NECONFORMITATE period-awareness istorica (datorie xfail strict): _VARIANTE_PLAFON_DIURNA are o SINGURA varianta
(2018-01-01) care aplica retroactiv valorile de azi (23 lei + capul 3-salarii) pentru 2018-2022. Capul "3 salarii"
a intrat 2023-01-01 (Legea 72/2022, art.76 alin.4^1); baza bugetara era alta pre-2023 (HG 714/2018 - codul insusi
citeaza inconsistent "HG 714/2018 (Ordinul 1235/2023)" pe valoarea 23). Fix BLOCAT: valorile istorice HG diurna NU
sunt in sursele repo (0 surse HG 714/518 pe server); §3 nu se inventeaza.

INPUT CERUT COSTIN: HG 714/2018 (+ succesoare) cu diurna interna bugetara istorica + data trecerii la 23 lei, ca
sa se splitze _VARIANTE_PLAFON_DIURNA in >=2 variante datate (2018 fara cap + valoarea epocii; 2023 cu 23 + cap).
EXTERN: si un nomenclator HG 518/1995 pe tari (inexistent) pentru automatizarea diurnei externe. Pana atunci:
deconturi pe perioada curenta = corecte; cele pe 2018-2022 folosesc regula de azi (datorie tracked).


## 03.08.2026 — Cluster "credit sponsorizare / D177" (sponsorizari) — profit CONFORM + 3 observatii.

PROFIT CONFORM: creditul de sponsorizare = min(0,75% CA; 20% impozit pe profit) + conditia registru entitati
(art.25 alin.4^1) = conform CF art.25 alin.(4) lit.i (verificat la sursa). Reportul pe 7 ani corect ELIMINAT (nu
mai exista din 2022; sumele legacy 2015-2021 utilizabile pana in 2028 - codul afirma corect). Gardat de
test_operatiuni_speciale.py (4 teste). FARA fix pe profit.

NECONFORMITATE / DECIZII deschise:
1. MICRO NU e period-aware (DATORIE xfail strict): _credit_sponsorizare_2018 intoarce 0 pentru micro la ORICE
   data, desi 2019-2023 micro avea creditul (20% impozit micro, redirectabil). Aplica retroactiv eliminarea din
   2024 (OUG 115/2023) - contrazice propriul docstring ("eliminarea micro -> varianta datata, trecutul ramane
   calculabil"). Fix BLOCAT: rata+start micro nu-s in consolidat (fostul art.56 alin.1^5 = "Abrogat"; §3 nu se
   inventeaza). Necesita textul istoric (OUG/lege introducere micro sponsorship).
2. D177 (redirectionare) = FORMULAR ABSENT = DECIZIE DE PRODUS. Se calculeaza doar scalarul redirectionabil_d177
   = plafon - credit; NU exista generator de formular/XML D177 conform Ordin ANAF 3562/2024, nici termen de
   depunere. Construirea formularului D177 = scop nou, cere decizia lui Costin.
3. Endpoint main.py:7853 apeleaza credit_sponsorizare FARA la_data (foloseste regula de azi indiferent de anul
   fiscal al sponsorizarii); d101.py nu apeleaza deloc motorul. Wiring de period-awareness - observatie.


## 03.08.2026 — Cluster "rezerva legala" (motor) — formula contabila CONFORMA + deductibilitate fiscala = decizie produs.

Formula rezervei legale CONTABILE (motor.py _rezerva_legala_2018): 5% din profit, plafon cumulat 20% capital minus
rezerva existenta, oprire la plafon = CORECTA structural (Legea 31/1990 art.183, OMFP 1802/2014 pct.421), period-aware
prin dispecer. Lipsea test NUMERIC (doar tautologic in test_versionare_formule) - adaugat gard golden pe valoare.

NECONFORMITATE / DECIZIE DE PRODUS deschisa:
1. Deductibilitatea FISCALA a rezervei legale (CF art.26 alin.(1) lit.a) LIPSESTE complet din sistem. Baza legala =
   "profitul contabil, LA CARE SE ADAUGA cheltuielile cu impozitul pe profit, pana ce atinge a cincea parte (20%) din
   capitalul social subscris si varsat". Add-back-ul cheltuielii cu impozitul NU exista nicaieri; d101 P6 "Deduceri
   fiscale" e input MANUAL din formular, necalculat. Implementarea (calcul deducere + legare in d101 P6) SCHIMBA
   declaratia de impozit pe profit -> DECIZIE DE PRODUS (§2.3 pct.2), cere decizia lui Costin. Regula E disponibila
   (art.26(1)a verbatim), deci nu e blocata pe temei - e o functionalitate de construit + conectat.
2. motor.py rezerva_legala e cod MORT: apelat doar din test tautologic, niciun apelant de productie (inchidere_an/
   bilant/d101 nu-l cheama). De conectat cand se implementeaza fluxul.
3. Minor: motor.py:82 foloseste capital_social generic; art.26(1)a cere "subscris si varsat".


## 03.08.2026 — CAMPANIE ACHITARE DATORII, sectiunea B: temeiuri istorice CONFIRMATE la sursa, datorii INCHISE.

Cercetare web (legislatie.just.ro / MO / static.anaf.ro), surse salvate in anaf_surse/ cu sha256:

B1. COTE REDUSE 9%/5% - data reala 01.01.2016 (Legea 227/2015, MO 688/2015), NU 2017 (ancora era gresita cu un
    an). Corectata in common.COTE tva_redusa_9/_5 la 2016-01-01; caveat "de reconfirmat" SCOS. Nota: apa/ingrasaminte
    (art.291 g/h) adaugate de Legea 175/2018 din 01.01.2019; locuinte 5% continuitate din vechiul cod (OUG 200/2008).
    Sursa: anaf_surse/cf_art291_2016_forma_initiala.txt (sha256 d065557f...).

B2. DIURNA interna bugetara: 20 lei HG 714/2018 (MO 1050/2018, din 2018) -> 23 lei Ordin MF 1235/2023 (MO 261/2023,
    din 01.04.2023). deconturi._VARIANTE_PLAFON_DIURNA acum 2 variante datate (20/23) period-aware; plafon 2,5x =
    50 lei pre-2023.04, 57,5 dupa. DATORIE + xfail INCHISE. Extern HG 518/1995 = nomenclator pe tari (salvat).
    Surse: anaf_surse/hg714_2018_diurna_interna.txt (ff589128...), hg518_1995_diurna_externa.txt (bc48ff12...).

B3. MICRO-SPONSORIZARE: regula la art.56 alin.(1^1) (nu 1^5): credit = 20% impozit micro, VALABIL 01.04.2019
    (Legea 30/2019; introdus OUG 25/2018) - 31.12.2023 (abrogat OUG 115/2023). sponsorizari.py branch micro acum
    period-aware (2019-2023: min(sponsorizare, 20% impozit micro); rest 0). DATORIE + xfail INCHISE.
    Sursa: anaf_surse/cf_art56_alin15_istoric_micro_sponsorizare.txt (sha256 918054ae...).

B4. GAZE NATURALE D394 codPR = 36 (ANAF structD394_15092025.pdf + structD394_10052022.pdf; OPANAF 77/2022 de la
    01.04.2022, urmare Legea 296/2020). CATEGORII lit.l (taxare_inversa.py) + CODPR "36" (d394.py) COMPLETE;
    gaze reverse-charge se poate acum depune in D394. DATORIE + xfail INCHISE. Sursa:
    anaf_surse/d394_codpr_gaze_naturale.txt (sha256 711ff5aa...).

SOLD dupa sectiunea B: 24 xfail -> 21 (inchise gaze, diurna, micro; cote reduse era refinare fara xfail).


## 03.08.2026 — CAMPANIE ACHITARE DATORII, sectiunile A + C: blocaje motivate + status.

Context-ul executorului critic incarcat dupa 12 clustere + sectiunea B; implementarile mari se scriu ca BLOCAJE
MOTIVATE (regula lui Costin: nu pe jumatate), cu groundwork-ul strans, pentru o sesiune cu context propriu.

### A1. Rezerva legala - deductibilitate fiscala art.26(1)a in d101 — BLOCAJ MOTIVAT (nevoie context propriu)
- CE: campul oficial e P13 "Rezerva legala deductibila" (d101_struct_anaf.txt:503, P13>=0), acum INPUT MANUAL in
  d101._P_INTRARI. De facut auto-computat.
- TEMEI VERIFICAT: CF art.26 alin.(1) lit.a (verbatim): "5% aplicate asupra profitului contabil, la care se
  adauga cheltuielile cu impozitul pe profit, pana ce atinge a cincea parte (20%) din capitalul social subscris
  si varsat". Deci P13 = min(5% x (profit_contabil + cheltuiala_impozit); 20% x capital_1012 - rezerva_1061), >=0.
- CE LIPSESTE (de ce e blocaj): d101.pull NU trage capital (cont 1012 subscris/varsat), rezerva existenta (1061),
  cheltuiala cu impozitul (691). Trebuie extins pull cu aceste 3 surse din balanta/inregistrari_linii. Plus proba
  pe schema efemera cu conturile populate + DUK. E o campanie proprie (data model + circular impozit<->rezerva).
- GROUNDWORK: formula clara, campul P13 identificat, sursele de date identificate. De implementat: pull+=1012/1061/
  691; calcul P13 auto cand nefurnizat; gard (omiterea deducerii cand conditiile sunt indeplinite -> imposibila);
  proba DUK. Fara ea firma supra-declara impozit pe profit.

### A2. D390 "ziua 15" - schema data_faptului_generator — BLOCAJ MOTIVAT (schimbare de schema pe date reale)
- CE: art.284 - exigibilitate intarziata (ziua 15 a lunii urmatoare faptului generator cand factura intarzie).
- CE LIPSESTE: camp nou data_faptului_generator in tabela facturi + migrare idempotenta pe TOTI tenantii + template.
  Costin cere: rulare pe schema efemera intai, arata, apoi tenanti; daca migrarea pica pe vreun tenant OPRESTE.
  Aceasta e o operatiune de deployment cu risc pe date reale - context propriu obligatoriu.
- GROUNDWORK: incadrarea actuala pe data_emitere e conforma in cazul normal (gard temporal exista, cluster
  exigibilitate|d390 inchis). Backward-compat: camp optional, gol -> comportament actual neschimbat.

### A3. D177 formular redirectionare — BLOCAJ MOTIVAT (structura oficiala neverificata + scop nou end-to-end)
- CE: formular de redirectionare a impozitului pe profit/micro nefolosit pt sponsorizare (Ordin ANAF 3562/2024).
- CE LIPSESTE: structura oficiala D177 (XSD/instructiuni) NU e in anaf_surse/. Costin cere: stabileste intai
  structura din anaf_surse/, daca lipseste desc-o de la ANAF si salveaz-o; fara structura oficiala NU inventa
  campuri. Apoi model+calcul+generare+UI+teste+DUK. Scop nou complet - context propriu.
- GROUNDWORK: motorul de credit (sponsorizari.py) calculeaza deja scalarul redirectionabil_d177 = plafon - credit.
  De construit formularul in jurul lui. Prima actiune: WebFetch structura D177 de la static.anaf.ro.

### C. DATORII MAI VECHI (GARZI)
- C1. Tichete cresa plafon indexat 740 (Ordinul 368/2026): RESEARCH la MO - de facut ca sectiunea B (metoda web
  a functionat: legislatie.just.ro/static.anaf.ro). Sursa primara daduse 503 anterior; reincearca. BLOCAJ:
  research nefacut in aceasta rulare (context), dar metoda e dovedita.
- C2. Fereastra culturale oct.2025-mar.2026 (240/470, Ordin 1574/3246/2025): idem C1, research la MO. BLOCAJ.
- C3. Metode amortizare neliniare MF/D406 (xfail test_datorie_mf_metode_amortizare): subsistem mijloace fixe,
  functionalitate de construit (degresiva/accelerata). RAMANE DESCHIS (xfail), scop propriu.
- C4. D112 sectiunea 8.3 avantaje pt TOATE biletele de valoare (E3_10/72/73/74/75): limita generator-wide.
  Implementare in generatorul D112 - scop propriu. BLOCAJ MOTIVAT.
- C5. Migrare tichete culturale pe tenanti reali (core.migrare_tichet_cultural): deployment pe date reale,
  aceleasi precautii ca A2 (efemera intai, apoi tenanti, oprire la esec). BLOCAJ MOTIVAT.
- C6. Tara XI (Irlanda de Nord post-Brexit): VERIFICAT-CORECT. XI e DEJA in d390.TARI_UE (d390.py:45) cu comentariu
    "post-Brexit, VIES". VIES foloseste XI pentru bunuri NI (Protocolul Irlanda/NI); nomenclatorul ANAF 2020 (doar
    GB) e cel invechit, codul e corect (inaintea nomenclatorului). Nu e datorie - observatie inchisa.


## 03.08.2026 — CAMPANIE A1 IMPLEMENTATA: rezerva legala deductibila (CF art.26(1)a) in d101.

Superseda blocajul A1 de mai sus - implementat si probat in aceasta rulare (commit 57777e5).

TEMEI (verbatim, verificat): CF art.26 alin.(1) lit.a: "5%% aplicate asupra profitului contabil, la care se
adauga cheltuielile cu impozitul pe profit, pana ce atinge a cincea parte (20%%) din capitalul social subscris
si varsat".

(1) DEPENDENTA CIRCULARA impozit<->rezerva REZOLVATA prin design: baza = profit contabil BRUT = P7 + cheltuiala
CONTABILA cu impozitul (cont 691, deja inregistrata in balanta), NU impozitul calculat de D101 -> cifra contabila
fixa, fara bucla. (d101 pune 69x in P2, deci P7 e post-691; se adauga 691 inapoi = profit pre-impozit.)

(2) SURSARE (d101.pull extins cu 3 interogari): capital 1012 (subscris/varsat) = sold cumulat pana la SFARSITUL
perioadei; rezerva 1061 EXISTENTA = sold cumulat pana la INCEPUTUL anului (anii anteriori); 691 = cheltuiala cu
impozitul pe anul curent. (Bug de escaping SQL prins in dezvoltare: triple-apostrof in loc de apostrof simplu.)

CALCUL (calcul_d101, camp oficial P13 "Rezerva legala deductibila", d101_struct_anaf.txt:503): auto cand P13 nu e
dat manual -> P13 = max(0, min(5%% x baza; 20%% x capital - rezerva existenta)); intra in P16 (deduceri) -> reduce
profitul impozabil P22 -> mai putin impozit. Override manual respectat.

GARD (§9): core/test_d101.py::test_rezerva_legala_deductibila_auto_art26_1_a (17500 / plafon musca 5000 / pierdere
0 / override manual 9000) + PROBA PE DATE REALE core/test_pull_declaratii.py::test_d101_rezerva_legala_din_conturi
_reale (conturi 1012/707/607/691 reale in schema efemera -> P13=17500). Omiterea deducerii cand conditiile sunt
indeplinite devine IMPOSIBILA (auto by default).

DUK: validatorul D101 nu e instalat in pachetul DUKIntegrator (duk.poate_valida D101 = False) -> proba DUK = GRI,
consemnata (§2.3 pct.3); proba pe date reale acopera sursarea + calculul end-to-end.

EFECT PE PRODUS: firma cu profit + capital care nu introducea manual P13 NU mai supra-declara impozitul pe profit
- deducerea rezervei legale se aplica automat din contabilitate.


## 03.08.2026 — Cluster "zilieri (impozit+CAS)" (contracte_speciale) — FIX period-awareness CAS.

Impozit 10%% (CF art.76(2) lit.r - venit asimilat salariilor) + CASS 0 (zilierii nu-s in art.157) = CONFORME.
NECONFORMITATE reparata: codul aplica CAS 25%% zilierilor din 2018-01-01, dar CAS pe zilieri exista LEGAL doar de
la 01.05.2019 (OUG 26/2019: adauga CF art.139(1) lit.s + Legea 52/2011 art.9^1; abroga exceptarea art.142 lit.t).
Pentru 2018-01-01..2019-04-30 codul retinea CAS 25 nedatorat + subevalua impozitul (7,5 vs 10) + net subevaluat
(67,5 vs 90 la brut 100). FIX: 2 variante datate - 2018-01-01 (doar impozit 10%% pe brut) + 2019-05-01 (CAS 25%% +
impozit pe brut-CAS). Verificat la sursa (/tmp/cf.txt: OUG 26/2019 pct.1/2, in vigoare 01.05.2019).

OBSERVATIE (nu neconformitate de calcul): plafonul de zile (max 90/an la acelasi beneficiar; 120 agricultura)
e doar in docstring, NEaplicat - motorul calculeaza pe brutul dat, nu semnaleaza depasirea. De implementat in
fluxul de introducere daca se cere semnalarea.


## 03.08.2026 — Cluster "regim marja second-hand" (tva_marja) — VERIFICAT conform + gard golden.

Motorul (tva_marja.py) calculeaza TVA pe marja = marja x cota/(100+cota) - suta MARITA (TVA inclus in marja, se
extrage), conform CF art.312 alin.(4) (baza = marja profitului EXCLUSIV valoarea taxei aferente). Nota: regula NU e
la art.313 (acela = aurul de investitii); codul citeaza corect art.312. Marja negativa/zero -> TVA 0. CONFORM.
Lipsea test numeric -> gard golden adaugat (marja 400 cota 21 -> 69,42; negativa -> 0; cota 19 -> 63,87).

OBSERVATII (integrare in main.py endpoint /vanzare-marja, NU formula):
1. Cota NU e validata period-aware: common.cota_ceruta doar respinge cota lipsa, nu face cross-check cu
   common.cota("tva_standard", data). Un client care trimite o cota gresita pentru perioada e acceptat tacit.
   De adaugat un cross-check la endpoint (avertisment/eroare la nepotrivire).
2. la_data NU se paseaza la motor (main.py:6351 apeleaza vanzare_marja fara la_data) -> versionarea FORMULEI se
   face pe data de azi, nu pe data tranzactiei. Inofensiv acum (o singura varianta din 2018), dar o tranzactie
   datata < 2018 ar folosi formula curenta in loc sa ridice. Fix: vanzare_marja(..., la_data=corp["data"]).


## 03.08.2026 — Cluster "regim marja turism" (tva_marja_turism) — VERIFICAT conform + gard golden.

Motorul (tva_marja_turism.py) calculeaza TVA pe marja de turism = marja_taxabila x cota/(100+cota) - suta MARITA,
conform CF art.311 alin.(4); scutirea PROPORTIONALA pentru partea serviciilor prestate in afara UE (alin.5) e
tratata (coef = cost_non_ue / cost_total). Marja negativa/zero -> TVA 0. Cota period-aware (parametru). Consistent
cu art.312 second-hand (deja verificat). CONFORM. Lipsea test numeric -> gard golden adaugat.

OBSERVATII (nu bug de formula):
1. Motorul NU e integrat in datorie.py (niciun apelant de productie; testat izolat). Daca turismul trebuie sa
   apara in datoria efectiva, lipseste wiring-ul.
2. Cota vine ca parametru cu default 21; la integrare, cota sa fie luata din common.cota(..., la_data), nu din
   default (un apelant care foloseste 21 pt o data < 01.08.2025 ar aplica gresit 21 in loc de 19).


## 03.08.2026 — Cluster "impozit dividend" (decontari_asociati) — FIX cote istorice (verificate la sursa).

Mecanismul e period-aware corect (common.cota("impozit_dividend", data), peticul if-data eliminat). DAR datele din
COTE erau GRESITE: singura intrare pre-2026 era 10% (petic mutat 1:1 din vechiul "else 10"). 10% NU a fost NICIODATA
cota pe dividende - e cota impozitului pe VENIT (CF art.78). Consecinta: orice D205 / nota dividend pentru 2023/2024/
2025 producea 10% in loc de 8% (supra-impozitare cu 2 puncte; 50000 -> 5000 in loc de 4000); iar 2023 si 2016-2022
dadeau PerioadaIndisponibila (data_in gresit 2024; era de 5% lipsa).

FIX: 3 intrari VERIFICATE la sursa (anaf_surse/impozit_dividende_istoric_cote.txt, sha256 d4dcab78...):
- 5% (01.01.2016-31.12.2022): Legea 227/2015 + OUG 50/2015 (MO 817/2015).
- 8% (01.01.2023-31.12.2025): OG 16/2022 (MO 716/2022), aprobata prin Legea 370/2022.
- 16% (de la 01.01.2026): Legea 141/2025. Cota se aplica dupa data DISTRIBUIRII.

TESTELE care cimentau 10% (test_impozit_dividend.py, test_d205.py) - clasa "teste care apara buguri", motivul
ne-auto-detectarii - actualizate la valorile reale. Restul (conturi 457/446/5121, mecanica notelor, D205 pe 16%
2026, lichidare) conform.


## 03.08.2026 — Cluster "contributii PFA (praguri CAS/CASS pe sm)" (d212) — VERIFICAT conform + fix citare temei.

Calculul contributiilor PFA in D212 (d212_engine.py) e CONFORM: CAS 25%% pe praguri 12/24 sm (CF art.148: <12 sm
optional baza 12; [12,24) baza 12; >=24 baza 24), CASS 10%% model LINIAR pe venitul net efectiv intre 6 sm si
plafon 60/72 sm (CF art.170 alin.1 - treptele 6/12/24 din alin.2-3 sunt DOAR pt venituri pasive lit.c-h, nu PFA),
impozit 10%% pe (net - CAS - CASS). sm period-aware din common.cota (reper 1 ian). Plafon 60->72 sm comuta pe an.
Cablat in productie (rip_api.fisa_d212 -> main.py endpoint /rip/d212). Gardat de test_d212.py (valori) + reper.

FIX de TEMEI (§3.1 - citare mecanica): plafonul CASS 72 sm pentru venituri 2026 era atribuit gresit "Legea 141/2025"
(aceea modifica TVA/accize, MO 699/25.07.2025). Sursa corecta (CF art.170 alin.1) = Legea 239/2025 art.XII pct.19
(MO 1160/15.12.2025), aplicabila veniturilor 2026. Valoarea (72 sm) e corecta si confirmata; gresit era doar actul.
Corectat in d212_engine.py:4/40/46 + test_d212.py:11/53 + coloana temeiuri Inventar A.

OBSERVATIE (nu bug de calcul): calea 2026 (PLAFOANE_VENIT_2026, 72 sm) e codata+testata dar DORMANTA in productie -
rip_api.py:145 blocheaza an != 2025 (corect/conservator pt sezonul curent: venituri 2025 depuse in 2026). Garda
trebuie ridicata la an=2026 la deschiderea depunerii din 2027.


## 03.08.2026 — Cluster "nomenclator cod_oblig<->cod_bugetar" (d100) — FIX cont bugetar obsolet + gard anti-drop.

D100 mapa cod_oblig 121 (micro) si 103 (profit) la contul bugetar 20470101 - OBSOLET, inlocuit oficial cu 5503 din
26.07.2018 (d100_struct_anaf.txt:562: "Se va inlocui peste tot contul bugetar 20470101 cu 5503"), + fara X-padare la
C(10). COROBORARE INTERNA decisiva: d101 (acelasi cod_oblig 103) si d112 emit deja "5503XXXXXX" - d100 isi contrazicea
fratii pentru exact aceeasi obligatie. FIX: COD_BUGETAR 121/103 -> "5503XXXXXX" (padat C(10), forma d101/d112). Sursa
UNICA (d710 importa acelasi COD_BUGETAR din d100 - fixul propaga). Testele care cimentau 20470101 (d100/d710) actualizate.

GARD anti-drop (clasa "drop tacit"): un cod_oblig fara cont bugetar (necunoscut in nomenclator) ridica acum ValueError,
nu omite tacit atributul obligatoriu (care ar fi produs un XML respins de ANAF fara niciun avertisment).

GENERALIZARE: 20470101 aparea DOAR in d100.COD_BUGETAR + testele d100/d710 (sursa unica). d112 foloseste corect
5503XXXXXX (+ 20470300XX pentru CAM, cont diferit legitim). Clasa complet acoperita.


## 03.08.2026 — Cluster "cota micro 121 (flag)" (d100) — VERIFICAT conform + gard bidirectional.

Generatorul e CONFORM struct D100 poz.17a: micro (cod_oblig 121) emite cota="1", profit (103) fara cota (regula
"daca cod_oblig=121 atunci cota=1 altfel cota=null"). Rata impozitului micro pentru SUMA e period-aware din registru
(impozit_micro=1%), separata de flag-ul de STRUCTURA cota="1" (checksum ANAF, mereu 1 pt 121).

Adaugat GARD bidirectional in build_xml: cod_oblig 121 fara cota="1" -> ValueError; cota pe orice alt cod_oblig ->
ValueError. Face imposibil un XML respins de validator (ERR cota micro), inclusiv pe apel direct/manual (generatorul
prin genereaza producea deja corect). Clasa "atribut conditionat de structura - aplicat sau eroare, nu emis gresit tacit".


## 03.08.2026 — Cluster "checksum totalPlata_A (R11b)" (d100) — VERIFICAT + aliniere la sursa unica.

Valoarea EMISA in XML (totalPlata_A = 2x sum(suma_dat), DUK R11b) era CORECTA. DAR o divergenta: calcul_d100 punea
res.total_plata_a = sum(suma_dat) (1x), iar build_xml recalcula 2x sum INDEPENDENT (nu folosea res). Toate celelalte
declaratii (d101/d300/d390/d710/d394) EMIT res.total_plata_a - d100 era exceptia (capcana latenta: cine ar folosi
res.total_plata_a al d100 ca checksum - ex. un cross-check ca la d390.py:233 - ar primi 1x, gresit). FIX: res.
total_plata_a = checksum (2x sum, calculat in calcul_d100) + build_xml il EMITE (o singura sursa, aliniat la
convenția tuturor declaratiilor). Gard: res.total_plata_a == valoarea din XML == 2x sum(suma_dat).


## 03.08.2026 — Cluster "scadente/nr_evidenta" (d100) — VERIFICAT conform + gard scadenta.

nr_evidenta: CONFORM struct D100 - 23 pozitii, format oficial (10 + cod_oblig + 01 + LLAA + ZZLLAA + 0+0+00 +
suma_control), poz.18="0" (dupa fix R16 pe validator). Gardat de 3 teste (23 caractere, prefix 10+cod_oblig+01,
suma de control poz.22-23). scadenta: _scadenta_zile = 25 a lunii URMATOARE perioadei (struct poz.15), format
ZZ.LL.AAAA. Conform pentru obligatiile generate de d100 (121 micro + 103 profit trimestrial: Q1-Q3 -> 25 apr/jul/
oct; Q4 -> 25 ian an urmator). Lipsea test pe scadenta -> gard golden adaugat.

OBSERVATIE: struct-ul are si alte reguli de scadenta (25/12, 28-29/07, 25 a lunii a 2-a) pentru ALTE obligatii
(accize etc.) pe care d100 NU le genereaza - regula standard "25 luna urmatoare" e cea aplicabila micro/profit.
(Definitivarea impozitului pe profit Q4 = D101, nu D100 - scadenta 25 martie an urmator, tratata acolo.)


## 03.08.2026 — Cluster "structura P1-P53" (d101) — VERIFICAT CONFORM SI COMPLET.

Structura P1-P53 din calcul_d101 e completa si corecta fata de OPANAF 206/2025 (D101_A600 v10). Toate formulele
derivate coincid rand-cu-rand cu structura oficiala: P3=P1-P2, P6=P4-P5, P7=P3+P6, P10=P7+P8-P9, P16=SP11..P15,
P21=SP17..P20, P22=P10-P16-P21, P34=SP23..P33, P35=P22+P34, P38a=P35+P36+P37-P38, P40 (profit impozabil cu
conditii), P41=P411+P412, P48 (dispecerat P46/P47), P52/P53, totalPlata_A=sum(P1..P53) fara sub-randuri 'din care'.
P13 rezerva legala (adaugat la A1) corect (baza P7+691, plafon 20% capital). d_grup tratat pe toate randurile
relevante. Toate 53 randurile principale tratate (calculate sau intrare); sub-randurile 'din care' excluse corect
din checksum. FARA neconformitate, FARA fix.

Deja gardat de test_golden_lant_formule_oficiale (lantul complet, golden 419200) + test_d101_reconstructie_proba_
duk_valid. §9: reaparitia imposibila prin golden. (xfail-ul mf_metode_amortizare din test_datorie NU afecteaza d101 -
amortizarea fiscala intra ca input P11, calculata extern.)


## 03.08.2026 — Cluster "R17 Data_S / termen" (d101) — BLOCAT pe DECIZIE DE PRODUS: scadenta D101 lege-vs-validator INVERSATE.

NECONFORMITATE DESCOPERITA + CONFLICT NEREZOLVABIL AUTONOM. Scadenta platii D101 (declaratia anuala de impozit pe
profit) e o regula period-aware. Legea si validatorul OFICIAL ANAF o citesc EXACT INVERS:

| An fiscal (Data_S) | LEGEA (CF art.42(1), verificat la sursa) | Validatorul OFICIAL DUKIntegrator (R17, testat) |
|---|---|---|
| 2022-2025 | 25 MARTIE an+1 (Legea 227/2015 text originar) | 25 IUNIE an+1 (R17: LL+6) |
| 2026+ | 25 IUNIE an+1 (OUG 8/2026 art.6 pct.12) | 25 MARTIE an+1 (R17.1: LL+3) |

EVIDENTA:
- CF art.42(1) text CURENT (consolidat, /tmp/cf.txt linia 845): "...pana la data de 25 IUNIE inclusiv a anului urmator",
  modificat de OUG 8/2026 art.6 pct.12 (MO nr.147 din 25 februarie 2026), aplicabil INCEPAND CU declaratia aferenta
  anului fiscal 2026 (OUG 8/2026 art.45 alin.21^4 + art.10 alin.2). Text pre-OUG (an fiscal <=2025) = "25 martie"
  (cercetare interna, Legea 227/2015 originar).
- Validatorul DUKIntegrator INSTALAT (jar oficial ANAF): eroare R17 pentru Data_S 2023/2024/2025 cere LL+6 (iunie),
  respinge martie; eroare R17.1 pentru Data_S 2026 cere LL+3 (martie), respinge iunie. Testat direct pe cei 4 ani.
- Codul (inainte de acest cluster) urmeaza VALIDATORUL (iunie 2022-2025, martie 2026+) - reconstruit ca declaratiile
  sa treaca DUKIntegrator. Probele DUK (test_d101_reconstructie_proba_duk_valid, test_imca_d101_duk_valid) trec DOAR
  cu valorile validatorului.

DE CE E DECIZIE DE PRODUS (nu fix mecanic): daca schimb codul la valorile LEGII, TOATE declaratiile D101 sunt RESPINSE
de validatorul oficial ANAF -> utilizatorii nu le pot depune. Daca pastrez valorile validatorului, ele contrazic textul
CF verificat. §3 spune TEXTUL CASTIGA, dar aici "textul" (legea) si "unealta oficiala" (DUKIntegrator) sunt in conflict
direct, iar tool-ul exista tocmai ca sa produca fisiere ACCEPTATE de ANAF.

RISC ASIMETRIC (de aceea nu-l inchid tacit): pentru 2022-2025, daca legea (martie) e corecta, valoarea validatorului
(iunie) declara o scadenta cu ~3 luni mai TARZIU -> risc de intarziere/amenda. Pentru 2026, validatorul (martie) e mai
DEVREME decat legea (iunie) -> depunere anticipata, fara amenda. Deci pericolul real e pe ramura 2022-2025.

INCERTITUDINE FACTUALA de rezolvat: termenul 2022-2025 - cercetarea interna spune 25 martie (Legea 227/2015 originar,
neschimbat pana la OUG 8/2026), dar jar-ul oficial ANAF cere 25 iunie pentru acei ani. Contradictie care cere verificare
autoritara (posibil o modificare intermediara martie->iunie ratata de cercetare, SAU jar-ul are regula veche/bugata).

STARE: cod REVERTIT la valorile validatorului (poarta verde, declaratiile raman acceptate de DUK). Neconformitatea fata
de lege e prinsa ca DATORIE xfail-strict (test_datorie_d101_scadenta_lege_vs_validator). NU am marcat clusterul in
Inventar A - ramane deschis pana la decizia lui Costin.

DECIZIA CERUTA (Costin):
  (a) La scadenta D101, cand legea si validatorul difera, tool-ul urmeaza LEGEA (accepta respingerea DUK pana ANAF
      updateaza jar-ul) sau VALIDATORUL (output acceptat azi, revizuit cand jar-ul se updateaza)?
  (b) Verificarea autoritara a termenului 2022-2025 (martie vs iunie), avand in vedere riscul de intarziere.


## 03.08.2026 — REZOLVARE cluster "R17 Data_S / termen" (d101): decizie Costin + temei 2022-2025 gasit (OUG 153/2020).

Decizie Costin (a): tool-ul urmeaza VALIDATORUL DUKIntegrator pe AMBELE ramuri - functia lui e sa produca declaratii
ACCEPTATE de ANAF. Neconformitatea aparenta fata de lege ramanea documentata; s-a dovedit ca nici nu exista (vezi b).
=> d101 scadenta: politica lege-vs-validator decisa.

(b) Termenul 2022-2025 verificat AUTORITAR la sursa: NU era conflict lege-vs-validator, ci un act ratat de prima
cercetare (exact ipoteza lui Costin). Mecanismul care a produs 25 iunie pentru anii fiscali 2021-2025 = OUG 153/2020
art.I alin.(13) lit.a): "prin derogare de la prevederile art.41 si 42 din Codul fiscal, termenul pentru depunerea
declaratiei anuale privind impozitul pe profit si plata impozitului... este pana la data de 25 iunie inclusiv a
anului urmator", aplicabil pentru perioada 2021-2025 (art.VI). Publicat in MO nr.817 din 04.09.2020. Deci valoarea
validatorului (iunie pt 2022-2025) e si LEGAL CORECTA - nu exista risc de intarziere. Datoria xfail INCHISA (stearsa
din test_datorie); temeiul in cod corectat de la "OPANAF 206/2025 REDARE" (vag) la OUG 153/2020 art.I alin.(13) lit.a
(2022-2025) si Legea 227/2015 art.42(1) (2026 baza). Sursa: anaf_surse/d101_scadenta_conflict_lege_validator.md.

Ramura 2026 (NU se reinvestigheaza - cerut de Costin): art.42(1) baza = 25 martie dupa incheierea schemei OUG
153/2020 = exact ce cere jar-ul DUK azi. OUG 8/2026 art.6 pct.12 (MO nr.147 din 25 februarie 2026) muta termenul de
baza la 25 iunie PERMANENT de la anul fiscal 2026; DAR declaratia pt fiscal 2026 se depune in 2027, iar ANAF
actualizeaza DUKIntegrator pana atunci - deci NU e conflict de fond, e doar un jar inca neactualizat. Cand jar-ul
trece la iunie pe 2026, probele DUK pe an=2026 (test_imca_d101_duk_valid, test_d101_reconstructie_proba_duk_valid)
pica automat -> semnal clar sa treci _scadenta_2026 de la LL+3 la LL+6. Nu necesita actiune acum.

Tabel final termen depunere D101 per an fiscal: 2021-2025 -> 25 iunie (OUG 153/2020 art.I alin.13 lit.a); 2026 ->
25 martie (baza art.42 azi), 25 iunie cand validatorul adopta OUG 8/2026. Cod: _scadenta_2022 (LL+6 iunie) +
_scadenta_2026 (LL+3 martie), gard de comportament test_scadenta_LL_plus_3_pentru_an_peste_2025 (valori DUK-valide
SI legal corecte pe 2022-2025). Cluster INCHIS.


## 03.08.2026 — Cluster "limita text 75" (d112) — 2 neconformitati de trunchiere reparate.

Verificarea limitei de text 75 in D112 a gasit DOUA campuri gresite fata de structura ANAF (D112 0126_030226):
(A) numeAsig/prenAsig (nume/prenume salariat, structura C(75)) erau doar ESCAPATE, nu si trunchiate (d112.py:271) -
un salariat cu nume >75 caractere producea exact eroarea "sir mai lung de 75 caractere" pe care fix-ul din 29.07 o
elimina in rest; necuprins nici in cod nici in test (fixtura firma_nume_lung n-are salariati). (B) functie_declar
are C(50), nu C(75) - se trunchia la 74 (default text_anaf) in loc de 50 (d112.py:133); o functie de 51-74 caractere
trecea de cod SI de gardul vechi (prag 75) dar depasea limita ANAF de 50. Reparat: numeAsig/prenAsig -> _d112esc(_t(
...)) (trunchiate la 74); functie_declar -> _t(..., 50). Restul (nume_declar/prenume_declar C75, den) erau deja
corecte. Gard nou test_limita_75_asigurat_si_functie_declar_50 (salariat nume 90->74, functie 60->50). Nota: den
ramane trunchiat la 74 desi structura permite 200 - alegere conservatoare (validatorul respinge empiric la 75), nu bug.


## 03.08.2026 — Cluster "nomenclator cod_oblig" (d112) — VERIFICAT CONFORM + gard pe cod_bugetar.

Maparea cod_oblig <-> cod_bugetar din D112 e integral conforma cu nomenclatorul oficial ANAF (structura D112,
Nomenclator 3). Toate 6 codurile emise de add_oblig coincid: 602 (impozit salarii, 5503XXXXXX), 412 (CAS asigurat,
5503XXXXXX), 432 (CASS asigurat, 5503XXXXXX), 480 (CAM, 20470300XX), 458 (CAS suportat angajator art.146(5^9),
5503XXXXXX), 459 (CASS suportat angajator art.168(6^1), 5503XXXXXX). Codurile bugetare toate corecte, inclusiv
distinctul 20470300XX al CAM (480), diferit de 5503XXXXXX al restului. FARA neconformitate. Testul vechi
(test_codurile_de_obligatie_corecte) verifica doar prezenta codOblig 602/412/432/480 ca substring - lipsea gardul pe
cod_bugetar (o inversare a lui ar fi trecut nedetectata). Gard nou test_cod_oblig_pereche_cu_cod_bugetar_corect
paza perechea. (458/459 apar doar la suprataxare part-time - netestate dedicat, dar codurile+bugetarul lor sunt
corecte in cod.)


## 03.08.2026 — Cluster "checksum totalPlata_A" (d205) — VERIFICAT valoarea emisa CONFORMA + aliniere sursa unica (clasa d100).

Verificare la sursa: totalPlata_A din D205 = suma(nrben)+suma(Tcastig)+suma(Tpierd)+suma(T_VB)+suma(T_GAR)+
suma(Tbaza)+suma(Timp), formula EXACTA din ANAF struct D205 (OPANAF 102/2025, l.80-85). Valoarea EMISA in XML era
deja corecta (DUK-valid, proba test_d205_contract_proba_duk_valid). La dividende (tip_venit 08) Tcastig/Tpierd/
T_VB/T_GAR=0, deci checksum = nrben+Tbaza+Timp.

CAPCANA LATENTA (identica cu d100 R11b): res.total_plata_a tinea DOAR total_imp (=Timp), NU checksum-ul emis, iar
build_xml recalcula checksum-ul INDEPENDENT (nu din res). Campul e numit dupa atributul XML (totalPlata_A), deci prin
conventie ar trebui sa TINA valoarea emisa - ca la toate celelalte declaratii (d100/d101/d300/d390/d710 emit
res.total_plata_a). Commit-ul d100 R11b (f26be10) enumerase explicit declaratiile aliniate; d205 LIPSEA din lista -
era ultimul outlier ramas din aceeasi clasa. Un cross-check care ar folosi res.total_plata_a al d205 ca checksum ar fi
primit Timp (8000), nu 58001 - gresit, exact bug-ul pe care d100 il inchisese.

FIX (red->green, PUR INTERN - valoarea EMISA neschimbata, nimic nou pe produs): calcul_d205 calculeaza checksum-ul si
il tine in res.total_plata_a; build_xml il EMITE din res (o singura sursa). Testul care asertase res.total_plata_a==8000
(=Timp, semantica veche gresita) actualizat sa astepte checksum-ul (58001); taxa 8000 ramane verificata via b.imp1.
Gard nou test_total_plata_a_res_egal_checksum_emis: res == header emis == suma componentelor sect_II parsate din XML.

GENERALIZARE: cu d205 inchis, invariantul res.total_plata_a == totalPlata_A emis e acum UNIVERSAL pe toate generatoarele
cu checksum totalPlata_A. Consecinta pentru orice generator viitor: campul-oglinda al unui atribut XML TINE valoarea
emisa, nu o valoare partiala convenabila; build_xml EMITE din res, nu recalculeaza independent (recalculul = capcana).


## 03.08.2026 — Cluster "trunchiere den/adresa" (d205) — NECONFORMITATE reparata (over-trunchiere + respingere), probata DUK.

Verificare la sursa + proba pe validator: campurile text din D205 se emiteau prin text_anaf cu limita DEFAULT
(74/75 car.), dar structura ANAF (OPANAF 102/2025) da limite mult mai mari, confirmate boundary-cu-boundary pe
DUKIntegrator: den C(200) (200 valid / 201 erori), adresa C(1000) (1000 valid / 1001 erori), functie_declar C(50)
(50 valid / 51 erori), den1 beneficiar C(100) (100 valid / 101 erori).

Doua tipuri de defect: (1) den si adresa erau OVER-trunchiate la ~75 = PIERDERE DE DATE - numele firmei peste 75
car. si adresa peste 75 (adresele reale depasesc frecvent 75) taiate silentios, desi ANAF le accepta pana la 200/1000.
Cheia: docstring-ul lui text_anaf (27.07) enumera declaratiile cu respingere empirica >75 (D300/D301/D390/D394/D112)
- D205 NU e in lista, deci blanket-75 nu era probat pentru D205; structura lui (200/1000) castiga (regula TEXTUL
CASTIGA, coroborata cu proba DUK, ca la lectia R17). (2) functie_declar (emis cu default 75) si den1 (emis NETRUNCHIAT)
puteau DEPASI 50/100 -> ANAF le RESPINGEA. Deci pe acelasi camp "text" coexistau over-trunchiere (den/adresa) si
under-/non-trunchiere (functie/den1).

FIX (red->green): limite explicite in build_xml - _t(nume,200), _t(adresa,1000), _t(declarant_functie,50),
_t(b.nume1,100). Proba DUK pe inputuri lungi (den250/adresa1500/functie80/den1-150) -> toate trunchiate la limita
-> XML valid. Garduri: test_trunchiere_den_adresa_functie_den1_la_limitele_anaf (lungimi exacte) +
test_trunchiere_lunga_ramane_duk_valida (proba DUK).

GENERALIZARE: text_anaf are o limita DEFAULT (75) potrivita doar pentru campurile C(75); orice camp cu alta limita
(mai mare SAU mai mica) trebuie sa paseze limita EXPLICIT. Un camp emis fara _t deloc (den1) e la fel de periculos ca
unul over-trunchiat. Consecinta: la fiecare generator, limita fiecarui atribut text = din structura ANAF a ACELUI
formular, verificata pe DUK - nu se presupune 75 uniform (lectia extinde clusterul d112 "limita text 75").


## 03.08.2026 — Cluster "randuri / checksum" (d300) — VERIFICAT CONFORM + gard golden (checksum + excludere 14.1/14.2).

Verificare la sursa + proba DUK: totalPlata_A din D300 = suma(camp 27..124), cu campurile 62 (rd 14.1) si 63
(rd 14.2) ELIMINATE din suma de control (struct D300). In cod rd 14.1/14.2 = R67/R68. Codul face
res.total_plata_a = sum(res.R.values()) si build_xml emite res.total_plata_a - sursa unica, ca celelalte
declaratii (aliniat cu clasa d100). R67/R68 nu-s in nicio allow-list manuala (gardul-clasa "randuri neacceptate"
le ridica ValueError), deci nu pot intra niciodata in sum(res.R): excluderea 62/63 e respectata PRIN CONSTRUCTIE,
nu prin scadere explicita. Probat: total_plata_a == sum(res.R) == 7810 == DUK valid; R67_1/R68_1 manual -> ValueError.

Toate randurile emise (R1_* .. R65_*, R17/R27/R28/R32/R34/R37/R40/R41/R42 computate) cad in campurile 27..124;
niciun rand sub 27 (header/identificare) sau eliminat (62/63) nu intra in suma. Cele 6 clustere d300 anterioare
verificasera maparea rand-cu-rand (cote->randuri, achizitii, ajustari, exigibilitate, pro-rata, taxare inversa)
si DUK-proba pe fiecare valida deja checksum-ul; lipsea DOAR gardul explicit pe formula checksum + pin-ul de
excludere 14.1/14.2. Adaugate acum (fara fix de cod - d300 era deja conform).

OBSERVATIE (datorie deschisa, in AFARA scopului randuri/checksum): adresa si den din D300 se emit prin
text_anaf cu limita DEFAULT (~75). Probat pe DUK: adresa de 152 car. e ACCEPTATA -> 75 e OVER-trunchiere latenta
(pierdere de date), exact clasa reparata la d205 (cluster "trunchiere den/adresa"). Docstring-ul lui text_anaf
(27.07) sustine ca D300 respingea empiric >75 - afirmatie acum INFIRMATA de proba DUK (ca la D205). RECOMANDARE:
un cluster/audit dedicat "limita text" pe TOATE declaratiile din lista 27.07 (D300/D301/D390/D394/D112) - limitele
reale sunt cele din structura fiecarui formular, verificate pe DUK, NU 75 uniform. Nereparata aici: scop = checksum.


## 03.08.2026 — Cluster "checksum totalPlata_A (R28)" (d301) — VERIFICAT CONFORM + gard de legatura (fara fix).

Verificare la sursa + proba DUK: totalPlata_A din D301 = INT(baza1+..+baza5 + tva1+..+tva5), suma de control
definita EXPLICIT de structura (poz.28) si impusa de DUKIntegrator regula R28 (respinge orice alt total - dovedit
numeric in clusterul rollup: total pe sectiunile 1-4 = 6022, R28 cere 12044). res.total_plata_a = sum(tot[t][0]+
tot[t][1] pe toate 5 tipurile) si build_xml emite res.total_plata_a - sursa unica, ca celelalte declaratii
(aliniat clasa d100). Checksum-ul include sectiunea 4.1 PRIN DEFINITIE (serviciul in baza4 SI baza5), fara dubla
impozitare pentru ca TVA-ul DATORAT ramane tva4 (o singura data).

Clusterul rollup (inchis anterior) verificase deja maparea tip->sectiune si gardase golden 12044 pe XML si pe
res.total_plata_a + proba DUK cu toate tipurile. Lipsea DOAR legatura EXPLICITA intr-un singur assert:
res.total_plata_a == totalPlata_A parsat din XML == suma pe toate tipurile. Adaugata (test_checksum_r28_res_egal_
emis_egal_suma_toate_tipurile): prinde atat divergenta res-vs-emis (clasa d100) cat si un tip scapat din suma.
Fara fix de cod - d301 era deja conform si aliniat.


## 03.08.2026 — AUDIT "limita text" pe TOATE declaratiile (datorie deschisa in rularea 3, ceruta de Costin).

CONTEXT: clusterele d205 (trunchiere den/adresa) si d300 (obs. randuri/checksum) au aratat ca limita
GLOBALA de text 74 ("ANAF respinge orice text >75", text_anaf 27.07) e o premisa FALSA. Audit dedicat pe
toate declaratiile: pentru fiecare camp text, limita reala din structura oficiala ANAF (anaf_surse/dNNN_struct*),
PROBATA pe validatorul DUK boundary-cu-boundary.

METODA: 9 investigatii read-only (cate una per declaratie) au mapat campurile text -> C(n) din structura ->
limita din cod. Apoi proba DUK: pentru fiecare camp, o valoare de lungime C(n) e ACCEPTATA iar C(n)+1 e RESPINSA.
REZULTAT: DUK impune EXACT C(n) din structura, pe toate declaratiile - premisa "75 universal" INFIRMATA definitiv.

LIMITE CONFIRMATE DUK (sursa unica core.common.LIMITE_TEXT_ANAF): den/denumire/denR/denP/denO = 200;
adresa/adresaR = 1000; functie_declar/functia_declarant = 50; functie_reprez = 100; nume/prenume_declar(ant),
numeAsig/prenAsig, den_intocmit, calitate_intocmit = 75; den1 (d205 beneficiar) = 100; banca/cont = 50;
telefon = 15; mail = 200. (nr_doc d301: DUK respinge si la C(20) - NU e limita de lungime simpla, are alte reguli
de format; EXCLUS din registru, lasat neatins. d406 = SAF-T, tipuri proprii din XSD - tratat separat.)

TREI CLASE DE DEFECT gasite si reparate (red->green pe test_limita_text_anaf.py):
1. OVER-trunchiere (pierdere de date): den/adresa/nume/prenume taiate la 74 desi ANAF accepta 200/1000/75.
   Denumiri de firma si adrese reale (>74 car.) erau taiate tacit. Reparat: fiecare curge pana la C(n) real.
2. UNDER-trunchiere (RESPINGERE ANAF): functie_declar/functia_declarant taiate la 74 desi C(50) - o functie de
   51-74 car. era emisa si ANAF o RESPINGEA. Reparat: trunchiere la 50.
3. FARA-limita (RESPINGERE ANAF): denO/denP (denumiri partener), mail, banca, cont, telefon, calitate_intocmit
   emise NETRUNCHIATE - o valoare peste C(n) era respinsa. Reparat: _t cu limita din registru.

FIX STRUCTURAL: (a) LIMITE_TEXT_ANAF = registru unic {declaratie: {camp: C(n)}}, sursa oficiala + DUK-confirmat;
(b) common.text_anaf CERE limita explicit (scos default-ul global 74 - un apel fara limita e TypeError, deci o
limita ne-oficiala e imposibila la runtime); (c) toate generatoarele (d100/d101/d112/d205/d300/d301/d390/d394/d710)
paseaza limita din registru. NOTA: d710 NU era in lista ceruta, dar foloseste text_anaf - scoaterea default-ului
l-ar fi rupt; adaugat si probat (identic d100).

GARD DE CLASA (ceruta explicit: "o limita care nu vine din structura devine imposibila"): test_limitele_de_text_
vin_din_registry - scaneaza AST fiecare generator si RESPINGE orice apel _t care nu primeste limita din
LIMITE_TEXT_ANAF (_LIM[...][...]); un literal sau un apel fara limita pica testul. Plus test_generatoarele_
trunchiaza_la_limita_per_camp (plafonare per-camp, fara DB) si test_limite_text_confirmate_pe_duk_boundary
(proba DUK boundary pe campurile materiale - regresie pe validatorul real). Testul vechi blanket-75
(test_atributele_respecta_limita_anaf) rescris pe limite per-camp.

GENERALIZARE / LECTIE: o afirmatie "empirica" pusa intr-un comentariu de cod ("ANAF respinge >75") fara proba
persistenta poate fi FALSA si se propaga ca dogma. Limita fiecarui camp text = din structura FORMULARULUI, probata
pe DUK, tinuta intr-un registru unic; codul nu are voie sa inventeze limite. (Extinde lectia R17: validatorul e
autoritatea; aici validatorul a CONFIRMAT structura, iar comentariul-dogma era gresit.) Datoria "limita text 75"
din predarea rularii 2 e ACHITATA pentru declaratiile pe atribute; d406 (SAF-T) ramane de facut (commit separat).


## 03.08.2026 — AUDIT "limita text" (partea 2): d406 (SAF-T / e-Factura).

d406 nu foloseste atribute XML, ci ELEMENTE SAF-T; limitele nu vin dintr-un struct .txt ci din SCHEMA XSD
oficiala (anaf_surse/d406_schema_anaf.xlsx, foaia SimpleTypes): SAFshorttextType=18, SAFmiddle1textType=35,
SAFmiddle2textType=70, SAFlongtextType=256. Acestea sunt "structura oficiala" pentru SAF-T (echivalentul C(n)),
impuse de validarea XSD.

STARE GASITA: doar 3 campuri din Header (Company/Name 256, StreetName 70, Contact/LastName 70) erau trunchiate
(prin c.text_anaf cu LITERAL). Toate celelalte campuri text erau emise NETRUNCHIATE prin _esc(): Customer/Supplier
Name (70), City (35, Header + parteneri), toate Description-urile (256 - Account/TaxCode/GL/Invoice/Payment/
PaymentLine), PostalCode (18), PaymentMethod (18). Risc: un nume/oras de partener mai lung decat tipul XSD era
respins de validarea SAF-T (exact clasa reparata pe celelalte declaratii).

FIX: d406 adaugat in LIMITE_TEXT_ANAF (chei pe tipul de camp: CompanyName 256, StreetName 70, City 35, PostalCode
18, ContactLastName 70, PartnerName 70, AccountDescription 256, Description 256, PaymentMethod 18). Toate emisiile
text trec acum prin text_anaf cu limita din registru (17 locuri). NOTA de implementare: in d406 aliasul modulului
`c` e SHADOWED de variabile de bucla (c=cont/customer) in MasterFiles, deci nu se putea folosi `c.text_anaf` in
bucle; s-a importat `text_anaf as _t` (uniform cu celelalte generatoare).

GARD: gardul de clasa test_limitele_de_text_vin_din_registry a fost extins sa prinda SI apeluri `.text_anaf`
(Attribute), nu doar `_t` (Name), si acopera acum si d406 (e in LIMITE_TEXT_ANAF). PROBA DUK boundary NU a fost
posibila pe d406: validarea DUK a d406 e xfail(strict) PREEXISTENT ("cont referit absent din chart" - test_smoke_duk)
- nu exista o baza SAF-T DUK-valida de mutat boundary-cu-boundary. Sursa limitelor = tipurile XSD oficiale (autoritare,
enforced de validarea XSD SAF-T); regresia e pazita de gardul de clasa AST + plafonarea la runtime prin text_anaf.
Cand se repara xfail-ul d406 DUK, se poate adauga si proba boundary. Datoria "limita text" e ACHITATA pe toate cele
9 declaratii cerute.


## 03.08.2026 — Cluster "nomenclator tari (HR->CR)" (d390) — NECONFORMITATE reparata (Croatia HR, nu CR), probata DUK.

Verificare la sursa + proba DUK boundary: nomenclatorul de tari din D390 foloseste, pentru fiecare stat UE,
prefixul de TVA (identic cu codul ISO). Codul avea o remapare _TARA_XML = {"HR": "CR"} cu un comentariu care o
declara corecta ("prefixul de TVA HR (Croatia) se scrie CR in nomenclatorul ANAF"). FALS: proba pe DUKIntegrator
(cu OIB croat VALID, ca sa nu intervina eroarea de codO) arata ca tara="CR" e RESPINSA ("eroare atribut: tara:
valoarea 'CR' nu se afla in lista") iar tara="HR" e ACCEPTATA (valid). Deci orice partener croat real producea un
D390 respins de ANAF - neconformitate latenta (niciun test nu folosea un partener croat).

FIX (red->green): _TARA_XML golit ({}); _tara_xml(t) intoarce codul ca atare, deci Croatia se emite HR. Comentariul
corectat. Garduri: test_croatia_emite_HR_nu_CR (tara="HR", nu "CR") + test_croatia_HR_trece_duk (proba DUK).

RESTUL NOMENCLATORULUI verificat (cluster = "nomenclator tari", nu doar HR): setul TARI_UE contine toate cele 26
state UE non-RO (RO = self, exclus) + GB + XI. GB (UK post-Brexit) si XI (Irlanda de Nord) sunt DUK-VALIDE pentru
2026 - validatorul le accepta, deci NU-s bug (R17: validatorul e autoritatea; nu se scot pe presupunerea Brexit
daca DUK le accepta). EL = Grecia (prefix TVA corect). Singura remapare gresita era HR->CR, eliminata.

LECTIE (a treia oara in aceasta campanie, dupa text_anaf-75 si R17): un comentariu care declara o regula "corecta"
NU e o proba. HR->CR suna plauzibil (unele tari au prefix TVA != ISO, ex. EL vs GR) dar era inventat; DUK a aratat
imediat ca HR e corect. Orice remapare de cod (tara, cod bugetar, tip) se verifica pe validator, nu pe comentariu.


## 03.08.2026 — Cluster "tipuri operatiune (pct.215)" (d394) — VERIFICAT + DATORIE ASI (decizie de produs deschisa).

Verificare: TIPURI = (A, L, C, V, AI, LS, AS, ASI, N) coincide EXACT cu setul de tipuri op1 din structura oficiala
D394 (formulele "op1(tip)=X" din anaf_surse/d394_struct_anaf.txt) - pin adaugat (test_tipuri_operatiune_pin_la_
structura_oficiala). Derivarea tip_operatiune(directie, taxare_inversa, tip_partener) (pct.215) e deja testata
(test_tip_respecta_compatibilitatea_cu_partenerul); produce doar L/N/C/V/A (celelalte 4 - AI/LS/AS/ASI - sunt manual).

NECONFORMITATE (probata DUK, lectia "comentariul nu e proba"): pe o baza D394 identica, substituind DOAR valoarea
atributului tip din <op1>, validatorul instalat accepta ca enum 8 tipuri (L/V/A/C/N/LS/AS/AI) dar RESPINGE **ASI**
("eroare atribut: tip: valoarea 'ASI' nu se afla in lista") - identic cu un tip inventat (control "XX"). Deci
structura pdf D394 are ASI (formula op1(tip)=ASI + facturiASI) DAR D394Validator.jar INSTALAT nu-l are in enum:
discrepanta pdf-vs-jar. Un contabil care introduce manual o operatiune tip=ASI produce un D394 RESPINS de ANAF.
ASI e tesut si in TIP_COTA_ZERO, REZ1_FARA_TVA, si logica rezumat (pct.217).

DE CE NU AM CORECTAT (decizie de produs, §2.3 pct.2): scoaterea ASI din TIPURI schimba CE POATE DECLARA
CONTABILUL (setul de tipuri de operatiune). Sunt 3 rezolvari plauzibile, fiecare cu implicatii: (a) scoate ASI
din TIPURI/TIP_COTA_ZERO/REZ1_FARA_TVA (tool-ul urmeaza VALIDATORUL, ca la D101 scadenta - fail-fast pt contabil
via gardul-clasa "tip necunoscut"); (b) remapeaza operatiunile "achizitii scutite intracomunitare" pe AI sau AS;
(c) validatorul instalat e o versiune veche si ASI e valid intr-o versiune noua OPANAF - de confirmat la sursa.
Alegerea cere Costin + confirmarea versiunii oficiale D394. Am consemnat cu gard anti-regresie
(test_asi_respins_de_validatorul_instalat_DATORIE): daca validatorul ajunge sa accepte ASI, testul pica si anunta.

INPUT CERUT (Costin): pentru versiunea curenta a validatorului D394, ASI e un tip valid sau scos? Daca scos, pe ce
tip merg achizitiile scutite intracomunitare? (Acelasi tipar ca datoria codPR gaze naturale lit.l din acelasi modul.)


## 03.08.2026 — ASI (d394): REZOLVARE INVESTIGATIE (jar vs pdf) — pdf-ul e invechit, jar-ul e curent.

La cererea lui Costin (verifica versiunea jar vs data pdf inainte de decizie), am stabilit:

1. **Jar-ul instalat = versiunea CURENTA ANAF, byte-identic.** D394Validator.jar instalat (md5 1ce55b54e2c4ec969ce7a827a12af986, 697332 B) e IDENTIC cu cel descarcat acum de la ANAF (update5/D394_31/D394Validator.jar). Versiunea curenta din D394IstoriaVersiunilor: **J8.0.2 (17-Sep-2025)**. Jar-ul NU e invechit.

2. **Pdf-ul din anaf_surse e din 2020.** structD394_02092020.pdf = versiunea **J4.0.0 (02-Sep-2020, OPANAF 3281/2020)**. Intre timp: J6.0.0 (OPANAF 77/2022), J7.0.0 (feb 2025 caen), J8.0.0/8.0.2 (sep 2025). Pdf-ul e invechit cu ~5 ani / 4 versiuni majore.

3. **ASI a fost SCOS din D394.** In toate seturile de parametri ale validatorului instalat (Parameters_v3..v7) "ASI" apare de 0 ori; validatorul are 8 tipuri: A, L, C, V, AI, LS, AS, N. Proba DUK (pe jar-ul curent) confirma: ASI respins, restul 8 acceptate. Deci codul (TIPURI cu 9 tipuri) urmeaza pdf-ul 2020, invechit.

4. **Semantica 2020 (din pdf J4):** AS = "achizitii regim special catre pers care aplica sistemul NORMAL de TVA"; ASI = "achizitii regim special catre pers care aplica sistemul de TVA LA INCASARE". AS si ASI erau o PERECHE, diferentiate de sistemul de TVA al partenerului. In J8 a ramas doar AS.

CONCLUZIE per arborele de decizie al lui Costin: jar CURENT + respinge ASI => **pdf-ul e invechit**. ASI trebuie SCOS din TIPURI/TIP_COTA_ZERO/REZ1_FARA_TVA (aliniere la validatorul curent, ca la D101 - tool-ul urmeaza validatorul).

MAPARE (unde merg operatiunile fost-ASI): NU am putut confirma dintr-un document de structura ANAF CURENT - structurile pdf postate public sunt versiuni vechi (structura_D394.pdf si _v200.pdf sunt din 2013, 4 tipuri; structD394_02092020 e J4). Specificatia curenta (J8) e incorporata DOAR in jar, care nu documenteaza in text unde merg fost-ASI. Evidenta 2020 (AS/ASI = pereche normal-vs-incasare, ASI eliminat) INDICA PUTERNIC ca achizitiile regim special se consolideaza sub AS (distinctia dupa sistemul de TVA al partenerului a fost abandonata), dar NU e confirmat de un text oficial curent. NU am schimbat TIPURI (instructiune Costin: raporteaza intai; nu ghici remaparea).

RAMANE PENTRU COSTIN: (a) greenlight pentru scoaterea ASI din TIPURI (aliniere validator - clar corecta); (b) confirmarea ca fost-ASI -> AS (achizitii regim special, indiferent de sistemul de TVA al partenerului) - sau o alta destinatie, de confirmat la sursa OPANAF 77/2022. Gardul test_asi_respins_de_validatorul_instalat_DATORIE ramane pana la rezolvare.


## 03.08.2026 — ASI (d394) REZOLVAT cu greenlight Costin: scos din cod + OPANAF 77/2022 confirmat + audit surse.

GREENLIGHT PUNCT 1 (scoatere ASI). ASI scos din TIPURI (acum 8 tipuri: A,L,C,V,AI,LS,AS,N), TIP_COTA_ZERO
(LS,AS,N,V), REZ1_FARA_TVA (V,LS,AS,N) + comentariile pct.217. Aliniere la D394Validator instalat (J8, care il
respinge), acelasi tipar ca la D101. Gardul fost-datorie test_asi_respins... transformat in GARD INVERS
(test_asi_ramane_scos_gard_invers): daca o versiune noua de validator ajunge sa ACCEPTE din nou ASI, testul PICA
si anunta. Pin-ul TIPURI mutat de pe pdf-ul 2020 invechit pe setul validatorului curent (test_TIPURI_e_setul_
validatorului_curent).

PUNCT 2 CONFIRMAT LA SURSA (Monitorul Oficial, nu pdf-uri invechite). Descarcat OPANAF 77/2022 (MO nr.95/
31.01.2022), salvat anaf_surse/opanaf_77_2022.pdf + .txt cu sha256 (86524aa921c226fafb417c4d494b112aebbc3e6dc6b91
ca228486b4b1bb3b22c). Textul CONFIRMA: 8 tipuri, ASI absent; AS = "achizitii regim special de la persoane care
aplica regimul special pentru agentiile de turism, bunurile second-hand, opere de arta, obiecte de colectie si
antichitati". Distinctia 2020 dupa sistemul de TVA al partenerului (AS=normal / ASI=la incasare) a fost ELIMINATA
=> fost-ASI -> AS. Remaparea NU mai e datorie, e confirmata.

DATE EXISTENTE (cerinta Costin: sa nu dispara tacit): op1.tip D394 NU e persistat in DB - nu exista tabela
d394_operatiuni; tipurile automate sunt DERIVATE din facturi (tip_operatiune produce doar L/N/C/V/A, niciodata
ASI), iar operatiunile manuale sunt pasate la generare (cheie_manual), nestocate. Nicio coloana din schema
(tenant_template.sql) nu tine op1.tip; nicio tabela de declaratii XML salvate. DECI NU EXISTA DATE ASI de migrat
la niciun tenant. Protectie forward: [GARD CLASA] din calcul_d394 respinge orice tip manual necunoscut (deci
inclusiv ASI) cu eroare vizibila - fail-fast, nu drop tacit.

PUNCT 3 - inlocuire pdf invechit + audit surse. d394_struct_anaf.txt (2020/J4) marcat prominent INVECHIT in antet,
cu trimitere la opanaf_77_2022 ca sursa curenta pentru tipuri. AUDIT anaf_surse/ dupa alte surse vechi cu acelasi
risc: **d301_struct_anaf.txt = 2013 (D301_A1.0.0)** si **d390_struct_anaf.txt = 2020 (OPANAF 705/2020, v3; validator
curent J4.1.2)** sunt si ele VECHI. Diferenta fata de d394: codul d301 (checksum R28, rollup) si d390 (nomenclator
tari HR->CR, tipuri IC) a fost deja VALIDATOR-VERIFICAT in clusterele din aceasta campanie, deci nu au produs bug
activ din structura veche. Restul (d100/d101/d112/d205/d300) au surse 2025/2026, curente. DATORIE NOUA (follow-up,
non-blocanta): reimprospateaza structurile d301 si d390 de la ANAF si re-verifica listele lor de tipuri/nomenclatoare
pe validatorul curent, ca la d394 - inainte ca vreo regula ne-verificata din structura veche sa fie folosita ca temei.

LECTIE: o structura pdf invechita in anaf_surse/ e o mina - a produs bug-ul ASI. Regula: sursa de tipuri/nomenclatoare
= validatorul INSTALAT (verifica-i versiunea vs versiunea curenta ANAF) + ordinul din Monitorul Oficial, NU un pdf de
structura vechi. Marcheaza pdf-urile vechi INVECHIT ca sa nu fie folosite orb.


## 04.08.2026 — Cluster "tip_partener" (d394) — VERIFICAT CONFORM (fara fix).

clasifica_partener(cui) mapeaza cele 4 categorii oficiale de tip_partener (pct.216, sursa curenta OPANAF 77/2022):
1 = persoana impozabila inregistrata in scopuri de TVA in RO (prefix RO sau sir numeric); 2 = neinregistrata
(fara CUI sau CUI ne-numeric); 3 = stabilita in alt stat membru UE (prefix de stat membru din _TARI_UE); 4 =
nestabilita in UE (alt prefix alfabetic). Probat: 5 cazuri de clasificare corecte (inclusiv HR->3 dupa fixul de
nomenclator din clusterul HR->CR) + proba DUK (validatorul accepta tip_partener UE/non-UE).

NUANTA DE DESIGN (conform, nu bug): cui_ro e o functie de NORMALIZARE (scoate prefixul RO si separatorii), NU de
validare - nu verifica checksum-ul CUI-ului RO. Deci un CUI RO invalid (ex. RO99999999) da tip_partener=1, iar
D394Validator il respinge la depunere (regula R218.2: "daca tip_partener=1 atunci cuiP valid") - fail-fast, cu
eroare vizibila, nu drop tacit. Aceasta e alegerea CORECTA: a reclasifica un CUI RO invalid la tip 2 ar declara
GRESIT un partener inregistrat ca neinregistrat (o greseala de continut), pe cand tip 1 + respingere DUK forteaza
corectarea CUI-ului. Ramura UE/non-UE se sprijina pe _TARI_UE, deja verificat pe validator in clusterul nomenclator
tari (HR->CR). Fara fix - conform. Gard consolidat: test_tip_partener_clasificare_pct216.


## 04.08.2026 — Cluster "rezumat1 campuri complete" (d394) — VERIFICAT cazurile comune + NECONFORMITATE ACTIVA (operatiuni N neinreg).

VERIFICARE (sursa curenta = validatorul RULAT J8, nu pdf-ul 2020 invechit): pentru partenerii INREGISTRATI (RO,
tip_partener=1) si STRAINI (UE tip 3 / non-UE tip 4), setul de campuri emis in <rezumat1> e COMPLET si corect.
Codul emite, 0-umplut, campurile cerute de rez1_tipuri(tip_partener, cota): facturi+baza pe fiecare tip cerut,
tva DOAR pentru A/L/C/AI (R232.2: taxare inversa are TVA la beneficiar, LS/AS sunt regim special). Probat pe DUK
(J8): o declaratie L(tp1)+A(tp1)+L(tp3) e VALIDA. rez1_tipuri e deja unit-testat pe reguli (R38/R41/R49/R53/R56/R591).

NECONFORMITATE ACTIVA (probata DUK): operatiunile N (achizitii de la parteneri NEINREGISTRATI, tip_partener=2)
sunt produse AUTOMAT - orice factura de achizitie FARA CUI de furnizor da tip_operatiune(primita, neinreg)=N, iar
pull() include achizitiile fara CUI (cui=""). DAR validatorul CURENT (J8) RESPINGE o astfel de declaratie:
codul NU emite atributele tehnice cerute de structura pentru tip 2 / N:
 - op1.tip_document (pct.228, N(1): 1=facturi/2=borderouri/3=file carnet/4=contracte/5=alte) - OBLIGATORIU pt tp2+N;
 - op1.tip_N (pct.229, 1=bunuri/2=servicii) - OBLIGATORIU pt tip in (V,C,N) + tip_partener in (1,2);
 - rezumat1.document_N (pct.60, = op1.tip_document) - <>null pt tp2+cota0;
iar rezumat1 emite facturiLS/bazaLS pe care R41.2/R42.2 le INTERZIC cand document_N<>1. Deci un tenant cu achizitii
de la furnizori neinregistrati produce un D394 RESPINS de ANAF - BUG ACTIV, nu latent (spre deosebire de ASI).

DE CE NU AM CORECTAT unilateral (DECIZIE DE PRODUS + continut declarat): pentru calea AUTO (N dintr-o factura),
tip_document=1 (facturi) si document_N=1 sunt clare, DAR tip_N (bunuri vs servicii) e CONTINUT DECLARAT - a-l
default gresit declara servicii ca bunuri (sau invers). Suportul pentru tip_document 2-5 (borderouri/file carnet/
contracte/alte) cere EXTINDEREA contractului (facturi/manual nu au campul). Optiuni (Costin):
 (a) implementeaza N auto: tip_document=1, document_N=1, tip_N derivat din natura facturii (bunuri/servicii) +
     datorie pentru tip_document 2-5 manual;
 (b) EXCLUDE N din declaratie cu AVERTISMENT VIZIBIL (D394 ramane submitabil pentru restul; contabilul trateaza
     achizitiile de la neinregistrati separat) - cheia: sa NU produca tacit o declaratie respinsa de ANAF;
 (c) blocheaza generarea cand exista N.
Recomandare: (b) ca protectie imediata (fail-visible) + (a) ca implementare completa. Gard anti-regresie +
datorie: test_rezumat1_tp2_neinreg_N_respins_de_validator_DATORIE (cand J8 accepta N, se aprinde si anunta).

INPUT CERUT (Costin): pentru achizitiile de la parteneri neinregistrati (tip 2 / N) - implementam suportul auto
(a) sau excludem cu avertisment (b) pana la o implementare completa? Si de unde vine tip_N (bunuri/servicii)?


## 04.08.2026 — Operatiuni N (d394): EXECUTAT approach (b) - excludere cu avertisment vizibil (decizie Costin).

Costin a ales approach (b) (nu a/c): tip_N e continut declarat, nu derivabil - un default gresit ar produce o
declaratie ACCEPTATA dar FALSA (mai rau decat una respinsa); (c) blocarea e disproportionata (un tenant cu o
singura achizitie de la neinregistrat n-ar mai putea depune deloc).

IMPLEMENTAT in calcul_d394: operatiunile N (auto din facturi fara CUI SI manuale) se EXCLUD din op1/rezumat1, cu
un AVERTISMENT VIZIBIL (in res.avertismente -> UI + fluxul de generare, nu doar log) care NUMESTE furnizorii si
sumele excluse ("ATENTIE: N operatiune(i) N EXCLUSE ... Furnizori/sume: <nume> (baza <x> lei); ..."). Restul
declaratiei ramane VALID pe validatorul curent (probat DUK). Nu tacit, nu declaratie falsa, nu blocare totala.

Garduri: test_operatiuni_N_excluse_cu_avertisment_vizibil (N absent din XML + avertisment numeste furnizor+suma +
D394 valid); test_N_ar_fi_respins_de_validator_daca_emis_GARD_INVERS (anti-regresie: injecteaza op1 N -> J8 il
respinge; ramane pana la implementarea completa, cand pica si anunta).

DATORIE (in GARZI 04.08) pt implementarea COMPLETA (approach a, campanie proprie dupa decizia UI): op1.tip_N
(camp nou contabil, UI bunuri/servicii), op1.tip_document (auto=1 facturi; 2-5 = extindere contract), rezumat1.
document_N. Cand se implementeaza, se scoate excluderea si se aprinde gardul invers.


## 04.08.2026 — Cluster "nomenclator codPR (art.331)" (d394) — VERIFICAT CONFORM pe validator + lit.l gaze deja rezolvat.

Nomenclatorul d394.CODPR mapeaza categoriile de taxare inversa (art.331 alin.2) in codurile op11: deseuri 22,
masa_lemnoasa 23, certificate_emisii 24, energie 25, certificate_verzi 26, cladiri_terenuri 27, aur 28, telefoane
29, circuite_integrate 30, console_tablete 31, gaze_naturale 36; iar cerealele folosesc subcodul NC (1001..121291,
codul 21 e centralizator - la op11 se pune subcodul). Comentariul citeaza Ghid_D394_2016.pdf (sursa INVECHITA, 2016).

VERIFICARE pe AUTORITATEA CURENTA (validatorul J8, nu ghidul 2016 - lectia ASI): probat DUK cod-cu-cod (taxare
inversa C cu fiecare categorie) - TOATE codurile CODPR (22-31, 36) + TOATE subcodurile cereale (1001, 1002, 1003,
1004, 1005, 1201, 1205, 120400, 120600, 121291, 10086000) sunt ACCEPTATE de validator. Nomenclatorul e conform.
Sursa comentata e veche, dar codurile-s validator-confirmate (acelasi tipar ca ASI/limita-text: nu te bazezi pe
pdf-ul vechi, probezi pe validator).

GAZE_NATURALE codPR 36 - fostul BLOCAJ al datoriei lit.l (art.331 alin.2 lit.l, gaze catre comerciant persoana
impozabila, introdusa de Legea 296/2020) - e acum CONFIRMAT valid pe J8. Datoria lit.l a fost REZOLVATA in commit
6675f19 ("CAMPANIE datorii B"): gaze_naturale adaugat in motor taxare_inversa.CATEGORII (lit:"l") + d394.CODPR
(36), iar xfail-ul test_datorie_gaze_naturale_taxare_inversa_art331_lit_l inchis (nu mai exista). Aceasta verificare
CONFIRMA independent, pe validatorul curent, ca 36 e codPR-ul corect - inchide definitiv intrebarea "codPR gaze
neconfirmat la sursa".

OBSERVATIE (doc-staleness, follow-up): bifa "taxare inversa | d394" din Inventar A e STALE - inca descrie gaze ca
LIPSA + "DATORIE xfail(strict) gaze in test_datorie" si refera test_datorie_gaze_naturale_taxare_inversa_art331_lit_l
care NU mai exista (rezolvat in 6675f19). De actualizat separat (gardul anti-stale o tolereaza prin fallback pe fisier).
Gard nou pentru clusterul curent: test_codpr_valide_pe_validatorul_curent (pineaza CODPR pe validator, nu pe Ghid 2016).


## 04.08.2026 — Cluster "totalPlata_A (R17)" (d394) — VERIFICAT CONFORM + gard sursa-unica/DUK (fara fix).

totalPlata_A din D394 = Suma(informatii.nrCui1..4) + Suma(rezumat2.baza[L+A+AI]) - suma de control impusa de
regula R17 a validatorului. Formula e cea CORECTA (comentariul d394.py:18 noteaza ca o formula VECHE, inventata,
fusese reparata). res.total_plata_a se calculeaza in calcul_d394 si build_xml il EMITE din res - SURSA UNICA,
aliniat la conventia tuturor declaratiilor cu checksum (clasa d100/d205/d300/d301).

VERIFICARE pe AUTORITATEA CURENTA (validatorul J8): probat direct - valoarea corecta (3002 pe un decont RO emisa+
primita) e R17-VALIDA; o valoare GRESITA (+999) e RESPINSA cu mesajul R17 ("atributul totalPlata_A trebuie sa fie
egal cu Suma(nrCui) + Suma(baza)"). Deci formula codului = exact ce impune R17, iar checksum-ul e pazit de validator.
Testul existent test_total_plata_a_dupa_formula_oficiala era TAUTOLOGIC (recalcula aceeasi formula in test); gardul
nou test_totalPlata_A_R17_sursa_unica_si_probat_pe_validator leaga res==emis (invariant clasa-d100) SI probeaza R17
pe validator (nu doar reasserteaza formula). Fara fix de cod - conform.

NOTA: cu acest cluster, TOATE clusterele d394 din secventa sunt inchise (tip_partener, rezumat1, nomenclator codPR,
totalPlata_A + cele anterioare). Urmeaza d406 (SAF-T) si d710. Datorii d394 ramase: suport complet N (approach a,
campanie proprie - GARZI 04.08).


## 04.08.2026 — Cluster "plan conturi pe norma" (d406) — VERIFICAT + REPARAT drop tacit al conturilor excluse.

D406 (SAF-T) emite planul de conturi in MasterFiles/GeneralLedgerAccounts. pull() citeste plan_conturi si il
FILTREAZA pe nomenclatorul OFICIAL al normei contabile a firmei: oficial = plan_oficial(baza_contabila), din
anaf_surse/d406_nomenclatoare_anaf.properties (cheia normei: plan_conturi_bal_soc_com pt 'A', plan_conturi_ONG pt
ONG, etc.). Conturile din planul firmei care NU sunt in nomenclatorul normei se EXCLUD - ANAF le respinge ("ID-ul
contului [731] trebuie sa se gaseasca in planul de conturi"; bug istoric: 731-738 venituri ONG erau in planul
default al tuturor firmelor). AccountID emis = sintetic (401.05 -> 401; validatorul cere numar intreg). Filtrarea e
CORECTA (pe nomenclatorul oficial, nu pe o lista scrisa de noi) - test_plan_oficial_citeste_nomenclatorul_norma_A
confirma ca nomenclatorul e citit (>100 conturi pt 'A').

NECONFORMITATE (drop TACIT): conturile excluse erau colectate in `strain` DAR pull() nici nu le returna (return cu
8 elemente, fara strain) - deci se pierdeau complet. Un cont cu SOLD care nu apartine normei disparea din SAF-T
FARA ca contabilul sa stie (acelasi tipar ca operatiunile N in d394). REPARAT: pull returneaza strain (9 elemente);
genereaza il despacheteaza si, daca e nevid, INSEREAZA la pozitia 0 in res.avertismente un mesaj care NUMESTE
conturile excluse + norma ("ATENTIE: N cont(uri) EXCLUS(e) din D406 - nu apartin normei ... : 731, ..."). Aliniat
cu decizia Costin 04.08 (approach b la N): exclus dar VIZIBIL, nu tacit. Gard DB: test_conturi_straine_de_norma_
sunt_semnalate_nu_excluse_tacit (firma 'A' cu cont 731 -> exclus + numit).

Corectat si o eroare de inventar: randul avea fisiere=test_limita_text_anaf.py (gresit); testele plan-conturi sunt
in test_d406.py - corectat.


## 04.08.2026 — Cluster "UoM UN/ECE" (d406) — VERIFICAT CONFORM pe validatorul SAF-T (fara fix).

d406 emite UnitOfMeasure ca cod UN/ECE Recommendation 20 (nomenclatorul international de unitati), NU unitatile
romanesti. UOM_UNECE mapeaza unitatea interna (buc/kg/mp/...) in codul UN/ECE (H87/KGM/MTK/...); default UOM_IMPLICIT
= H87 (bucata); uom_unece() intoarce (cod, gasit?) - la necunoscut (H87, False), semnaland apelantului ca s-a folosit
implicitul (mai bine o unitate DECLARATA decat un XML respins).

VERIFICARE pe AUTORITATEA CURENTA: (1) XSD saft.xsd defineste UnitOfMeasure = SAFcodeType (cod generic cu lungime,
NU enumerare - deci lista valida e in VALIDATOR, nu in XSD); (2) codurile-tinta din UOM_UNECE sunt validator-
confirmate - comentariul din cod noteaza proba 15.07.2026 (BUC respins "valoarea nu se afla in lista"), iar acum am
CONFIRMAT independent prin EXTRACTIE din D406Validator.jar (/opt/duk/saft/val/...): codurile distinctive H87, KGM,
GRM, TNE, LTR, MLT, MTR, CMT, KMT, MTK, MTQ, HUR, KWH, MWH sunt TOATE prezente ca string in jar; BUC = 0 aparitii
(absent, confirmand bug-ul istoric "BUC hardcodat -> respins"). Codurile scurte DAY/MON/ANN/SET/PR sunt coduri UN/ECE
Rec.20 standard (verificarea prin grep e neconcludenta pe ele din cauza substring-urilor, dar sunt nomenclator-standard).

Fara fix - conform. Gard nou test_uom_unece_mapare_coduri_valide (mapare + default H87 + semnal la necunoscut +
absenta BUC + format cod UN/ECE). Corectat inventarul (fisiere test_limita_text -> test_d406, ca la plan conturi).


## 04.08.2026 — Reimprospatare surse invechite: d301 (tip_valuta) — VERIFICAT pe validator + DECIZIE HRK deschisa.

CAMPANIE "reimprospatarea surselor invechite" (metoda jar-vs-pdf ca la D394/ASI). Auditul anaf_surse/ a gasit
d301_struct_anaf.txt = structura 2013 (D301_A1.0.0, 28.01.2013), invechita.

CONFRUNTARE 3 coloane (tip_valuta), sursa = proba DUK boundary pe D301Validator.jar instalat (D301_9):
- VALIDATOR (probat DUK 04.08, fiecare cod ISO trecut prin DUKIntegrator): 20 valute =
  AUD BGN CAD CHF CZK DKK EGP EUR GBP HRK HUF JPY MDL NOK PLN RON SEK TRY USD XDR.
- COD (core/d301.py VALUTE): 19 valute (= EXACT pdf-ul 2013, fara HRK).
- PDF 2013: 19 valute (identic cu codul).

Rezultat:
- TIPARUL ASI (cod care urmeaza un document mort, cu valori RESPINSE de validator): NU apare. Toate 19 din VALUTE
  sunt validator-acceptate. Niciun cod mort de scos.
- ACOPERIRE LIPSA: HRK (kuna croata) - validatorul o ACCEPTA, codul o RESPINGE (erori_generare "Valuta neacceptata").
  Adaugata de ANAF post-2013 (Croatia in UE din iul.2013; HRK folosit pana la trecerea la EUR 01.01.2023).
  Efect: un D301 cu operatiune in HRK (achizitie istorica / rectificare din Croatia pre-2023) e blocat de codul
  nostru desi ANAF il accepta - cod mai STRICT decat validatorul.

ACTIUNI FACUTE (neutre, nu schimba ce declara contabilul):
- pdf-ul 2013 marcat INVECHIT in antet; docstring d301.py noteaza ancorarea pe validator, nu pe pdf.
- comentariul VALUTE mutat de pe pdf pe validatorul instalat (D301_9, proba DUK 04.08).
- gard nou test_valute_ancorate_pe_validator_nu_pe_pdf_2013: VALUTE ⊆ set-validator (anti-ASI, imposibil cod mort)
  + delta = {HRK} pinuit; test_valute_snapshot_validator_confirmat_pe_duk (proba DUK vie: HRK acceptat, ZZZ respins).

DECIZIE DE PRODUS DESCHISA (Costin): se adauga HRK in VALUTE (aliniere la validator, permite declararea operatiunilor
istorice/rectificari in kuna croata)? Recomandare Code: DA - aliniaza codul la validatorul ANAF (autoritatea, R17),
inlatura o respingere falsa; HRK e valuta legacy (fara operatiuni noi), risc minim. Se adauga cu 1 linie + reprobare
DUK + actualizarea delta din gard. Blocat pana la greenlight fiindca schimba nomenclatorul de valute declarabil (§5).


## 04.08.2026 — Reimprospatare surse invechite: d390 (TARI_UE + TIPURI) — VERIFICAT CONFORM pe validator (fara fix).

CAMPANIE "reimprospatarea surselor invechite" (metoda jar-vs-pdf). Auditul anaf_surse/ a gasit
d390_struct_anaf.txt = derivarea de structura 2020 (OPANAF 705/11.03.2020), invechita.

CONFRUNTARE pe validatorul INSTALAT D390_11 (proba DUK boundary 04.08.2026):
- TARI_UE (cod, 28 tari): fiecare tara recunoscuta de validator (regula R24.1 'algoritmul specific X').
  Niciun cod mort (tiparul ASI NU apare). GB (post-Brexit) si XI recunoscute pentru 2026 (reconfirmat pe jar-ul
  instalat, nu pe comentariul vechi). Grecia = EL (GR respins), Croatia = HR (CR respins - reconfirmare a fixului
  HR->CR din 03.08). Candidati exteriori testati (GR, CR, microstate MC/SM/AD/LI/VA, Crown IM/JE/GG) - TOTI
  respinsi 'nu se afla in lista' -> FARA gap de acoperire.
- TIPURI (cod, 6): L/T/P/R (emisa) + A/S (primita) toate VALID pe validator; fake (Z/X/ASI) respinse.

REZULTAT: d390 NU diverge de validatorul curent - spre deosebire de d301 (unde validatorul avea HRK in plus).
Nicio reparatie, nicio decizie de produs.

FACUT:
- pdf 2020 marcat INVECHIT in antet (nomenclatoare -> validator; OPANAF 705/2020 ramane temeiul LEGAL citat).
- comentariu de ancorare pe validator langa TARI_UE/TIPURI in d390.py.
- gard nou test_nomenclatoare_d390_ancorate_pe_validator_nu_pe_pdf_2020 (TARI_UE + TIPURI == set-validator,
  EL nu GR, HR nu CR) + test_d390_snapshot_validator_confirmat_pe_duk (proba DUK vie: GB recunoscut, CR respins).


## 04.08.2026 — Reimprospatare surse (generalizare): GARD DE CLASA "nomenclatoarele ancorate pe validator".

Dupa d301 si d390, generalizare pe TOATE sursele din anaf_surse/ (pasul 6).

ENUMERARE surse de STRUCTURA pre-2024 folosite ca temei activ (an antet / INVECHIT / citate in cod):
- d301_struct (2013) - INVECHIT, citat d301.py. d390_struct (2020) - INVECHIT. d394_struct (2020) - INVECHIT,
  citat d394.py (ASI, 03.08). Toate cele pre-2024 CITATE sunt deja INVECHIT.
- d406_nomenclatoare.properties (~2011) - citat d406.py (plan_oficial); verificat pe norma 04.08.
  d406_schema.xlsx (2026) - curent. d100_struct (2026), d101_struct (2024) - curente.
  d112/d205/d300_struct - NEcitate prin stem (dormante).

GARD DE CLASA ales: "fiecare pin de nomenclator e ANCORAT PE VALIDATOR, nu pe document"
(core/test_nomenclatoare_ancorate.py), NU un prag de vechime de N ani. MOTIV (cerut: alege forma mai puternica
si spune de ce): vechimea NU e riscul - un nomenclator din 2013 poate fi curent (D301 tipuri 1-5), unul din 2025
poate fi depasit maine. Riscul real e DIVERGENTA fata de validatorul instalat, exact ce au ascuns ASI (pdf D394
2020: 9 tipuri incl. ASI; validatorul J8 il respinsese) si HRK (pdf D301 2013: 19 valute; validatorul D301_9
accepta 20). Un prag de N ani ar rata AMBELE - nu erau despre varsta, ci despre ce accepta validatorul azi.

Gardul DESCOPERA (AST) constantele de forma nomenclator (set/tuple/frozenset de coduri scurte alfanumerice
majuscule) in generatoare si CERE ca fiecare sa fie in registrul ANCORE, cu un test care atinge validatorul
(proba DUK) sau specificatia oficiala masinala (schema_anaf, unde DUK e xfail - d406). 9 nomenclatoare
descoperite si ancorate (d301.VALUTE; d390.TARI_UE/TIPURI; d394.TIPURI/TIP_COTA_ZERO/REZ1_FARA_TVA/OP1_CU_TVA/
_TARI_UE; d406._UE_NON_RO). Un nomenclator nou fara ancora pica gardul (RED probat) - forteaza proba pe
validatorul instalat, nu copierea unui pdf.


## 04.08.2026 — HRK in D301 (VALUTE): EXECUTAT cu greenlight Costin (aliniere la validator).

Decizia deschisa in intrarea "Reimprospatare surse invechite: d301" a fost aprobata de Costin: DA pentru HRK.
Motiv (Costin): codul era mai STRICT decat validatorul -> respingere FALSA a unei declaratii valide. HRK apare
doar la rectificari/achizitii istorice pre-2023 (Croatia -> EUR 01.01.2023), dar cand apare, contabilul e blocat
fara temei. Adaugarea nu creeaza risc: validatorul o accepta.

EXECUTAT: "HRK" adaugat in core.d301.VALUTE (acum 20 valute = EXACT setul validatorului D301_9). Reprobat pe DUK
04.08.2026: un D301 cu tip_valuta=HRK trece poarta codului (erori_generare nu-l mai respinge) SI e DUK-valid
(stare "valid", tip_valuta nerespins). Gardul test_valute_ancorate_pe_validator_nu_pe_pdf_2013 actualizat: delta
cod-vs-validator e acum VID (VALUTE == VALIDATOR_D301), fara cod mort si fara gap de acoperire.


## 04.08.2026 — Verificare temei la MO: OPANAF 705/2020 (d390) si 592/2016 (d301) - tiparul "temei neverificat".

Costin (04.08): temeiurile OPANAF 705/2020 (d390) si 592/2016 (d301) erau PRESUPUSE in vigoare, nerecitite la MO -
exact tiparul de temei neverificat. Validatorul confirma valorile, dar actul citat trebuie confirmat la sursa.

VERIFICAT (cautari MO / Portal Legislativ / ANAF, 04.08.2026):

- OPANAF 592/2016 (D301, decont special TVA): IN VIGOARE, neabrogat. MODIFICAT/COMPLETAT prin OPANAF 779/2024
  (MO 374/22.04.2024): a introdus checkbox-ul "Declaratie rectificativa ca urmare a unei notificari de conformare"
  la formularele 301, 101, 101 Grup si 710, plus regula ca la rectificare TOATE sectiunile se completeaza cu date
  valide la momentul declararii. NU a atins nomenclatorul de valute (tip_valuta) sau tipurile de operatiune 1-5
  (confirmate separat pe validatorul instalat D301_9). Temei d301.py actualizat: "592/2016 modificat prin 779/2024".

- OPANAF 705/2020 (D390, recapitulativa VIES): IN VIGOARE (MO 217/17.03.2020). Nu s-a gasit act de abrogare sau
  ordin de inlocuire in 2021-2026 (cautari MO/Portal Legislativ + lege5/portaluri il arata ca act curent; alte
  forme au primit ordine noi - D205/D207 OPANAF 102/2025, D212 OPANAF 7015/2024 - dar NU D390). Temei d390.py
  actualizat cu data verificarii.

LIMITA verificarii (ce nu am putut confirma definitiv): PDF-ul oficial 779/2024 pe static.anaf.ro e scanat
(imagine), neextractibil ca text; pagina Portal Legislativ pt 705/2020 nu afiseaza istoricul de amendamente in
excerpt. Confirmarea se sprijina pe surse secundare (Universul Juridic, noulcodfiscal, lege5, contabilul.manager)
+ pe faptul ca validatorul INSTALAT (D301_9, D390_11 din versiuni.xml oficial 15.07.2026) reflecta regulile
curente si codul se potriveste cu el. Absenta unui ordin de inlocuire pt 705/2020 = "negasit", nu "inexistent".

DATORIE (non-blocanta, follow-up): OPANAF 779/2024 a adaugat la D301 (si D101/D710) checkbox-ul de rectificare
din notificare de conformare. Codul NU emite acest flag. E OPTIONAL - un D301 fara el e DUK-valid (dovedit:
D301 cu HRK trece "valid" 04.08), deci nu blocheaza depunerea; se adauga la primul caz real de rectificare din
notificare de conformare. Vezi si d_recN la d710 (tipar similar de flag de rectificare versionat).

Surse: legislatie.just.ro/Public/DetaliiDocument/281972 (OPANAF 779/2024); universuljuridic.ro (rezumat 779/2024);
legislatie.just.ro/Public/DetaliiDocument/223871 (OPANAF 705/2020); noulcodfiscal.ro/.../ordin-opanaf-779-2024.


## 04.08.2026 — C5 EXECUTAT: migrare tichete culturale pe tenanti reali.

Campania "implementarile ramase", punctul 1. Dump de siguranta luat inainte
(backup_pre_migrari_20260804_1312.sql.gz, 322 CREATE TABLE, valid).

core.migrare_tichet_cultural aplicat pe tenantii reali. Un singur tenant real in productie: tenant_001.
- EFEMERA intai (schema scratch efemer_migr_cultural cu constrangerile vechi): inainte cultural RESPINS
  (CheckViolation); dupa aplicare cultural+ocazional ACCEPTATE, valoare invalida tot respinsa; a doua
  aplicare identica (idempotent); schema stearsa.
- TENANT_001: cultural in CK False -> True; eveniment CK include acum 'ocazional'; a doua aplicare
  idempotenta (fara eroare). verifica()=True.
Zero esecuri. Toti tenantii reali (1) migrati. 50 teste tichete/salarizare verzi dupa migrare.

EFECT PE PRODUS: contabilul poate inregistra tichete culturale (tip='cultural', eveniment='ocazional')
pe tenant_001 - inainte respinse de constrangerea DB. Template-ul era deja actualizat (tenanti noi ok);
acum si tenantul existent.


## 04.08.2026 — C4 IMPLEMENTAT: sectiunea 8.3 avantaje D112 (bilete de valoare, E3_10/72/74/75 + E3_60).

Campania "implementarile ramase", punctul 2. Generatorul D112 nu emitea sectiunea 8.3 (avantaje detaliate)
pentru NICIUN bilet de valoare - limita generator-wide. Implementat.

STRUCTURA OFICIALA (d112_struct_anaf.txt:6293-6332): E3_60 "8.3 Avantaje" = suma; E3_60 >= E3_10 + E3_72 +
E3_73 + E3_74 + E3_75 + E3_57 + E3_58 + E3_44. Mapare: E3_10 masa (8.3.1), E3_72 cresa (8.3.1.1), E3_73 cadou
(8.3.1.2), E3_74 cultural (8.3.1.3), E3_75 vacanta (8.3.1.4).

DECIZIE TEHNICA (probata DUK 04.08.2026, 3 scenarii): sectiunea se emite fara a atinge E3_8 (venit) sau E1_1.
- (a) fara 8.3 -> VALID (baseline).
- (b) E3_60 + componente, E3_8 NESCHIMBAT -> VALID. [ALES]
- (c) E3_8 += nominal bilete -> RESPINS "DUK regula S111: E1_1(3000)=Suma(E3_8)(3200)" (ar cere cascada E1_1/E3_9,
  restatement de venit riscant pe un generator valid in productie).
Constrangerea oficiala e ">=" (E3_8 >= ...+E3_60); E3_8 (venit, mii lei) >= E3_60 (bilete, sute) prin constructie.
Deci sectiunea 8.3 se adauga INFORMATIV, fara restatement de venit. Emisa DOAR cand exista avantaje (salariatii
fara bilete raman byte-neschimbati).

IMPLEMENTARE: pull() ataseaza nominalele per tip pe salariat (e83_masa/vacanta/cultural/cresa, din calcul_salariu,
separate de tichete_nominal=baza CASS); _d112_genereaza emite E3_60 + componentele in asiguratE3. Gard nou
core/test_d112_avantaje.py (defalcare corecta + omitere cand 0 + proba DUK). Zero regresie (salariati fara bilete
neschimbati; proba: D112 fara bilete inca valid, fara E3_60).

SUB-BLOCAJ MOTIVAT (cadou E3_73, 4 elemente):
1. CE: E3_73 (cadou, 8.3.1.2) NU e emis.
2. DE CE: tichetul cadou NU e in pipeline-ul de impozit al D112 - calcul_salariu (core/salarizare.py) nu proceseaza
   tip='cadou' (nu are param tichet_cadou, nu-l impoziteaza); pull() d112 nu-l trage. Cadoul are reguli proprii
   (plafon neimpozabil 300 lei/ocazie, art.76(4)a CF) neimplementate in salariu.
3. CE TREBUIE: cablarea cadou in calcul_salariu (param + tratament fiscal 300 lei plafon) + pull d112 + registru
   BILETE_VALOARE_TRATAMENT[cadou]; apoi E3_73 se adauga banal ca celelalte 4.
4. URMATOR: campanie proprie "tichete cadou end-to-end" (ca la cultural/cresa), dupa care E3_73 e o linie.

EFECT PE PRODUS: D112 declara acum defalcat avantajele in bilete (masa/vacanta/cultural/cresa) in sectiunea 8.3 -
inainte le raporta doar agregat prin impozit/baza CASS. tenant_001 n-are bilete azi (beneficii_lunare gol), deci
efect imediat zero; se activeaza cand se acorda bilete.


## 04.08.2026 — Punctul 3 (approach a) EXECUTAT: suport N in D394 - dar tip_N NU EXISTA in validator (tipar ASI).

Campania "implementarile ramase", punctul 3. Cerinta: implementeaza approach (a) pentru operatiunile N
(achizitii de la parteneri NEINREGISTRATI). Groundwork-ul (DECIZII/GARZI 04.08) presupunea ca N cere op1.tip_N
(pct.229, bunuri/servicii) = CONTINUT DECLARAT ce cere camp nou + UI.

DESCOPERIRE MAJORA (proba jar v5 + DUK, metoda ca la ASI/HRK): **op1.tip_N NU EXISTA in validatorul INSTALAT v5.**
Extractia atributelor din D394Validator.jar (v5/Op1.class) da lista COMPLETA: tip, tip_partener, cota, cuiP, denP,
nrFact, baza, tva, tip_document, taraP/judP + adresa. NICIUN tip_N. Proba DUK directa: un op1 cu tip_N -> "tip_N:
atribut necunoscut in namespace v5". Deci premisa approach b (tip_N = continut declarat, cere UI bunuri/servicii)
se baza pe un camp din pdf-ul de structura care NU e in validatorul instalat - EXACT tiparul ASI (pdf vs jar).

CE CERE DE FAPT v5 pentru N (probat DUK, iterativ pana la "valid"):
- op1: tip_document="1" (facturi) - R220/pct.228, OBLIGATORIU pt tip_partener=2 + N.
- rezumat1 (tp=2, cota=0): document_N="1" + bazaN/facturiN (R60.1/R59/R62); document_N conditioneaza facturiLS (R41.2).
- op11 cu codPR + detaliu (nrN/valN): R233.6 - pentru PERSOANA FIZICA (achizitie fara CUI = persoana fizica),
  op11 e OBLIGATORIU. codPR = categoria art.331 a bunurilor (R233.3/R233.4). Detaliu.class v5: campurile N = nrN/valN.

CONTINUTUL DECLARAT REAL = op11.codPR (CATEGORIA bunurilor art.331), NU tip_N. Si acesta REUTILIZEAZA campul
`categorie_331` care EXISTA DEJA pe factura (DB + pull d394 il trece deja). Deci:
- N cu categorie art.331 -> DECLARAT VALID (op1.tip_document + rezumat1.document_N + op11.codPR + detaliu nrN/valN).
  Probat DUK "valid" pe validatorul instalat (J8/v5).
- N FARA categorie -> ramane EXCLUS cu avertisment care numeste furnizorul+suma si CERE adaugarea categoriei
  (default = NIMIC, contabilul alege explicit - NU se ghiceste). Restul declaratiei ramane valid.

IMPLEMENTAT (core/d394.py): scoasa excluderea neconditionata; N inclus cand codpr_din_categorie(categorie_331)
exista (auto + manual); rezumat1.document_N=1; op11 extins pt N (tp=2, tip=N); detaliu extins (nrN/valN);
emisie op1.tip_document="1" pt N; avertisment actualizat. Garduri noi: test_N_cu_categorie_art331_e_declarat_si_
valid_pe_duk + test_N_fara_categorie_ramane_exclus_cu_avertisment. Gardul invers (test_N_ar_fi_respins_...) RAMANE
valid: un op1 N GOL (fara tip_document/document_N) e tot respins -> confirma ca atributele emise sunt necesare.

RAMAS (sub-piesa separabila, front-end): UI-ul pentru categorie_331. Campul EXISTA in DB + generator + pull, DAR
NU e expus in UI (grep categorie_331 in *.js = 0 rezultate). Locul: static/js/ecrane/facturi_ecran.js, functia
primitaDetaliu (validarea unei facturi de achizitie, ~linia 107) - un select "categorie art.331" (nomenclatorul
CODPR: cereale/deseuri/masa lemnoasa/...) pe facturile de achizitie FARA CUI furnizor, + endpoint de salvare pe
facturi.categorie_331 (modelul: campul pr-cont "Cont cheltuiala" din aceeasi functie are deja salvare). Pana la UI,
categorie_331 se poate seta doar in DB. tip_document 2-5 (borderouri/contracte) = extindere separata (facturi/manual
n-au campul) - sub-blocaj.

EFECT PE PRODUS: o achizitie de la un furnizor neinregistrat (persoana fizica) cu categoria art.331 completata se
DECLARA acum in D394 (inainte: exclusa, contabilul o depunea separat manual). Fara categorie: exclusa cu avertisment
explicit. tenant_001 n-are astfel de facturi azi.


## 04.08.2026 — Punctul 3 (N) - CORECTII dupa reviziune Costin: nomenclator lit.D + gap clasifica_partener.

Reviziunea a gasit doua probleme reale in prima livrare a suportului N. Corectate:

1. NOMENCLATOR N GRESIT (reparat). Prima implementare reutiliza codpr_din_categorie (art.331 = lit.C, coduri
   21-36). DAR N (achizitii de la persoane fizice) are nomenclator PROPRIU: lit.D (OPANAF 77/2022 pct.10):
   "cereale si plante tehnice, deseuri, masa lemnoasa, terenuri, constructii, ALTE bunuri si servicii". Validatorul
   v5 (DUK regula R64.3, probat 04.08): pt tip_partener=2 codPR trebuie in 21-23 SAU 32-35. Codurile art.331
   ne-N (ex. gaze=36, cladiri=27) sunt RESPINSE. Vechea impl ar fi emis codPR=36 pt o achizitie N de gaze de la
   persoana fizica -> D394 RESPINS. REPARAT: nomenclator propriu CODPR_N = {cereale:21, deseuri:22, masa_lemnoasa:23,
   terenuri:32, constructii:33, alte_bunuri:34, alte_servicii:35}; codpr_N_din_categorie; N inclus DOAR cu categorie
   lit.D valida (altfel exclus, fara cod invalid). 34/35 = catch-all "alte bunuri/servicii" - fac declarabila ORICE
   achizitie N. AICI traieste distinctia bunuri-vs-servicii (in "alte"), NU ca un tip_N global (care nu exista in v5).
   Probat DUK: deseuri/alte_bunuri/alte_servicii/masa_lemnoasa/terenuri -> valid; gaze(36) -> exclus. Garduri noi:
   test_N_cu_categorie_litD_e_declarat_si_valid_pe_duk, test_N_categorie_ne_litD_e_exclusa_nu_emite_cod_invalid.

2. GARD INVERS cu aserthie SLABA (intarit). test_N_ar_fi_respins...GARD_INVERS avea "N" in er (litera N prinde
   orice text de eroare). Intarit: cere regula SPECIFICA (tip_document/document_N/R228/R60) - un op1 N gol e respins
   fiindca lipseste tip_document (R228), nu din orice motiv.

3. DATORIE (din reviziune, NEreparata - concern separat pct.216): clasifica_partener trateaza ORICE CUI numeric ca
   tip 1 (INREGISTRAT in scopuri de TVA). O PERSOANA JURIDICA NEINREGISTRATA (are CUI dar NU e platitor de TVA) e
   clasificata GRESIT tip 1 -> operatiunile ei nu ajung la N (tip 2). clasifica_partener foloseste doar prezenta
   CUI-ului, nu statutul de platitor TVA. CE TREBUIE: statut platitor_tva PER PARTENER (nu exista pe tabela clienti;
   firma_profil.platitor_tva e al firmei proprii). core.anaf_api il poate lua din ANAF (scpTVA), dar clasifica_partener
   nu-l consulta. Fix = stocare platitor_tva pe partener (lookup ANAF / snapshot, ca F180 pe firma) + clasifica_partener
   sa-l foloseasca. Impact: azi, N acopera DOAR achizitiile FARA CUI (persoane fizice) - cazul dominant; PJ neinregistrata
   cu CUI e o nisa. URMATOR: campanie proprie "statut TVA per partener" (pct.216 complet), dupa care N prinde si PJ neinreg.

EFECT: N declarabil corect pentru toate categoriile lit.D (inclusiv "alte bunuri/servicii" = achizitii generale de la
persoane fizice), cu codurile CORECTE (nu mai emite coduri art.331 ne-N respinse de ANAF).


## 04.08.2026 — Punctul 4 (A2) EXECUTAT: D390 "ziua 15" art.284 - camp optional data_faptului_generator.

Campania "implementarile ramase", punctul 4. Dump de siguranta inainte (backup_pre_d390_ziua15_20260804_1519.sql.gz,
322 CREATE TABLE). Precautii C5: efemera intai, tenant real dupa, idempotent, oprire la esec.

TEMEI (CF art.284): exigibilitatea operatiunilor intracomunitare intervine la data emiterii facturii, DAR nu mai
tarziu de a 15-a zi a lunii urmatoare celei in care a avut loc faptul generator. D390 se depune pe EXIGIBILITATE,
nu pe data emiterii. Edge-case-ul "ziua 15" era consemnat ca datorie la clusterul "exigibilitate / prag | d390"
(03.08); acum implementat.

IMPLEMENTARE:
- Camp NOU data_faptului_generator (date, NULL) pe facturi. Migrare idempotenta core.migrare_d390_faptul_generator
  (ADD COLUMN IF NOT EXISTS) + mirror in tenant_template.sql (sursa unica). Aplicat pe tenant_001 (singurul tenant
  real): coloana False -> True, idempotent. Efemera intai (schema scratch): migrare + probe, apoi drop. Zero esecuri.
- d390.pull() incadreaza pe EXIGIBILITATE = MIN(data_emitere, ziua 15 a lunii urmatoare faptului), calculata in SQL
  (CASE/LEAST). Camp NULL -> exigibilitate = data_emitere = COMPORTAMENT ANTERIOR (backward-compat).

CAMP OPTIONAL - backward-compat PROBAT explicit (test round-trip pe schema scratch):
- factura FARA fapt (data_emitere iulie) -> IULIE; factura control fara fapt (aug) -> AUGUST: NESCHIMBAT.
- factura emisa TARZIU (20 aug) cu fapt in iunie -> deadline 15 iulie -> exigibilitate 15 iulie -> se MUTA in IULIE
  (din august). Regula ziua-15 aplicata doar cand faptul e completat.
Gard nou core/test_d390_ziua15.py (test_migrare_si_exigibilitate_ziua15, gated DB): migrare idempotenta +
backward-compat + mutarea pe exigibilitate.

RAMAS (front-end, sub-piesa): UI pentru data_faptului_generator pe factura (optional). Campul e in DB/generator;
pana la UI se seteaza in DB. Fara el, comportamentul e cel actual (data_emitere) - nu blocheaza nimic.

EFECT PE PRODUS: o factura IC emisa cu intarziere, dar cu faptul generator completat, e declarata in D390 pe luna
CORECTA a exigibilitatii (art.284), nu pe luna emiterii. Fara faptul completat: comportament neschimbat. tenant_001
n-are facturi IC cu acest caz azi.


## 04.08.2026 — Punctul 4 (A2) - verificare la sursa a cazului INVERS (facturare anticipata), ceruta de Costin.

Costin a cerut verificarea cazului complementar: factura emisa INAINTE de faptul generator (avans/facturare
anticipata, ex. emitere 28.07, fapt 05.08). Formula implementata: exigibilitate = MIN(data_emitere, ziua 15 a
lunii urmatoare faptului).

VERIFICAT LA SURSA (CF art.284 alin.(2) integral, anaf_surse/cod_fiscal_227_2015_consolidat.html):
"exigibilitatea taxei intervine LA DATA EMITERII FACTURII ... ORI in cea de-a 15-a zi a lunii urmatoare celei in
care a intervenit faptul generator, DACA NU A FOST EMISA NICIO FACTURA/autofactura pana la data respectiva."

CONCLUZIE: MIN e CORECT (nu neconformitate). Regula: cand EXISTA factura (orice rand din tabela facturi e o
factura emisa), exigibilitate = data emiterii; ziua-15 e DOAR fallback cand nu s-a emis nicio factura pana atunci.
Deci: data_emitere <= ziua15 -> exigibilitate = data_emitere; data_emitere > ziua15 (factura tarzie) -> fallback
ziua15. Adica EXACT MIN(data_emitere, ziua15), dat fiind ca factura exista mereu.
- Caz TARZIU (emitere 20.08, fapt iunie): factura lipseste la 15.07 -> exigibilitate 15.07 -> IULIE. MIN=15.07. OK.
- Caz INVERS (emitere 28.07, fapt 05.08): factura exista (28.07 < 15.09) -> exigibilitate = 28.07 -> IULIE.
  MIN(28.07, 15.09)=28.07. OK. Probat empiric (IULIE=[1500], AUGUST=[]).
AVANSURI: art.282 alin.(2) lit.b (avansul declanseaza exigibilitate) e pentru livrari/prestari DOMESTICE; achizitiile
IC sunt guvernate de art.284 SEPARAT, care NU are regula de avans -> nu se aplica la IC. Deci factura anticipata IC
da exigibilitate la data emiterii, fara tratament de avans.

Proba explicita adaugata in core/test_d390_ziua15.py (factura D, facturare anticipata -> exigibilitate = data emiterii).


## 04.08.2026 — Punctul 5 (A3 D177): structura OBTINUTA + salvata, dar BLOCAJ MOTIVAT pe mecanism (formular PDF).

Campania "implementarile ramase", punctul 5. Predarea presupunea ca structura D177 lipseste si trebuie descarcata.
DESCARCATA si SALVATA in anaf_surse/ (contrar presupunerii): OPANAF_3562_2024_D177.pdf (306903 bytes, HTTP 200,
sha256 salvat) + OPANAF_3562_2024_D177.txt (extractibil cu pdftotext - NU e scanat, WebFetch esuase dar pdftotext
merge) + d177_structura_note.txt (lista de campuri). Deci "sursa oficiala lipseste" NU mai e adevarat.

STRUCTURA (campuri, din OPANAF + instructiuni): identificare contribuabil (CIF/denumire/adresa); an fiscal; suma
maxima redirectionabila (= MIN(0.75% cifra afaceri, 20% impozit profit) - motorul o calculeaza deja,
core/sponsorizari.py redirectionabil_d177); 4 subsectiuni de beneficiari (persoane juridice fara scop lucrativ/cult;
alti beneficiari L32/1994; mecenat persoane fizice; UNICEF/org internationale) cu denumire/CIF/IBAN/adresa/contract/
suma; imputernicit optional; acord informare beneficiar. Vezi anaf_surse/d177_structura_note.txt.

BLOCAJ MOTIVAT (4 elemente) - pe MECANISM, nu pe structura:
1. CE: generarea formularului D177 nu e implementata (motorul calculeaza doar SUMA redirectionabila).
2. DE CE: D177 e FORMULAR PDF ("Cerere", format electronic via SPV), NU declaratie XML cu validator. OPANAF 3562/2024
   aproba "modelul, continutul si instructiunile" formularului - NU o schema XML. Nu exista D177Validator, .xsd, sau
   intrare in CHEIE_DUK. Codebase-ul genereaza declaratii XML validate DUK (d100/d394/...); D177 NU se incadreaza:
   fara schema XML si fara validator, un D177 generat NU se poate proba (nimic de validat) - contravine metodei
   R17 (validatorul e autoritatea) folosite peste tot. Producerea PDF-ului cere infrastructura de completare
   smart-PDF (template oficial + XFA), ABSENTA din codebase.
3. CE TREBUIE: DECIZIE DE PRODUS pe materializare (schimba ce ajunge la contabil, NU rezulta din structura):
   (a) model de date structurat (continutul cererii) pt completare/verificare manuala; sau (b) generare PDF cu
   template-ul oficial + infrastructura noua; sau (c) asteptare pana ANAF publica o schema XML pt D177. Plus:
   confirmarea ca D177 se depune ca PDF (nu XML) - probabil da, dat fiind ca e "cerere".
4. URMATOR: campanie proprie "D177 formular" dupa decizia de produs pe mecanism. Structura + temeiurile sunt gata
   in anaf_surse/ (groundwork facut). Trec la punctul 6.

Sursa: static.anaf.ro/static/10/Anaf/legislatie/OPANAF_3562_2024.pdf; lege5.ro instructiuni formular 177 (secundar).


## 04.08.2026 — Punctul 6 (C3 amortizare MF neliniara): temeiuri culese, BLOCAJ MOTIVAT (subsistem).

Campania "implementarile ramase", punctul 6. Modulul MF (core/d406_active.py calc_asset) calculeaza DOAR
amortizare liniara (rata = amortizabil/dnf_luni), desi metoda (liniara/degresiva/accelerata) e STOCATA per
activ (mijloace_fixe_import_api._normalizeaza_metoda) si emisa in D406 (DepreciationMethod) - dar IGNORATA la
calculul sumelor. xfail test_datorie_mf_metode_amortizare.

TEMEIURI LA SURSA (CF art.28, anaf_surse/cod_fiscal_227_2015_consolidat.html - culese acum):
- alin.(5) eligibilitate pe clasa: a) constructii -> DOAR liniara; b) echipamente tehnologice/masini/unelte/
  instalatii/computere -> liniara, degresiva SAU accelerata; c) orice alt MF -> liniara sau degresiva.
- alin.(6) LINIARA: amortizare = valoare / durata (constant). [IMPLEMENTAT]
- alin.(7) DEGRESIVA: cota liniara x coeficient, pe valoarea ramasa: 1,5 (durata 2-5 ani); 2,0 (6-10 ani);
  2,5 (>10 ani). [norme HG 1/2016: switch la liniara cand cota degresiva anuala < ramas/ani-ramasi]
- alin.(8) ACCELERATA: an 1 <= 50% din valoarea de intrare; anii urmatori = valoare ramasa / durata normala ramasa.
- alin.(8^1): exceptie pt active de cercetare-dezvoltare (art.20) - accelerata extinsa.

BLOCAJ MOTIVAT (4 elemente):
1. CE: metodele degresiva + accelerata nu sunt calculate (doar liniara); calc_asset ignora mf.metoda pt sume.
2. DE CE: SUBSISTEM cu reguli ANUALE subtile, nu o formula punctuala: (a) schema pe ani (degresiva/accelerata dau
   sume DIFERITE per an, nu constante ca liniara); (b) degresiva cere SWITCH la liniara (norme HG 1/2016) cand cota
   degresiva < ramas/ani-ramasi; (c) accelerata: 50% an 1 apoi ramas/durata-ramasa; (d) PRORATAREA primului an
   PARTIAL (PIF la mijloc de an) interactioneaza cu schema anuala; (e) eligibilitate pe clasa de activ (constructii
   doar liniara - un gard care respinge degresiva/accelerata pe constructii). calc_asset azi e pe LUNI (liniar);
   metodele sunt pe ANI -> reproiectare a modelului de amortizare + D406 AssetTransactions. Cere teste golden pe
   fiecare metoda + interactiunea cu proratarea. Groundwork-ul (DECIZII 31.07) il marcheaza "cluster MF/D406 viitor,
   scop propriu".
3. CE TREBUIE: campanie proprie "amortizare MF metode" cu: functie de schema anuala per metoda (degresiva cu switch,
   accelerata), integrare in calc_asset (schema anuala -> valoarea pt anul cerut, cu proratare an 1), gard pe clasa
   (constructii doar liniara), teste golden per metoda + emisie D406 corecta. Temeiurile sunt gata (CF art.28 alin.5-8).
4. URMATOR: dupa aceasta campanie proprie. NU se rezolva pe jumatate (o metoda incompleta ar da amortizare fiscala
   GRESITA = cifra intr-o declaratie, mai rau decat absenta). xfail RAMANE deschis. Trec la punctul 7.

Fara implementare pe jumatate: o amortizare degresiva/accelerata gresita ar produce o deducere fiscala eronata in
D101 (impozit pe profit) - cifra invizibila care ajunge la ANAF. Se face intreg, cu teste, sau deloc.


## 04.08.2026 — Punctul 7 (C1 cresa + C2 culturale): re-research MO. C2 CONFIRMAT+DEBLOCAT; C1 confirmat la emitent, neaplicat.

Campania "implementarile ramase", punctul 7. Reincercare la MO a ordinelor de indexare (metoda §3 decizia d:
sursa oficiala + salvare cu sha256; secundarul nu inlocuieste primarul).

C2 (culturale, fereastra oct.2025-mar.2026 = fosta GRI verdict 16): CONFIRMAT LA PRIMAR + DEBLOCAT.
Obtinut TEXTUL OPERATIV al Ordinului MF/MC 1.574/3.246/2025 (anaf_surse/ordin_1574_3246_2025_cultural.pdf, sha256):
"Pentru semestrul II al anului 2025 ... maximum 240 lei/luna, respectiv maximum 470 lei/eveniment ... se aplica si
pentru primele 2 luni ale semestrului I 2026" (feb-mar 2026). Publicat MO nr. 900/01.10.2025. Fereastra oct.2025-
mar.2026 (240/470) ADAUGATA in _FERESTRE_CULTURAL; _CULTURAL_GRI = None (nu mai e GRI). Teste actualizate din
"blocheaza GRI" in "confirmat 240/470" (plafon + DB insert). Progresie coerenta: 220/450 -> 240/470 -> 250/490.

C1 (cresa, indexare 740): CONFIRMAT LA EMITENT + MO-referinta, dar NEAPLICAT (nu se deblocheaza acum).
Ordin MF/MMSS 368/179/2026, MO Partea I nr. 249/31.03.2026, valoare 740 lei S1 2026 (din aprilie 2026, + aug-sep
2026), valoarea calculata 739,76 rotunjita. CONFIRMAT de EMITENT (pagina oficiala mmuncii.gov.ro pt acest ordin) +
MO-referinta din surse multiple independente (juridice.ro, avocatnet, universuljuridic, crowe). DAR: (a) TEXTUL
operativ al ordinului NU s-a obtinut (primar strict - pagina ministerului nu expune PDF-ul extractibil, URL-urile
ghicite 404); (b) plafon_cresa e FIX (450), nu are mecanism de ferestre datate ca plafon_cultural; (c) valorile
intermediare (ex. 710 - semestrul anterior) nu-s cercetate. -> indexarea RAMANE neaplicata (cap conservator 450),
nota din plafon_cresa upgrade-uita cu confirmarea + data incercarii. Se deblocheaza cand: (a) textul ordinului
368/179/2026 obtinut la MO + (b) mecanism _FERESTRE_CRESA cu istoricul complet. DATA INCERCARII: 04.08.2026.

Surse: mmuncii.gov.ro (ordin cresa S1 2026); upromania.ro Ordinul-3246-2025 (text cultural, salvat); juridice.ro,
avocatnet.ro, universuljuridic.ro (referinte MO).


## 04.08.2026 — Operatiuni N (d394): PIVOT dupa proba DUK - approach (a) CONDITIONAT livrat (SUPERSEDA cele 2 intrari N de mai sus).

Aceasta intrare ACTUALIZEAZA cele doua intrari N anterioare de azi ("NECONFORMITATE ACTIVA ... Optiuni Costin" +
"EXECUTAT approach (b)"). Ele descriau starea INTERMEDIARA; groundwork-ul pe approach (a) a schimbat imaginea.

DESCOPERIRE (proba DUK, groundwork approach a): **campul `op1.tip_N` NU EXISTA in validatorul v5.** Intrarea
anterioara il dadea "OBLIGATORIU pt tip in (V,C,N)" pe baza structurii pdf - dar la injectarea lui, D394Validator
instalat (J8) raspunde "tip_N atribut necunoscut". Extras atributele reale din v5/Op1.class: NU contine tip_N
(tiparul ASI - structura pdf spune un camp pe care jar-ul instalat il respinge). Consecinta: intrebarea "de unde vine
tip_N (bunuri/servicii)?" din intrarea anterioara DISPARE - nu exista camp de completat.

PIVOT: fara tip_N, dilema "continut declarat nederivabil" cade, deci approach (a) devine VIABIL - N se emite cu
`tip_document=1` (facturi) + `document_N=1` + `op11.codPR` (din `categorie_331`, nomenclatorul lit.D) + detaliu
nrN/valN. **PROBAT DUK J8: o operatiune N cu categorie lit.D e ACCEPTATA** (test_N_cu_categorie_litD_e_declarat_si_
valid_pe_duk).

STARE LIVRATA (approach a CONDITIONAT): N se EMITE VALID cand are `categorie_331` din lit.D; FARA categorie (azi nu
exista UI care s-o seteze) ramane EXCLUS cu avertisment vizibil (fostul approach b devine fallback-ul pentru cazul
fara categorie). Categorie ne-lit.D -> exclusa, nu emite cod invalid.

REVIZIUNE COSTIN (3 defecte reale reparate, commit 21b4f48): (1) nomenclatorul N folosea lit.C (21-36, ex. gaze=36
respins R64.3) in loc de lit.D (21-23/32-35 incl. "alte bunuri/servicii") -> CODPR_N dedicat; (2) asertiunea gardului
invers slaba ("N" matcha orice) -> intarita pe R228/R60/document_N/tip_document; (3) clasificarea.

Garduri (inlocuiesc test_rezumat1_tp2_neinreg_N_respins_de_validator_DATORIE, redenumit/scos la implementare):
test_N_cu_categorie_litD_e_declarat_si_valid_pe_duk (emisie valida), test_N_ar_fi_respins_de_validator_daca_emis_
GARD_INVERS (N incomplet -> J8 respinge), test_N_fara_categorie_ramane_exclus_cu_avertisment,
test_N_categorie_ne_litD_e_exclusa.

DATORIE RAMASA (deblocaj complet): UI categorie_331 (deblocajul principal - fara ecran N in calea auto ramane exclus),
tip_document 2-5 (borderouri/carnet/contracte/alte = extindere de contract, facturi/manual n-au campul). Consemnate
in GARZI.md ("04.08 Datorii deschise ale campaniei" + "DATORIE suport COMPLET operatiuni N").


## 04.08.2026 - D177: DECIZIE COSTIN - RAMANE IN AFARA SCOPE-ULUI, AMANAT EXPLICIT (supersedeaza blocajul motivat de la pct.5).

Intrarea de la punctul 5 ("structura OBTINUTA + BLOCAJ MOTIVAT pe mecanism") astepta decizia lui Costin pe canal/scope.
DECIZIE (Costin, 04.08.2026): **D177 ramane IN AFARA SCOPE-ULUI, amanat EXPLICIT** (nu "de facut candva").

Temei al deciziei: D177 e o **cerere-formular PDF, nu o declaratie XML** - nu are validator DUK instalat. Toata
arhitectura de declaratii se sprijina pe validator ca AUTORITATE (R17): fiecare piesa fiscala e probata mecanic contra
jar-ului. D177 ar fi **prima piesa construita pe interpretarea unui PDF, fara proba mecanica** - exact tiparul care a
generat defecte reale in aceasta campanie si inainte: ASI (D394, structura pdf vs jar), HRK (D301), nomenclatorul N
gresit (lit.C vs lit.D). A construi un generator D177 pe citirea unui PDF ar reintroduce clasa de eroare pe care
validatorul o inchide. In plus: D177 e cerere **ANUALA**, nu obligatie lunara - beneficiu mic fata de risc.

Proba/artefact: structura OPANAF 3562/2024 ramane in anaf_surse/ (nu se pierde munca de descarcare). Alternativa
respinsa: a construi acum pe interpretare de PDF (respinsa - fara ancora de validare mecanica). Limita: decizia se
redeschide DOAR cu o decizie noua Costin, si numai daca (a) apare un canal de validare mecanica pt D177, SAU (b) se
accepta explicit constructia pe interpretare de PDF asumand riscul. Consemnat: GARZI 04.08, FUNCTIONALITATI.csv F206.


## 04.08.2026 — Localizare fix „achizitie fara rand facturi": DIRECTIA BACKEND (operatiunea emite factura), nu UI.

DECIZIE (Costin, 04.08): operatiunile de achizitie (`achizitie_ic` main.py:7077, `achizitie_taxare_inversa`
main.py:7019) emit INTAI un rand in `facturi` (tert, directie=primita, categorie_331 la taxare inversa,
data_faptului_generator la IC), apoi contabilizeaza in jurnal cu `factura_id` legat. NU ecran nou, NU camp in
primitaDetaliu.

TEMEI: harta facturi<->inregistrari (investigatie 04.08). Straturi complementare CORECTE: factura = sursa citita de
D390/D394; inregistrarea = derivata, citita de D100/D101/D205; legate prin `factura_id`. Defectul NU e arhitectura,
ci ca `achizitie_ic`/`achizitie_taxare_inversa` scriu DOAR in jurnal -> inregistrari orfane -> absente din D390/D394
(GARZI „NECONFORMITATE ACTIVA" 04.08). Efect fiscal numit: o achizitie IC introdusa azi NU ajunge in D390 (VIES lunar
obligatoriu), desi D100/D101/D205 o vad.

ALTERNATIVE RESPINSE:
- (a) Camp categorie_331 in `primitaDetaliu` (validarea e-Facturii SPV). RESPINS: `efactura_primite.cif_emitent` e
  TEXT NOT NULL (furnizor mereu cu CUI) -> „furnizor fara CUI" structural imposibil acolo -> UI mort; iar IC nu vine ca
  e-Factura SPV (RO_CIUS e domestic). Probat la sursa (schema + 0 date reale). A fost premisa comenzii initiale,
  infirmata la verificare.
- (b) Ecran nou de editare factura de achizitie. RESPINS: achizitiile se introduc DEJA in `operatiuni_ecran.js`; un
  ecran nou = a doua cale de intrare, redundanta (tiparul „arbori paraleli"). Se repara calea existenta.

LOCALIZAREA UI a campurilor: `operatiuni_ecran.js` (unde se introduc operatiunile), DUPA ce backend-ul emite corect
randul `facturi`. Vezi GARZI „NECONFORMITATE ACTIVA" 04.08 pentru clasa de defect si gardul anti-regresie planificat.


## 04.08.2026 — achizitie_agricultor EXCEPTAT NUMIT din fix-ul "achizitie emite factura" (tratament D394 neconfirmabil la sursa).

Context: fix-ul NECONFORMITATII ACTIVE (operatiune achizitie -> rand facturi + factura_id) s-a extins la toate
handlerele achizitie_* (decizie Costin: optiunea A, gard de clasa onest). La verificarea la sursa a specificului
(cerinta Costin: "nu le trata ca pe clone"), achizitie_agricultor s-a dovedit un caz pe care NU-l pot confirma.

DECIZIE: achizitie_agricultor NU emite (inca) rand facturi; ramane NECONFORMITATE DESCHISA in GARZI, iar gardul de
clasa il EXCEPTEAZA NUMIT (set EXCEPTATE, cu motiv), NU tacit.

TEMEI (CF art.315^1, verificat in core/tva_agricultori.py + surse): agricultorul in regim special forfetar NU
colecteaza TVA si NU e inregistrat in scop TVA (alin.4); cumparatorul deduce compensatia forfetara 8% ca TVA
(alin.17) doar daca agricultorul e in Registru. DAR: cum se declara aceasta achizitie in D394 (tip_partener al
agricultorului forfetar? intra compensatia in baza D394? sub ce cod?) NU e confirmabil la sursa - niciun ghidaj in
d394_struct_anaf.txt sau instructiunile D394; regim special, distinct de achizitia obisnuita si de N. A construi un
rand facturi pe presupunere ar produce o linie D394 gresita (mai rau decat orfan - §3 nu se inventeaza).

ALTERNATIVA RESPINSA: a-l trata ca pe celelalte 3 (clona) - respinsa, fiindca regimul e special si tratamentul D394
neconfirmat. D300 e deja acoperit prin 4426 din inregistrari (compensatia deductibila apare in TVA deductibila).

DEBLOCARE: cand se confirma la sursa (instructiuni D394 / ghid ANAF pe agricultori forfetari) cum intra achizitia in
D394. Consemnat: GARZI "NECONFORMITATE ACTIVA" 04.08 (sectiunea achizitie->jurnal).


## 05.08.2026 — clasifica_partener: statut platitor TVA INGHETAT-LA-CREARE pe factura (nu cache mutabil, nu forma CUI).

DECIZIE (Costin): statutul de platitor TVA al tertului se INGHEATA pe factura la creare (`facturi.tert_platitor_tva`),
ca FAPT CONTABIL imutabil ca oricare de pe factura. clasifica_partener il consulta in loc de euristica pe forma CUI.

TEMEI: statutul e ISTORIC (o firma poate fi platitoare azi si nu era acum 3 luni). O factura veche trebuie clasificata
dupa statutul de ATUNCI. Inghet-la-creare da asta GRATIS: flag-ul stocat = statutul de la data facturii. ANAF ofera
istoricul (PlatitorTvaRest/v9 inregistrare_scop_Tva.perioade_TVA[] cu data_inceput/sfarsit_ScpTVA), deci corectitudinea
istorica e realizabila.

ALTERNATIVA RESPINSA: cache per-CUI cu statutul curent, clasificat la pull. RESPINSA (argument Costin): ar face
clasificarea dependenta de o stare externa MUTABILA - aceeasi factura clasificata diferit la doua rulari. Contabilitatea
ingheata faptele; un fapt pe factura nu se schimba retroactiv fiindca ANAF-ul de azi arata altceva.

LIMITA SCRISA (nu ascunsa): (1) facturi LEGACY fara flag -> euristica de forma; backfill via perioade_TVA doar cand
un tenant are facturi legacy reale (trigger scris in GARZI 05.08; pe tenant_001 gol nu se scrie cod pe presupuneri).
(2) decalaj snapshot ANAF (corectie retroactiva neactualizata). (3) ANAF-jos la creare -> flag NULL -> euristica (nu
blocheaza emiterea). Din caveat: _tva_inceput_activ arunca perioadele inchise desi ANAF le trimite - REPARAT: anaf_api
pastreaza perioade_TVA[] intreg (tva_perioade), exact ce cere backfill-ul; nu se arunca ce ANAF ofera.

DEBLOCHEAZA corectitudinea N (N depinde de tip_partener): un PJ neplatitor cu CUI valid -> flag False -> tip 2 -> N
(inainte: tip 1). Probat in ambele sensuri + istoric (acelasi CUI, doua facturi, doua clasificari). F004 refolosit
(nu cale noua). Consemnat GARZI 05.08.

## 05.08.2026 — GARDUL DE CONTINUT: directia (a) golden BLOCATA la sursa; A DOUA CALE e mecanismul real. D300 primul.

DECIZIA: campania de gard de continut (DUK valideaza STRUCTURA, nu semantica — un total GRESIT dar structural
valid trece azi) se face pe DIRECTIA (b) A DOUA CALE de reconciliere pe totaluri, NU pe (a) golden derivat din
exemplu oficial ANAF.

TEMEI/PROBA: inventar exhaustiv `anaf_surse/` + tot repo-ul (grep/find, exclus venv, 05.08) -> NICIUN fisier e o
declaratie ANAF completata cu cifre. Tot ce exista: structura XML / nomenclator / istoric versiuni / act normativ /
tabele de plafoane. ANAF publica structura+instructiuni, nu declaratii-model completate. Deci golden pe TOTAL de
declaratie din exemplu oficial = NESURSABIL. Golden pe VALORI unitare (deducere art.77, cote, plafoane) ramane
posibil unde legea da exemplu de calcul — dar aia e aproape exact ce fac deja `test_dXXX` (unit pe formula), nu
acopera totalurile.

PIVOT (supersedeaza EXPLICIT): intentia consemnata in ISTORIC 04.08 — "gard de CONTINUT (golden pe exemplul oficial
ANAF + a doua cale pe totaluri)" — se reduce la A DOUA CALE. Ramura "golden pe exemplul oficial ANAF" e INCHISA ca
blocata la sursa (nu exista sursa), scris ca atare in TESTE (fir) + GARZI cat.4.

ALTERNATIVA RESPINSA: golden derivat din PROPRIUL nostru calcul. Respinsa explicit de Costin: un golden scris din
calculul modulului APARA bug-ul (testul afirma ce face codul, nu ce cere legea) — a patra aparitie a clasei
"teste care aserteaza valoarea gresita" (test_datorie_teste_care_apara_buguri).

TIPAR PENTRU TOATE CELE 6 DECLARATII (cerut de Costin, stabilit pe D300):
  1. NON-TAUTOLOGIA se PROBEAZA, nu se declara: calea 2 nu are voie sa atinga functia de agregare a
     generatorului (probat mecanic pe AST — modulul caii 2 nu importa/foloseste calcul_d300/_segmente/_int/pull).
  2. MUTATIE obligatorie: factura pierduta din agregare / cota in bucketul gresit / semn inversat -> reconcilierea PICA.
  3. La DIVERGENTA: gardul NU repara tacit nici una din cai. Eroare vizibila care numeste diferenta si AMBELE valori.
     Un gard care alege singur cine are dreptate e mai rau decat niciunul.

ORDINE (efect fiscal x cost, confirmata Costin): D300 -> D394(reconciliat vs D300) -> D112 -> D406 -> D101/D205.

D300 LIVRAT (05.08): core/d300_reconciliere.py (pull SQL propriu + agregare proprie pe cote, confruntata cu randurile
automate R9/R10/R11 colectat + R22/R23 deductibil), poarta in d300.genereaza. LIMITA DECLARATA (6 puncte) in GARZI
cat.4 la DESCHIDEREA campaniei (nu la final): manual/pro_rata/R33-R42 neacoperite, tva_la_incasare NEACOPERIT,
input partajat gresit = §8, cota fara-linii dedusa identic, deriva legislativa = alt gard.


## 05.08.2026 — TIPAR gard de continut: HARD-BLOCK la divergenta (toate cele 6 declaratii, nu per-decl)

DECIZIA (tipar, nu caz): la orice gard de a-doua-cale din campania GARDUL DE CONTINUT, divergenta intre cele
doua cai OPRESTE generarea (ridica exceptie), NU emite un avertisment. Se aplica identic la D300 (livrat), D394,
D112, D406, D101, D205 - nu se re-decide per declaratie.

TEMEI: warn-only e un avertisment pe care cineva il citeste sau nu, iar cifra pleaca oricum la ANAF. Un total
gresit dar structural-valid e exact ce DUK NU prinde - daca nici gardul de continut nu-l opreste, nu exista nicaieri
o oprire. Scopul gardului e ca cifra gresita sa NU ajunga la autoritate, nu sa fie insotita de o nota. (cerinta
Costin 05.08, confirmata dupa livrarea D300.)

ALTERNATIVA RESPINSA: warn-only (genereaza + avertisment). Respinsa: muta raspunderea pe cititorul avertismentului
si nu opreste iesirea gresita.

CONSECINTA ACCEPTATA: un fals-pozitiv al gardului (bug in calea 2) blocheaza o declaratie legitima. Pretul e corect:
calea 2 se probeaza mecanic (non-tautologie pe AST + mutatie) inainte de a fi poarta, exact ca sa nu blocheze fals.


## 05.08.2026 — GARD CONTINUT D394 (pas 2/6): recalcul propriu al rezumat2, NU reconciliere incrucisata vs D300

DECIZIA: gardul de continut D394 = recalcul INDEPENDENT al totalurilor rezumat2 (bazaL/tvaL/bazaA/tvaA pe cota)
din liniile brute (acelasi tipar ca D300), NU reconciliere incrucisata D394<->D300.

TEMEI (doua descoperiri la sursa, 05.08):
1. Reconcilierea incrucisata propusa in plan ar fi fost TAUTOLOGICA sau nesound:
   - gardul existent `test_d300_d394_paritate` confrunta calcul_d300 vs calcul_d394 dar AMBELE citesc aceleasi
     factura_linii si deduc cota identic - propriul lui docstring o spune: "sursa e comuna (liniile)". E aceeasi
     cale de doua ori; prinde doar DRIFTUL intre generatoare, nu un bug comun de agregare. (Exact riscul semnalat
     de Costin la pornire: "daca ambele citesc aceeasi agregare din acelasi loc, nu-i incrucisata".)
   - chiar corectata, confruntarea nu e EGALITATE: D300 colectat >= D394 livrari L pe cota (D300 = TVA totala,
     D394 = subsetul raportabil B2B/reportabil). Reziduul structural o face inegalitate -> divergenta falsa.
   Deci recalculul propriu (self-contained, ca la D300) e singura cale cu adevarat non-tautologica AICI.

2. ACOPERIRE (raspuns explicit la cerinta Costin - "cat din trafic ramane neacoperit; daca e majoritatea, gardul
   e siguranta falsa si se regandeste"): tot traficul REAL D394 e acoperit. Verificat in cod: taxare-inversa (tip
   C/V) si N (persoane fizice) sunt tratate AUTO din tabela facturi (tip_operatiune pe taxare_inversa + clasificare
   partener), NU prin manual=. manual['operatiuni'] (bonuri/borderouri/AI/AS/LS) NU are UI sau tabela care sa-l
   alimenteze azi (vine doar din body-ul cererii b['manual'], niciun ecran nu-l scrie) -> in practica gol. Gaura
   LIMITA-1 e deci un REZIDUU nealimentat, NU majoritatea. NU e siguranta falsa. CONDITIE scrisa (GARZI): daca
   apare o UI de operatiuni manuale, gaura devine reala si gardul trebuie EXTINS, nu doar documentat.

NON-TAUTOLOGIE probata pe AST: d394_reconciliere nu importa/foloseste calcul_d394/d394.pull/_int. Cale proprie:
SQL propriu + clasificare proprie + agregare proprie. Hard-block la divergenta (tipar 05.08), numind ambele valori.

ALTERNATIVA RESPINSA: reconciliere incrucisata D394<->D300 pe egalitate. Respinsa (motivele 1+2 de mai sus).
NOTA: `test_d300_d394_paritate` RAMANE ca detector de DRIFT intre generatoare (util, onest documentat), nu se
sterge; gardul de CONTINUT genuin e d394_reconciliere.

PROBA: schema efemera, F1 emisa 1000@21% + F2 emisa 500@11% + F3 primita 800@21% RO -> rezumat2 corect, divergente
[]. Mutatie 'achizitie pierduta' -> "cota 21%% bazaA: generator=0 vs cale2=800". Suita 1397 passed (+6), verificator 0.


## 05.08.2026 — GARD CONTINUT D112 (pas 3/6): DOAR cazul simplu (CAS/CASS din brut), restul declarat afara

DECIZIA: gardul de continut D112 reconciliaza DOAR CAZUL SIMPLU - CAS/CASS per angajat = brut x cota, pentru
angajatii fara nicio structura care schimba formula. Se scrie explicit "cazul simplu acoperit", NU "D112 acoperit".

CE INTRA: CAS (25%) + CASS (10%) pe angajatii cu brut STRICT peste salariul minim (facilitatea OUG 89/2025 se
declanseaza EXACT la brut==salariu minim; peste minim -> facilitate 0 -> baza contributie = brut), fara concediu
medical, norma intreaga, ne-scutiti, fara tichete, angajati luna intreaga.

CE RAMANE IN AFARA (raspuns explicit la cerinta Costin - "daca facilitatile raman afara, scris ca atare"):
FACILITATI (constructii/IT/agricol, salariu minim), SCUTIRI, PLAFOANE, PART-TIME suprataxare, CONCEDII MEDICALE
(baze/procente proprii OUG 158/2005), IMPOZIT (cere deducerea personala degresiva art.77 - calcul complex, exclus),
CAM (agregat angajator), TICHETE (schimba baza CASS/impozit). Un angajat cu oricare -> NEACOPERIT (sarit, nu alarma
falsa - probat: salariatul la minim cu cas aberant NU alarmeaza).

TEMEI acoperirii: facilitatea din salarizare.calcul_salariu (linia `facilitate = facilitate_val if vbt == sm ...`)
se aplica DOAR la brut == salariu minim. Deci brut > minim => facilitate 0 => baza_contrib = brut => cas = brut x
cota_cas exact. Verificat la sursa in salarizare.py, nu presupus.

NON-TAUTOLOGIE (cerinta Costin 1 - D112 e cel mai expus): probata pe lantul de import TRANZITIV, nu doar direct.
Testul construieste inchiderea tranzitiva a importurilor core.* pornind din d112_reconciliere si asertaza ca NU
contine core.salarizare / core.d112 / core.salariu_istoric. Calea 2 isi trage singura brutul (SQL propriu, mirror
pe salariu_la) si cotele din common.cota (registrul de lege period-aware, NU un intermediar al generatorului).

POARTA in d112.genereaza (care are salariati cu cas/cass calculate) paseaza acele valori caii 2 ca DATE de
verificat; calea 2 NU cheama pull/calcul_salariu. Hard-block la divergenta (tipar 05.08), numind angajatul si
ambele valori.

ALTERNATIVA RESPINSA: a extinde gardul pe impozit/CAM/facilitati acum. Respinsa: impozitul cere deducerea degresiva
(re-implementare mare = risc propriu si suprafata de tautologie), facilitatile/CM cer replicarea logicii din
calcul_salariu. Un gard care acopera doar cazul simplu, ONEST declarat, e mai bun decat unul care pretinde ca
acopera tot dar refoloseste agregarea generatorului. Extindere = pas separat, cu decizie.

PROBA: 2 salariati simpli (brut 6000/8000) -> cas 1500/2000, cass 600/800, reconciliati; salariat la minim (4050)
SARIT. Mutatie 'cas gresit' -> "salariat 1 cas: generator=9999 vs cale2=1500". Suita 1402 passed (+5), verificator 0.


## 05.08.2026 — D112 gard, doua completari cerute la review (acoperire cifrata + skip-suspect)

Dupa livrarea D112 (cazul simplu), Costin a cerut doua rigori inainte de D406:

1. ACOPERIRE CIFRATA, nu doar lista in/out. Estimare pe structura TIPICA de cabinet RO (NU masurata - tenantii
   de test sunt goi): gardul reconciliaza probabil o MINORITATE, ~20-35% din salariati; ~65-80% sar. Excluderile
   dominante: salariu MINIM (facilitate - pondere mare la IMM-uri RO) + TICHETE de masa (beneficiu larg raspandit),
   suprapuse, plus CM/part-time. Baza estimarii: structura pietei muncii RO (prevalenta salariului minim la IMM +
   uz larg al tichetelor tax-advantaged), nu cifre de productie. Scris in GARZI ca 'acoperire estimata', ca sa nu
   para 'D112 are a doua cale' in general - acopera cazul simplu al celei mai grele declaratii lunare, nu majoritatea.
   De reverificat cu cifra reala cand exista payroll.

2. SKIP-SUSPECT vs SKIP-LEGITIM. Distinctia se poate face CURAT: skip-legitim = complexitate fiscala reala
   (facilitate/CM/part-time/scutire/tichete/luna partiala) -> tacut, in afara scopului. skip-SUSPECT = angajat EMIS
   de generator cu date corupte: brut LIPSA (istoric+salariati.salariu_brut ambele goale -> generatorul calculeaza
   pe float(None or 0)=0 si emite contributii ZERO tacut - exact clasa pentru care s-a construit garda cere_coloane)
   SAU brut SUB minimul legal pentru full-time luna intreaga. Acestea devin HARD-BLOCK semnalat ('null base = eroare
   pana la proba contrarie'), nu skip tacut. Restul (pontaj aberant / cota necunoscuta) NU ating calea simpla: calea
   simpla foloseste brutul CONTRACTUAL (nu pontajul) si nu are cote per-angajat (ratele vin din lege) - deci nu exista
   alt vector de corupere pe calea simpla in afara brutului. Consemnat ca limita: coruperea pe caile NESIMPLE
   (facilitate/CM) ramane neacoperita fiindca acele cazuri sunt oricum sarite.

PROBA: brut NULL -> "brut LIPSA...SUSPECTE" ridica; brut 3000 (<minim 4050) full-time -> "SUB salariul minim" ridica;
facilitate la minim (4050) -> sarit-legitim, tacut. Teste: test_skip_suspect_brut_lipsa/sub_minim. Suita verde.


## 05.08.2026 — GARD CONTINUT D406/SAF-T (pas 4/6): balanta de rulaje independenta + Sdebit=Scredit

DECIZIA: gardul de continut D406 reconciliaza GeneralLedgerEntries - construieste o balanta de RULAJE per cont
INDEPENDENTA din inregistrari_linii (SQL propriu) si o leaga de totalurile per-cont din SAF-T-ul emis, plus
invariantul dublei partide Sdebit=Scredit. Cerinta Costin: "Sdebit=Scredit + legare la balanta".

TEMEI/STRUCTURA (verificat la sursa): fiecare inregistrari_linii = (cont_debit, cont_credit, suma) -> in SAF-T
devine DOUA TransactionLine (debit pe cont_debit, credit pe cont_credit). Deci Sdebit=Scredit e in mare parte
STRUCTURAL (garantat de model). Valoarea reala a gardului = legarea PER CONT la rulajul independent: prinde emisia
care pierde/dubleaza o nota sau o linie, sau o mapeaza pe contul gresit. Exact clasa bug-ului ISTORIC (16.07):
<GeneralLedgerEntries> ramanea GOL pentru orice firma printr-un except:pass tacit - calea 2 ar fi gasit notele in
DB si ar fi strigat (probat: res.note=[] -> ridica, numind fiecare cont saft=0 vs cale2=rulaj).

"Legare la balanta": nu exista o balanta de verificare stocata (solduri_api tine balanta de DESCHIDERE, import xlsx,
nu rulaje). Deci calea 2 CONSTRUIESTE balanta de rulaje a lunii din inregistrari_linii - aia e balanta la care se
leaga SAF-T-ul. Sursa comuna (inregistrari_linii), agregare INDEPENDENTA -> non-tautologic pe agregare/emisie.

NON-TAUTOLOGIE probata pe AST: d406_reconciliere nu importa/foloseste d406.pull/construieste/_generalledger.
res.note se citeste ca DATE de verificat (ce a emis generatorul), calea 2 isi trage singura liniile.

LIMITA DECLARATA (GARZI cat.4): acopera GeneralLedgerEntries; NU SalesInvoices/PurchaseInvoices/Payments/Assets/
MovementOfGoods (reconcilierea linii-antet facturi exista deja partial). Input partajat gresit = §8.

ALTERNATIVA RESPINSA: a verifica DOAR Sdebit=Scredit global. Respinsa: e structural garantat (fiecare linie e
echilibrata prin constructie) -> ar fi un gard care trece mereu. De aceea legarea per-cont la rulaj e miezul.

PROBA: 3 note echilibrate (4111/707 1000, 5121/4111 600, 371/401 400) -> genereaza cu poarta OK, divergente [].
Mutatie 'GL gol' -> ridica numind fiecare cont; 'suma alterata' -> "cont 4111 debit: saft=... vs cale2=1000";
'dezechilibru' -> "DEZECHILIBRU dubla partida". Suita 1409 passed (+5), verificator 0.


## 05.08.2026 — GARD CONTINUT D101 (profit CONTABIL) + D205 (dividende, recalcul propriu) - campania COMPLETA 6/6

D101 (pas 5/6): calea 2 recalculeaza INDEPENDENT P1/P2/P4/P5 (venituri/cheltuieli, clasele 7/6) din inregistrari_linii
si le confrunta cu res.P. Acopera PROFITUL CONTABIL, nu pe cel IMPOZABIL - scris ca atare. TEMEI (verificat la sursa,
d101.py:104-106 + genereaza): doar P1/P2/P4/P5 vin din contabilitate (pull); ajustarile fiscale (P6/P7/P8...) sunt
INTRARI MANUALE ale contabilului (default 0) = §8, iar profitul impozabil P9 e formula pazita de golden
(test_golden_lant_formule_oficiale). Cerinta Costin: "daca ajustarile raman afara, calea 2 verifica doar profitul
contabil - scrie asta". Asa e scris. Non-tautologie AST (nu foloseste calcul_d101/pull; SQL propriu).

D205 (pas 6/6): calea 2 recalculeaza INDEPENDENT baza+impozitul per beneficiar (Σ cont 457 x cota asociat x cota
impozit dividende din common.cota) si le confrunta cu res.beneficiari. NU cross-check D205<->D100 (cerinta Costin:
"verifica pe AST ca nu e capcana paritatii"): D100 declara ACELASI impozit pe dividende, derivat din ACEEASI
distributie (cont 457) -> same-source trap, exact ca paritatea D300/D394 tautologica. Deci recalcul propriu (SQL
propriu + formula proprie), probat non-tautologic pe AST. ALTERNATIVA RESPINSA: cross-check cu D100 (motivul de mai sus).

CAMPANIA COMPLETA (6/6): D300, D394, D112(caz simplu), D406(GL), D101(contabil), D205. Tiparul uniform: recalcul
independent (SQL+formula proprii, non-tautologie probata pe AST), mutatie obligatorie, hard-block la divergenta care
numeste ambele valori, limita de acoperire DECLARATA per declaratie. Golden full-decl (directia a) ramane blocata la
sursa (nu exista exemple ANAF completate).

PROBA: D101 res.P P1=1000 vs mutatie 9999 -> ridica; D205 imp 1600 (16% pe 10000) vs mutatie 1 -> ridica; beneficiar
pierdut -> ridica. Suita 1417 passed (+8), verificator 0.


## 05.08.2026 — PIVOT decizia (c): push pe main NU mai cere aprobarea lui Costin

SUPERSEDEAZA EXPLICIT decizia (c) anterioara ("push pe main = decizia EXCLUSIVA a lui Costin"). Costin a rasturnat-o
05.08.2026.

REGULA FINALA (permanenta): DUPA FIECARE EXECUTIE, fara sa ceara cineva, se face TOT:
  - registrele (GARZI/DECIZII/TESTE/ISTORIC) - §2.2.1, neschimbata;
  - commit local;
  - push pe backup/lant-<data> - ca inainte;
  - push pe main - NOU, fara aprobare.

CONDITIE ABSOLUTA: push pe main DOAR sub POARTA VERDE - pytest cu COLLECTED confirmat (rulat, nu dedus) + verificator
TOTAL 0 + tree curat (git status --porcelain gol). Poarta ROSIE sau TREE MURDAR -> NU se impinge pe main, se
raporteaza si se OPRESTE (WIP salvat). FARA EXCEPTII, fara "repar dupa push". Pe main fast-forward; daca origin/main
a avansat sub tine, pull --rebase INAINTE (memoria main partajat), nu se forteaza niciodata.

TEMEI: intermediarul (push = decizia lui Costin) era o prudenta la inceputul lucrului nesupravegheat; dupa campania
de garduri (poarta pytest+verificator la fiecare commit, hard-block la neconformitate) mecanismul de poarta e
suficient de strans incat push-ul automat sub poarta verde nu adauga risc. Costin decide LANSAREA (piata), nu fiecare push.

UNDE TRAIESTE NORMA: CLAUDE.md (§2.1 rol Code, §2 bucla pas 4, §2.3 pct.3/pct.8, criteriile de oprire) - editate in
ACELASI commit; formularea veche "push pe main = decizia lui Costin" ELIMINATA (nu coexista doua reguli contradictorii).
Raportul §2.2 sect.11 confirma de acum HEAD=origin/main=backup pe acelasi commit.

CONSECINTA ACCEPTATA: un push gresit ajunge direct pe main. Mitigat de poarta verde obligatorie + fast-forward-only +
pull --rebase pe divergenta. ALTERNATIVA RESPINSA: a pastra aprobarea manuala - respinsa de Costin (incetineste fara
sa adauge siguranta peste poarta mecanica).


## 05.08.2026 — EXTINDEREA ACOPERIRII Punctul 1 sub-caz 1a: D112 facilitate la minim (toata luna, full-time)

Campanie noua (extinderea acoperirii, 4 puncte). Punctul 1 = cazurile complexe D112, luate in ordinea prevalentei.
Sub-caz 1a: facilitatea la salariul minim, TOATA luna, full-time, salariu STABIL (fara schimbare in luna).

TEMEI (verificat la sursa INAINTE de cod, common.cota): 2026 S1 sm=4050 facilitate=300 plafon=4300; S2 sm=4325
facilitate=200 plafon=4600; cas=25% cass=10%. Comanda: python -c cota(salariu_minim/facilitate_salariu_minim/...).
Formula generatorului (salarizare.py:60,79-82): facilitate = facilitate_val x facilitate_prorata; baza_contrib =
b_imp - facilitate; cas=baza_contrib x cota_cas, cass=baza_contrib x cota_cass. Pentru minim STABIL toata luna,
facilitate_prorata=1.0 -> facilitate=facilitate_val -> baza=sm-facilitate. calea 2 aplica formula INDEPENDENT cu
valorile din registrul de lege (nu din calcul_salariu).

Detectare independenta a "stabil la minim toata luna": brut(luna_sf)==sm SI nicio intrare salariu_istoric cu
valabil_din IN luna (SQL propriu _stabil_la_minim). Schimbare in luna -> facilitate PRORATATA -> ramane sarit
(sub-caz ulterior, NEACOPERIT numit).

ROTUNJIRE (corectie): generatorul tine cas la 2 zecimale (937.50); D112 il EMITE ca intreg prin _d112int
(ROUND_HALF_UP -> 938). calea 2 confrunta valoarea EMISA: got = _q(g[cas]) rotunjit la intreg, nu int() trunchiere
(bug prins la 937.50->937). Non-tautologic: rotunjirea e spec ANAF, agregarea ramane independenta.

ACOPERIRE: ~20-35% -> ~30-45% estimat (nemasurat). Suprapunerea minim x tichete ramane la sub-cazul 1b.

PROBA: salariat la 4050 toata luna -> generator cas 937.50 (emis 938), calea 2 baza=3750 cas=938, reconciliat;
mutatie cas=999 -> "salariat 3 cas: generator=999 vs cale2=938" ridica. Facilitate proratata (schimbare 2026-06-16)
-> sarit. Non-tautologie tranzitiva neschimbata (doar common.cota adaugat). Suita 1418 passed (+1), verificator 0.


## 05.08.2026 - EXTINDEREA ACOPERIRII Punctul 1 sub-caz 1b: D112 tichete de masa (CAS reconciliat, CASS numit-afara)

Sub-caz 1b: angajat PESTE salariul minim, luna intreaga, full-time, ne-scutit, fara CM, fara alte beneficii
(vacanta/cultural/cresa in beneficii_lunare -> deja sarit prin ben_ids), DAR cu tichet_masa_valoare > 0.

TEMEI / SEMANTICA (verificat la sursa INAINTE de cod, salarizare.py + d112.py):
  - salarizare.py:203-208: baza_contrib = b_imp - facilitate, b_imp = b + exces_vac. Tichetele de MASA nu intra in
    b_imp (doar EXCESUL de tichete de vacanta peste 6 sm intra). Deci cas = baza_contrib x cota_cas si CASS SALARIAL
    (cass = baza_contrib x cota_cass) NU sunt atinse de tichetele de masa.
  - salarizare.py:215-236: tichete de MASA = CASS 10% + impozit 10% pe nominal, FARA CAS, FARA CAM. cass_tichete
    = (tichete_nominal + tichete_vac) x cota_cass, camp SEPARAT.
  - d112.py:239 (build): cass += cass_tichete. Deci CASS-ul EMIS per angajat = s["cass"] (salarial) + s["cass_tichete"].
    pull() pastreaza cele doua SEPARAT (s["cass"]=salarial=brut x cota_cass, s["cass_tichete"]=increment tichete).
  Verificat empiric: salariat 6000+tichet40, pontaj confirmat -> cas=1500, cass=600, cass_tichete=84, tichete_nominal=840.

DECIZIE: calea 2 reconciliaza DOAR CAS = brut x cota_cas pentru angajatii cu tichete de masa (EMIS = reconciliabil,
tichetele nu-l ating). CASS ramane NUMIT-AFARA: CASS-ul EMIS = brut x cota_cass + cass_tichete; a-l recalcula ar cere
re-derivarea cass_tichete (nominal x zile-pontaj x cota_cass) = TAUTOLOGIE cu motorul de tichete + dependenta de
pontaj. Confruntarea componentei salariale (s["cass"]) ar amesteca contractul "confrunta valoarea EMISA" (1a) cu o
componenta intermediara -> RESPINSA ca risc de acoperire falsa (mai bine CASS explicit afara decat un numar partial
prezentat ca "cass reconciliat"). Combo facilitate(la minim)+tichete = sub-caz ulterior, SARIT (ramura brut==sm).

IMPLEMENTARE (core/d112_reconciliere.py): skip-ul neconditionat pe tichet_masa_valoare -> flag are_tichete_masa;
skip ben_ids RAMANE (garanteaza fara vacanta/cultural/cresa -> exces_vac=0 -> DOAR tichete de masa); ramura caz-simplu
confrunta doar "cas" si adauga sid in cheia NOUA reconciliati_cas_doar. Non-tautologie tranzitiva NESCHIMBATA (niciun
import nou; test_non_tautologie ramane verde).

ACOPERIRE: ~30-45% -> ~35-50% estimat (nemasurat; tichetele de masa = beneficiu larg raspandit, dar reconciliaza DOAR
CAS pe ei). De reverificat cu cifra reala cand exista payroll.

PROBA: 8->10 teste in test_d112_reconciliere.py. test_tichete_masa_cas_reconciliat_cass_ramane_afara: cas=1500 &
cass_tichete>0 -> reconciliat_cas_doar; mutatie cas=9999 -> "salariat 7 cas: generator=9999 vs cale2=1500" ridica;
mutatie cass=1 -> NU ridica (limita CASS-afara reala, nu omisiune tacuta). test_tichete_masa_la_minim_ramane_sarit:
combo minim+tichete -> sarit. RED probat: pe codul vechi (git checkout) ambele pica (tichete sarite / cheie inexistenta).
Suita 1420 passed (+2), verificator 0.


## 05.08.2026 - EXTINDEREA ACOPERIRII Punctul 1 sub-caz 1c-PT: D112 part-time suprataxare (CAS+CASS pe baza ridicata)

Sub-caz 1c partea PART-TIME (partea CM ramane separata). Angajat part-time, luna intreaga, ne-scutit
(scutit_contrib_minim=scutit_pt, d112.py:431), fara CM, fara alte beneficii, fara tichete.

TEMEI (verificat la sursa INAINTE de cod): CF art.146 alin.(5^6) + art.168 alin.(6^1) - contributia nu poate fi mai
mica decat cea pe salariul minim brut, la contract cu norma intreaga SAU timp partial (conditia legala e VENITUL sub
minim, nu norma - corectie 15.07). Pragul = sm - facilitate (structura D112: prag_pt, d112.py:449). Proratare pe zile
lucrate (OMF 1855/2022 pct.2, nivel DEJA diminuat - interpretare B, DECIZII 29.07). full month + fara CM ->
zile_lucr=nzl -> prag_zile = prag_pt EXACT (d112.py:517-520), fara dependenta de pontaj.

SEMANTICA EMISIE (d112.py:249-266, 515-525): daca 0<brut<prag_zile -> pt_aplica: B4_8P=cas_min_pt=round(prag x cota_cas),
B4_6P=cass_min_pt, diferenta fata de retinut (B4_8D/B4_6D) pe angajator. Emisul per angajat pe contributie = cas_min_pt
(retinut + diferenta angajator). Peste prag (brut>=prag) -> pt_aplica False, cas/cass pe brut (part-time n-are facilitate,
norma_intreaga=False). Deci EMIS = max(brut, sm-facilitate) x cota, uniform.

DECIZIE: calea 2 reconciliaza COMPLET (CAS+CASS) part-time: exp = _q(max(brut, sm-fac_val) x cota); confrunta emisul
(g[cas_min_pt]/g[cass_min_pt] daca pt_aplica, altfel g[cas]/g[cass]) - valoarea EMISA la ANAF pe baza ridicata. prag
recalculat INDEPENDENT (sm-facilitate din common.cota), nu citit din g[baza_minim_pt] -> non-tautologic. Part-time +
tichete = combo ulterior, sarit. Empiric: brut2025 -> pt_aplica, cas_min_pt=938 (3750x25%), cass_min_pt=375; brut8000 ->
pt_aplica False, cas=2000.

IMPLEMENTARE (core/d112_reconciliere.py): skip part_time -> flag este_pt (skip scutit_contrib_minim ramane);
ramura part-time INAINTE de brut==sm (dupa filtrele cm/ben/luna); part-time -> reconciliati (complet). Non-tautologie
tranzitiva neschimbata (niciun import nou).

ACOPERIRE: ~35-50% -> ~40-55% estimat (nemasurat). Ramas la Punctul 1: CONCEDIILE MEDICALE (1c-CM), sub-caz mai mare.

PROBA: 10->12 teste. part_time sub prag reconciliat + mutatie cas_min_pt=9999 -> "salariat 10 cas: generator=9999 vs
cale2=938"; part_time peste prag reconciliat pe brut + mutatie cas -> "cale2=2000". RED probat (git checkout: part-time
inca sarit -> reconciliati=[1,2,3]). Suita 1422 passed (+2), verificator 0.


## 05.08.2026 - 3 decizii de produs pe inventarul deschiselor non-campanie (Costin)

Grupa D a inventarului (GARZI sectiunea INVENTAR DESCHISE NON-CAMPANIE) = elemente blocate pe o decizie de produs,
nu pe munca sau pe extern. Costin a decis toate trei:

1. **state_plata** (test_datorie:145) - DECIS: **PERSISTARE LA EMITERE CU HASH**. Statul de plata se ingheata la
   emitere (snapshot calculat + hash, ca declaratiile depuse); reafisarea CITESTE snapshotul, nu recalculeaza.
   Motiv: integritate - un stat dat salariatului in ianuarie trebuie sa arate IDENTIC reafisat in iulie, chiar daca
   s-a schimbat cota/salariul minim/codul intre timp. Azi tabela exista dar nimic nu scrie in ea -> recalcul la
   fiecare afisare. Muta din D (cere decizie) in A (actabil azi). Implementare: la emitere salveaza snapshot+hash;
   afisarea citeste snapshotul; recalcul doar INAINTE de emitere.

2. **teste_care_apara_buguri** (test_datorie:235) - DECIS: **FELIA TVA-21% INTAI**. Sweep DOAR pe cele ~15 module cu
   cota TVA 21% hardcodata -> cota din registru (common.cota, period-aware; cota() ridica la expirare). Motiv: 21% e
   cota care CHIAR se va schimba -> expunerea concreta; un test care aserteaza 21% literal apara bugul la schimbarea
   cotei. Restul (~70 teste care aserteaza constante fiscale fara temei) RAMANE in inventar A cu declansator, plan
   separat. Felia TVA-21% muta in A (actabil), restul ramane consemnat.

3. **F144 GV profit/produs** (CSV F144) - DECIS: **LIMITARE ACCEPTATA, DOCUMENTATA**. Gestiunea valorica (GV) ramane
   fara profit pe produs, fiindca costul pe articol nu exista in GV. NU e bug de corectitudine - e scop de
   functionalitate (feature neconstruit). Se documenteaza explicit ca limitare intentionata. Muta din D in C (decizie
   luata). Se redeschide DOAR cu o decizie noua de a construi cost pe articol in GV.

Efect pe inventar: grupa D (3 elemente) -> 0. state_plata + felia TVA-21% -> A. F144 -> C.


## 05.08.2026 — Coduri CM 14 si 18 IMPOZABILE (nu intra in scutirea CF art.62 lit.c)

CF art.62 lit.c scuteste de impozit indemnizatiile pentru: risc maternal, maternitate, cresterea/ingrijirea
copilului, ingrijirea pacientului cu afectiuni oncologice. Setul de coduri neimpozabile = {08,09,15,17,91,92}
(salarizare._CM_COD_NEIMPOZABIL, mapat la structura D112 C2-rows - vezi GARZI 05.08 tura 8). Doua coduri INVECINATE
raman IMPOZABILE, cu distinctia:

- **Cod 14 = neoplazii / SIDA ale ASIGURATULUI insusi** (boala proprie -> incapacitate proprie, ca boala obisnuita).
  Verificat la sursa: OUG 158/2005 art.9 (indemnizatie 100% pt "neoplaziilor, SIDA" ale asiguratului); salarizare.py:404
  ("neoplazii-SIDA"), :464 ("PNS 12/13/14"). NU e "ingrijirea pacientului cu afectiuni oncologice" din art.62 lit.c -
  aceea e INGRIJITORUL (cod 17, in set). Distinctia pacient(14)/ingrijitor(17) e reala si transanta -> 14 IMPOZABIL.

- **Cod 18 = carantina / izolare a copilului** (nu "copil BOLNAV"). art.62 lit.c scuteste "ingrijirea copilului BOLNAV"
  (cod 09/91/92), nu izolarea/carantina unui copil sanatos-dar-expus. LIMITA: nomenclatorul numeric al codului 18 NU e
  in anaf_surse (D_9 vine din Legea 125/2006, necapturata verbatim local); clasificarea "carantina/izolare copil" e
  data de Costin + logica art.62 (nu e "copil bolnav"). Daca apare temeiul care il scuteste (alt alineat art.62 sau
  redefinire nomenclator), se REDESCHIDE decizia. Pana atunci: 18 IMPOZABIL.

Alt temei de scutire cautat: art.62 (celelalte litere) NU acopera nici boala proprie oncologica, nici carantina
copilului -> niciunul nu se scuteste. GARD: test_cm_coduri_14_18_raman_impozabile_decizie_05_08 (pineaza setul; muta 14/18
sau schimba setul fara re-decizie -> pica). Redeschiderea cere modificarea ACESTEI intrari + a gardului.


## 06.08.2026 — C-4 Tranșa 2, Cluster 1: seed firme + alocare tenant + reverificare CUI
- **Decizia 5 Costin (reverificare ANAF v9 la seed) — ÎNDEPLINITĂ.** Cele 11 CUI fictive (M1..T2, lot 95–96M)
  re-interogate ANAF webservice v9 (`core.anaf_api.valideaza_cui`, endpoint PlatitorTvaRest/v9/tva) la 2026-08-06:
  toate 11 `gasit=False` (0 firme reale) → NU s-a folosit rezerva (96756476/96939899). Proba în ISTORIC tura 16.
- **Alocare tenant (stabilă, R2):** M1=tenant_002, M2=tenant_003, P1=tenant_004, P2=tenant_005, N1=tenant_006,
  S1=tenant_007, S2=tenant_008, S3=tenant_009, NR1=tenant_010, T1=tenant_011, T2=tenant_012 (S4=tenant_001 tranșa 1),
  toate sub Cabinet Prisma firm_id 1968. Numerele ies din ordinea provizionării în seed (idempotentă pe CUI+firmă).
- **regim_fiscal S3 = 'micro' (placeholder).** S3 e agricultor forfetar (art.315^1), regim nemodelat ca valoare
  distinctă în firma_profil.regim_fiscal (câmp text liber micro/profit); S3 e neplătitor TVA și nu depune D101/D300,
  deci valoarea nu afectează livrabilele tranșei 2. De reconfirmat dacă tranșa 3 (D100/D406 S3) cere altă valoare.


## 06.08.2026 — C-4 Tranșa 2: perioada fiscală TVA trimestrială (D300/D394/D390) — CONSTATARE + design recomandat
Constatare (probă în GARZI 06.08 + ISTORIC tura 16): D300/D394 nu agregă trimestrul pentru plătitorii trimestriali;
produc declarații DUK-valide dar sub-raportate (P2 Q2 omite aprilie T-2). d394.tip_d394 hardcodat "L". Reparația e
clară pe temei (CF art.322) DAR atinge forma API-ului de perioadă → design de confirmat cu Costin înainte de refactor:
- **Opțiunea A:** caller-ul (declaratii_api/UI) pasează trim=Q pentru firmele trimestriale; genereaza calculează
  eticheta luna=sfârșit-trimestru (3/6/9/12) pentru XML. Curat conceptual, dar UI trebuie să știe perioada firmei
  (există în firma_profil.tip_decont → derivabil).
- **Opțiunea B (RECOMANDATĂ de executor):** genereaza citește tip_decont din profil și, dacă T/S/A, remapează
  luna-ancoră → fereastra corectă intern, DECUPLÂND „luna-etichetă din XML" (3/6/9/12) de „fereastra de date"
  (trimestrul). Minim invaziv pe caller (declaratii_api/UI rămân neatinse), localizat în d300/d394/d390.
Ripple de gestionat la reparație (oricare opțiune): d300.valideaza (regula luna∈{2,3,5,6,8,9,11,12} pentru T — de
reconciliat cu noul model), nr_evidenta/scadenta (folosesc luna), D390 (aceeași clasă). Fiecare cu gard + RED/GREEN +
DUK. NEDECIS — recomandarea B stă până confirmă Costin; nu blochează alt lucru (firmele lunare merg).


## 06.08.2026 — Optiunea B IMPLEMENTATĂ (perioada fiscală TVA trimestrială D300/D394)
Decizia de design de mai sus (06.08) — REZOLVATĂ cu opțiunea B, aprobată de Costin. Fereastra de date urmează vectorul
fiscal (tip_decont), decuplată de eticheta luna din XML; declaratii_api/UI NEATINSE. tip_decont citit din vector
(nu presupus); lipsă → eroare. Fixturile care generau D300/D394 fără tip_decont (test_d394.PROF, test_achizitii_factura)
au primit tip_decont='L' explicit (23 teste, foloseau default-ul tăcut eliminat). Detaliu GARZI 06.08.


## 06.08.2026 — D300 taxare inversă: AUTO furnizor (rd.13) / MANUAL beneficiar (decizie Costin)
Fix aplicat pentru bug-ul „D300 furnizor pierde livrarea cu taxare inversă". Decizie Costin (opțiunea 1):
- **Latura beneficiarului (rd.12 colectat + rd.27 deductibil, net zero) RĂMÂNE MANUALĂ** — e o decizie contabilă
  (auto-taxare art.331), cu gardul existent `test_taxare_inversa_rd12_se_declara_manual` NEATINS.
- **Latura furnizorului (rd.13) devine AUTO** — NU e o decizie contabilă, e un fapt deja în sistem (factură emisă cu
  flag `taxare_inversa`). Omiterea ei din rd.13 era pierdere de informație, nu design → se derivă automat.
Implementare: `calcul_d300` rutează emisă+taxare_inversa → rd.13 (bază fără TVA); primita+taxare_inversa EXCLUSĂ din
auto-deducere (altfel dublează manualul beneficiarului). GARDĂ ANTI-DUBLĂ-NUMĂRARE: dacă rd.13 vine ȘI auto ȘI manual
(R13_1) → EROARE vizibilă, nu însumare tăcută. `d300.pull` citește `taxare_inversa`; `d300_reconciliere` aliniat
(exclude taxare inversă din cale2, ca `calcul_d300`). Seed T-6 S1: factura primită păstrează cota 21 (pt D394 tip C);
D300 beneficiar se completează manual la generare — codul nou nu mai auto-deduce, deci fără dublă numărare.


## 06.08.2026 (tura 2) — C-4 Tranșa 2 predare: item (e) T-5 forfetar livrat + clasificarea restului
**Livrat (bug C-4 real).** T-5 achiziție de la agricultor forfetar (S3→P1, art.315^1): `calcul_d300`
derivă TVA din COTĂ și ignoră antetul facturii → compensația forfetară 8% (antet `tva`=2000, cotă linie 0)
cădea tăcut în `alte_a` cu un avertisment GENERIC ("cotă în afara 21/11/9") care nu numea suma; cumpărătorul
P1 putea pierde deducerea (art.315^1 al.17) → TVA de plată supraevaluată. FIX (commit d1a2e4d): TVA orfan
din antet (antet − rânduri pe cotă) la achiziții primite, semnalat CANTITATIV — după precedentul avertismentului
9% deductibil. NU se auto-deduce (lipsă flag "în Registrul agricultorilor" = decizie de produs, "nu se forțează"
per C4_date.md) și NU se schimbă XML → rămâne DUK-valid. Gard `test_d300_forfait_agricol.py` (RED probat pe cod
vechi + bidirecțional: sub-raportare/supra-corecție + DUK). Suită 1465 passed, verificator 0.

**Clasificare la sursă a restului predării (proba contrarie stabilită per item — nu bug C-4 reachable):**
- **(b) D390 P1 achiziție IC = coverage-seed.** Codul e deja corect: `d390.pull` cade `c.cui → tert_cui` (bug
  reparat 16.07.2026, cu comentariu în sursă); o factură primită cu `tert_cui` prefix UE → tip A. Lipsește doar
  seed-ul (niciun partener UE în seed). Blast-radius pe seed-ul partajat (schimbă D300/D394 P1) → coverage pe
  schemă efemeră, nu pe seed.
- **(c) D301 N1 = coverage-seed.** `d301.pull` citește tabelul `d301_operatiuni` (NU facturi; `d301.py:239`),
  gol în seed; generatorul e deja DUK-valid (clustere închise). Pragul L10 (10.000 EUR, obligația de depunere
  art.317) NEENFORCED = decizie de produs (aceeași clasă ca L3/395k).
- **(d) D300 pe marjă S1/S2 = DECIZIE DE PRODUS.** `tva_marja`/`tva_marja_turism` sunt STANDALONE, neimportate
  în `core/d300.py`; endpoint-urile `main.py` postează doar ciorne în `inregistrari`. Nicio operațiune pe marjă
  nu ajunge în D300 (observație deja declarată: "neintegrat în datorie.py = observație"). Integrarea cere model
  nou (flag/tabel pentru operațiunea pe marjă) → greenlight Costin.
- **(f) Limite TVA L1/L2/L3/L4/L10/L12 = clasă mixtă.** L4 (plafon TVA la încasare) e ENFORCED period-aware
  (`common.py:393`, `COTE["plafon_tva_incasare"]`) și deja testat. L1 (micro→profit 100k), L2 (lunar/trim 100k),
  L3 (scutire 395k), L10 (10k IC) sunt NEENFORCED — regim/perioadă/statut plătitor se fixează MANUAL în seed
  (GARZI:1555, C2_firme "limite declarate") = C-5/decizie de produs → prag±1 NU e C-4 (CONFIRMĂ lecția tranșei 1).
  L12 (storno/retur/ajustare) e structural (rânduri negative), fără caz ±1.

**Oprire §2.3 pct.6** (buget context) la graniță curată. Actionabil rămas FĂRĂ decizie de produs = coverage-seed
(b)+(c) pe schemă efemeră; blocat pe decizie = (d) marjă + (f) L1/L2/L3/L10 (enforcement praguri).


## 06.08.2026 (tura 3) — C-4 Tranșa 3 ÎNCHISĂ (anuale + tranziția de an) — ultima tranșă C-4
**Livrat (bug reachable reparat):** D101 crăpa (`ValueError`) la orice apel prin API cu `ca_an_precedent_eur`
(injectat de `declaratii_api._d101`, respins de `calcul_d101`). Fix: `genereaza` scoate cheia și porează
eligibilitatea IMCA (CF art.18^1 alin.1): sub 50 mil euro → nu se aplică; peste prag fără P47 → eroare clară;
peste prag cu P47 → generează. Gard `test_d101_imca_ca_precedent.py` (RED + API-path + DUK + mutație). Detaliu GARZI.

**Decizii de produs DESCHISE (reziduu C-4, nu blochează — greenlight Costin pt o campanie ulterioară):**
1. **Perioadă fiscală parțială / regim dual pe an (T1 înființare mid-an, T2 micro→profit mid-an):** motoarele
   D101/bilanț presupun Jan1–Dec31 fix; nu există câmp `data_infiintare`, nici împărțire de an, nici comutare de
   regim. „D101 pro-rata din trimestrul de tranziție" (T2) și „bilanț parțial" (T1) = model nou. Împerecheat cu
   enforcement-ul pragului CA (golul de praguri, tura 2 — L1 micro→profit).
2. **D207 nerezidenți (NR1, art.231):** neimplementat integral (fără generator/api/test). Declarație nouă.
3. **IMCA pe calea DB:** VT/Vs/I/A nu se derivă din balanță; după fix, IMCA e accesibil doar prin P47 manual /
   `calcul_d101(imca=)`. Wiring-ul complet (pull IMCA) = decizie de produs (niciun firmă C-4 nu-l atinge, <50 mil).

**Verificat conform (fără bug):** D392 NU se depune (intenționat, C4_date.md:108); decembrie/granița de an corectă
(D300/D112/D394/D406 12/2026 pe fereastra corectă); D205 = dividende (salariile în D112).

**Notă T1 bilanț:** sumele ies corecte (fereastra Jan–Dec prinde doar iul–dec, nimic înainte de înființare);
rămâne doar inacuratețea antetului Data_I (01.01 în loc de 01.07) — impact fiscal minim, corectare = decizie produs.

**C-4 COMPLET (3 tranșe):** T1 salarizare (închisă), T2 coerență+TVA (închisă), T3 anuale+tranziție (închisă azi).

## 06.08.2026 — A6: D394 linie scutită către CUI — proba DUK FĂCUTĂ (închide DATORIE 31.07)

O livrare (tip L) cu cotă 0 către un partener RO cu CUI era IGNORATĂ cu avertisment (dropată din op1), deși
rezumat1 R41.1 cere „cota 0 → facturiLS indiferent de partener" iar R38.2 interzice facturiL la cota 0. FIX
(`core/d394.py`): se reclasifică L→LS (livrare scutită) în loc de drop tăcut. Temei: pct.215 interzice N la
tip_partener=1; V=taxare inversă (deja rutată); AS e pentru achiziții — deci LS e SINGURA încadrare validă a
unei livrări cota-0 către RO CUI. Reconcilierea a-doua-cale (`d394_reconciliere`) acoperă doar cota>0 → neafectată.

Marker stabil: **d394 linie scutita catre cui proba duk facuta**.

PROBĂ: factură MULTI-COTĂ exact cazul din datorie — 21% (bază 1000) + 11% (bază 500) + scutit cota 0 (bază 300)
către RO14399840 → DUK `stare=valid`; linia scutită încadrată LS (prezentă în `res.op1`, `tip="LS"` în XML), NU
mai apare avertisment de ignorare. Test: `core/test_d394.py::test_d394_scutit_livrare_ro_cui_inclus_ca_LS_nu_dropat`.

## 06.08.2026 — #12: salariul minim din lună = cea mai mică valoare (art.77 alin.3)

CF art.77 alin.(3) teza finală, verificat VERBATIM în `anaf_surse/cod_fiscal_227_2015_consolidat.html`:
„În situația în care, în cursul aceleiași luni, se utilizează mai multe valori ale salariului minim brut pe
țară, se ia în calcul valoarea cea mai mică a salariului minim brut pe țară." Același principiu explicit la
plafonul de 20% facilitate (art.76). NU e regulă din pliant — e text de lege la MO.

`cota("salariu_minim", la_data)` întorcea valoarea LA DATA, nu minimul din lună. FIX:
`common.salariu_minim_luna(la_data)` întoarce cea mai mică valoare activă în lună; rutate siturile de calcul
lunar (salarizare: deducere art.77(3), facilitate art.76, plafon CM 12sm + d112 salariul minim lunar).

Marker stabil: **salariu minim cea mai mica valoare din luna tratat**.

PROBĂ: test unitar pe o lună cu DOUĂ valori (5000 de la 1, 5200 de la 15) → alege 5000. No-op pe date reale:
D112 tenant_001 2026-07 **BYTE-IDENTIC** cu/fără fix (sha256 `ea0520b0c8b2eb0c`, len 12379) → zero regresie.
Nicio lună reală n-are încă două valori (schimbările de salariu minim sunt la granița de lună: 4050 ian-2025,
4325 iul-2026), deci regula nu bite azi — dar e implementată corect pentru când va fi. Test:
`core/test_12_salariu_minim_luna.py`.

## 06.08.2026 — #10: deducere art.77(4) "4 si peste" = 45% confirmat la MO (inchide xfail)

Sursele secundare se contraziceau (45% vs 40%). Sursa MO LOCALA anaf_surse/cod_fiscal_227_2015_consolidat.html
contine tabelul art.77(4) VERBATIM: "Persoane aflate in intretinere ... 4 si peste ... 1 salariu minim ->
45,00%" (scara 20/25/30/35/45). Codul (salarizare.py _deducere_personala_2018) foloseste 45% -> COINCID.
nivel_sursa ridicat REDARE->MO+verbatim pe temeiul scarii. Codul NU s-a schimbat (valoarea era corecta).
Marker: **deducere 45% 4+ verificat in monitorul oficial**.

## 06.08.2026 — #11: deducere 100 lei/copil necablata + gard defensiv

Marker: **deducere 100 lei/copil - functionalitate necablata, gard defensiv pus, cablarea completa in §PRODUS
cu temei art.77(10)b/(12)/(13)**. copii_scoala nu e coloana pe salariati; apelantii reali (d112/stat_plata)
trec 0 -> deducerea de 100 lei/copil NU se acorda azi (cod mort). Gard defensiv (salarizare.py
_deducere_personala_2018): ridica daca copii_scoala>0 fara flag declaratie_copii, citand art.77(12)-(13) ->
la cablare esueaza vizibil, nu acorda dublu. Cablarea completa (input copii scolarizati + declaratie parinte
+ UI) = build-new, in §PRODUS. Proba: D112 byte-identic cu/fara gard (copii_scoala=0 pe date reale).

## 07.08.2026 — CM: model de EPISOD (reparatie calcul fiscal, OUG 158/2005 art.17(1))

Indemnizatia CM se calculeaza pe EPISOD (art.17(1): "raportat la fiecare episod de boala"), nu pe certificat
izolat. Verificat verbatim la MO: anaf_surse/oug_158_2005_consolidat.html. TREI defecte din aceeasi lipsa, reparate:
1. Procentul (55/65/75) pe zile_episod (suma certificatelor episodului), NU pe zilele certificatului curent.
   Inainte: episod 7+13 zile = 55%+65% (660+1560=2220); acum = 75% pe tot (2850) -> +630 lei/episod sub-platiti
   la baza 200 lei/zi.
2. Diminuarea de 1 zi (Ordinul 506/1030/2026) O DATA pe episod (pe certificatul initial), nu pe fiecare certificat.
3. Portia angajator (zilele 2-6, Norme OUG 158/2005) O DATA pe episod (pe initial); pe continuari zile_ang=0.
   Al treilea defect - aceeasi lipsa de model; fara el, continuarile ar emite D_20 gresit.

Legatura episodului: contabilul bifeaza "certificat de continuare" + seria/numarul certificatului INITIAL
(transcriere de pe hartie, NU deductie). Recalcul RETROACTIV al certificatelor anterioare NECONFIRMATE. Un
certificat de continuare care ar recalcula o perioada CONFIRMATA e REFUZAT cu INSTRUCTIUNE (firma + luna +
cat creste in lei + "deschide perioada / depune D112 rectificativa") - decizie Costin 07.08 (respecta lock-ul
perioadei). Design System cap.6 (mesaj de eroare = instructiune).

art.XI L141/2025: PLUMBAT (data_episod_initial -> alege_varianta pe data certificatului INITIAL), dar INERT azi -
forma pre-141 (75% uniform, art.17(1) anterior 1 august 2025) NU e in _VARIANTE_PROCENT_CM (blocat pe sursa
verbatim, xfail #16 ramane DESCHIS). Granita 31 iulie 2025 vs 1 august 2025 nu se poate proba pana intra forma pre-141.

Migrare core/migrare_cm_episod.py (12/12 scheme, backup pre_cm_episod_20260807_095848.dump). Backfill: fiecare
rand existent = propriul episod -> D112 BYTE-IDENTIC (sha ea0520b0c8b2eb0c) pe date reale, ZERO re-calcul. DUK pe
D112 cu episod 20 zile @75% = valid (singura observatie = avertisment preexistent salariat 4, nelegat de CM).
Gard: core/test_cm_episod.py. NEFACUT: sugestia AUTO de legare (heuristica salariat+cod+zile adiacente) - calea
manuala (autoritara) e completa; sugestia = follow-up usor.

## 07.08.2026 — #16 INCHIS: CM art.XI L141/2025 - forma pre-141 (75% uniform) la MO

Forma art.17(1) OUG 158/2005 ANTERIOARA Legii 141/2025 obtinuta verbatim la MO
(anaf_surse/oug_158_2005_pre_L141.html, forma consolidata valabila la 7 martie 2025, ultima inainte de L141):
"se determina prin aplicarea procentului de 75% asupra bazei de calcul stabilite conform art. 10" - procent
UNIC 75% pentru cod 01, fara diferentiere pe durata (fara lit. a/b/c). Verificat: contine 75% verbatim, ZERO
aparitii de 55%/65%, alin.(2) 100% pentru tuberculoza/SIDA/neoplazii/infectocontagioase grupa A/urgente/arsuri.

Implementat: _procent_cm_pre_141 (75% uniform cod 01; restul codurilor delegate la forma post-141, neatinse de
L141/2025) + varianta datata in _VARIANTE_PROCENT_CM. Selectia formei: art.XI L141/2025 - dupa data
certificatului INITIAL al episodului (data_episod_initial, deja plumbat in modelul de episod). Granita: art.IX
L141/2025 (MOF 699 din 25 iulie 2025) in vigoare la 1 august 2025 (art.X).

Marker: **cm art xi regim dupa certificat initial verificat la sursa**.

PROBE: cert initial 31 iulie 2025 -> 75% uniform (5 si 20 zile); cert initial 1 august 2025 -> 55% (5 zile) /
75% (20 zile); granita 31 iulie (0.75) vs 1 august (0.55); coduri speciale 100%/85% identice in ambele regimuri.
No-op pe date reale: D112 byte-identic (ea0520b0c8b2eb0c), datele reale fiind 2026 = post-141. Ambele forme
nivel_sursa=MO+verbatim. Gard: core/test_cm_episod.py (test_art_xi_granita_pre_post_141, test_coduri_speciale_neatinse_de_l141).

## 07.08.2026 — B1: plafon_facilitate_salariu_minim 2025 = 4300 (OUG 156/2024 art.LXVI) + B1 = CLASA

Lipsea plafon_facilitate_salariu_minim @2025 din common.py -> calcul_salariu pe orice luna din 2025 ridica
PerioadaIndisponibila. Adaugat un rand DATAT: @1 ianuarie 2025 = 4300 lei.

Sursa MO+verbatim (anaf_surse/oug_156_2024.pdf, OUG 156/2024 art. LXVI alin.(1) lit.b): "venitul brut realizat
din salarii ... fara a include contravaloarea tichetelor de masa, voucherelor de vacanta, respectiv indemnizatia
de hrana ... nu depaseste nivelul de 4.300 lei inclusiv"; "se aplica veniturilor aferente lunilor ianuarie -
decembrie 2025 inclusiv". Confirmat: 4.300 (NU 4.000, care era iulie-decembrie 2024 prin OUG 115/2023 art.LXXIII).
Marker: **plafon facilitate salariu minim 2025 verificat la sursa oug 156/2024**.

FINDING (PASUL 4, generalizare): B1 NU e un singur rand - e o CLASA. DATA_START_SISTEM = 1 ianuarie 2025
(2023/2024 = sub podea, nereparabile by design). Pentru 2025, dupa adaugarea plafonului, calcul_salariu MAI
ridica pe **tichet_masa_plafon @2025** (definit doar de la 1 ianuarie 2026). Deci 2025 ramane BLOCAT pana se
adauga si valoarea nominala maxima a tichetului de masa in 2025 (indexata semestrial, Legea 165/2018 art.32;
NU e in anaf_surse - doar cadrul general). tva_redusa @martie 2025 lipseste dar NU e folosit de salarizare.

Probe: plafon @2025-03 = (4300, OUG 156/2024 art.LXVI); no-op 2026 D112 byte-identic (ea0520b0c8b2eb0c);
regresie salarizare 36 passed. Granita facilitatii (brut sub/peste 4300) NU se poate proba prin calcul_salariu
pana nu intra si tichet_masa_plafon 2025.

## 07.08.2026 — B1/tichet_masa_plafon 2025: 3 intervale + gol octombrie + corectie data_in 45

Trei valori datate, verificate VERBATIM la sursa:
- 40,04 lei @1 ianuarie 2025 (ian-mar 2025) - Ordinul MF 4.679/2024 (anaf_limite_2025.pdf). NU 956/2024 (sursa secundara gresita).
- 40,18 lei @1 aprilie 2025 (apr-sep 2025) - Ordinul MF 484/2025 (anaf_limite_2025.pdf), data_out EXPLICIT 30
  septembrie 2025 (sfarsit de acoperire; aug+sep incluse explicit in ordin). NU 484/280 (sursa secundara gresita).
- 45 lei @1 noiembrie 2025 (nov 2025+) - Legea 201/2025 art.I pct.1 ("nu poate depasi suma de 45 lei") + art.II
  alin.(1) ("se aplica incepand cu drepturile aferente lunii noiembrie 2025") - legea_201_2025.html verbatim.
Marker: **tichet masa plafon 2025 verificat la sursa (ordin 4679/2024, ordin 484/2025, legea 201/2025)**.

REPARATIE (nu efect colateral): randul de 45 lei era @2026-01-01 (GRESIT) - Legea 201/2025 se aplica de la
NOIEMBRIE 2025. Noiembrie-decembrie 2025 erau tratate GRESIT (nu doar neacoperite). Corectat data_in @2026-01 ->
@2025-11. 2026 ramane 45 (D112 byte-identic ea0520b0c8b2eb0c).

EXTENSIE _deriva_data_out: respecta un data_out EXPLICIT oriunde e setat (nu-l suprascrie din succesor).
Verificat: nicio valoare COTE existenta n-are data_out explicit -> comportament identic pt cele existente.
Necesar ca 40,18 sa NU se propage TACIT peste OCTOMBRIE 2025 (gol de sursa) - o valoare fiscala fara temei.

DESCHIS: octombrie 2025 (o luna) - cere Ordinul MF pentru tichetul de masa semestrul II 2025 (negasit local;
ordin_1574_3246_2025_cultural = tichete CULTURALE, nu de masa). Pana atunci calcul_salariu(octombrie 2025) ridica
blocaj motivat ("gol in registru"), NU o valoare inventata. calcul_salariu(2025) merge peste tot except octombrie.

## 07.08.2026 — Corpus (1): legarea temeiurilor COTE la fisiere locale + ridicare MO (13 valori)

Verificate VERBATIM act cu act (in fisierele deja locale), apoi nivel_sursa REDARE->MO + url la fisier + text_citat:
- cod_fiscal_227_2015_consolidat.html: cas 25% (art.138a), cass 10% (art.156), cam 2,25% (art.220^3 alin.1),
  impozit_micro 1% (art.51 alin.1), impozit_profit 16% (art.17), impozit_venit 10% (art.64 alin.1).
- legea_141_2025_consolidat.html: tva_standard 21% (Art.II pct.42), tva_redusa 11% (pct.42), impozit_dividend 16% (Art.II pct.1).
- cf_art291_2016_forma_initiala.txt: tva_redusa_9 9% (art.291 alin.2), tva_redusa_5 5% (art.291 alin.3).
- salariu_minim: url EXTERN (legislatie.just.ro, BLOCAT de pe server) CORECTAT -> fisier LOCAL: 4050 (HG 1506/2024
  art.1), 4325 (HG 146/2026 art.1).
Rezultat: COTE MO+local 4 -> 17. Zero acte aduse. D112 byte-identic (ea0520b0c8b2eb0c) - doar temeiuri, nicio valoare.

RAMAN REDARE (16, raportate act cu act):
- ACTE LIPSA local: facilitate_salariu_minim (OUG 115/2023, OUG 89/2025), plafon_facilitate @2026 (OUG 89/2025),
  plafon_avans (OUG 115/2023), plafon_mijloc_fix 5000 (OUG 8/2026), plafon_tva_incasare (Legea 296/2020, OUG 8/2026),
  plafon_sold_casa (Legea 70/2015), impozit_dividend 8% @2023 (OG 16/2022).
- FORME ISTORICE neacoperite de fisierele locale: tva_standard 19% @2017 (forma 2016=20%, consolidat=21% - lipsa 2017),
  plafon_mijloc_fix 2500 @2015, impozit_dividend 5% @2016 (doar fisier de NOTE, nu MO), comasarea tva_redusa_9/5->11%
  @2025 (neconfirmat specific pct.42/43).
Finding: cod_fiscal_227 e CONSOLIDAT LA ZI (post-141/OUG 89) -> NU contine formele istorice -> confirma nevoia gardei 2 (forma acopera perioada).

## 07.08.2026 — Corpus (2): manifest anaf_surse/INDEX.json + 3 garzi peste registrul de temeiuri

Plus legat: tva_redusa_9 @2025 (11%, art.291 alin.2, Legea 141 pct.42) -> MO (aceeasi baza verbatim ca
tva_redusa alin.2). tva_redusa_5 @2025 (alin.3 abrogat de pct.43) RAMANE REDARE: unde ajung fostele
operatiuni de 5% dupa abrogare (11% vs standard) nu e confirmat verbatim -> de DECIS. COTE MO+local 17->19.

MANIFEST anaf_surse/INDEX.json (regenerabil: anaf_surse/gen_index.py): harta fisier-sursa -> {tip_forma,
cote acoperite}. tip_forma declarat manual: consolidat_la_zi (cod_fiscal_227, legea_141) vs forma_la_data
(forme initiale / HG-uri / ordine / liste ANAF la o data fixa).

CELE 3 GARZI (core/test_corpus_surse.py):
- G1 test_temei_mo_are_sursa_locala: nivel_sursa=MO => url catre anaf_surse/ + fisier EXISTENT pe disc.
- G2 test_forma_consolidata_nu_e_sursa_pentru_valoare_cu_succesor: o forma consolidat_la_zi nu poate fi
  sursa pt o valoare care are un succesor mai nou (forma la zi n-o mai contine). Prinde exact riscul gasit:
  cod_fiscal_227 e consolidat LA ZI -> nu contine formele istorice. Formele forma_la_data sunt exceptate.
- G3 test_cote_volatile_fara_mo_set_fix: warning la generare (avertizeaza_cote_volatile_fara_mo) DOAR pt
  valoarea CURENTA (data_in max) a unei cote, non-MO SI (volatila: >=2 intrari SAU recenta: +/-18 luni).
  PRAG ALES: 18 luni. Motiv: taie complet zgomotul pe cele 29 REDARE stabile-vechi cu o singura intrare;
  semnaleaza doar ce e viu si de sursat/decis. SET masurat la 2026-08-07 (5, fixat in test, nu ghicit):
  facilitate_salariu_minim, plafon_facilitate_salariu_minim, plafon_mijloc_fix, plafon_tva_incasare
  (toate 4 = OUG 8/2026 + OUG 89/2025, acte de adus) + tva_redusa_5 (comasare de decis).

Bug prins la masurare: garda 3 lua initial intrari[-1] = cea mai VECHE (COTE e ordonat descrescator);
corectat la max(intrari, key data_in) = valoarea curenta. Fara masurare ar fi semnalat exact valorile istorice.

## 07.08.2026 — Corpus (3): OUG 8/2026 + OUG 89/2025 aduse local, 6 valori legate verbatim -> MO

OUG 8/2026 (anaf_surse/oug_8_2026.html) - confirmat verbatim, act cu act:
- plafon_tva_incasare 5.000.000 (1 mar-31 dec 2026) + 5.500.000 (de la 1 ian 2027): art.282 alin.(3) lit.a/b CF.
- plafon_mijloc_fix 5.000 (2026): art.28 alin.(2) lit.b CF.
OUG 89/2025 (anaf_surse/oug_89_2025.html) - confirmat verbatim:
- facilitate_salariu_minim 200 (iul-dec 2026): art.III alin.(1).
- plafon_facilitate 4.300 (ian-iun 2026) + 4.600 (iul-dec 2026): art.III alin.(1) lit.b).
  Verificat inainte de a atinge metadata: lit.b din COTE e CORECT (lit.a=salariul de baza egal cu minimul;
  lit.b=venitul brut, fara tichete, <= plafon). Nu am corectat nimic - era deja corect.

RAMANE REDARE (raportat, nefortat): facilitate_salariu_minim 300 @2025 - OUG 89/2025 mentioneaza 300 lei
DOAR pt perioada 1 ian-30 iun 2026, NU pt 2025; sursa lui 2025 (OUG 115/2023) nu e adusa.

NEASTEPTAT in cele doua acte:
1. plafon_mijloc_fix 5.000 "se actualizeaza anual, in functie de indicele de inflatie, prin HG" (art.28 alin.2
   lit.b) - deci valoarea poate creste anual prin HG viitoare, nu e fixa.
2. TVA la incasare intra la 5M de la 1 MARTIE 2026 (nu 1 ian); art.9 OUG 8/2026 confirma ca ian-feb 2026 raman
   la 4,5M (perioada de tranzitie). COTE avea deja data_in 2026-03-01 - corect.
3. Ambele acte citeaza pragurile VECHI doar ca referinta de tranzitie (2.500 mijloc fix, 4,5M TVA) - NU le
   surseaza; acele valori istorice raman REDARE (sursele lor primare nu-s aduse).

Rezultat: COTE MO 18->24, REDARE 15->9. D112 byte-identic (ea0520b0c8b2eb0c) - doar temeiuri, nicio valoare.
Garda 3 dupa: semnaleaza DOAR tva_redusa_5 (decizie de produs, nu act lipsa). Cele 4 plafoane au iesit din set.

REDARE ramase (9): tva_standard 19% @2017, tva_redusa_5 11% @2025 (de decis), impozit_dividend 5% @2016 +
8% @2023, plafon_tva_incasare 4,5M @2021 (Legea 296/2020), plafon_mijloc_fix 2.500 @2015 (Legea 227 forma
initiala), plafon_sold_casa 50.000 (Legea 70/2015), plafon_avans 5.000 (OUG 115/2023), facilitate 300 @2025
(OUG 115/2023). Toate istorice (recalculari retroactive) sau decizie - niciuna valoare curenta vie fara sursa.


## 08.08.2026 — Restart prod dupa deploy + mecanism "running == HEAD" (detector vizibil, NU auto-restart)

**Decizie (aprobata Costin):** dupa un fix de COD, serviciul se REPORNESTE (`sudo systemctl restart iconta-nou`)
si efectul se PROBEAZA live, nu se presupune. Facut azi pentru DEFECT-1 (d112/schema) si DEFECT-3 (stat-plata).
Temei: DEFECT-1 a aratat ca "publicat pe git" != "ruleaza in productie" — prod a rulat cod din 1 august, 45+
commituri in urma, cu un blocaj (D112 500) invizibil oricui privea doar git-ul sau suita.

**Mecanism de clasa "running == HEAD" — ALES: detector vizibil periodic, NU auto-restart in post-commit.**
Temei: constrangerea lui Costin "sa nu repornesti serviciul in mijlocul unei operatii a unui contabil" EXCLUDE
varianta post-commit-reporneste (post-commit se declanseaza la momente arbitrare). Detectorul nu reporneste
niciodata; un OM reporneste la fereastra sigura; driftul devine ZGOMOTOS (banner + sentinela `.git/RUNNING_STALE`
+ alerta), nu tacut — exact ce a lipsit 6 zile. Include raport PATRU-way (HEAD = origin/main = backup = RUNNING;
raportul nu e "incheiat" cat timp procesul viu != HEAD) + audit al migrarilor prod vs HEAD (schema PUBLIC, care nu
are inca gard — template-guard-ul acopera doar schemele de tenant). Necablat inca — campanie separata. Candidatul
de clasa e in GARZI 07.08.

## 08.08.2026 — Fix DEFECT-3 pe AMBELE fete + ratchet pe catch-uri (in loc de fix-total)

**Backend:** `perioada.py` (e_confirmat/confirma/deconfirma) primea `schema` dar folosea `perioada_confirmata`
NECALIFICAT -> 500 pe o conexiune fara search_path pe tenant. Fix: `_tbl(schema)` califica cand schema e dat.
Clasa: 5 rute payroll/documente (stat-plata/fluturas/pain001 x2/balanta) pasau `schema` unui helper tenant pe
`db.get_conn()` gol -> conformate la `db.get_conn(schema)`. Convenția "helper-ele folosesc nume necalificate ->
apelantul deschide get_conn(schema)" era DEJA documentata (comentariul _schema_cabinet_sau_404); cele 5 o incalcau.
stat-plata = confirmat crapa (UndefinedTable, RED->GREEN); restul conformate (nu au crapat pe datele S4).

**Frontend (decizia de fond):** un `catch{}` gol care inghite un fetch PRIMAR si randeaza o stare goala e mai
GRAV decat un ecran care crapa — minte plauzibil, contabilul depune gresit fara sa stie ca serverul a esuat.
Reparate cele 4 cele mai grave (evidente financiare/legale care mint: stat-plata, casa/registru, RIP, jurnal) cu
ramura de EROARE VIZIBILA (rosu, "Nu am putut incarca... — asta NU inseamna fara date"), pastrand navigarea.

**Ratchet (decizie de guvernare, NU fix-total):** harta = 17 catch-uri periculoase; nu se repara toate acum
(ar fi un refactor de ~17 ecrane, buget). Gardul `test_catch_vizibil.py` pune un RATCHET (baseline 54 de
catch-goale-langa-api): nicio CALE NOUA nu mai intra, iar repararea din rest COBOARA baseline in acelasi commit.
Ratchet in loc de fix-total = opreste regresia clasei fara sa blocheze livrarea pe reparatia integrala.


## 08.08.2026 - PIVOT: eliminarea raportului SCURT; un singur format de raport (11 sectiuni)

SUPERSEDEAZA: incadrarea COMPLET / SCURT introdusa in CLAUDE.md §2.2 pe 02.08.2026 (nu exista ca intrare DECIZII
separata - a trait doar in regula §2.2). INTERMEDIAR (02.08 -> 08.08): raportul avea doua forme - COMPLET (titlu
+ sectiunile 1-10) pentru inchideri de cluster / logica fiscala, si SCURT (titlu + sectiunile 1, 2, 5) pentru
modificari de registru / infrastructura / un singur pas. FINAL (08.08): UN SINGUR FORMAT. Orice executie produce
titlu + TOATE sectiunile 1-11, in ordine. O sectiune care nu se aplica se scrie EXPLICIT "N/A - <motiv>",
niciodata prin omisiune; nu exista submultime de sectiuni care se pot sari, nu exista "N/A colectiv".

TEMEI (proces, nu fiscal): forma SCURT permitea sarirea sectiunilor 3, 4, 6-11 - exact sectiunile care tin
executorul cinstit (proba, temei, decizii cerute, generalizare pe clasa, garduri, efect pe produs, registre
actualizate). O campanie "de un singur pas" care sare proba si generalizarea ascunde tocmai unde se pierde
disciplina. Costin: "nu exista raport SCURT. Raportul are 11 pozitii obligatorii, toate."

PROBA: CLAUDE.md §2.2 - blocul "CAND SE APLICA ... COMPLET / SCURT" inlocuit cu "UN SINGUR FORMAT ..."; §2.3
pct.7 "sectiunile 1-10" -> "TOATE sectiunile 1-11"; grep dupa "SCURT" / "sectiunile 1-10" / "sectiunile 1, 2, 5"
in CLAUDE.md = NICIUNA (commit 543a367, 08.08.2026).


## 08.08.2026 — PIVOT scope batch 3 (G10): PREDARE_LANT supersedează GARZI; no-op sha256 pe AMBELE ieșiri

Constatare (turele de CITIRE batch 3, 08.08): cele două registre divergeau pe scope-ul batch 3, așa cum a fost
găsit la sursă:
- GARZI ("08.08 — G10: e-Transport = ABATERE cunoscuta, tratat la BATCH 3") numea DOAR e-Transport și cerea proba
  no-op sha256 DOAR pe XML e-Transport.
- PREDARE_LANT ("08.08 seara, G10 Faza 2") adăuga emitere ca al doilea ecran (3b) ȘI extindea no-op sha256 pe
  factura generată, nu doar pe XML.

PIVOT (supersedează EXPLICIT redarea din GARZI): PREDARE_LANT e mai nou și mai complet; batch 3 = e-Transport (3a)
+ emitere (3b), iar proba no-op sha256 acoperă IEȘIREA REALĂ a fiecărui ecran — XML pentru e-Transport, factura
(linii + `totaluri_din_linii` PURE) pentru emitere. Motiv: o probă no-op care nu atinge ieșirea reală a ecranului
NU dovedește că restructurarea n-a schimbat ce pleacă la ANAF / la contabil; trebuie să hash-uiască exact
artefactul pe care-l produce ecranul.

PROBĂ: e-Transport sha256 XML = 480d4bf2… (frontend vechi == nou, set complet); emitere sha256 factură = 2197a759…
(facturi_api vechi == nou, total=423.50 / tva=73.50). Ambele garduri headless hash-uiesc ieșirea reală, în poartă
(test_etransport_randuri_dinamice.py / test_emitere_randuri_dinamice.py).

## 08.08.2026 — Detector "running == HEAD" VIZIBIL IN APP (superadmin) LIVRAT (mecanism 1 din decizia iulie)

Comanda Costin (executie): cablat DETECTORUL vizibil inainte de urmatoarea parcurgere (nu dupa), ca sa nu mai stea pe premisa neverificata (prod a rulat cod din 1 aug, 45 commituri in urma, 6 zile tacut). LIVRAT partea vizibila in app: commitul rulat se stampileaza in memorie la pornirea procesului (core/versiune.py, in lifespan) - fidel procesului viu, NU dedus din mtime-uri; `/admin/versiune` (superadmin-only) compara cu HEAD; banner `.caseta-atentie` in desktopAdmin DOAR la divergenta, DOAR superadmin. NU reporneste, NU repara (constrangerea din iulie respectata; post-commit neatins). Gard test_running_head.py + mutatie. Mecanismul (2) cron/sentinela/Brevo + (3) raport patru-way + auditul schema PUBLIC = scop separat, necablat aici (comanda a cerut semnalul vizibil in app).

## 09.08.2026 — D112 v1.03-072026: doar D_14a/D_15a/D_16a inchise; restul raman datorie (verbatim sau deloc)

Comanda Costin (executie): D112 pe structura in vigoare (Ordin comun 605/95/928/2314/2026, 07/2026), campuri
confirmate VERBATIM din corpus; ce nu se confirma ramane in GARZI. DE CE doar 3 din 13:
- D_14a/D_15a/D_16a au definitie verbatim (rd.103a/104a/105a) SI operanzi existenti in aplicatie (za/zf) =>
  actabile. D_16a=D_14a+D_15a e singura formula-agregat data explicit pe zile.
- Celelalte 10 pica testul "verbatim sau deloc" pe UNUL din doua motive: (a) structura NU da formula (B3_7D,
  C_10D - doar antet; D_20a/D_21a - doar descriere narativa "diferenta recalculata", nu mecanismul), sau (b) cer
  date pe care aplicatia nu le are (D_9a program national, E3_97 pensii ocupationale) ori o regula de calcul
  neimplementata (D_9b diminuare 1 zi). A emite valori deduse (ex. C2_155=0) ar incalca "nicio formula dedusa".
TEMEI: anaf_surse/structura_D112_0726_030826.pdf (rd. citate), anaf_surse/d112_06082026.xsd (tipuri: toate 13
atribute confirmate; C2_155/C2_156 uppercase in XSD). PROBA (autoritatea J27, NU structura): kit D112 upgradat
08.08 (D112Validator.jar bak_pre_J27_20260808); XML 07/2026 cu CM cod 01 -> fara fix: 3 erori "atributul trebuie
sa existe" + S103a/S104a; cu fix: DUK stare=VALID. Nivel sursa: XSD/structura = REDARE oficiala; DUK J27 = autoritate.
Gating (an,luna)>=(2026,7): structura spune "se aplica din 01.07.2026"; regenerarea unei luni < 07/2026 pastreaza
structura veche, altfel DUK ar respinge structura anterioara.

## 09.08.2026 — Publicarea completa = patru pasi, automata dupa poarta verde (four-way)

Comanda Costin (executie): dupa fiecare executie cu poarta verde, cei patru pasi de publicare (commit, push
origin/main+backup, deploy, restart) se fac AUTOMAT, fara sa fie ceruti in comanda; publicarea nu e completa pana
cand procesul viu nu ruleaza codul comis (four-way running==HEAD). DE CE: publicarea se oprea la disc pentru ca
deploy-ul si restartul depindeau de ce isi amintea sa ceara cel care compunea comanda; detectorul running==HEAD
(DECIZII 08.08) semnala divergenta, dar nimeni n-o repara (la aceasta comanda procesul rula 6589873 din 03:26 in
timp ce HEAD era f20ee85).

CE ERA DEJA (verificat, nu presupus - chestionar pct.4): push-ul pe origin/main SI backup e DEJA regula scrisa
(CLAUDE.md §2.3 pct.8, decizia c 05.08) SI cablat mecanic (post-commit hook, 07.08) -> three-way. Lipseau doar
pasii 3-4 (deploy + restart) si a patra latura de confirmare (RUNNING).

CE SE SCHIMBA: CLAUDE.md §2.3 pct.10 NOU (patru pasi + four-way, cu stop point pastrat pe restart vizibil); §2.2
sect.11 extins de la three-way la four-way (HEAD = origin/main = backup = RUNNING = <hash>, start-time dupa commit).

DE CE executor, nu hook: pasii 1-2 sunt stare remote fara risc vizibil -> cablati in post-commit. Restartul are
stop point uman (comportament vizibil utilizatorului; utilizatori activi -> eventual fereastra = decizie de produs)
-> NU se cableaza orb (ar reporni prod la fiecare commit); ramane pas de executor, obligatoriu, cu raportare
inainte. Coerent cu decizia iulie "detector vizibil, NU auto-restart" (DECIZII 08.08): auto-restartul orb ramane
interzis; ce devine obligatoriu e restartul CONSTIENT al executorului dupa poarta verde.

TEMEI: CLAUDE.md §2.3 pct.8 (push three-way) + §2.2 sect.11, core/versiune.py (detector running==HEAD),
iconta-nou.service (WorkingDirectory=/home/costin/iconta_nou -> deploy = HEAD pe disc). Registrul care face regula
sa supravietuiasca schimbarii de sesiune = CLAUDE.md (incarcat la fiecare sesiune) - acolo intra pct.10.

## 09.08.2026 — OUG 91/2025 (diminuare CM 1 zi): nucleul aplicatiei CONFORM cu textul oficial; 5 divergente ca intrebari

Comanda Costin (executie): adu textul oficial OUG 91/2025 + norme, stabileste verbatim regula, compara cu app,
repara ce e verbatim, listeaza restul. REZULTAT: aplicatia implementa DEJA diminuarea (chestionar pct.4 confirmat -
nu presupun lipsa) si, pe aspectele pe care textul le spune CLAR, COINCIDE cu el - deci nucleul NU necesita reparatie.

TEMEI (verbatim, sursa oficiala legislatie.just.ro, aduse in corpus):
- OUG 91/2025 art.II(1) (MO 1223/31.12.2025): "certificatele ... eliberate in perioada 1 februarie 2026-31
  decembrie 2027 ... se calculeaza si se platesc prin diminuarea cu o zi"; a) angajator zilele 2-6, b) FNUASS ziua
  urmatoare; art.II(2): ziua diminuata "constituie stagiu de asigurare".
- Legea 64/2026 (MO 416/15.05.2026): alin.(1^1) "o singura zi, indiferent de numarul certificatelor" (episod
  fara intrerupere); alin.(4) exceptii art.2(1) lit c)/d^1)/e) + programe nationale; alin.(5) spitalizare;
  art.VI(4) exceptiile alin.(4)/(5) se aplica de la 01.06.2026.
- Ordin 506/1030/2026 art.78^4(4) (MO 507/19.06.2026): "Ci = Mzbci x ....% x (NZLCM - 1) ... minus prima zi
  LUCRATOARE" - REZOLVA ambiguitatea zi calendaristica vs lucratoare: e ZI LUCRATOARE (constrangerea "nu alegi tu"
  nu s-a aprins - norma alege). Exemplul normei (442 lei) reprodus de gard.
- OUG 158/2005 art.2(1): c)=maternitate, d)=ingrijire copil bolnav, d^1)=oncologic, e)=risc maternal.

DE CE nucleul e conform: app calculeaza NZLCM-1 (o zi lucratoare), o data/episod (prima_zi_din_episod),
in fereastra 2026-2027 (variante datate), exceptand 08/15/17 (=lit c/d^1/e) + spitalizare, angajator 5 zile /
FNUASS din 7; ziua diminuata nu reduce niciun stagiu. Proba before->after: episod 20 zile (init 7 + cont 13),
media 200 -> 3000 lei fara diminuare, 2850 cu diminuare (dif -150 = o zi x 200 x 75%%, o data pe initial, din FNUASS).

CE RAMANE (5 divergente, NEatinse - vezi GARZI 09.08 tura 4): (1) izolare cod 51 - CONFLICT norma (se diminueaza)
vs ANAF D112 (exceptat); (2) faza excepatiilor 01.06.2026 vs aplicarea din 01.02.2026 in app (certificate
02-05.2026); (3) programe nationale pe coduri regulate - BLOCAT_DATE (marcaj lipsa, ~D_9a); (4) gating pe
data_inceput vs "eliberate" (data_acordare); (5) cod 02 accident - nomenclator neconfirmat. Toate afecteaza
LUNI INCHISE si/sau sunt ambigue -> NU le-am atins (stop point "raportezi inainte de a atinge sume pe luni
inchise" + "nu alegi interpretarea"); le pun ca decizii pentru Costin.

## 09.08.2026 — CM OUG 91/2025: 4 decizii de calcul (izolare, faza excepatiilor, cod 02, gating)

Comanda Costin (executie): din cele 5 divergente CM (GARZI 09.08 tura 4), patru se implementeaza acum, a
cincea se amana. Cele patru decizii, cu temeiul fiecareia:

1. **Izolare (cod 51): SE DIMINUEAZA.** Temei: Ordin 506/1030/2026 art.78^4 alin.(2^1)/(2^2) NU listeaza
   izolarea printre exceptii (doar art.2(1) lit c/d^1/e + programe nationale + spitalizare); OUG 91 art.II(1)
   mentioneaza izolarea DOAR la suportare (lit a) -> trece pe FNUASS, b(ii) "a 2-a zi"), NU la diminuare.
   Norma de calcul PREVALEAZA asupra formatului de raportare D112 (care o excepta - structura_D112 p.2). Verificat
   la J27: emiterea unui D112 cu CM 51 diminuat NU declanseaza nicio regula impotriva reducerii (erorile vazute =
   D_12 obligatoriu la 51 + agregatul C2 pentru randul izolare - completitudine generator D112, separat, neatins
   per constrangere). Daca apare conflict la validare, se raporteaza; NU se rezolva platind altfel decat norma.

2. **Exceptiile de la diminuare se aplica de la 01.06.2026, nu de la 01.02.2026.** Temei VERBATIM: Legea 64/2026
   art.VI(4) "Prevederile art. II alin.(4) si (5) se aplica ... incepand cu data de 1 a lunii urmatoare intrarii
   in vigoare a legii de aprobare" (Legea 64 in vigoare 18.05.2026 -> 01.06.2026). Implementat: varianta datata
   2026-02-01 (diminuare FARA exceptii) + 2026-06-01 (diminuare CU exceptii 08/15/17 + programe nationale +
   spitalizare). Certificate 02-05.2026 cu aceste coduri: se diminueaza.

3. **Cod 02 (si 03/04): RAMAN NEDIMINUATE.** Temei: Nomenclator 9 (anaf_surse/d112_struct_anaf.txt) le
   clasifica "accident ... neconfirmat de casa de pensii" in G1 (incapacitate temporara); asimilarea accidentelor
   de traseu/munca la Legea 346/2002 (cand se confirma) NU e rezolvata verbatim in OUG 91/Ordin 506, iar Legea
   346/2002 NU e in corpus. Decizie Costin "cod 02 nu alegi tu, listezi" -> raman nediminuate pana la confirmare.
   LIPSA (de adus): Legea 346/2002 + o afirmatie verbatim ca accidentele "neconfirmate" sunt/nu sunt supuse
   diminuarii OUG 91.

4. **Gating pe DATA ELIBERARII certificatului.** Temei VERBATIM: OUG 91 art.II(1) "certificatele de concediu
   medical ELIBERATE in perioada 1 februarie 2026-31 decembrie 2027". Implementat: dispecerul de variante
   (calcul_cm) alege pe data_eliberare (= data_acordare), nu pe data_inceput; apelantul (salariati_api) o
   transmite. Fallback pe la_data daca lipseste.

5. Programe nationale pe coduri regulate: AMANATA (decizie de produs - marcaj pe certificat, ~D_9a). Neatinsa.

PROBA pe date reale (tenant_001, read-only): din 11 CM, UN singur certificat schimbat de corectie - id=46
(05/2026, cod 08 maternitate): 3034 -> 2832 lei (-202, o zi lucratoare; maternitatea se diminueaza in 05.2026,
exceptata abia din 06.2026). ZERO luni depuse/confirmate la ANAF afectate (stop point neaprins). Nu s-a modificat
nicio valoare stocata (doar calculul; recalculul efectiv al lunilor = a doua comanda).

## 09.08.2026 — Corpus (pasul 3, amanat 08.08): 7 acte aduse, 4 temeiuri COTE ridicate la MO, 1 stop point

Comanda Costin (executie): completeaza corpusul - toate actele pe care aplicatia le invoca drept temei si nu au
sursa locala. Sursa oficiala legislatie.just.ro (local; server-ul ramane blocat la download).

ADUSE (7, forma consolidata "(A)"): anaf_surse/ legea_346_2002_consolidat.html, oug_115_2023_consolidat.html,
legea_296_2020_consolidat.html, legea_70_2015_consolidat.html, og_16_2022_consolidat.html,
legea_136_2020_consolidat.html, oug_34_2024_consolidat.html.

RIDICATE REDARE->MO dupa verificare VERBATIM in fisierul adus (act cu act; valoarea de cod NEATINSA - doar
metadata nivel_sursa/url/text_citat; cele 4 valori confirmate neschimbate; INDEX.json regenerat):
- impozit_dividend 8% @2023 -> OG 16/2022 ("cota de impozit de 8% asupra dividendului brut", art.43 alin.2 CF).
- plafon_tva_incasare 4.500.000 @2021 -> Legea 296/2020 ("cifra de afaceri ... nu a depasit plafonul de 4.500.000 lei").
- plafon_sold_casa 50.000 @2015 -> Legea 70/2015 ("plafon zilnic de 50.000 lei/tranzactie").
- plafon_avans_decontare 5.000 @2023 -> OUG 115/2023 (modifica Legea 70/2015 art.4 lit.e: "plafon zilnic de 5.000 lei").
Gard: G1 (test_corpus_surse) - MO => fisier local existent; mutatie probata (sters og_16 -> G1 rosu; restaurat -> verde).

STOP POINT (act adus NU confirma valoarea din cod): facilitate_salariu_minim 300 @2025 citeaza OUG 115/2023, dar
OUG 115/2023 NU contine cei 300 lei (doar o amenda). RAMANE REDARE, neatins. Candidatul real = OUG 156/2024
(deja local, art.LXVI; structura D112: "Suma300 cf.OUG156/2024") - re-citarea = tura non-read-only, decizie separata.

pct.4 Legea 346/2002 (blocheaza cod 02/03/04): adusa + verificata. CONFIRMA accident de munca + boli profesionale
(cod 03/04 = domeniul ei, NU OUG 158). NU acopera explicit "accident de traseu/deplasare" (cod 02) in forma
actualizata la 2011. Nomenclator 9 (d112_struct): 02/03/04 "neconfirmat de casa de pensii" = G1 (incapacitate,
OUG 158) cat timp neconfirmate. Decizia cod 02/03/04 ramane a lui Costin (nu am atins codul de calcul).

RAMAN REDARE (raportate, nu inchise - forma consolidata la zi NU le confirma):
- Legea 227/2015 valori istorice: tva 19% @2017, dividend 5% @2016, plafon mijloc fix 2.500 @2015 - superseded;
  CF consolidat (local) nu le contine. Necesita forma-la-data (CF forma de baza 08.09.2015, just.ro/171282).
- tva_redusa_5 @2025 (abrogare alin.3 de L141 pct.43): unde ajung fostele operatiuni de 5% (11% vs 21%) NU e
  confirmat verbatim -> DE DECIS (Costin), nu verificare.

## 09.08.2026 (tura 7) — Cele 4 pozitii deschise din corpus: 3 corectate verbatim, 1 propunere

Comanda Costin: fa ce se poate, propune ce nu. Separ ce e sprijinit de act de rationamentul propriu.

POZ.1 facilitate_salariu_minim 300 @2025 - CORECTAT (temei gresit). SPRIJINIT DE ACT: OUG 156/2024 art.LXVI
alin.(1) VERBATIM "suma de 300 lei/luna ... nu se cuprinde in baza lunara de calcul al contributiilor sociale
obligatorii" (venit brut <= 4.300 lei). Re-citat OUG 115/2023 -> OUG 156/2024 (deja local), REDARE->MO. Valoare
300 NEschimbata -> ZERO efect in bani. (Chestionar pct.4 confirmat: poz.1 = corectura de temei fara bani.)

POZ.2 tva_redusa_5 @2025 - CORECTAT (nu era "alegere", actul transeaza). SPRIJINIT DE ACT: Legea 141/2025 pct.42,
CF art.291 alin.(2) lit.g) "manuale scolare, carti, ziare si reviste" + lit.h) "acces la castele, muzee ...
monumente" = cota redusa 11%. RATIONAMENT PROPRIU (marcat): locuintele sociale (fost alin.3 lit.c) NU apar in
lista alin.(2) -> trec la 21% standard; categoria "5%" s-a SPLIT. Valoarea 0.11 e corecta pt operatiunile reduse
supravietuitoare (carti/cultural), care sunt cele folosite in D301; locuintele domestice nu trec prin aceasta
cota. REDARE->MO. ZERO efect in bani (0.11 neschimbat; locuintele nu erau calculate via aceasta cota).

POZ.3 valori istorice - CORECTAT toate 3 (aduse forme-la-data). SPRIJINIT DE ACT:
- tva_standard 19% @2017: CF forma initiala 2015 (anaf_surse/cf_2015_forma_initiala.html) art.291 alin.(1) lit.b)
  "19% incepand cu data de 1 ianuarie 2017". REDARE->MO.
- impozit_dividend 5% @2016: OUG 50/2015 (oug_50_2015_consolidat.html) art.97 alin.(8) "Cota de 5% ... dividende
  distribuite incepand cu data de 1 ianuarie 2016". Temei corectat Legea 227/2015->OUG 50/2015 (CF initial spune
  5% "din 2017"; OUG 50/2015 accelereaza la 2016). REDARE->MO.
- plafon_mijloc_fix 2.500 @2015: HG 276/2013 (hg_276_2013.html) "valoarea de intrare a mijloacelor fixe ... este
  de 2.500 lei". Temei corectat Legea 227/2015->HG 276/2013 (CF art.28 trimite la HG; 2.500 NU e in CF). REDARE->MO.
ZERO efect in bani (valorile neschimbate; corectii de temei/sursa).

POZ.4 cod 02 (accident de traseu) - PROPUNERE (actul primar NU transeaza). SPRIJINIT DE ACT: Nomenclator 9 + 10
(anaf_surse/d112_struct_anaf.txt) clasifica 02/03/04 "neconfirmat de casa de pensii" in G1 = incapacitate
temporara (OUG 158); OUG 91/Ordin 506 diminueaza indemnizatiile OUG 158 mai putin exceptiile (art.2(1) lit
c/d^1/e + programe nationale + spitalizare), in care 02/03/04 NU intra. LIPSA verbatim primar: Legea 346/2002 NU
contine "traseu/deplasare" - defera la Legea 319/2006 (ABSENTA din corpus) pt definitia accidentului.
POZITIA MEA ASUMATA: **cod 02/03/04 SE DIMINUEAZA** cat timp sunt "neconfirmate" (paltite ca OUG 158/G1, deci
urmeaza aceeasi diminuare ca celelalte coduri G1). Dupa confirmarea casei de pensii trec la FAAMBP (Legea 346),
ies din sistemul CM. DE CE: clasificarea operativa (cum sunt declarate/paltite acum) primeaza; exceptia e o lista
inchisa in care accidentele nu figureaza. EFECT IN BANI: -1 zi lucratoare/episod pe codurile 02/03/04 (~150-200
lei/episod). RISC daca gresesc (accidentele trebuie protejate de diminuare): subplata cu 1 zi, reversibila; 0
certificate reale (tenant_001 n-are 02/03/04), 0 luni depuse. NEATINS codul de calcul (propunere, nu executie);
daca accepti, aplic + aduc Legea 319/2006 pt confirmarea primara.

## 09.08.2026 (tura 8) — Cod 02/03/04 SE DIMINUEAZA (propunere aplicata) + Legea 319/2006 in corpus

Comanda Costin: aplica propunerea pe cod 02/03/04 si adu Legea 319/2006. Propunerea din tura 7 (poz.4) ACCEPTATA.

TEMEI (verbatim, adus azi): Legea 319/2006 (anaf_surse/legea_319_2006_consolidat.html, forma consolidata) art.5
lit.g): "accident de munca - vatamarea violenta a organismului ... care au loc in timpul procesului de munca sau
in indeplinirea indatoririlor de serviciu"; include "accidentul de traseu ori de circulatie ... persoane
angajate". Coroborat cu Nomenclator 9/10 (d112_struct): 02/03/04 "neconfirmat de casa de pensii" = G1
(incapacitate temporara, OUG 158) cat timp neconfirmate; Legea 346/2002 (FAAMBP) le preia DUPA confirmare
(atunci ies din sistemul CM). => cat timp sunt in D112 ca neconfirmate, se platesc OUG 158/G1 -> se diminueaza.

FACUT: eliminata exceptia accidentelor din core/salarizare.py (_CM_COD_ACCIDENT_NECONFIRMAT scos). Cod 02/03/04
se diminueaza acum cu 1 zi lucratoare/episod ca orice cod G1 (SINGURELE exceptii ramase = Legea 64 alin.(4)/(5):
08/15/17 + programe nationale + spitalizare, de la 01.06.2026). Izolare 51 se diminua deja.

EFECT IN BANI: -1 zi lucratoare/episod pe codurile 02/03/04 (~150-200 lei/episod, dupa media si procent). Pe date
reale: 0 (tenant_001 n-are certificate 02/03/04), 0 luni depuse afectate (stop point neaprins). Certificate viitoare
02/03/04 in fereastra 01.02.2026-31.12.2027: diminuate.

Supersedeaza decizia din tura 4/7 ("raman nediminuate pana la confirmare"): confirmarea a venit (Legea 319/2006 +
Nomenclator). Gard: core/test_cm_episod.py::test_cod_02_03_04_se_diminueaza (mutatie: re-exceptare -> rosu).

## 09.08.2026 (tura 9) — D112 D_9a: marcaj "program national de sanatate" pe certificatul CM (date -> ecran -> D112)

Comanda Costin: construieste locul de intrare pentru D_9a (blocat pe date) si emite-l in D112. STRUCTURA VERBATIM
(structura_D112_0726_030826.pdf rd.98a, XSD IntInt1_1SType): D_9a N(1), "9.1 - se bifeaza pentru CM acordate
pacientilor inclusi in programele nationale de sanatate" (se aplica din 07/2026). Conditie de completare = BIFA
per certificat (structura o da explicit ca marcaj) -> se poate EMITE verbatim.

CONSTRUIT (DB -> ecran -> D112):
- DB: concedii_medicale.program_national boolean DEFAULT false (core/migrare_program_national_cm.py, idempotent,
  aplicat pe 12 tenanti; mirror in tenant_template.sql). Migrare aditiva metadata-only (ADD COLUMN IF NOT EXISTS)
  - NU atinge date existente (fara rescriere).
- Ecran: flux_concediu.js - checkbox .set-bifa "Pacient inclus in program national de sanatate (D112 D_9a)" +
  payload program_national. Regula DS REUTILIZATA (checkbox cu eticheta v2.11 .set-bifa) - NICIUN tipar nou ->
  nicio regula noua in DESIGN_SYSTEM/verificator (citata la capul patch-ului frontend).
- Persistenta: salariati_api.salveaza_concediu stocheaza program_national; d112.pull il citeste in dict.
- D112: asiguratD emite D_9a="1" cand marcajul e setat (gated >=07/2026). J27: DUK stare=VALID, 0 erori.
- Calcul: program_national exceptat de la diminuarea de 1 zi (Ordin 506/1030/2026 art.78^4 alin.(2^1) "bolnavilor
  inclusi in programele nationale"), FAZAT 01.06.2026 (Legea 64 art.VI(4)) - inchide gapul "programe nationale pe
  coduri regulate" din GARZI (acum exista marcajul, nu doar codurile 12/13/14).

EFECT IN BANI: marcajul nou (0 certificate existente il au) -> 0 acum. Certificate viitoare cu program national:
D_9a="1" in D112 + exceptat de la diminuare (de la 01.06.2026). Nicio munca in plus obligatorie pt contabil (bifa
optionala, default nebifat).

## 09.08.2026 (tura 10) — E3_97 plafon 400 EUR: cautat la sursa; curs si excedent NU-s reglementate verbatim -> decizie Costin

Comanda Costin: nu presupune - cauta cursul/cumulul/excedentul plafonului de 400 euro. CAUTAT (act cu act):
- CF art.76 alin.(4^1) lit.e^1) (cod_fiscal_227_2015_consolidat.html): "contributiile la un fond de pensii
  ocupational potrivit Legii nr.1/2020 ... in limita a 400 euro anual pentru fiecare persoana" (OUG 8/2026 pct.30,
  de la 01.03.2026). => defineste plafonul (400 EUR ANUAL/persoana) dar NU cursul, NU excedentul.
- CF art.76 alin.(4^2): "Ordinea in care veniturile prevazute la alin.(4^1) se includ in plafonul lunar de cel
  mult 33% ... se stabileste de angajator." => doar ORDINEA. NU exista alin.(4^3).
- CF art.76 alin.(4): curs pt avantaje in natura (alin.3): "cursul de schimb comunicat de BNR valabil pentru
  datele respective" - context ALTUL (avantaje alin.3, nu plafoanele EUR din 4^1).
- CF art.78 alin.(2) lit.a): "cursul leu/euro comunicat de BNR, in vigoare in ULTIMA ZI A LUNII pentru care se
  platesc drepturile salariale" - context ETF (deducere plafon anual), NU atasat lui art.76(4^1).
- OUG 8/2026 art.10 alin.(10): pt pensii ocupationale se iau in calcul "contributiile platite incepand cu data de
  1 martie 2026" => confirma CUMULUL (anual, de la 01.03.2026).
- HG 1/2016 (norme metodologice CF, adus azi in corpus): "pensii ocupationale" NEGASIT (normele sunt anterioare
  OUG 8/2026 care a introdus lit.e^1; nu acopera mecanismul).

REZULTAT pe cele 3 aspecte:
- CUMUL: REGLEMENTAT (400 EUR anual/persoana; de la 01.03.2026). Distributia pe luni a campului D112 lunar E3_97
  NU e specificata.
- CURS: NEATASAT lui art.76(4^1) - doi candidati divergenti (art.76(4) "valabil pentru datele respective" vs
  art.78(2)(a) "ultima zi a lunii"). NU se poate alege verbatim.
- EXCEDENT: doar IMPLICIT (peste plafonul de 33% + plafoanele individuale -> impozabil); NICIO fraza verbatim
  "partea care depaseste ... este venit impozabil" pt (4^1) in sursele cautate.

Pct.2 (alte plafoane in valuta in app): curs_bnr.py trateaza cursul BNR general PENTRU FACTURI (nu salarii);
aplicatia NU trateaza niciun plafon EUR de salariu (pensii facultative/sanatate/ocupationale) si nici plafonul
lunar de 33% din art.76(4^1). Deci NICIUN analog de reutilizat sau de contrazis (stop point 2 neaprins).

DECIZIE: per "verbatim sau deloc" + stop point ("mecanismul chiar nu e reglementat: te opresti pe E3_97"), NU
construiesc emisia/plafonarea E3_97 (curs+excedent neconfirmate). Ramane decizia lui Costin: (i) ce curs se
foloseste (art.76(4) vs art.78(2)(a)); (ii) cum se trateaza excedentul (impozabil, unde); (iii) metoda de
colectare (A: contabilul introduce partea neimpozabila lunara; B: app aplica plafonul). D_9a ramane livrat (tura 9).

## 09.08.2026 (tura 11) — E3_97: curs+cumul CONFIRMATE verbatim (corectie tura 10); build oprit pe stop point #2 (subsistem 33%)

Comanda Costin: cursul e reglementat in alt articol - confirma si construieste. CORECTIE la tura 10 (unde am
spus "curs neatasat"): cursul ESTE reglementat, prin lantul verbatim art.78(2)(a) + OUG 8/2026 art.10(9).

CONFIRMAT VERBATIM (act local):
- CURS: CF art.78 alin.(2) lit.a) (introdus de OUG 8/2026 pct.34): "Pentru verificarea incadrarii in plafonul
  anual, cursul de schimb utilizat pentru determinarea echivalentului in euro este cursul leu/euro comunicat de
  Banca Nationala a Romaniei, in vigoare in ULTIMA ZI A LUNII pentru care se platesc drepturile salariale." Se
  leaga de art.76(4^1) prin OUG 8/2026 art.10 alin.(9): "la verificarea incadrarii in limita echivalentului in lei
  a 400 euro anual prevazuta la art. 6 pct. 26, 29, 32 si 36 ..." - pct.29 = art.76(4^1) lit.e (angajator) ->
  aceeasi verificare anuala in euro guverneaza familia de plafoane art.76(4^1), inclusiv e^1 (pensii ocupationale).
- CUMUL: anual, in EURO, per persoana; pentru ocupationale de la 01.03.2026 (OUG 8/2026 art.10 alin.(10)).
  Verificarea = cumul in euro pe parcursul anului (fiecare luna convertita la cursul ultimei zile a lunii).
- EXCEDENT: doar IMPLICIT (art.76(4^1) neimpozabil "in limita"; art.76(4^2) doar ordinea). ALEGEREA lui Costin
  (constrangere): partea peste plafon = IMPOZABILA (venit din salarii). Declarat ca alegere, nu ca temei.
- OUG 8/2026 NU are curs propriu (foloseste cel din art.78(2)(a)); are doar cumulul de tranzitie 2026 (art.10(9)/(10)).
- App (pct.2): core/curs_bnr.py da deja cursul BNR (leu/euro, ultima zi) - REUTILIZABIL pt conversie. App NU are
  niciun plafon art.76(4^1) si nici plafonul lunar de 33%.

STOP POINT #2 APRINS (build oprit inainte de a construi): E3_97 e in art.76(4^1) -> neimpozabil DOAR in limita
plafonului LUNAR de 33% (pe SUMA tuturor art.76(4^1) a-j) + plafonul EUR + ordinea (art.76(4^2), angajator).
33% POATE MUSCA: exemplu, o contributie lumpy de 2.020 lei intr-o luna pe salariu minim (4.325) depaseste 33% =
1.427 lei -> impozabil, chiar in cadrul plafonului anual EUR. Aplicatia NU tine niciun element art.76(4^1) si nici
plafonul de 33% -> constructia CORECTA a E3_97 cere subsistemul, nu doar plafonul EUR. Ce presupune subsistemul:
  (a) plafonul lunar de 33% din salariul de baza, pe SUMA elementelor art.76(4^1) (a-j);
  (b) cele 10 elemente (a-j) ca intrari (app are 0; E3_97 ar fi primul);
  (c) ordinea de includere in plafon (art.76(4^2), decisa de angajator);
  (d) plafoanele EUR (e:400 facultative, e^1:400 ocupationale, f:400 sanatate, h:100 sport) cu cumul in euro;
  (e) rutarea excedentului (peste 33% SAU peste plafonul EUR) in baza impozabila.
METODA (decisa de Costin, scrisa aici): B - aplicatia aplica plafonul, contabilul introduce contributia BRUTA.

DECIZIE CERUTA (scope, chestionar pct.6): (A) construiesc E3_97 ACUM cu plafonul EUR (400/an, curs art.78(2)(a),
cumul euro) + plafonul de 33% aplicat pe E3_97 ca UNIC element art.76(4^1) urmarit (corect pt datele curente,
extensibil), sau (B) construiesc subsistemul complet art.76(4^1) (a doua comanda). Nu am construit nimic in aceasta
tura (stop point #2 "te opresti inainte de a-l construi").

## 09.08.2026 (tura 12) — "Probat" = prin /auth/login (calea browserului), NU pe hash; 4 conturi test probate real

Costin a semnalat ca cele 4 conturi nu se logheaza si ca "probat" nu inseamna acelasi lucru. CLARIFICARE onesta:
in tura anterioara NU am probat niciun cont prin autentificare si NU am creat conturile - scrierile au fost
BLOCATE de clasificator, iar raportul a spus VERDICT: NEEDS INPUT (conturi "de creat - blocat", fara parole).
Nu a existat o proba de autentificare (deci nici una falsa de reprodus); tabelul cu 4 emailuri fara parole a fost
insa inselator ca "conturi date" - imi asum formularea.

STANDARD FIXAT (metoda): a PROBA un cont = POST /auth/login (auth_api.login: verifica activ + firma_activa +
parola, apoi lockout/beta la endpoint), NU verifica_parola pe hash. Un hash valid poate trece pe DB in timp ce
loginul din browser esueaza (activ=false -> AUTH_ESEC; firma suspendata; beta 403; lockout 429). GARD:
core/test_login_proba_metoda.py - cont cu hash VALID + activ=false trece verifica_parola dar PICA la login();
activ=true -> login() reuseste. Mutatie: daca login() n-ar verifica activ, assert (2) pica.

CAUZA reala a "nu se logheaza": in tura trecuta nicio parola n-a fost setata (scrieri blocate) -> niciun
credential functional. Endpoint-ul /auth/login e corect (401 la parola gresita, 200 la parola corecta). Poarta
beta NU blocheaza (200, nu 403). Acum scrierile de cont au fost permise -> conturile create + PROBATE prin
/auth/login (toate HTTP 200 + token).

CONTURI TEST create (rol / email / firma; parolele DOAR in raportul din chat, nu aici):
- administrator (superadmin): admin@prisma-cont.test (NOU, firma null).
- cabinet (admin_firma): patron@prisma-cont.test (existent, parola resetata; Cabinet Contabil Prisma SRL, id 1968).
- asistent (angajat): asistent@prisma-cont.test (NOU, firma 1968, poate_pregati=true, valida/depune=false).
- client: client@prisma-cont.test (NOU, firma 1968, legat de tenant_001 "Panificatie Salarii Speciale SRL" id=4784).
Contul REAL costin.hateganu@gmail.com (superadmin id=1) NEATINS. Constrangeri: parole prin nucleu.hash_parola
(scrypt, nimic slabit); parolele NU in git/registre/fisier comis.

## 09.08.2026 — Cross-check TVA D300 era MORT (apel d300.genereaza cu semnatura veche); reparat + gardat

BUG: control_incrucisat.verifica_tva chema _d300.genereaza(conn, schema, an, luna). d300.genereaza a fost
schimbat (06.08.2026, fereastra pe perioada fiscala TVA) sa ceara un obiect Perioada: genereaza(conn, schema,
perioada, manual=None). Apelul ridica TypeError, prins de `except Exception -> gri` din verifica_tva -> verdict
permanent GRI, niciodata rosu. Cross-check-ul D300-vs-4427/4426 (facturi emise/primite necontabilizate) a fost
MORT tacit, inclusiv in cronul zilnic alerte_control_fiscal (acelasi apel). Descoperit de proba de date de test
(cazul L1: o factura emisa fara nota validata NU producea rosu).

FIX: verifica_tva construieste Perioada(an, luna=luna) (din core.common), oglindind calea corecta din
declaratii_api (_d300). Temei: d300.pull/genereaza cer perioada.luna (D300 lunar).

CLASA: singurul apelant d300 stale era acesta. grep "genereaza(conn, schema, an, luna)" -> d112/d390/d406 si-au
PASTRAT semnatura (an, luna); apelantii lor sunt corecti (control_incrucisat:326 d112, salarii_contare:72 d112).

ALTERNATIVA RESPINSA: a ingusta `except Exception -> gri` ca sa NU inghita TypeError de programare (ar fi facut
bug-ul zgomotos de la inceput). Respinsa acum: except-ul larg e legitim pentru erori de DATE (profil incomplet ->
gri corect); distinctia date-vs-programare e fragila. Riscul de re-rupere e acoperit MECANIC de gard
(test_control_incrucisat_wiring), nu de ingustarea except-ului.

LIMITA: gardul acopera doar verifica_tva (D300). verifica_d112/verifica_d390 au semnatura corecta azi, dar nu au
inca un gard de cablaj end-to-end propriu (cele 61 teste din test_control_incrucisat sunt pe compara_* PURE).

## 09.08.2026 — Firul de intrare cabinet nou se testeaza intr-un CABINET SEPARAT, nu peste date reale

Contul de lucru al lui Costin e admin_firma intr-un cabinet cu 12 firme REALE. Datele de test (4 firme
alfa/beta/gama/delta din ~/date_test_cabinet) importate acolo ar face verdictele Controlului fiscal
neatribuibile (nu se mai stie ce rosu vine din test vs real) si ar polua un cabinet de productie.

DECIZIE: mediu de test izolat = cabinet nou "CABINET TEST FIR INTRARE SRL" (accounting_firms id=4163) + cont
admin_firma dedicat (fir-intrare@prisma-cont.test, user 6504, poate_pregati/valida/depune=true) creat cu
auth_api.inregistreaza_cabinet (scrypt). Un user apartine UNUI cabinet -> contul real NU poate accesa alt
cabinet; de aceea cont NOU, nu reutilizarea contului real. Login probat prin /auth/login (HTTP 200 + token).
Parola DOAR in raportul din chat (nu in git/registre). Cabinetul real + cele 12 firme NEATINSE.

ALTERNATIVA RESPINSA: superadmin (costin id=1) sa vada firmele de test - respinsa: schema_tenant da
superadminului doar tenantii cu accounting_firm_id IS NULL; firmele de test au accounting_firm_id=4163 ->
superadmin nu le-ar atinge. Trebuie admin_firma al cabinetului 4163.

LIMITA: firmele de test au CUI-uri FALSE (valid checksum, inexistente la ANAF) -> fluxul Migrare
"import CUI -> validare ANAF -> provisionare" le respinge; se adauga MANUAL (Adauga firma: provision_tenant
valideaza CUI-ul doar offline, precompletarea ANAF e best-effort inghitita). Vezi ISTORIC + raport pt. ordine.

## 09.08.2026 — Doua "forme care spun altceva decat faptul": balanta straina si "La zi" cu intarziati

Constatari de ecran (cabinet test 4163, GAMA/ALFA): app-ul stie faptul corect, il prezinta inselator.

(1) IMPORT SOLDURI accepta fisier cu structura straina. istoric_declaratii.csv incarcat la solduri -> "D394"
citit ca numar de cont, debit/credit 0 -> verifica_echilibru zice "echilibrat" (0==0), bulina verde, importul
SALVA balanta goala. Importul de parteneri avea verificare de continut (compara cu balanta), solduri NU avea
niciuna (chestionar pt.4: da, mecanisme diferite - solduri e general, accepta orice cont, dar n-avea poarta
"e chiar o balanta?"). FIX: solduri_api.balanta_valida (PURA): (a) niciun cont nu incepe cu cifra -> fisier
strain; (b) total debit=0 SI credit=0 -> balanta goala. Poarta in importa (refuz, ca la dezechilibru) + ruta
preview intoarce valida/motiv + UI avert + salvare blocata. NU schimba verifica_echilibru (folosit de audit_preluare).

(2) CONTROL FISCAL "LA ZI" numara declaratiile depuse DUPA termen. D112 dec: termen 26.01, depusa 20.07 -> randul
scria "dupa termen" dar categoria = La zi -> "LA ZI (19)" ascundea 14 depuneri intarziate. STARE NOUA in model
(nu doar afisare, dar FARA DB - data_depunere deja stocata): _clasifica capata cosul cu_intarziere (dd>termen),
separat de confirmate. NUME (decizie Costin, pt.5): "Depuse cu intarziere". SEVERITATE (decizie Costin):
informativ - NU urca pastila (_stare neatins); depus tarziu != restanta (constrangere respectata) -> firma
ramane verde daca totul e depus. Probat pe ALFA: La zi 19 -> La zi 5 + Depuse cu intarziere 14, firma verde, restante 0.

ALTERNATIVA RESPINSA (pt.2): urca pastila la galben pe istoric de intarzieri - respinsa de Costin (firma e
conforma acum; intarzierea e fapt istoric vizibil in grup separat, nu risc curent).

## 09.08.2026 — Mesaje UI backend fara diacritice: reparate; NU se pune gard mecanic de clasa

Mesajele balanta_valida (solduri_api, adaugate azi) erau fara diacritice; reparate + ghilimele romanesti „".
Regula "diacritice" din verificator_conformitate scaneaza DOAR .js (frontend) -> de aceea a scapat un mesaj .py.

DECIZIE (stop point): NU extind un gard mecanic de diacritice pe backend .py. Motiv: in .py nu se pot izola sigur
textele user-facing de restul (docstring, comentarii, print/raise din scripturi de migrare dev, SQL, identificatori
englezi, termeni tehnici CUI/TVA/CAEN/simboluri de cont, citate legale verbatim in Temei.text_citat) -> fals-pozitive.
Un scanner care ar cere diacritice pe "cont"/"data"/"balanta" din SQL/docstring ar fi zgomot. GARD INGUST in schimb:
test pe mesajele balanta_valida (au diacritice) - pe ce s-a inchis, fara fals-pozitive.

Verificat (chestionar pt.4): singurul text user-facing fara diacritice scris azi = mesajele solduri. Restul
diacritic-less din diff-ul de azi = neuser-facing: print/raise din migrare_pontaj/data_incetare/rapoarte_salvate
(scripturi dev), Temei.text_citat (provenienta legala, nerandata in UI, disciplina verbatim-MO separata).

## 09.08.2026 — PREDARE_LANT.md = al 5-lea pas de publicare (dupa poarta verde), obligatoriu in raport

Constatare tura 17: la publicare s-au actualizat DECIZII/GARZI/TESTE/ISTORIC, dar PREDARE_LANT - fisierul de care
depinde sesiunea urmatoare - a lipsit din lista, adica exact ce conteaza pentru continuitate era singurul optional.
DECIZIE: PREDARE_LANT intra in pasii de publicare (CLAUDE.md §2.3 pct.10, acum CINCI pasi: commit/push/deploy/
restart/predare) + in raport (§2.2 sect.11, listat INTOTDEAUNA: "rescris (tura N)"+diff SAU "nemodificat - starea
din tura N ramane valida"+de ce). Reguli PREDARE: se SUPRASCRIE (stare curenta, nu jurnal - jurnalul e ISTORIC.md);
contine in ordine four-way ultima executie (SHA+ora), fronturi deschise cu blocaj, ce e in lucru, ce urmeaza; daca
niciun front nu s-a miscat, ramane neatins DAR raportul o spune explicit. Backup CLAUDE.md.bak inainte, cu assert pe
ancora (4 ancore, fiecare cu o singura aparitie).

## 09.08.2026 — /raportari: filtrul de AUTOR coborat in SQL (aparare de date sub garda de ruta)

Audit 3de694e poz.4: /raportari/{rid} + /{rid}/citit aveau SQL nefiltrat pe proprietar; apararea statea intr-un
singur strat (ruta). Clasa D300 mort (aparare intr-un strat cedeaza tacut). PUNCT DE OPRIRE ridicat: garda actuala
e pe AUTOR (raportare vizibila DOAR autorului), nu pe cabinet; cabinetul ar fi strict mai larg. DECIZIE Costin: NU
se relaxeaza la cabinet - filtrul de AUTOR coboara in SQL (firul_complet primeste cerut_de_uid + e_superadmin;
non-superadmin -> AND autor_id=cerut_de_uid), sub garda de ruta care RAMANE. Data-layer = ruta (autor), zero
relaxare de vizibilitate. ALTERNATIVE RESPINSE: filtru de cabinet in SQL (mai larg decat autorul); relaxare la
cabinet-vizibil (schimba ce vede contabilul). Gap /raportari/{rid}/citit (marcheaza_citit fara check proprietar ->
orice user marca citit pe fir strain, dovedit 200 pe cod vechi) - INTRAT in acelasi lot (check proprietar pe ruta).
/raportari/admin ramane superadmin (global by design; apararea = gate-ul superadmin). Gard: test_izolare_raportari.

## 10.08.2026 — Real bate static: divergenta setInapoi migrare INFIRMATA in browser

Analiza statica (fork) a indicat divergenta setInapoi != pusher pe migrare (importXFirma face
setInapoi(()=>wizardSolduri), diferit de pusher pe calea per-firma). Observatia in browser REAL a
infirmat-o: pe calea per-firma, back = pusher ("Import date"), iar fixul pop-priority NU muta destinatia
la nivelul 1. Real bate static - exact motivul pentru care s-a construit capacitatea de probare in browser
(frontend_test/, Playwright). NOTA: la data acestei intrari, drumul MULTI-STRAT din bug (Solduri>Salariati>
Istoric, adancime >1) inca se probeaza; decizia de fix se ia dupa tabelul complet pe toate nivelurile.

## 10.08.2026 (tura 20) — Antet wizard: fix de clasa in navigator.js (back prefera pop natural) + proba browser

Bug (browser, cabinet 4163): pe calea 'Migrare cabinet' antetul acumuleaza (Firme > Migrare cabinet > Solduri >
Salariati...) si back-ul nu revine la meniu. RE-DIAGNOZA (real bate static): NU e la nivel sus.pasi/mergi (cum
indica analiza statica), ci la nivel STIVA de ferestre - meniuMigrare deschide fiecare strat ca fereastra
(nav.deschide), iar wizardSolduri/fratii fac setInapoi(()=>meniuMigrare) = re-randare IN LOC in loc de pop pe
fereastra -> ferestre stivuite. Dovedit in browser: caile pasi (per-firma/firme/facturi) sunt curate (back=pusher,
fixul NU le schimba); doar calea straturi acumuleaza.
DECIZIE Costin (dupa proba per-wizard in browser): fix de clasa in navigator.js - back face pop NATURAL (pas pe
traseu, altfel fereastra daca stiva>1) INAINTE de setInapoi custom; custom ramane doar fara pop natural. +
trunchiere (ultimul nod vizibil, parintii ellipsis; nu overflow:hidden care taia dreapta). Gardat cu proba browser
reala: cod vechi exit 1, cod nou exit 0. Alternative respinse: fix ingust doar-antet; per-wizard manual.
LIMITE: pachete/setari netestate depth prin UI; portal/admin/asistent nereachable cu 4163 (cer client/superadmin/
angajat). Proba NU e in poarta verde (decizia lui Costin cand ruleaza).

## 10.08.2026 — Fir intrare cap-coada (4163): D101 totalPlata_A e checksum ANAF (nu bug); ZERO-BASE D100/D300

Parcurs firul de intrare pe cele 4 firme (cai reale). Doua concerne ridicate de proba, verificate:
1. BETA D101 total_plata_a=-11212 pe pierdere NU e bug: anaf_surse/d101_struct_anaf.txt:417 defineste totalPlata_A
   = "Suma de control" = suma(P1..P53) -> negativ pe pierdere e conform specificatiei; impozitul real (P15) = 0 pe
   pierdere (corect). Verificat la SURSA oficiala, NEreparat (o "corectie" ar fi stricat conformitatea).
2. ZERO-BASE: D100/D300 genereaza declaratie pe zero silentios, pe cand D205/D112 refuza golul/suspectul. GASIT,
   NEREPARAT - motiv: nil D300 e legal SI obligatoriu (platitor TVA depune lunar chiar pe zero); DELTA D100=0
   reflecta corect facturile NEcontabilizate (defectul DELTA), prins de cross-check (verifica_tva ROSU). Refuzul
   D300/D100 pe zero ar bloca declaratiile nil legale. DECIZIE DESCHISA Costin: vrei ca D100/D300 sa AVERTIZEZE
   (nu refuze) cand genereaza zero desi exista facturi necontabilizate?

## 10.08.2026 (tura 22) — ZERO-BASE hardening D100/D300: avertisment non-blocant pe zero-suspect

Decizie Costin (raspuns la §6 tura 21): un zero care poate fi defect nu trebuie sa arate ca un nil legal.
Constrangere: NU bloca generarea/depunerea - nil-ul D300 e legal si obligatoriu, decide contabilul.
IMPLEMENTAT: D100 si D300 emit un AVERTISMENT (res.avertismente, non-blocant, surfaced la UI prin getattr in
ruta) cand declaratia e pe ZERO dar exista facturi in perioada:
- D100: venituri contabilizate (70x) = 0 DAR facturi emise in fereastra trim > 0 (necontabilizate).
- D300: R tot zero DAR facturi in fereastra > 0 (necontabilizate / TVA la incasare nedecontata).
Nil legal (fara facturi) -> FARA avertisment (control negativ in gard). NU se calculeaza nicio valoare fiscala
noua - doar se semnaleaza inconsistenta facturi-vs-declaratie. Probat pe DELTA real (D100 pe zero cu 3 facturi
-> avertisment). Gard: core/test_zero_base_declaratii.py (old-fail/new-pass). Vezi si DECIZII tura 21 (D101
checksum ANAF + nil D300 legal).

## 10.08.2026 (tura 23) — DUK-validat toate declaratiile (4 firme). D100 gol REFUZAT (PIVOT tura 22)

Validat prin DUKIntegrator oficial toate declaratiile pe 4163 - prima oara. 5 defecte structurale gasite (nu
fusesera niciodata validate oficial). Reparat 1 (cel mai clar + DUK-dovedit); 4 raportate (fiecare investigatie
la sursa proprie, nu batch-rush - lectia D101 unde o valoare parea gresita dar era corecta).

PIVOT tura 22: avertismentul non-blocant pe D100 gol -> REFUZ. Motiv: DUK a dovedit ca D100 pe zero emite XML
STRUCTURAL INVALID ('lipsa sectiune obligatorie <obligatie>' - obligatoriu >=1, verificat anaf_surse/
d100_struct_anaf.txt). Nil-ul D100 NU e depozitabil -> se refuza (ca D390 'nu se depune pe zero'), nu se emite
XML invalid + avertisment. D300 RAMANE pe avertisment (nil-ul D300 E legal si depozitabil). Probat DELTA real
(D100 refuzat cu hint 'contabilizeaza cele 3 facturi').

DEFECTE DUK RAMASE (raportate, de reparat pe rand la sursa):
- D394 codPR '21' respins: 21 (cereale) e CENTRALIZATOR; la op11 se pune SUBCODUL NC (1001 grau...), nu 21
  (d394.py:92). Seed 'cereale' prea grosier. Nuanta date+app.
- D112 asiguratB3 (CM): nepotrivire zile/baza CAS pe indemnizatia de concediu medical (salarizare CM). Fiscal, deep.
- D301 data_doc ISO (BETA): BUG DE DATE DE TEST - seed a inserat ISO ocolind ruta care valideaza ZZ.LL.AAAA;
  nu e bug de app (generatorul emite ce e in DB; ruta valideaza inputul real). Fix = corectat seed-ul.
- D406 SupplierID pe PurchaseInvoices (SAF-T): structural, deep (XSD).
D390 'codO invalid' pe ALFA/DELTA = CUI-uri UE FALSE din setul de test (nu bug de app; app deja avertizeaza).

## 10.08.2026 (tura 24) — Refacut 4 declaratii conform specificatiilor oficiale (DUK-dovedit)

Comanda: "verificarea de pana acum era CIRCULARA (cod+test scrise pe aceeasi presupunere, neconfruntate cu
validatorul); refa toate declaratiile conform specificatiilor oficiale". Cele 4 defecte DUK ramase din tura 23
reparate la SURSA (anaf_surse/XSD, nu memorie), fiecare cu gard old-fail/new-pass + re-validare DUK. Proba
obiectiva = DUKIntegrator (EXTERN codului+testelor noastre) pe arborele combinat, 4 firme.

- D394 codPR cereale (core/d394.py): spec anaf_surse/d394_struct_anaf.txt poz.68-70 ("op11(codPR)=bun pt bun<>21
  SAU lung(op11(codPR))>2 pt bun=21") -> la op11 pt cereale se cere SUBCODUL NC (lung>2: 1001 grau, 1005 porumb),
  NU centralizatorul '21'. op11 nu mai emite '21' (exclude cu avertisment cand lipseste subcodul); calea N
  recunoaste subcodul NC. Comentariul-CREDINTA anterior ("validatorul accepta 21 pt tip_partener=2, probat 04.08")
  = INFIRMAT de DUK - exact verificarea circulara semnalata. DUK: eroarea "21 nu se afla in lista"+R63/R80/R81
  DISPARUTA; calea cu subcod '1005' -> D394 VALID.
- D112 asiguratB3 concediu medical (core/d112.py): spec d112_struct asiguratB3 B3_7 ("ERR daca B3_7=0 si B3_6>0")
  + OUG 158/2005 art.17 (Ci=media_zilnica x procent x zile). Defectul: d112 recalcula media pe 6 luni dar lua
  indemnizatia (B3_12/B3_13) direct din coloanele stocate; certificat cu media>0/zile>0 dar brut_ang=brut_fnuass=0
  -> XML auto-contradictoriu -> DUK V47/V52. Fix: completeaza indemnizatia din media x procent_cm(canonic) x zile
  DOAR cand lipseste; certificatele cu suma stocata NEATINSE. DUK tenant_013+014: erori V47/V52 -> VALID
  (B3_7=655=B3_12+B3_13).
- D301 data_doc (core/d301.py): spec d301_struct poz.35 (data_doc C(10) Format ZZ.LL.AAAA). Codul emitea ISO.
  DIVERGENTA fata de tura 23 (care-l clasase "bug de seed, nu app"): am ales DEFENSE-IN-DEPTH in generator
  (_data_doc_ro normalizeaza orice format stocat -> ZZ.LL.AAAA), nu doar corectia seed-ului. Motiv: ruta valideaza
  inputul, DAR datele pot ajunge pe alte cai (import/backfill) -> generatorul emite formatul cerut de ANAF
  indiferent de stocare. DUK D301: VALID pe toate 4 firmele (fork raportase "gri" pe o rulare izolata; rularea
  combinata confirma valid).
- D406 SupplierID (core/d406.py): spec d406_schema_anaf.xlsx "5. Structures" + saft.xsd (regula SD.P.22/23:
  SupplierID nu poate fi "0"; cod 08 'neidentificat' interzis EXPLICIT pe SupplierID). Codul dadea "0" pt PF fara
  cod fiscal. Fix: _partener_id_saft -> cu cod fiscal 00/01/02; PF fara cod fiscal -> tipul 04+cod alfanumeric
  (placeholder-ul PREVAZUT de norma, NU inventeaza CUI); fara cod nici nume -> ValueError (raporteaza, nu cade pe
  "0"). DUK SAF-T: "SupplierID nu poate fi 0" -> VALID pe toate 4 firmele.

GASIT, NU REPARAT IN COD (date/decizie produs Costin - clasa R233.6/R24.1: cod corect pe date corecte):
- D394 R233.6 ramas pe ALFA (PF-01): achizitie cereale de la persoana fizica fara CUI, categorie coarsa 'cereale'
  fara subcod NC pe factura -> op11 obligatoriu la PF dar fara subcod NU se poate emite codPR valid. DECIZIE:
  (1) corecteaza seed PF-01 cu subcod NC real (ex 1005) -> D394 valid (dovedit pe calea cu subcod); SAU (2) daca
  achizitia de cereale de la PF fara CUI nu e operatiune art.331/N reala (taxarea inversa cere ambii platitori
  TVA), categorie_331 n-ar trebui setata. Spre deosebire de D394 codPR '21' (cod MEREU gresit -> fix de cod), aici
  codul e corect; lipsa e in DATE.
- D390 R24.1 pe ALFA/DELTA: CUI-uri UE FALSE in seed (12345678901 / 811111114 nu trec algoritmul de tara).
  Generatorul deja AVERTIZEAZA ("X facturi fara CUI UE valid") si emite CUI-ul stocat - cu CUI real ar fi valid.
  Gap de DATE (seed), NU defect de cod (asimetrie fata de D394 '21' care era mereu gresit). Decizie: seed cu CUI UE
  reale, SAU exclude ops fara CUI UE valid (decizie de continut = produs).
- D112 split zile stocat anomal (semnalat de fork): fixul completeaza suma pe split-ul STOCAT (za/zf); daca
  certificatele de test se re-salveaza prin salariati_api.salveaza_concediu, split-ul canonic (min 5 + diminuare
  OUG91/2025) ar diferi. Radacina reala: orice cale care scrie certificate fara a calcula suma (seed/import direct)
  ar trebui sa calculeze suma la scriere. Decizie produs.

## 10.08.2026 (tura 25) — Reconstruit TOATE declaratiile confruntate cu sursa oficiala (DUK-dovedit)

Comanda: turele 23-24 atinsesera doar cele 4 cu defecte DUK; restul trecusera validarea, unele doar pe NIL
(nu dovedeste nimic). "Reconstruieste toate conform sursei oficiale - structuri, nomenclatoare, XSD - nu
conform intelegerii din cod." Metoda: 10 audituri paralele (agenti PROASPETI, ca sa citeasca sursa fara
mostenirea presupunerilor), field-by-field pe anaf_surse/*_struct + XSD, pe DATE POPULATE (injectii ROLLBACK
unde seed-ul era nil), fiecare defect cu gard old-fail/new-pass + DUK before/after. Teza confirmata de la
prima constatare: DUK e LENIENT pe campuri pe care nu le verifica -> "a trecut validarea" nu = conform.

DEFECTE REALE REPARATE (8 declaratii, 10 defecte; fiecare la sursa citata + gard + DUK):
- D100 (core/d100.py): (1) micro cod 121 trim IV scadenta = 25.06.(an+1), NU 25.01 (sursa d100_struct
  L807-811 + validator R15.1 - ANAF RESPINGEA D100-ul de Q4 al unei micro; DUK erori R15.1 -> valid). (2)
  profit 102/103/105 sfarsit de an (luna 12) scadenta = 25.12.an (25.LS), NU 25.01.an+1 (sursa L258-260/L3286;
  DUK lenient accepta ambele, dar termenul emis era cu o luna tarziu). Introdus _scadenta_cod(cod,an,luna).
  CROSS-CHECK: D710 (care imparte logica obligatiei D100) emitea deja corect 25.06.2027 pt micro trim IV -
  D100 era neconform cu propriul frate.
- D101 (core/d101.py): nr_evid poz.1-2 = "11", NU "10" (OPANAF 206/2025 poz.19 + exemplul lucrat ANAF
  11103011212250413000028). Codul avea doar un comentariu auto-referential ("poz.1-2 '10'") - modul de esec
  "comentariu suspect". DUK R18 valideaza DOAR checksum-ul (poz.22-23), nu poz.1-2 -> accepta tacut "10".
- D205 (core/d205.py): cifR/den1 (obligatorii, rand 34/31) puteau fi emise GOALE cand asociatul n-are CNP ->
  XML invalid la ANAF ("cifR: atribut prezent dar vid nepermis"). Fix: refuz cu ValueError care numeste
  beneficiarul (oglinda erori_generare). Clasa ZERO-BASE (ca D100 gol).
- D300 (core/d300.py): liniile taxabile la o cota FARA rand DUK-valid pe 2026 (19%/5%) erau aruncate TACIT cu
  sfat gresit ("pune-le manual la randuri" - randuri pe care DUK le respinge). DELTA: o livrare 19% (TVA 190)
  disparea din TVA colectata (sub-declarare). Fix: avertisment CUANTIFICAT (arata TVA-ul) + sfat corect (NU
  la R69/R71/R74; corecteaza cota facturii sau regularizare R16); separa liniile 0% de cele taxabile. XML
  neschimbat (nu auto-emite un rand respins). Agentul a PROBAT DUK direct (nu comentariul): v12/2026 respinge
  R69/R70/R71/R74/R75/R24, accepta R9/R10/R11/R22/R23/R13/R16 - codul avea dreptate acolo.
- D390 (core/d390.py): incoerenta de rotunjire (R16): baza per-operatie rotunjita individual, dar totalurile
  rezumat (bazaL..bazaR) rotunjeau suma Decimal bruta -> pe baze fractionare divergeau (2x1000.50: op 1001+1001
  =2002 dar bazaL=2001) -> DUK R16. Fix: totalurile derivate din intregii deja-rotunjiti. (Seed-ul avea baze
  intregi rotunde -> nu se vedea.)
- D394 (core/d394.py): (1) V (livrare taxare inversa) emisa la cota produsului (21) in loc de 0 (sursa poz.217:
  cota=0 IFF tip in LS,AS,N,V; validator R217.2 + cascada R68.2/R69.2/R35/R77-79). Cheia _adauga purta cota
  bunului pt V; exista doar reclasarea L->LS. Fix: cheia foloseste 0 pt V. (2) CRASH LATENT: pull() chema
  cota_standard(an,luna) dar an/luna nu erau legate in pull -> orice achizitie cu taxare inversa fara linii de
  detaliu -> NameError la d394.py:831 (exact calea pe care comentariul pretindea ca o trateaza).
- D406 (core/d406.py): PaymentMethod folosea literalii "VIR"/"NUM" in loc de codul ANAF pe 2 cifre
  (Nom_Mecanisme_plati: doar 01/02/03/98/99; XSD fara enum -> impus de DUK). "VIR" -> DUK respinge. Fix: mapper
  payment_method_anaf (numerar->01, compensare->02, virament/card/transfer->03), default 03. (A iesit doar cand
  s-a exercitat sectiunea Payments - fisierele de baza n-aveau plati.)
- D112 (core/d112.py): carantina (cod 07) angajatorC2 Rd2.2 omitea C2_213 (Sum D_14) si C2_215 (Sum D_20).
  Carantina NU e integral-FNUASS -> angajatorul suporta primele zile -> aceste coloane sunt >0 si obligatorii
  (sursa rd.49c/49e). DUK before (cod 07): erori A49c/A43d.2/A49e -> valid. Codul emitea doar 4 din 6 coloane.

CONFORM, FARA FIX (dovedit field-by-field, nu doar "a trecut"):
- D301 (core/d301.py): fiecare camp confruntat cu sursa + fiecare comentariu suspect (temei obligatoriu, tip=5
  emite doua randuri, formula totalPlata_A) RE-PROBAT direct pe DUK - toate au tinut.
- D710 (core/d710.py): nu are struct dedicat; spec-ul e "Zona 710" in d100_struct; validatorul D710_56 e
  INSTALAT (/home/costin/duk/dist), 22 teste DUK-gated. Fiecare camp confruntat - conform.

DOCSTRING-URI STALE CORECTATE (comentariu-only, verificatorul sare peste docstring-uri; exact hazardul comenzii):
- d101.py: sectiunea "Corpul declaratiei (P1-P16...)" descria un mapping INVENTAT (P11=Impozit calculat,
  P15=Diferenta datorata) care contrazicea codul real (P1..P53) -> inlocuita cu pointer la sursa.
- d205.py: "tip_venit = 25 -> dividende" era GRESIT (25=castiguri aur investitie; dividendele=08, cum foloseste
  corect codul) -> corectat.

GASIT, NU REPARAT (date/decizie produs Costin; cod corect pe date corecte):
- D112 asiguratD D_1/D_2/D_5/D_6/D_7 (obligatorii) pot fi emise GOALE pe un certificat CM fara serie/numar/date
  -> XML invalid ("D_1: atributul trebuie sa existe"). ACEEASI CLASA ZERO-BASE ca fixul D205 cifR - AR MERITA
  acelasi refuz-pe-gol, DAR hard-block-ul rupe 4 fixtures minimale din test_pull_declaratii.py (shared) si cere
  confirmarea ca fluxul salveaza_concediu garanteaza aceste campuri. Decizie de contract de date -> Costin.
- D390 R24.1: CUI UE FALS in seed (12345678901/811111114). Cu CUI real (DE136695976/FR40303265045 injectate)
  -> valid pe ambele firme. Recomandare: corecteaza seed; NU exclude tacit ops fara CUI valid (ar sub-raporta o
  op obligatorie legal). Optional produs: avertisment per-partener pre-emitere.
- D394 R233.6 (ALFA cereale de la PF fara subcod NC pe factura - seed); C/V manuale nu poarta op11 (path
  manual nealimentat - UI); prsAfiliat hardcodat 0 (fara model de date afiliati).
- D300: 19%/5% fara rand DUK-valid 2026 (rutare la R16 = decizie); liniile 0% neclasificate (scutit cu/fara
  drept/export); achizitiile cu taxare inversa aruncate TACIT (net-zero, dar merita avertisment).
- D205 divid_P (platit) mereu 0 desi sursa e dividende PLATITE (model distribuit-vs-platit); Rezid hardcodat 1
  (nerezident). D301 pers_inreg hardcodat 1 (nu exista coloana firma_profil). D406 GL TaxCode=300 (nu in
  TVA_NoteContabile, DUK accepta); PF tip-04 absent din Customers/Suppliers master (radacina in facturi_api).
- D101 scadenta lege-vs-validator (cunoscut, codul urmeaza validatorul); D100 an fiscal modificat nemodelat.
- XSD-vs-DUK: d112 Str_codBoalaSType enum stale (01-15) dar DUK accepta 91/92/17; d406 namespace fara "t" +
  containere goale omise - AMBELE corecte pe DUK (validatorul e autoritatea, nu XSD-ul livrat izolat).

Proba obiectiva COMBINATA (frontend_test/valideaza_duk.py, 4 firme, arborele cu toate 8 fixurile): fara
regresie - toate declaratiile valide raman valide; avertismentul D300 nou apare pe DELTA; erorile ramase =
DATE (R233.6/R24.1). Un singur commit prin poarta verde; doar 4163; 1968 neatins.

## 10.08.2026 (tura 26) — Reparat toate deciziile §6 (Costin) din auditul tura 25 (DUK-dovedit)

Comanda: Costin a decis pe §6 tura 25. Metoda: 7 audituri/fixuri paralele (agenti proaspeti), fiecare la sursa
citata + gard old-fail/new-pass (pe HEAD 6cd0054) + DUK before/after pe DATE POPULATE (injectii ROLLBACK).

FIXURI DE COD (6 declaratii, 9 defecte):
- D112 (core/d112.py): asiguratD D_1/D_2/D_5/D_6/D_7 (use="required" in d112_06082026.xsd) puteau fi emise GOALE
  -> REFUZ ZERO-BASE (ValueError care numeste salariatul + campurile), ca D205 cifR. + REPARAT cele 4 fixtures din
  test_pull_declaratii.py care construiau certificate CM fara serie/numar/date (Costin: fixtures gresite se repara,
  nu se ocolesc) - acum cu serie/numar/date realiste. CONSTATARE salveaza_concediu (Costin a cerut verificarea):
  garanteaza DOAR D_7 (data_sfarsit, G9); NU verifica serie/numar/data_acordare/data_inceput -> fluxul de salvare
  e o RADACINA SECUNDARA (poate persista date invalide). Refuzul din d112 e ultima linie; un gard simetric in
  salveaza_concediu (4 campuri, langa G9 ~L383) = RECOMANDAT, neaplicat (schimba UX la salvare; Costin a cerut sa
  raportez).
- D205 (core/d205.py): (1) divid_D/divid_P (rand 39a/39b) - pull() citea doar platit dar emitea divid_P=0. Acum
  distribuit = Sum credit 457, platit = Sum debit 457 (semantica cont 457 bifunctional); baza1/imp1 pe suma
  PLATITA (pastreaza reconcilierea verde). (2) Rezid (rand 32) hardcodat "1" -> derivat din CNP (_cnp_rezident:
  13 cifre, prima 1-8 = rezident). DESCOPERIRE: DUK regula R32 INTERZICE Rezid=2 pt tip_venit1=08 (dividende) -
  beneficiarii nerezidenti de dividende merg pe D207, nu D205 -> fixul ii REFUZA (nu emite Rezid=2). Coloana
  asociati.tara NU se adauga (R32 o face inutila pt dividende).
- D300 (core/d300.py): (1) achizitiile cu taxare inversa (beneficiar) erau aruncate TACIT -> acum deriva R12_1/
  R12_2 (colectat) + R25_1/R25_2 (deductibil), net-zero, cu gard anti-dubla-numarare (simetric cu rd.13). Ales
  rd.12/25 (nu rd.7) pt ca DUK respinge R7 fara R20 (probat). (2) liniile 0% clasificate: achizitie 0% curata ->
  R26_1; livrare 0% -> avertisment per-linie cu suma (natura scutit-cu-drept R14/fara-drept R15/export NU e
  captata in date -> NU se inventeaza).
- D301 (core/d301.py): pers_inreg (poz.15) hardcodat "1" (ramura "2" moarta) -> _pers_inreg(prof) face "2"
  reachable din prof["inreg_art317"]. REFUZAT derivarea din operatiuni_ic (doctrina codului: e flag de FAPT, nu
  marker de inregistrare art.317 - o firma cu achizitii IC dar neinregistrata e tot "1"). Default sigur "1".
- D394 (core/d394.py): (1) op11/codPR pt operatiuni MANUALE C/V - calea manuala nu pasa categoria -> op1 fara op11
  obligatoriu (poz.233/R233.5) -> invalid. Acum manual["operatiuni"] poarta categorie_331 (nume categorie SAU
  subcod NC direct). (2) prsAfiliat (poz.6a) hardcodat "0" -> sourced din prof["are_operatiuni_afiliate"].
  REFUZAT fake-derivarea (niciun model de date afiliati, confirmat via information_schema).
- D406 (core/d406.py): (1) GL/PaymentLine TaxCode "300" (inexistent in nomenclator) -> 380304 (cota 0 note fara
  TVA, art.319 alin.10, singurul cod 0 din TVA_NoteContabile) + declarat in TaxTable. (2) PF tip-04 absent din
  Customers/Suppliers master - RADACINA in d406.py pull() (NU facturi_api - verificat: e CRUD pur): derivarea
  master folosea _partener_registration_number (00/01/02) + filtra tert_cui!='' -> exclus. Acum _partener_id_saft
  + drop filtru + dedup pe pid SAF-T.

SEED DE TEST CORECTAT (decizia #2 Costin - date, nu cod; committed pe 4163, 1968 neatins):
- D390 R24.1: CUI UE FALSE inlocuite cu reale checksum-valide - t013 DE811111114->DE136695976, FR12345678901->
  FR40303265045; t016 DE811111114->DE136695976. NU s-au exclus operatiuni (Costin: o op obligatorie disparuta e
  mai grava decat una cu CUI invalid). D390 t013 + t016: erori R24.1 -> VALID.
- D394 R233.6: cereale de la PF (PF-01) categorie_331 'cereale' (centralizator) -> '1005' (porumb, subcod NC).
  D394 t013: erori R233.6 -> VALID. Sursa seed (~/date_test_cabinet: genereaza.py + XML e-Factura + seed_luna.sql)
  actualizata, ca re-seed sa pastreze fixul.

## 10.08.2026 (tura 26) — REGULA: la conflict XSD-livrat vs validator DUK, VALIDATORUL e autoritatea

Decizia #4 Costin, consemnata ca REGULA (sa nu se redeschida): cand XSD-ul livrat de ANAF si DUKIntegrator
instalat NU sunt de acord, se urmeaza VALIDATORUL (poarta reala de depunere), nu XSD-ul citit izolat. Cazuri
dovedite (tura 25): d112 Str_codBoalaSType enum stale (01-15) dar DUK accepta codurile 91/92/17; d406 namespace
fara "t" (mfp:...d406:... vs XSD targetNamespace ...d406t...) + containerele SourceDocuments goale OMISE (DUK
respinge un <Payments> gol injectat). In toate, XML-ul emis e DUK-valid; lxml-vs-XSD pica doar pe discrepanta
XSD. NU se "repara" codul dupa XSD contra validatorului. (Simetric cu D101 lege-vs-validator: codul urmeaza
validatorul.)

## 10.08.2026 (tura 26) — Coloane de date RAPORTATE (nu adaugate): constrangerea 1968-neatins

Trei fixuri sunt COMPLETE la nivel de cod (ramura corecta reachable + sourced dintr-un camp + default sigur +
dovedite cu valori injectate), dar valoarea EXACTA cere un camp care nu exista. NU am adaugat coloanele: un ALTER
pe firma_profil/facturi ar atinge schema cabinetului REAL 1968 (interzis), iar o coloana goala fara UI nu schimba
nimic functional. DDL raportat pentru decizia Costin (cum secventiaza + cum trateaza 1968):
- D301 pers_inreg=2 (art.317): `firma_profil.inreg_art317 boolean NOT NULL DEFAULT false`.
- D394 prsAfiliat=1: `firma_profil.are_operatiuni_afiliate boolean NOT NULL DEFAULT false`.
- D300 clasificare livrari 0% (R14 cu drept / R15 fara drept / export): `facturi.natura_scutire varchar(16)`.
Codul consuma deja prof.get(...)/campul (pull() firma_profil = SELECT * -> curge automat cand coloana exista;
1968 fara coloana -> .get() default sigur). Pana atunci: pers_inreg=1, prsAfiliat=0, livrari 0% avertizate per-linie.

## 10.08.2026 (tura 27) — LANT legislatie TURA 1/4: corpusul de legislatie la zi pentru fiecare declaratie

Comanda: lant de 4 ture (fiecare raportata inainte de urmatoarea) care inchide "declaratie invalida" (T1-3) +
"declaratie valida care nu reflecta contabilitatea" (T4). TURA 1 = legislatia: pentru fiecare declaratie, actul
ANAF care APROBA forma + legea substantiala, verificat la zi in MO, adus in corpus unde lipsea/era depasit.

Metoda: 4 audituri web paralele (agenti proaspeti cu WebSearch/WebFetch), ancorate pe server (versiuni.xml +
/home/costin/duk/dist/D<F>IstoriaVersiunilor) si confirmate web (static.anaf.ro, legislatie.just.ro, CECCAR/
PwC/MO). Corpusul avea legea SUBSTANTIALA (CF + acte modificatoare) + structurile extrase, dar NU ordinele care
aproba forma (doar 77/2022 + 3562/2024).

ACT CURENT care aproba forma, per declaratie (adus in corpus, nivel PRIMAR static.anaf.ro daca nu se noteaza altfel):
- D100/D710: OPANAF 57/2026 (MO 55/23.01.2026), amendeaza baza 587/2016 -> opanaf_57_2026_d100_d710.pdf.
- D101: OPANAF 206/2025 (MO 140/18.02.2025) -> opanaf_206_2025_d101.pdf.
- D112: Ordin comun 605/95/928/2314/2026 (ANAF 605, MO 463+463bis/02.06.2026), din luna 07/2026 -> opanaf_605_2026_d112.pdf.
  SUPERSEDA 2066/.../2025 (ce cita struct-ul). DISCREPANTA: validatorul instalat D112_209 (Apr 2026) e ANTERIOR
  formei iulie-2026 -> DUK-ul de pe server e o generatie in urma pe D112 (flag Costin - actualizare DUK).
- D205: OPANAF 303/2026 (MO 187/11.03.2026) -> opanaf_303_2026_d205.pdf; baza OPANAF 179/2022 -> opanaf_179_2022_d205_d207_baza.pdf.
  SUPERSEDA 102/2025. (102/2025 = REFERENCE-ONLY: MO 65/27.01.2025, nefetchabil - 404 ANAF + legislatie.just.ro
  blocheaza serverul.)
- D300: OPANAF 174/2026 (MO 105/09.02.2026, reforma TVA Legea 141/2025) -> opanaf_174_2026_d300.pdf. Struct-ul
  "D300_A10.0.0 v12" era versiune de tranzitie, inlocuita de 174/2026.
- D301: OPANAF 592/2016 (MO 94/08.02.2016) -> opanaf_592_2016_d301.pdf. Inca ordinul care aproba modelul (niciun
  ordin nou); d301_struct e etichetat 2013 (provenienta), validatorul D301_9 = packaging.
- D390: OPANAF 705/2020 (MO 217/17.03.2020) -> opanaf_705_2020_d390.pdf. Inca in vigoare; NICIUN amendator
  (validatorul D390_11/2026 = doar packaging - confirmat pe legislatie.just.ro).
- D394: OPANAF 2194/2025 (MO 852/17.09.2025, rate 21%/11% + CAEN Rev.3) -> opanaf_2194_2025_d394.pdf; baza
  3769/2015 -> opanaf_3769_2015_d394_baza.pdf. CORPUSUL ERA DEPASIT: avea doar 77/2022, superseded de 2194/2025
  (care corespunde validatorului D394_31). 77/2022 lasat ca istoric.
- D406: OPANAF 1783/2021 (MO 1073/09.11.2021) + amendator 407/2025 (MO 310/08.04.2025, a inlocuit Anexa 5) ->
  opanaf_1783_2021_saft_d406.pdf + opanaf_407_2025_saft_d406.pdf. Baza legala CPF Legea 207/2015 art.59^1.
- D177: OPANAF 3562/2024 (MO 643/05.07.2024) - DEJA prezent si curent (OPANAF_3562_2024_D177.pdf). Nimic de adus.

RAMAS (raportat, nu adus - decizie/urmarire Costin):
- REFERENCE-ONLY (nefetchabile de pe server; legislatie.just.ro respinge curl-ul host-ului): D205 OPANAF 102/2025;
  CPF Legea 207/2015 consolidat (art.59^1 = baza legala D406/SAF-T). Coperirea substantiala e intacta (ordinele
  in corpus, CF prezent), dar aceste doua raman de adus dintr-un mirror accesibil.
- CF MASTER STALE: cod_fiscal_227_2015_consolidat.html (adus 02.08) pare consolidat PRE-2025 (nu contine Legea
  141/2025 / 239/2025); reforma 2025 e prezenta separat (legea_141_2025_consolidat.html) + COTE o citeaza, deci
  valorile sunt acoperite, DAR fisierul-master CF e depasit -> de reimprospatat dintr-un mirror accesibil.
- DISCREPANTE validator-vs-ordin (packaging vs lege): D112_209 in urma formei 605/2026 (real, flag DUK);
  D390_11/D394_31/D301_9 = doar bump de packaging, legea neschimbata (confirmat).

## 10.08.2026 (tura 28) — LANT legislatie TURA 2/4: catalogul exhaustiv al datelor care invalideaza

Comanda: identifica si CONSTRUIESTE toate tipurile de date care pot face o declaratie invalida - exhaustiv, "ce
scapa aici nu se prinde mai tarziu"; pt FIECARE declaratie: ce o invalideaza, ce incalca, sursa, ce mesaj primeste
utilizatorul. Metoda: 10 audituri paralele (agenti proaspeti), fiecare tip CONSTRUIT pe date POPULATE (injectii
ROLLBACK) + rulat prin genereaza + DUKIntegrator; XML corupt trimis direct la DUK pt regulile pe care generatorul
nu le poate produce (dovada ca gardul e load-bearing). Rezultat: CATALOG_INVALIDITATE.md (livrabil persistent +
checklist TURA 3/4). Total ~350 tipuri catalogate; distributie mesaj (a) refuz / (b) avertisment / (c) emis-tacit
+DUK / (d) tacit-complet.

11 TEME TRANSVERSALE (se repara o data, acopera multe declaratii) - tintele TUREI 3/4:
- T1 checksum CUI/CNP NICIODATA pre-validat (9/9 declaratii) - dominanta; exista valideaza_cnp la import asociati,
  nefolosit pe declaratii. Fix comun.
- T2 valideaza(res) = COD MORT (D300/D301/D406/D390: genereaza cheama doar erori_generare, nu valideaza) - verificari
  prietenoase calculate dar niciodata aratate -> user primeste eroarea DUK bruta.
- T3 coercitie TACITA enum-necunoscut->default (D406 UOM->H87/plata->03/cota->taxcode; D301 tip->1/valuta->EUR; D394
  CUI garbage->partener strain) - date GRESITE trec validarea.
- T4 avertizeaza-dar-emite-INVALID (D394 op1 C/V fara op11 -> R233.5).
- T5 cale MANUALA/IMPORT ocoleste gardurile (D205 imp1 gresit, D301 nr_doc/val, D710 obligatii).
- T6 passthrough NETRUNCHIAT -> overflow (D301 nr_doc>C(20) leak pur; D112 D_1/D_2/D_23; D390 codO>12 CORUPE TVA).
- T7 SEMANTIC gresit-dar-consistent -> DUK nu prinde (D205 imp1≠rate×baza, D301 RON curs≠1, D710 suma_ded, agregare
  mis-contabilizata, CUI proprietar gresit) -> TINTA TURA 4 (reconciliere).
- T8 gap-uri NON-IMPUNERE DUK (D300 R25=R12 neimpus -> TVA colectata supra-declarata; D101 d_reg/d_succ/cod_bug).
- T9 EXCEPTII BRUTE in loc de mesaj (D710/D390 decimal.InvalidOperation, KeyError).
- T10 UNREACHABLE = completitudine feature (rectificativa/succesor/grup/D406 Payments/CNP-03/D390 <cos>).
- T11 VALIDATOR IN URMA FORMEI (D112_209 anterior formei 605/2026 - campuri noi neverificate; infra, flag Costin).

Cele mai grave (d) - date gresite ajung la ANAF, nimeni nu prinde:
- D205 imp1≠rate×baza pe beneficiar MANUAL (trece de generator SI DUK).
- D300 CR-5 R12 fara R25 (V19/V20 neimpus) -> TVA colectata supra-declarata.
- D394 G-d1 CUI cu litere -> partener strain tip3/4 -> LS cota0.
- D406 coercitie UOM/plata/cota tacita -> date gresite DUK-valide.
- D390 CUI UE checksum-invalid fara diagnoza per-partener + tara mistypata -> partener disparut.
- D112 judet_casa bogus -> casa de sanatate gresita mascata.
- D710 suma_ded aruncat tacit.
Detalii complete per declaratie + surse: CATALOG_INVALIDITATE.md.

## 10.08.2026 (tura 29) — LANT legislatie TURA 3/4: mesajul catre utilizator (motivul exact al invaliditatii, PRE-DUK)

Comanda: ia fiecare declaratie x fiecare tip de date invalide; aplicatia sa prezinte MOTIVUL EXACT al
invaliditatii; repara tot ce gasesti. Reparate temele transversale din catalogul tura 28 (CATALOG_INVALIDITATE.md).
10 audituri/reparatii paralele, fiecare cu gard old-fail (HEAD 8b74ccb)/new-pass + proba DUK before/after pe date
POPULATE; baseline valid ramane DUK-valid la toate.

FUNDATIE T1: core/identitate.py (NOU, LEAF) - valideaza_cui/valideaza_cnp/valideaza_cif OFFLINE, sursa CANONICA
pentru declaratii. Validatoarele existau imprastiate (solduri_parteneri_api/salariati_import_api/tenant_provisioning)
si erau folosite DOAR la import, NICIODATA in generatoare - de-aici gap-ul 9/9. Verificat contra valorilor pe care
DUK le accepta/respinge (301111003 valid/301111004 invalid; CNP idem). Gard: core/test_identitate.py (dubla ancora
valid+invalid). Cele 4 validatoare vechi raman (au apelantii lor); consolidarea = curatare ulterioara.

REPARAT per declaratie (motiv EXACT pre-DUK; hard-block pe identitate obligatorie, avertisment unde blocajul ar
subtia nedrept declaratia - principiul Costin "utilizatorul afla, nu declaratia se subtiaza"):
- D100: T1 CUI firma checksum/format/lungime -> ValueError; T6 den/adresa supra-lungime -> avertisment.
- D101: T1 cif checksum; cod_obligatie ∉{102-105}; caen N(4); P-uri negative (set source-backed, exclude P23-33
  fara constrangere de semn); parent<Σsub; plafoane V2-V7. (CAEN full-list + checksum-uri pe randuri COMPUTATE =
  raportate, nereimplementate - n-ar adauga acoperire.)
- D112: T1 CNP angajat (format+checksum) + CUI firma; numeAsig gol / data_angajare NULL; caen/cod-boala out-of-enum
  (enum extras din XSD via _enum_xsd, nu tabel hardcodat); T6 serie/numar/diagnostic (D_1/D_2/D_23) overflow ->
  ValueError numind salariatul/campul. Fixtures reparate: test_d112_reconciliere (CNP ...012->...028 valid).
- D205: T1 CNP beneficiar checksum (c1) + CUI platitor (c2); CNP duplicat (tip_venit1+cifR) (c3) R41b -> ValueError
  numind beneficiarul. Fixtures reparate (de coordonator): test_d205_reconciliere (IONESCU ...012->...011),
  test_d205 test_id_inreg (beneficiar B CNP distinct). d1 (imp1≠rate×baza manual) -> TURA 4.
- D300: T2 valideaza() COD MORT -> CABLAT in genereaza (split severitate: _blocante_pre_duk->ValueError tip_decont
  A/S↔luna R18; _avertismente_marja->warn ±1%); T1 cui/caen/pro_rata. CR-5 (R25=R12 neimpus) -> TURA 4.
- D301: T2 valideaza() cablat (nr_doc/data_doc gol, tip/valuta out-of-nomenclator); T1 cif; an<2013; T6 nr_doc>C(20)
  (era leak pur); T3 tip=0/valuta-lipsa coercitii -> blocate cu motiv (nu default tacit). Rest -> TURA 4.
- D390: FLAGSHIP checksum_vies() OFFLINE (DE/HR/FR verificat contra DUK; restul "neverificat", zero false-pozitiv)
  -> avertisment PER-PARTENER numind partenerul + motiv + "va fi respins DUK R24.1"; tara mistypata (CR/EL) ->
  numit + sugestie + BLOCAJ (nu mai dispare tacit); codO>12 -> NU se mai trunchiaza (corupea TVA), blocaj; T2
  valideaza() cablat; telefon>15 clamp+avert, cui>10 blocaj; codO="" pt A/S omis. VIES full-27 = deferat (Costin).
  FINDING (non-circular): catalogul zicea "codO cerut doar L,T,P"; proba DUK a agentului INFIRMA (R fara codO ->
  R24.2 respins) -> pastrat L,T,P,R (DUK-ancorat), documentat.
- D394: T3/G-d1 CUI cu litere -> P_INVALID + BLOCAJ (nu mai devine tacit partener strain - cel mai grav);
  T1 cuiP checksum (R218.2/R218.3) + CUI firma (R6); T4 op1 C/V fara op11 -> EXCLUS (nu mai avertizeaza-dar-emite)
  + R233.5; N cu CUI de firma -> exclus R233.4. G-x1 asimetrie cota -> decizie produs (Costin).
- D406: T1 partener + CUI firma; E3/E4 CNP in tert_cui -> acum 03+CNP (CNP valid -> DUK valid; invalid -> ValueError)
  = fix de CONFORMITATE; T3 UOM/cota/PaymentMethod coercitie -> avertisment PER-ITEM numind factura+valoarea; T2
  AccountType cablat tintit (nu tot valideaza() - ar bloca fixtures + redundant cu reconcilierea). Payments/
  InvoiceType/TaxCode/BaseRate/HeaderComment/Country = NESONDAT (hardcodat, cer code-injection).
- D710: T9 exceptii brute -> ValueError prietenos (suma nenumerica/lipsa cod_oblig/negativa); T1 CUI; cod_oblig ∉
  nomenclator + cod_bugetar (R14a) + cota micro (R17) + scadenta calendar; C5 cod 131/132 -> blocat (era crash NPE).
  Fixtures reparate: test_d710 (escape-hatch buggy -> blocaj). J1 (suma_ded aruncat) -> TURA 4.

RAMAS pentru TURA 4 (reconciliere; semantic gresit-dar-consistent, DUK nu prinde): T7 (D205 imp1, D301 RON curs≠1
+ rotunjire, D710 suma_ded, agregare mis-contabilizata, D100 suma_dat), T8 (D300 CR-5 R25=R12, D101 d_reg/d_succ/
cod_bug). Decizii produs: D101 scadenta LL+3-vs-LL+6, D394 G-x1 asimetrie cota, D301 pers_inreg (coloana
inreg_art317), D390 VIES full-27, T10 completitudine feature (rectificativa etc.), T11 actualizare DUK D112_209.

Bump √ INVENTAR_A: clusterul "nomenclator COD_BUGETAR" (d710) 04.08->10.08 - functia test_cod_bugetar_nomenclator_
duk_si_antidrop a fost reparata (escape-hatch buggy -> blocaj), re-verificata DUK R14a.

## 10.08.2026 (tura 30) — LANT legislatie TURA 4/4: reconcilierea sursa-vs-declaratie (capstone)

Comanda: fiecare declaratie agrega dintr-o sursa (facturi/note/salarii/certificate); confrunta cap-la-cap sursa
pe perioada vs ce a raportat declaratia - diferenta = date pierdute pe drum. Inventariaza, verifica ce exista,
completeaza, gardeaza-le sa nu mai moara tacit (clasa D300 mort); ruleaza la generare SI se vede in Control fiscal,
din acelasi mecanism.

INVENTAR (2 straturi): (1) gen-gate `dXXX_reconciliere.verifica_reconciliere` cablat in genereaza (hard-block,
recompute INDEPENDENT non-tautologic din sursa vs res); (2) Control fiscal `control_incrucisat` (verde/rosu/gri).

COMPLETAT reconcilierile gen-gate LIPSA (recompute independent din sursa, non-tautologic, cablat, cu probe anti-mort):
- D100 (core/d100_reconciliere.py NOU): baza impozabila recalculata din cont 70x (SQL propriu) x cota (registru) vs
  res.suma_dat. Inchide #31 aggregation-loss (venit mis-contabilizat -> suma_dat gresit, azi DUK-valid).
- D301 (core/d301_reconciliere.py NOU): Sigma(baza per tip) din d301_operatiuni cu regula CORECTA (RON->curs 1) vs
  res. Inchide aggregation-loss + semanticul T7 (RON curs≠1 -> baza supraevaluata).
- D390 (core/d390_reconciliere.py NOU): Sigma(baza per tip)+nrOPI+total din facturi IC vs res (Layer-1 gen-gate,
  complementar cu Layer-2 verifica_d390 tolerant).

GAP-URI T7/T8 INCHISE (semantic gresit-dar-consistent pe care DUK nu-l prinde):
- D205 (d205_reconciliere): beneficiar MANUAL imp1 ≠ round(cota_dividend×baza1) -> ValueError (d1, cel mai grav
  D205; azi trecea de generator SI DUK). Verifica doua campuri declarate, fara ledger.
- D300 (d300 _oglinda_r12_r25): R25=R12 (V19/V20, NEIMPUS de validatorul instalat) -> ValueError (CR-5/T8; R12 fara
  R25 = TVA colectata supra-declarata, azi DUK-valid). Cablat in genereaza, calcul_d300 pastrat pur.
- D710 (d710): suma_ded aruncat tacit -> IMPLEMENTAT corect pt model 9# (cod 121: suma_plata=max(dat-ded,0), emite
  suma_ded_I/_C, reconciliaza totalPlata_A) / BLOCAT pt model 8# (cod 103: suma_ded interzis, DUK R14-21). CORECTIE
  DE SURSA non-circulara: premisa "model 8# = dat-ded" era gresita - proba DUK arata 8#=dat (deducere doar 9#).

META-GARD "NICIO RECONCILIERE NU MOARE TACIT" (core/test_reconciliere_vie.py) - generalizeaza gardul tura 14 de la
D300 la toate 9, MECANIC (AST, imun la mentiuni docstring): fiecare dXXX_reconciliere (a) exista, (b) e importat SI
apelat in genereaza (orice stil de import - un modul necablat = mort), (c) NON-TAUTOLOGIC (nu importa core.dXXX),
(d) are test_dXXX_reconciliere (proba de FIRE pe divergenta traieste acolo). D710 exceptat (input manual).

CONTROL FISCAL, ACELASI MECANISM (control_incrucisat.reconciliaza_declaratii + wiring in control_fiscal_api.
evalueaza_firma): pentru fiecare declaratie aplicabila ruleaza ACEIASI reconcilieri (forma reconciliaza, non-blocant)
si surfaceaza 3-state STRUCTURAT (declaratie+eticheta+mesaj+temei+remediu); escaladeaza pastila firmei -> divergenta
inrosaste firma in Control fiscal. ANTI-MORT clasificat: date lipsa -> GRI genuin; reconciliere care CRAPA
(semnatura/bug) -> ROSU "VERIFICARE INTRERUPTA" (NICIODATA gri tacit); divergenta reala -> ROSU numind ambele valori.
Probat: injectie aggregation-loss -> ROSU numind 310 vs 210; apel rupt -> ROSU-rupt, nu gri.

Fiecare reconciliere: gard old-fail/new-pass + probe anti-mort (fire pe divergenta injectata ROLLBACK) + baseline
DUK-valid. Doar 4163; 1968 neatins.

RAMAS (raportat): panel UI dedicat "Reconciliere surse<->declaratii" in main.py (findings deja curg prin
evalueaza_firma.reconciliere_surse + escaladeaza pastila; panelul per-declaratie cere edit front-end).

## 10.08.2026 (tura 30) — LANT legislatie COMPLET (TURA 1-4): declaratiile, cap-coada

Cele doua clase de risc, inchise cap-coada in 4 ture inlantuite:
- TURA 1 (tura 27): corpusul de legislatie la zi - actul care aproba forma fiecarei declaratii, adus din MO/ANAF.
- TURA 2 (tura 28): CATALOG_INVALIDITATE.md - exhaustiv, ce date invalideaza fiecare declaratie (11 teme transversale).
- TURA 3 (tura 29): mesajul exact al invaliditatii PRE-DUK (validator identitate partajat + reparatii pe toate 10).
- TURA 4 (tura 30): reconcilierea sursa-vs-declaratie (aggregation-loss + semantic) + meta-gard anti-mort + Control fiscal.
Rezultat: "declaratie invalida" (T1-3) si "declaratie valida care nu reflecta contabilitatea" (T4) - ambele acum
prinse PRE-DUK (mesaj exact) sau la reconciliere (divergenta sursa), nu tacit. Decizii produs deschise (Costin):
D101 scadenta LL+3/LL+6, D394 G-x1 asimetrie cota, D301 pers_inreg (coloana inreg_art317), D390 VIES full-27,
completitudine feature (rectificativa/succesor/grup), actualizare DUK D112_209, panel UI reconciliere.


## 10.08.2026 — Registrul FUNCTIONALITATI.csv = baza de cunostinte a AI-ului: descrierile trebuie sa fie ADEVARUL curent (Lot 0)
Decizie: coloanele servite AI-ului (raportari_ai.py: Functionalitate/Descriere/Acces UI, filtrate pe Stare LIVE) NU au voie sa descrie feature-uri ELIMINATE ca active. Un registru stale nu e cosmetica - AI-ul de triaj (F152) raspunde clientilor DIN el, deci minte.
Temei: comanda Costin ("un registru stale inseamna ca AI-ul minte utilizatorii; daca gasesti intrari care nu mai corespund realitatii, corecteaza registrul, nu doar codul"). Sursa: core/raportari_ai.py::_baza_cunostinte foloseste r[0]/r[1]/r[4] pe randurile LIVE.
Proba: contul gratuit ELIMINAT 26.07 aparea inca in 5 descrieri LIVE (F092/F171/F172/F180/F188) + F188 Sursa cod cita functia moarta register_gratuit. Toate reparate. Gard nou pe existenta fisierelor (test_sursa_cod_refera_fisiere_care_exista), ROSU pe registrul vechi.

Sub-decizie (grupare stabila la editarea descrierii): F188 fixat in EXPLICIT="Cabinet si portal client" in genereaza_grupe_functii.py. Gruparea VIZIBILA a paginii Functionalitati NU trebuie sa depinda de cuvintele din descriere - o corectie de text (scoaterea "cont gratuit") mutase F188 keyword-grup Cabinet->Contabilitate. Override peste keyword; login.js GRUPE_FUNC regenerat = identic (no-op).

RAMAS (nereparat, notat GARZI): F176 pastreaza cross-ref la F160 (ELIMINAT) in "e-Factura/e-Transport (F126/F160/F121), cinci pozitii un singur auth" - scoaterea lui F160 cere re-verificarea numaratorii "cinci pozitii"; harm mic (ID intern, nu claim user-facing). De reincadrat la Lot 1 (transversal, F176 e conectorul OAuth).

## 10.08.2026 — F116 headere de securitate: registru corectat la adevar, deploy = decizie infra (Lot 1)
Constatare: F116 pretindea "headere (HSTS, X-Frame-Options, X-Content-Type, Referrer-Policy)" dar nginx live are add_header=0 (zero headere pe raspuns 443, verificat 10.08). Registrul mintea (AI ar descrie protectii inexistente).
Decizie: registrul corectat la ADEVAR (headere NEDEPLOYATE). Deploy-ul NU se face nesupravegheat: nginx server config (/etc/nginx/sites-available/iconta) e root-owned, in afara git, ne-gated (fara poarta verde); reload afecteaza TOTI userii reali (inclusiv cabinet 1968); HSTS semi-permanent. Per §2.3 pct.3 (infra pe real = deployment, consemnat) + constrangerea "1968 nu se atinge" -> FLAG Costin (§6 raport Lot 1).
Recomandare: adu nginx server config sub versionare (config_server/) ca driftul de headere sa fie guardabil mecanic.

## 11.08.2026 — Sursa cod "CONCURENTA:" pe LIVE = drift (Lot 3, generalizare pe clasa)
Decizie: o functionalitate LIVE/PARTIAL nu poate pastra Sursa cod = referinta la concurent (SAGA/SmartBill/Oblio/WinMentor/FGO/Keez). La CONSTRUIRE se actualizeaza la modulul real. Referinta la concurenta e legitima DOAR pe non-LIVE (feature analizat, neconstruit - F127/F130/F149 etc.).
Temei: registrul e harta de cod a AI-ului (F152) + a dezvoltatorului; "CONCURENTA: Oblio" descrie de unde a venit IDEEA, nu unde e CODUL. Checkul de existenta din Lot 0 nu prinde (proza fara path-token).
Proba: 10 intrari LIVE reparate (F126/F138-142/F144-147) -> module reale (toate fisierele exista). Gard nou test_sursa_cod_nu_e_referinta_de_concurenta, ROSU pe cele 10 inainte.

## 11.08.2026 — ZERO-BASE la importurile de migrare: fisier nerecunoscut = eroare, nu 0 tacit
Decizie: un import care nu gaseste coloana-cheie de identificare RESPINGE (400), nu intoarce 0 randuri prezentat ca succes. Aliniaza toata familia la comportamentul retete/articole (care ridicau deja pe coloane lipsa).
Temei: comanda Costin (certificare comportament; ZERO-BASE: rezultat gol/zero = eroare pana la proba contrara; clasa "accepta orice fisier si declara succes" reparata doar punctual pe solduri strict=True).
Proba: feed gunoi comportamental (HTTP 200 total=0 inainte) + gard unit ROSU pe cod vechi. Cele 8 importuri: retete/articole aveau checkul; asociati/istoric/mijloace/salariati/solduri reparate acum. (solduri avea deja strict=True pe numeric; adaugat si checkul de coloana debit/credit.)

## 11.08.2026 — F116 headere securitate APLICATE pe nginx prod (constrangerea 1968 ridicata de Costin)
Decizie/executie: headerele promise in registru aplicate pe nginx prod dupa ce Costin a ridicat explicit "1968 neatins" pentru aceasta operatiune. CSP livrat prin Report-Only -> parcurgere (0 violari) -> enforce. HSTS max-age scurt (300s) intai, de urcat dupa verificare. Config adus sub versionare (config_server/iconta-nginx.conf).
Temei: comanda Costin (nivel infra, nu act fiscal). Proba: curl extern + login formular sub enforce + 38 ecrane 0 violari + 0 5xx.

## 11.08.2026 — DS §2.1 "exclusiv .camp-input" mecanizat (decizia Costin §6.1)
Decizie Costin: clasele ad-hoc pe input (.pr-input/.asi-per-sel + em-moneda-select/em-curs-input/dlg-input/fd-email-input/asi-cauta/firme-q) refactorate la .camp-input; toleranta verificatorului era LACUNA a uneltei, nu dezlegare. Extins verificatorul (INPUT_NECONFORM) sa prinda TOATA clasa - orice input non-.camp-input pica. Layout pastrat prin clase secundare (pr-den/pr-mic/em-cui/em-nume/fd-email-input flex/dlg-input width) + rehook JS (asi-per-sel -> data-per). Proba: gard rosu pe 27 (cod vechi), verde dupa; vizual nerupt.

## 11.08.2026 — Ajutor contextual: coloana separata + "?" selectiv + semn dinamic
Decizie (comanda Costin): ajutorul pentru contabil NU se amesteca cu descrierea tehnica -> coloana noua `ajutor` in FUNCTIONALITATI.csv (a 11-a), text in 7 sectiuni (Ce face / Cand / Ce pregatesti / Pas cu pas / Ce iese / Greseli / Reguli fiscale). Servit la runtime prin core/ajutor.py (cache la restart) via GET /ajutor/{fid}, randat in modal de semnAjutor(fid) + handler delegat global pe [data-ajutor].
"?" SELECTIV, nu peste tot (regula Costin): se pune unde exista regula fiscala / preconditie / consecinta / "ce se intampla dupa" care NU se vede din eticheta. NU pe butoane/campuri evidente (Salveaza/Anuleaza/Cauta/Inapoi/Denumire), NU pe CRUD evident (Parteneri F018/Produse F070/Clienti/Salariati-CRUD F078), NU pe infra fara UI directa (F001/F008/F092/F104/F105/F106/F116/F038/cronuri F110-112/F177-179).
Semn DINAMIC pe ecrane-wizard/meniu: la declaratii (mapare _DECL_AJUTOR tip->fid, 10) si operatiuni speciale (_OP_AJUTOR cheie->fid, 14), un singur "?" adaptiv urmareste selectia -> 24 functionalitati acoperite fara a aglomera meniul cu 24 de semne.
F014 Capacitate: ajutor scris (registru) dar "?" neplast — management pur, fara continut fiscal, ecran auto-explicativ.
Temei: comanda Costin (UI/produs, nu act fiscal). Valorile fiscale din texte (cote 21/11, plafoane diurna/sponsorizare, temeiuri OMFP 1802/2014, OMF 107/2025, CF, L52/2011, L141/2025, GDPR art.15/17/20) trimit la sursa oficiala, nu inventate. Proba: /ajutor/Fxxx -> 200 pe cele cu ajutor, 404 pe cele fara; modal end-to-end pe Casa 0 erori consola.

## 11.08.2026 — Ajutor de ansamblu: bun-venit la prima logare + "?" general, distinct de contextual
Decizie (comanda Costin): un cabinet NOU, la prima logare, vede o prezentare schematica a aplicatiei INAINTE
de operare; apare o singura data; dupa aceea semnul "?" GENERAL din bara de stare o redeschide oricand.
- Continut DERIVAT, nu scris separat: firul de intrare = STRATURI (migrare.js, 9 pasi, migrarea prima) +
  ansamblul = grupele din registru (genereaza_grupe_functii.repartizeaza, SURSA UNICA a repartizarii) +
  coloana `ajutor` (45 semne "?" contextuale in prezentare, care deschid ajutorul functionalitatii).
- DISTINCTIA general vs contextual (ceruta explicit): GENERAL = .nav-ghid, buton de bara-chrome (pill patrat cu
  grila 2x2 + "?", alb pe bara albastra, sus, langa clopot/iesire), deschide "Prezentarea aplicatiei" (tot
  ansamblul). CONTEXTUAL = .ajutor-btn, cerc mic albastru pe fond alb, inline langa eticheta, deschide
  "Ajutor · <functionalitate>" (un singur subiect). Diferite prin pozitie (bara vs inline), forma (patrat/grila
  vs cerc), culoare (alb-pe-albastru vs albastru-pe-alb), titlu si domeniu (general vs punctual).
- "Apare o data" = flag SERVER users.bun_venit_vazut_la (NU localStorage per-browser): urmareste cabinetul, nu
  tab-ul/dispozitivul. Userii EXISTENTI (inclusiv cabinetul real) backfill-uiti la "vazut" -> welcome-ul e doar
  pentru cabinete NOI (nu retroactiv; datele contabile neatinse, doar un flag de onboarding pus pe "onboardat").
Temei: comanda Costin (UI/produs, nu act fiscal). Alternativa RESPINSA: localStorage (per-browser -> ar reaparea
pe alt dispozitiv, n-ar respecta "prima logare a cabinetului"). Proba: browser end-to-end + TestClient (vezi TESTE).

## 11.08.2026 — Restart la publicare: NECONDITIONAT de tipul commitului (cablat, nu judecata executor)
Decizie/executie (comanda Costin): pasul de restart din ritualul de publicare NU mai decide dupa tipul commitului
(runtime vs docs). Cauza divergentei prinse la audit: restartam doar la commituri de runtime/CSV; un commit de
docs a lasat procesul viu pe commitul anterior (RUNNING b0ccc40 != HEAD f504f00). Rescrierea PREDARE descria
comportamentul, nu-l schimba - clasa ramanea deschisa (urmatorul commit de docs o reproducea).
- Mecanism: restart cablat in scripts/githooks/post-commit (dupa cele doua push-uri), NECONDITIONAT. NU s-a inventat
  un al doilea mecanism - s-a completat cel existent (post-commit facea deja push-ul, §2.3 pct.8).
- Gard: core/test_publicare_restart_neconditionat.py - cade la disparitia restartului sau la orice inspectie de
  continut in hook. Probat rosu/verde pe mutatie reala.
- STOP POINT (comportament vizibil cu utilizatori activi) MUTAT inainte de commit: decizia se ia cand alegi sa
  comiti, nu dupa; odata comis pe poarta verde, serviciul preia HEAD neconditionat.
Temei: CLAUDE.md §2.3 pct.10 (restartul era deja cerut neconditionat, doar necablat) + regula reparatiei reale
(elimini problema, nu o descrii). Alternativa RESPINSA: restart manual conditionat + descriere corecta in PREDARE.

## 11.08.2026 — ALFA date D406: CUI-uri sintetice valide + BUG generator nomenclator (expus de datele complete)
Decizie/executie (comanda Costin): tenant_013 facut apt de proba DUK prin constructie de date de test cu validitate
reala. CUI: NU s-a folosit CUI-ul niciunei firme reale (stop point Costin) - corectata DOAR cifra de control a
placeholder-elor secventiale existente (12345678->12345674, 87654321->87654329), pattern sintetic evident; restul
(143000000/145000006/301111003, DE/FR straine, PF gol) treceau deja.
DESCOPERIRE (proba pe date reale): popularea nomenclatorului clienti/furnizori a EXPUS un bug de generator
(core/d406.py pull() ~1123/1133): Partener(id=str(r["id"])) emitea id-ul BRUT din tabel ca RegistrationNumber/
CustomerID SAF-T (DUK "format invalid"), in loc de _partener_id_saft(cui)=00+CUI (cum face deja calea de fallback
cand nomenclatorul e gol). Fix dovedit throwaway -> DUK 'valid'. NEcomis: schimbare de GENERATOR (nu Payments, dar
tot generator) cu RAZA peste ALFA (la alti tenanti cu CUI de nomenclator invalid ar incepe sa RIDICE - corect: esec
zgomotos vs iesire tacit-gresita) -> cere decizia lui Costin, ca Payments. Temei: comanda + "arata defectele, nu le
ascunde" + "proba pe date reale". Alternativa respinsa: a fi comis fix-ul unilateral (garda generatorului).

## 11.08.2026 — D406 nomenclator: id brut de partener = bug PROD, reparat pe calea principala (PIVOT peste nota de mai sus)
Costin: e bug de PRODUCTIE, nu decizie de produs - "calea de rezerva corecta nu justifica o cale principala gresita".
PIVOT peste intrarea anterioara (11.08) care lasase fix-ul NEcomis pentru decizie: acum se COMITE. Reparat: pull()
foloseste _partener_id_saft si pe nomenclator (nu doar pe fallback) -> identitate SAF-T conforma (00/01/02/03/04),
o singura logica; dedup + passthrough ValueError (ca fallback-ul, sa nu mascheze CUI invalid in RuntimeError).
Gard anti-regresie: test_d406_partener_id_neconform. FAMILY-CHECK (cerut): tiparul "id brut ca identificator" NU
exista in D394/D390/e-Factura (folosesc valoarea CUI) -> clasa = D406, inchisa. Temei: regula reparatiei reale +
"clasa se inchide intreaga sau deloc". Stop-point onorat: tenantii care trec azi raman neschimbati (fallback neatins).

## 11.08.2026 — PIVOT: D406 depunabil structural (supersedeaza EXPLICIT "27.07 NU e depunabil")
Supersedeaza intrarea 27.07.2026 "D406 (SAF-T) NU e depunabil: gap cunoscut" (de la inceputul fisierului): motivul
ei - "SourceDocuments emite o SINGURA linie sintetica per factura + Payments gol -> NEDEPUNABIL" - NU mai e adevarat.
- INTERMEDIAR (27.07, dimineata): linie sintetica per factura -> nedepunabil.
- FINAL (azi): liniile REALE per produs reparate 27.07 (intrarea ulterioara din aceeasi zi) + period-aware 03.08;
  identitatea partenerului din nomenclator conforma (fix PROD 11.08: era id brut -> _partener_id_saft, gardat);
  DUKIntegrator -v D406 'valid' pe DATE REALE (tenant_013 2026-08).
RAMAS deschis, cu motivul REAL de AZI (nu iulie): F035 = Payments neemis (cod complet, pull() nu populeaza plati -
asteapta sursa maparei, decizie Costin); F036 = doar amortizare liniara (degresiva/accelerata art.28 neimplementate)
+ fragment; F037 = fragment (endpoint separat, nu in AuditFile lunar). Registrul F035/F036/F037 adus la PARTIAL
11.08.2026 cu motivul de azi (starile raman in enum: PARTIAL). Temei: SURSA UNICA - registrul e adevarul despre stare,
deci trebuie sa fie adevarat. DRIFT-CHECK pe restul registrului: singurele randuri cu stare pre-reparatie erau
F035/F036/F037; "bug" in alte descrieri = "buget", "mock" (F067/F123) descrie corect starea curenta, F076 "bug reparat"
e istoric-corect.

## 11.08.2026 — Modal landing: 3 functii LIVE scoase din EXCLUDE in lista publica
Decizie (comanda Costin): functiile LIVE vizibile in UI trebuie sa apara in modalul public "Functionalitati".
Reclasificate din EXCLUDE ("infra invizibila"/"meta") in EXPLICIT (grupa "Cabinet si portal client"): F083 (sinteza
zilnica pe email), F113 (PWA instalabila), F199 (export GDPR portabilitate) - capabilitati REALE de user, nu infra.
LASATE in EXCLUDE, cu motiv: F008/F104 (infra transversala), F117 (sanatate server, superadmin), F165 (CLI, nu UI),
F189 (mecanic regim SRL/PFA - suportul PFA e deja reprezentat prin features proprii: Motor D212, RIP, import RIP),
F200 (stergere cabinet = executie superadmin; cererea user F205 e deja in modal), F203 (modalul insusi). Migrarea (9)
ramane COMASATA intr-o intrare. Regula onorata: nu se promite public ce nu e LIVE (RESPINS/ELIMINAT/AMANAT/PLANIFICAT
raman afara). SURSA UNICA: modalul se genereaza din registru (repartizeaza), sincron gardat de GRUPE_FUNC_STALE.

## 12.08.2026 — Ghiduri publice pe volum: multi-slug + triere LIVE + grounding verbatim
Decizie (comanda Costin): pagini de ghid pe volum, fiecare la o intrebare distincta, sprijinite pe corpus (temei
verbatim + regula concreta + exemplu numeric + defect din practica), nu pe formulari generale. Extins mecanismul de
descoperire: ghid_slug suporta mai multe slug-uri separate cu "|" -> o functionalitate poate avea mai multe pagini
(F040 diurna: interna + externa, intrebari diferite). Triere respectata (20.07): doar LIVE cu valoare de client
(F040, F029). Grounding: fiecare valoare fiscala din anaf_surse (CF art.76, HG714/2018, Ordin 1235/2023, HG518/1995,
Legea 141/2025, OG 16/2022), ZERO din memorie. Verificat ca app-ul e corect INAINTE de a promite public: cota
dividende 16% e in common.py period-aware (eroarea 10% reparata). SARIT (fara temei in corpus / defect deschis / nu
LIVE) - se reiau cand corpusul/starea permit: vezi raport §5/§8.

## 12.08.2026 — Ghiduri pe volum: 9 pagini, grounding verbatim, valori 2026 din SURSA nu din memorie
Executie (comanda Costin, fara loturi, fara confirmari): scris toate paginile cu temei in corpus pe functiile LIVE.
Metoda: subagenti paraleli, fiecare citeste sursa din anaf_surse verbatim + verifica functia LIVE in registru + scrie
pagina; verificate pe citari inainte de publicare. DISCIPLINA SURSEI (dovada): agentul micro a corectat presupunerea
briefului (1%/3%, 500.000 euro) cu valorile REALE 2026 din Cod fiscal (cota UNICA 1% - OUG 89/2025; plafon 100.000
euro - OUG 8/2026) -> a urmat sursa, nu memoria. Agentul TVA la incasare a OMIS regula "90 de zile" (absenta din
versiunea consolidata) - corect. Toate 9 au intrebare distincta si temei verbatim; niciun SKIP la aceasta rulare.
RAMASE saritе (stop points): D101 (conflict lege/validator - decizie deschisa), D406 (PARTIAL, nu LIVE), e-Factura/
e-Transport (fara actul lor in anaf_surse). Ghiduri 6->15.

## 12.08.2026 — Ghiduri, lot final: regimuri speciale TVA + decont D300 (corpus puternic epuizat)
Inca 3 pagini verbatim: marja second-hand (art.312), agentii turism (art.311), decont D300 (art.323/303). Total 18
ghiduri. Corpusul cu regula concreta + numar (cote/plafoane/formule) e epuizat pe functiile LIVE. Ce ramane e ori
structural-subtire (D301/D710 = mecanica XML, fara regula punctuala noua), ori stop-point (D101 conflict, D406 PARTIAL),
ori fara act in anaf_surse (e-Factura OUG 120/2021, e-Transport OUG 41/2022 - absente din corpus).


### 13.08.2026 D392 CONFIRMAT SUSPENDAT LEGAL pana 31.12.2026 (scos din campanie)  (nu se construieste)
DECIZIE: D392 (392A/392B) NU se construieste - suspendat legal la data curenta.
TEMEI (verbatim, corpus local anaf_surse/oug_115_2023_consolidat.html, Articolul LXII): "Aplicarea prevederilor
art. 324 alin. (4)-(6) din Legea nr. 227/2015 ... se suspenda incepand cu data de 1 ianuarie 2024 si pana la data
de 31 decembrie 2026 inclusiv." Art.324 CF: alin.(4)=392A, (5)=392B, (6)=393. Confirma cu temei exact decizia
20.07 (F194 RESPINS). Sursa bate memoria: extras din actul consolidat din corpus, nu din memorie.
LIMITA: se reevalueaza inainte de termenele 2027 (392A/392B pe anul 2026 s-ar depune, in vechea logica, pana la
28.02.2027) - daca nu apare o noua OUG de prelungire, redevine obligatorie.

### 13.08.2026 D307 REACTIVAT din AMANAT - construit si LIVE (PIVOT peste AMANAT)  (F217, baafe62)
DECIZIE: D307 (ajustare/corectie/regularizare TVA) se construieste (cerut de Costin in campania de 6). Supersedeaza
starea AMANAT (F175). Coexista ca F217 LIVE (tiparul D207: F193 AMANAT + F209 LIVE).
TEMEI: are validator oficial ANAF (D307Validator.jar) -> proba MECANICA pe DUK, nu interpretare de PDF. OPANAF
793/2016; CF art.270(7) transfer active, art.324(8)(9), art.316(11) anulare cod TVA. PROBAT: DUKIntegrator -v
D307 'valid' pe tip A/L/C + d_anulare. Structura in vigoare v0/namespace :v1; atribut mail (nu email); TVA <=0 permis.


### 13.08.2026 Analytics public FARA date personale -> FARA obligatie de consimtamant  (F/ecran superadmin, 19d32f4)
DECIZIE: se inregistreaza evenimente publice de interes (deschidere modal, click Intra in cont, vizita ghid)
intr-o tabela public.eveniment_public care stocheaza EXCLUSIV: tip (lista alba), pagina (calea proprie curatata),
creat_la. NICIUN identificator de persoana - fara IP, User-Agent, cookie, sesiune, amprenta, user_id, referrer.
TEMEI: fara date personale => datele nu sunt personale in sensul RGPD => NU exista obligatia de consimtamant
(fara banner). Endpoint-ul public NU citeste si NU persista IP/UA (spre deosebire de _ip_client folosit doar la
rate-limit efemer). Precedent in cod: public.audit_log e deja fara IP/UA.
PROBA: garda core/test_eveniment_public.py cade daca DDL-ul sau schema reala capata orice camp personal
(ip/user_agent/cookie/sesiune/amprenta/user_id/referrer). sendBeacon nu trimite antete custom => niciun
identificator adaugat pe drum. LIMITA: fara identificator NU exista dedup/filtrare de boti - cifrele sunt brute
(chestiune de calitate a datelor, NU de confidentialitate); se consemneaza, nu se repara cu un identificator.


### 13.08.2026 Ajutor contextual: gard pe CLASA declaratiilor + clichet, NU completare fortata a tuturor LIVE  (78a2968)
DECIZIE: se completeaza ajutorul pentru cele 11 declaratii (sursabile din act) + gard mecanic dublu; NU se
completeaza fortat toate cele 87 LIVE fara ajutor. Multe din restul sunt infra/tehnice (Autentificare, Provisioning
tenant, Navigator, Design System, croane, securitate) - pentru ele "ce trebuie sa stie contabilul" ar fi INVENTAT
(punct de oprire respectat: se raporteaza, nu se completeaza din intuitie).
TEMEI: regula verificarii la sursa - textul "Reguli fiscale" al fiecarei declaratii vine din actul adus in corpus
(OPANAF + CF), nu din memorie. Unde nu exista sursa de continut contabil, nu se scrie.
PROBA: gard core/test_registru_functionalitati.py - (1) "Declaratia D*" LIVE fara ajutor -> rosu (mutatie F212);
(2) clichet baseline 76 (scop 0), orice LIVE nou fara ajutor ridica numarul -> rosu.
LIMITA: 76 LIVE inca fara ajutor (contabil-facing sursabile + infra) - de triat/scris la o trecere dedicata;
clichetul le tine sub control si forteaza descresterea. NU se relaxeaza baselineul in sus.


### 13.08.2026 Ajutor contextual COMPLET pe partea de contabil (50 scrise); raman 26 infra excepate  (f330941)
DECIZIE: cele ~50 de functionalitati LIVE orientate spre contabil primesc explicatie (executarea bucketului
"de scris" din decizia anterioara). Clichetul de acoperire coboara 76 -> 26. Cele 26 ramase sunt strict infra/
tehnice (auth, provisioning tenant, navigator, design system, croane, securitate, API, importuri de migrare):
raman FARA ajutor pentru ca explicatia "pentru contabil" ar fi inventata (punct de oprire) - nu au caz de
utilizare de contabil. Ele raman baza clichetului (26).
TEMEI: regula verificarii la sursa - fiecare afirmatie fiscala din cele 50 e ancorata pe act din corpus
(anaf_surse); o cifra fara temei in corpus a fost OMISA (ex. prag Intrastat), nu presupusa.
LIMITA: daca vreo functie "infra" devine cu adevarat contabil-facing, primeste ajutor si clichetul scade sub 26.


### 13.08.2026 Surse corpus: legislatie.just.ro BLOCAT server-side; consolidat doar via ANAF (CF+CPF) sau browser
DECIZIE: actele consolidate 'la zi' se aduc server-side DOAR pentru cele doua coduri (CF 227/2015, CPF 207/2015)
de pe static.anaf.ro; pentru restul, static.anaf.ro serveste doar forma initiala/republicata -> consolidatul se
aduce din browser (om) sau cu client cu amprenta de browser.
TEMEI: proba pe server - curl HTTP/2 -> PROTOCOL_ERROR, --http1.1/wget/urllib/requests -> empty reply catre
legislatie.just.ro (WAF pe amprenta TLS/HTTP). static.anaf.ro raspunde. Supersedeaza nota veche ca --http1.1 merge.
CONSECINTA: nu se pune in corpus forma INITIALA a unui act puternic modificat (e-Factura OUG120/2021,
e-Transport OUG41/2022) sub pretextul 'consolidat' - ar fi text expirat folosit ca in vigoare. Se raporteaza si
se aduce consolidatul separat.
FAPT CONFIRMAT: diurna interna 23 lei/zi e in vigoare in 2026 (OMF 1235/2023, adus in corpus). Valoarea din cod
si din paginile publice are acum act pe disc.


### 13.08.2026 PIVOT: legislatie.just.ro e blocat la NIVEL DE IP al serverului, NU de amprenta client (supersedeaza nota de mai sus)
CONSTATARE (corecteaza intrarea anterioara de azi care sugera 'de adus cu client cu amprenta de browser'):
descarcarea de pe just.ro NU e posibila de pe server prin NICIO metoda client-side. Probat serios, la cererea lui
Costin: curl (HTTP/2 -> PROTOCOL_ERROR; --http1.1 -> empty reply), wget/urllib/requests, SI chromium REAL
(playwright, headless, UA de browser, --disable-http2) -> ERR_EMPTY_RESPONSE / ERR_HTTP2_PROTOCOL_ERROR. In acelasi
timp, din acelasi chromium: example.com=200, static.anaf.ro=200. Deci blocajul e pe CONEXIUNEA server->just.ro
(IP/rutare/egress al serverului respins de WAF-ul just.ro, posibil declansat de accesele automate anterioare), NU
pe metoda/amprenta -> un browser real de pe server e blocat la fel.
DECIZIE: nu se mai incearca variatii client-side de pe server pentru just.ro (efort inutil). Ocolirea printr-un
proxy/alt IP ar fi circumventie ABUZIVA a unui control de acces pe care site-ul il aplica acestui host
(constrangerea lui Costin: 'nu ocoli protectiile in mod abuziv') -> INTERZIS. Actele consolidate de pe just.ro se
aduc din BROWSERUL OMULUI (alt IP), pe URL-urile predate. Rezultat concret: 0 din cele 43 aduse de pe server.


## 13.08.2026 — MF/D406 amortizare PE METODA (CF art.28): DATORIE 03.08 INCHISA

Continuarea datoriei din 03.08 (subsistem mijloace fixe): motorul D406/SAF-T (core/d406_active.py)
calcula amortizarea DOAR LINIAR (rata = amortizabil/dnf); metoda din activ (degresiva/accelerata/
superaccelerata) era MAPATA dupa cod dar IGNORATA in calcul. La import, "superaccelerata" era chiar
retrogradata tacut la "accelerata" (substring "acceler"), apoi calculata liniar. Decizie Costin:
optiunea C - se calculeaza pe metoda, cu golden pe fiecare + proba DUK.

TEMEIURI verificate VERBATIM la sursa (anaf_surse/cod_fiscal_227_2015_consolidat.txt, oug_8_2026.txt):
  - alin.(6) liniara: cota liniara la valoarea de intrare.
  - alin.(7) degresiva: cota liniara x coeficient - 1,5 (durata 2-5 ani) / 2,0 (6-10 ani) / 2,5 (>10 ani) -
    pe valoarea ramasa, cu trecere la liniar pe durata ramasa (comutarea e din metodologia normelor
    HG 1/2016 pct.25, al carei tabel an-cu-an e elidat in corpus; coeficientii sunt verbatim din alin.7).
  - alin.(8) accelerata: an 1 = max 50% din valoarea de intrare; anii urmatori = valoare ramasa /
    durata normala ramasa. Permisa doar echipamente/masini/unelte/computere (alin.5 lit.b).
  - alin.(8^1) superaccelerata (introdus de OUG 8/2026, art.6 pct.8, MO 147 din 25.02.2026): an 1 =
    max 65%; rest ca la accelerata. Doar active NOI puse in functiune 1 ian-31 dec 2026, subgrupele
    2.1 (echipamente tehnologice/masini/unelte/instalatii) si 2.4 (animale si plantatii); de la anul fiscal 2026.

IMPLEMENTARE (core/d406_active.py): calc_asset alege metoda din activ (_norm_metoda) si calculeaza:
liniar (cale pastrata byte-echivalent - fara regresie pe cele 14 teste D406 existente); ne-liniar prin
schema pe LUNI de utilizare (amortizarea incepe luna urmatoare PIF, alin.12), mapata pe ani calendaristici.
Degresivul foloseste _amort_anual_degresiv (coef pe durata + comutare la liniar). Accelerat/superaccelerat:
plafon an 1 (50%/65%) + rest liniar pe durata ramasa. Toate se aplica valorii amortizabile (valoare-rezidual)
si amortizeaza integral (accum final = amortizabil, book_end = rezidual). Sub 2 ani (dnf<24) metodele
ne-liniare nu au sens -> fallback liniar. DepreciationPercentage in XML = cota nominala liniara (100x12/dnf)
ca referinta; amortizarea reala a perioadei e in DepreciationForPeriod (DUK nu verifica acest camp aritmetic).

REGRESIE INCHISA: la import, superaccel se verifica ACUM inaintea acceler in AMBII normalizatori
(_normalizeaza_metoda din mijloace_fixe_import_api.py si _norm_metoda din d406_active.py), robust si la
"super accelerata"/"super-accelerata".

GOLDEN (core/test_d406_amortizare.py, 15 teste): activ 100.000 lei, rezidual 0, durata 60 luni, PIF
20.12.2025 (amortizare din ian.2026, ani utilizare = ani calendaristici). Cifre calculate de mana din lege:
degresiv 30.000/21.000/16.333,33/16.333,34/16.333,33; accelerat 50.000 apoi 12.500x4; superaccelerat 65.000
apoi 8.750x4; liniar ~20.000/an. Fiecare metoda amortizeaza integral. + test coeficienti degresivi pe durata
(1,5/2,0/2,5), test 50%/65% an 1, test fallback sub 2 ani, test ordinea superaccel<acceler in ambii normalizatori.

PROBA DUK (core/test_d406_active_duk.py, pe tenant_013 = ALFA MICRO SRL, CUI 301111003): generatorul
NOU d406_active.xml_d406_anual_active emite D406 ANUAL complet cu HeaderComment='A' (poarta care permite
sectiunea Assets - sursa: enumul AUDIT_FILE_TYPE din D406Validator.jar: L=lunar/T=trimestrial/C=la
cerere/A=anual; cu L/T Asset are max 0 aparitii). Profilul anual: perioada 1-12 pe acelasi an, toate
sectiunile non-Asset prezente dar GOALE, GeneralLedgerEntries gol, SourceDocuments cu cele 5 subsectiuni
(AssetTransactions cu NumberOfAssetTransactions=0), doar <Assets> populat. Fisier cu 6 active (2 reale
liniare din tenant_013 + 4 sintetice, cate una pe metoda) -> DUKIntegrator_AnLunaUI (pachet oficial ANAF)
raspunde stare='valid', zero erori. DUK accepta textul literal al metodei in DepreciationMethod (nu
verifica enumerarea acelui camp). NOTA: DUK verifica STRUCTURA, nu aritmetica - cifrele sunt pazite de
golden. RAMAS (nu blocheaza, nu e datorie): cablarea raportarii anuale de active in fluxul de depunere
(endpoint/UI) - D406 oricum nu e depunabil integral (vezi nota 27.07 - SourceDocuments pe continut real);
xml_d406_anual_active exista si e DUK-valid, gata de cablat cand se face raportarea anuala.

Marker inchidere datorie: **mf amortizare degresiva si accelerata calculate dupa metoda activului**. xfail
test_datorie_mf_metode_amortizare ELIMINAT.


### 13.08.2026 D406 amortizare: restrictii pe categorii (CF art.28 alin.5 + alin.8^1) aplicate in motor

calc_asset REFUZA acum (ValueError, nu downgrade tacit) metoda pe care legea nu o permite pentru categoria
activului. Categoria se deduce din cont_imobilizare, folosind denumirile conturilor din OMFP 1802/2014 (in
corpus - Catalogul HG 2139/2004 nu e in corpus):
 - 212 Constructii            -> alin.5 lit.a: DOAR liniara
 - 2131 Echipamente tehnologice (masini/utilaje/instalatii) -> lit.b (denumire OMFP = textul legii): lin/deg/accel
 - 2132/2133/214/necunoscut   -> lit.c ("oricarui altui mijloc fix"): lin/deg (FARA accelerata)
 - 2134/217 Animale si plantatii (subgrupa 2.4) -> lit.c (lin/deg) + superaccelerata (exceptia alin.8^1)
 - 211 Terenuri              -> neamortizabil (nicio metoda)
 - superaccelerata (alin.8^1): DOAR subgrupa 2.1 (2131) sau 2.4 (2134/217), cu PIF in 2026.
Refuzul se propaga in xml_asset/xml_assets si in endpoint (/tenants/{id}/d406-active -> 422 cu motivul).
Teste: core/test_d406_restrictii_metode.py (matrice categorie x metoda + propagare in XML + temei in mesaj).

DATE CARE LIPSESC din tabelul mijloace_fixe pentru verificarea COMPLETA (raportate lui Costin, NU inventate):
 1. "Computere si echipamente periferice" - lit.b le permite accelerata, dar in OMFP 1802 nu au cont propriu
    (stau in 214 birotica sau 2132) -> un computer inregistrat la 214/2132 e clasificat lit.c si i se REFUZA
    accelerata, desi legea o permite. Lipseste: un camp de categorie/subgrupa (Catalog) sau un flag "computer".
 2. "Activ NOU" (conditie alin.8^1 pt superaccelerata) - nu exista flag nou/la-mana-a-doua -> se verifica doar
    subgrupa + PIF 2026; conditia "nou" ramane raspunderea contabilului.
 3. Import-ul pune cont_imobilizare="2131" cand coloana lipseste (mijloace_fixe_import_api) -> un activ
    neclasificat devine "echipament" (permisiv, permite accelerata). Pana la un camp de categorie explicit,
    restrictia musca doar daca cont_imobilizare e furnizat corect.
Decizia de fond: se aplica ce se poate proba din date (constructii->liniar, transport/mobilier->fara accelerat,
fereastra superaccelerata), se refuza ce e clar interzis; ce nu se poate proba (computer lit.b, "nou") se
raporteaza in loc sa se ghiceasca.


## 13.08.2026 — Lot 2: 10 declaratii noi (D393/D395/D397/D200/D201/D204/D208/D216/D120/D600)

Setul de declaratii cu validator DUK instalat era EPUIZAT (toate 21 forme D + S1003/S1005 aveau generator).
Decizie Costin: se instaleaza validatoare noi de la ANAF si se construiesc 10 declaratii, la alegere, cu proba DUK.

INSTALARE: 15 validatoare aduse de pe serverul de update ANAF (static.anaf.ro/static/10/Anaf/update5/,
urlVersiuni din config.properties) in /home/costin/duk/dist/lib/. static.anaf.ro raspunde server-side
(just.ro ramane blocat la IP - vezi 13.08 corpus). validatoare_instalate() le vede pe disc.

CONSTRUITE (10), toate probate VALID pe validatorul OFICIAL (test_declaratii_lot2_duk.py):
  informative: D393 (bilete transport intl), D395 (colete postale ramburs), D397 (transport alternativ),
               D208 (transfer imobiliare - notari, semestriala);
  venituri PF: D200 (venituri Romania), D201 (venituri strainatate), D204 (asocieri f.p.j.);
  alte:        D216 (impozit special bunuri valoare mare), D120 (decont accize), D600 (baza CAS/CASS).

METODA (ca la loturile anterioare): STRUCTURA din VALIDATOR (arbitru) - radacina/namespace/campuri citite
din bytecode-ul DXXXValidator.jar si probate camp cu camp; GENERATOR MANUAL (valorile din input, ca d230/d104),
suma de control = suma din input; contract dXXX (NS/pull/erori_generare/calcul_dXXX/build_xml/genereaza).
Cablate: CHEIE_DUK, DECLARATII, _DOAR_API (toate 10 manuale), FUNCTIONALITATI.csv F218-F227 (LIVE + ajutor).

REGULA VERIFICARII LA SURSA - LIMITARE DECLARATA: actele OPANAF care aproba modelele NU sunt in corpus
(just.ro blocat la IP; static.anaf.ro nu le are consolidat). Deci semantica vine din ETICHETELE OFICIALE ale
validatorului (arbitrul ANAF) + regulile lui, NU din textul actului. In consecinta NU s-au fabricat cote/rate/
plafoane: D200/D201 nu calculeaza impozit (il stabileste ANAF); D216 nu hardcodeaza cota/plafon (vin din input;
COTA 0,3% din aritmetica e constanta impusa de validator, documentata); D120 nu precompleteaza niveluri de acciza;
D600 nu hardcodeaza plafoanele CAS/CASS. Actele raman de adus din browser (om) pentru sursa completa.

REGULI descoperite (arbitrul bate premisa): D204 versiunea in vigoare = radacina d204/ns v3 (nu declaratie204/v1);
D600 luna FIX 12; D120 totalPlata_A TREBUIE 0; D216 totalPlata_A = suma cifrelor din cif (R4); D208 structura reala
= tranzactie->imobile->(beneficiari + parti), partile obligatorii; D200/D201 sectiuni lowercase sect/sect_2.

DUK generatie noua (D216): DUKIntegrator.jar -jar cu DecValidation.jar VECHI din lib/ (2018) crapa
(NoClassDefFound/cod eroare) fara fisier de rezultat -> calea -jar ar fi raportat FALS "valid" (fisier gol=valid).
core/duk.py reparat: la marcaje de esec fara rezultat, reincearca cu DecValidation NOU (2024, din pachetul SAF-T)
pe classpath (general.Main); plus FAIL-SAFE anti fals-verde (eroare pe stdout fara fisier de rezultat -> gri, nu valid).
Aceeasi baza noua va debloca D177/D212/D398/D700 cand vor fi cablate. Fara regresie pe validatoarele vechi (D390/D406 probate).

### 13.08.2026 D177 - fals-verde preexistent EXPUS de fail-safe-ul DUK (lot 2)
Reparatia duk.py (retry generatie noua + anti fals-verde) a scos la iveala ca proba DUK a lui D177 era
FALS-VERDE: validatorul D177 e de generatie noua, iar generatorul core/d177.py produce root/namespace stale
(declaratie177, ns :v1) pe care validatorul CURENT il respinge ("element necunoscut"). Sub duk.py vechi, plain
-jar crapa fara fisier de rezultat -> raportat "valid". Acum se ruleaza prin DecValidation nou -> eroarea reala.
DECIZIE: test_d177_valid_pe_validatorul_oficial marcat xfail(strict) ca DATORIE (nu se ascunde, nu se lasa fals-verde);
d177 se reconstruieste dupa structura validatorului CURENT (root/ns/campuri), cu proba DUK, ca lotul 2 - task separat.
Doar D177 e afectat dintre declaratiile cablate (D406 foloseste calea SAF-T separata; D212/D398/D700 nu-s cablate).

### 14.08.2026 D177 REPARAT — datoria din 13.08 INCHISA (root D177 + totalPlata_A=0)
Verificare forensica ceruta de Costin (respingerea e reala? ce difera?): respingerea era REALA, dar strict pe
NUMELE RADACINII - generatorul emitea <declaratie177>, validatorul curent (J2.0.3, pachet v1, activ pt 2025 din
_dateVersionTable) cere <D177>. Namespace IDENTIC (mfp:anaf:dgti:d177:declaratie:v1), TOATE atributele (radacina
+ beneficiar) recunoscute, niciunul lipsa. Dovada: schimband doar rootul in <D177> dispare "element necunoscut".
In plus, doua reguli de VALOARE nesatisfacute de vechea proba fals-verde: totalPlata_A trebuie = 0 (vechea
formula round(sumaRest/100) era FALS-confirmata pe validatorul vechi care crapa tacit), si perioada = an fiscal
complet (R6: dataSfarsit = 31.12.an cand dataInceput e in acelasi an; R4.1: luna = luna din dataSfarsit = 12).
FIX core/d177.py: radacina declaratie177 -> D177; calcul_d177 totalPlata_A "0"; docstring corectat.
FIX core/test_d177.py: date an fiscal 2025, CUI beneficiar valid, luna=12, control_sum asteapta "0"; xfail
ELIMINAT - test_d177_valid_pe_validatorul_oficial trece GENUIN pe validatorul oficial (via DecValidation nou din
duk.py), nu mai e fals-verde. Singura declaratie afectata era D177 (verificat: din 31 cablate, doar d177+d216
sunt generatie noua; d216 valida corect). Datorie INCHISA.

## 14.08.2026 — Compensari cu tertii (core/compensare.py): corpus actualizat intai, apoi motor

Compensarea reciproca a creantelor si datoriilor fata de acelasi partener (client 4111 + furnizor 401).
Cerinta Costin: "verifica la sursa; daca actul lipseste, actualizeaza corpusul intai".

CORPUS ACTUALIZAT INTAI (acte aduse de pe surse reachable non-just.ro; just.ro ramane blocat la IP):
- Cod civil (Legea 287/2009) art.1616-1623 - compensarea legala (codulcivil.ro).
- OUG 77/1999 - baza sistemului de compensare intre operatori (legex.ro; forma initiala, modificata ulterior).
- HG 685/1999 - Norme compensare (legex.ro). ATENTIE: ABROGAT de HG 773/2019 (01.01.2020) -> marcat "abrogat"
  in INDEX (gen_index _ABROGATE, inlocuit_de hg_773_2019). Surse neoficiale (disclaimer legex/codulcivil).
INDEX.json regenerat (PYTHONPATH=. venv/bin/python anaf_surse/gen_index.py).

MOTOR (core/compensare.py, PUR, ca decontari_asociati): suma_compensabila = min(creanta, datorie);
nota_compensare -> 401 = 4111 pe suma compensata; propune_compensari (doar partenerii cu AMBELE solduri > 0);
pull din solduri_parteneri (411* debit = creanta, 401* credit = datorie).
TEMEI verbatim din corpus:
- Cod civil art.1616 "se sting pana la concurenta celei mai mici" -> min; art.1617 (certe/lichide/exigibile,
  preconditii confirmate de contabil); art.1618 (excluderi).
- OMFP 1802/2014 pct.56 alin.(3): compensarea se inregistreaza DUPA contabilizare; valoarea BRUTA se prezinta
  in note -> nota pastreaza brutul + resturile, nu doar netul; alin.(1) necompensarea e despre PREZENTAREA in
  situatii, distincta de stingerea reala.

NEHARDCODAT (regula verificarii la sursa): pragul de la care compensarea intre operatori intra in sistemul
electronic - HG 685/1999 (care il stabilea) e abrogat, iar HG 773/2019 (pragul curent) nu e in corpus.
necesita_sistem_electronic(suma, prag) intoarce None fara prag (necunoscut, nu False); pragul se da din
configurare dupa aducerea HG 773/2019. De adus din browser: HG 773/2019 (consolidat, pt plafonul curent).
Teste: core/test_compensare.py (min art.1616, nota 401=4111 echilibrata, brut/rest pct.56, ambele-parti
obligatorii, prag None, sursa in corpus). 9 teste.

### 14.08.2026 HG 773/2019 adus integral; necesita_sistem_electronic re-cablat (NU exista prag valoric)
Fisierul HG 773/2019 din anaf_surse era SHELL-ul JS al just.ro ("Se incarca", fara corpul actului) -> sters.
Textul INTEGRAL al Normelor (Art.1-10) adus de pe surse reachable non-just.ro (theexperts.ro + contabilul.
manager.ro, cross-check; partea dispozitiva din PDF Lege5/alcont.ro) -> hg_773_2019_norme_monitorizare_
datorii_nerambursate.{html,txt,sha256}; INDEX regenerat (in vigoare).
CONSTATARE (sursa bate premisa): HG 773/2019 NU contine niciun prag VALORIC in lei. Pragul ~10.000 lei (100 mil
ROL) apartinea HG 685/1999, ABROGAT de HG 773/2019 (Art.3 al hotararii). Actul in vigoare foloseste criteriul de
VECHIME: facturi restante mai vechi de 30 de zile de la emitere/scadenta (Norme Art.2 alin.1), pentru persoane
juridice cu capital de stat; sistemul e SIC (Sistemul Informatic de Compensare), gestionat de CPPI Busteni;
"compensare = stingerea... pana la concurenta obligatiei celei mai mici, prin ordine de compensare" (Art.3 lit.a
- coroboreaza regula min din Cod civil art.1616).
CABLAT (core/compensare.py): necesita_sistem_electronic(varsta_factura_zile, cu_capital_de_stat) = varsta > 30
si capital de stat (PRAG_VECHIME_ZILE=30, temei HG 773/2019 Art.2), NU pe suma; fara varsta -> None.
propune_compensari ia varsta din input (per partener); pull pe solduri (balante) nu are varsta -> semnal None
(onest). Teste actualizate (test_sic_pe_varsta_factura_hg773 + sursa in corpus include hg_773).

## 14.08.2026 — Campanie "toate declaratiile ramase": clasificare + Lot 3 (6 declaratii)
Din 60 forme D/B oferite de ANAF, 31 erau construite. Cele 29 ramase: 19 declaratii FISCALE constructibile;
10 EXCLUSE cu motiv (D392 suspendata legal; D017/D085/D092/D163/D700 = inregistrare/mentiuni/optiune; D179 =
cerere de compensare; D180 = nota de certificare; B230/B900 = borderouri). Toate cele 29 validatoare instalate
de la static.anaf.ro.
LOT 3 construit (generatoare MANUALE, structura din validator = arbitru, probat DUK VALID fiecare):
D106 (informativa dividende de stat, OPANAF 1292/2014, root declaratie106), D108 (impozit reprezentanta,
CF Titlul VI = 18.000 lei/an, root D108), D114 (CAM, CF Titlul V, root D114, lunara), D130 (decont titei,
OPANAF 1950/2012, root declaratie130), D318 (rambursare TVA din alt stat UE, art.302 CF + Directiva 2008/9,
root D318, sumaControl=0), D603 (exceptare CASS, art.154 CF, root d603).
ACTE: aduse in corpus de pe static.anaf.ro (D106 OPANAF 1292/2014; D130 OPANAF 1950/2012; D318 instructiuni +
art.302 CF). D108 = temei CF Titlul VI deja in corpus. D603/D114 = temei in CF (art.154 / Titlul V) in corpus,
dar OPANAF-ul dedicat (3697/2016, resp. formularul CAM) NU e liber obtenabil (lege5 auth-wall / just.ro blocat)
-> semantica din validator, gol raportat.
Cablate CHEIE_DUK + DECLARATII + _DOAR_API + FUNCTIONALITATI F228-F233 (+ genereaza_grupe_functii --scrie).
Teste: core/test_declaratii_lot3_duk.py (6; d106 cu conn mock - trage header din firma_profil).
RAMASE de construit (valuri urmatoare): D101G, D169, D169n, D119, D213, D214, D398, D399, D401, D402, D403,
D407, D212 (declaratia unica - complex).

## 14.08.2026 — Campanie declaratii ramase: Lot 4 (6): D119/D169n/D213/D214/D401/D402
Construite (manuale, structura din validator, probat DUK VALID - core/test_declaratii_lot4_duk.py):
D119 (declaratie speciala BNR, root D119, lunara), D169n (neconcordante beneficiar real fiducie/AML,
OPANAF 2175/2025, root D169n), D213 (instrainare pachet control terenuri agricole extravilan, OPANAF 216/2023
+ Legea 17/2014 art.42, root D213), D214 (instrainare prin hotarare judecatoreasca, OPANAF 216/2023, root D214),
D401 (proprietati imobiliare nerezidenti - DAC, root declaratie401, depusa de primarie), D402 (venituri
salariale nerezidenti - DAC1, OMFP 2727/2015, root declaratie402). Acte aduse de pe static.anaf.ro/ilegis.ro
(D169n/D213/D214/D402); D401 = semantica din validator (act DAC de adus); D119 = scop din pagina ANAF.
Corectii premisa (sursa bate premisa): D169n NU e despre e-TVA ci beneficiar real fiducie; D213 NU e norme de
venit agricol ci instrainare pachet control. Toate conn=None (manuale). Cablate CHEIE_DUK/DECLARATII/_DOAR_API/
FUNCTIONALITATI F234-F239. Total declaratii cablate: 43.
RAMASE: D101G (grup fiscal profit), D169 (fiducie inregistrare), D398/D399 (OSS/IOSS TVA), D403/D407 (DAC2/DAC
asigurari-financiare), D212 (declaratia unica - complex).

## 14.08.2026 — Campanie declaratii ramase: Lot 5 (6): D169/D398/D399/D403/D407 (+ D101G datorie)
Construite (manuale, structura din validator, probat DUK VALID - core/test_declaratii_lot5_duk.py):
D169 (inregistrare fiducie, L.129/2019, root D169, generatie noua - DecValidation nou), D398 (OSS TVA UE/non-UE,
art.314/315 CF, root d398 minuscul, generatie noua), D399 (IOSS TVA import, art.315^2 CF, root declaratie399,
trimestriale), D403 (DAC2/CRS asigurari viata, OMFP 2727/2015, root declaratie403), D407 (institutii financiare
raportoare, root D407, semestriala). Toate conn=None (manuale). Corectii premisa: D407 = polite/instrumente
financiare (nu DAC/CRS conturi); D169 vs D169n = inregistrare vs neconcordante.
D101G (grup fiscal impozit profit) - CONSTRUIT corect pe forma v2 (P01-P16, OPANAF 206/2025 in corpus, root
declaratie ns v2) DAR proba DUK BLOCATA de infrastructura: schema de structura v2 D101G nu e deployata in DUK pe
server (dist/lib/DecValidation.jar vechi nu cunoaste d101g; SAF-T DecValidation cere v1 hardwired pt toate
perioadele; niciun XSD d101g instalat). DATORIE: test_declaratii_lot5_duk.py::[d101g] = xfail(strict); se
probeaza cand se instaleaza DecValidation care cunoaste d101g v2. Modulul e cablat si folosibil (produce XML v2).
Cablate CHEIE_DUK/DECLARATII/_DOAR_API/FUNCTIONALITATI F240-F245. Total declaratii cablate: 49.
RAMASE: D212 (declaratia unica persoane fizice - complex, ns v11).

## 2026-08-14 — D212 Declaratia Unica (lot 6, final campanie declaratii)

**Cerinta:** ultima declaratie ramasa din campania "construieste toate declaratiile ramase".

**Ce s-a construit:** `core/d212.py` — generator MANUAL al Declaratiei Unice (impozit pe venit +
CAS/CASS persoane fizice: PFA/II/IF, chirii, investitii, alte surse). Root `<d212>`, ns
`mfp:anaf:dgti:d212:declaratie:v11`. Caz minim = identificarea (cif/nume_c/adresa_c); capitolele
sunt extensibile prin `manual`: cap11 (realizat, cap.I), cap12 (estimat, cap.II), cap14,
oblig_realizat/oblig_estimat, coasigurat. Atribute root obligatorii (d_rec, rectif1/2,
totalPlata_A, luna_r=12, an_r, bifa_succesor, anulare_litA/B, bifa_conformare, bifa111..bifa15,
nerezident, cif, nume_c, adresa_c) puse pe valori neutre. totalPlata_A calculat (nu hardcodat).

**Distinctie fata de F030:** `core/d212_engine.py` (F030) = motorul de CALCUL in sistem real
(venit net, plafoane CAS/CASS) din RIP > Fisa D212. `core/d212.py` (F246) = generatorul XML-ului
OFICIAL pentru depunere. Fisiere si functionalitati distincte.

**Sursa/temei:** structura din `D212Validator.jar` (arbitru); act adus in corpus ca
`anaf_surse/D212_IstoriaVersiunilor.txt` (+.sha256), inclus in INDEX prin gen_index. CF art.148-149,
154, 170 (CAS/CASS persoane fizice). Scadenta 25 mai.

**Proba DUK:** `core.duk.valideaza("d212", ...)` → **valid** pe calea STANDARD (retry-ul
DecValidation nou din core/duk.py il proceseaza corect). NB: la build initial subagentul a raportat
ca standardul esueaza cu NoClassDefFoundError dec/DECTagCtx si ca doar un merge chirurgical de clase
dec ar valida — acel caveat NU se confirma pe server: `core.duk.valideaza` intoarce valid direct.
Deci, spre deosebire de D101G, D212 NU e datorie de infrastructura — e complet probat.
Test: `core/test_declaratii_lot6_duk.py::test_d212_duk_valid` (proba reala, nu xfail).

**Cablat:** CHEIE_DUK "d212":"D212"; declaratii_api import + _d212 dispatch + DECLARATII
"d212":("anual",_d212) + _DOAR_API (cere date de identificare, deci doar-API, ca celelalte manuale);
FUNCTIONALITATI F246 (LIVE, cu ajutor); GRUPE_FUNC regenerat.

**Campanie declaratii — bilant:** construite si probate DUK 19 declaratii fiscale in loturile 3-6:
lot3 (d106,d108,d114,d130,d318,d603), lot4 (d119,d169n,d213,d214,d401,d402),
lot5 (d169,d398,d399,d403,d407 + d101g DATORIE), lot6 (d212). Total DECLARATII in dispecer: 50.
Datorie ramasa: D101G (schema v2 OPANAF 206/2025 neinstalata in DecValidation pe server — xfail strict).


## 2026-08-15 — D300 remediere: decizii de arhitectură (B1-B4, HEAD c8d3947)
- **Rânduri manuale D300 PERSISTATE, nu efemere prin body.** Tabel d300_manual + 3 rute REST (core/d300_manual_api.py);
  genereaza citește rândurile din DB. MOTIV: paritate preview<->depunere - calea /coada regenerează decontul
  server-side FĂRĂ body.manual (ca la d301); dacă rândurile ar sta doar în body-ul din UI, depunerea prin /coada le-ar
  pierde. Persistența garantează că ce vede contabilul în preview = ce se depune.
- **Cele 3 câmpuri noi pe facturi OBLIGATORII (NOT NULL DEFAULT) de la început** (tert_tara, tip_operatiune,
  furnizor_tva_incasare). Nu opționale/nullable: un câmp de clasificare TVA lipsă = rutare tăcut greșită. tert_tara
  backfill din prefixul VIES al CUI (RO/DE/... din codul de TVA), nu default fabricat.
- **Convenție bunuri-implicit pentru IC** (livrare -> R1, achiziție -> R5 + R18): în lipsa unui câmp bunuri/servicii pe
  factură, generatorul presupune BUNURI și avertizează pentru reclasificarea serviciilor. Limita și convenția stau
  împreună - vezi datoria din GARZI (15.08 - D300 remediere).

## 2026-08-15 — Bun-vs-serviciu IC = proprietate a operațiunii, SURSĂ UNICĂ partajată D300<->D390 (nu câmp, nu sursă duplicată)
- **Decizia.** Bun-vs-serviciu la operațiunile intracomunitare este o **proprietate a OPERAȚIUNII** (reclasificare),
  nu a declarației, și nici "un câmp lipsă pe factură". Sursa e UNICĂ: tabelul `d390_reclasificare`, scris o singură
  dată din panoul D390 (F125) și CITIT de AMBELE declarații (D300 via `d300._incarca_reclasificari` -> `d390.pull_reclasificari`;
  D390 via `d390.calculeaza` -> `pull_reclasificari`). Reclasificarea **MUTĂ**, nu adaugă: emisă P -> D300 rd.3 (R3/R3.1)
  și D390 bazaP (nu R1/L); primită S -> D300 rd.7+rd.20 (oglindă net zero) și D390 bazaS (nu R5+R18/A).
- **De ce (corectează formularea anterioară).** Nota de la 2026-08-15 ("convenție bunuri-implicit, în lipsa unui câmp")
  descria doar JUMĂTATE din model: D300 primise implicitul de la D390 (emisă->L, primită->A) FĂRĂ mecanismul de corecție.
  Costin a semnalat inconsecvența: "o singură sursă cu gard care face imposibilă reapariția rândurilor auto peste cele
  reclasificate" + "cele două declarații trebuie oricum să se reconcilieze între ele". Nu se introduce un al doilea câmp
  pe factură (ar duplica sursa și ar putea diverge de D390); reclasificarea rămâne singura sursă.
- **Validată pe DIRECȚIE.** Tipul reclasificat e validat contra direcției la scriere ȘI la citire (aceeași regulă,
  `d390._reclasificare_tip` + `TIPURI_DIRECTIE`): emisă acceptă L/T/P/R, primită A/S; un tip nelegal ridică eroare
  vizibilă, nu revine tăcut la default (misclasificare). Gard de reconciliere cross-declarație:
  core/test_d300_b1_rutare.py (test_recon_*). Probă pe date reale: firma grea tenant_017, iulie 2026 (D300 R3_1/R7_1 ==
  D390 bazaP/bazaS, DUK valid).
- **Limită declarată rămasă:** T/R (triangulație / regim special agricultori) NU sunt pe axa bun-serviciu — rutate
  numeric ca bunuri, semnalate explicit, neacoperite pe D300 (raportat separat).

## 2026-08-15 — Plimbarea lui Costin: decizii de canal, formulare si versionare
Cinci decizii luate la remedierea celor 8 constatari (commituri 58e2aed / 8a965f4 / 434efa3 / 087b33a).
- **Canalul neutru de rezultat se numeste in cod `note_rezultat`, NU `constatari`.** Verificatorul rezerva numele de
  lista `constatari` pentru verdictele cu temei (control fiscal); un al doilea inteles pe acelasi nume ar dilua gardul.
  Rezultatele neutre (ex. „fara erori DUK”) circula pe canalul `note_rezultat`, separat de `avertismente`.
  Eticheta din UI ramane „Constatari” (limbaj de utilizator), dar cheia de date e note_rezultat (087b33a, #7).
- **„Validat cu DUKIntegrator (validatorul oficial ANAF rulat local)” - validarea NU e depunere.** Formularea
  veche „Validat la ANAF” sugera o depunere care nu s-a intamplat; textul spune acum explicit ca s-a rulat
  validatorul oficial local si ca „Nu a fost depusa la ANAF” (8a965f4, #4).
- **Coada afiseaza perioada DECLARATA ca perioada, scadenta e etichetata explicit „termen”.** lista_coada
  intoarce perioada din payload (an/luna/trim) -> „august 2026”; scadenta apare pe rand separat ca
  „termen (scadenta)”, ca sa nu se confunde luna declarata cu termenul (8a965f4, #3).
- **Cardul de pe ecranul principal e patru-ochi-aware.** Cu patru-ochi ON -> „De validat”; cu patru-ochi OFF
  (mono-utilizator) -> „De depus”, pentru ca fluxul de coada e neconditionat (mono-utilizatorul depune cap la
  cap), deci si afisajul trebuie sa reflecte actiunea reala (8a965f4, #2).
- **Versionarea asseturilor = hash de continut, nu contor manual.** Tokenul ?v= nu mai e o decizie umana de
  incrementat (sursa de eroare la #1); e derivat mecanic din continutul fisierului si gardat (087b33a). Vezi GARZI 15.08.


## 16.08.2026 — tip_decont (periodicitate TVA) NU se fabrica
ANAF v9 nu intoarce periodicitatea TVA (lunar/trimestrial) — confirmat la sursa (`anaf_api.valideaza_cui` n-are cheie de
periodicitate; comentariu si in `migrare.js`). Decizie: NU se fabrica o valoare implicita (regula 4). Ramane alegerea
contabilului; lipsa la un platitor e semnalata EXPLICIT in completitudinea profilului (`firma_profil_api.blocaje` ->
"D300/D394: periodicitatea TVA nu e aleasa"), nu prin "—" tacut. Q8 din parcurgerea onboarding CUBUS (16.08).

## 16.08.2026 — amortizarea "la zi" pe metoda; casat = necunoscut explicit; ultima luna absoarbe rotunjirea
Ecranul MF + notele (lunara/casare/reevaluare) calculau liniar ignorand metoda. Sursa unica de amortizare =
motorul core.d406_active (CF art.28). Trei alegeri de CORECTITUDINE (nu de produs — cifre afisate/inscrise):
1. Casat: amortizat/ramas = None (instantaneul de la casare nu se pastreaza in mijloace_fixe -> necunoscut
   declarat explicit, regula 4), NU 0/valoare-plina (fostul default tacit, gresea in sens invers).
2. Ultima luna de amortizare absoarbe restul de rotunjire (liniar SI neliniar) -> suma amortizarilor lunare
   1..dnf = valoarea amortizabila EXACT; un activ nu se amortizeaza cu mai mult/putin decat costul-rezidual.
3. Metoda nepermisa pe categorie NU se calculeaza liniar tacit: eroare pe rand (ecran) / 422 (note), care
   NUMESTE categoria si metodele permise (mesajul din _verifica_categorie).
Motivul comun: amortizarea e fapt fiscal (DS cap.17) — o singura sursa, fara default tacit al cifrei.

## 16.08.2026 — preview=salvare: o singura poarta de validare (verifica_randuri)
Previzualizarea si salvarea NU pot fi doua cai de cod care valideaza acelasi camp (DS cap.24). `extrage`
ramane PARSER (poate seta flaguri de parsare cnp_valid/ok), dar VERDICTUL de validare — la preview SI la
salvare — vine dintr-o singura sursa: `verifica_randuri`. Preview il intoarce (`erori`), importa il ridica.
Normalizarea tuplu(parteneri)/lista intr-un singur loc: `migrare_api.erori_verifica`. Decizie de a NU sterge
flagurile lui extrage in aceasta tura (risc de consumatori nedescoperiti); ele nu mai sunt autoritatea de
validare. Efectul vizibil: la preview, randurile pe care salvarea le-ar respinge sunt aratate si Salvarea e
blocata — corectitudine (ce vede userul), nu decizie de produs.

## 16.08.2026 — skip la importul de salariati: NU exista; textele se aliniaza la BLOCARE
Importul de salariati NU sare randuri cu CNP invalid - le BLOCHEAZA (importa() ridica la prima poarta,
verifica_randuri). Decizie: eliminam codul mort (sarite_cnp + bucla de skip) si textele care promiteau skip
("vor fi sarite" / "X sariti"), in loc sa "reparam" skip-ul (care ar fi pierdere tacuta de date - exact ce
gardul D1a voia sa evite). Superseda test_salariati_skip_surfatat_in_ui (premisa falsa). Alinierea textului
la comportamentul real = CORECTITUDINE (text care descrie ce face aplicatia), nu decizie de produs.

## 16.08.2026 — periodicitatea declaratiilor TVA: EFECTIVA (tip_decont), nu statica (C7)
Pentru setul TVA-decont (d300/d394/d406), periodicitatea care decide parametrul cerut (luna vs trim) e cea
EFECTIVA a firmei (tip_decont) - ACEEASI sursa ca /declaratii/tipuri si wizardul, NU periodicitatea statica din
harta. Firma trimestriala trimite `trim`; generatoarele sunt ancorate pe LUNA (agrega trimestrul din ultima
luna), deci dispecerul `genereaza` converteste trim->luna-ancora (T*3) intr-un SINGUR loc, dupa validare.
Corectitudine (declaratie blocata), nu decizie de produs. C8 (format data nativ la Casa) = NU defect de
aplicatie (locale de browser), verificat la sursa - NEreparat, cu motiv (nu se fabrica un fix pentru un nedefect).

## 16.08.2026 - pontaj neconfirmat pe Stat de plata: stare de PERIOADA, afisata GRI (C1)
Starea "pontaj neconfirmat" e o stare de PERIOADA (an,luna,domeniu=pontaj), nu un atribut de salariat.
DS cap.23: se afiseaza o data, GRI (.caseta-info + semafor gri), NU rosu (nu e atentionare). Marcajul
per-salariat rosu "pontaj neconfirmat" (firme.js) implica FALS ca pontajul altui salariat ar fi confirmat
(aceeasi luna, aceeasi stare) - defect de adevar. Consecinta REALA per-salariat = "tichete blocate" (doar
la cei cu tichete>0), afisata gri. Audit tenant_003: Ana (tichet=40) marcata, Radu (tichet=0) nu - diferenta
cheiata pe tichete, confirmata la sursa (stat_plata_api.py:67). Corectitudine (text ce descrie starea), nu
decizie de produs.

## 16.08.2026 - import per firma: dupa salvare, revenire pe traseu la firma (C2)
Dupa salvarea unui strat de import (per firma), navigarea revine cu nav.inapoiPas() la ecranul de la care
s-a plecat (meniul firmei sau lista de firme din wizard), NU deschide o fereastra NOUA de wizard de CABINET
(care arata toate firmele - "in afara firmei pe care lucra contabilul"). Mesajul de succes supravietuieste
revenirea prin var de modul _migMesaj (tiparul _bonuriMesaj), consumat la re-randare (arataMesaj "ok", DS
cap.6). Corectitudine UX (feedback + pozitie), aliniere la tiparul deja rezolvat (bonuri, retete, status-save).

## 16.08.2026 - model CSV descarcabil la toate straturile de import; format din parser (C4)
Fiecare strat de import cu fisier ofera "Descarca model (CSV)"; formatul = citit din PARSER
(core/*_import_api.py), nu din textul de pe ecran. Adaugat la 8 straturi (parteneri/salariati/asociati/
mijloace/istoric/articole/retete/rip); solduri il avea. plan_conturi = cautare/adaugare (fara upload), exclus.
Intro-ul care descrie coloanele trebuie sa NUMEASCA tot ce citeste parserul: mijloace (cont imobilizare +
amortizare) si articole (cont stoc + cheltuiala) omiteau conturi citite la import -> completate. Model comun
(_descarcaModelCSV + MODELE), exemple realiste care trec parserul (probat round-trip pe mijloace).
Corectitudine (text care descrie ce accepta aplicatia), nu decizie de produs.

## 17.08.2026 - poarta verde vizuala (CLAUDE.md §2.3 pct.11): axe+mobil+baseline pe ecranele atinse
Ceruta de Costin. Nicio poarta verde fara cele trei unelte vizuale rulate pe ecranele ATINSE in tura, cu
rezultatele (CU CIFRE) in raport §3. Obligatie de EXECUTOR - cer app viu + browser + auth, deci NU se cableaza
in pre-commit (ca restartul, pct.10). O tura care nu a atins niciun ecran e SCUTITA, dar o DECLARA explicit
("niciun ecran atins -> uneltele vizuale N/A"). Extinde Regula 14 din MEMORY.md (axe + profil telefon la orice
ecran atins). Gardat structural de core/test_infra_vizuala.py. Uneltele: frontend_test/vizual/ (README acolo).

## 17.08.2026 - verdictul de control fiscal: diacritice + fara nume intern de camp (audit tenant_004)
Ecranul Control fiscal al tenant_004 (Distributie Profit IC SRL) arata 13 mesaje de verdict (D300/D394/D406/D100/
D101/D390 necompletat + 2x "necunoscut declarat") in proza romaneasca FARA diacritice, unul scurgand numele
coloanei din baza (platitor_tva_anaf_inceput) in loc de label-ul UI. TEMEI: DS cap.1 (text afisat = diacritice) +
Regula 14 pct.4 (nume intern aratat utilizatorului = defect). Corectitudinea textelor care descriu ce face
aplicatia NU e decizie de produs (comanda 17.08). Reparat toate 13 + trimis la label-ul real "Data inregistrarii
in scopuri de TVA". Gard dedicat test_control_fiscal_diacritice.py: gardul canonic le rata pentru ca sunt args
pozitionale la emitenti / return-uri de builder, nu roluri recunoscute. Clasa mai larga (erori de generare
declaratii afisate contabilului) DECLARATA deschisa in GARZI - distinctie user-facing vs developer ne-mecanica.
Matricea de 64 neatinsa; 221 teste tinta verzi.

## 17.08.2026 - Thunk-urile de reconciliere NU re-implementeaza derivarea generatorului [audit tenant_002]
DECIZIE: derivarea obligatiilor unei declaratii traieste O SINGURA data, in generator (d100.deriva_obligatii),
si e CHEMATA de reconcilierea din control_incrucisat (_thunk_d100), nu re-implementata de mana. TEMEI: copia de
mana din _thunk_d100 driftase de d100.pull/genereaza (profit-base-fix 16.08) -> crash "too many values to unpack"
clasificat gri pe fiecare firma + baza profit pe venituri (latent). Aceeasi clasa ca test_control_incrucisat_wiring
(d300 semnatura). PROBA: test_reconciliere_d100_wiring RED (micro gri-crash, profit gri-crash) -> GREEN. LIMITA:
d205 re-deriva la fel inline dar NU e driftat azi (verificat prin rulare, derivarea coincide); pattern-ul persista
acolo, neguardat end-to-end - vezi raport 17.08 sect.5.

## 17.08.2026 - reg_com obligatoriu in bilant: poarta blocheaza, nu doar avertizeaza [audit tenant_002]
DECIZIE: lipsa Nr. registrul comertului OPRESTE generarea bilantului (S1005 si S1003), nu doar adauga
avertisment soft. TEMEI la sursa: DUKIntegrator -v S1005 respinge XML-ul fara regCom ("atributul trebuie sa
existe", pachet oficial ANAF reguli 2026.1) - un bilant fara regCom NU e depozitabil. Aliniaza codul cu
promisiunea UI existenta ("Nr. registrul comertului - blocheaza Bilant S1005") si cu contractul portii
erori_generare ("STOP cu mesaj clar, nu XML respins de ANAF"). PROBA: test_bilant_regcom_poarta RED (S1005+
S1003 emiteau XML) -> GREEN. Corectitudinea declaratiei nu e decizie de produs (comanda 17.08).

## 17.08.2026 - Selecturile vector obligatorii cer alegere explicita (fara default fabricat) [audit tenant_001]
DECIZIE: regim_fiscal, platitor_tva, operatiuni_ic la NULL se afiseaza ca alege (nu prima optiune reala) si
salvarea cere alegere explicita (tri-stare: gol -> null, NU false tacit). Backend respinge platitor_tva=None
(TVA_LIPSA), simetric cu operatiuni_ic care era deja corect. TEMEI: Regula 4 (fara valori implicite fabricate) +
DECIZII 23.07 (frontendul distinge nesetat de Nu, fara preselectie) + DS cap.6 (validari preventive cu mesaj
langa camp). partida_simpla (PFA/II/PFL) expus din vector_fiscal_api.citeste -> regimul NU se pretinde la partida
simpla (n-are micro/profit). PROBA: 2 garzi RED->GREEN + proba vizuala Playwright (selecturile alege, Salvarea
blocheaza cu mesaje per-camp, DB ramane NULL). Corectitudinea nu e decizie de produs (comanda 17.08).

## 17.08.2026 - declarant: se cere EXPLICIT in profil + avertisment la generare (fara fabricare tacita) [tenant_001]
DECIZIE: declarant_nume + declarant_functie sunt OBLIGATORII in profil (Date firma le cere, cu declaratiile pe care
le blocheaza; salveaza_date valideaza) - la fel ca regim_fiscal. La GENERARE, cand lipsesc, generatorul emite
implicit "ADMINISTRATOR" (DUK respinge campul gol al declarantului) DAR ANUNTAT prin avertisment - tiparul
preexistent d301/d390, extins la TOATE (d100/d101/d205/d112/d300/bilant). declarant_prenume ramane optional
(fallback "-" legitim in forma ANAF). TEMEI: Regula 4 (fara valori fabricate tacit) + DS cap.6. XML NESCHIMBAT
(amprenta/DUK neatinse - warn-ul e doar in avertismente, nu in XML). PROBA: garzi RED->GREEN + behavioral D112
(tenant_001, declarant NULL -> avertisment emis, XML tot ADMINISTRATOR). Corectitudinea nu e decizie de produs.

## 17.08.2026 — Import salariati: salariu_brut obligatoriu si > 0 (audit tenant_005)

**Decizie.** `salariati_import_api.verifica_randuri` respinge randurile cu salariu de baza lipsa/0/negativ (motiv `salariu_lipsa`), ca poarta unica a importului — aceeasi invarianta ca la creare (`salariati_api` #8: brut obligatoriu > 0). Pana acum importul verifica CNP/data/norma/ore/judet/IBAN dar NU salariul; comentariul din verifica_randuri (linia ~189) recunostea explicit gaura ("brut 1500 la norma intreaga sub minim... toate au intrat, migrarea a zis gata").

**Temei.** Cod fiscal art.146(5^6)/168(6^1) — podeaua CAS/CASS sub salariul minim: un salariat cu baza 0/lipsa produce suprataxa angajatorului pe podea (cost pozitiv) desi net 0. DS cap.17 (fara default fiscal fabricat: parser `_numar` intoarce 0.0 pt coloana absenta) + cap.6 (validare preventiva cu mesaj) + MEMORY §13 (data lipsa se semnaleaza explicit, nu se calculeaza tacit). Un CIM la norma intreaga nu poate avea baza sub minim/zero (Codul muncii art.164).

**Proba.** tenant_005 (P2, Constructii Profit Trim): salariatul Ionescu Marin are `salariu_istoric.salariu_brut=0` -> Stat de plata 08/2026 afiseaza "brut 0 · net 0 · cost 825" (825 = cas_suprataxa 589.29 + cass_suprataxa 235.71, podeaua pe baza zero), fara niciun semnal. Gard RED->GREEN: `test_salariu_brut_lipsa/negativ_e_respins` (pe cod vechi verifica_randuri intoarce [], accepta tacit).

**Ramas (front deschis).** Datele REZIDUALE cu brut=0 deja in baza NU sunt reparate de gardul de import; Stat de plata inca afiseaza "cost 825" tacit pe ele. Semnalul pe ecranul Stat de plata (brut 0 -> "salariu de baza lipsa") = cluster separat.

## 17.08.2026 — Editare salariu cablata + semnal baza lipsa pe Stat de plata (audit tenant_005)

**Decizie.** Cardul de salariat (Stat de plata) primeste butonul „Salariu” care cableaza `PUT /salariati/{id}` cu {salariu_brut, valabil_din} — editarea/marirea salariului nu exista in UI (doar creare „+ Salariat nou” + editari IBAN/COR/incetare). `SalariatEdit.valabil_din` adaugat la model (backendul `actualizeaza_salariat` il onora deja prin kwarg). `stat_plata` intoarce `baza_lipsa`/`salariu_baza`; cardul semnaleaza baza contractuala lipsa/0 in rosu, cu trimitere la butonul de corectie.

**Temei.** MEMORY §13 (aplicatia lasa omul sa ajunga la tot ce poate produce + semnaleaza explicit data lipsa). DS cap.5 (INPUT in-ecran) + cap.6 (mesaj de stare). Cod fiscal art.146(5^6)/168(6^1) (suprataxa sub-minim care producea cost 825 pe baza 0). Continua decizia 17.08 (import salariu_brut obligatoriu): importul BLOCHEAZA baza 0, iar Stat de plata SEMNALEAZA + ofera corectia pt datele reziduale/legacy.

**Proba.** tenant_005 Ionescu Marin (brut=0): Stat de plata arata brut 0 / cost 825 tacit; acum badge rosu + sub-linie + buton „Salariu” prin care se pune salariul real (UPSERT pe istoric la data angajarii). Gard RED->GREEN `test_stat_plata_semnaleaza_baza_lipsa` (KeyError pe cod vechi).

## 17.08.2026 — Import articole: stoc fara pret = invalid (audit tenant_005, Regula 13)

**Decizie.** `articole_import_api.extrage` respinge un articol cu cantitate > 0 dar pret 0/lipsa (motiv afisat in preview, rand rosu). Pana acum verificarea inline respingea doar valori negative; un pret 0 (coloana absenta -> parser 0.0) trecea ca valid, iar `importa` scria miscarea de intrare cu valoare 0.

**Temei.** DS cap.17 (fara default fabricat) + principiul necunoscut-ramane-necunoscut. Contabil: un stoc real e evaluat la cost de achizitie > 0 (OMFP 1802/2014); cantitate fara cost = date lipsa, nu valoare 0. Acelasi tipar ca salariu_brut (import salariati) — generalizat prin sweep pe toata familia de import.

**Proba.** Gard RED->GREEN `test_articole_stoc_fara_pret_e_invalid` (pe cod vechi articolul 'Nisip 200 buc fara pret' = valid; dupa = invalid, motiv 'are stoc dar pret unitar 0/lipsa'). Articol fara stoc (cant 0) fara pret ramane VALID (nomenclator pur). Sweep restul modulelor de import: curate.

## 18.08.2026 — existenta_firma_an numara achizitiile IC + casa/banca (audit tenant_006)

**Decizie.** `control_incrucisat.existenta_firma_an(an)` (premisa restantelor D100/D101/D406-neplatitor) numara acum, pe langa facturi/salariati/inregistrari, orice OPERATIUNE DATATA in an: d301_operatiuni (achizitii IC), casa_operatiuni, extras_linii (banca), bonuri, chitante, mijloace_fixe (data_pif). Nomenclatoarele (articole/furnizori/plan) si soldurile_initiale/parteneri (pot preceda existenta firmei) raman EXCLUSE explicit.

**Temei.** Regula 14 pct.2 (cifrele care descriu aceeasi operatiune pe acelasi ecran coincid) + Regula 4/13. Un NEPLATITOR cu achizitii intracomunitare (tenant_006, Achizitii IC Neplatitor SRL) isi inregistreaza activitatea in d301_operatiuni, nu in facturi. Semaforul afisa simultan "operatiuni intracomunitare inregistrate in iun 2026" (restanta D301, din d301_operatiuni) SI "nu pot demonstra ca firma era activa in 2026" (D100/D406, din existenta_firma_an care ignora d301) — aceeasi operatiune, doua verdicte opuse. Criteriul de activitate = tabel de operatiuni datate, autor firma.

**Proba.** existenta_firma_an(tenant_006, 2026): False -> True (are 1 d301_operatiuni an=2026, 0 facturi). Semafor dupa fix (apel direct evalueaza_firma): D100/D406 2026 T1+T2 trec din NECLAR "necunoscut declarat" in LIPSA (restante concrete), aliniat cu D301 iun; 2025 ramane "necunoscut" (fara activitate demonstrabila). Consistent cu tenant_005 (are facturi 2026 -> aceeasi cale). Gard RED->GREEN `test_existenta_activitate` (4 teste, schema temporara). Suita control/premisa/matrice: 198 passed. Limita declarata: euristica ramane la granularitate de AN (nu de trimestru).

## 18.08.2026 — D100 micro pe FAPT (baza de venituri): d100_fapt (audit tenant_006)

**Decizie.** `obligatii_datorate` gateaza D100 micro pe FAPT (baza de venituri a trimestrului), simetric cu d390_fapt/d112_fapt: True=are venituri -> restanta; False=trimestru inchis fara venituri (si fara facturi emise) -> neaplicabil cu temei; None=venituri 0 dar exista facturi emise (posibil necontabilizate) -> emit (reminder). Poarta DOAR pe restante (termen<azi); obligatia curenta/viitoare se emite normal. Fara callback (matrice de 64) -> comportament vechi. Gateaza DOAR micro; profit (D101) neatins.

**Temei.** D100 pe zero e STRUCTURAL invalid la DUKIntegrator (sectiunea <obligatie> obligatorie >=1, anaf_surse/d100_struct_anaf.txt; d100.genereaza REFUZA "pe zero"). Un trimestru inchis fara venituri NU are D100 de depus -> semaforul care il arata restanta afirma o obligatie care dovedit nu poate exista (Regula 13 corectitudine, nu decizie de produs). Baza calculata din ACEEASI sursa ca generatorul (d100.pull + deriva_obligatii).

**Proba.** tenant_006 (achizitie IC, fara venituri): D100 T1/T2 2026 trec din LIPSA (restanta) in NEAPLICABILE "nu se datoreaza - fara venituri"; raman D301+D406. tenant_003 (venituri 0, D100 REFUZA "pe zero" la generator): la fel, neaplic consistent cu generatorul (inainte: restante moarte). tenant_002 T1 (are venituri) -> restanta pastrata. Gard test_d100_fapt (5 teste pure + mutatie-probata: dezactivarea portii -> restantele [2025-12,2026-3,2026-6] reapar). Regresie: matrice/premisa/termene/control/d100 = 232 passed.

## 18.08.2026 — a11y contrast Control fiscal + import blockages verificate (audit tenant_006)

**Decizie.** Contrastul pe ecranul Control fiscal (panou #e9edf3) reparat SCOPED: codurile declaratiilor `.cf-rand-decl/.cf-incr-cap .mig-sold-cont` var(--albastru) #347ab8 (3.87) -> #2f6fa6 (4.53); sub-textul verdictelor `.cf-incr-temei` var(--gri-semafor) #9aa3b2 (2.16) -> #5c6675 (4.95). Token global neatins (ca `.camp-ajutor` in v2.42). Regula noua (DS v2.43): un token AA pe ALB nu e neaparat AA pe un panou colorat.

**Temei.** WCAG 2.1 AA 1.4.3 (4.5:1 text normal). axe-core pe Control fiscal: 17 perechi color-contrast serious, 2 tokeni. Ecran neacoperit de auditul a11y tenant_005 (dashboard/vector/salariati).

**Proba.** axe contrast=0 pe Control fiscal dupa fix (era 17), captura privita (identitate vizuala pastrata, lizibilitate imbunatatita). Gard `test_a11y_contrast_tokens.py` extins cu 2 perechi (recalcul din sursa pe #e9edf3), mutatie-probat RED (culorile rele -> 2 failed). versioneaza_assets --scrie (stil.css re-stampilat, 2 fisiere).

**Import blockages verificate CURAT (Regula 14 pct.4).** Provocate vizual pe tenant_006: (a) salariati cu CNP invalid -> rand marcat rosu+warning, cutie de eroare VIZIBILA "rand N: NUME: CNP invalid (motiv)", buton Salveaza dezactivat; (b) solduri neechilibrate -> "debitul difera de credit cu 500,00. Corecteaza fisierul (debit=credit) inainte de salvare", badge neechilibrat, Salveaza dezactivat. Ambele: camp marcat, motiv vizibil (nu title-only), consecinta, unde se corecteaza, diacritice, fara nume interne. axe pe Vector fiscal + Date firma: contrast=0 (curate); contrastul e izolat pe Control fiscal.

## 18.08.2026 — Field-level error marking + front D390 (decizie ascutita) — audit tenant_006

**Decizie (field-marking, front 3 LIVRAT).** `eroareCamp`/`curataEroriCamp` (api.js) marcheaza acum si INPUTUL cu eroare (clasa `camp-invalid` + aria-invalid + contur rosu), nu doar mesajul ancorat. App-wide (7 ecrane). Override CSS cu specificitate 0,7,1 ca sa invinga bordura globala `!important` (contrast_ferestre_v1, 0,6,1). Temei: Regula 14 pct.4. Proba: captura privita Date firma (2 campuri goale rosii, dispar la corectare); gard test_fieldmark mutatie-probat.

**Front D390 <-> d301 (front 2, RAMANE DECIZIE, ascutit).** Verificat la sursa: art.325 CF + OPANAF 705/2020 - un art.317-inregistrat CHIAR datoreaza D390 cod A pentru achizitii IC de bunuri. DAR blocajul NU e doar "D390 nu citeste d301": `d301_operatiuni` are doar (tip, nr_doc, data_doc, val_valuta, curs, tva) - NU are codul TVA + tara FURNIZORULUI, pe care D390 cod A le CERE (codT/codO). Deci D390 cod A nu se poate construi din d301. Fixul corect = decizie de produs pe fluxul datelor: (a) extinzi d301_operatiuni cu TVA+tara partener, SAU (b) achizitiile IC intra ca facturi (care au partenerul). Plus firma trebuie art.317=True (tenant_006 e False). Nu reparat - cere alegere de produs + confirmare temei.

## 18.08.2026 — D390 pe zero semnaleaza achizitiile din d301 (front 2, corectitudine) — audit tenant_006

**Decizie (corectitudine, LIVRAT).** Cand D390 refuza "pe zero" DAR exista operatiuni in d301_operatiuni in perioada, mesajul le SEMNALEAZA si indruma spre adaugarea manuala (Tip A - achizitie bunuri IC, cu tara + cod TVA furnizor), in loc de mesajul generic "verifica facturile UE" (fals cand firma ARE achizitii in D301). Mirror al refuzului D301 care semnaleaza facturile IC neintroduse.

**Temei.** Regula 4 (nu spune fals "nu ai operatiuni") + art.325 CF / OPANAF 705/2020. D390 SE POATE produce manual - PROBAT: linie cod A -> genereaza XML valid (nr_opi=1); DUK valideaza algoritmul codului TVA furnizor (a respins un cod DE fabricat, corect). Deci nu e blocaj de corectitudine, ci ghidaj anti-omisiune.

**Auto-derivare d301->D390 (RAMANE DECIZIE, recomandare EXECUTOR: NU).** Full auto-derivarea ar cere coloane noi partener (cod TVA + tara) in d301_operatiuni + camp in ecranul D301 (pe care D301 nu-l cere) + migrare DB, si beneficiaza DOAR firmele art.317 (caz de margine, achizitii rare). Recomand SA NU se construiasca: calea manuala (UI clasificare Tip A) + avertismentul acopera corect fluxul. De redeschis daca volumul art.317 o cere.

**Proba.** tenant_006 (1 d301 op iun, 0 facturi): mesajul D390 semnaleaza acum "1 operatiune in D301... adauga manual Tip A". Gard RED(mutatie)->GREEN test_d390_d301_semnal. 19 passed d390.

## 18.08.2026 — Auto-derivare d301_operatiuni -> D390 cod A/S (decizia Costin, CONSTRUITA) — audit tenant_006

**Decizie (Costin, peste recomandarea executorului de a NU construi).** Achizitiile IC ale unui neplatitor art.317, inregistrate O SINGURA data in ecranul D301 (d301_operatiuni cu furnizor), alimenteaza AUTOMAT D390: tip 1/3 (bunuri) -> cod A, tip 5 (servicii IC) -> cod S; tip 2 (transport nou) + tip 4 (art.307 mixt, nu toate IC) EXCLUSE (clasificare manuala daca e cazul). Se deriveaza DOAR operatiunile cu TARA furnizorului (codT obligatoriu in D390; codO poate lipsi = NOTA 1).

**Parti.** (A) Migrare DB: d301_operatiuni + partener_tara/partener_cod/partener_den (core/migrare_d301_partener, mirror tenant_template.sql; 19/19 scheme). (B) API+UI: d301_operatiuni_api (parse+valida+insert+lista furnizor) + ecran D301 (3 campuri furnizor optionale + nota + indicator grila "fara furnizor -> nu intra in D390"). (C) Generator: d390.operatiuni_din_d301 injectat in calculeaza ca linii pre-tipizate A/S INTOTDEAUNA; reconcilierea a-doua-cale primeste _pull_d301 PROPRIU (independent, aceeasi mapare). (D) Refuzul-pe-zero rafinat: daca d301 are operatiuni fara tara, indruma spre completarea furnizorului.

**Temei.** art.325 CF + OPANAF 705/2020 (D390 art.316/317). Maparea tip D301 (OPANAF 592/2016) -> cod D390 (bunuri->A, servicii->S) la sursa.

**Proba.** tenant_006 op tip 1 cu furnizor DE (129273398) -> D390 auto-derivat, DUK VALID (baza 52261, cod A, codO in XML). Captura privita ecran D301 (campuri furnizor + indicator "⚠ fara furnizor — nu intra in D390 (cod A)"). Gard: cele doua cai (generator + reconciliere) coincid (mutatie mapare -> divergenta). 103 passed regresie (d390/d301/reconciliere/control/audit_schema).

## 18.08.2026 — tip 3 (produse accizabile) -> D390 cod A: VERIFICAT sursa+DUK + rafinare avertisment

**Verificare (Regula 5).** OPANAF 394/2017 anexa 2 (instructiunile D390 citate de aplicatie), coloana "Tipul operatiunii": cod A = "achizitii intracomunitare de bunuri" - TOATE achizitiile IC de bunuri (art.308 CF), FARA excludere pentru produse accizabile. Produsele accizabile SUNT bunuri -> tip 3 -> cod A CORECT. Confirmat la DUK: op tip 3 cu furnizor DE -> `<operatie tip="A" ...>`, rezumat bazaA populat, DUK VALID. Simetric: tip 5 -> `tip="S"`, bazaS, DUK valid.

**Rafinare avertisment (defect adiacent gasit).** achizitii_d301 (folosit la refuzul-pe-zero) numara acum DOAR tipurile auto-derivabile (1/3/5) FARA tara - operatiunile care AR TREBUI in D390 dar nu au aparut. tip 2 (transport nou) / tip 4 (art.307 mixt) NU se numara nici cu tara: nu intra in D390 nici asa, deci a spune "lipseste tara" ar fi fals. Inainte: tip 2 cu tara declansa fals "completeaza tara furnizorului".

**Proba.** tip 2/4 cu tara -> mesaj GENERIC (D390 pe zero legitim); tip 1/3/5 fara tara -> mesaj care semnaleaza d301. Gard test_achizitii_d301_numara_doar_mapabile_fara_tara (tip 2/4 cu tara + tip 1/3/5 fara tara -> count 3). 116 passed regresie d390.

## 18.08.2026 — tip 4 (art.307 alin.(3)(5)(6)) EXCLUS din D390: VERIFICAT la sursa + nota UI

**Verificare (Regula 5).** Codul fiscal art. 307 (anaf_surse/cod_fiscal_227_2015_consolidat), alineatele care compun D301 Sectiunea 4 (tip 4): alin.(3) = gaz/energie electrica/termica (art.275(1) lit.e/f) de la nestabilit -> LIVRARE cu loc in RO, nu achizitie IC; alin.(5) = bunuri iesite din regim suspensiv (art.295(1) lit.a/d) -> operatiune INTERNA; alin.(6) = taxare inversa GENERALA pentru livrari/prestari cu loc in RO de la nestabilit neinregistrat -> nu IC. NICIUNA intracomunitara -> tip 4 EXCLUS din declaratia recapitulativa D390 e CORECT. Serviciile IC (art.307 alin.2) NU se pun ca tip 4, ci ca tip 5 (S4.1 = subset al S4, OPANAF 592/2016) -> cod S, deja mapate. tip 2 (mijloace transport noi) exclus (raportare speciala).

**Efect UI.** Grila D301 arata acum pentru tip 2/4 o nota "(nu intra in D390 — transport nou / taxare inversa locala, art. 307 alin.(3)/(5)/(6))", CHIAR daca au furnizor - contabilul stie ca excluderea e intentionata, nu o omisiune. Comentariul mapicarii _D301_TIP_COD (d390.py) actualizat cu temeiul precis (era vag "amestec").

**Proba.** Captura privita: op tip 4 cu furnizor DE -> nota "nu intra in D390 — taxare inversa locala art. 307 alin.(3)/(5)/(6)"; op tip 1 fara furnizor -> "⚠ fara furnizor". Fara schimbare de mapare (era corecta); gard existent test_mapare_tip_cod pineaza tip 4 exclus din output.

## 18.08.2026 — Mis-clasificare: tip 4 cu cod TVA furnizor -> indiciu "poate e serviciu IC (tip 5)"

**Decizie.** O operatiune D301 tip 4 (art.307 alin.(3)(5)(6), exclusa din D390) care are COD TVA furnizor completat e SUSPECTA de mis-clasificare: codul de TVA exclude alin.(6) (furnizori neinregistrati), lasand gaz/energie (alin.3/5) SAU un SERVICIU intracomunitar (alin.2) pus GRESIT ca tip 4 - care ar trebui tip 5 ca sa apara in D390 (cod S). lista intoarce d390_posibil_serviciu = (tip==4 AND partener_cod != ''); grila D301 arata indiciu SOFT: "⚠ daca e serviciu intracomunitar, foloseste tip 5 (D390 cod S)".

**Temei.** Regula 4 (nu tace pe un posibil gol de conformitate) + CF art.307 alin.(2) (servicii IC = tip 5). Indiciu SOFT, nu blocaj: nu e certitudine (gazul/energia alin.3/5 pot avea si ele furnizor inregistrat) -> avertizeaza, nu impune. Astfel un serviciu IC ratacit pe tip 4 (deci absent din D390) e semnalat contabilului.

**Proba.** lista pe tenant_006: tip 4 cu cod -> posibil_serviciu True; tip 4 fara cod -> False; tip 5 -> False. Gard test_d390_posibil_serviciu_semnaleaza_tip4_cu_cod (mutatie: fara tip==4 -> tip 5 semnalat -> pica). 25 passed regresie.

## 18.08.2026 — Fals-pozitiv benign: confirmarea "nu e serviciu IC" stinge indiciul tip 4

**Decizie.** Indiciul de mis-clasificare (tip 4 cu cod TVA furnizor -> "poate e serviciu IC, foloseste tip 5") are un fals-pozitiv benign: gaz/energie/bunuri (art.307 alin.3/5) de la un furnizor INregistrat au si ele cod TVA, deci primesc indiciul desi sunt legitim tip 4. Rezolvare: contabilul apasa "confirma (nu e serviciu)" -> d390_confirmat_local=true -> indiciul se stinge pentru acea operatiune. Reversibil ("anuleaza"). Coloana noua d301_operatiuni.d390_confirmat_local (migrare_d301_confirmat, 19/19 scheme); ruta PUT /d301-operatiuni/{id}/confirma-local; lista: d390_posibil_serviciu = (tip==4 AND cod AND NOT confirmat).

**Temei.** Regula 4 (indiciu, nu blocaj; contabilul decide). Nu se poate distinge din date serviciul de gaz/energie (ambele cu cod TVA) -> confirmarea manuala e singura cale corecta, fara a ascunde tacit un posibil gol de conformitate.

**Proba.** lista pe tenant_006: op tip 4 cu cod -> posibil_serviciu True; confirma_local(True) -> False; confirma_local(False) -> True (reversibil). Gard test_confirma_local_stinge_indiciul_reversibil (mutatie: lista ignora confirmarea -> ramane True -> pica). Migrare verificata test_audit_schema. 37 passed regresie.

## 18.08.2026 — Confirmarea "nu e serviciu" persista per-furnizor (nu re-confirmi lunar)

**Decizie.** Un furnizor (tara+cod) confirmat "local" pe ORICE operatiune tip 4 (orice luna) stinge indiciul de mis-clasificare si pentru VIITOARELE operatiuni de la ACELASI furnizor - contabilul nu re-confirma lunar acelasi furnizor de gaz/energie. Derivat din confirmarile per-operatiune existente (SELECT DISTINCT tara,cod WHERE d390_confirmat_local=true), FARA tabel separat. Operatiunea confirmata direct arata "✓ confirmat local [anuleaza]"; cea mostenita arata "✓ furnizor confirmat local" (flag d390_furnizor_confirmat, nu d390_confirmat_local).

**Temei.** Inchide §5 al raportului anterior (confirmarea era per-operatiune). Un furnizor de gaz/energie are natura consecventa -> confirmarea lui o data se aplica tuturor operatiunilor lui. Nu ascunde datele (op ramane, marcata).

**Proba.** Doua op tip 4 acelasi furnizor DE/777, luni diferite (iun/iul): initial ambele posibil_serviciu=True; dupa confirma iun -> iun confirmat_local=True, iul posibil_serviciu=False + furnizor_confirmat=True (mostenit). Gard test_confirmare_per_furnizor_persista_intre_luni (mutatie: fara mostenire -> iul ramane semnalat -> pica). 25 passed.

## 18.08.2026 — a11y contrast pe grila D301: .btn-link + summary (axe pe ecranul atins, §5)

**Decizie.** axe-core rulat pe grila D301 (modificata repetat: campuri furnizor, indicii, butoane confirma/anuleaza) a gasit 2 perechi contrast sub AA: `.btn-link` #3d8fd6 (3.44 pe alb, 2.93 pe panoul #e9edf3) - butoanele sterge/confirma/anuleaza, app-wide; `.dec-xml summary` var(--albastru) #347ab8 (3.86 pe #e9edf3). Reparate la #2f6fa6 (4.53 pe #e9edf3, 5.32 pe alb). Inchide "RAMAS"-ul notat la DS v2.42 (.btn-link inca #3d8fd6 literal).

**Temei.** WCAG 2.1 AA 1.4.3 (4.5:1). Rule 14 (axe pe ecranul atins). Tinta de atingere a butoanelor-link (18px inaltime) = excepatia inline WCAG 2.5.8 (in randul de text al operatiunii) -> acceptata, notata.

**Proba.** axe pe grila D301: contrast 8 -> 0 (butoane-link + summary). Gard test_btn_link_contrast_pe_alb_si_panou + test_dec_xml_summary_contrast_pe_panou (recalcul din sursa >= 4.5), mutatie-probat (#2f6fa6->#3d8fd6 -> pica). Ramas: axe "region" (landmark) 26 noduri (front separat); tinta 18px inline.
