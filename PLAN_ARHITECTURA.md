# ARHITECTURA iConta — PLAN NORMATIV

**Versiunea 4** — adaugă Partea B: P14–P20, principiile de conformitate. Scopul nu e doar o aplicație care calculează corect, ci una care se poate apăra la un control.

Acest document spune **cum trebuie să fie**, nu cum este. Nu descrie codul existent și nu s-a scris citindu-l.

Confruntarea cu ce există e o operațiune ulterioară și separată. Diferența dintre acest document și realitate e lista de reparat.

---

# PARTEA I — PRINCIPIILE

Douăzeci de reguli. Fiecare e formulată ca interdicție verificabilă, nu ca intenție.

Primele treisprezece privesc **corectitudinea a ceea ce producem**. Ultimele șapte privesc **ce se cere de la noi când suntem verificați** — și fără ele o aplicație poate calcula impecabil și rămâne inutilizabilă la un control.

---

## A. CORECTITUDINEA

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
- când arbitrul o contrazice, dezacordul rămâne vizibil până la lămurire.

Motivul: o interpretare care poartă același marcaj ca un fapt legal devine imposibil de contestat. Nimeni nu discută un articol de lege — și atunci o alegere greșită supraviețuiește la nesfârșit sub aparența unei obligații.

### P12 — Datele unei firme nu ies din firma ei

Fiecare firmă e izolată prin construcție, nu prin filtru scris de mână. O interogare care ajunge la baza de date fără contextul firmei **eșuează**; nu întoarce date parțiale și nu întoarce date ale altcuiva.

Aceeași regulă la nivelul cabinetului: un cabinet vede firmele lui. Drepturile se verifică la sursă, în interogare, nu doar în interfață.

### P13 — Textul nu e purtător de decizie

Într-o aplicație de contabilitate, aproape tot ce pare text e altceva. Confuzia e cauza unei clase întregi de defecte: cine crede că o frază e text, o rescrie — și rescrie o decizie fără să știe.

| Ce e | Ce pare | Unde stă de fapt |
|---|---|---|
| **Nomenclatura oficială** | text | intrare în registru, cu temei; nu o scriem noi |
| **Afirmația** | frază | structură: fel, domeniu, surse, remediu |
| **Datele omului** | text | text autentic, dar al lui; nu poartă decizii de-ale noastre |

**Ce e text cu adevărat:** ce e fix în interfață — etichete, titluri, ajutor. Acela primește **cheie** și loc unic de definire.

*Ce vine din date* nu are formă textuală până la randare. Nu se stochează ca frază, nu se compară, nu se clasifică după conținut.

**Testul de proiectare:** dacă rescrii o frază și se schimbă comportamentul, textul acela nu era text.

**Ce nu rezolvă nici cheia, nici structura:** un text corect ca formă poate fi fals ca afirmație. De aceea eticheta se **derivă din starea efectivă**, nu se alege de cine randează.

**Corolarul:** între momentul în care aplicația știe ceva și momentul în care omul citește există **un singur pas**.

---

## B. CONFORMITATEA

### P14 — Orice cifră se desface până la documentul care o justifică

La un control, întrebarea nu e „e corectă formula", ci „arătați-mi din ce iese cifra asta". Legea contabilității cere document justificativ pentru orice înregistrare; consecința pentru aplicație e că lanțul trebuie să existe **ca dată**, nu să fie reconstituibil prin raționament.

Lanțul complet, navigabil în ambele sensuri:

```
poziție din declarație
   ↔ înregistrare contabilă
      ↔ document primar
         ↔ sursa lui (fișier încărcat, factură electronică, extras, introducere manuală)
```

- fiecare verigă e navigabilă la cerere, fără recalculare;
- o poziție care nu se poate desface e un defect, nu o limitare;
- lanțul se păstrează pentru documentele **emise**, nu se reface din starea de azi;
- suma pozițiilor desfăcute trebuie să dea exact valoarea declarată; altfel lanțul e rupt și se spune.

Corolar: pentru orice poziție dintr-o declarație depusă, aplicația produce lista documentelor care o compun — chiar dacă între timp evidența s-a schimbat.

### P15 — După închiderea unei perioade, nu se modifică; se stornează

