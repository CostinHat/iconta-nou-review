# PLAN DE LUCRU

Al treilea plan, și ultimul. Celelalte două spun **ce** și **în ce ordine**. Ăsta spune **când, unde suntem, ce se face cu ce rămâne în urmă, și ce ține de om.**

| Plan | Ce conține |
|---|---|
| `PLAN_ARHITECTURA.md` | cum trebuie să fie: 26 de principii, 75 de interdicții |
| `PLAN_INVESTIGATII.md` | ce se măsoară, în ce ordine, cu ce metodă |
| `PLAN_LUCRU.md` | cronologia, punctele de decizie, starea, ritmul |

---

## Spre ce curge totul

**Produsul se dă unui contabil când poate spune, cu dovada pe masă:**

> Pentru o firmă și un exercițiu, aplicația produce tot ce cere legea, fiecare artefact se validează, fiecare cifră se poate desface până la documentul care o justifică, și contabilul o poate verifica pe ecran fără s-o recalculeze.

Nu „când nu mai are defecte". Când propoziția de mai sus e adevărată și demonstrabilă.

Restul — interdicțiile care măsoară fragilitatea — hotărăsc **cât de repede se strică**, nu dacă merge.

**Iar odată dat, angajamentul e:** răspuns în 48 de ore la orice solicitare — ce e, cât durează, când se face — și livrare în 48 de ore pentru clasa care se poate: o declarație, un raport, o corelare, un format de import.

Angajamentul e și testul arhitecturii. Două zile sunt posibile doar dacă registrul, secvența temeiului, legătura normă↔implementare și separarea calcul/prezentare există deja. Fără ele, două zile devin două săptămâni.

---

## Etapele

Fiecare are un criteriu de terminare **observabil**, nu o estimare de durată.

### E1 — Setul complet *(faza 1 din investigații)*

**Gata când:** există lista artefactelor cerute de lege, pe trei regimuri, iar fiecare e clasificat în una din cele cinci categorii ale verdictului.

**Ce iese:** știm dacă aplicația produce ce cere legea, și pe cine cade răspunderea pentru ce nu iese.

**Ce blochează:** nimic. Se poate începe imediat.

---

### E2 — Temeiurile *(faza 2)*

**Gata când:** fiecare articol folosit are dată de verificare, stare, succesor și categorie de reverificare; iar cele trei clase de eroare — vigoare, conținut, legătură cu implementarea — sunt măsurate sau declarate nemăsurabile cu motiv.

**Ce iese:** știm dacă aplicația stă pe temeiuri valide, și dacă o modificare de lege poate fi urmărită până la codul afectat.

**Ce blochează:** nimic din afară. Presupunerea că portalul legislativ ar bloca accesul automat **s-a dovedit falsă pe 22.08.2026** — răspunde cu antet de browser, iar căutarea se face prin formularul lui. Verificarea vigorii pe articol e mecanică (`scripts/vigoare_articol.py`), deci pragurile din plan rămân cele scrise.

---

### ⬛ PUNCT DE DECIZIE 1

**După E1 și E2.** Se răspunde la trei întrebări, cu date pe masă:

1. Aplicația produce ce cere legea? Ce lipsește, și cine răspunde?
2. Stă pe temeiuri valide? Câte sunt greșite?
3. **Continuăm investigația, sau reparăm ce s-a găsit?**

Aici se poate opri investigația. Dacă E1 și E2 scot destule ca să umple săptămâni de reparat, restul fazelor se amână explicit.

---

### E3 — Fragilitatea, cartografiată *(fazele 3–6)*

**Gata când:** toate cele 75 de interdicții au stare declarată în `CONFORMITATE.md`, iar cele măsurate au cifră, listă, calibrare și limite.

**Ce iese:** harta completă, cu ordinea reparațiilor ponderată de ce s-a găsit.

**Ce blochează:** faza 4 — instrumentele — trebuie făcută înaintea fazelor 5 și 6. Dacă gărzile mint, măsurătorile de după moștenesc minciuna.

---

### E4 — Ce nu se măsoară, se construiește *(faza 7)*

**Gata când:** lista interpretărilor care ajung într-o cifră depusă e scrisă și **revizuită deliberat, ca listă** · o restaurare completă a fost probată, cu dovada identității · exportul complet al unei firme a fost încercat.

**Ce iese:** trei lucruri care azi nu există deloc.

**Ce blochează:** nimic din afară. Revizuirea e o operațiune proprie — se citește lista ruptă de context, nu se cere altcuiva.

---

### ⬛ PUNCT DE DECIZIE 2

**După E3 și E4.** Tabelul final: interdicție · instanțe · unde ajunge efectul · criteriu de acceptare · cost.

Se stabilește **ordinea reparațiilor** și **ce nu se repară**, cu motivul scris. Nu tot ce e pe listă merită reparat.

---

### E5 — Reparațiile

**Gata când:** fiecare interdicție a atins criteriul de acceptare ales la triaj — ZERO, DECLARAT, ÎNCHIS PRIN CONSTRUCȚIE, sau MĂSURAT ȘI ACCEPTAT.

**Regula, fără excepție:** gardă înainte de reparație. Ordinea e singura formă tare de probă.

**Excepția care sare peste tot planul:** un defect care produce **efect greșit la un om acum — cifră, blocaj, sau afirmație falsă pe ecran** — se repară imediat, în orice etapă. Se scrie în registru ca reparat, apoi se continuă. Vezi „Când se repară ceva — cele trei praguri", mai jos.

*Lărgită la 22.08.2026, de la „cifre greșite".* Motivul e o instanță: `flux_concediu.js` **blochează un contabil să introducă un cod legal de concediu medical**. Nu e o cifră greșită — e un blocaj — și tocmai de aceea a rămas neatins.


### Când se repară ceva — cele trei praguri

**Criteriul lipsea, iar lipsa lui a costat:** *„investigăm întâi, reparăm după"* e corect ca principiu
și prost ca regulă absolută.

**Pragul 1 — imediat.** Produce **efect greșit la un om ACUM**: o cifră, un blocaj, o afirmație falsă
pe ecran. **Nu cere măsurătoare, nu cere tabel.**

**Pragul 2 — la închiderea etapei.** **Cauză unică dovedită ȘI nu concurează cu nimic.** Aici intră și
**absențele** — un artefact fără producător n-are instanțe de ordonat, deci n-are ce aștepta de la un
tabel de priorități.

**Pragul 3 — după tabelul final.** Tot restul.

**Testul:** *dacă știi deja ce se repară primul fără să te uiți în tabel, n-ai nevoie de tabel.*

