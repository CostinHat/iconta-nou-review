## 16.09.2026, partea a treia — **aplicația compară, în sfârșit, amortizarea pe care o declară cu cea pe care a înregistrat-o**

**Pentru un contabil: nu se schimbă nimic din ce vezi azi, dar aplicația începe să-ți spună ceva ce
până acum nu putea.** Amortizarea unui mijloc fix se calculează în două locuri: în fișa activului
(de unde pleacă raportarea SAF-T către ANAF) și în nota lunară care intră în contabilitate. Până azi
nimic nu verifica dacă cele două spun același lucru.

**Acum verifică — și prima rulare a găsit trei nepotriviri pe firmele existente**, dintre care una
mare: o firmă la care fișele activelor spun 3.500 lei amortizare strânsă, iar contul din
contabilitate are 2.600. Cauza obișnuită e simplă și reparabilă: nota lunară de amortizare n-a fost
generată pe una sau mai multe luni. Aplicația o spune acum, cu ambele cifre, și îți zice ce să faci.

**Ce NU face, deliberat: nu blochează nimic.** Constatarea se vede în supervizor și atât. Dacă cere
sau nu o confirmare înainte de depunere e o decizie a lui Costin, pe care n-o iau eu — și până o dă,
constatarea n-are niciun efect asupra depunerii.

**Când refuză să acuze.** Dacă există note încă în ciornă pe contul de amortizare, aplicația spune
*„nu mă pronunț încă"*, nu *„e greșit": diferența se poate închide chiar la validarea lor. La fel
dacă nu poate calcula amortizarea unui activ (metodă nepermisă de lege pe categoria lui) — atunci
propria ei cifră e incompletă, și n-are dreptul să acuze contabilitatea pentru asta.

**Ce a ieșit la iveală construind, și e despre unealta mea, nu despre aplicație:** prima formă a
comparației **tăcea** exact în cazul în care nu putea citi fișele — adică fix când ar fi trebuit să
strige. A prins-o propria ei probă, înainte de orice rulare pe date reale.

*Restanța închisă: R191. Restanță redeschisă: R115 (tăria constatării noi e a lui Costin). R192
rămâne deschisă: confruntarea există, decizia de produs nu.*

## 16.09.2026, partea a doua — **reevaluarea unei imobilizări ajunge, în sfârșit, și în declarație**

**Pentru un contabil: da, s-a schimbat ceva.** Până azi, când reevaluai un mijloc fix, aplicația
scria corect nota contabilă — dar **fișa activului rămânea pe valoarea veche**. Consecința pe care
n-o vedea nimeni: SAF-T-ul anual declara către ANAF **costul vechi**, iar amortizarea lunilor
următoare se calcula tot pe el. Două evidențe despre același utilaj, și nici una nu știa de cealaltă.

**Acum:** reevaluarea se consemnează ca propunere (notă ciornă, ca înainte), iar în momentul în care
**validezi nota**, fișa activului urcă la valoarea reevaluată — și declarația o declară. Măsurat pe
un activ de 3.000 lei reevaluat la 3.500: după ciornă declarația spune tot 3.000 (corect — nimic n-a
fost aprobat încă), după validare spune 3.500.

**Și ceva ce nu se vedea din cerință.** Amortizarea nu continuă pur și simplu pe valoarea nouă: la
reevaluare, amortizarea strânsă până atunci se **șterge** din valoarea activului (așa cere norma
contabilă), deci de la data aceea utilajul se amortizează de la zero, pe valoarea nouă, pe **durata
rămasă**. Dacă am fi urcat doar cifra din fișă, aplicația ar fi socotit amortizare care nu s-a
înregistrat niciodată — o greșeală mai greu de găsit decât cea reparată. Dacă durata normală s-a
epuizat deja, aplicația **refuză** și spune de ce: durata nouă se ia din raportul evaluatorului, nu
o poate inventa programul.