O perioadă închisă e o afirmație despre trecut. Modificarea ei retroactivă rupe corespondența dintre ce s-a declarat și ce se poate dovedi.

- Închiderea e un act deliberat, cu autor și moment, nu o consecință a trecerii timpului.
- După închidere, editarea e **imposibilă**, nu nerecomandată.
- Corectarea se face prin înregistrare nouă care o referă pe cea corectată; cea veche rămâne.
- Redeschiderea e posibilă, dar e act consemnat, cu motiv, și marchează documentele emise din acea perioadă ca fiind sub rezervă.
- Numerotarea documentelor emise nu are goluri și nu se reia; un număr anulat rămâne anulat.

### P16 — Cine a autorizat, se știe

Orice act cu efect juridic extern — o depunere, o emitere de factură, o închidere de perioadă, o corecție — are un autor identificat, nu doar un moment.

- Autorizarea e distinctă de execuție: cine apasă poate să nu fie cine răspunde.
- Un act făcut de sistem, fără om în spate, se marchează ca atare și e excepție declarată.
- Urma nu se poate șterge și nu se poate edita. Se păstrează cel puțin cât obligația la care se referă.

Aceeași disciplină pentru orice operațiune care atinge date fiscale: cine, ce, când, valoarea dinainte și cea de după. Jurnalizarea nu e o funcționalitate; e felul în care P14 și P16 devin verificabile.

### P17 — Ce se păstrează, cât și pe ce temei

Termenele de păstrare nu sunt o setare, sunt obligații cu temei propriu, iar unele intră în conflict cu dreptul la ștergere.

- Fiecare categorie de dată are termen și temei scris.
- La o cerere de ștergere, ce nu poate fi șters se **numește**, cu temeiul — nu se ignoră și nu se șterge din greșeală.
- Anonimizarea e alternativă doar acolo unde obligația privește fapta, nu identitatea.
- Expirarea unui termen nu produce ștergere automată fără verificarea celorlalte temeiuri care ar putea acoperi aceeași dată.

### P18 — Legea se schimbă retroactiv, iar aplicația știe pe cine

O reglementare publicată în septembrie și aplicabilă din iulie e situația obișnuită, nu excepția. O aplicație fără ciclu de viață pentru asta produce, tăcut, declarații depuse care au devenit incorecte.

La orice modificare de regulă cu efect anterior publicării:

- se determină **perioadele afectate**;
- se determină **documentele deja emise** sub regula veche;
- fiecare devine o **contradicție** vizibilă, nu se rescrie;
- rezultă o listă de rectificative posibile, cu diferența calculată;
- decizia de a rectifica e a omului; absența deciziei rămâne vizibilă.

Regula veche nu se șterge din registru. Perioadele trecute rămân interogabile sub ea — altfel P2 se rupe.

### P19 — Cu exteriorul, „nu știu" e o stare legitimă

Orice schimb cu o autoritate sau cu un serviciu extern poate rămâne nelămurit. O aplicație care nu modelează starea asta forțează omul între două greșeli: retrimite și depune de două ori, sau nu retrimite și ratează termenul.

Stările obligatorii: **nepornită, în curs, confirmată, respinsă, nelămurită**.

- „Nelămurită" nu se convertește singură în niciuna dintre celelalte.
- Nicio retrimitere automată dintr-o stare nelămurită.
- Reconcilierea cu autoritatea — ce spune ea că a primit — e operațiune proprie, nu presupunere.
- Identificatorul primit de la autoritate se păstrează; fără el, confirmarea nu e confirmare.

### P20 — Proveniența se păstrează, iar o presupunere nu devine fapt

Aceeași sumă poate veni dintr-o factură electronică, dintr-o recunoaștere automată de imagine, dintr-o potrivire de extras sau din tastatura contabilului. Prima e autoritate; a doua e ipoteză cu probabilitate; a treia e presupunere; a patra e afirmația omului.

- Fiecare valoare intrată din afară poartă **sursa** și **gradul de certitudine**.
- O valoare nesigură nu devine sigură prin salvare. Devine sigură prin **confirmare explicită**, consemnată.
- Un calcul care stă pe valori neconfirmate spune asta în rezultat.
- O potrivire automată e propunere până e acceptată; refuzul se consemnează la fel ca acceptarea.