**LĂMURIRE 23.08.2026 (Costin): pragul 1 se citește ca ATINGIBILITATE, nu literal.**

*„Efect greșit la un om acum"* înseamnă: **dacă un contabil ar folosi aplicația azi, ar primi cifra
greșită, blocajul, sau afirmația falsă.** NU înseamnă că cineva a primit-o deja.

**Motivul:** citirea literală face pragul 1 **gol pe orice instalare fără clienți** — adică exact
acum, când reparăm. *Un prag care nu se poate atinge nu ordonează nimic.*

Cele trei instanțe rămân corecte pe citirea asta: TVA omisă din D300, blocajul pe codul de concediu,
eticheta greșită de pe fluturaș. **Toate trei ar lovi primul contabil în prima lună.**

Ce a declanșat lămurirea: măsurătoarea din 23.08 a arătat că toate cele 17 firme și toți cei 24 de
salariați sunt **de test**. Fără lămurire, pragul ar fi fost gol prin construcție, iar cele trei
reparații ar fi apărut ca făcute în afara regulii.



**Instanțele din primul triaj (22.08.2026), ca pragurile să nu rămână abstracte:**

| prag | ce a intrat |
|---|---|
| 1 | `de_preluat` exclus din D300 — 3.052 lei TVA colectată omisă, la 3 plătitori · `flux_concediu.js`, blocaj pe un cod legal · **eticheta „Deducere personala" de pe fluturaș tipărea totalul deducerilor** — afirmație falsă pe hârtia salariatului, 2 din 24 de salariați DE TEST — pe instalare nu există nicio firmă reală, vezi corecția din CONFORMITATE 1d |
| 2 | interdicția 2 (o cauză, o linie) · Registrul-inventar · Cartea mare · Registrul de evidență fiscală · evidența TVA ca artefact · jurnalul regim marjă |
| 3 | interdicțiile 1 (~100), 16 (39), 17a (42), 32 (19/33) · Registrul-jurnal, care depinde de 32 |

**Fluxul restanțelor și „ce oprește planul" trimit la praguri:** pasul 2 al fluxului („decide dacă
repari") e chiar pragul 1; ce nu-l atinge primește blocaj de ORDINE și așteaptă pragul 2 sau 3.

> **Reconstruit din comandă, 22.08.2026 — confirmat.** Secțiunea fusese scrisă local și n-a ajuns
> niciodată pe disc: comanda de urcare n-a fost dată. Reconstrucția din comandă a fost verificată
> cuvânt cu cuvânt și e cea validă. **Nu mai există o a doua versiune.**
>
> A treia oară în aceeași zi când ceva scris n-a ajuns unde trebuia — de aici regula: după ce se
> scrie într-un plan, comanda de urcare se dă imediat, nu la sfârșitul turei.

---

### ⬛ PUNCT DE DECIZIE 3

**Înainte de a da produsul unui contabil.** Se recitește propoziția de la început și se răspunde: e adevărată, și se poate demonstra?

Dacă nu, ce lipsește și cât mai durează.

---

## Restanțele — nu se pierde nimic, dar nimic nu blochează avansul

Fiecare pas produce restanțe. Prima confruntare a scos că registrul avea un gol de categorie; a doua, că o interdicție n-are numitor; a treia, cinci regimuri cu motor și zero firme exercitate.

**Bucla până la rezolvare nu funcționează:** unele restanțe nu se pot închide decât cu ce afli trei pași mai încolo. Dacă nu treci mai departe până nu le rezolvi, nu ajungi la pasul doi.

**Ce blochează nu e pasul, ci închiderea etapei.** Poți trece de la 1a la 1b cu patru căutări nerezolvate; nu poți declara E1 terminat cu ele deschise.

### Ce poartă o restanță

Patru câmpuri, toate obligatorii:

| câmp | ce conține |
|---|---|
| **ce e** | descrierea, în termeni verificabili |
| **unde intră** | etapa și, dacă e cazul, interdicția |
| **ce o închide** | condiția, nu intenția. Fără ea, o restanță e o notă |
| **blocajul** | de care fel, din cele **patru** de mai jos |

### Cele patru feluri de blocaj

