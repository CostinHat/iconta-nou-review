---
title: Retururile unui magazin online în e-Factura
description: Cum se corectează facturile pentru bunuri returnate în sistemul RO e-Factura, ce document se emite și cum se ajustează baza de impozitare a TVA conform Codului fiscal.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum gestionez retururile unui magazin online în e-Factura?

Un retur nu se rezolvă prin ștergerea facturii inițiale — factura o dată transmisă în RO e-Factura rămâne în sistem. Corectarea se face printr-un document nou, cu reguli precise stabilite de Codul fiscal.

### Cadrul general: RO e-Factura

Sistemul național de facturare electronică este reglementat de OUG nr. 120/2021 privind administrarea, funcționarea și implementarea sistemului național privind factura electronică RO e-Factura. Odată transmisă în sistem, o factură primește un identificator unic (index de încărcare) și nu poate fi retrasă sau ștearsă — orice modificare ulterioară a valorilor facturate se face printr-un document distinct, tot electronic, tot prin sistemul RO e-Factura.

### Cum se corectează o factură pentru un bun returnat

Codul fiscal (Legea nr. 227/2015) reglementează explicit corectarea facturilor la art. 330. Pentru o factură deja transmisă beneficiarului, sunt două variante:

- se emite o factură nouă care cuprinde, pe de o parte, datele facturii inițiale, numărul și data acesteia, cu valorile trecute cu semnul minus, iar pe de altă parte informațiile și valorile corecte; sau
- se emite concomitent o factură cu valorile corecte și o factură separată cu valorile cu semnul minus, în care se menționează numărul și data facturii corectate (art. 330 alin. (1) lit. b)).

Practic, pentru un retur total, a doua variantă înseamnă o factură de stornare (cu semnul minus, egală cu factura inițială) — fără o factură nouă de vânzare, pentru că nu mai există livrare.

### Ajustarea bazei de impozitare a TVA

Un retur de marfă e unul dintre cazurile explicite în care Codul fiscal impune reducerea bazei de impozitare a TVA: art. 287 lit. b) prevede ajustarea „în cazul refuzurilor totale sau parțiale privind cantitatea, calitatea ori prețurile bunurilor livrate sau ale serviciilor prestate, precum și în cazul desființării totale ori parțiale a contractului pentru livrarea sau prestarea în cauză". Factura de corecție cu semnul minus e instrumentul prin care furnizorul reduce atât venitul, cât și TVA colectată aferentă valorii returnate.

### Pașii practici

1. **Identifică factura inițială** din sistemul propriu (nu se caută în RO e-Factura numărul „vechi" pentru a-l edita — nu se poate).
2. **Emite factura de corecție** (stornare totală sau parțială, după caz) cu referire explicită la numărul și data facturii corectate, conform art. 330 alin. (1) lit. b) din Codul fiscal.
3. **Transmite factura de corecție** prin RO e-Factura, la fel ca orice altă factură emisă — termenul de transmitere e cel general aplicabil facturilor, nu unul separat pentru retururi.
4. **Reflectă ajustarea în decontul de TVA** al perioadei în care s-a emis factura de corecție, ca reducere a bazei de impozitare potrivit art. 287 lit. b).
5. Pentru retur parțial (client păstrează o parte din comandă), factura de corecție reflectă doar diferența — nu se stornează integral urmată de o factură nouă, decât dacă fluxul intern o cere.

### Ce nu trebuie făcut

Nu se modifică manual, în afara sistemului, o factură deja raportată în RO e-Factura, chiar dacă eroarea e minoră. Orice corecție — inclusiv un simplu retur de marfă fără dispută asupra prețului — trece prin fluxul de corectare al art. 330, pentru că sistemul e conceput să păstreze istoricul complet al facturilor, inclusiv al celor stornate.
