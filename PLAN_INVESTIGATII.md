# PLAN DE INVESTIGAȚII

**Versiunea 10.** Aliniat la `PLAN_ARHITECTURA.md` v14: **75 de interdicții**, 26 de principii, plus Partea 00 — ce face sistemul. P22 și P23 sunt în faza 1; **P24, P25, P26 intră în faza 7**, fiindcă cer decizii și construcție, nu măsurători.

**Planul de arhitectură nu se mai extinde.** Ce urmează e confruntarea.

---

## Afirmația care trebuie dovedită

> **Aplicația face contabilitate conformă.**

Are un înțeles precis, iar dovada e la fel de precisă: pentru o firmă și un exercițiu financiar, aplicația produce **exact setul de artefacte pe care legea îl cere**, iar fiecare **se validează**.

Nimic altceva nu dovedește asta. Nici numărul de teste, nici absența defectelor găsite, nici conformitatea cu regulile noastre de construcție.

**Restul investigației nu răspunde la întrebarea asta.** Cele 75 de interdicții măsoară cât de *fragil* e rezultatul. Sunt importante, dar sunt a doua întrebare.

---

## Ritmul de lucru

Fiecare tură: **observații pe runda precedentă** · **deciziile cerute, în cap** · **comanda pentru runda următoare**.

Rezultatul se scrie în `CONFORMITATE.md`, care intră în §11 al fiecărui raport. Planul stabilește ordinea și metoda; starea trăiește în registru.