### Două reguli care traversează

**Omul are ultimul cuvânt, iar dezacordul lui se înregistrează.** Contabilul poartă răspunderea legală, nu aplicația. Un blocaj fără cale de trecere face produsul inutilizabil profesional; o trecere tăcută pierde urma. Deci: trecerea există, cere motiv, rămâne vizibilă ca dezacord — nu ca problemă rezolvată.

**Două scrieri simultane nu se pierd tăcut.** Doi oameni din același cabinet, pe aceeași lună: cine salvează al doilea trebuie să afle că starea s-a schimbat sub el. Suprascrierea fără avertisment produce declarații greșite pe care nimeni nu le poate explica.

---

# PARTEA II — STRATURILE

Dependența curge **într-o singură direcție**: fiecare strat cunoaște doar straturile de sub el. Un strat nu poate chema în sus și nu poate ocoli un nivel.

```
  7  PREZENTARE        randează, nu decide
  6  ORCHESTRARE       rutare, flux, drepturi, coadă, perioade închise
  5  DOCUMENTE         artefacte emise, înghețate, cu lanț și autor
  4  EVIDENȚA          ce s-a întâmplat, per firmă, cu proveniență
  3  CALCUL            funcții pure: intrări + dată → rezultat
  2  REGISTRUL         adevăruri, interpretări, reguli de produs
  1  TEMEIURI          corpusul legislativ, imuabil

  ═  VERIFICAREA       traversează, NUMAI CITEȘTE
  ═  URMA              traversează, se scrie o dată, nu se editează
```

### 1 — Temeiuri

Corpusul de acte normative și documentația validatorului. Imuabil: un act nu se modifică, se abrogă și se înlocuiește. Actele abrogate rămân, cu succesor.

### 2 — Registrul

Tot ce e normativ: valori cu temei, interpretări, reguli de produs, convenții de calcul, nomenclatură oficială, termene de retenție. Structura lui e Partea III.

Se interoghează pe dată. Nu cunoaște firme, nu cunoaște baza de date, nu cunoaște ecrane.

### 3 — Calcul

Funcții pure. Primesc intrări explicite și o dată, întorc un rezultat. Nu citesc baza de date, nu scriu nicăieri, nu cunosc firma, nu cunosc data curentă.

Rezultatul poartă cu el **interpretările** pe care stă și **gradul de certitudine** al intrărilor.

### 4 — Evidența

Ce s-a întâmplat efectiv: facturi, mișcări, salariați, pontaje, extrase, înregistrări contabile.

Fiecare valoare poartă **proveniența**. Izolarea per firmă e proprietate a stratului, nu grijă a apelantului. Perioadele închise sunt imposibil de modificat de aici.

**Nu calculează fiscal** — cere calculul de la stratul 3.

### 5 — Documente

Artefactele care ies către un om sau o autoritate.

Fiecare poartă: **numărul exemplarului, momentul emiterii, autorul autorizării, amprenta conținutului, lanțul până la documentele primare, starea trimiterii**. Append-only.

### 6 — Orchestrare

Rute, flux, drepturi, coada de validare, închiderea și redeschiderea perioadelor, notificări, detecția scrierilor concurente.

Decide **cine are voie și când**, niciodată **cât e**.

### 7 — Prezentare

Randează ce primește. Nicio regulă fiscală, niciun prag, nicio comparație de valori.

E **singurul strat în care există text** — fraze fixe cu cheie, plus randarea structurilor primite. Nu compune sens, nu decide ce să spună.

### Verificarea — transversal, doar-citire

Recalculează independent, compară căi, confruntă cu arbitrul, reconciliază.

**Nu scrie nimic. Nu emite nimic. Nu corectează nimic.** Nu-și ia dovada din proză: nici din docstring, nici din comentariu, nici din textul interfeței.

### Urma — transversal, se scrie o dată

Cine, ce, când, valoarea dinainte și cea de după. Nu se editează, nu se șterge.

E singura excepție de la „o citire nu scrie": o citire de date personale poate lăsa urma faptului că a avut loc. Excepția e mecanică — orice operațiune poate jurnaliza, niciuna nu poate scrie altceva.

