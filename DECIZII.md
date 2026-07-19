# iConta — REGISTRU DE DECIZII

**De ce am facut asa.** Pentru CE s-a facut si CAND -> ISTORIC.md. Pentru ce urmeaza -> DE_FACUT.md.
Pentru norma UI -> DESIGN_SYSTEM.md. Pentru cod -> git.

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
