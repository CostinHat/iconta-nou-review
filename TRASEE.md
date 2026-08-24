# TRASEE — ce parcurge fiecare lucru prin aplicație

Al patrulea document. Celelalte trei spun **cum trebuie construit**, **ce se măsoară** și **când**. Ăsta spune **ce se întâmplă cu un document, de la intrare până la ieșire** — și e ce lipsea când s-a verificat E1.

Consecința lipsei, măsurată: s-a verificat că D301 iese și se validează, dar nu că traseul până la el e complet. Coada „De depus" conținea trei declarații care n-au trecut prin validator. N-a ieșit din nicio măsurătoare — a ieșit fiindcă cineva a apăsat un buton.

---

## Cum se folosește

**Un traseu se parcurge, nu se citește.** Verificarea unui artefact înseamnă parcurgerea traseului lui, pas cu pas, pe date reale, cu ce trebuie să fie adevărat după fiecare pas.

**Un artefact care iese corect la capătul unui traseu nesparcurs nu e verificat.** E doar produs.

**Ce e scris aici din conversație e marcat `[știut]`. Ce trebuie completat din cod e marcat `[de completat]`.** Nu se inventează pași plauzibili — e chiar greșeala care a produs 13 ghiduri greșite din 40.

---

## Ce poartă un traseu

| element | ce conține |
|---|---|
| **precondiții** | ce trebuie să existe în firmă ca traseul să poată fi parcurs |
| **pașii** | în ordine, fiecare cu ce declanșează trecerea la următorul |
| **ce se verifică după fiecare pas** | nu că pasul a mers — ce trebuie să fie adevărat după el |
| **stările** | în ce stare e obiectul după fiecare pas |
| **cine** | ce rol poate face fiecare pas |
| **traseele negative** | ce se întâmplă când ceva lipsește sau e respins |
| **ce nu are voie** | tranzițiile interzise |

---

# I. DECLARAȚIA

## Traseul principal

```
1. DATELE EXISTĂ ÎN EVIDENȚĂ
      ↓
2. GENERARE
      ↓
3. VALIDARE cu instrumentul oficial
      ↓
4. INTRARE ÎN COADĂ
      ↓
5. APROBARE  (patru ochi, dacă politica e activă și posibilă)
      ↓
6. CONFIRMARE DEPUNERE  (cu index de la autoritate)
      ↓
7. DEPUSĂ
```

### Ce se verifică după fiecare pas

**După 1 — datele:** `[știut]` operațiunile care trebuie să intre în declarație sunt în evidență, nu doar în documente. Cazul care a produs regula: TVA colectată pe facturi în stare `de_preluat`, excluse tăcut din D300.

**După 2 — generarea:** `[știut]` fiecare operațiune din evidență care ar trebui să apară, apare. Absența unei operațiuni nu e vizibilă în structura declarației — D300 cu 18 din 19 e perfect coerent.

**După 3 — validarea:** `[știut]` verdictul se păstrează, cu data și cu ce a spus validatorul. **Un verdict care nu se păstrează nu s-a produs.**

**După 4 — coada:** `[știut]` o declarație intră în coadă **numai cu verdict de validare**. Coada înseamnă „gata de depus", nu „generată".

**După 5 — aprobarea:** `[știut]` cine a aprobat se consemnează. Dacă patru ochi e activ și posibil, cel care aprobă nu e cel care a pregătit.

**După 6 — confirmarea:** `[de completat]` ce se schimbă efectiv — starea, indexul, momentul, autorul.

**După 7 — depusă:** `[de completat]` ce se poate și ce nu se mai poate face cu ea.

### Traseele negative

`[de completat]` — validatorul respinge · autoritatea respinge · datele se schimbă după generare · declarația se retrage · rectificativa.

**Cel puțin astea trebuie să existe ca trasee, nu ca erori.** O respingere nu e un eșec al aplicației; e o stare a documentului.

### Ce nu are voie

`[știut]` O declarație în coadă fără verdict de validare.
`[știut]` O declarație marcată depusă fără să fi trecut prin validare.
`[de completat]` Restul.

---

# II. FACTURA EMISĂ

```
1. CREARE
      ↓
2. STARE  ──  emisa / de_preluat  [știut: două căi de creare, două stări]
      ↓
3. CONTABILIZARE  [știut: nu se face automat; propunerea de conturi lipsește]
      ↓
4. INTRĂ ÎN: D300 · D394 · e-Factura · jurnalul de vânzări
```

**Ce se verifică:** `[știut]` o factură emisă apare în toate ieșirile care o cuprind. Cazul: `de_preluat` era exclus din D300 și inclus în export.

`[știut]` Cele două căi de creare — `creeaza_factura` (7 apelanți, pune `emisa`) și `emite_factura` (6 apelanți, pune `de_preluat`) — produc două populații în aceeași firmă, iar starea nu se mai schimbă niciodată.

**Ce nu are voie:** `[știut]` o factură fără cod fiscal de partener — nu intră în D394 și nu se corelează în VIES.

---

# III. STATUL DE PLATĂ ȘI FLUTURAȘUL

```
1. PONTAJ
      ↓
2. CALCUL  (contribuții, deduceri, facilități, concedii medicale)
      ↓
3. EMITERE STAT  [știut: înghețat cu amprentă, exemplar numerotat]
      ↓
4. FLUTURAȘ  [știut: randare peste rândul statului, nu al doilea calcul]
      ↓
5. PREDARE  [de completat: se marchează?]
      ↓
6. D112
```

