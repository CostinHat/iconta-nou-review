# ARHITECTURA iConta — PLAN NORMATIV

**Versiunea 2** — adaugă P11 (interpretarea declarată) și P12 (izolarea per firmă). Registrul de adevăruri e restructurat pe trei feluri de intrări, fiindcă P11 îl schimbă din temelie.

Acest document spune **cum trebuie să fie**, nu cum este. Nu descrie codul existent și nu s-a scris citindu-l.

Confruntarea cu ce există e o operațiune ulterioară și separată. Diferența dintre acest document și realitate e lista de reparat.

---

# PARTEA I — PRINCIPIILE

Douăsprezece reguli din care decurge tot restul. Fiecare e formulată ca interdicție verificabilă, nu ca intenție.

### P1 — Un adevăr, un loc

Orice valoare, formulă, nomenclator sau regulă de eligibilitate există **într-un singur loc** și se citește de acolo. Nu se copiază, nu se re-declară, nu se recalculează în paralel.

Corolar: dacă două module au nevoie de același adevăr, îl cer din același loc. Dacă unul dintre ele „îl are deja", asta e defectul.

### P2 — Timpul e parametru, nu context

Orice adevăr fiscal se cere **pe o dată**. Nicio funcție de calcul nu citește data curentă.

Consecință obligatorie: recalcularea unei perioade trecute produce exact același rezultat ca prima calculare, oricând s-ar face și indiferent ce s-a schimbat în lege între timp.

### P3 — Cine calculează nu afișează, cine afișează nu calculează

Un număr arătat unui om provine dintr-un singur calcul, făcut într-un singur loc. Stratul de prezentare primește rezultate, nu ingrediente.

Interdicție explicită: nicio regulă fiscală nu se implementează în interfață. Nici măcar o comparație, nici măcar un prag.

### P4 — Documentul emis e fapt; recalculul e a doua părere

Ce a fost dat unui om sau depus la o autoritate se **îngheață cu amprentă** și nu se rescrie. Un recalcul ulterior care diferă nu corectează documentul: produce o **contradicție**, care se arată.

Corecția e un document nou, care îl referă pe primul. Primul rămâne.

### P5 — O afirmație poartă domeniul și sursele

Nimic nu se afirmă despre o firmă fără să spună **la ce se referă** (perioadă sau obiect identificabil) și **pe ce s-a uitat**.

O afirmație fără domeniu nu poate exista. O afirmație fără surse consultate e o opinie, nu o constatare.

### P6 — Verdele afirmă; ce nu s-a verificat se spune

Absența unei contradicții nu e o verificare. Un verdict favorabil declară ce a fost verificat; ce nu s-a putut verifica apare distinct și nu se stinge prin partea care s-a putut face.

Ierarhia stărilor: **necunoscut domină favorabil**; problema domină necunoscutul.

### P7 — Verificarea e independentă prin construcție și prin disciplină

Calea a doua nu importă calea întâi, nu-i copiază constantele, nu-i reproduce formulele.

Când cele două nu coincid, întrebarea se duce la arbitru. **Nu se aliniază una la cealaltă.** O modificare simultană a ambelor cere decizie scrisă, cu motiv.

### P8 — Arbitrul e extern

Când legea, interpretarea noastră și validatorul oficial nu coincid, decide **validatorul**, iar dezacordul se documentează ca atare, nu se ascunde.

Nicio valoare fiscală nu intră în cod fără temei verificat la sursa oficială. Memoria nu e sursă.

### P9 — Perimetrul e declarat

Ce nu e acoperit se scrie. Un modul, o firmă sau o funcționalitate în afara scopului e o **alegere consemnată**, nu o omisiune tăcută.

O declarație de perimetru devenită neadevărată se aprinde.

### P10 — Regula scrisă e regulă păzită

Fiecare principiu de aici are un mecanism care îl face imposibil de încălcat, sau e declarat explicit negardabil, cu motivul scris.

Un principiu fără gardă și fără declarație de negardabilitate nu face parte din arhitectură — e o intenție.

