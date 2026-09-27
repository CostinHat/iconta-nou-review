---
title: Cum verific SAF-T cu registrul de casă?
description: Registrul de casă se verifică față de D406 pe soldurile și rulajele contului 5311 din GeneralLedgerAccounts și GeneralLedgerEntries, apoi pe plățile în numerar din Payments (PaymentMethod 01). Temeiul este OMFP 2634/2015 pentru registrul de casă și schema aprobată prin OPANAF 1783/2021.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific SAF-T cu registrul de casă?

Registrul de casă are o particularitate: arată soldul zi de zi. De aceea e un instrument de verificare mai fin decât balanța. Dacă D406 se împacă cu registrul de casă la nivel de lună, dar nu la nivel de zi, eroarea e aproape sigur de dată contabilă.

### Ce este registrul de casă

Conform OMFP 2634/2015 (anexa 2, normele specifice pentru documentele financiar-contabile), registrul de casă servește ca document de înregistrare operativă a încasărilor și plăților în numerar, ca document de stabilire a soldului de casă „la sfârșitul fiecărei zile” și ca document de înregistrare în contabilitate. Se întocmește zilnic, pe baza documentelor justificative de încasări și plăți. Pentru numerarul în valută există un registru de casă separat.

### Unde apare casa în D406

În structura din anexa 1 la OPANAF 1783/2021:

- **GeneralLedgerAccounts**: conturile analitice de casă (5311 pentru lei, 5314 pentru valută), cu soldurile inițial și final;
- **GeneralLedgerEntries**: fiecare înregistrare pe contul de casă, cu data tranzacției și data înregistrării;
- **Payments**: încasările și plățile în numerar, cu **PaymentMethod 01 (Numerar)**. Pentru PaymentMechanism, codul recomandat este 10 („plata în numerar”), conform nomenclatorului Nom_Mecanisme_plati din schema ANAF.

### Pasul 1: soldul la început și la sfârșit

Soldul inițial al contului 5311 din D406 trebuie să fie egal cu soldul reportat în registrul de casă la prima zi a perioadei. Soldul final trebuie să fie egal cu soldul din ultima zi. La 5314 se face aceeași comparație, pe fiecare valută, în lei.

### Pasul 2: rulajele pe zile

Exportați din GeneralLedgerEntries mișcările contului 5311, grupate pe TransactionDate, și comparați-le cu totalurile zilnice din registrul de casă. Diferențele tipice sunt:

- o chitanță înregistrată în contabilitate cu data documentului, iar în registru cu altă dată;
- raportul Z înregistrat global la final de lună, deși registrul de casă îl preia zilnic;
- depunerile la bancă (581) înregistrate doar pe o parte.

### Pasul 3: plățile în numerar din Payments

Prin sondaj, fiecare chitanță către un client sau plată către un furnizor din registrul de casă trebuie să apară în Payments cu PaymentMethod 01 și cu codul corect al partenerului. Pentru operațiunile fără partener (avansuri de trezorerie, depuneri la bancă), schema cere în câmpurile de partener codul firmei raportoare.

### Exemplu

Pe iulie 2026, registrul de casă are sold inițial 2.340 lei, încasări de 48.900 lei, plăți de 47.100 lei și sold final 4.140 lei. D406 are același sold final, dar pe 14 iulie registrul arată sold 9.870 lei, iar din GeneralLedgerEntries rezultă 3.870 lei. Cauza: o depunere la bancă de 6.000 lei înregistrată în contabilitate pe 14, dar efectuată și trecută în registru pe 15. Totalul lunar se împacă, dar ordinea zilelor nu. Soldul zilnic trebuie însă să fie real, pentru că la un control plafonul de numerar se verifică pe zile.

### De reținut

- Registrul de casă se întocmește zilnic (OMFP 2634/2015), deci se compară cu D406 pe zile, nu doar pe lună.
- Casa apare în D406 prin contul 5311/5314 (solduri și înregistrări) și prin Payments cu PaymentMethod 01.
- Codul de mecanism recomandat pentru numerar este 10.
- Datele diferite dintre registru și nota contabilă sunt cauza cea mai frecventă a diferențelor zilnice.
