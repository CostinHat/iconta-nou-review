---
title: Cum se raportează autofacturile în D406?
description: În SAF-T, autofactura se raportează ca orice factură, în SalesInvoices sau PurchaseInvoices, dar cu tipul de factură 389 și cu indicatorul de autofacturare completat corect, conform schemei aprobate prin OPANAF 1783/2021.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se raportează autofacturile în D406?

Autofactura nu are o secțiune separată în D406. Se raportează în aceeași structură ca facturile obișnuite, dar are un cod propriu: **389**. Codul apare în câmpul „tip factură” și, în cazul autofacturării pe bază de acord, și în indicatorul de autofacturare.

### Ce spune schema SAF-T

Anexa 1 la OPANAF 1783/2021 spune că subsecțiunile SalesInvoices (facturi de vânzare) și PurchaseInvoices (facturi de achiziție) conțin, printre altele, „indicatorul privind autofacturarea”. Detaliile sunt în schema de raportare publicată de ANAF (pct. 6 din aceeași anexă). În schemă contează două câmpuri din structura facturii:

- **S.I.9 InvoiceType** este obligatoriu și se validează cu nomenclatorul Nom_Tipuri_facturi. Nomenclatorul enumeră codurile folosite: 380 (factură), 381 (notă de credit), 384 (factură corectată), 389 (autofactură) și 751. Pentru codul 389 precizează: „Autofactură (indiferent de situația care a generat emiterea autofacturii)”.
- **S.I.13 Self-billing indicator** este tot obligatoriu. Regula semantică este: „Utilizați numai codul 389 pentru autofactură sau altfel cu valoarea 0 (zero)”. Observația de la câmp îl leagă de facturile emise „în numele și pe seama furnizorului, pentru care există un acord de autofacturare”.

### Ce autofacturi pot apărea

Codul fiscal cere autofactura în mai multe situații:

- art. 319 alin. (8): persoana înregistrată conform art. 316 autofacturează livrările și prestările către sine;
- art. 319 alin. (9): transferurile în alt stat membru și operațiunile asimilate achizițiilor intracomunitare;
- art. 319 alin. (3): beneficiarul emite autofactură pentru ajustarea taxei deductibile când furnizorul nu emite factura de corecție;
- art. 319 alin. (18): beneficiarul emite factura în numele și în contul furnizorului. Aceasta este autofacturarea pe bază de acord, pentru care art. 319 alin. (20) lit. k) cere mențiunea „autofactură”.

### Cum se completează practic

1. **Stabiliți subsecțiunea după sensul operațiunii.** O autofactură prin care colectați taxa pentru o livrare către sine intră la vânzări. Autofactura emisă de beneficiar în locul furnizorului se reflectă la achiziții, pentru că documentul descrie o achiziție.
2. **Completați InvoiceType cu 389** pentru orice autofactură. Nomenclatorul spune expres că situația care a generat-o nu contează.
3. **Completați Self-billing indicator cu 389** când există acord de autofacturare în sensul art. 319 alin. (18). În celelalte cazuri, verificați cu validatorul ANAF ce valoare acceptă. Regula schemei este fie 389, fie 0.
4. **Alegeți codul de taxă (TaxCode)** din nomenclatorul potrivit operațiunii: livrări, achiziții sau note contabile. Autofactura nu are un cod de taxă propriu. Codul urmează regimul TVA al operațiunii.
5. **Verificați corespondența cu GeneralLedgerEntries.** Aceeași autofactură trebuie să apară și în înregistrările contabile, pe conturile folosite efectiv.

### Exemplu

O societate plătitoare de TVA ia din stoc bunuri de 2.000 lei pentru a le da gratuit, iar operațiunea este taxabilă ca livrare către sine. Emite autofactura AF-12 cu TVA 21%, adică 420 lei. În D406, AF-12 apare în SalesInvoices cu InvoiceType 389, cu baza de 2.000 lei, cu TVA de 420 lei și cu codul de taxă al livrărilor la cota de 21%. În registrul-jurnal apare nota contabilă corespunzătoare.

### De reținut

- Autofactura se raportează în SalesInvoices sau PurchaseInvoices, după sensul operațiunii. Nu are secțiune proprie.
- InvoiceType 389 se folosește pentru orice autofactură (nomenclatorul Nom_Tipuri_facturi).
- Self-billing indicator este obligatoriu: fie 389, fie 0. Cazul-tip pentru 389 este acordul de autofacturare din Codul fiscal art. 319 alin. (18).
- Rulați validatorul ANAF înainte de depunere. Nomenclatoarele se actualizează, iar codurile greșite duc la respingerea fișierului.