### P11 — Aplicația nu execută legea; o aplică la un caz, iar pasul dintre ele e vizibil

Textul normativ nu determină singur rezultatul în fiecare situație concretă. Între lege și cifră există un pas de interpretare, iar acel pas **nu are voie să fie îngropat într-o condiție din cod**.

Când o regulă lasă loc, alegerea se consemnează ca **interpretare**, distinctă de o valoare cu temei direct. O interpretare:

- citează textul care a lăsat loc;
- enumeră variantele posibile;
- spune ce s-a ales, de ce, de către cine și când;
- rămâne **repunibilă în discuție**, spre deosebire de un temei;
- când arbitrul o contrazice, dezacordul rămâne vizibil până la lămurire, nu se stinge prin alinierea tăcută a codului.

Motivul: o interpretare care poartă același marcaj ca un fapt legal devine imposibil de contestat. Nimeni nu discută un articol de lege — și atunci o alegere greșită supraviețuiește la nesfârșit sub aparența unei obligații.

### P12 — Datele unei firme nu ies din firma ei

Fiecare firmă e izolată prin construcție, nu prin filtru scris de mână. O interogare care ajunge la baza de date fără contextul firmei **eșuează**; nu întoarce date parțiale și nu întoarce date ale altcuiva.

Aceeași regulă la nivelul cabinetului: un cabinet vede firmele lui. Drepturile se verifică la sursă, în interogare, nu doar în interfață.

---

# PARTEA II — STRATURILE

Șapte straturi. Dependența curge **într-o singură direcție**: fiecare strat cunoaște doar straturile de sub el. Un strat nu poate chema în sus și nu poate ocoli un nivel.

```
  7  PREZENTARE        randează, nu decide
  6  ORCHESTRARE       rutare, flux, drepturi, coadă
  5  DOCUMENTE         artefacte emise, înghețate
  4  EVIDENȚA          ce s-a întâmplat, per firmă
  3  CALCUL            funcții pure: intrări + dată → rezultat
  2  REGISTRUL         adevăruri, interpretări, reguli de produs
  1  TEMEIURI          corpusul legislativ, imuabil

  ═  VERIFICAREA       traversează, dar NUMAI CITEȘTE
```

### 1 — Temeiuri

Corpusul de acte normative și documentația validatorului. Imuabil: un act nu se modifică, se abrogă și se înlocuiește.

Nu cunoaște nimic. Nimeni nu-l modifică prin cod.

### 2 — Registrul

Tot ce e normativ: valori cu temei, interpretări, reguli de produs. Structura lui e Partea III.

Se interoghează pe dată. Nu cunoaște firme, nu cunoaște baza de date, nu cunoaște ecrane.

### 3 — Calcul

Funcții pure. Primesc intrări explicite și o dată, întorc un rezultat. Nu citesc baza de date, nu scriu nicăieri, nu cunosc firma, nu cunosc data curentă.

Un calcul fiscal e reproductibil: aceleași intrări dau același rezultat, azi și peste doi ani.

Un rezultat care depinde de o interpretare o **poartă cu el** — cine primește cifra poate afla pe ce alegere stă.

### 4 — Evidența

Ce s-a întâmplat efectiv: facturi, mișcări, salariați, pontaje, extrase, înregistrări contabile.

Izolarea per firmă e proprietate a stratului, nu grijă a apelantului. Scrie și citește. **Nu calculează fiscal** — cere calculul de la stratul 3.

### 5 — Documente

Artefactele care ies din aplicație către un om sau o autoritate: declarații, fluturași, facturi emise, adeverințe, bilanțuri.

Fiecare poartă: **numărul exemplarului, momentul emiterii, autorul, amprenta conținutului**. Append-only. Nimic nu se rescrie.

### 6 — Orchestrare

Rute, flux de lucru, drepturi, coada de validare, perioade închise, notificări.

Decide **cine are voie și când**, niciodată **cât e**.

### 7 — Prezentare

Randează ce primește. Nu conține nicio regulă fiscală, niciun prag, nicio comparație de valori.