---

# PARTEA III — REGISTRUL

### Trei feluri de intrări, care nu se amestecă

| Fel | Ce e | Cum se schimbă | Se poate contesta? |
|---|---|---|---|
| **Temei** | legea spune direct | când se schimbă legea | nu — se verifică |
| **Interpretare** | legea lasă loc, noi am ales | prin decizie nouă | da |
| **Regulă de produs** | legea nu spune nimic, noi am decis | prin decizie nouă | da |

Amestecarea lor e interzisă, fiindcă se **revizuiesc diferit**. Dacă o alegere de-a noastră poartă marcajul unui temei, devine imposibil de repus în discuție; dacă un temei poartă marcajul unei alegeri, devine negociabil — ceea ce e mai rău.

### Ce poartă un TEMEI

Valoarea, formula sau denumirea oficială · actul, articolul, alineatul · nivelul sursei · valabil de la, cu „valabil până" derivat din succesor · textul citat verbatim.

### Ce poartă o INTERPRETARE

Textul care a lăsat loc, citat · de ce lasă loc · variantele posibile, enumerate · ce s-a ales · motivul · cine și când · ce spune arbitrul · dacă arbitrul contrazice, dezacordul marcat ca deschis.

O interpretare fără variantele enumerate nu e interpretare, e o valoare deghizată.

### Ce poartă o REGULĂ DE PRODUS

Ce face · decizia care a fixat-o, cu data · motivul · temeiul intern din care decurge.

### Categoriile de conținut

| Categorie | Conținut |
|---|---|
| **Cote și procente** | TVA, CAS, CASS, impozit pe venit, CAM, profit, micro, dividende, impozit minim |
| **Praguri și plafoane** | salariu minim general și sectorial, plafoane de înregistrare, de achiziții intracomunitare, de deducere, de beneficii, ale bazei de calcul, de rambursare |
| **Facilități** | sume netaxabile, condiții, perioade de aplicare |
| **Nomenclatoare** | coduri de indemnizație, de operațiune, tipuri de operațiune, plan de conturi, CAEN, algoritmi de validare a codurilor de TVA din UE, tipuri de asigurat — **cu denumirile oficiale, verbatim** |
| **Formule** | deducere personală, bază minimă la timp parțial, medie zilnică, indemnizație pe episod, prorate |
| **Convenții de calcul** | rotunjire, ordinea de aplicare, ce se scade înainte de proratare, regula de alegere a cursului valutar |
| **Calendare** | termene pe tip de declarație, zile lucrătoare, sărbători, reguli de decalare |
| **Eligibilitate** | ce declarație datorează o firmă, pe ce criteriu, de la ce dată |
| **Structuri** | câmpurile fiecărei declarații, regulile de validare, maparea între surse și poziții |
| **Retenție** | ce categorie de dată se păstrează, cât, pe ce temei, ce împiedică ștergerea |

Distincția dintre **Formule** și **Convenții**: formulele spun *ce* se calculează, convențiile spun *cum*.

Lista e închisă. Un adevăr care nu se încadrează e semnal că registrul are un gol, nu că adevărul poate sta oriunde.

### Reguli de acces

- Nimeni nu scrie o valoare din aceste categorii în afara registrului.
- Se interoghează **pe data operațiunii**. O interogare fără dată e o eroare, nu un default.
- O valoare fără temei, interpretare sau regulă de produs nu poate intra.
- Actele abrogate nu se șterg: primesc succesor și rămân interogabile pentru perioadele trecute.
- O interpretare contrazisă de arbitru rămâne marcată ca dezacord deschis.
- **Denumirile oficiale sunt intrări cu temei**, nu șiruri în cod. O etichetă reformulată e o abatere de la sursă, nu o îmbunătățire de stil.
- **O modificare cu efect retroactiv declanșează P18**, nu se aplică tăcut.

### Ce e în afara registrului

**Cursul valutar** — valoare pe dată, dar fapt de piață, nu normă. Regula de alegere a lui e însă convenție de calcul și intră.

---

# PARTEA IV — CICLUL DE VIAȚĂ AL UNUI DOCUMENT