**Ce se verifică:** `[știut]` fluturașul și D112 spun același lucru despre aceeași lună. Cazul: fluturașul acorda 920 lei tichete pe care statul nu-i dădea.

`[știut]` Podeaua part-time e aceeași în stat și în declarație.

**Precondiții:** `[știut]` pontajul trebuie să existe — fără el, tichetele se blochează, iar calculul stă pe zile presupuse.

---

# IV. CONCEDIUL MEDICAL

```
1. CERTIFICAT INTRODUS  (cod indemnizație, perioadă, inițial / în continuare)
      ↓
2. VERIFICARE ÎNAINTE DE PLATĂ  [știut: obligație legală de a respinge certificatele greșite]
      ↓
3. CALCUL  (media pe 6 luni, procentul pe episod, diminuarea)
      ↓
4. INTRĂ ÎN STAT DE PLATĂ
      ↓
5. D112
```

**Ce se verifică:** `[știut]` media pe 6 luni se calculează din sursă, nu dintr-un tabel intermediar. Cazul: media depindea de ce ecrane deschisese cineva.

`[știut]` Procentul se determină pe episod, nu pe certificat. Diminuarea se aplică o dată pe episod.

---

# V. NOTA CONTABILĂ

```
1. DOCUMENT (factură, extras, stat)
      ↓
2. PROPUNERE DE CONTURI  [știut: NU EXISTĂ]
      ↓
3. CONFIRMARE DE CĂTRE OM  [știut: ecranul există, ruta există]
      ↓
4. NOTĂ SALVATĂ
      ↓
5. INTRĂ ÎN: registrul-jurnal · cartea mare · balanță · D406
```

**Starea măsurată:** `[știut]` 9.981 din 10.023 de facturi n-au notă. Cele 42 cu notă au fost create manual, prin ecran.

**Ce se verifică:** `[știut]` nota poartă documentul justificativ — felul, numărul, data. Fără el, registrul-jurnal nu e conform, iar lanțul P14 e rupt.

---

# VI. TRASEE DE COMPLETAT DIN COD

`[de completat]` — nu le scriu din presupunere:

importul de e-Factura · extrasul bancar și potrivirea · NIR și recepția · casa și registrul de casă · inventarierea · închiderea de lună · închiderea de an și situațiile financiare · trecerea de regim fiscal · preluarea unei firme.

Pentru fiecare, aceeași structură: precondiții, pași, ce se verifică după fiecare, stări, cine, trasee negative, ce nu are voie.

---

# VII. CE MAI TREBUIE PENTRU TESTARE, ÎN AFARĂ DE TRASEE

Ce n-am spus până acum și lipsește la fel de mult.

## 1. Stările și tranzițiile legale

Pentru fiecare obiect — declarație, factură, stat, notă, perioadă — lista completă a stărilor și ce trecere e permisă din fiecare.

**Fără ea, o stare greșită nu se poate recunoaște.** Cazul: `de_preluat` însemna două lucruri opuse în două module, iar nimic n-o contrazicea.

**Și tranzițiile interzise, explicit:** ce nu se poate întoarce. O perioadă închisă. O declarație depusă. Un document emis.

## 2. Rolurile — cine poate face fiecare pas

Ce poate un asistent, ce poate un administrator de cabinet, ce poate superadmin.

**Contează pentru testare:** verificarea cu un cont care poate tot nu testează restricția. Patru ochi verificat cu superadmin nu verifică patru ochi.

## 3. Precondițiile — ce date trebuie să existe

Pentru fiecare traseu: ce trebuie să aibă firma ca traseul să poată fi parcurs.

**Cazul măsurat:** firmele de test au 3–19 note și 3.000 de facturi. Verdictul familiei A din faza 1 a fost dat pe o evidență cu 0,4% acoperire. Nu era greșit — era pe altceva decât credeam.

**Iar de aici decurge:** care firmă poate exercita care traseu. Azi nu se știe.

## 4. Traseele negative

Ce se întâmplă când merge prost — respingere, lipsă, întrerupere, timeout.

**Sunt cele care nu se testează niciodată**, fiindcă nu se produc singure. Iar când se produc, se produc la un client.

## 5. Ce trebuie să fie adevărat DUPĂ fiecare pas

Nu că pasul a mers — ce s-a schimbat în urma lui, verificabil.

**Diferența:** „butonul a funcționat, coada a trecut de la 3 la 2" e o observație. „Declarația are stare depusă, cu autor și moment, iar verdictul de validare e păstrat" e o verificare.

## 6. Ce nu se testează niciodată, și de ce

Traseele care ating exteriorul real: depunerea la autoritate, transmiterea e-Facturii, plata.

**Se declară ca netestabile**, cu ce se poate testa în locul lor — până unde merge traseul intern, și unde se oprește.

Altfel rămân în aer: nici verificate, nici declarate.

---

# VIII. DE UNDE SE COMPLETEAZĂ

**Pașii** — din cod: ce rută cheamă ce, ce stare pune fiecare.

**Ce se verifică după** — din `PLAN_ARHITECTURA`, Partea IV, plus din ce s-a măsurat.

**Stările** — din schemă și din nomenclatoare.

**Rolurile** — din verificările de drepturi.

**Precondițiile** — din ce eșuează când lipsesc datele.

**Traseele negative** — din ce tratează codul azi, plus ce ar trebui să trateze.

**Ce nu are voie** — din interdicțiile din plan, aplicate la traseu.

Un traseu completat din presupunere e mai rău decât unul lipsă: se verifică ceva care nu există, iar verificarea trece.