**Ce s-a întrebat pe validatorul oficial.** Un câmp din SAF-T (`AppreciationForPeriod`) era zero de
când există generatorul, iar acum poartă creșterea reală. Validatorul ANAF a fost rulat pe fișierul
nou: **valid**.

**Ce a ieșit la iveală reparând, și rămâne deschis:** cifra pe care nota o șterge din amortizare se
calculează din **motorul de amortizare**, nu din ce s-a înregistrat efectiv. Dacă reevaluezi înainte
de a genera amortizarea lunii, cele două nu coincid. E consemnat ca **R192** și se închide împreună
cu R191 — confruntarea dintre amortizarea declarată și cea înregistrată, care e chiar lucrarea
următoare.

*Restanța închisă: R59, deschisă pe 26.08.2026. Restanță deschisă: R192.*

## 16.09.2026 — **etapa 2 se închide; trei lucruri care schimbă ce vede contabilul, dintre care unul bloca declarația de tot**

**Pentru un contabil: da, azi s-a schimbat ceva, în trei locuri.** Nu e o zi de întărire.

**MIJLOACELE FIXE NU PUTEAU IEȘI DELOC ÎN SAF-T, de două zile.** Ruta care scoate lista de mijloace
fixe pentru D406 răspundea cu eroare la **orice** cerere — nu la una anume, la toate. Cine încerca să
genereze SAF-T-ul cu mijloace fixe nu primea nici fișier, nici un motiv pe care să-l poată citi.
Cauza, în cod: numele coloanelor se citeau **înainte** de a se face interogarea, deci veneau de la
interogarea dinainte sau lipseau cu totul. Reparat, și păzit de-acum: o gardă nouă cade dacă cineva
mai scrie vreodată cele două în ordinea greșită. *Defectul stătea de două zile și nu-l semnalase
nimeni — nu fiindcă nu se folosea, ci fiindcă eroarea era de tipul care nu ajunge la un om.*

**O ACHIZIȚIE INTRACOMUNITARĂ DE SERVICII AJUNGEA PE RÂNDUL BUNURILOR.** În decont, serviciile primite
din UE se declară la rândul 7, bunurile la rândul 5 — două rânduri diferite, cu aceeași sumă
posibilă. Aplicația întreba omul „bunuri sau servicii?" la introducere, **și apoi uita răspunsul**:
nu-l scria nicăieri, iar la generarea decontului totul cădea pe rândul bunurilor. Acum răspunsul se
scrie **pe factură**, ca o coloană a ei, și rămâne înghețat acolo: o factură emisă azi va spune
peste doi ani același lucru, indiferent ce s-a mai schimbat în fișe. *Alegerea a fost a lui Costin, și
motivul ei e mecanic: singura altă sursă posibilă — reclasificarea — ține minte perechea
partener-lună, deci n-ar fi putut despărți două operațiuni ale aceluiași partener din aceeași lună.*

**O VÂNZARE INTRACOMUNITARĂ NU PRODUCEA NICIO FACTURĂ.** Se înregistra ca operațiune, dar nu lăsa
niciun rând în facturi — iar fără rând în facturi nu ajungea nici în decont (rândurile 1 și 3), nici
în declarația 390. Practic: livrarea exista în aplicație și **lipsea din amândouă declarațiile**. Acum
emite factură, ca orice livrare, și s-a probat cap-coadă că ajunge în amândouă.

**Cât de mult s-a schimbat pe portofoliul viu:** deocamdată **nimic de recalculat**, fiindcă nicio
firmă din portofoliu n-are încă o achiziție IC de servicii sau o vânzare IC înregistrată pe calea
asta. Ca și ieri, defectele erau reale în cod și neexercitate în producție. *Diferența e că azi două
dintre ele ar fi produs o declarație greșită, nu una imposibil de generat — iar o declarație greșită
pleacă la ANAF fără să se plângă nimeni.*

