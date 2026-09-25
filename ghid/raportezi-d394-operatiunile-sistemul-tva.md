---
title: Cum raportezi în D394 operațiunile din sistemul TVA la încasare
description: Facturile cu mențiunea „TVA la încasare" intră în D394 în funcție de data emiterii, nu de data încasării — regula rămâne valabilă indiferent când devine exigibilă taxa.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum raportezi în D394 operațiunile din sistemul TVA la încasare

Cea mai frecventă greșeală la D394 pentru firmele cu TVA la încasare: se așteaptă încasarea facturii ca să o includă în declarație. Regula e exact opusă — D394 urmărește **emiterea** facturii, nu exigibilitatea taxei.

### Regula pentru livrări/prestări (furnizor)

Instrucțiunile de completare a formularului (394), aprobate prin OPANAF 2194/2025, sunt explicite:

> „Declarația trebuie să conțină facturile care au fost emise în perioada de raportare, inclusiv cele care au înscrisă mențiunea «taxare inversă» sau «TVA la încasare», **indiferent de data la care intervine exigibilitatea TVA**."

Așadar, dacă emiți în septembrie o factură cu mențiunea „TVA la încasare", ea intră în D394 pe septembrie — chiar dacă încasarea (și, odată cu ea, exigibilitatea taxei) se produce abia în noiembrie sau nu se produce deloc în acel an.

### Regula pentru achiziții (client)

Simetric, pentru achizițiile de bunuri/servicii, declarația trebuie să conțină facturile **primite** în perioada de raportare, indiferent de data exigibilității taxei, inclusiv cele cu mențiunea „taxare inversă" sau „TVA la încasare" (aceleași instrucțiuni, OPANAF 2194/2025).

### De ce contează distincția

TVA la încasare (art. 282 alin. 3-8 Cod fiscal) amână doar **exigibilitatea taxei** — momentul în care taxa devine datorată/deductibilă efectiv — nu momentul raportării informative în D394. D394 e o declarație informativă de tranzacții (cine a facturat cui, cât), nu o declarație de TVA de plată; de aceea urmărește documentul emis, nu fluxul de numerar.

Această separare de logică apare și în cazul selectării codului de operațiune corespunzător în formular: la achiziții, pe lângă codurile standard L/A, există un cod dedicat **AÎ** — „achiziții de la persoane impozabile care aplică sistemul de TVA la încasare" — tocmai pentru a marca distinct aceste tranzacții față de achizițiile obișnuite.

### Cine e obligat să depună D394

Persoanele impozabile înregistrate în scopuri de TVA în România conform art. 316 Cod fiscal:
- pentru livrări de bunuri/prestări de servicii taxabile în România, pentru orice operațiune pentru care se emite factură conform Titlului VII din Codul fiscal, inclusiv avansuri și operațiuni cu TVA la încasare;
- pentru achiziții de bunuri/servicii taxabile cu locul livrării/prestării în România (art. 275, respectiv art. 278 Cod fiscal), inclusiv cele cu taxare inversă la beneficiar (art. 307 alin. 2, 3, 5 și 6 și art. 331 Cod fiscal).

Achizițiile intracomunitare care se raportează în D390 nu se mai reintroduc în D394 — instrucțiunile OPANAF 2194/2025 exclud explicit acest dublaj.

### Practic

- Nu aștepta încasarea ca să treci factura în D394 a lunii/trimestrului respectiv — criteriul e data facturii.
- Verifică menționarea corectă a mențiunii „TVA la încasare" pe factură, pentru ca ea să fie corect identificabilă atât la tine, cât și la client.
- La reconcilierea D394 cu jurnalul de vânzări/cumpărări, filtrează după data documentului, nu după data plății — altfel apar diferențe care nu sunt erori, ci pur și simplu o confuzie de criteriu.
