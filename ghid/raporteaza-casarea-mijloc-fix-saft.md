---
title: Cum se raportează casarea unui mijloc fix în SAF-T?
description: Casarea se raportează în D406 Active, o dată pe an. În AssetTransactions apare o tranzacție cu codul 50 „Casare mijloace fixe”, iar în MasterFiles (Assets) ieșirea apare în valoarea AssetDisposal. Temeiul este schema aprobată prin OPANAF 1783/2021, iar scoaterea din evidență urmează OMFP 1802/2014 pct. 242-243.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se raportează casarea unui mijloc fix în SAF-T?

Casarea nu se raportează în D406-ul lunar sau trimestrial. Ea intră în raportarea anuală „Active”, unde schema ANAF are un cod dedicat: **50 – Casare mijloace fixe**.

### Scoaterea din evidență

OMFP 1802/2014 pct. 242 alin. (1) prevede că o imobilizare corporală „trebuie scoasă din evidență la cedare sau casare, atunci când niciun beneficiu economic viitor nu mai este așteptat din utilizarea sa ulterioară”. Pct. 243 alin. (1) cere ca, la scoaterea din evidență, să fie evidențiate distinct veniturile din vânzare, cheltuielile reprezentând valoarea neamortizată și celelalte cheltuieli legate de cedare. Documentele de casare (decizia, procesul-verbal) sunt baza pentru înregistrarea contabilă și pentru tranzacția raportată în SAF-T.

### Când se raportează

Conform anexei 4 la OPANAF 1783/2021, secțiunea „Active” se transmite „la termenul de depunere a situaţiilor financiare aferente exerciţiului financiar” (pct. 1). Informațiile se întocmesc la nivelul anului financiar și se transmit printr-o singură depunere (pct. 7). Declarația pentru „Active” poate fi transmisă independent de celelalte secțiuni (pct. 8). O casare din martie 2026 apare deci în D406 Active pentru exercițiul 2026.

### Ce câmpuri se completează

**În SourceDocuments, subsecțiunea AssetTransactions:**

- **AssetTransactionType** (SD.AT.5, obligatoriu) = **50**. Codul se validează cu „Nomenclator imobilizari”. Nomenclatorul precizează că un cod din afara listei „conduce la semnalarea unei erori fatale, cu rejectarea declarației informative D406”.
- **AssetID**: același identificator de inventar ca în MasterFiles.
- **AssetTransactionDate**: data casării, în format AAAA-LL-ZZ.
- **TransactionID**: trimiterea la nota contabilă din registrul-jurnal (obligatoriu).
- **AssetTransactionValuation**: costul de achiziție (AcquisitionAndProductionCostOnTransaction), valoarea contabilă (BookValueOnTransaction) și suma netă a tranzacției (AssetTransactionAmount). La o casare fără încasări, suma netă este de regulă 0.

**În MasterFiles, subsecțiunea Assets:** mijlocul fix casat în cursul anului rămâne în raportare pentru anul respectiv. Valoarea ieșirii apare în **AssetDisposal**, adică „valoarea contabilă a ieșirilor de mijloace fixe în timpul perioadei selectate”. Amortizarea calculată până la casare apare în **DepreciationForPeriod**, iar valoarea contabilă de la final (BookValueEnd) devine zero.

### Exemplu

Un utilaj cu cost de 30.000 lei și amortizare cumulată de 26.000 lei se casează pe 15 octombrie 2026. Din dezmembrare nu se obține nimic.

- Contabil: 2813 = 2131 cu 26.000 lei și 6583 = 2131 cu 4.000 lei (valoarea neamortizată).
- În AssetTransactions: tip 50, data 2026-10-15, cost 30.000, valoare contabilă 4.000, sumă netă 0.
- În Assets: AssetDisposal cu valoarea ieșirii, iar BookValueEnd = 0.

### Greșeli frecvente

- Activul casat e scos din nomenclatorul Assets înainte de raportarea anuală, deși a existat în patrimoniu o parte din an.
- Casarea e raportată cu codul 20 (vânzare) sau 130 (alte tranzacții) în loc de 50.
- Casarea nu e corelată cu nota contabilă: TransactionID lipsește sau trimite la altă înregistrare.

### De reținut

- Casarea se raportează în D406 Active, anual, la termenul situațiilor financiare (anexa 4 la OPANAF 1783/2021).
- Codul tranzacției este 50 „Casare mijloace fixe”. Un cod din afara nomenclatorului duce la respingerea declarației.
- În Assets, ieșirea apare prin AssetDisposal, iar activul rămâne raportat pentru anul casării.
- Scoaterea din evidență se face conform OMFP 1802/2014 pct. 242-243.