```
INTRARE          date brute → evidență, cu proveniență și grad de certitudine
   ↓
CALCUL           evidență + registru(la_data) → rezultat + interpretări + certitudine
   ↓
PREVIZUALIZARE   rezultat randat, aceleași reguli ca la emitere
   ↓
VERIFICARE       cale independentă + arbitru extern
   ↓
EMITERE          înghețat cu amprentă, exemplar numerotat, autor, lanț păstrat
   ↓
TRIMITERE        stare explicită: în curs / confirmată / respinsă / NELĂMURITĂ
   ↓
PREDARE          eveniment propriu: cui, când
   ↓
RECONCILIERE     document emis ↔ evidență ↔ recalcul ↔ ce confirmă autoritatea
```

### Reguli obligatorii pe traseu

**Previzualizarea și emiterea folosesc același calcul.** Nu două implementări, nu două reguli de validare.

**Rezultatul poartă interpretările pe care stă** și gradul de certitudine al intrărilor.

**Verificarea precedă emiterea și nu o poate declanșa.** Un verificator care emite nu mai e verificator.

**Emiterea e idempotentă și repetabilă.** Fiecare emitere produce un exemplar nou, numerotat. Nicio schemă nu interzice al doilea exemplar.

**Emiterea îngheață lanțul**, nu doar cifrele. Documentele care au compus o poziție rămân legate de exemplarul emis, chiar dacă evidența se schimbă după.

**Predarea e distinctă de emitere.**

**Reconcilierea compară patru lucruri**: documentul emis, evidența din care a rezultat, recalculul de azi, și ce confirmă autoritatea că a primit.

**O interpretare schimbată nu rescrie documentele emise sub cea veche.** Produce contradicții.

**O modificare retroactivă de lege parcurge P18** — perioade afectate, documente devenite incorecte, listă de rectificative, decizie a omului.

---

# PARTEA V — CONTRACTE ÎNTRE MODULE

### Ce declară un modul

Ce primește · ce întoarce, ca tip · ce garantează · **pe ce interpretări stă** · **ce certitudine au intrările** · ce nu poate spune.

### Perechile generator ↔ verificator

- nu importă modulul verificat, nici tranzitiv;
- nu-i copiază constantele — le cere din registru;
- nu-i reproduce formulele;
- nu se modifică în același commit fără decizie scrisă cu motiv;
- nu se aliniază la el când diverg — diferența se duce la arbitru.

Când divergența vine dintr-o interpretare, nu dintr-o eroare, interpretarea se ridică la decizie.

### Interfața cu autoritățile

Patru componente separate: **generarea**, **validarea**, **transmiterea**, **reconcilierea**.

Un artefact validat dar netransmis, sau transmis fără validare, sunt stări distincte și vizibile. Ce spune autoritatea că a primit se confruntă cu ce credem noi că am trimis.

### Erorile publicate

Spun ce lipsește și unde se rezolvă · nu conțin nume de câmpuri, tabele, clase sau tipuri interne · sunt în limba interfeței, cu diacritice.

Un refuz motivat nu devine niciodată eroare generică.

---

# PARTEA VI — CE E INTERZIS PRIN CONSTRUCȚIE