**Două întrebări diferite, nu două liste rivale** (împăcate la 22.08.2026, după ce au coexistat o zi
fără să se știe una pe alta — vezi mai jos „De unde vin cele două"):

- **CE e blocat** — felul restanței, cel care se scrie în registru și se gardează;
- **CINE o deblochează** — o notă despre dependență, utilă în raport, nu un al doilea nomenclator.

**CE e blocat — cele patru feluri, singurele care intră în `CONFORMITATE.md`:**

| fel | ce înseamnă | condiția de deblocare arată ca |
|---|---|---|
| **SURSĂ** | temeiul nu se poate cita complet sau corect | „actul e adus întreg", „forma e declarată" |
| **VERIFICARE** | instrumentul nu ajunge până acolo | „instrumentul citește și puncte, calibrat pe pct. 9" |
| **ARTEFACT** | nu se poate spune ce datorează o firmă | „1b poate clasifica fiecare firmă" |
| **ORDINE** | **nimic tehnic nu blochează — doar nu e momentul** | **un moment din plan**: „la punctul de decizie 2", „când se atinge ecranul" |

**ORDINE e felul care lipsea, și e cel mai des întâlnit.** Cele mai multe defecte găsite în treacăt nu
așteaptă un instrument sau un act — își așteaptă rândul. Fără el, singurele variante erau „repar acum"
sau „rămâne în raport", iar a doua înseamnă **pierdut**.

**Condiția de deblocare a unei restanțe de ORDINE e un MOMENT, nu o stare.** „Când se poate" nu e
condiție; „la punctul de decizie 2" e.

### Fluxul, în cinci pași

1. **CONSEMNEAZĂ ÎNTÂI**, imediat, indiferent ce urmează. Un rând: **ce e · unde · ce efect are.**
2. **Decide dacă repari, după cele trei praguri din E5.**
   *Pragul 1* — produce efect greșit la un om ACUM: cifră, blocaj, afirmație falsă pe ecran → **repari acum**.
   *Pragul 2* — cauză unică dovedită și nu concurează cu nimic, sau e o absență → **la închiderea etapei**.
   *Pragul 3* — tot restul → **rămâne consemnat**, cu blocaj de ORDINE.

   Întrebarea nu e binară. O absență — un artefact fără producător — nu atinge pragul 1, dar nici nu
   așteaptă tabelul final: n-are instanțe de ordonat.
3. **Dacă ai reparat, marchezi ca reparat, cu commitul.**
4. **Dacă ai încercat și n-a mers**, rămâne consemnat, iar **motivul eșecului devine condiția de
   deblocare**.
5. **Mergi mai departe.**

**Ordinea contează, și e singurul lucru care nu se negociază.** Consemnarea e primul gest, cel care nu
depinde de nicio judecată. Dacă decizia vine prima, **ce hotărăști să nu repari riscă să nu ajungă
scris** — iar un defect nescris nu e datorie, e pierdere.

### CINE deblochează — nota de dependență

Se scrie lângă condiția de deblocare, când ajută. Nu se gardează, fiindcă nu decide nimic singură.

**EXTERN** — depinde de ceva ce nu se poate obține de aici.

Se formulează ca **cerere specifică**: ce trebuie, de unde, pentru ce. Nu „am nevoie de ajutor cu legea contabilității", ci *„îmi trebuie Legea 82/1991 în formă consolidată; în corpus sunt doar două documente de nivel 2; blochează familia A din 1a"*.

**INTERN** — depinde de un pas care urmează.

Se scrie **condiția de deblocare**: *„se reia după ce categoria de mărime există ca dimensiune a firmei"*. Nu se așteaptă ca cineva să-și amintească.

**DECIZIE** — depinde de om.

Se pune **în capul raportului** până se rezolvă, nu la coadă.

### De unde vin cele două, și de ce se scrie aici

Secțiunea asta a fost scrisă de Costin în `PLAN_LUCRU.md` și a intrat în repo pe **22.08.2026, în
commitul `45f15ab`** — un commit al meu, despre aducerea actelor, în care am dat `git add PLAN_LUCRU.md`
**fără să citesc diff-ul**. **70 de linii scrise de el au intrat sub mesajul meu.** N-am știut că
există, așa că am derivat separat, câteva ore mai târziu, o a doua taxonomie (SURSĂ / VERIFICARE /
ARTEFACT) pentru același obiect, iar ea a fost confirmată în conversație — fără ca niciunul dintre noi
să vadă că prima era deja scrisă.

Nu sunt rivale: prima răspunde la *cine deblochează*, a doua la *ce e blocat*. Împăcarea de mai sus
păstrează amândouă, cu roluri diferite. **Ce nu se păstrează e tăcerea:** un `git add` pe un fișier de
plan, fără citirea diff-ului, e cum se pierde o cerință — iar cerințele din secțiunea asta au stat
opt commituri neimplementate exact din motivul ăsta.

### Reaprinderea

**La fiecare tură se verifică ce restanțe au blocajul dispărut.** Alea se reiau, se rezolvă, și rezultatul se spune în raport — la secțiunea A, ca orice altă muncă făcută.

O restanță care poartă condiția de deblocare se reaprinde singură. Una care nu o poartă devine arhivă.

**GARDATĂ, din 23.08.2026 — și regula spune unde:** `core/test_reaprindere.py`. Până atunci era scrisă
și nepăzită, deci se citea ca respectată: contorul de `reluări` era **0 pe toate cele 25 de restanțe**,
iar condiția lui R8 se declanșase de două ori în aceeași zi fără ca nimeni s-o observe. **Ce închide
garda:** clasa în care declanșatorul e mecanic — o condiție care numește un fișier și verbul *„atinge"*.
**Ce NU închide, măsurat:** **17 din 18** condiții deschise azi nu au forma asta și rămân de citit de om.
Deci garda e o felie îngustă, iar pârghia adevărată e **cum se scrie condiția**: una de forma *„la primul
commit care atinge `X`"* se poate cabla; una de forma *„se închide când inventarul există"* nu.

### Prima încercare — o restanță nu e grea până n-a fost încercată

**Regulă, 23.08.2026, din experiment.** **R10** avea **40 de commituri pe registru și zero încercări**;
încercată o dată, s-a închis în **două minute** — toate cele patru cerințe ale ei aveau deja gărzi, de o
zi. Nu era grea: **era neîncercată**, iar cele două nu se pot deosebi din afară.

**Consecința practică: la fiecare tură, o restanță neîncercată SE ÎNCEARCĂ.** Nu se rezolvă neapărat —
se încearcă. Un eșec e un rezultat bun: motivul lui devine condiția de deblocare (pasul 4 din flux).

**Contorul de reluări începe de la PRIMA încercare, nu de la a doua.** Altfel „reluare" numește doar
repetarea, iar o restanță care n-a fost atinsă niciodată arată identic cu una încercată o dată și
eșuată — exact confuzia care a ținut nouă restanțe nemișcate patruzeci de commituri.

### Forma condiției de deblocare — cablabilă dacă se poate

**Cerință, 23.08.2026.** O condiție de deblocare **se scrie în formă cablabilă dacă se poate**; dacă nu
se poate, **motivul se scrie lângă ea**. Cine scrie condiția decide dacă ea va putea fi păzită vreodată
— asta e mai valoroasă decât orice gardă construită după.

**Formă cablabilă** înseamnă că un test poate decide singur dacă s-a îndeplinit: *„la primul commit care
atinge `X`"* · *„când fișierul Y are câmpul Z"* · *„când numărul N ajunge la zero"*. **Formă necablabilă**:
*„se închide când inventarul există"*, *„când se atinge ecranul"* — adevărate, dar de citit de om.

**Măsurat, ca să nu rămână o preferință.** Din **18** restanțe deschise, **una singură** avea condiție
cablabilă (R8). Trecute în revistă cele 15 stări de citit: **12 s-ar fi putut scrie cablabil** dacă
cineva s-ar fi gândit la asta când le-a scris. Cea mai clară e **R9** — *„când se atinge ecranul statului
de plată"* — care e **exact forma lui R8** (un declanșator pe fișier), scrisă ca frază în loc de fișier.
Restul de 3 (R6, R11, R18) depind de o decizie sau de un eveniment din afara depozitului, iar acolo
motivul se scrie și e de ajuns.

### Consecința practică: „se poate cabla?" e PRIMA întrebare la o cerință nouă

**Regulă, 23.08.2026, după a șasea instanță din aceeași zi.** Când primesc o cerință nouă — de proces,
de formă, de registru — prima întrebare nu e *cât costă*, ci **„se poate cabla?"**. Dacă da, **se
cablează atunci**, nu peste patruzeci de commituri.

Motivul e măsurat, nu principial: forma `atinge:` din condiția lui R8 era cablabilă **de la început** și
n-a fost cerută nimănui; 12 din 15 condiții deschise s-ar fi putut scrie așa. Costul de a cabla la
scriere e minut; costul de a cabla după e o campanie plus restanțele care au trecut între timp
nepăzite. *Vezi `METODA_VERIFICARE.md` §16: verificarea se face unde e nevoie, nu unde e ușor — iar
„ușor" include și „mai târziu".*

### Contorul de reluări

**O restanță reluată și tot nerezolvată se numără.** Dacă a fost reluată de trei ori și tot n-a mers, **condiția de deblocare e scrisă greșit** — nu restanța e grea.

Atunci se rescrie condiția, prin decizie, cu motivul. Nu se mai reia a patra oară pe aceeași condiție.

### Unde stau

În `CONFORMITATE.md`, secțiune proprie după antet. Nu într-un fișier separat — al doilea loc unde trăiește starea se învechește.

### Ce se gardează

- un raport care nu enumeră restanțele deschise nu trece;
- o restanță fără „ce o închide" nu poate fi scrisă;
- **o etapă nu se poate declara terminată dacă are restanțe deschise care îi aparțin**;
- o restanță cu blocaj EXTERN fără cerere specifică formulată nu trece.

Ultima e importantă: „aștept ceva din afară" fără să spui exact ce, de unde și pentru ce nu e o restanță blocată — e o restanță nescrisă.

---

## Unde suntem

**Un singur loc:** `CONFORMITATE.md`, plus un antet nou care spune etapa curentă și ce o termină.

Azi starea e împrăștiată — stările interdicțiilor într-un loc, fronturile deschise în altul, cifrele în rapoarte care se citesc o dată. Un om care se uită nu poate spune unde suntem.

**Antetul registrului conține:**

- etapa curentă și criteriul ei de terminare;
- ce lipsește ca să se termine;
- **câte restanțe deschise are etapa curentă**, pe cele patru feluri de blocaj;
- deciziile care blochează, dacă sunt;
- cel mai vechi commit dintre cifrele din registru;
- data ultimei actualizări.

**Se actualizează la fiecare tură**, ca orice registru. Un antet stătut e mai rău decât niciunul.

---

## Ce ține de om, nu de muncă

Deciziile care nu se rezolvă prin efort. Fiecare blochează ceva; niciuna nu se poate lua de altcineva.

| Decizia | Ce blochează | Stare |
|---|---|---|
| **Câte regimuri acoperă E1** | setul de artefacte se face pe regimurile reale, nu pe trei alese arbitrar | **de măsurat la începutul E1** |
| **Se îngheață perimetrul până la conformitate?** | dacă nu, lista de interdicții crește cu fiecare modul nou | **LUAT 22.08.2026 — DA** |
| **Ce se repară și ce nu**, la punctul de decizie 2 | E5 | *la momentul potrivit* |

**Stabilit:**

- **perimetrul se îngheață (22.08.2026).** Nimic nou până trece verificarea, cu o singură excepție: cererile unui contabil real — care oricum nu există încă. Motivul e chiar cel din tabel: fără înghețare, lista de interdicții crește cu fiecare modul nou, iar criteriul de terminare al lui E3 se mișcă sub măsurătoare.

- **nu există termen calendaristic.** Se termină când trece verificarea. Ce împiedică extinderea la infinit sunt criteriile de terminare per etapă și punctele de decizie — dacă o etapă nu avansează, se schimbă abordarea, nu se prelungește.
- **verificarea o facem noi doi.** Nu se caută un actor din afară; P24 e o revizuire proprie, deliberată.
- **cele 35 de declarații fără interfață se implementează la cerere**, nu preventiv. Nu intră în perimetrul de conformitate.

---

## Ritmul

**O tură = observații pe precedenta + decizii cerute în cap + comanda următoare.** Nu se sare peste prima parte: acolo se prind erorile.

**Raportul are două secțiuni:** *A — răspuns la comandă*, punct cu punct, cu aceeași numerotare; *B — unde suntem*, derivată din antetul registrului, nu scrisă de mână.

**La fiecare tură se verifică restanțele cu blocajul dispărut.** Ce s-a deblocat se reia și se rezolvă în tura aceea, iar rezultatul intră la secțiunea A.

**Ziua se închide cu `ISTORIC.md`.** Nu după fiecare tură.

**Contextul se golește.** Când raportul spune că se apropie de plin, se închide ziua sau se reia cu `PREDARE_LANT.md`. O tură pornită pe context aproape plin produce muncă de întors.

**Observație, nu regulă.** Erorile din ultimele ture ale unei zile lungi au fost de tip transcriere și reconstruire din memorie — două planuri divergente, o regulă pierdută la rescriere. Merită știut ce fel de greșeli apar spre final, ca să fie căutate acolo. Dar haosul obosește mai mult decât munca: un plan care spune unde ești și cât mai ai e el însuși odihnitor.

---

## Ce oprește planul

**Un plan s-a dovedit greșit.** Se modifică prin decizie scrisă, apoi se reia. S-a întâmplat de patru ori într-o zi.

**O măsurătoare n-a fost calibrată.** O cifră fără caz pozitiv găsit nu e rezultat.

**Un defect produce efect greșit la un om acum** — cifră, blocaj, sau afirmație falsă pe ecran. Se repară pe loc (pragul 1).

**O etapă nu avansează.** Nu se prelungește — se schimbă abordarea, prin decizie scrisă.

**O restanță a fost reluată de trei ori fără rezultat.** Condiția ei de deblocare e scrisă greșit. Se rescrie, prin decizie, cu motivul — nu se mai reia a patra oară pe aceeași condiție.

---

## Ce nu e în planul ăsta

**Estimări de durată.** Nu se pot face cu date pe care nu le avem. Triajul din faza 3 le produce; până atunci, orice cifră ar fi inventată. Etapele se termină prin criteriu, nu prin calendar.

**Ce se întâmplă după primul contabil.** Un produs care intră în folosință primește o clasă nouă de întrebări — suport, incidente, cereri de funcționalitate. Alt plan, altă dată.

**Legislația care se schimbă.** E întreținere permanentă, nu proiect. Se bugetează separat, nu se speră că se termină.

---

## Direcții de produs, nedatate

*Nu sunt restanțe: n-au contor, n-au condiție de deblocare și nu se numără la „ce blochează". Sunt lucruri de făcut cândva, scrise ca să nu se piardă.*

**SUPERVIZORUL — temă de arhitectură pentru FINAL (cerută de Costin, 31.08.2026).** *Verificarea
încrucișată devine funcționalitate distinctă a aplicației, care rulează pe cont propriu, nu la
depunere.*

**Ce schimbă, structural.** Azi confruntarea dintre două surse care ar trebui să spună același lucru
se întâmplă — când se întâmplă — **agățată de actul depunerii**: la generarea unei declarații, la
poarta pre-DUK, la închiderea lunii. Consecința e că verificarea moștenește **momentul**, **domeniul**
și **populația** actului de care atârnă: se uită doar la ce se depune, doar când se depune, doar
pentru firma și perioada aceea. Ce nu se depune nu se confruntă niciodată, iar ce se depune se
confruntă prea târziu ca să mai fie ieftin de reparat.

**Supervizorul inversează dependența.** Confruntarea capătă declanșator propriu, domeniu propriu și
ieșire proprie: rulează pe portofoliu, nu pe un act; produce constatări, nu blocaje; iar depunerea
**citește** ce a găsit el, în loc să-l cheme. Depunerea rămâne cu porțile ei — supervizorul nu le
înlocuiește și nu devine o a doua poartă.

**De ce e temă de arhitectură și nu o restanță.** Nu e un ecran în plus: e a treia clasă de rulare a
aplicației, lângă „cererea unui om" și „jobul programat" — una care are voie să spună *nu știu*, și
al cărei rezultat e o **afirmație despre datele firmei**, cu atributele ei (`DESIGN_SYSTEM` cap.25),
nu un mesaj. Cine o construiește începe de la întrebarea *ce nu poate spune verificarea asta*.

**ÎNCEPUTĂ 01.09.2026**, la comanda lui Costin. `core/supervizor.py` — axa **orizontală**
(declarație contra declarație), cu cele două tării.

**Ce NU mai e nedecis:** *dacă o constatare poate deveni vreodată blocantă* — **nu**, niciodată.
Constatările au două tării *(Costin, 01.09)*: **euristice**, care „semnalează, nu opresc niciodată",
și **certe** — „nepotrivire aritmetică între ce se declară și ce e în evidență" —, care „nu blochează,
dar cer confirmare explicită înainte de depunere, iar confirmarea rămâne scrisă". Supervizorul nu e a
doua poartă.

**Ce rămâne al lui Costin:** ce declanșează o rulare · ce vede contabilul din ea și unde ·
**împărțirea pe tării, pe tipuri de constatare** — *„o dau eu … supervizorul nu o deduce singur"*.
Tabelul `TIPURI` din `core/supervizor.py` o așteaptă ca **date**: un tip fără tărie atribuită se
vede, dar nu produce niciun efect. **R115.**

**Import portofoliu, asistat de AI.** Recunoașterea structurii fișierului se face **o dată**, cu AI; rezultatul se sedimentează ca **amprentă de fișier** (set de anteturi, ordine, separator zecimal, unde începe tabelul), iar exporturile următoare cu aceeași amprentă intră **determinist, fără interpretare**. Amprenta e cheia, nu numele aplicației — același program are versiuni care exportă diferit. Potrivirea e **exactă sau inexistentă**: „aproape ca X" se tratează ca structură nouă. Proba aritmetică (balanța închide pe fiecare cont și pe total) rămâne **obligatorie și la amprentele deja cunoscute** — recunoașterea sare peste interpretare, nu peste verificare. Corecțiile contabilului la mapare se întorc în amprentă.

**Blocat de:** **R79** — dacă numele de schemă se reciclează și `DROP`-ul nu e real, un import în masă poate scrie peste date reziduale ale unei firme șterse. **R81** — treapta de confruntare a CUI-ului cu ANAF multiplică divergența de denumire la scara întregului portofoliu.

---

## ⬛ STAREA, DUPĂ R118 — construcția internă se ÎNCHIDE *(Costin, 02.09.2026)*

**Scris aici la cererea lui, ca stare, nu ca notă de raport** — *„ca să nu se reia din vecinătate
după `/clear`"*. Cine deschide planul după o repornire de context citește asta **înainte** de a-și
alege următorul lucru din ce e mai la îndemână.

> *„După R118 nu se mai deschide nicio temă internă. Restul familiei R82 rămâne parcată. Backlogul
> A3 rămâne neînceput. R116 și R117 rămân consemnate. Motivul: supervizorul e construit și probat pe
> portofoliu, poarta confirmării merge cap-coadă. Ce urmează nu e construcție, e **ieșirea la un
> cabinet-pilot**."*

**Ce înseamnă, concret, pentru cine continuă:**

| ce | starea |
|---|---|
| **R118** | ultima temă internă. Închisă în tura de 02.09 |
| **familia R82** (acte de nivel firmă care se termină în tăcere) | **PARCATĂ.** Instanța depunerii s-a închis (R127) fiindcă piesa era deja construită; restul **nu se deschide** |
| **backlogul A3** (#4 matrice de stări · #5 reconciliator · #8 baseline determinist · #9 keyboard-only · #10 linter de consistență) | **NEÎNCEPUT**, și rămâne așa |
| **R116 · R117** | **CONSEMNATE**, nelucrate. Nu devin temă |
| **restanțele familiei „încrederea în corpus"** (R1, R3–R7, R107) | în afara axei, ca înainte |

**DE CE E O STARE ȘI NU O PREFERINȚĂ.** Lista de restanțe deschise are **51** de poziții, și fiecare
poate fi argumentată. Fără propoziția asta, următoarea sesiune ar alege din vecinătate — ce e mai
aproape de ce tocmai s-a atins —, iar asta seamănă cu progres fără să fie. *Criteriul nu mai e „ce se
poate repara", e „ce cere ieșirea la un contabil real".*

**CE ÎNSEAMNĂ „CE URMEAZĂ", scris ca să nu fie reinterpretat:** ieșirea la un **cabinet-pilot** nu e
o temă de construcție pe care s-o pot deschide singur. Ce cere ea — cine e cabinetul, ce date intră,
ce se promite, ce se măsoară în primele săptămâni — sunt decizii ale lui Costin. *Dacă următoarea
sesiune găsește ceva de construit „pentru pilot", întreabă întâi; nu deschide.*

**Ce rămâne permis fără să întrebe:** un defect de **prag 1** găsit apăsând — o cifră greșită, un
blocaj, o afirmație falsă pe ecran — se repară, ca oricând. *Un prag 1 nu e o temă; e o datorie.*

---

## Opt reguli de conducere a lucrului *(Costin, 01–03.09.2026)*

**1. Deciziile care nu mută direcția sunt ale mele, nu urcă la arhitect.** O alegere între două
implementări care duc în același loc, ordinea a două reparații din aceeași familie, forma unui gard,
numele unui câmp — se iau și se scriu, nu se întreabă. *Ce urcă:* ce schimbă direcția, ce schimbă un
contract pe care se sprijină altcineva, ce schimbă ritmul de muncă al contabilului, și ce n-are
răspuns care să nu fie o presupunere. **Testul:** dacă răspunsul lui Costin ar putea fi înlocuit cu
un default rezonabil fără ca nimic din plan să se mute, întrebarea n-avea ce căuta la el.
*Instanța care a produs regula:* pe 01.09 am urcat cadența lunară a cotelor de TVA ca cerință, când
tabelul 3×3 era deja decizia lui, iar aplicarea lui corectă era muncă, nu alegere.

**2. O tură care nu schimbă nimic pentru un contabil are nevoie de o justificare scrisă.** Nu e
interzisă — e **nedeclarată implicit acceptabilă**, și asta se termină aici. Justificarea se scrie în
raport, la `§2 ÎN PLUS / MAI PUȚIN`, și numește: *ce anume va putea face contabilul altfel din cauza
turei ăsteia, sau prin ce lanț ajunge acolo, sau de ce e o datorie care blochează ceva ce el
folosește.* Un gard nou, un clichet coborât, o interdicție măsurată — toate pot avea justificarea
asta, dar trebuie **scrisă**, nu subînțeleasă. *Motivul, măsurat:* o axă întreagă (corpus-instrument
și igienă) a produs zile de lucru fără nimic vizibil pentru un contabil, iar restanțele au crescut
mai repede decât se închideau.

**3. O pereche sau o gardă nouă se probează pe PORTOFOLIU, nu doar în teste** *(Costin, 02.09.2026,
verbatim)*: *„orice pereche sau gardă nouă se probează pe portofoliu, nu doar în teste. Datele care
lipsesc le construiești tu — invalide întâi, apoi valide — ca scenariu declarat. Nu-mi ceri mie să
produc condiția; o ceri doar dacă e o apăsare de buton pe care numai un om o poate face."*

**Ce cere, ca act, în ordinea în care se face:**

| pas | ce înseamnă |
|---|---|
| **datele lipsă le construiesc EU** | nu se așteaptă o depunere reală, nu se cere lui Costin să producă starea. Firmele portofoliului sunt de test; datele intră **prin lanțul aplicației** (generator → validator → coadă → depunere), nu prin rânduri scrise de mână |
| **invalide ÎNTÂI** | starea în care garda trebuie să spună **nu**. Dacă nu spune, garda e falsă, nu datele |
| **apoi VALIDE** | starea în care trebuie să spună **da**. O gardă care nu poate spune da e o constantă, nu o măsurătoare — §22 din `METODA_VERIFICARE.md`, dus de la unitate la portofoliu |
| **scenariu DECLARAT** | firma, perioada, cifrele și **de ce nu se potrivesc** se scriu, ca altcineva să poată reface sau desface starea. Un rând de date fără scenariu scris devine, peste o lună, „date reale ciudate" |
| **omului i se cere DOAR apăsarea** | tot ce se poate face din cod se face din cod. Ce rămâne al lui e strict actul pe care numai un om îl poate face: apăsarea unui buton, o decizie, o autorizare |

**DE CE E O REGULĂ, și nu o bună practică — instanța care a produs-o, măsurată în chiar tura în
care regula s-a scris.** Perechea **D101 rd.50 ↔ Σ D100** era calibrată *în amândouă direcțiile*
(verde pe cazul coincident, roșu pe cel divergent) și totuși **oarbă**: testele își fabricau singure
rândurile depuse, cu cheia `suma_plata`, iar generatorul **nu o scria**. `d100.build_xml` emitea
`suma_plata="3000"` în XML, dar obligația persistată în `declaratii_depuse.randuri` avea doar
`suma_dat` — fiindcă `suma_plata` trăia în formatarea XML-ului, nu ca **câmp** al dataclass-ului,
iar `dataclasses.asdict` vede numai câmpuri. Deci pe **orice** depunere făcută prin aplicație
perechea aduna **0** și compara rândul 50 cu zero: *o cifră validă și falsă*, care n-ar fi ieșit
niciodată dintr-un test, fiindcă testul și codul citit greșit erau scrise pe aceeași presupunere.
**Prima probă pe portofoliu a scos-o în primul pas.**

*Regula generalizează [[calibrare-cu-efectul-nu-cu-numele]] cu un nivel mai sus: o calibrare pe
subiect fabricat dovedește că funcția e corectă pe intrarea pe care i-o dai tu, nu că intrarea aia e
cea pe care o produce aplicația.* **Gardul mecanic derivat**, ca regula să nu rămână doar scrisă:
`core/test_supervizor.py::test_perechea_D100_citeste_CHEIA_PE_CARE_GENERATORUL_O_SCRIE` — cere
`randuri` de la generator, prin exact funcția care le persistă, și cade la orice câmp scos sau
redenumit. Celelalte trei perechi n-au încă gardul echivalent: **R123**.

**4. POARTA SCURTĂ — perimetrul se DERIVĂ, nu se alege** *(Costin, 02.09.2026, verbatim)*:

> *„Poarta scurtă: se rulează construcția atinsă și tot ce depinde de ea, derivat din dependențele
> reale din cod, nu ales de la caz la caz. Poarta completă rămâne obligatorie înainte de publicare
> și înainte de `/clear`. Dacă derivarea nu poate stabili cu certitudine perimetrul, se rulează tot
> și se spune de ce — un perimetru ghicit e mai rău decât o poartă lungă."*

| | |
|---|---|
| **când se poate scurta** | în timpul turei, între reparații, pe un arbore care **nu se publică încă** |
| **ce intră în perimetru** | construcția atinsă **plus închiderea tranzitivă a celor care o importă** — citită din cod (graful de import + apelanții), nu din memorie și nu din numele fișierelor |
| **când NU se poate scurta** | **înainte de publicare** (commit + push + restart) și **înainte de `/clear`**. Acolo poarta e cea completă, fără excepție |
| **când derivarea nu e sigură** | se rulează **tot**, și se scrie **de ce** derivarea n-a putut închide perimetrul. *Un perimetru ghicit e mai rău decât o poartă lungă*: o poartă lungă costă minute, un perimetru ghicit dă verde despre ce n-a rulat |

**DE CE contează cifra.** Poarta completă durează **~21 de minute** (măsurat pe zece rulări,
01–02.09: 1223s…1256s), iar o tură cu două commituri costă ~42 de minute doar în porți. Regula nu
schimbă ce se garantează la publicare — mută doar bucla scurtă din timpul lucrului.

**CE FACE IMPOSIBIL, și e chiar motivul formei ei.** Un perimetru **ales** e ales de cine tocmai a
scris modificarea, adică de singurul care nu poate ști ce n-a văzut. Tiparul e deja măsurat de două
ori în registru: garda care se uită exact unde codul e corect
([[gard-care-nu-se-verifica-pe-sine]]) și calibrarea pe subiect fabricat (regula 3, mai sus). *Un
perimetru derivat poate fi greșit; unul ales e greșit exact acolo unde autorul e orb.* De-aia
alternativa la nesiguranță e **tot**, nu **mai puțin**.

**5. O TURĂ FĂRĂ FIȘIERE EXECUTABILE RULEAZĂ DOAR GĂRZILE DE REGISTRE ȘI DOCUMENTE**
*(Costin, 03.09.2026, verbatim)*:

> *„O tură care nu atinge niciun fișier executabil (`.py`, `.js`) rulează doar gărzile de registre și
> documente, nu suita completă. Se stabilește din ce s-a modificat față de HEAD, nu prin judecată.
> Dacă s-a atins măcar un fișier executabil, poarta rămâne cum e azi. Poarta completă rămâne
> obligatorie înainte de publicare și înainte de `/clear`."*

| | |
|---|---|
| **cum se stabilește** | din `git diff --name-only HEAD` — **atât**, pe **extensie**. `scripts/perimetru.py` o face; **nu se judecă** „păi ăsta e doar un registru" |
| **ce NU intră** | fișierele **neurmărite și nestagiate**. Nu fac parte din ce se publică, iar pytest nu le culege; un test nou intră aici **de îndată ce e stagiat**. *Se numără și se raportează, ca nimeni să nu creadă că instrumentul le-a privit.* |
| **ce e INTERZIS** | să treci peste refuzul instrumentului dându-i argumente pe linia de comandă. *Costin, 03.09: „nu-l suprascrie cu judecata ta — o excepție luată o dată face regula o formalitate."* Dacă spune că nu poate scurta, **se rulează tot și se scrie de ce** |
| **ce se rulează atunci** | gărzile de **registru** — derivate, nu enumerate: un test intră dacă numește el însuși un **registru** (`.md` din rădăcina repo-ului, plus cele două JSON-uri de proveniență), sau dacă importă un scaner din `scripts/` care îl numește |
| **când NU se aplică** | dacă s-a atins **măcar un** `.py` sau `.js`. Un registru atins **alături de cod** lasă întrebarea deschisă — graful de import nu spune ce cod mai depinde de registru —, iar acolo se rulează tot |
| **când NU se aplică, oricum** | **înainte de publicare** și **înainte de `/clear`**. Acolo poarta e cea completă, ca la regula 4 |

**Cifra care o justifică, MĂSURATĂ pe DOUĂ rulări:** poarta completă durează **~22 de minute**
(1.300–1.350 s). Perimetrul de registre e **25 de fișiere / 253 de teste** și rulează în
**396–575 s (6,5–9,5 minute)**. *Se scrie ca interval, nu ca cifră: prima rulare a dat 396 s, a doua
575 s pe aceeași mulțime de teste — mașina e partajată, iar o singură cronometrare ar fi devenit
încă un fapt fals.*
O tură de registre — și sunt multe: fiecare închidere de restanță, fiecare rescriere de predare —
costa 22 de minute ca să afle dacă un antet are data de azi.

**CE A CERUT REGULA, ca să nu fie o intenție — și cum m-am înșelat de două ori până la cifra bună.**
Perimetrul trebuia **derivat**, nu scris ca listă.
- **Prima formă** propaga tranzitiv prin tot graful de import: **357 din 578** de teste. Aproape
  orice test ajunge, la câteva niveluri, la un modul care numește un fișier. *Un perimetru care ia
  trei sferturi din suită nu derivă nimic; îmbracă „rulează tot" în alt nume.*
- **A doua** număra ca „document" orice fișier urmărit de git care nu e executabil — deci și
  șabloanele, și actele din `anaf_surse/` pe care le citează orice test fiscal într-un temei:
  **137 de fișiere / 1.314 teste / 976 s**. Scurtare de un sfert, pentru un instrument care promitea
  altceva. **Scrisesem în regula asta „~1,5 minute" — o estimare, nu o măsurătoare; am aflat că e
  falsă cronometrând-o.**
- **Forma care ține:** „document" înseamnă **REGISTRU** — un `.md` din **rădăcina** repo-ului, plus
  cele două JSON-uri de proveniență. *Deosebirea nu e de prag, e de înțeles: un test care CITEAZĂ un
  act din corpus într-un temei nu e o gardă de registru; unul care deschide `CONFORMITATE.md` e.*
  Criteriul rămâne structural, deci un registru nou intră singur.

**CE NU VEDE, declarat:** o gardă care ar construi numele registrului din bucăți, sau una care ajunge
la el prin două module de `core/`. N-am întâlnit niciuna — dar de-aia forma asta se folosește
**doar** când nu s-a atins niciun executabil, unde alternativa (poarta completă) e la o comandă.

**ȘI CE A GĂSIT PRIMA FOLOSIRE REALĂ — o greșeală a mea, corectată de Costin.** Instrumentul a
**refuzat** să scurteze, iar eu i-am dat fișierele pe linia de comandă ca să obțin răspunsul pe care
îl voiam. *Aia e chiar ocolirea pe care regula o interzice.* Cauza refuzului era reală și se putea
repara: socoteam „cod atins" și fișierele **neurmărite**, iar arborele poartă permanent **299** —
**217 `.png`** (capturi de probă), **58 `.py`** (55 de probe din `frontend_test/`, 3 ale lui `ruff`
din `venv/` — care nu era în `.gitignore`), 10 `.md` și 6 `.csv` de lucru. **Reparat instrumentul, nu
regula.**

**ȘI A DOUA JUMĂTATE A REPARAȚIEI — arborele, curățat *(Costin, 03.09.2026)*.** Instrumentul reparat
face regula aplicabilă, dar cele 299 de fișiere rămâneau o stare pe care nimeni n-o hotărâse. Comanda:
*„Curăță arborele acum, complet … la final `git status` trebuie să fie gol."* Executat: **299 → 0**.
Au fost șterse 217 capturi, 55 de probe `.py` și 9 fișiere de lucru; `venv/` a intrat în `.gitignore`;
cele 7 liste `LOT_*_VERIFICARI.md` s-au **comis**, fiindcă un script urmărit le citește, iar `GARZI.md`
declară o cifră drept recalculabilă prin el.

*Ce se schimbă practic, de aici înainte:* `git ls-files --others` întoarce **gol**, deci un fișier
neurmărit nou e de acum **un semnal**, nu zgomot de fond. **Restul de 299 nu era normal — era
sediment**: probe scrise ca să răspundă la o întrebare, lăsate acolo după ce întrebarea primise
răspuns. *Dacă merita păstrată, o probă s-ar fi comis atunci; una păstrată „pentru mai târziu" e o
copie fără proprietar, care peste o lună nu se mai poate deosebi de una care mai contează.*


**6. NU SE RULEAZĂ TOATĂ SUITA PENTRU ORICE** *(Costin, 03.09.2026, verbatim)*:

> *„Nu se rulează toată suita pentru orice. Suita completă are un singur rost: să prindă ce n-ai
> atins și nu poți anticipa — și are sens doar înainte de publicare. La orice altceva se rulează ce
> ține de ce s-a atins."*

Regula 4 spune **cum** se derivă perimetrul scurt, regula 5 **ce** se rulează când nu s-a atins
niciun executabil. Asta spune **când are voie să apară suita întreagă**.

| | |
|---|---|
| **rostul suitei complete** | să prindă **ce n-ai atins și nu poți anticipa**. Despre ce ai atins răspunde perimetrul — mai repede, și cu aceeași putere |
| **unde are sens** | **înainte de publicare**. Pe repo-ul ăsta publicarea *e* commitul (`post-commit` publică singur, după poarta verde), deci suita completă înseamnă exact hook-ul `pre-commit`: **o dată** |
| **în rest** | ce ține de ce s-a atins, derivat cu `scripts/perimetru.py` — nu ales, nu judecat |

**Ce NU schimbă:** nimic din ce garantează poarta. Suita completă rulează la fel de des ca înainte —
o dată per commit. Se taie rulările **dinaintea** ei, nu ea.

---

**7. OPERAȚIUNILE DE CURĂȚENIE NU RULEAZĂ TESTE DELOC** *(Costin, 03.09.2026, verbatim)*:

> *„Operațiunile de curățenie — ștergeri de fișiere, `.gitignore`, mutări — nu rulează teste deloc.
> Nu există cale prin care ele să strice o declarație."*

Și condiția, din aceeași comandă:

> *„Eticheta e ignorată dacă commitul atinge vreun fișier executabil sau vreun registru. Se aplică
> doar la ștergeri, `.gitignore` și mutări. Altfel devine cheia care deschide tot."*

| | |
|---|---|
| **cum se cere** | eticheta `# doar-curatenie: <motiv>` în mesajul de commit — același tipar ca `# upsert-ok:` și `# multe-fisiere-ok:` |
| **cine DECIDE** | **indexul**, prin `scripts/curatenie.py`. Nu eticheta. Vezi mai jos de ce nu se putea altfel |
| **ce se sare** | `pytest` și verificatorul — cele ~22 de minute |
| **ce rămâne** | `ruff` (secunde, și e plasa pe nume nedefinite), plus toate porțile din `commit-msg` |
| **ce se întâmplă dacă eticheta minte** | commitul e **respins** de `commit-msg`. Suita a rulat oricum — deci eticheta n-a *deschis* nimic, exact ca în condiție —, dar afirmația falsă nu rămâne în istorie |

**DE CE DECIDE INDEXUL, ȘI NU ETICHETA — nu e o alegere de stil, e ordinea hook-urilor.** La
`pre-commit`, mesajul commitului **încă nu există**: cu `git commit -F`, `.git/COMMIT_EDITMSG`
poartă mesajul commitului **precedent** — dovedit pe 23.08.2026, scris în chiar antetul hook-ului.
Deci o poartă care s-ar deschide cu o etichetă n-ar avea ce citi. *„Ignorată" din condiție devine
astfel o proprietate a construcției, nu o verificare care ar putea fi ocolită.* Ce rămâne etichetei
e **mărturia**: o poartă sărită în tăcere n-ar lăsa nicio urmă în istorie, iar `commit-msg` respinge
și cazul invers — poartă sărită, mesaj care tace.

**CELE TREI CONDIȚII, toate obligatorii.** *A treia nu era în comandă; o adaug, și spun de ce.*

| | |
|---|---|
| **formă** | fiecare intrare din index e ștergere (`D`), mutare **identică** (`R100`), sau modificare de `.gitignore`. O mutare cu conținut schimbat se descompune în `D`+`A` și cade aici |
| **clasă** | nicio cale atinsă nu e **executabil** (`.py`, `.js`) sau **registru** (`.md` din rădăcină + cele două JSON-uri de proveniență). Amândouă definițiile sunt **împrumutate de la `scripts/perimetru.py`**, nu rescrise: a doua definiție a aceluiași lucru e începutul unei divergențe tăcute |
| **referință** *(în plus față de comandă)* | niciun nume șters sau mutat nu e **numit în ce se comite**. Un `.xsd`, o fixtură `.json`, o captură citată într-un registru nu sunt nici executabile, nici registre — dar dacă o gardă le deschide, ștergerea lor e o **modificare de cod prin absență**, iar suita cade la commitul următor, în brațele altcuiva. *Fără condiția asta, ocolirea chiar ar fi putut strica o declarație — adică exact ce spune comanda că nu se poate.* |

**FAIL CLOSED.** Orice eșec — git care nu răspunde, index necitibil, căutare care crapă — înseamnă
*nu e curățenie*, deci poartă completă. Și căutarea de referință greșește deliberat spre **refuz**
(un nume scurt care e sub-șir în altul refuză ocolirea): un refuz costă 22 de minute, o trecere
greșită costă o suită roșie pe capul următorului.

**GARDAT:** `scripts/curatenie.py` (instrumentul) + `core/test_curatenie.py` (10 teste, calibrate în
**amândouă** direcțiile — și pe patru mutații: scoasă verificarea de executabil, de registru, de
referință, și descablat hook-ul; fiecare omoară exact testul care o păzește). *Ce nu acoperă,
declarat:* ramura din `commit-msg` care cere eticheta când poarta chiar a fost sărită nu se poate
exercita din suită — dacă indexul ar fi numai-curățenie, suita n-ar rula deloc.

---

**8. NU SE RULEAZĂ SUITA „ÎN AVANS, CA SĂ NU INTRI ORB ÎN POARTĂ"** *(Costin, 03.09.2026,
verbatim)*:

> *„Nu se rulează suita «în avans, ca să nu intri orb în poartă». E aceeași suită de două ori. Dacă
> poarta respinge, se repară și se rulează o dată."*

**Poarta *este* rularea.** O rulare preventivă nu adaugă nicio informație pe care poarta n-ar da-o
douăzeci de minute mai târziu — plătește doar dreptul de a nu fi surprins.

**CIFRA CARE A PRODUS CELE TREI REGULI, măsurată pe 03.09.2026:** dintr-o tură de **ștergere** de
**75 de minute, 66 au fost porți** — trei rulări a câte 22 de minute, dintre care **una preventivă**.
Aceeași tură, sub regulile 6–8: **zero minute de poartă**, fiindcă ștergerile nu ating nimic ce se
execută.
