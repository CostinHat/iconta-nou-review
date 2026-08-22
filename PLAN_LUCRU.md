# PLAN DE LUCRU

Al treilea plan, și ultimul. Celelalte două spun **ce** și **în ce ordine**. Ăsta spune **când, cât, unde suntem, și ce ține de om.**

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

**Ce blochează:** accesul la portalul legislativ. Dacă rămâne inaccesibil automat, verificarea vigorii e muncă manuală, iar pragurile din plan trebuie recalibrate.

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

**Excepția care sare peste tot planul:** un defect care produce cifre greșite azi se repară imediat, în orice etapă. Se scrie în registru ca reparat, apoi se continuă.

---

### ⬛ PUNCT DE DECIZIE 3

**Înainte de a da produsul unui contabil.** Se recitește propoziția de la început și se răspunde: e adevărată, și se poate demonstra?

Dacă nu, ce lipsește și cât mai durează.

---

## Unde suntem

**Un singur loc:** `CONFORMITATE.md`, plus un antet nou care spune etapa curentă și ce o termină.

Azi starea e împrăștiată — stările interdicțiilor într-un loc, fronturile deschise în altul, cifrele în rapoarte care se citesc o dată. Un om care se uită nu poate spune unde suntem.

**Antetul registrului conține:**

- etapa curentă și criteriul ei de terminare;
- ce lipsește ca să se termine;
- deciziile care blochează, dacă sunt;
- data ultimei actualizări.

**Se actualizează la fiecare tură**, ca orice registru. Un antet stătut e mai rău decât niciunul.

---

## Ce ține de om, nu de muncă

Deciziile care nu se rezolvă prin efort. Fiecare blochează ceva; niciuna nu se poate lua de altcineva.

| Decizia | Ce blochează | Stare |
|---|---|---|
| **Câte regimuri acoperă E1** | setul de artefacte se face pe regimurile reale, nu pe trei alese arbitrar | **de măsurat la începutul E1** |
| **Se îngheață perimetrul până la conformitate?** | dacă nu, lista de interdicții crește cu fiecare modul nou | **deschis** |
| **Ce se repară și ce nu**, la punctul de decizie 2 | E5 | *la momentul potrivit* |

**Stabilit:**

- **nu există termen calendaristic.** Se termină când trece verificarea. Ce împiedică extinderea la infinit sunt criteriile de terminare per etapă și punctele de decizie — dacă o etapă nu avansează, se schimbă abordarea, nu se prelungește.
- **verificarea o facem noi doi.** Nu se caută un actor din afară; P24 e o revizuire proprie, deliberată.
- **cele 35 de declarații fără interfață se implementează la cerere**, nu preventiv. Nu intră în perimetrul de conformitate.

---

## Ritmul

**O tură = observații pe precedenta + decizii cerute în cap + comanda următoare.** Nu se sare peste prima parte: acolo se prind erorile.

**Ziua se închide cu `ISTORIC.md`.** Nu după fiecare tură.

**Contextul se golește.** Când raportul spune că se apropie de plin, se închide ziua sau se reia cu `PREDARE_LANT.md`. O tură pornită pe context aproape plin produce muncă de întors.

**Observație, nu regulă.** Erorile din ultimele ture ale unei zile lungi au fost de tip transcriere și reconstruire din memorie — două planuri divergente, o regulă pierdută la rescriere. Merită știut ce fel de greșeli apar spre final, ca să fie căutate acolo. Dar haosul obosește mai mult decât munca: un plan care spune unde ești și cât mai ai e el însuși odihnitor.

---

## Ce oprește planul

**Un plan s-a dovedit greșit.** Se modifică prin decizie scrisă, apoi se reia. S-a întâmplat de patru ori într-o zi.

**O măsurătoare n-a fost calibrată.** O cifră fără caz pozitiv găsit nu e rezultat.

**Un defect produce cifre greșite azi.** Se repară pe loc.

**O etapă nu avansează.** Nu se prelungește — se schimbă abordarea, prin decizie scrisă.

---

## Ce nu e în planul ăsta

**Estimări de durată.** Nu se pot face cu date pe care nu le avem. Triajul din faza 3 le produce; până atunci, orice cifră ar fi inventată. Etapele se termină prin criteriu, nu prin calendar.

**Ce se întâmplă după primul contabil.** Un produs care intră în folosință primește o clasă nouă de întrebări — suport, incidente, cereri de funcționalitate. Alt plan, altă dată.

**Legislația care se schimbă.** E întreținere permanentă, nu proiect. Se bugetează separat, nu se speră că se termină.