O stare arătată pe ecran e o stare calculată în altă parte. Interfața n-are voie să deducă „e în regulă" din absența unui semnal.

### Verificarea — strat transversal, doar-citire

Recalculează independent, compară căi, confruntă cu arbitrul, reconciliază.

**Nu scrie nimic. Nu emite nimic. Nu corectează nimic.** Produce afirmații. Cine acționează pe ele e altcineva.

---

# PARTEA III — REGISTRUL

### Trei feluri de intrări, care nu se amestecă

| Fel | Ce e | Cum se schimbă | Se poate contesta? |
|---|---|---|---|
| **Temei** | legea spune direct valoarea sau regula | când se schimbă legea | nu — se verifică |
| **Interpretare** | legea lasă loc, noi am ales | prin decizie nouă, oricând | da |
| **Regulă de produs** | legea nu spune nimic, noi am decis | prin decizie nouă, oricând | da |

Amestecarea lor e interzisă, fiindcă se **revizuiesc diferit**. Un temei nu se discută, se verifică. O interpretare și o regulă de produs se discută oricând. Dacă o alegere de-a noastră poartă marcajul unui temei, devine imposibil de repus în discuție; dacă un temei poartă marcajul unei alegeri, devine negociabil — ceea ce e mai rău.

### Ce poartă un TEMEI

- valoarea sau formula;
- actul, articolul, alineatul;
- nivelul sursei — Monitor Oficial, interpretare oficială a autorității, practică a validatorului;
- valabil de la; valabil până se derivă din succesor, nu se scrie manual;
- textul citat, verbatim.

### Ce poartă o INTERPRETARE

- textul normativ care a lăsat loc, citat;
- **de ce lasă loc** — ce anume nu determină legea singură;
- variantele posibile, enumerate;
- ce s-a ales;
- motivul alegerii;
- cine a decis și când;
- ce spune arbitrul, dacă a fost întrebat;
- **dacă arbitrul contrazice**: dezacordul, marcat ca deschis, nu ca rezolvat.

O interpretare fără variantele enumerate nu e o interpretare, e o valoare deghizată. Dacă nu poți numi cealaltă variantă, legea nu lăsa loc.

### Ce poartă o REGULĂ DE PRODUS

- ce face regula;
- decizia care a fixat-o, cu data;
- motivul;
- temeiul intern din care decurge, dacă există.

### Categoriile de conținut

| Categorie | Conținut |
|---|---|
| **Cote și procente** | TVA standard și reduse, CAS, CASS, impozit pe venit, CAM, impozit pe profit, micro, dividende, impozit minim |
| **Praguri și plafoane** | salariu minim general și sectorial, plafon de înregistrare în scopuri de TVA, plafon de achiziții intracomunitare, plafoane de deducere, plafoane de beneficii, plafonul bazei de calcul, praguri de rambursare |
| **Facilități** | sume netaxabile, condițiile de acordare, perioadele de aplicare |
| **Nomenclatoare** | coduri de indemnizație, coduri de operațiune în recapitulativă, tipuri de operațiune în decontul special, plan de conturi, CAEN, prefixe și algoritmi de validare a codurilor de TVA din UE, tipuri de asigurat |
| **Formule** | deducere personală, bază minimă la timp parțial, medie zilnică pentru indemnizație, indemnizație pe episod, prorate |
| **Calendare** | termene de depunere pe tip de declarație, zile lucrătoare, sărbători legale, reguli de decalare |
| **Eligibilitate** | ce declarație datorează o firmă, pe ce criteriu, de la ce dată |
| **Structuri** | câmpurile fiecărei declarații, regulile de validare, maparea între surse și poziții |
| **Convenții de calcul** | rotunjire, ordine de aplicare, ce se scade înainte de proratare, regula de alegere a cursului valutar (ce dată, ce sursă) |

Lista e închisă. Un adevăr care nu se încadrează în nicio categorie e semnal că registrul are un gol care se completează prin decizie, nu că adevărul poate sta oriunde.

