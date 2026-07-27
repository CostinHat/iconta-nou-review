# iConta — REGISTRU DE DECIZII

**De ce am facut asa.** Pentru CE s-a facut si CAND -> ISTORIC.md. Pentru ce urmeaza -> DE_FACUT.md.
Pentru norma UI -> DESIGN_SYSTEM.md. Pentru cod -> git.

## 27.07.2026 — D406 (SAF-T) NU e depunabil: gap cunoscut

Verificat la sursa (git + ANAF). In D406 periodic, SourceDocuments (SalesInvoices/PurchaseInvoices) e OBLIGATORIU la nivel de linie de factura (InvoiceLine cu AccountID + TaxInformation). Generatorul nostru (core/d406.py) emite, de la snapshot-ul initial (cbf24ce), o SINGURA linie sintetica per factura (cont 707/371, cantitate 1, pret = net total, descriere = numele partenerului), NU liniile reale din `factura_linii` (n. atins niciodata); Payments = gol.

Proba DUK din IULIE (15-16.07, nu iunie) a fost pe STRUCTURA: 15.07 validatorul accepta "orice gunoi" (namespace), apoi "36 erori -> 1", apoi 16.07 "VALID pe date reale + profil minim izolat — 5 discrepante structurale". DUK verifica FORMA, nu completitudinea continutului -> un fisier cu facturi sintetice trece validarea dar e INCOMPLET fata de cerinta ANAF.

CONSECINTE (27.07): afirmatia PERMISE "D100-D406 pe DUK" era inselatoare pentru D406 -> mutata pe INTERZISE; F035/F036/F037 -> PARTIAL. Generatorul NU se repara acum (sesiune separata). REPARATIA presupune: SalesInvoices/PurchaseInvoices cu liniile REALE pe produs (din factura_linii: cod, cantitate, pret unitar, AccountID + TaxInformation pe fiecare linie) + sectiunea Payments; apoi re-validare DUK pe CONTINUT real.

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
(obligație lunară fixă) — contrar instr. completare D390 (anexa OPANAF 705/2020; principiu identic OPANAF
394/2017 pct.1.2 la D394): D390 se depune NUMAI pentru lunile în care ia naștere exigibilitatea operațiunilor IC.
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
TEMEI: D390 se depune pe exigibilitatea operatiunilor IN LUNA (instr. completare D390, anexa OPANAF 394/2017
pct.1.2). Bifa de profil e un indicator, nu adevarul lunar; cand contrazice faptul, faptul castiga si divergenta
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
  .camp-ajutor cu temeiul (instr. D390, anexa OPANAF 394/2017 pct.1.2).
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
