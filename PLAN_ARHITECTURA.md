# ARHITECTURA iConta — PLAN NORMATIV

**Versiunea 14 — ultima înainte de confruntare.** Corectează P24 (revizuirea se face intern, deliberat, nu de un specialist din afară) și adaugă la Partea 00 **angajamentul de răspuns în 48 de ore** și ce cere el de la arhitectură.

**Corecție 22.08.2026 — v14.1.** Din Partea 0 a fost **scoasă** limita declarată „accesul la sursa
externă". Nu era o limită: portalul răspunde cu antet de browser, iar căutarea se face prin formularul
lui. În locul ei s-a scris ce s-a aflat, plus consecința — pragurile de reverificare sunt realiste, nu
optimiste. **Nu e o extindere a planului**, e o presupunere falsificată de o probă, scoasă prin decizie
scrisă, cum cere Partea VII: *„Dacă un principiu se dovedește greșit, se schimbă documentul — prin
decizie scrisă, cu motiv, nu prin adaptare tăcută."*

Versiunea 13 adăugase **Partea 00: ce face sistemul** — fără de care nu există criteriu de proporționalitate — plus **P24, P25, P26**.

**De aici nu se mai adaugă.** Planul a crescut de la 10 principii la 26 într-o singură zi. Fiecare e justificat, dar de la un punct principiul marginal costă mai mult decât apără, iar sistemul de control devine el însuși ceva de întreținut. Ce urmează e confruntarea, nu completarea.

Versiunea 10 adăugase **P21 — norma știe ce depinde de ea**: legătura dintre articol și tot ce îl implementează, navigabilă în ambele sensuri. Fără ea, P18 cere ceva ce nu se poate face.

Versiunea 9 adăugase: validatorul e o constrângere, nu o sursă alternativă · întâi se modifică planul, apoi se conformează codul.
Versiunea 8 completase etapa temeiului: „nu înțeleg" ca stare legitimă și cererea specifică · verificarea pe articol, nu pe act · ierarhia surselor · absența temeiului ca rezultat declarat · traducerea text→formulă, ca limită.

Acest document spune **cum trebuie să fie**, nu cum este. Nu descrie codul existent și nu s-a scris citindu-l.

---

# PARTEA 00 — CE FACE SISTEMUL

Douăzeci și șase de principii spun ce n-are voie. Niciunul nu spunea ce e. Fără asta nu există criteriu de proporționalitate: nu se poate spune „constrângerea asta e prea scumpă pentru ce apără", fiindcă nu e scris ce apără.

### Ce ia

**Faptele economice ale unei firme**, din patru feluri de surse, cu certitudini diferite: facturi electronice primite de la autoritate · documente încărcate de om · extrase și fișiere importate · date introduse direct.

**Normele fiscale și contabile** în vigoare la data fiecărei operațiuni.

**Deciziile omului** acolo unde norma nu determină rezultatul.

### Ce produce

**Evidența contabilă** a firmei, ținută pe perioade.

**Artefactele pe care legea le cere:** registre obligatorii, situații financiare, declarații fiscale — fiecare în forma cerută și validat cu instrumentul oficial, unde există.

**Dovada că fiecare cifră e corectă:** lanțul până la documentul care o justifică, și temeiul normativ pe care stă.

### Pentru cine

**Cabinetul de contabilitate**, care ține evidența mai multor firme și răspunde juridic pentru fiecare.

Nu pentru firma care își ține singură contabilitatea, nu pentru inspector, nu pentru salariat — deși toți trei ating rezultatul.

### Ce înseamnă că a reușit

**Contabilul depune declarațiile din aplicație, fără să le recalculeze în altă parte.**

Asta cuprinde tot restul: dacă recalculează, ori nu are încredere în cifră (P22), ori nu poate dovedi de unde vine (P14), ori a fost surprins de ceva ce nu i s-a cerut la timp (P23). Fiecare principiu din documentul ăsta apără o parte din propoziția aia.

### Ce nu face

Nu ține locul contabilului la judecata profesională. Nu decide încadrări acolo unde legea lasă loc — le cere. Nu verifică dacă premisele introduse sunt adevărate; poate doar semnala improbabilul.

### Angajamentul față de cabinet

**Răspuns în 48 de ore la orice solicitare** — ce e, cât durează, când se face.

**Livrare în 48 de ore** pentru clasa de cereri care se pot livra atât de repede: o declarație în plus, un raport, o corelare nouă, un format de import.

Distincția e ce face promisiunea credibilă. „Orice solicitare rezolvată în 48 de ore" se încalcă la prima cerere care înseamnă un flux rescris — iar o promisiune încălcată o dată nu mai valorează nimic. Un cabinet care primește în două zile *„e o zi de muncă, o fac joi"* e mai bine servit decât unul care primește tăcere.

**Ce cere angajamentul de la arhitectură.** Livrarea în două zile e posibilă doar dacă drumul e scurt, iar el e scurt doar dacă:

- **nomenclatoarele, structurile și convențiile sunt în registru** (P1) — altfel fiecare cerere le re-declară;
- **temeiul se verifică pe o secvență cunoscută** (Partea 0) — altfel verificarea singură ia zilele;
- **norma știe ce depinde de ea** (P21) — altfel nu se știe ce se atinge;
- **calculul e separat de prezentare** (P3) — altfel un raport nou cere atins motorul.

Fără ele, două zile devin două săptămâni. **Angajamentul nu e politică comercială — e testul practic al arhitecturii.**

### Criteriul de proporționalitate

Un principiu sau o interdicție se justifică dacă absența lui poate face contabilul să nu depună din aplicație, sau să nu poată apăra ce a depus.

Ce nu trece testul ăsta e prudență, nu arhitectură — și costă mai mult decât apără.

---

# PARTEA 0 — SECVENȚA OBLIGATORIE

Înaintea oricărei reguli de structură, o regulă de procedură. Se aplică **de fiecare dată** când se scrie sau se modifică ceva ce depinde de o normă.

```
1.  AM ACTUL, ȘI ÎNȚELEG CE SPUNE DESPRE CAZUL MEU?
       nu-l am              → îl aduc
       nu-l pot aduce       → CER, numind exact ce-mi trebuie
       îl am, nu-l înțeleg  → CER, spunând ce am citit, ce am înțeles,
                              și unde se oprește înțelegerea
       nu există temei      → declar „am căutat în X, Y, Z și nu am găsit",
                              și cer decizia
       îl am și îl înțeleg  → mai departe

2.  ARTICOLUL E ÎN VIGOARE ÎN FORMA ASTA, LA DATA OPERAȚIUNII?
       neverificat / expirat → verific la sursă externă, notez data
       modificat             → folosesc forma valabilă la acea dată
       abrogat               → folosesc succesorul; actul vechi rămâne
       în vigoare            → mai departe

3.  ARTICOLUL CHIAR SPUNE CE ÎI ATRIBUI?
       citez VERBATIM, iar citatul trebuie să conțină valoarea sau regula
       pe care o justifică
       nu o conține → nu e temeiul potrivit; îl caut pe cel corect

4.  DACĂ AM MAI MULTE SURSE, SE CONTRAZIC?
       da → NU aleg pe cea mai comodă. Se ridică la decizie.
       nu → mai departe

5.  TEXTUL DETERMINĂ REZULTATUL?
       nu → MĂ OPRESC și cer decizia
       da → mai departe

6.  APLIC
```

---

### Pasul 1 — „nu înțeleg" e o stare legitimă

Cea mai periculoasă situație nu e „nu găsesc actul". Aia e evidentă și se rezolvă. E **„am actul, l-am citit, dar nu-mi spune ce fac în cazul ăsta"** — care nu se manifestă în niciun fel. Se produce ceva plauzibil și se merge mai departe. Plauzibil nu e corect.

