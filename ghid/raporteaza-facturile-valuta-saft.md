---
title: Cum se raportează facturile în valută în SAF-T?
description: În D406, fiecare sumă a unei facturi în valută se raportează în lei (Amount), împreună cu codul valutei, suma în valută și, opțional, cursul folosit. Cursul este cel de la exigibilitatea taxei, conform Codul fiscal art. 290, iar structura e stabilită prin schema aprobată la OPANAF 1783/2021.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se raportează facturile în valută în SAF-T?

O factură în euro nu se raportează în SAF-T doar în euro. Fiecare sumă apare în lei, iar alături se trec valuta și suma în valută. Fișierul D406 are o singură monedă de bază, leul. Informația valutară însoțește suma în lei, nu o înlocuiește.

### Moneda fișierului

Anexa 1 pct. 6 la OPANAF 1783/2021 trimite la schema de raportare publicată de ANAF. În schemă, câmpul de antet **DefaultCurrencyCode** se completează cu „RON” pentru România. Totalurile de control ale subsecțiunilor SalesInvoices și PurchaseInvoices (total debit, total credit) sunt definite „în valuta implicită a antetului”, deci în lei.

### Structura unei sume (AmountStructure)

Sumele din facturi folosesc structura comună AmountStructure, cu patru elemente:

- **Amount**: obligatoriu, suma în lei. Observația din schemă: „Se completează cu valoarea în RON, pentru România”.
- **CurrencyCode**: obligatoriu, codul de trei litere al valutei conform ISO 4217 (EUR, USD etc.). Se validează cu nomenclatorul ISO4217CurrCodes.
- **CurrencyAmount**: obligatoriu, suma în valută. Dacă valuta este RON, se completează cu aceeași valoare ca Amount.
- **ExchangeRate**: opțional, cursul folosit, cu maximum 4 zecimale. Schema dă relația „CurrencyAmount x ExchangeRate = Sumă”.

Schema mai precizează că nu se mai face validarea dintre suma în lei și suma în valută convertită cu cursul raportat. Validatorul nu vă va semnala deci un curs greșit. Răspunderea pentru corectitudine rămâne a dumneavoastră.

### Ce curs se folosește

Cursul rezultă din Codul fiscal, nu din schemă. Art. 290 alin. (2) prevede că, pentru operațiunile care nu sunt importuri, se aplică ultimul curs comunicat de BNR, ultimul curs publicat de BCE sau cursul băncii prin care se fac decontările, „valabil la data la care intervine exigibilitatea taxei”. Art. 319 alin. (23) permite exprimarea sumelor de pe factură în orice monedă, cu condiția ca TVA să fie exprimată în lei.

Observația din schemă la ExchangeRate spune același lucru: cursul pentru determinarea în lei a bazei impozabile este cel de la data exigibilității taxei, indiferent de data la care se recepționează bunurile sau factura.

### Exemplu

O factură de vânzare de 10.000 EUR, cu exigibilitatea la data livrării, când cursul BNR a fost 5,0850 lei:

- Amount = 50850.00
- CurrencyCode = EUR
- CurrencyAmount = 10000.00
- ExchangeRate = 5.0850

În GeneralLedgerEntries, înregistrarea contabilă a facturii apare tot în lei, cu aceleași sume. Diferențele de curs de la încasare nu modifică factura raportată. Ele apar ca înregistrări contabile separate, pe conturile de diferențe de curs.

### Verificări înainte de depunere

1. Toate facturile în valută au CurrencyCode diferit de RON și CurrencyAmount completat.
2. Amount este egal cu suma din contabilitate pentru aceeași factură (contul de client sau furnizor).
3. Cursul raportat corespunde datei exigibilității, nu datei înregistrării facturii primite.
4. Totalurile subsecțiunii SalesInvoices sau PurchaseInvoices, în lei, se regăsesc în rulajele conturilor contabile.

### De reținut

- Moneda de bază a fișierului D406 este RON. Toate totalurile sunt în lei.
- Fiecare sumă în valută are Amount în lei, plus CurrencyCode și CurrencyAmount (obligatorii) și ExchangeRate (opțional).
- Cursul este cel de la exigibilitatea taxei (Codul fiscal art. 290 alin. (2)).
- Validatorul nu verifică produsul curs × sumă în valută, deci corelarea trebuie verificată intern.
