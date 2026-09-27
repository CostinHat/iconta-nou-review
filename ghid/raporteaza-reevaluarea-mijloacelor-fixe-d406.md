---
title: Cum se raportează reevaluarea mijloacelor fixe în D406?
description: Reevaluarea se raportează în D406 Active, anual. În AssetTransactions apare o tranzacție cu codul 70 (reevaluare pozitivă) sau 60 (reevaluare negativă) pentru fiecare activ reevaluat, iar în Assets se reflectă noile valori. Temeiul este schema aprobată prin OPANAF 1783/2021, iar reevaluarea contabilă urmează OMFP 1802/2014 pct. 102-105.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se raportează reevaluarea mijloacelor fixe în D406?

Reevaluarea unei clădiri sau a unui echipament intră în raportarea anuală D406 Active. Nomenclatorul ANAF are două coduri distincte pentru ea: **70 – Reevaluare pozitivă** și **60 – Reevaluare negativă**. Fiecare activ reevaluat apare ca tranzacție separată.

### Reevaluarea contabilă

OMFP 1802/2014 pct. 102 prevede că reevaluarea imobilizărilor corporale se face la valoarea justă de la data bilanțului, stabilită de regulă de evaluatori autorizați. Conform pct. 104, valoarea rezultată din reevaluare se atribuie activului în locul costului, iar amortizarea se aplică de atunci pe noua valoare. Pct. 105 alin. (1) cere ca elementele din aceeași categorie să fie reevaluate simultan. Aceste reguli explică de ce reevaluarea produce de obicei mai multe tranzacții în același an, câte una pentru fiecare activ din categorie.

### Când se raportează

Anexa 4 la OPANAF 1783/2021 stabilește că secțiunea „Active” se transmite la termenul de depunere a situațiilor financiare (pct. 1), printr-o singură depunere pentru anul financiar (pct. 7), și poate fi transmisă independent de restul D406 (pct. 8). O reevaluare efectuată la 31 decembrie 2026 apare deci în D406 Active pentru exercițiul 2026.

### Câmpurile relevante

**AssetTransactions (SourceDocuments):**

- **AssetTransactionType** (obligatoriu): 70 pentru creștere de valoare, 60 pentru descreștere. Codul se validează cu „Nomenclator imobilizari”, iar un cod din afara listei duce la respingerea declarației.
- **AssetID**: identificatorul de inventar din MasterFiles.
- **AssetTransactionDate**: data reevaluării.
- **TransactionID**: legătura cu nota contabilă (de exemplu, înregistrarea pe 105 „Rezerve din reevaluare”).
- **AssetTransactionValuation**: valorile tranzacției (cost, valoare contabilă, sumă).

**Assets (MasterFiles):** pentru fiecare activ se raportează valorile de început și de sfârșit de perioadă (AcquisitionAndProductionCostsBegin/End, BookValueBegin/End), amortizarea perioadei și amortizarea cumulată. După reevaluare, valorile de sfârșit trebuie să reflecte noua valoare. Anexa 1 la OPANAF 1783/2021 menționează expres „reevaluări” printre informațiile despre active.

Ajustările pentru depreciere nu sunt reevaluări. Ele au coduri proprii: 100 (ajustare de valoare negativă) și 110 (reversare ajustare de valoare).

### Exemplu

O clădire are, înainte de reevaluare, o valoare contabilă netă de 400.000 lei. Evaluatorul stabilește o valoare justă de 460.000 lei la 31.12.2026.

- Contabil: creșterea de 60.000 lei se înregistrează în rezerva din reevaluare (105).
- În AssetTransactions: tip 70, data 2026-12-31, valoarea tranzacției de 60.000 lei, TransactionID-ul notei contabile.
- În Assets: valoarea contabilă de la final reflectă noua valoare, de 460.000 lei.

Dacă în aceeași categorie alt activ scade de la 90.000 la 80.000 lei, se raportează pentru el o tranzacție separată, cu tipul 60.

### De reținut

- Reevaluarea se raportează în D406 Active, anual, la termenul situațiilor financiare.
- Codul 70 este pentru reevaluarea pozitivă, iar 60 pentru cea negativă. Ajustările pentru depreciere au codurile 100 și 110.
- Fiecare activ reevaluat este o tranzacție distinctă, cu legătură la nota contabilă.
- Valorile de final din Assets trebuie să fie egale cu registrul de imobilizări după reevaluare.