Toate cele trei erori din Anexa B au trecut prin punctul ăsta: textul a fost citit, n-a fost înțeles complet, și în loc de o întrebare a ieșit o interpretare.

**Cererea trebuie să fie specifică.** Nu „am nevoie de ajutor cu D112", ci: *„am OUG 158/2005 art. 10; nu-mi spune cum se tratează lunile fără venituri din cele 6 — îmi trebuie normele de aplicare, sau o decizie."*

Trei elemente obligatorii în orice cerere: **ce am citit** · **ce am înțeles** · **unde se oprește înțelegerea**.

**Când nu există temei**, asta e un rezultat, nu un eșec. Unele valori vin din practica autorității, din documentația validatorului, sau din nicăieri. Se declară: „am căutat în X, Y, Z și nu am găsit temei" — și se cere decizia. Ce nu se face: să se blocheze la infinit, sau să se treacă tăcut.

### Pasul 2 — se verifică articolul, nu actul

Un act poate fi în vigoare permanent și modificat de câteva ori pe an. Codul fiscal e exemplul: verificarea „mai e în vigoare?" trece mereu, iar articolul 77 poate fi rescris de o ordonanță pe care n-o ai.

**Unitatea de verificare e articolul la o dată**, nu actul.

Un act nu-și anunță propria modificare, la fel cum nu-și anunță abrogarea: ambele sunt scrise în actul modificator. Absența lui din corpus nu dovedește că nu există.

Consecința reală: OUG 89/2025 a modificat art. III din OUG 156/2024, iar art. LXX a fost abrogat de OUG 29/2026. Actul de bază e în vigoare; două articole din el, nu.

### Pasul 3 — actul chiar spune ce îi atribui

Un act corect și în vigoare poate fi **temeiul greșit**. Se întâmplă când valoarea a fost fixată de un act modificator, iar citarea trimite la actul de bază.

Mecanismul: **citatul verbatim trebuie să conțină valoarea sau regula pe care o justifică.** Dacă o cotă de 16% e sprijinită pe un citat în care nu apare 16, citarea e falsă — indiferent cât de corect e actul.

### Pasul 4 — ierarhia surselor

Când două surse spun altceva, nivelul decide **ce se întâmplă**, nu **cine câștigă**:

| Nivel | Ce e |
|---|---|
| 1 | Monitorul Oficial — textul legii |
| 2 | Interpretarea oficială a autorității — norme, instrucțiuni, structuri publicate |
| 3 | Practica validatorului — ce acceptă efectiv instrumentul |

**Regula: o sursă de nivel inferior nu poate contrazice una superioară fără să se ridice la decizie** — inclusiv, și mai ales, când e mai comodă.

Nu se alege tăcut nici legea, nici validatorul. Divergența dintre niveluri e chiar semnalul că cineva trebuie să decidă.

**Ce înseamnă asta pentru validator, explicit.** Validatorul nu e o sursă alternativă de adevăr. Ce acceptă sau respinge el e o **constrângere**, nu o normă.

Nomenclatorul se ia din sursa normativă. Dacă validatorul acceptă mai puțin decât prevede norma, sau altceva, aceea e o constrângere a arbitrului — se declară ca dezacord marcat, nu se rescrie nomenclatorul după ea.

Cazul care a produs regula: nomenclatorul oficial al codurilor de indemnizație are douăzeci de poziții; enumerarea din structura tehnică publicată are cincisprezece; validatorul acceptă coduri pe care structura le respinge. **Sursa e nomenclatorul.** Structura tehnică e o constrângere mai îngustă decât realitatea, iar un nomenclator ancorat pe ea blochează depunerea unei declarații legale.

### Cele cinci verificări sunt diferite, și fiecare a eșuat separat

| Verificare | Ce întreabă | Cum a eșuat |
|---|---|---|
| **1** | am actul, și înțeleg? | „Încadrat cu salariul minim" — citit, neînțeles complet, interpretat în loc de întrebat |
| **2** | articolul e în vigoare în forma asta? | OPANAF 394/2017, citat în nouă locuri, abrogat de 705/2020. HG 685/1999, abrogat de HG 773/2019 |
| **3** | articolul chiar conține ce îi atribui? | Trei citări false: facilitatea de 300 lei, cota de dividende, pragul mijloacelor fixe — pe acte corecte și în vigoare |
| **4** | sursele se contrazic? | Podeaua part-time: legea zice una, structura publicată de autoritate zice alta. S-a ales în cod |
| **5** | textul determină rezultatul? | Aceeași instanță, cealaltă față: alegerea n-a fost cerută |

Până la versiunea asta, doar prima jumătate din prima era regulă.

### Pragul de reverificare a vigorii

O dată de verificare fără termen devine formalitate: un articol verificat acum doi ani poartă o dată, deci trece — și poate fi rescris de un an.

| Categorie | Se reverifică |
|---|---|
| articole care fixează valori curente — cote, praguri, salariu minim, facilități | la fiecare utilizare într-o valoare nouă, și cel puțin **trimestrial** |
| ordine care aprobă structuri de declarații | **înainte de fiecare perioadă de raportare** în care se folosesc |
| articole de fond stabile — Codul fiscal, legea contabilității | **semestrial**, plus la orice modificare anunțată |
| articole care reglementează perioade închise | **niciodată** — perioada e închisă, forma de atunci e cea care contează |

Ultimul rând e important: un articol abrogat azi rămâne temeiul corect pentru o perioadă în care era în vigoare. Reverificarea privește doar ce se folosește pentru perioade curente.

### Ce e obligatoriu și ce e verificabil

Secvența e comportament, deci nu se poate garda integral. Ce se poate garda e **urma ei**:

- o valoare fără temei, sau fără declarația „nu există temei", nu intră;
- o valoare cu articol fără dată de verificare, sau cu verificare expirată, nu intră;
- o valoare al cărei citat verbatim **nu conține valoarea** nu intră;
- o valoare pe un articol abrogat sau modificat, fără succesor citat, nu intră;
- o valoare care are surse de niveluri diferite în dezacord, fără decizie, nu intră.

Asta nu dovedește că secvența a fost parcursă. Dovedește că nu se poate pretinde că a fost.

### O limită declarată, și o presupunere care s-a dovedit falsă

**Presupunerea, corectată la 22.08.2026: accesul la sursa externă NU e o limită.** Până atunci planul
spunea că pasul 2 depinde de un portal legislativ care ar putea bloca accesul automat, deci verificarea
vigorii ar deveni muncă a omului. **Nu era blocat.** Portalul Legislativ (`legislatie.just.ro`) răspunde
**403** unui client care nu se prezintă și **200** cu un antet de browser obișnuit. Căutarea se face
**prin formularul lui** — POST cu tokenul antiforgery al paginii, tip de document + număr + an — nu
ghicind identificatori. Iar pentru actele mari, forma consolidată la zi e **un document separat**, legat
din pagina actului de bază: pagina de bază conține doar cuprinsul, deci un act mare citit de acolo pare
gol fără să fie.

Deci verificarea vigorii pe articol e **mecanică**: `scripts/vigoare_articol.py` citește articolul din
forma consolidată la zi și raportează starea lui plus marcajele de modificare, iar
`scripts/portal_legislativ.py` aduce actul în corpus cu amprentă. Amândouă au fost construite și
folosite în ziua în care presupunerea a căzut — 19 articole verificate, patru acte aduse.

**Ce NU face instrumentul, declarat:** spune că articolul e în vigoare în forma asta, nu că **spune** ce
îi atribuim. Aia e verificarea 3, și rămâne o citire.

**Consecința: pragurile de reverificare sunt realiste, nu optimiste.** Argumentul vechi — „un termen
imposibil produce câmpuri completate formal, ceea ce e mai rău decât absența lor" — rămâne adevărat ca
principiu, dar nu se mai aplică aici: trimestrial pentru valorile curente și semestrial pentru
articolele de fond sunt termene pe care le ține un instrument, nu o corvoadă care se bifează.