| # | Interdicție | Din |
|---|---|---|
| 1 | O valoare fiscală scrisă în afara registrului | P1 |
| 2 | O interogare a registrului fără dată | P2 |
| 3 | Un calcul fiscal care citește data curentă | P2 |
| 4 | O regulă fiscală implementată în stratul de prezentare | P3 |
| 5 | Un strat care cheamă în sus sau ocolește un nivel | P3 |
| 6 | O cerere de citire care modifică date de business | P4 |
| 7 | Un document emis care se rescrie | P4 |
| 8 | O schemă care interzice al doilea exemplar | P4 |
| 9 | O afirmație fără domeniu sau fără surse | P5 |
| 10 | Un verdict favorabil care coexistă cu necunoscut nedeclarat | P6 |
| 11 | Un verificator care importă modulul verificat | P7 |
| 12 | O modificare simultană verificator/verificat fără decizie scrisă | P7 |
| 13 | Un refuz cu nume interne sau fără diacritice | P3 |
| 14 | Un parametru cu valoare implicită într-o funcție de calcul fiscal | P2 |
| 15 | Reguli diferite la previzualizare față de salvare | P3 |
| 16 | Un nomenclator derivat dintr-o sursă secundară | P8 |
| 17 | Un adevăr din registru, re-declarat în alt modul | P1 |
| 18 | O gardă care își ia dovada din proză | P10 |
| 19 | O gardă care raportează favorabil pe zero rânduri | P10 |
| 20 | O declarație de perimetru devenită neadevărată | P9 |
| 21 | O interpretare care apare ca și cum ar fi text de lege | P11 |
| 22 | O interpretare fără variantele posibile enumerate | P11 |
| 23 | Un dezacord cu arbitrul, stins prin aliniere fără decizie | P11 |
| 24 | O interogare fără contextul firmei | P12 |
| 25 | Un drept verificat numai în interfață | P12 |
| 26 | O decizie luată comparând sau clasificând text | P13 |
| 27 | Un verdict stocat ca frază, nu ca structură | P13 |
| 28 | O denumire de nomenclator oficial scrisă ca literal în cod | P13 |
| 29 | O frază fixă de interfață fără cheie și loc unic | P13 |
| 30 | Două stări distincte cu aceeași etichetă | P13 |
| 31 | O etichetă aleasă de cine randează, nu derivată din stare | P13·P3 |
| 32 | O poziție de declarație care nu se poate desface până la document | P14 |
| 33 | Un lanț de justificare a cărui sumă nu dă valoarea declarată | P14 |
| 34 | Modificarea unei înregistrări dintr-o perioadă închisă | P15 |
| 35 | Un număr de document reutilizat, sau o serie cu goluri | P15 |
| 36 | O redeschidere de perioadă fără motiv consemnat | P15 |
| 37 | Un act cu efect juridic extern, fără autor identificat | P16 |
| 38 | O urmă de audit care se poate edita sau șterge | P16 |
| 39 | O ștergere care atinge date aflate sub obligație de păstrare | P17 |
| 40 | O categorie de dată fără termen și temei de retenție | P17 |
| 41 | O modificare retroactivă aplicată fără lista perioadelor afectate | P18 |
| 42 | O regulă veche ștearsă din registru la înlocuire | P18·P2 |
| 43 | O retrimitere automată dintr-o stare nelămurită | P19 |
| 44 | O trimitere considerată confirmată fără identificator de la autoritate | P19 |
| 45 | O valoare intrată din afară, fără sursă și grad de certitudine | P20 |
| 46 | O presupunere devenită fapt fără confirmare consemnată | P20 |
| 47 | Un blocaj fără cale de trecere pentru om, sau o trecere fără urmă | traversal |
| 48 | O suprascriere concurentă fără avertisment | traversal |

---

# PARTEA VII — CUM SE FOLOSEȘTE DOCUMENTUL

**Nu se modifică pentru a se potrivi cu realitatea.** Dacă o parte din aplicație îl încalcă, se schimbă aplicația. Dacă un principiu se dovedește greșit, se schimbă documentul — prin decizie scrisă, cu motiv, nu prin adaptare tăcută.

**Confruntarea e o operațiune separată.** Rezultatul se scrie în `CONFORMITATE.md`, o secțiune per interdicție, cu stare declarată: MĂSURATĂ, NEMĂSURABILĂ, PARȚIAL, NEÎNCEPUTĂ. „Investigată" nu e o stare. Un câmp gol nu e permis: dacă nu se poate măsura, se scrie de ce.

**Ordinea reparațiilor** decurge din structură și din risc juridic:

| # | Grup | Principii | Interdicții |
|---|---|---|---|
| 1 | Registrul | P1, P11, P13 parțial | 1, 2, 16, 17, 21, 22, 23, 28 |
| 2 | Inalterabilitatea și urma | P15, P16 | 34–38 |
| 3 | Trasabilitatea | P14 | 32, 33 |
| 4 | Direcția dependenței | P3, P13 | 4, 5, 13, 15, 26, 27, 31 |
| 5 | Documentele și trimiterea | P4, P19 | 6, 7, 8, 43, 44 |
| 6 | Proveniența | P20 | 45, 46 |
| 7 | Izolarea | P12 | 24, 25 |
| 8 | Retenția și retroactivitatea | P17, P18 | 39–42 |
| 9 | Restul | — | 29, 30, 47, 48 |