**Restul zilei: etapa 2 a campaniei s-a închis.** Cele 29 de unități rămase — locurile prin care o
valoare intră în aplicație și ajunge într-o declarație — sunt acum probate una câte una, pe lanțul
întreg: valoarea intră, se înregistrează, ajunge în rândul corect al declarației cu suma corectă, iar
declarația se generează și trece validatorul oficial. **31 de lanțuri, 29 verzi.** Cele două roșii
n-au fost greșeli ale probei: erau chiar defectele de mai sus.

**Ce a mai ieșit la iveală ieri seară, și se scrie aici fiindcă ziua de ieri s-a consemnat la prânz:**
o **proformă** făcea decontul de TVA imposibil de generat, fiindcă a doua cale de verificare o
număra · o **achiziție intracomunitară** se scria ca fiind din România, deci lipsea din decont · iar
**două ortografii ale aceluiași partener** (cu și fără diacritice) fac declarația 394 de nedepus, și
nimic nu spunea asta înainte de a o trimite. Toate trei, reparate.

**Un lucru pe care l-am aflat greșind, și e de folos oricui atinge zona:** am lărgit interogarea ca să
aducă noua coloană, dar am uitat locul de dedesubt care **enumeră** câmpurile facturii — coloana
venea din bază și se pierdea o linie mai jos, tăcut, iar declarația arăta exact ca înainte. *Un
SELECT lărgit nu e o citire lărgită.* Și, tot azi: proba mea a citit greșit fișierul XML de cinci ori
la rând, iar a patra oară **a suprascris datele reale ale unui asociat** — refăcute din artefactul
probei dinainte. De-aceea fiecare probă are acum două lucruri pe care nu le avea: o verificare că
n-a măsurat în gol, și o desfacere care readuce starea de unde a plecat.

**Ce urmează nu se mai alege.** Costin a numit patru lucrări, în ordine: reevaluarea care nu ajunge la
registrul de amortizare · amortizarea calculată de două ori din surse diferite, fără nimic care să
confrunte cifrele · cele opt locuri prin care se scriu date de declarație fără nicio probă · și cele
opt trimiteri la validatorul oficial care nu se regăsesc în el. După ele nu se deschide nicio temă
nouă.

## 15.09.2026 — **planul E se închide; și, pentru prima dată în etapa asta, se schimbă o cifră pe care o vede contabilul**

**Pentru un contabil: da, azi s-a schimbat ceva** — și merită citit, fiindcă zilele dinainte au fost
toate „nimic vizibil".

**O PROFORMĂ NU MAI INTRĂ ÎN D300.** Până azi, o proformă emisă era numărată ca livrare taxabilă:
măsurat pe o firmă cu o singură operațiune în lună, o proformă de 500 + 105 lei dădea `R9_1=500`,
`R9_2=105`, TVA de plată 105. Iar dacă proforma se transforma apoi în factură, **aceeași operațiune
economică se declara de două ori**, în două luni. Cauza, în cod: interogarea principală a lui D300
filtra pe dată și pe status, dar niciodată pe **tipul documentului** — iar proforma primește un status
declarabil. Tiparul corect exista deja alături: D394 excludea proformele de mult. Acum regula trăiește
într-un singur loc (`nomenclator_status_factura.clauza_tip_document`), iar D300 o cere pe toate cele
patru drumuri ale lui prin `facturi`.

**PARTENERUL DIN D394 SE CITEȘTE DE PE FACTURĂ**, nu din fișa clientului. Până azi, o corectură de CUI
în fișa unui client schimba partenerul dintr-un D394 **regenerat pentru o lună trecută**, deși
documentul emis atunci spunea altceva. Decizia lui Costin, scrisă în registru: *factura e autoritatea;
istoria se corectează prin storno și reemitere, nu prin editarea fișei.* Fișa rămâne rezervă — o
factură veche fără cod fiscal, emisă doar pe `client_id`, și-ar pierde altfel partenerul cu totul.