**Limita care rămâne: traducerea din text în formulă nu se verifică mecanic.** Citatul conține „deducerea scade cu 0,5 puncte la fiecare 50 de lei"; codul conține o expresie. Că a doua îl implementează corect pe primul **nu verifică nimic din tot ce e mai sus**. Rămâne judecată umană, iar arbitrul o acoperă doar unde validează.

---

# PARTEA I — PRINCIPIILE

Douăzeci și șase de reguli. Primele treisprezece privesc **corectitudinea a ceea ce producem**; ultimele treisprezece, **ce se cere de la noi când suntem verificați** — de o autoritate, de contabilul care lucrează cu cifra, și de timp.

---

## A. CORECTITUDINEA

### P1 — Un adevăr, un loc

Orice valoare, formulă, nomenclator sau regulă de eligibilitate există **într-un singur loc** și se citește de acolo.

**Un temei lângă o valoare nu e registrul.** O valoare care poartă actul și articolul, dar trăiește într-un modul de calcul, e tot în afara registrului. Sursa se dovedește prin locul unde stă, nu prin adnotarea de lângă ea.

### P2 — Timpul e parametru, nu context

Orice adevăr fiscal se cere **pe o dată**. Nicio funcție de calcul nu citește data curentă.

Consecință: recalcularea unei perioade trecute produce exact același rezultat ca prima calculare.

### P3 — Cine calculează nu afișează, cine afișează nu calculează

Un număr arătat unui om provine dintr-un singur calcul. Stratul de prezentare primește rezultate, nu ingrediente.

Nicio regulă fiscală nu se implementează în interfață. Nici măcar o comparație, nici măcar un prag.

### P4 — Documentul emis e fapt; recalculul e a doua părere

Ce a fost dat unui om sau depus la o autoritate se **îngheață cu amprentă**. Un recalcul care diferă nu corectează documentul: produce o **contradicție**, care se arată.

Corecția e un document nou, care îl referă pe primul.

### P5 — O afirmație poartă domeniul și sursele

Nimic nu se afirmă despre o firmă fără să spună **la ce se referă** și **pe ce s-a uitat**.

### P6 — Verdele afirmă; ce nu s-a verificat se spune

Absența unei contradicții nu e o verificare.

Ierarhia: **necunoscut domină favorabil**; problema domină necunoscutul.

### P7 — Verificarea e independentă prin construcție și prin disciplină

Calea a doua nu importă calea întâi, nu-i copiază constantele, nu-i reproduce formulele.

Când cele două nu coincid, întrebarea se duce la arbitru. **Nu se aliniază una la cealaltă.**

### P8 — Temeiul se verifică pe cinci axe, iar niciuna nu le acoperă pe celelalte

**Nicio valoare fiscală nu intră în cod fără temei verificat la sursa oficială. Memoria nu e sursă.**

Cele cinci verificări sunt detaliate în Partea 0. Pe scurt:

1. **Am actul și îl înțeleg?** „Nu înțeleg" e o stare legitimă și duce la o cerere specifică, nu la o presupunere.
2. **Articolul e în vigoare în forma asta, la data operațiunii?** Nu se răspunde din corpus.
3. **Articolul chiar conține ce îi atribui?** Prin citat verbatim care conține valoarea.
4. **Sursele se contrazic?** O sursă inferioară nu poate contrazice una superioară fără decizie.
5. **Textul determină rezultatul?** Dacă nu — P11.

**Fiecare articol folosit poartă:** data ultimei verificări · starea la acea dată · succesorul, dacă e cazul · categoria de reverificare.

**Arbitrul e extern.** Când legea, structura publicată de autoritate și validatorul nu coincid, situația nu se tranșează la scriere.

### P9 — Perimetrul e declarat

Ce nu e acoperit se scrie. O declarație de perimetru devenită neadevărată se aprinde.

### P10 — Regula scrisă e regulă păzită

Fiecare principiu are un mecanism care îl face imposibil de încălcat, sau e declarat explicit negardabil, cu motivul scris.

### P11 — Unde textul nu determină rezultatul, nu se alege — se cere decizia

> Când textul determină rezultatul, se aplică.
> Când nu-l determină, **se oprește și se cere decizia**.

Nu se alege și se marchează. **Alegerea nu e a celui care scrie codul.**

**Testul practic:** ar citi un contabil competent același text și ar ajunge la alt rezultat?

**Pragul:** se oprește când alegerea schimbă o cifră care **ajunge la o autoritate sau la un om**. O alegere care afectează doar o reprezentare internă se face și se notează.

**Ce se consemnează, când decizia s-a luat:** textul care a lăsat loc, citat · varianta aleasă · **varianta respinsă, numită** · motivul · cine a decis și când.

### P12 — Datele unei firme nu ies din firma ei

Izolare prin construcție, nu prin filtru scris de mână. O interogare fără contextul firmei **eșuează**.

Drepturile se verifică în interogare, nu doar în interfață.

### P13 — Textul nu e purtător de decizie

| Ce e | Ce pare | Unde stă de fapt |
|---|---|---|
| **Nomenclatura oficială** | text | intrare în registru, cu temei |
| **Afirmația** | frază | structură: fel, domeniu, surse, remediu |
| **Datele omului** | text | text autentic, dar al lui |

**Ce e text cu adevărat:** ce e fix în interfață. Acela primește **cheie** și loc unic.

**Testul:** dacă rescrii o frază și se schimbă comportamentul, textul acela nu era text.

Eticheta se **derivă din starea efectivă**, nu se alege de cine randează.

---

## B. CONFORMITATEA

### P14 — Orice cifră se desface până la documentul care o justifică

```
poziție din declarație ↔ înregistrare contabilă ↔ document primar ↔ sursa lui
```

Fiecare verigă navigabilă la cerere, fără recalculare · lanțul se păstrează pentru documentele **emise** · suma pozițiilor desfăcute dă exact valoarea declarată.

### P15 — După închiderea unei perioade, nu se modifică; se stornează

Închiderea e act deliberat, cu autor · editarea devine **imposibilă** · corectarea prin înregistrare nouă · redeschiderea e act consemnat, cu motiv · numerotarea nu are goluri și nu se reia.

### P16 — Cine a autorizat, se știe

Orice act cu efect juridic extern are autor identificat. Autorizarea e distinctă de execuție. Urma nu se poate șterge și nu se poate edita.

### P17 — Ce se păstrează, cât și pe ce temei

Fiecare categorie are termen și temei. La o cerere de ștergere, ce nu poate fi șters se **numește**, cu temeiul.

### P18 — Legea se schimbă retroactiv, iar aplicația știe pe cine

Se determină perioadele afectate · documentele emise sub regula veche · fiecare devine **contradicție** vizibilă · listă de rectificative cu diferența · decizia e a omului.

Regula veche nu se șterge din registru.

**P18 depinde de P21.** Fără legătura de la articol la ce depinde de el, se pot determina perioadele afectate, dar nu și codul care trebuie schimbat.

### P19 — Cu exteriorul, „nu știu" e o stare legitimă

Stările: **nepornită, în curs, confirmată, respinsă, nelămurită**. „Nelămurită" nu se convertește singură. Identificatorul de la autoritate se păstrează.

### P20 — Proveniența se păstrează, iar o presupunere nu devine fapt

Fiecare valoare din afară poartă **sursa** și **gradul de certitudine**. Devine sigură prin **confirmare explicită**.

### P21 — Norma știe ce depinde de ea

P14 leagă cifra de documentul care o justifică. P21 leagă **regula de norma care o impune**. Sunt două lanțuri diferite: primul merge spre datele firmei, al doilea spre lege.

**Orice element care implementează o normă poartă articolul pe care îl implementează** — nu doar valorile, ci și:

- formulele de calcul;
- condițiile de eligibilitate;
- structurile de declarație și maparea câmpurilor;
- nomenclatoarele și denumirile lor;
- termenele și regulile de decalare;
- regulile de validare;
- convențiile de calcul.

**Legătura e navigabilă în ambele sensuri.** De la o implementare se poate afla temeiul — asta există parțial azi, pentru valori. De la un articol se poate întreba **ce depinde de tine** — asta nu există deloc, și e sensul care contează la modificare.

**La o modificare de articol, lista dependenților se generează, nu se reconstituie.** Nu se caută prin memorie, nu se face grep, nu se descoperă din întâmplare.

**Fără P21, P18 nu se poate executa.** P18 cere ca la o schimbare retroactivă să se determine documentele afectate. Aplicația poate ști ce *perioade* sunt afectate — dar nu ce *cod* trebuie schimbat. Un articol modificat lasă în urmă implementări care nu se pot găsi decât căutându-le.

Consecința reală: OPANAF 394/2017 era citat în nouă locuri. Toate nouă au fost găsite abia când cineva a căutat anume, după ce abrogarea a ieșit la iveală din întâmplare. Cu legătura inversă, întrebarea „ce depinde de 394/2017?" ar fi avut răspuns imediat.

### P22 — Cifra se poate verifica de un om, pe ecran

P14 face cifra apărabilă la un control. P21 o leagă de normă. **P22 o face verificabilă de contabilul care lucrează cu ea**, în ziua în care o produce.

Distincția e practică: un contabil care nu poate verifica o cifră are două opțiuni — să aibă încredere, sau s-o refacă în altă parte. Amândouă sunt eșecuri ale produsului. A doua e mai frecventă, iar atunci aplicația nu i-a economisit munca, i-a adăugat una.

Trei lucruri, toate la cerere, niciunul îngrămădit pe ecran:

**1. Din ce se compune cifra.** Nu doar rezultatul, ci pașii: brutul, baza de contribuții, fiecare contribuție, deducerea, baza de impozit. Contabilul cunoaște formula — vrea să vadă **unde diferă**, nu să recalculeze de la zero.

**2. Ce nu s-a aplicat, și de ce.** Aici greșesc oamenii: nu la ce s-a calculat greșit, ci la ce nu s-a acordat deloc. O deducere suplimentară neacordată, o facilitate pierdută, o scutire neaplicată — toate sunt invizibile dacă ecranul arată doar ce s-a aplicat.

Fiecare element care **putea** interveni și n-a intervenit se arată, cu motivul și cu temeiul: *„facilitate 200 lei — neacordată: brutul depășește salariul minim (OUG 156/2024 art. LXVI)"*.

O absență nemotivată nu se poate contesta, fiindcă nu se vede.

**3. Ce s-a schimbat față de perioada anterioară.** Un contabil nu verifică o lună izolat; se uită la ea știind luna precedentă. Dacă un net diferă, prima întrebare e de ce.

Aplicația are ambele perioade. Poate spune: *brutul e neschimbat; deducerea a scăzut cu 130 de lei, fiindcă salariul minim s-a modificat de la 1 iulie.*

E cel mai puternic instrument de verificare din cele trei — mai puternic decât temeiul afișat — fiindcă atrage atenția exact acolo unde ceva s-a mișcat.

**Temeiul însoțește fiecare dintre cele trei.** P21 leagă regula de articol în cod; P22 cere ca legătura să **iasă la suprafață**. O legătură care trăiește doar în cod nu ajută pe cine verifică.

**Ce nu înseamnă P22:** că totul se afișează mereu. Ecranul rămâne curat; explicația se cere. Diferența dintre un produs verificabil și unul obositor e că al doilea arată tot, tot timpul.

### P23 — Ce lipsește se cere la timp; ce nu s-a cerut e vina aplicației

Aplicația nu răspunde de datele pe care nu le-a primit. Răspunde de a fi cerut ce-i trebuia, **când încă era util**.

Trei situații, cu răspundere diferită:

| Situația | A cui e |
|---|---|
| datele lipsesc, **aplicația a cerut** | a omului — a fost întrebat și n-a completat |
| datele lipsesc, **aplicația n-a cerut** | **a aplicației** — cea mai gravă formă, fiindcă rezultatul pare complet |
| artefactul nu se poate produce **indiferent de date** | a aplicației — e o lipsă a ei, nu a datelor |

**A doua e cea periculoasă.** Un rezultat produs peste date lipsă, fără ca cineva să fi fost întrebat, arată identic cu unul corect. „Nu se datorează" pe o firmă cu operațiuni neînregistrate e chiar cazul: aplicația a răspuns la ce avea, nu la ce trebuia să aibă.

**Cererea are un moment.** O lipsă descoperită la generare, în ziua depunerii, e o lipsă semnalată prea târziu — chiar dacă e semnalată corect. Ce lipsește se cere **când datele mai pot fi obținute**: la introducere, la închiderea perioadei, la prima verificare care le atinge.

**Ce trebuie să spună cererea:** ce lipsește · de ce e necesar, cu temeiul · unde se completează · ce nu se poate face fără el.

**Consecința pentru orice verdict:** un rezultat calculat peste date incomplete nu e „gata", e „gata cu ce am avut". Distincția intră în rezultat, nu într-o notă alăturată — e P6 aplicat la date, nu la verificări.

### P24 — O interpretare care ajunge într-o cifră depusă se revizuiește deliberat

O decizie luată, consemnată impecabil, poate fi greșită. Nimic din lanțul automat nu o poate contrazice: nu sursa, fiindcă textul e chiar cel ambiguu; nu validatorul, fiindcă el verifică structura, nu încadrarea; nu testele, fiindcă ele verifică ce s-a decis.

Deci o decizie de interpretare are **două stări**:

| stare | ce înseamnă |
|---|---|
| **luată** | s-a ales, cu varianta respinsă numită și motivul scris |
| **revizuită** | alegerea a fost recitită deliberat, ca listă, separat de momentul în care s-a luat |

**Revizuirea nu e obligatorie pentru toate.** E obligatorie pentru cele care ajung într-o cifră depusă la o autoritate sau dată unui om — aceeași treaptă de prioritate ca peste tot.

**De ce e o operațiune separată, nu o a doua părere pe loc.** O alegere făcută în timpul construcției poartă contextul ei: ce era la îndemână, ce nu bloca, ce părea evident atunci. Recitită ca listă, ruptă de context, se judecă altfel — și acolo ies alegerile care păreau evidente și nu erau.

Ce se citește: *legea spune X · am înțeles Y · alternativa era Z · am ales Y fiindcă…* Nu codul, nu ecranul — lista alegerilor.

O decizie care ajunge într-o cifră depusă și n-a fost revizuită se declară ca atare. Nu se ascunde în spatele faptului că e bine documentată.

### P25 — Evidența supraviețuiește, iar restaurarea se poate dovedi

Nicăieri altundeva nu scrie că datele nu se pierd. P17 spune cât se păstrează — nu că rezistă.

Pentru un cabinet care ține evidența a zeci de firme, pierderea lor nu e un incident tehnic: e răspunderea lui juridică, față de clienți și față de autoritate. Un termen de păstrare de zece ani nu înseamnă nimic dacă datele dispar în al treilea.

**Ce se cere:**

- **copii de siguranță**, cu ritm și retenție declarate, nu presupuse;
- **restaurarea probată**, nu doar posibilă — o copie din care nu s-a restaurat niciodată e o presupunere;
- **dovada că ce s-a restaurat e ce era** — prin amprentă, nu prin comparare la ochi. Fără ea, o restaurare e o afirmație;
- **izolarea copiilor** față de ce se poate strica: o copie ștearsă odată cu originalul nu e copie.

**Documentele emise au un regim mai strict.** Ele sunt fapte, nu stări; pierderea unui exemplar emis nu se repară prin regenerare, fiindcă regenerarea produce alt document.