**Convențiile de calcul, adăugate 22.08.2026 după confruntarea cu codul.** Nu sunt „Formule": formulele spun **ce** se calculează, convențiile spun **cum**. Rotunjirea `HALF_UP` pe sume fiscale (contra celei bancare) e un adevăr cu temei, are deja gardă, și nu încăpea în nicio categorie — nu e cotă, prag, facilitate, nomenclator, formulă, calendar, eligibilitate sau structură.

**Cursul valutar** rămâne în afara registrului **ca valoare** — e un fapt de piață, nu o normă. Dar **regula de alegere a lui** — ce dată se folosește, din ce sursă, consecvent — e convenție și intră.

### Reguli de acces

- Nimeni nu scrie o valoare din aceste categorii în afara registrului.
- Se interoghează **pe data operațiunii**, nu pe data calculului.
- O interogare fără dată e o eroare, nu un default.
- O valoare fără temei, interpretare sau regulă de produs nu poate intra.
- Când un act se abrogă, intrările lui nu se șterg: primesc succesor și rămân interogabile pentru perioadele trecute.
- O interpretare pe care arbitrul o contrazice rămâne marcată ca dezacord deschis până la lămurire.

---

# PARTEA IV — CICLUL DE VIAȚĂ AL UNUI DOCUMENT

Același traseu pentru orice iese din aplicație: declarație, fluturaș, factură, bilanț.

```
INTRARE          date brute → evidență
   ↓
CALCUL           evidență + registru(la_data) → rezultat + interpretările folosite
   ↓
PREVIZUALIZARE   rezultat randat, aceleași reguli ca la emitere
   ↓
VERIFICARE       cale independentă + arbitru extern
   ↓
EMITERE          rezultat înghețat cu amprentă, exemplar numerotat
   ↓
PREDARE          eveniment propriu: cui, când
   ↓
RECONCILIERE     document emis ↔ evidență ↔ recalcul
```

### Reguli obligatorii pe traseu

**Previzualizarea și emiterea folosesc același calcul.** Nu două implementări, nu două reguli de validare. Ce se vede la previzualizare e ce se emite.

**Rezultatul poartă interpretările pe care stă.** Când o cifră depinde de o alegere care putea fi alta, asta se poate afla din rezultat, nu din citirea codului.

**Verificarea precedă emiterea și nu o poate declanșa.** Un verificator care emite nu mai e verificator.

**Emiterea e idempotentă și repetabilă.** Fiecare emitere produce un exemplar nou, numerotat. Nicio schemă nu interzice al doilea exemplar.

**Predarea e distinctă de emitere.** Se poate emite de zece ori înainte de a preda; ce contează e exemplarul predat. Dacă predarea nu se marchează, asta e o limită declarată, nu o presupunere tăcută.

**Reconcilierea compară trei lucruri**, nu două: documentul emis, evidența din care a rezultat, și recalculul de azi. Divergențele dintre oricare două sunt contradicții, nu erori de rotunjire — până la proba contrarie.

**O interpretare schimbată nu rescrie documentele emise sub cea veche.** Produce contradicții, care se arată. Regimul unui document e cel de la emitere.

---

# PARTEA V — CONTRACTE ÎNTRE MODULE

### Ce declară un modul

- **ce primește** — intrări explicite, fără citiri ascunse;
- **ce întoarce** — un tip, nu un dicționar liber;
- **ce garantează** — invariantele rezultatului;
- **pe ce interpretări stă** — dacă vreo alegere putea fi alta;
- **ce nu poate spune** — limitele, declarate ca date, nu ca proză.

### Perechile generator ↔ verificator

Pentru fiecare document generat există o cale de verificare cu următoarele proprietăți obligatorii:

- **nu importă** modulul verificat, nici direct, nici tranzitiv;
- **nu-i copiază** constantele — le cere din registru;
- **nu-i reproduce** formulele — le recalculează din sursă;
- **nu se modifică** în același commit cu el fără decizie scrisă cu motiv;
- **nu se aliniază** la el când diverg — diferența se duce la arbitru.