Pasul 2 urcă înaintea trasabilității deliberat: un lanț de justificare construit peste o evidență care se poate modifica retroactiv nu dovedește nimic.

**Fiecare interdicție primește un gard înainte de reparație**, nu după. Ordinea e singura formă tare de probă.

---

# ANEXĂ A — DE CE P11

**„Încadrat cu salariul de bază minim brut."** Egalitate strictă, sau sub un plafon? Legea nu spune. S-a ales egalitatea strictă, dar alegerea a trăit într-o comparație din cod. Consecința: un leu peste minim costă salariatul optzeci și doi.

**Facilitatea la baza minimă part-time.** Legea spune că e pentru normă întreagă; structura publicată de autoritate o scade totuși din nivelul de referință, iar validatorul o implementează. S-a ales urmarea legii, contra arbitrului, cu raționament în comentariu — dar nu ca dezacord marcat. Două săptămâni mai târziu, semnalul care contrazicea alegerea fusese înghețat ca așteptat, iar a doua cale de verificare fusese aliniată la prima.

**Codificarea perioadei trimestriale.** Cifra 09 pentru trimestrul al treilea arăta ca o eroare și a fost raportată ca atare. Era codificarea corectă a autorității.

În toate trei, **cineva a decis ceva ce legea nu decisese**, iar decizia a devenit invizibilă în momentul în care a intrat în cod.

---

# ANEXĂ B — DE CE P13

**Text care afirmă fals.** „Vector necompletat" pe firme cu vectorul complet. „Patru-ochi e dezactivat" pe o politică doar suspendată. „Validarea în doi ✓" pe un cabinet cu un singur validator. „0 firme erau deja în portofoliu" când erau.

**Text folosit ca dată.** Clasificarea duplicatelor la import se făcea potrivind proză. O reformulare a mesajului ar fi schimbat tăcut rezultatul.

**Text citit de o gardă ca dovadă.** Patru instanțe într-o zi: docstring luat drept SQL, comentariu luat drept randare, explicație luată drept cod.

**Text scris pentru programator, livrat contabilului.** Refuzuri corecte pe fond, ilizibile pentru cine le primea.

**Text duplicat.** Un câmp care spunea același lucru ca afirmația structurată de alături — două surse ale aceleiași fraze.

Și, în nomenclatură: trei etichete de coduri de indemnizație greșite față de sursa oficială, două inversate între ele. Reformulări făcute de cineva care credea că scrie text.

---

# ANEXĂ C — DE CE PARTEA B

P1–P13 asigură că **producem cifra corectă**. P14–P20 asigură că **o putem apăra**.

Distincția contează fiindcă cele două eșuează diferit. O eroare de calcul se vede: cifra e greșită, cineva o prinde. O lipsă de conformitate nu se vede până la control — și atunci nu se mai poate repara retroactiv.

| Fără | Consecința la control |
|---|---|
| P14 trasabilitate | „De unde iese suma?" nu are răspuns; contabilul reface manual munca aplicației |
| P15 inalterabilitate | evidența s-a schimbat după depunere; declarația nu mai corespunde nimănui |
| P16 responsabilitate | nu se știe cine a autorizat; răspunderea nu se poate stabili |
| P17 retenție | ori s-a șters ce trebuia păstrat, ori s-a păstrat ce trebuia șters |
| P18 retroactivitate | declarații depuse au devenit incorecte și nimeni nu știe care |
| P19 stare externă | depunere dublă, sau termen ratat |
| P20 proveniență | o presupunere a devenit fapt și a intrat într-o declarație |

Niciunul dintre acestea nu e o eroare de calcul. Toate sunt motive pentru care o aplicație corectă matematic poate fi neconformă legal.

**Consecința comercială**, care e aceeași cu cea juridică: dacă un contabil nu poate răspunde cu aplicația la un control, o va dubla cu evidența lui paralelă — și atunci produsul nu i-a economisit munca, i-a adăugat una.