### P26 — Clientul își poate lua evidența, oricând

Firma e obligată prin lege să-și păstreze documentele ani după ce relația cu cabinetul s-a încheiat. Cabinetul, la fel, față de clienții lui.

Deci portabilitatea nu e o curtoazie comercială — e o precondiție ca produsul să poată fi folosit fără să încalce o obligație.

**Ce se cere:**

- **exportul complet**, la cererea titularului, fără intervenția noastră și fără negociere;
- **într-o formă utilizabilă** — documentele în formatul în care au fost emise, evidența într-un format deschis, nu într-unul pe care doar noi îl citim;
- **cu lanțul păstrat** — un export care rupe legătura dintre declarație și documentele justificative transferă date, nu evidență;
- **la orice nivel** — o firmă care pleacă de la un cabinet; un cabinet care pleacă de la noi.

**Efectul secundar contează la fel de mult:** un produs din care nu poți ieși e un produs de care te temi. Portabilitatea e ce face posibilă încrederea, nu ce o slăbește.

### Două reguli care traversează

**Omul are ultimul cuvânt, iar dezacordul lui se înregistrează.**

**Două scrieri simultane nu se pierd tăcut.**

---

# PARTEA II — STRATURILE

```
  7  PREZENTARE        randează, nu decide
  6  ORCHESTRARE       rutare, flux, drepturi, coadă, perioade închise
  5  DOCUMENTE         artefacte emise, înghețate, cu lanț și autor
  4  EVIDENȚA          ce s-a întâmplat, per firmă, cu proveniență
  3  CALCUL            funcții pure: intrări + dată → rezultat
  2  REGISTRUL         adevăruri, decizii de interpretare, reguli de produs
  1  TEMEIURI          corpusul, cu vigoarea verificată pe articol

  ═  VERIFICAREA       traversează, NUMAI CITEȘTE
  ═  URMA              traversează, se scrie o dată, nu se editează
```

Dependența curge **într-o singură direcție**.

### 1 — Temeiuri

Corpusul de acte normative și documentația validatorului.

**Fiecare act poartă:** textul verbatim · amprenta textului, ca să se poată dovedi că n-a fost modificat după aducere · data aducerii.

**Fiecare articol folosit poartă:** data verificării vigorii · starea la acea dată (în vigoare · modificat · abrogat) · succesorul · categoria de reverificare.

Unitatea de verificare e **articolul**, nu actul: un act poate fi în vigoare permanent și modificat de câteva ori pe an.

**Textul e imuabil.** Actele abrogate **rămân în corpus**, cu succesorul indicat.

### 2 — Registrul

Tot ce e normativ. Se interoghează pe dată.

### 3 — Calcul

Funcții pure. Nu citesc baza de date, nu scriu, nu cunosc firma, nu cunosc data curentă. Rezultatul poartă **deciziile de interpretare** și **gradul de certitudine** al intrărilor.

### 4 — Evidența

Fiecare valoare poartă **proveniența**. Izolarea per firmă e proprietate a stratului. Perioadele închise sunt imposibil de modificat de aici.

### 5 — Documente

Numărul exemplarului, momentul, autorul autorizării, amprenta, lanțul, starea trimiterii. Append-only.

### 6 — Orchestrare

Decide **cine are voie și când**, niciodată **cât e**.

### 7 — Prezentare

Singurul strat în care există text. Nu compune sens.

### Verificarea

Nu scrie, nu emite, nu corectează. Nu-și ia dovada din proză.

### Urma

Se scrie o dată. Singura excepție de la „o citire nu scrie": o citire de date personale poate lăsa urma faptului că a avut loc.

---

# PARTEA III — REGISTRUL

### Trei feluri de intrări, care nu se amestecă

| Fel | Ce e | Cine îl stabilește | Se poate contesta? |
|---|---|---|---|
| **Temei** | legea spune direct | nimeni — se verifică la sursă | nu |
| **Decizie de interpretare** | legea lasă loc; s-a cerut și s-a luat o decizie | Costin | da, oricând |
| **Regulă de produs** | legea nu spune nimic | Costin | da, oricând |

Amestecarea e interzisă, fiindcă se **revizuiesc diferit**.

Cele două de jos au **autor uman și dată**. Nicio intrare din aceste categorii nu apare fără să fi fost cerută.

### Ce poartă un TEMEI

Valoarea, formula sau denumirea oficială · **articolul din corpus, cu vigoarea verificată la data operațiunii** · nivelul sursei · valabil de la, cu „valabil până" derivat din succesor · **citatul verbatim, care conține valoarea justificată**.

### Ce poartă o DECIZIE DE INTERPRETARE

Textul care a lăsat loc, citat · de ce lasă loc · varianta aleasă · **varianta respinsă, numită** · motivul · cine a decis și când · ce spune arbitrul · dezacordul marcat ca deschis, dacă arbitrul contrazice.

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

**Formule** spun *ce* se calculează; **convenții** spun *cum*.

Lista e închisă.

### Reguli de acces

- Nimeni nu scrie o valoare din aceste categorii în afara registrului. **Un temei atașat lângă valoare nu ține loc de registru.**
- Se interoghează **pe data operațiunii**. O interogare fără dată e o eroare, nu un default.
- O valoare fără temei, decizie sau regulă de produs nu poate intra.
- **O valoare nu intră dacă articolul n-are vigoarea verificată**, dacă verificarea a expirat, sau dacă e abrogat ori modificat fără succesor citat.
- **O valoare nu intră dacă citatul verbatim nu conține valoarea pe care o justifică.**
- **O valoare nu intră dacă are surse de niveluri diferite în dezacord, fără decizie.**
- **O valoare fără temei intră doar cu declarația „am căutat în X, Y, Z și nu am găsit", plus decizie.**
- Actele abrogate nu se șterg: primesc succesor și rămân interogabile pentru perioadele trecute.
- O decizie contrazisă de arbitru rămâne marcată ca dezacord deschis.
- **Denumirile oficiale sunt intrări cu temei**, nu șiruri în cod.
- **O intrare din AFARA unui nomenclator de registru se REFUZĂ, nu se semnalează.** *(Adăugat 26.08.2026, prin decizia lui Costin, după R54.)* Planul spunea deja că nimeni nu scrie o valoare din aceste categorii în afara registrului, dar nu spunea ce se face cu o valoare care **vine din afară** și nu se regăsește în el. Motivul deciziei, scris: *„o notă cu cont inexistent nu e evidență, e un rând care arată ca evidență. Nu se poate depune, nu se poate desface la control, iar contabilul află abia când generează ceva.”* Argumentul contrar — că refuzul blochează pe cine lucrează repede — se rezolvă altfel: cine vrea o intrare nouă o creează în nomenclator, **și aia e chiar decizia pe care trebuie s-o ia conștient**. **Refuzul numește intrarea și spune unde se creează** — nu „valoare invalidă”, ci *„contul 7O7 nu există în planul firmei; îl adaugi din Plan de conturi”*. Fără partea a doua, refuzul mută munca fără s-o îndrume.
- **O modificare cu efect retroactiv declanșează P18.**
- **Nicio decizie de interpretare nu intră fără să fi fost cerută.**

**O EXCEPȚIE DE ACCES SE SCRIE LOCAL PE RUTĂ, NICIODATĂ ÎN FUNCȚIA COMUNĂ** *(28.08.2026, după R83)*

`auth_api.schema_tenant` — poarta prin care trec **153** de rute din `main.py` *(măsurat pe
`5adb1d9`; erau 154 înainte ca activarea să iasă din mulțime — cifra se redatează, nu se copiază)* —
cere `activ = true`
pe toate trei ramurile de rol. Asta e **implicit și corect**: o firmă scoasă din portofoliul de lucru
n-are de ce să răspundă la cereri de conținut.

