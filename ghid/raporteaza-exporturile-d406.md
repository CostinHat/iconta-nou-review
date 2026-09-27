---
title: Cum se raportează exporturile în D406?
description: Exportul de bunuri se raportează în SalesInvoices cu codul de taxă 310313, „livrări scutite cu drept de deducere cf. art. 294 alin. (1) lit. a) și b) (Exporturi)”, cu clientul non-UE identificat cu prefixul 02 sau 06, conform schemei aprobate prin OPANAF 1783/2021.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se raportează exporturile în D406?

Factura de export intră în D406 în subsecțiunea SalesInvoices, ca orice vânzare. Diferența o fac trei elemente: codul de taxă de export, identificarea clientului din afara UE și, de regulă, informația valutară.

### Temeiul scutirii

Codul fiscal art. 294 alin. (1) lit. a) și b) scutește de TVA livrările de bunuri expediate sau transportate în afara Uniunii Europene. Scutirea este cu drept de deducere. Factura trebuie să conțină trimiterea la dispoziția de scutire, conform art. 319 alin. (20) lit. l).

### Codul de taxă (TaxCode)

Anexa 1 la OPANAF 1783/2021 cere ca, pentru TVA, codurile de taxă să fie selectate din nomenclatorul „Coduri de taxă TVA pentru operațiuni”. În nomenclatorul de livrări din schema publicată de ANAF, exportul are un cod dedicat:

- **310313**: „Livrari de bunuri scutite cu drept de deducere cf Art. 294 alin (1) lit a) si b) din Codul Fiscal (Exporturi)”. Corespunde rândului 14 din D300.

Codurile vecine se confundă ușor cu exportul:

- **310314**: alte livrări și prestări scutite cu drept de deducere, altele decât exporturile;
- **310305**: prestări de servicii cu locul prestării în afara UE (nu sunt exporturi de bunuri);
- **310304**: livrări de bunuri cu locul livrării în afara României;
- **310301**: livrări intracomunitare scutite (nu export).

Codul intră în câmpul TaxCode al liniei de factură. Câmpul TaxType se completează cu codul pentru TVA.

### Clientul din afara UE

În schemă, codul clientului (CustomerID) are un prefix care arată categoria:

- **02** + codul țării + codul fiscal din statul respectiv, pentru operatorii economici din state din afara UE (exemplul din schemă: 02TK123005284);
- **06** + codul țării + un cod de client alocat de dumneavoastră, pentru operatorii din afara UE care nu sunt înregistrați în scopuri de TVA.

Același cod de client trebuie folosit în MasterFiles (Customers), în SalesInvoices, în GeneralLedgerEntries și în Payments.

### Valuta

Dacă factura de export e în valută, fiecare sumă se raportează în lei (Amount), împreună cu CurrencyCode, CurrencyAmount și, opțional, ExchangeRate. Cursul este cel de la exigibilitatea taxei, conform Codul fiscal art. 290 alin. (2).

### Exemplu

O societate livrează utilaje în Turcia, cu factură de 20.000 EUR, la un curs de 5,08 lei. În D406, factura apare în SalesInvoices cu:

- CustomerID = 02TR urmat de codul fiscal turc al clientului;
- linia de factură cu TaxCode 310313, bază de 101.600 lei și TVA 0;
- Amount 101600.00, CurrencyCode EUR, CurrencyAmount 20000.00.

În registrul-jurnal apare înregistrarea pe contul clientului și pe contul de venituri.

### Greșeli frecvente

- Se folosește 310301 (livrare intracomunitară) sau 310314 în loc de 310313. D406 nu se mai corelează cu rândul de export din D300.
- Clientul non-UE e raportat cu prefixul 01, care e rezervat statelor membre UE.
- Exportul de servicii e încadrat ca export de bunuri. Serviciile cu locul prestării în afara UE au codul 310305.

### De reținut

- Exportul de bunuri se raportează în SalesInvoices, cu TaxCode 310313 (art. 294 alin. (1) lit. a) și b)).
- Clientul din afara UE se identifică cu prefixul 02 (cu cod fiscal) sau 06 (fără înregistrare în scopuri de TVA).
- Sumele se raportează în lei, cu informația valutară alăturată.
- Verificați ca totalul exporturilor din D406 să fie egal cu rândul de export din decontul de TVA al aceleiași perioade.