**Cât de mult s-a schimbat azi, măsurat înainte de a atinge codul:** **zero**. Portofoliul viu are 47
de documente, toate de tip `factura` — nicio proformă, niciun aviz —, și 28 de facturi emise, niciuna
cu CUI diferit de fișă. Defectele erau reale în cod și **neexercitate în producție**. *Dacă
portofoliul ar fi avut proforme, reparația ar fi rescris declarații deja depuse, și ar fi cerut alt
plan — de-aia cifra se măsoară înainte, nu se presupune după.*

**Restul zilei a fost întărire**, fără efect vizibil: planul E s-a închis pe toate etapele lui.
`MODULE_CU_SQL_FARA_STRAT` **78 → 0** (E2a: registrul straturilor s-a lărgit la *orice* modul cu SQL,
cu migrările într-o clasă de excludere numită, nu tăcută) · `REPOSITORY care își deschid conexiunea`
**32 → 0** (E2b: 39 de `commit`-uri scoase din depozite, actul cursului BNR mutat în modulul lui, două
programe CLI plecate în `scripts/`, opt acte etichetate greșit care și-au primit stratul adevărat) ·
cele patru datorii fiscale din registru, **scoase** (E4) · iar subsetul rutelor care scriu în cifre de
declarație, **49 → 8**, cu probe care merg până în rândul declarației, nu până la codul HTTP.

**Două lucruri pe care le-am aflat greșind, și se scriu ca atare.** La E4, „dependența" scrisă în plan
— *o firmă de probă cu profilul potrivit* — **nu exista**: lipseau datele, nu firma, iar ele încap în
câteva rânduri semănate în schema efemeră a probei. Se aștepta de o lună și jumătate după trei
insert-uri. Și, tot la E4: pragul „75 de caractere" din datorie era **vechi** — din 03.08 fiecare câmp
are limita lui oficială, iar garda care conta **sărea** exact peste declarațiile din datorie. *Un test
care sare nu e o verificare, e o intenție.*

**E5 n-a fost închis: a fost mutat.** „Motoarele fiscale se pot citi" nu are criteriu de ieșire —
lizibilitatea nu se termină, fiindcă motoarele se schimbă odată cu legea. A devenit **regula 9** din
`PLAN_LUCRU.md`: un motor deschis pentru altceva se lasă citibil la închidere. *Un pas care nu se
poate închide, ținut în plan ca pas, e o datorie care crește tăcut în dreptul unui plan altfel
terminat.*




## 14.09.2026, partea a doua — **E1: ritmul se numără o singură dată**

Pentru un contabil: nimic vizibil. Aceleași praguri, același refuz, același text. Ce s-a schimbat e
**unde** se numără.

**Ce era.** Trei limitatoare anti-abuz țineau starea în memoria procesului — `_reset_rate`,
`_cui_rate`, `_magic_rate` —, iar funcția care le folosea își scria premisa în docstring:
*„in-memory, **single worker**"*. Premisa murise la P6 valul 3, când unitatea a primit
`WEB_CONCURRENCY=2`. Consecința, măsurată: **prag efectiv dublu** pe trei rute publice (una dintre
ele apără cheia ANAF), contoare golite la fiecare publicare, și un dicționar care nu uita niciodată
un IP — cheiat pe un antet venit din cerere.

**Ce e acum.** `public.cereri_ritm`, cu tiparul scris la P6 pentru `login_esecuri`: un rând per
cerere admisă, fereastra în `WHERE`, ștergerea celor expirate la fiecare scriere, ridicare la bază
căzută. Peste tipar, un lucru nou: un **blocaj consultativ pe `(cheie, ip)`**. La login, două
inserări concurente sunt amândouă adevărate; la ritm, două cereri simultane ar fi putut trece
amândouă de prag. *Cursa nu s-a micșorat, s-a scos.*