**Investigăm înainte să reparăm.** Excepția: un defect care produce **efect greșit la un om acum — cifră, blocaj, sau afirmație falsă pe ecran** — se repară imediat. (Lărgită la 22.08.2026; vezi `PLAN_LUCRU.md`, „Restanțele".)

**Întâi se modifică planul, apoi se conformează codul.** Când investigația scoate o regulă nouă sau corectează una veche, ea intră în `PLAN_ARHITECTURA.md` mai întâi.

**Termen de final al investigației: [de fixat].** Fără dată, o investigație bine făcută se extinde la infinit și devine chiar bucla din care voiam să ieșim. La termen se decide cu ce s-a măsurat.

---

## Prioritatea, peste tot

1. **Ajunge în ceva depus la o autoritate** — problemă legală a clientului, pe care el nu o poate vedea;
2. **Ajunge la un om** — fluturaș, factură, adeverință;
3. **Rămâne înăuntru** — rapoarte, ecrane, evidență internă.

---

# FAZA 1 — SETUL COMPLET

**Singura fază care răspunde la afirmația de mai sus.** Nu se caută defecte. Se verifică o afirmație: iese setul, sau nu iese.

### 1a — Ce cere legea

Lista completă a artefactelor pe care o firmă trebuie să le poată produce pentru un exercițiu financiar. **Din lege, cu temei — nu din ce știe aplicația să facă.**

- **registrele obligatorii** — registrul-jurnal, registrul-inventar, cartea mare, și oricare altele impuse de regim;
- **situațiile financiare** — cu forma și termenele lor;
- **declarațiile fiscale** — toate cele datorate, după vectorul fiscal;
- **documentele justificative** — ce trebuie să existe și în ce formă;
- **evidențele speciale** — registrul de evidență fiscală, jurnalele de TVA, registrul de casă.

**Pe regimurile reale, nu pe trei alese arbitrar.** Prima operațiune din E1 e să afli câte sunt: micro/profit · plătitor/neplătitor de TVA · lunar/trimestrial · plus cele speciale — agricultori, turism cu marjă, second-hand, construcții, și oricare altele pe care aplicația le acoperă sau pretinde că le acoperă.

Pentru fiecare: ce module îl deservesc, și pe câte firme din matrice e exercitat efectiv.

Cele trei de mai jos sunt punctul de plecare, nu lista:

| Regim | De ce contează |
|---|---|
| micro, fără salariați | setul minim |
| micro, cu salariați | adaugă tot ce ține de salarizare |
| profit, plătitor de TVA lunar | setul maxim uzual |

Un regim pentru care aplicația are module dar nicio firmă exercitată e semnal: „există modulul" nu e „produce artefactul".

### 1b — Ce produce aplicația

Pentru fiecare artefact:

1. **Se produce azi?** Măsurat pe o firmă cu date reale. „Există ruta" nu e „produce artefactul".
2. **Se validează?** Cu instrumentul oficial, unde există. Cu structura cerută de lege, unde nu.
3. **Dacă nu — de ce, și a cui e răspunderea?** Aici e distincția care contează, și e P23:

| Cauza | A cui e |
|---|---|
| lipsesc date, **aplicația le-a cerut la timp** | a omului — nu e defect al aplicației |
| lipsesc date, **aplicația nu le-a cerut** | **a aplicației** — cea mai gravă formă |
| lipsesc date, **cerute prea târziu** — la generare, când nu mai pot fi obținute | a aplicației |
| artefactul nu se poate produce **indiferent de date** | a aplicației |

Un artefact care nu iese fiindcă lipsesc date pe care aplicația le-a cerut la timp **nu se numără ca defect**. Unul care nu iese fiindcă nimeni n-a cerut datele, se numără.

**Calibrare:** o firmă cu vectorul fiscal incomplet. Aplicația a cerut completarea la înregistrarea firmei, sau descoperă lipsa abia când se generează prima declarație?

### 1c — Se poate verifica ce iese?

**Interdicții:** 63, 64, 65, 66 — P22.

Un artefact care iese și se validează, dar pe care contabilul nu-l poate verifica, îl obligă să-l refacă în altă parte. Atunci produsul nu i-a economisit munca.

Pentru un eșantion de cifre — un net de pe fluturaș, o poziție din decont, un rând din D112:

1. **se poate vedea din ce se compune**, la cerere?
2. **se vede ce nu s-a aplicat și de ce** — o deducere neacordată, o facilitate pierdută, o scutire neaplicată?
3. **se vede ce s-a schimbat față de perioada anterioară**, cu motivul?
4. **temeiul ajunge pe ecran**, sau trăiește doar în cod?

**Calibrare:** netul unui salariat la salariul minim, în două luni consecutive care traversează 1 iulie 2026. Diferența vine din trei surse simultan — salariul minim, facilitatea, deducerea. Dacă aplicația nu poate explica diferența, punctul 3 nu e acoperit.

**Ce se măsoară la 64:** nu „câte explicații lipsesc", ci **câte elemente puteau interveni și n-au intervenit** — acela e numitorul. Pe un fluturaș obișnuit sunt cel puțin: facilitatea de la salariul minim, deducerea suplimentară pentru tineri, cea pentru copii școlarizați, scutirile sectoriale.

### 1d — Verdictul

Cinci liste, nu trei:

| listă | ce conține | e defect? |
|---|---|---|
| **1** | ies și se validează și se pot verifica pe ecran | nu |
| **2** | nu ies, fiindcă lipsesc date **cerute la timp** | nu — a omului |
| **3** | nu ies, fiindcă lipsesc date **necerute sau cerute prea târziu** | **da** |
| **4** | ies, dar nu se validează | **da** |
| **5** | ies și se validează, dar **nu se pot verifica pe ecran** | **da** |

**Criteriul de gata al aplicației:** listele 3, 4 și 5 goale, pe fiecare regim. Lista 2 poate avea conținut — ea măsoară ce n-a completat contabilul, nu ce n-a făcut aplicația.

Despicarea contează: fără ea, o firmă cu date incomplete face aplicația să pară defectă, iar una cu lipse necerute o face să pară completă.

**Ce ar dovedi că planul e greșit aici:** dacă lista din 1a conține artefacte pe care nimeni nu le cere în practică, sau dacă îi lipsesc lucruri pe care o inspecție le solicită de rutină. Iar la 1c: dacă explicațiile cerute de P22 se dovedesc lucruri pe care un contabil nu le citește niciodată, principiul e prea larg și se restrânge.

---

# FAZA 2 — TEMEIURILE

**Interdicții:** 49–59 (grupul 0) plus **60–62** (P21 — legătura de la normă la implementare).

**De ce imediat după setul complet, și înaintea a orice altceva:** o valoare corect așezată în registru, care se sprijină pe un articol abrogat, pe un citat care n-o conține, sau pe un text neînțeles, e greșită oricât de bine ar fi structurat registrul. Temeiurile sunt fundația fundației.

### Ce se măsoară

| # | Interdicție |
|---|---|
| 49 | articole folosite fără dată de verificare a vigorii |
| 50 | valori sprijinite pe articole abrogate sau modificate, fără succesor citat |
| 51 | reguli scrise din memorie, cu actul lipsă din corpus |
| 52 | acte din corpus al căror text s-a modificat după aducere |
| 53 | citate verbatim care nu conțin valoarea justificată |
| 54 | articole cu verificarea vigorii expirată față de pragul lor |
| 55 | articole fără categorie de reverificare atribuită |
| 56 | reguli scrise când textul a fost citit dar nu înțeles, fără cerere specifică |
| 57 | valori fără temei, intrate fără declarația „am căutat și nu am găsit" |
| 58 | surse de nivel inferior care contrazic una superioară, fără decizie |
| 59 | verificări de vigoare făcute pe act, nu pe articolul folosit |
| 60 | reguli, formule sau structuri care implementează o normă, fără articolul asociat |
| 61 | articole din corpus fără lista dependenților, generabilă la cerere |
| 62 | modificări de articol aplicate fără parcurgerea listei dependenților |

### Ce e măsurabil și ce nu

**53 e cel mai măsurabil din tot planul.** Citatul verbatim conține valoarea justificată, sau nu. Se verifică mecanic, fără judecată.

**49, 52, 55** sunt măsurabile după ce câmpurile există. Prima operațiune e inventarul: câte acte sunt în corpus, de când, cu ce se folosesc.

**54 nu mai e aici, iar textul de dinainte era greșit** (corectat 23.08.2026): spunea că *„azi nu există câmpurile"*. **Pragul există din 01.08.2026** — `CONFIRMARE_COTE_PRAG_LUNI`, implicit 6 luni, în `core/expirare_cote.py`, rulat **lunar din cron** ca RAPORT, nu ca blocaj. Măsurat: **0 confirmări expirate**, cea mai veche având 16 zile. Planul a fost scris înaintea muncii care l-a schimbat.

**50 și 59** cer verificarea vigorii la sursă externă, pe articol. Rămâne cea mai mare muncă din fază **ca volum**, dar nu mai e blocată: portalul e accesibil (antet de browser + formularul lui de căutare), iar `scripts/vigoare_articol.py` citește starea articolului din forma consolidată la zi. Ce rămâne de făcut e să treacă prin toate articolele, nu să se găsească o cale la ele.

**51, 56, 57** nu sunt măsurabile retroactiv. O regulă scrisă din memorie sau dintr-un text neînțeles nu se distinge de una scrisă corect. Sunt **reguli de proces**, aplicabile de acum înainte, iar starea lor e NEMĂSURABILĂ RETROACTIV, cu motivul scris.

**58** e măsurabilă doar unde ambele surse sunt în corpus.

**60 e cea mai mare din fază, și cea mai valoroasă.** Azi doar valorile poartă temei; formulele, condițiile de eligibilitate, structurile de declarație, nomenclatoarele, termenele și regulile de validare nu poartă nimic. Măsurătoarea nu e „câte au temei", ci **câte elemente care implementează o normă există, și câte dintre ele îl poartă**. Numitorul e greu — de aceea se calibrează pe cazuri unde legătura e cunoscută: formula deducerii personale ↔ art. 77 alin. (4); podeaua part-time ↔ art. 146 alin. (5^6) și art. 168 alin. (6^1); nomenclatorul codurilor de indemnizație ↔ ordinul care îl aprobă.

**61 — textul de dinainte spunea *„se măsoară trivial azi: zero, legătura inversă nu există deloc"*, și nu mai e adevărat** (corectat 23.08.2026). Legătura inversă **se poate genera pentru 16 din cele 17 articole** citate de registrul de cote, iar unealta e construită: `core/dependenti_act.py`. Ce a făcut-o posibilă e o reparație din **aceeași zi** — R17, cheia grafului: pe graful conflat, unealta ar fi dat răspunsuri scurte cu încredere, mai rău decât să lipsească. Ce rămâne e domeniul: 17 articole, față de 339 de acte în corpus.

**62 e nemăsurabilă retroactiv.** E regulă de proces. Dar are un test: se ia o modificare legislativă recentă și se întreabă *ce ar fi trebuit schimbat*. Dacă răspunsul cere căutare, legătura lipsește.


### REGULA, adăugată 23.08.2026 (Costin): fiecare „se măsoară trivial" se verifică înainte de a fi transcris

Planul a fost scris **înaintea muncii care l-a schimbat**. În aceeași fază, două afirmații ale lui s-au
dovedit false în aceeași zi — **54** („azi nu există câmpurile": pragul exista de trei săptămâni) și
**61** („trivial: zero": era 16 din 17, deblocat de o reparație făcută cu ore înainte).

Niciuna nu e un defect al planului. Amândouă sunt afirmații care erau adevărate când s-au scris și au
încetat să fie, fără ca nimic să se aprindă — **doc-stătut, la nivel de plan**.

**Deci:** o propoziție din plan care spune *„se măsoară trivial"*, *„nu există"*, *„e zero"* sau
*„azi nu se poate" * **se verifică înainte de a fi transcrisă într-un registru sau într-un raport.**
Costul verificării e mic — o comandă — iar costul netransciderii e o cifră falsă care intră în lanț și
se propagă mai departe cu autoritatea planului.

Aceeași disciplină pe care o cere **interdicția 76** pentru instrumente: nu întrebi *dacă* a fost
adevărat, ci *dacă mai e*.

### Calibrare obligatorie

Din cazurile cunoscute — dacă scanul nu le găsește, e rupt:

- **OPANAF 394/2017**, citat în nouă locuri, abrogat de OPANAF 705/2020 → interdicția 50;
- **HG 685/1999**, abrogat de HG 773/2019 → 50;
- **art. LXX din OUG 156/2024**, abrogat de OUG 29/2026, într-un act rămas în vigoare → 59;
- **facilitatea de 300 lei** atribuită unui act care n-o conținea → 53;
- **cota de dividende** atribuită Codului fiscal în loc de ordonanța care o fixase → 53;
- **pragul mijloacelor fixe**, la fel → 53;
- **podeaua part-time**, unde structura publicată contrazice legea și s-a ales în cod → 58;
- **cele nouă locuri care citau OPANAF 394/2017** → 60 și 61: au fost găsite abia când cineva a căutat anume. Cu legătura inversă, întrebarea „ce depinde de 394/2017?" ar fi avut răspuns imediat.

### Ce ar dovedi că planul e greșit aici

Dacă pragurile de reverificare din plan se dovedesc imposibil de respectat, nu se completează formal — se schimbă pragurile, prin decizie, cu motivul scris. **Motivul „nu avem acces la sursa oficială" a căzut pe 22.08.2026** și nu se mai poate invoca: portalul răspunde, iar instrumentul există.

---

# FAZA 3 — UNDE STĂM CU FRAGILITATEA

### 3a — Inventarul retrospectiv

Campaniile din iulie–august au măsurat interdicții care nu erau încă formulate. Cifrele există în registre; în `CONFORMITATE.md` scrie NEÎNCEPUTĂ.

Cel puțin: **6** (`test_get_fara_scriere`, 2 din 168) · **7** (statul append-only) · **8** (`UNIQUE` ridicat) · **9, 10** (afirmațiile, 120 → 17) · **11, 12** (`test_cale_a_doua`, 13 căi) · **13** (nume interne 4 → 0) · **14** (25 din 78) · **20** (perimetrul) · **26** (`migrare.js`) · **34** (`perioada_confirmata`, un domeniu).

**La transfer:** o măsurătoare veche fără calibrare devine PARȚIAL, nu MĂSURATĂ. Ce nu se reconstituie onest rămâne NEÎNCEPUTĂ.

**De reparat odată cu transferul:** câmpul „unde ajunge efectul" a fost completat pe grupuri, nu per interdicție. Cel puțin trei sunt greșite.

**De adăugat:** interdicțiile 49–75 n-au secțiuni în `CONFORMITATE.md` — registrul a fost scris când erau 48. **FĂCUT (23.08.2026)**: registrul are azi **76** de secțiuni.

**STARE, verificată pe 23.08.2026:** transferul **nu a început**. Toate cele douăsprezece numite mai sus — 6, 7, 8, 9, 10, 11, 12, 13, 14, 20, 26, 34 — scriu încă `NEÎNCEPUTĂ` în `CONFORMITATE.md`. **Zero transferate.**

### 3b — Triajul

**ORDINEA, corectată 23.08.2026: 3a intră ÎNAINTEA lui 3b, și nu s-a respectat.** Prima tură de triaj a pornit peste toate 76, dintre care 50 scriu NEÎNCEPUTĂ — iar cel puțin douăsprezece dintre ele **au cifre** în alte registre. Un triaj pe poziții nemăsurate ordonează după presupuneri, nu după stare. Ce **nu** cade din prima tură: pragul 3 e ordonat pe **artefacte** (faza 1), nu pe interdicții, deci ordinea lui rămâne; ce cade e pretenția că triajul acoperă toate 76.

O trecere **superficială** peste toate 75. Nu se măsoară; se răspunde la trei întrebări:

1. **Există o instanță vie** care produce azi o cifră greșită, un verdict fals, sau o afirmație care nu se poate dovedi?
2. **Cât costă măsurătoarea completă?** Sub 1h · 1–4h · peste 4h · cere instrument nou.
3. **Ce criteriu de acceptare i se potrivește?**

Triajul nu produce cifre. Produce **ordinea fazei 5** și estimarea totală.

### 3c — Ce leagă fazele

Pentru fiecare artefact din faza 1 care **nu iese sau nu se validează**: care interdicții stau în calea lui? Alea urcă automat la vârf, indiferent ce spune triajul.

---

# FAZA 4 — INSTRUMENTELE

**Interdicții:** 18, 19.

Dacă instrumentele mint, toate măsurătorile de după moștenesc minciuna. Într-o zi s-au găsit patru gărzi care își luau dovada din proză, trei care raportau favorabil pe zero rânduri, una cu un octet invizibil în regex care nu putea deveni verde niciodată, și o a cincea apărută chiar în timp ce se construia registrul pentru clasa asta — citirea cu `\s*` care traversa linia nouă.

**Ce se măsoară, pentru fiecare gardă:** își ia dovada din proză? · a rulat pe date nenule? · mutația care o probează e reproductibilă azi? · scrisă înainte sau după fixul pe care îl păzește?

**Calibrare, toate cinci din istoric.**

**Datorie moștenită:** orice gardă care parsează `.md` are gaura citirii peste marginea rândului. De scanat toate.

**Ce ar dovedi că planul e greșit aici:** dacă majoritatea gărzilor sunt scrise după fix și totuși prind regresii reale, atunci regula „gardă înainte de reparație" e mai slabă decât credem.

---

# FAZA 5 — CE ARDE

**Compoziția se stabilește la 3b și 3c.** Intră interdicțiile care blochează un artefact din faza 1, apoi cele cu instanță vie, în ordinea celor trei trepte de prioritate.

Ce anticipez, pe baza a ce se știe deja — dacă triajul contrazice, triajul câștigă:

| Probabil în față | De ce |
|---|---|
| 16, 28 | codurile de boală blochează azi depunerea unui D112 legal — instanță vie confirmată |
| 34, 38 | o evidență modificabilă retroactiv și o urmă editabilă nu se pot apăra |
| 37 | fără autor identificat, răspunderea nu se poate stabili |
| 2, 14 | aceeași cauză: defaultul din `cota()`; face recalculul unei luni trecute nereproductibil |
| 24, 25 | datele unei firme la altcineva nu se repară cu scuze |

**Ce ar dovedi că planul e greșit aici:** o interdicție cu risc juridic mare, cu zero instanțe și fără istoric — semn că a fost derivată din teamă. Se coboară, nu se bifează.

---

# FAZA 6 — RESTUL, CARTOGRAFIAT

Grupat pe instrument comun, nu pe temă.

**Grupul JavaScript** — 4, 5, 13, 15, 26, 27, 29, 30, 31, plus partea JS din 16 și 28. Un singur instrument, unsprezece interdicții. Din motivul ăsta 16 rămâne PARȚIAL până aici: `CM_CODURI` din `flux_concediu.js` e unul dintre cele patru straturi ale codurilor de boală, iar scanul actual nu-l vede.

**Grupul documente** — 6, 7, 8, 35, 36, plus ce n-a intrat în faza 5. Se măsoară **la nivel de schemă, nu de rută**.

**Grupul lanț** — 32, 33. Cel mai scump, și legat direct de faza 1: un artefact care iese dar nu se poate desface până la document e conform ca formă și indefensabil ca fond. Se face după 60–62, fiindcă e celălalt capăt al aceleiași idei: P14 leagă cifra de document, P21 leagă regula de normă.

**Grupul exterior** — 43, 44, 45, 46.

**Grupul retenție** — 39, 40, 41, 42. Cere decizii de conținut mai mult decât măsurători.

**Rămase** — 1, 3, 17, 21, 22, 23, 47, 48 (cele din registru, deja măsurate parțial, plus cele două neatinse).

**Ce ar dovedi că planul e greșit aici:** un grup întreg curat. Întrebarea nu e „mergem mai departe", ci „instrumentul chiar vedea ceva?".

---

# FAZA 7 — CE NU SE MĂSOARĂ, SE CONSTRUIEȘTE

**Interdicții:** 70–75 — P24, P25, P26.

Trei principii care nu produc măsurători utile, fiindcă răspunsul e cunoscut dinainte: interpretările n-au fost revizuite ca listă niciodată; restaurarea din copii nu s-a probat; exportul cu lanțul păstrat nu există.

Ce se măsoară e **cât costă construirea**, nu câte instanțe sunt.

**70 — revizuirea.** Se numără câte decizii de interpretare ajung într-o cifră depusă. Alea sunt lista care se recitește deliberat, ruptă de contextul în care s-a decis. Restul se declară ca nerevizuite și rămân așa.

**71–73 — supraviețuirea.** Se probează o restaurare completă, pe o firmă, cu dovada că ce a ieșit e ce era. Dacă nu se poate proba, nu se poate afirma.

**74–75 — portabilitatea.** Se ia o firmă și se încearcă exportul complet, ca și cum ar pleca. Ce nu iese, sau iese rupt de lanț, e lista.

**De ce la sfârșit:** cer decizii de produs și muncă de construcție, nu cartografiere. Iar 71–73 sunt singurele din tot planul care nu privesc corectitudinea, ci existența — și dacă ele cad, restul nu mai contează.

---

# FAZA 8 — VERDICTUL ȘI CADENȚA

**Tabelul final:** interdicție · instanțe · unde ajunge efectul · criteriu de acceptare · cost de reparație.

Din el iese ordinea reparațiilor: cea din Partea VII a planului de arhitectură, ponderată cu ce s-a găsit efectiv și cu ce blochează un artefact.

**Cadența de remăsurare.** Confruntarea nu e un eveniment. Podeaua part-time a fost corectă, apoi ruptă, apoi corectă. Calea a doua a fost independentă, apoi aliniată. Deci:

- criteriul **ZERO** se remăsoară la fiecare poartă, mecanic;
- criteriul **DECLARAT** se remăsoară când lista de excepții crește;
- **vigoarea articolelor** se reverifică la pragurile din Partea 0 a planului de arhitectură;
- restul, la interval fix, cu instrumentul păstrat, nu reinventat.

**Setul complet din faza 1 se reverifică la fiecare schimbare legislativă majoră.**

---

## Stările și criteriile de acceptare

**Starea măsurătorii:**

| stare | ce înseamnă |
|---|---|
| **MĂSURATĂ** | acoperă domeniul revendicat; punctele oarbe sunt inerente |
| **PARȚIAL** | regiune cunoscută, măsurabilă, lăsată deliberat afară; cifra e plafon inferior |
| **NEMĂSURABILĂ** | nu se poate număra, cu motivul — nu din slăbiciunea instrumentului |
| **NEMĂSURABILĂ RETROACTIV** | e regulă de proces; se aplică de acum înainte, dar trecutul nu se poate reconstitui |
| **NEÎNCEPUTĂ** | nu s-a măsurat |

**Criteriul de acceptare** — se alege la triaj:

| criteriu | când se aplică |
|---|---|
| **ZERO** | nicio instanță nu are voie să existe |
| **DECLARAT** | instanțele pot exista, fiecare cu motiv scris |
| **ÎNCHIS PRIN CONSTRUCȚIE** | nu se mai poate întâmpla, indiferent de instanțele vechi |
| **MĂSURAT ȘI ACCEPTAT** | cunoscut, documentat, deliberat nereparat, cu motiv |

O interdicție fără criteriu ales nu se poate declara închisă.

---

## Reguli de măsurare

1. **Calibrare pe caz cunoscut, înainte de total.** Fără cazul pozitiv găsit, scanul e rupt.
2. **Nu se produce lista întâi.** Se privesc 30 înainte de a anunța un total.
3. **Se privesc, nu se numără.** Trei rezultate numite zgomot s-au dovedit reale la a doua citire.
4. **Fiecare măsurătoare declară ce nu vede.**
5. **Confruntare cu un al doilea instrument.** A corectat deja un detector care dădea 1167 cu 90% zgomot.
6. **Dovada vine din artefact**, nu din proză.
7. **Cache curățat între probe.**
8. **Cifra e plafon inferior când judecata e umană.**

---

## Ce oprește planul

**Planul de arhitectură s-a dovedit greșit.** De patru ori până acum: categoria „convenții de calcul" lipsea; tensiunea P8↔16 nu era tensiune, ci o distincție care lipsea; „un temei lângă o valoare nu e registrul" nu era scris; iar etapa temeiului avea patru verificări nescrise. Se modifică planul prin decizie, apoi se reia.

**O măsurătoare n-a fost calibrată.** O cifră fără caz pozitiv găsit nu e rezultat.

**Un defect produce efect greșit la un om acum** — cifră, blocaj, sau afirmație falsă pe ecran. Se repară pe loc, se scrie în registru, apoi se continuă.

**Triajul spune că nu merită.** O fază estimată la trei zile, fără instanță vie și fără risc juridic mare, se amână explicit, cu motivul scris.

**Termenul a expirat.** Se decide cu ce s-a măsurat.

---

## Un lucru de făcut în afara acestui plan

**Registrul de interpretări nu e doar pentru cod.** E singurul artefact pe care un contabil îl poate revizui în două ore și poate spune dacă alegerile sunt corecte. Nu e muncă de tester — e o întrebare de specialitate pusă unui specialist. Corectitudinea legală a unei interpretări nu se poate stabili altfel: sursa nu răspunde întotdeauna, iar arbitrul acoperă doar ce validează.

**ORDINE SCHIMBATĂ 23.08.2026 (Costin), la punctul de decizie 1.** Faza 4 — instrumentele — **urcă imediat după acest punct, înaintea a orice altceva**. Era pe locul patru fiindcă părea ieftină; pe 23.08 s-a dovedit că e cea care decide dacă restul măsurătorilor înseamnă ceva: din 10 porți verzi care stăteau pe `graf_temei`, **3 erau false** — una raporta o cifră umflată, două treceau pe zero rânduri de 19 zile. **Ordinea de aici: instrumentele → temeiurile (ce a rămas din faza 2) → triajul → restul.**

**Și criteriul fazei 4 se lărgește, tot din ce s-a văzut atunci:** nu se măsoară doar *câte gărzi își iau dovada din proză* și *câte raportează verde pe zero*, ci și **pe ce instrument stă fiecare gardă, și dacă instrumentul acela a fost calibrat**.
