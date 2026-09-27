---
title: "SAF-T și salariile: există o secțiune de personal?"
description: D406 nu are o secțiune de personal sau de state de plată. Salariile apar doar ca înregistrări contabile în GeneralLedgerEntries, pe conturile 421, 431, 436, 444, 641, 646, cu TaxType-urile din nomenclatorul de impozite (602, 412, 432, 480), conform structurii aprobate prin OPANAF 1783/2021.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# SAF-T și salariile: există o secțiune de personal?

Nu. SAF-T-ul românesc nu are o secțiune „Personal” sau „Payroll” și nu raportează state de plată pe angajați. Salariile ajung în D406 exclusiv prin registrul-jurnal, ca note contabile. Datele pe salariat merg în continuare prin D112.

### Structura fișierului

Anexa 1 pct. 4-5 la OPANAF 1783/2021 enumeră secțiunile raportabile:

- Header (antet);
- MasterFiles: conturi contabile, clienți, furnizori, tabele de taxe, unități de măsură, tipuri de analiză, tipuri de mișcări, produse, stocuri, proprietari, active;
- GeneralLedgerEntries: înregistrările contabile;
- SourceDocuments: facturi de vânzare, facturi de achiziție, plăți, mișcări de bunuri, tranzacții cu active.

Nicio secțiune nu privește personalul. Salarizarea apare doar în **GeneralLedgerEntries**, care conține înregistrările contabile „la nivel de tranzacţie, incluzând conturile contabile analitice”.

### Ce se raportează pentru salarii

Notele contabile lunare de salarii se raportează cu fiecare linie a lor:

- contul analitic (AccountID): 641, 421, 444, 4315, 4316, 436, 646 etc.;
- suma pe debit sau pe credit;
- **TaxInformation**, obligatoriu pe fiecare linie.

Pentru TaxInformation, schema trimite la nomenclatorul de impozite (TAX-IMP), care are coduri pentru obligațiile salariale:

- **602**: impozit pe veniturile din salarii și asimilate salariilor;
- **412**: contribuția individuală de asigurări sociale reținută de la asigurați;
- **432**: contribuția pentru asigurări de sănătate reținută de la asigurați;
- **480**: contribuția asiguratorie pentru muncă.

Regula pentru TaxCode din schemă: pentru un TaxType diferit de TVA sau de impozitele cu reținere la sursă din nomenclatorul WHT, TaxCode se completează cu **000000**. Pentru liniile fără relevanță fiscală, schema cere TaxType 000 și TaxCode 000000. Codurile concrete se verifică în versiunea de nomenclator valabilă pentru perioada raportată.

### Partenerul pe liniile de salarii

Fiecare linie din registrul-jurnal are câmpurile CustomerID și SupplierID. Observația din schemă spune că, pentru liniile care nu reprezintă datorii sau creanțe ce trebuie urmărite contabil „pe fiecare persoană fizică sau juridică”, se completează codul contribuabilului raportor. Pentru cele urmărite pe persoană, se completează codul partenerului, așa cum e definit în MasterFiles.

Aplicat: la conturile de contribuții față de buget (431, 436, 444) se folosește codul firmei. La 421, dacă țineți analitic pe fiecare salariat, schema permite identificarea persoanei fizice cu prefixul **03** urmat de CNP. Verificați însă ce acceptă validatorul pentru conturile de personal.

### Exemplu

Pentru un salariat cu brut de 6.000 lei, nota lunară are linii pe 641 (debit 6.000), 4315 (credit, CAS reținut), 4316 (credit, CASS reținut), 444 (credit, impozit) și 421 (credit, netul). Separat, linia 646 = 436 reprezintă contribuția asiguratorie pentru muncă. În D406, fiecare linie apare cu contul ei și cu TaxType corespunzător (412, 432, 602, 480), cu TaxCode 000000. Plata netului prin bancă apare apoi în Payments, cu PaymentMethod 03.

### De reținut

- D406 nu are secțiune de personal. Salariile intră doar în GeneralLedgerEntries.
- Fiecare linie are TaxInformation obligatoriu: TaxType din nomenclatorul de impozite (602, 412, 432, 480 etc.) și TaxCode 000000.
- Pentru liniile fără urmărire pe persoană se folosește codul firmei. Persoana fizică are prefixul 03 plus CNP.
- Datele pe salariat (brut, contribuții, zile lucrate) se declară prin D112, nu prin SAF-T.