**Cum se știe că ține.** Nu din citirea codului: din **două procese reale**. Unul epuizează pragul
pe `/public/magic-link`, celălalt — alt PID, altă memorie — primește `429` la a șasea. Forma
dinainte ar fi răspuns `200`, fiindcă al doilea proces pornea cu dicționarul gol.

**Ce a rămas deschis, și se scrie ca să nu pară închis:** rotația jurnalelor. Fișierul e scris și
verificat (`config/iconta-logrotate`, `logrotate --debug` fără nicio notă), dar instalarea în
`/etc/logrotate.d/` cere root — ca `WEB_CONCURRENCY=2` la P6. Până atunci, `uvicorn.log` crește în
continuare, iar constatarea D3 din audit rămâne DESCHISĂ.

## 14.09.2026 — **planul de întărire P0…P7 se închide formal**

Pentru un contabil: nimic. Nicio linie de cod de producție n-a fost atinsă azi — e o zi de
consemnare, nu de lucru.

**Ce s-a scris.** Cei opt pași P0…P7 sunt marcați `CLOSED_ACCEPTED`, fiecare cu commitul lui final,
într-un tabel la capătul lui `PLAN_HARDENING.md`. Lângă el stau două lucruri care fac diferența
între o închidere și o declarație: **poarta care a lăsat-o să treacă**, copiată din ieșirea
hook-ului (5840 de teste, ruff OK, verificator `TOTAL: 0`, arbore curat), și **cele șase restanțe
care rămân deschise**, fiecare cu cifra ei și cu motivul pentru care nu blochează.

*O închidere care n-ar numi ce rămâne ar fi o cifră flatantă — exact clasa pe care planul o
păzește de opt pași.* Niciuna dintre cele șase n-are lucrare pornită, și niciuna nu contrazice
criteriul pasului ei: `_raspuns` e serializarea mutată la P5 · `D3`=1 e stratul HTTP însuși ·
cele 7 rute GRI sunt clichet, iar GRI nu e verde · cele 6 căi C5 au verdict scris · R178 și R183
sunt proprietăți ale configurației, măsurate, nu regresii.

**Ce rămâne în vigoare:** gărzile. Criteriile celor opt pași nu sunt propoziții dintr-un raport, ci
probe care rulează la fiecare commit.

## 13.09.2026, partea a cincea — **P7 · valul use-case: 385 de corpuri de rută, și faza se ÎNCHIDE**

Pentru un contabil, a cincea oară azi: nu s-a schimbat nimic. Aceleași ecrane, aceleași declarații,
aceleași refuzuri — cuvânt cu cuvânt, și asta nu mai e o promisiune, e o confruntare.

### Ce s-a schimbat, sub capotă

**Cele 385 de corpuri de rută au plecat din `main.py`** în **27 de module `core/uc_*.py`**, împreună
cu **58 de helperi** și **12 nume de modul** pe care le cereau. `main.py`: **11714 → 6546** de linii.
Fiecare rută a rămas la locul ei, cu decoratorul, semnătura și docstringul — FastAPI validează pe
semnătură, deci contractul de intrare e literal același —, iar corpul a devenit o delegare.

Cifra care a ținut faza deschisă două valuri, **`RUTE_CARE_DESCHID_SINGURE_TRANZACTIA`**, a mers
**385 → 73 → 17 → 5 → 0**. Cu ea, **toate cele patru criterii canonice ale lui P7 sunt satisfăcute**,
și faza se închide.

### Ce a făcut posibilă mutarea: un vocabular de refuz

`HTTPException` nu poate trăi în use-case — al doilea criteriu canonic o interzice. Dar decizia care
produce refuzul se ia **înăuntrul tranzacției**, adică exact în codul care pleacă. S-a scris deci
`core/erori.py`: clase care numesc **condiția** (*inexistent*, *fără drept*, *conflict*, *date
invalide*…), iar traducerea condiție → cod HTTP e **o singură hartă**, în stratul HTTP.