Când divergența vine dintr-o interpretare, nu dintr-o eroare, cele două căi nu se aliniază: interpretarea se ridică la decizie.

### Interfața cu autoritățile

Orice comunicare cu o autoritate externă are trei componente separate:

- **generarea** artefactului;
- **validarea** cu instrumentul oficial;
- **transmiterea**.

Cele trei nu se amestecă. Un artefact validat dar netransmis, sau transmis fără validare, sunt stări distincte și vizibile.

### Erorile publicate

Orice refuz care ajunge la un om e scris pentru el, nu pentru programator:

- spune **ce lipsește sau ce nu se potrivește**;
- spune **unde se rezolvă**;
- nu conține nume de câmpuri, tabele, clase sau tipuri interne;
- e în limba interfeței, cu diacritice.

Un refuz motivat nu devine niciodată eroare generică.

---

# PARTEA VI — CE E INTERZIS PRIN CONSTRUCȚIE

Nu convenții. Fiecare are un mecanism care o face imposibilă.

| # | Interdicție | Din |
|---|---|---|
| 1 | O valoare fiscală scrisă în afara registrului | P1 |
| 2 | O interogare a registrului fără dată | P2 |
| 3 | Un calcul fiscal care citește data curentă | P2 |
| 4 | O regulă fiscală implementată în stratul de prezentare | P3 |
| 5 | Un strat care cheamă în sus sau ocolește un nivel | P3 |
| 6 | O cerere de citire care modifică date | P4 |
| 7 | Un document emis care se rescrie | P4 |
| 8 | O schemă care interzice al doilea exemplar | P4 |
| 9 | O afirmație fără domeniu sau fără surse | P5 |
| 10 | Un verdict favorabil care coexistă cu necunoscut nedeclarat | P6 |
| 11 | Un verificator care importă modulul verificat | P7 |
| 12 | O modificare simultană verificator/verificat fără decizie scrisă | P7 |
| 13 | Un refuz care ajunge la om cu nume interne sau fără diacritice | P3 |
| 14 | Un parametru cu valoare implicită într-o funcție de calcul fiscal | P2 |
| 15 | Reguli diferite la previzualizare față de salvare | P3 |
| 16 | Un nomenclator derivat dintr-o sursă secundară în locul celei normative | P8 |
| 17 | Un adevăr din registru, re-declarat în alt modul | P1 |
| 18 | O gardă care își ia dovada din proză | P10 |
| 19 | O gardă care raportează favorabil pe zero rânduri | P10 |
| 20 | O declarație de perimetru devenită neadevărată | P9 |
| 21 | **O alegere de interpretare care apare ca și cum ar fi text de lege** | P11 |
| 22 | **O interpretare fără variantele posibile enumerate** | P11 |
| 23 | **Un dezacord cu arbitrul, stins prin aliniere fără decizie** | P11 |
| 24 | **O interogare care ajunge la baza de date fără contextul firmei** | P12 |
| 25 | **Un drept verificat numai în interfață, nu și în interogare** | P12 |

### Ce se poate măsura, și cât (22.08.2026, după prima confruntare)

Trei interdicții nu se măsoară complet. Se scrie aici, ca nimeni să nu ia o cifră drept un total.

**22 — NEMĂSURABILĂ.** Nu din slăbiciunea instrumentului: nu are numitor. O interpretare nemarcată e
indistinguibilă de un calcul. Se poate număra ce poartă un marcaj; nu se poate număra ce n-a fost
recunoscut niciodată ca alegere. Orice cifră ar însemna „cele găsite de cine a căutat", nu „câte
sunt". Se declară ca atare și **nu se cere o cifră pentru ea**.

Ce se poate face în schimb, și s-a făcut: `core/interpretare.py` face interpretarea **declarabilă**,
cu variantele obligatorii, iar `core/test_comparatii_clasificate.py` închide clasa
**NECLASIFICAT** — nu clasa *greșit clasificat*.