Golul, găsit pe 28.08.2026: planul **nu spunea nimic** despre ce înseamnă o firmă **inactivă** pentru
drepturile de acces, iar secțiunea de față era despre registrul de valori fiscale — cine poate scrie
o valoare și cu ce temei —, nu despre accesul unui om la o firmă. Consecința a fost un act imposibil:
`POST /tenants/{id}/activare` se apăra cu poarta comună, deci **reactivarea unei firme dezactivate
răspundea 404 întotdeauna** (R83).

**Regula, scrisă acum:**
- **implicit, orice rută trece prin poarta comună**, care cere firma **activă**;
- o rută al cărei act are sens **tocmai pe o firmă inactivă** — azi una singură, activarea — își
  scrie **propria verificare, local**, cu regula de **rol păstrată identică**; singurul lucru care
  diferă e `activ`;
- **funcția comună nu se modifică pentru o excepție.** Un parametru implicit pe o funcție de acces
  chemată din atâtea locuri e o poartă care se poate uita deschisă;
- **excepția are un singur apelant**, iar asta se păzește mecanic. A doua chemare o transformă într-o
  poartă paralelă — adică într-o schimbare a funcției comune, pe furiș.

*(Decizia lui Costin, varianta (a); gard: `core/test_activare_firma_inactiva.py`.)*

**CÂND E O EXCEPȚIE ȘI CÂND E O POARTĂ: regula, după R83 și R84** *(28.08.2026)*

Cele două restanțe s-au reparat în aceeași zi, cu forme **diferite**, iar diferența nu e de gust:

| câte rute | forma | de ce |
|---|---|---|
| **una** | verificare **locală pe rută** (R83: activarea) | e singura al cărei act are sens pe o firmă inactivă; o funcție privată cu **un** apelant se scoate fără să atingă nimic |
| **o clasă** | **poartă declarată** separată, cerută explicit (R84: `schema_tenant_citire`, 13 rute) | treisprezece verificări locale nu mai sunt o excepție, sunt cod duplicat pe care nimeni nu-l mai citește — iar a paisprezecea copie n-ar avea de ce să pice |
| **oricâte** | **NU** un parametru pe `schema_tenant` | un implicit pe o funcție de acces chemată din 153 de locuri e o poartă care se poate uita deschisă |

**Ce e obligatoriu în amândouă formele:**
- regula de **rol** rămâne **identică** cu a porții comune — singurul lucru care diferă e `activ`;
- apelanții se **numără mecanic**, iar numărul e pinat: un apelant în plus **cade poarta**, nu
  capătă acces tăcut (`core/test_activare_firma_inactiva.py`, `core/test_poarta_citire_istorica.py`);
- o poartă de **citire** nu se cere din acte de **scriere**. Pe două dintre cele 13 căi există și
  câte un `POST` — au rămas pe poarta comună. *O firmă scoasă din portofoliu se citește, nu se
  modifică*, iar asta e păzit, nu doar scris aici.

**ORICE FAPT ECONOMIC NOU CONSTRUIT PRODUCE NOTA CONTABILĂ AUTOMAT** *(29.08.2026, decizia R36)*

Regula, în formă normativă:

- **implicit, actul care construiește faptul economic scrie și nota.** Nu există un al doilea act
  („contabilizează") pe care omul să trebuiască să și-l amintească. Dacă faptul există în aplicație,
  evidența lui există odată cu el.
- **o rută manuală se acceptă numai cu declarație explicită**, scrisă **lângă cod** — în docstringul
  rutei sau al modulului —, nu doar în registru. Declarația spune **de ce** actul rămâne separat:
  fiindcă cere o **alegere** care nu se poate deriva (ce factură stinge o încasare), fiindcă e o
  **rulare de perioadă** fără act declanșator (amortizarea), sau fiindcă e **supapa** pentru fapte
  pe care aplicația nu le modelează (nota liberă din jurnal).
- **absența contabilizării automate NU e o stare neutră.** E o lipsă, și se numește ca atare. Sarcina
  probei stă pe manual, nu pe automat.
- ce **nu** decide regula: **starea** în care intră nota. Patru-ochi, ciornă vs validată, propunerea
  de la salarii — toate rămân unde sunt. *„Automat" e despre cine produce nota, nu despre în ce stare
  intră.*

**De ce contează forma asta și nu „hibrid, cu granița scrisă":** o graniță trasată peste starea de
fapt îngheață și golurile. *O regulă care descrie ce e nu mai poate arăta ce lipsește.* Cu regula de
mai sus, harta din 29.08.2026 a produs două restanțe (R87, R88) exact acolo unde altfel s-ar fi citit
„așa e proiectat".

**O NOTĂ DE PE CALEA LIBERĂ CARE CONTEAZĂ EVIDENT O FACTURĂ POARTĂ CHEIA EI** *(29.08.2026, DDD3)*

Regula de mai sus spune că faptul își produce nota. Aici e cealaltă direcție: **ce se întâmplă cu o
notă care vine din supapă.** `POST /tenants/{id}/jurnal` rămâne excepția declarată — nota liberă e
pentru fapte pe care aplicația nu le modelează —, dar **contractul ei se schimbă**:

- dacă nota are **semnătura unei contări de factură** (un cont de terț — 4111 · 401 · 404 — și un
  cont de fond sau de TVA) **și** exact **una** dintre facturile declarabile ale lunii se potrivește
  pe total, **la ban**, **și** factura aia n-are deja o notă de contare — atunci nota primește
  `factura_id` **la scriere**, iar răspunsul rutei îl conține.
- dacă se potrivesc **două** facturi, **nu se leagă niciuna**. *O legătură greșită e mai rea decât
  lipsa ei: ar face o factură să pară contată de altcineva.*

**De ce e un contract, nu un detaliu:** până azi, o notă din jurnalul liber nu putea purta niciodată
`factura_id`, iar mecanismul anti-dublare — care se uită exact la cheia aia — era orb la ea. Legarea
la sursă e **reparația**; căutarea de note fără cheie, făcută înainte de fiecare notă automată, rămâne
**plasă**, nu mecanism principal. *Un sistem care trăiește din prinderea greșelii, în loc s-o evite,
are un singur punct de eșec.*

**Ce nu acoperă, declarat:** o factură contată manual pe `461`/`462` nu se leagă — conturile alea nu
sunt scrise de niciun drum factură→notă din cod. Și nu se leagă retroactiv nimic: regula e despre
notele scrise **de acum**.

### Ce e în afara registrului

**Cursul valutar** — valoare pe dată, dar fapt de piață, nu normă. Regula de alegere a lui e însă convenție de calcul și intră.

---

# PARTEA IV — CICLUL DE VIAȚĂ AL UNUI DOCUMENT

```
INTRARE          date brute → evidență, cu proveniență și grad de certitudine
   ↓
CALCUL           evidență + registru(la_data) → rezultat + decizii + certitudine
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

**Previzualizarea și emiterea folosesc același calcul.**

**Rezultatul poartă deciziile de interpretare pe care stă.**

**Verificarea precedă emiterea și nu o poate declanșa.**

**Emiterea e idempotentă și repetabilă.** Nicio schemă nu interzice al doilea exemplar.

**Emiterea îngheață lanțul**, nu doar cifrele.

**Predarea e distinctă de emitere.**

**Reconcilierea compară patru lucruri**: documentul emis, evidența, recalculul, și ce confirmă autoritatea.

**O decizie schimbată nu rescrie documentele emise sub cea veche.**

**O modificare retroactivă de lege parcurge P18.**

---

# PARTEA V — CONTRACTE ÎNTRE MODULE

**Ce declară un modul:** ce primește · ce întoarce, ca tip · ce garantează · **pe ce decizii de interpretare stă** · **ce certitudine au intrările** · ce nu poate spune.

**Perechile generator ↔ verificator:** nu importă modulul verificat, nici tranzitiv · nu-i copiază constantele · nu-i reproduce formulele · nu se modifică în același commit fără decizie scrisă · **nu se aliniază la el când diverg**.

**Interfața cu autoritățile:** patru componente separate — generarea, validarea, transmiterea, reconcilierea.

**Erorile publicate:** spun ce lipsește și unde se rezolvă · fără nume interne · în limba interfeței, cu diacritice.

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
| 21 | O alegere de interpretare făcută la scriere, fără să fi fost cerută decizia | P11 |
| 22 | O decizie de interpretare înregistrată fără varianta respinsă numită | P11 |
| 23 | Un dezacord lege ↔ arbitru, tranșat în cod în loc să fie ridicat la decizie | P8·P11 |
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
| 49 | Un articol folosit fără dată de verificare a vigorii | Partea 0 · P8 |
| 50 | O valoare sprijinită pe un articol abrogat sau modificat, fără succesor citat | Partea 0 · P8 |
| 51 | O regulă scrisă din memorie, când actul lipsește din corpus | Partea 0 · P8 |
| 52 | Un act din corpus al cărui text s-a modificat după aducere | stratul 1 |
| 53 | Un citat verbatim care nu conține valoarea pe care o justifică | Partea 0 · P8 |
| 54 | Un articol folosit cu verificarea vigorii expirată față de pragul lui | Partea 0 · P8 |
| 55 | Un articol din corpus fără categorie de reverificare atribuită | stratul 1 |
| 56 | **O regulă scrisă când textul a fost citit dar nu înțeles, fără cerere specifică** | Partea 0 · P8 |
| 57 | **O valoare fără temei, intrată fără declarația „am căutat și nu am găsit"** | Partea 0 · P8 |
| 58 | **O sursă de nivel inferior care contrazice una superioară, fără decizie** | Partea 0 · P8 |
| 59 | **Verificarea vigorii făcută pe act, nu pe articolul folosit** | Partea 0 · P8 |
| 60 | **O regulă, formulă sau structură care implementează o normă, fără articolul asociat** | P21 |
| 61 | **Un articol din corpus fără lista dependenților, generabilă la cerere** | P21 |
| 62 | **O modificare de articol aplicată fără parcurgerea listei dependenților** | P21·P18 |
| 63 | **O cifră afișată fără posibilitatea de a-i vedea, la cerere, componentele** | P22 |
| 64 | **Un element care putea interveni și n-a intervenit, fără motiv și temei afișabile** | P22 |
| 65 | **O valoare diferită de perioada anterioară, fără explicația diferenței** | P22 |
| 66 | **O legătură normă↔implementare care există în cod, dar nu ajunge pe ecran** | P22·P21 |
| 67 | **Un rezultat produs peste date lipsă, fără ca lipsa să fi fost cerută** | P23 |
| 68 | **O lipsă semnalată abia la generare, când datele nu mai pot fi obținute** | P23 |
| 69 | **Un verdict care nu distinge „gata" de „gata cu ce am avut"** | P23·P6 |
| 70 | **O interpretare care ajunge într-o cifră depusă, nerevizuită fără să fie declarată ca atare** | P24 |
| 71 | **O copie de siguranță din care nu s-a restaurat niciodată** | P25 |
| 72 | **O restaurare care nu se poate dovedi identică cu originalul** | P25 |
| 73 | **O copie care se poate pierde odată cu originalul** | P25 |
| 74 | **Un export care rupe lanțul dintre declarație și documentele justificative** | P26·P14 |
| 75 | **Date care se pot lua doar cu intervenția noastră, sau într-un format închis** | P26 |
| 76 | **Un instrument de măsurare fără calibrare pe propriul mod de eșec** | P24 |
| 77 | **Un blocaj fără temei: aplicația oprește un act și nu spune pe ce se sprijină** | P24·P14 |

**Interdicția 76, adăugată 23.08.2026 (Costin), cu motivul ei.** Calibrarea **pozitivă** dovedește că
instrumentul **găsește ce caută**. Nu dovedește că **nu ratează**. Patru instanțe într-o singură zi,
toate cu calibrare care trecea:

| instrument | forma pe care s-a legat | calibrarea existentă, și de ce trecea |
|---|---|---|
| `graf_temei` | cheie pe **numele simplu** al funcției | patru afirmații pozitive și una negativă din prima zi — toate pe o zonă unde numele erau unice |
| `vigoare_punct` | marcajul se termină la primul `)` · un singur tipar de numerotare | cazul pct. 9, care n-are paranteze în adresă |
| `scan_instrumente` (calibrarea) | **cuvântul** „calibrare" în docstring | nicio calibrare — era instrument nou |
| `scan_instrumente` (legătura) | **numele fișierului** `test_<modul>.py` | idem |

**Corolarul, fiindcă e partea folosibilă — un instrument se calibrează pe felul în care POATE greși:**

- unul **cheiat pe nume** → pe o **coliziune de nume**;
- unul care **citește marcaje** → pe **două marcaje lipite**, și pe unul cu paranteze în adresă;
- unul care **caută un cuvânt** → pe un caz unde **cuvântul lipsește dar lucrul există**, și pe unul
  unde cuvântul există dar lucrul nu;
- unul care **numără o clasă** → pe un membru pe care **nu trebuie** să-l găsească.

**Nu e o regulă despre cum lucrăm, ci despre ce face un instrument credibil** — iar pe instrumente
stau toate măsurătorile de după.



---

# PARTEA VII — CUM SE FOLOSEȘTE DOCUMENTUL

**Întâi se modifică planul, apoi se conformează codul.** Nicio schimbare de fundament nu se face direct în aplicație. Când apare o regulă nouă sau se corectează una veche, ea intră aici mai întâi; abia apoi se confruntă și se repară.

Motivul: o regulă aplicată în cod fără să fie scrisă în plan trăiește doar în locul unde a fost aplicată. Următoarea dată când cineva atinge alt modul, n-o știe.

**Nu se modifică pentru a se potrivi cu realitatea.** Dacă aplicația îl încalcă, se schimbă aplicația. Dacă un principiu se dovedește greșit, se schimbă documentul — prin decizie scrisă, cu motiv, nu prin adaptare tăcută.

**Confruntarea e o operațiune separată**, în `CONFORMITATE.md`, cu stare declarată per interdicție.

**Ordinea reparațiilor:**

| # | Grup | Principii | Interdicții |
|---|---|---|---|
| 0 | **Temeiurile** | Partea 0, P8 | 49–59 |
| 1 | Registrul | P1, P11, P13 parțial | 1, 2, 16, 17, 21, 22, 23, 28 |
| 2 | Inalterabilitatea și urma | P15, P16 | 34–38 |
| 3 | Trasabilitatea | P14, **P21**, **P22** | 32, 33, **60–66** |
| 4 | Direcția dependenței | P3, P13 | 4, 5, 13, 15, 26, 27, 31 |
| 5 | Documentele și trimiterea | P4, P19, **P23** | 6, 7, 8, 43, 44, **67, 68, 69** |
| 6 | Proveniența | P20 | 45, 46 |
| 7 | Izolarea | P12 | 24, 25 |
| 8 | Retenția și retroactivitatea | P17, P18 | 39–42 |
| 8b | **Supraviețuirea și portabilitatea** | **P25, P26** | **71–75** |
| 8c | **Revizuirea interpretărilor** | **P24** | **70** |
| 9 | Restul | — | 29, 30, 47, 48 |

**Grupul 0 e deasupra registrului.** O valoare corect așezată în registru, care se sprijină pe un articol abrogat, pe un citat care n-o conține, sau pe un text neînțeles, e greșită oricât de bine ar fi structurat registrul.

**Fiecare interdicție primește un gard înainte de reparație.**

---

# ANEXĂ A — DE CE PARTEA 0

**Verificarea 1 — înțelegerea.** Cea mai periculoasă situație nu e „nu găsesc actul", ci „am actul, l-am citit, dar nu-mi spune ce fac în cazul ăsta". Nu se manifestă în niciun fel: se produce ceva plauzibil și se merge mai departe. La „încadrat cu salariul minim", textul a fost citit, n-a fost înțeles complet, și în loc de o întrebare a ieșit o interpretare.

**Verificarea 2 — vigoarea.** OPANAF 394/2017, citat în nouă locuri, era abrogat de OPANAF 705/2020. HG 685/1999, abrogat de HG 773/2019. Ambele găsite din întâmplare. Iar OUG 156/2024 e în vigoare, dar art. LXX a fost abrogat de OUG 29/2026 și art. LXVI modificat de OUG 89/2025 — de aceea unitatea de verificare e articolul, nu actul.

**Verificarea 3 — conținutul.** Trei citări false: facilitatea de 300 de lei atribuită unui act care nu o conținea; cota de dividende atribuită Codului fiscal în loc de ordonanța care o fixase; pragul mijloacelor fixe, la fel. **Actele existau și erau în vigoare.** Greșit era ce li se atribuia.

**Verificarea 4 — ierarhia.** La podeaua part-time, legea spune una și structura publicată de autoritate spune alta. S-a ales în cod, fără decizie. Regula lipsă: o sursă inferioară nu poate contrazice una superioară fără să se ridice la decizie — mai ales când e mai comodă.

**Verificarea 5 — determinarea.** Aceeași instanță, cealaltă față: alegerea n-a fost cerută.

**PRINCIPIUL, decis de Costin pe 06.09.2026** *(`DECIZII.md` 72; instanța: R151, art. 291 alin. (5)
Cod fiscal)*:

> **O alegere fiscală care nu se poate deriva mecanic din datele existente se cere de la om, la
> operațiune — niciodată preselectată, niciodată dedusă pe ghicite. Se cere doar ce nu se poate
> stabili; nu se cere ce aplicația poate stabili singură din datele pe care le are deja.**

Are **două jumătăți**, și amândouă sunt norme:

1. **Ce nu se poate deriva se CERE.** Nu se alege în cod, nu se pune un default „rezonabil", nu se
   deduce din context. Motivul, verbatim din decizie: *„a ghici ar produce o cifră validă și
   falsă."* Ăsta e cazul cel mai rău dintre toate — nu o eroare care se vede, ci o cifră care trece
   toate verificările de formă și e greșită pe fond. Instanța: art. 291 alin. (5) are două ramuri
   (cota faptului generator vs. cota facturii/avansului care l-a precedat), iar datele operațiunii
   **nu spun care document a fost primul**.

2. **Ce se poate stabili NU se cere.** O întrebare pusă degeaba mută pe om o muncă pe care aplicația
   o putea face, și îi tocește atenția pentru întrebările care contează. Instanța, din aceeași
   reparație: când contabilul alege ramura de excepție și dă o dată **ulterioară** livrării,
   aplicația are amândouă datele — deci nu întreabă a doua oară, ci **arată contradicția**.

**„Cerută" înseamnă NEPRESELECTATĂ, și asta nu e o precizare de stil.** Un `select` obligatoriu se
randează cu prima opțiune deja aleasă. O alegere juridică pusă pe ecran în forma asta **arată** ca o
întrebare și **funcționează** ca un default: omul apasă „trimite" fără să fi ales nimic, iar
aplicația a răspuns în locul lui. *E același default fiscal tăcut pe care casa îl interzice în cod,
doar că îmbrăcat în interfață — deci invizibil pentru orice gardă scrisă în Python.* De aceea
câmpul de alegere pornește de la o opțiune goală, selectată, și rămâne obligatoriu.

**Unde se aplică:** oriunde norma lasă două căi și faptele din evidență nu le deosebesc. Nu e o
regulă despre TVA; art. 291 alin. (5) e doar prima instanță care a ajuns până la capăt.

**Ce arată împreună:** „am citit actul" nu acoperă niciuna dintre celelalte patru. Sunt cinci verificări diferite, iar până acum doar prima jumătate a primei era regulă.

---

# ANEXĂ B — DE CE P11

**„Încadrat cu salariul de bază minim brut."** Egalitate strictă, sau sub un plafon? Legea nu spune. S-a ales egalitatea strictă la scriere, iar alegerea a trăit într-o comparație din cod. Consecința: un leu peste minim costă salariatul optzeci și doi.

**Facilitatea la baza minimă part-time.** Legea spune că e pentru normă întreagă; structura publicată de autoritate o scade totuși din nivelul de referință, iar validatorul o implementează. S-a ales urmarea legii, contra arbitrului, cu raționamentul scris într-un comentariu. **Nimeni n-a fost întrebat.** Două săptămâni mai târziu, semnalul care contrazicea alegerea fusese înghețat ca așteptat, iar a doua cale de verificare fusese aliniată la prima. Divergența: 70,25 lei pe lună, pe fiecare salariat part-time sub minim.

**Codificarea perioadei trimestriale.** Cifra 09 pentru trimestrul al treilea arăta ca o eroare. Era codificarea corectă a autorității.

**De ce prima versiune era insuficientă.** Cerea ca alegerea să fie *documentată*. Dar lăsa alegerea la cel care scrie codul.

Forma corectă: **alegerea nu e a lui.** Decizia intră în registru fiindcă a fost luată, nu fiindcă cineva și-a amintit s-o consemneze.

---

# ANEXĂ C — DE CE P13

**Text care afirmă fals.** „Vector necompletat" pe firme cu vectorul complet. „Patru-ochi e dezactivat" pe o politică doar suspendată. „Validarea în doi ✓" pe un cabinet cu un singur validator.

**Text folosit ca dată.** Clasificarea duplicatelor la import se făcea potrivind proză.

**Text citit de o gardă ca dovadă.** Patru instanțe într-o zi.

**Text scris pentru programator, livrat contabilului.**

**Text duplicat.** Un câmp care spunea același lucru ca afirmația structurată de alături.

Și, în nomenclatură: trei etichete de coduri de indemnizație greșite față de sursa oficială, două inversate între ele.

---

# ANEXĂ D — DE CE PARTEA B

P1–P13 asigură că **producem cifra corectă**. P14–P20 asigură că **o putem apăra**.

| Fără | Consecința la control |
|---|---|
| P14 trasabilitate | „De unde iese suma?" nu are răspuns |
| P15 inalterabilitate | evidența s-a schimbat după depunere |
| P16 responsabilitate | nu se știe cine a autorizat |
| P17 retenție | ori s-a șters ce trebuia păstrat, ori invers |
| P18 retroactivitate | declarații depuse au devenit incorecte și nimeni nu știe care |
| P19 stare externă | depunere dublă, sau termen ratat |
| P20 proveniență | o presupunere a devenit fapt și a intrat într-o declarație |
| P21 legătura cu norma | o modificare de lege lasă în urmă cod care nu se poate găsi |
| P22 verificabilitate | contabilul nu poate verifica cifra, deci o reface în altă parte |
| P23 ce lipsește | un rezultat peste date incomplete arată identic cu unul corect |
| P24 revizuire | o interpretare greșită supraviețuiește, bine documentată |
| P25 supraviețuire | evidența dispare, iar răspunderea rămâne a cabinetului |
| P26 portabilitate | clientul nu-și poate lua evidența pe care legea îl obligă s-o păstreze |

**Consecința comercială e aceeași cu cea juridică:** dacă un contabil nu poate răspunde cu aplicația la un control, o va dubla cu evidența lui paralelă — și atunci produsul nu i-a economisit munca, i-a adăugat una.

Același lucru se întâmplă, la scară mai mică dar în fiecare zi, dacă nu poate verifica o cifră pe ecran. P22 nu e confort — e ce împiedică apariția evidenței paralele.