**Ce face traducerea sigură e o măsurătoare, nu o speranță:** `HTTPException` **nu e prinsă
nicăieri** — zero `except HTTPException` în tot repo-ul —, deci înlocuirea ei nu poate schimba niciun
flux de control. La fel s-a măsurat că niciun obiect de răspuns nu se construiește înăuntrul unei
tranzacții.

### Ce NU a trecut granița

Obiectele de protocol. Un `Response`/`FileResponse` se construiește tot în înveliș, din valorile pe
care use-case-ul le întoarce (**15 rute**); un `UploadFile` se citește în înveliș și se pasează ca
`bytes` + nume (**12 rute**); gărzile de ritm care se uită la IP-ul cererii rămân deasupra, pe primul
rând (**2 rute**). *Un use-case care vorbește HTTP n-ar fi un use-case.*

Și un al treilea fel de graniță, care n-a fost evident: `_TENANT_TEMPLATE` și `_STATIC_DIR` nu sunt
constante — se **aleg la pornire**, în stratul HTTP. Mutate ca valori, use-case-ul ar fi rămas cu
`None` iar scriitorul cu copia lui: o legătură ruptă pe tăcute, care s-ar fi văzut abia în producție.
S-au mutat invers, și așa e și corect ca strat: **HTTP-ul configurează, use-case-ul consumă.**

### Dovada că nu s-a schimbat contractul

`core/test_p7_uc.py` ia `main.py` **de la commitul dinainte de val** (`git show 43fd2197:main.py`) și
confruntă, **funcție cu funcție**, mulțimile de perechi `(cod HTTP, mesaj)` pe care le ridică —
mesajul comparat ca **arbore**, nu ca text, fiindcă dedentarea schimbă sursa fără să schimbe
valoarea. Trece cu **o singură abatere declarată**, cu motivul scris în fișier: un input-guard
telegrafic (`"suma invalida"`) care a intrat în domeniul regulii G5 odată cu mutarea și și-a primit
constrângerea în mesaj.

*Fișierul acela era citat de două ori în cod înainte să existe — `core/erori.py` și `main.py` îl
numeau ca dovadă a parității. Trimiterea la ceva inexistent se semnalează; aici s-a semnalat
construind lucrul citat.*

### Ce a ieșit la iveală mutând, și e clasa zilei

**Întreaga mașinărie de gărzi doc↔cod era ancorată pe presupunerea că logica aplicației stă în
`main.py`.** Mutând-o, ~40 de gărzi au devenit deodată oarbe sau roșii — nu fiindcă s-ar fi stricat
codul, ci fiindcă se uitau unde nu mai e nimic. Fiecare a fost re-ancorată prin accesorul comun
(`core/scan_sql_efectiv.py`), fără să-și piardă semantica.

**Patru lucruri s-au pierdut tăcut, și fiecare a fost prins de alt instrument:** două gărzi
anti-spam (`_rate_limit_*`) lăsate pe dinafară de mutator · comentariile de pe linia decoratorului,
printre care cinci marcaje `[api_intern_v1]` pe care un instrument le citește ca declarație · și un
RE-EXPORT (`main.pastila_firma`) scos de curățenia automată de importuri, care a lăsat șase firme cu
`control_fiscal` în eroare. Toate patru erau lucruri pe care codul le spunea, iar valul le-a rescris
din ceva care nu le conținea. Fiecare și-a primit garda.

**Iar două scanere aveau `main.py` ca punct orb DECLARAT** (`scan_data_curenta`, `scan_constante`):
valul le-a închis gaura, iar clichetele lor au urcat — nu fiindcă s-a scris cod nou, ci fiindcă
**instrumentul vede mai mult**. Fiecare urcare e scrisă cu lista exactă a cazurilor nou-expuse, și
fiecare caz se regăsește, la aceeași formă, în `git show HEAD:main.py`.


