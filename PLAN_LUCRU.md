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