**21 — măsurabilă pe forma declarată.** Scanul găsește interpretările care iau forma unei
**comparații** pe o valoare de registru. Măsurat: 15 candidate, 2 confirmate la citire pe context.
Nu vede alegerile care nu sunt comparații — codificarea trimestrială `09`, ordinea de aplicare, felul
de rotunjire. Cifra e un **plafon inferior**, nu un total.

**23 — măsurabilă pe forma declarată.** `core/test_cale_a_doua.py` prinde alinierea *scrisă* („aliniat
cu <modulul verificat>") și cere decizie scrisă la co-modificare. O aliniere **tăcută** — schimbi
formula fără s-o spui — nu lasă amprentă textuală. Gardul își declară singur limita; arbitrul rămâne
judecătorul final.

**Ce NU verifică garda comparațiilor**, ca să nu se citească drept mai mult decât e: că temeiul citat
**chiar determină** comparația. Aia e o judecată semantică. O gardă care ar pretinde că o face ar fi
mai rea decât una care lipsește — ar transforma o citire umană într-un verde automat. Marcajul e un
**link verificabil** (cheia se rezolvă în registru sau nu), nu o frază citită.

---

# PARTEA VII — CUM SE FOLOSEȘTE DOCUMENTUL

**Nu se modifică pentru a se potrivi cu realitatea.** Dacă o parte din aplicație îl încalcă, se schimbă aplicația. Dacă un principiu se dovedește greșit, se schimbă documentul — dar prin decizie scrisă, cu motiv, nu prin adaptare tăcută.

**Confruntarea e o operațiune separată.** Se ia principiu cu principiu și interdicție cu interdicție, și se măsoară câte instanțe există. Rezultatul e o listă de reparat, ordonată după cât de departe ajunge efectul.

**Ordinea reparațiilor** decurge din structură, nu din numărul de instanțe:

1. **Registrul** — P1, P11, interdicțiile 1, 2, 16, 17, 21, 22, 23. Elimină clasa care produce continuu divergențe, și separă ce e lege de ce am ales noi.
2. **Direcția dependenței** — P3, interdicțiile 4, 5, 13, 15.
3. **Documentele** — P4, interdicțiile 6, 7, 8.
4. **Izolarea** — P12, interdicțiile 24, 25.
5. **Restul.**

**Fiecare interdicție primește un gard înainte de reparație**, nu după. Ordinea e singura formă tare de probă.

---

# ANEXĂ — DE CE P11

Trei situații reale, toate din aceeași săptămână, toate cu aceeași formă:

**„Încadrat cu salariul de bază minim brut."** Egalitate strictă, sau sub un plafon? Legea nu spune. S-a ales egalitatea strictă — corect, probabil — dar alegerea a trăit într-o comparație din cod, nu ca interpretare. Consecința e vizibilă pentru orice patron: un leu peste minim costă salariatul optzeci și doi.

**Facilitatea la baza minimă part-time.** Legea spune că facilitatea e pentru normă întreagă. Structura publicată de autoritate o scade totuși din nivelul de referință, iar validatorul o implementează. S-a ales urmarea legii, contra arbitrului, cu raționament scris în comentariu — dar nu ca dezacord marcat. Două săptămâni mai târziu, semnalul care contrazicea alegerea fusese înghețat ca așteptat, iar a doua cale de verificare fusese aliniată la prima.

**Codificarea perioadei trimestriale.** Cifra 09 pentru trimestrul al treilea arăta ca o eroare și a fost raportată ca atare. Era codificarea corectă a autorității. O oră de investigație, care nu ar fi fost necesară dacă alegerea ar fi fost consemnată ca interpretare cu textul citat.

Ce au în comun: în toate trei, **cineva a decis ceva ce legea nu decisese**, iar decizia a devenit invizibilă în momentul în care a intrat în cod. Prima a rămas nediscutată. A doua a produs o divergență în bani. A treia a costat timp.

P11 nu împiedică interpretarea — e inevitabilă. Împiedică interpretarea să se deghizeze în lege.