## 13.09.2026, partea a patra — **P7 · valul D4: 215 instrucțiuni mutate, și faza tot nu se închide**

Pentru un contabil, a patra oară azi: nu s-a schimbat nimic. Aceleași ecrane, aceleași declarații,
aceleași cifre. Ce s-a schimbat e unde stă SQL-ul — și ce știm despre cât mai avem de făcut.

### Ce s-a schimbat, sub capotă

Cele **37 de module mixte** — cele care făceau două straturi deodată, de la `core/d223.py` cu o
instrucțiune la `core/control_incrucisat.py` cu 45 și `main.py` cu 38 în helperii de modul — și-au
dat cele **215 instrucțiuni SQL** la **37 de `core/repo_*.py`**. `D4` **37 → 0**.

Mutarea a fost făcută de un instrument, `scripts/p7_d4_separa.py`, nu cu mâna. Motivul e o
măsurătoare, nu o preferință: 215 poziții în 13 forme diferite de loc, iar modul de eșec al unei
mutări manuale — parametri schimbați de ordine, un `fetchone` devenit `fetchall`, un `%s` pierdut —
**nu se vede la citire**. Instrumentul mută expresii, nu text; ce nu poate rezolva mecanic
raportează și lasă neatins. **Rest: 0 din 215.**

**Dovada că s-a mutat, nu s-a rescris:** amprenta SQL a întregului cod de producție — **1050
instrucțiuni distincte, 1307 în total** — e identică înainte și după.

### Partea care merită citită: cifra care arăta bine

După val: `D1`=0, `D2`=0, `D4`=0, **`P7_ACTION_REQUIRED`=0**. Citită singură, cifra spune că faza s-a
terminat. **Nu s-a.** Textul canonic cere patru straturi, iar despre use-case spune că *deține
tranzacția (P4) și orchestrează*. Măsurat: **385 din 421 de rute își deschid singure tranzacția**,
doar **7** deleagă către un modul `USE_CASE`, iar use-case-uri declarate sunt **4**.

*Un `ACTION_REQUIRED=0` care nu acoperă un criteriu canonic nu e o stare, e o lipsă de detector.* Am
închis golul cu un instrument și o gardă, nu cu o propoziție în predare: `scripts/p7_criterii.py`
măsoară toate patru criteriile, iar `core/test_p7_criterii.py` ține clichetul celor 385 **și
interzice planului să declare P7 închisă peste el**.

### Ce a mai scos valul, și toate trei sunt aceeași clasă

1. **O justificare ancorată prin vecinătate nu se mută cu codul.** Trei `ON CONFLICT DO UPDATE` au
   trecut în depozit, iar `# upsert-ok:` a rămas în modulul vechi. Prins de `test_upsert_motivat` la
   prima rulare — de instrument, nu de mine.
2. **Instrumentul traseelor a tăcut din nou**, a doua oară în două valuri: 12 adnotări deodată.
   Reparat cu **perechea nominală** modul ↔ `repo_<același nume>`.
3. **Citările în plan s-au mutat iar** — 8 ancore. De data asta reparate cu un instrument,
   `scripts/reancoreaza_plan.py`, care a greșit el însuși de două ori înainte să meargă: cerea
   unicitatea fragmentului pe tot planul, și lua reperul din fișierul deja editat.

### Cifre

`D4` **37 → 0** · `P7_RAW_ITEMS` **38 → 1** · `P7_ACTION_REQUIRED` **37 → 0** · straturi declarate
**167** (96 `FISCAL_ENGINE` · 65 `REPOSITORY` · 4 `USE_CASE` · 2 `HTTP`). Criteriul rămas:
**385/421**. Poarta: **5795 verzi / 0 roșii** · 12 sărite · 14 xfail ·
verificator **TOTAL 0**.

**P7 RĂMÂNE DESCHISĂ.** *Zero pe toate detectoarele nu e zero pe fază.*
