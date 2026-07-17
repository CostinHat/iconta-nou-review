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
