---
title: Cum se raportează mărfurile în custodie în D406?
description: Mărfurile primite în custodie nu sunt stoc propriu. În secțiunea „Stocuri” din D406 (OPANAF 1783/2021) se identifică prin câmpul OwnerID, care trimite la tabela Owners, iar în contabilitate stau în contul extrabilanțier 8033 (OMFP 1802/2014).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se raportează mărfurile în custodie în D406?

Mărfurile primite în custodie se află fizic în depozitul tău, dar aparțin altcuiva. În fișierul SAF-T, diferența nu se face printr-o secțiune separată. Ea se face prin câmpul care arată **cine este proprietarul** fiecărei poziții de stoc. Dacă acest câmp este completat cu CUI-ul propriu pentru toate pozițiile, marfa terților apare ca stoc al firmei.

### Când intră stocurile în D406

OPANAF 1783/2021, anexa 4, pct. 9-10: informațiile din secțiunea „Stocuri” se transmit numai la solicitarea organului fiscal central, în termenul stabilit de acesta, de cel puțin 30 de zile calendaristice de la solicitare. Custodia apare deci în declarația cerută special pentru stocuri.

Potrivit aceluiași ordin, secțiunea PhysicalStock (Stocuri) conține, printre altele, ID-ul depozitului, codul produsului, codul NC și „detalii despre proprietarul stocurilor”. Tabela Owners (Proprietari) conține detalii despre proprietarii stocurilor.

### Câmpurile relevante din schemă

Schema SAF-T publicată de ANAF, secțiunea MasterFiles, arată astfel:

- **MF.PS.2 WarehouseID** – depozitul în care se păstrează bunurile, completat după fișa de magazie;
- **MF.PS.9 OwnerID** – referința la tabela Owners. Codul are prefixul tipului: 00 urmat de CUI pentru operatorii români (fără atributul „RO”), 01 plus codul țării și codul de TVA pentru operatorii din alte state membre, 02 pentru operatori din afara UE, 03 urmat de CNP pentru persoane fizice;
- **MF.O.3 OwnerID** și **MF.O.2 CompanyStructure** – identificarea proprietarului, cu nume și adresă, în tabela Owners;
- **MF.O.4 AccountID** – contul analitic, validat pe planul de conturi aplicabil.

Nomenclatorul de mișcări de stoc nu are un cod dedicat custodiei. Codurile sunt 10 achiziție, 30 vânzare, 80 transfer intern etc., iar pentru ce nu se încadrează există codul 180 „Alte tranzacții”. Intrarea și ieșirea din custodie nu sunt achiziții sau vânzări. Nu le raporta cu codurile 10/30, care ar sugera un transfer de proprietate.

### Evidența contabilă din care se alimentează fișierul

OMFP 1802/2014 descrie contul **8033 „Valori materiale primite în păstrare sau custodie”**. În debit se înregistrează, la prețurile din documentele încheiate, valorile materiale primite, iar în credit ieșirile prin restituire, achiziție pentru nevoile entității, distrugere sau lipsuri la inventar. Nu se folosește contul 371.

OMFP 2634/2015 (anexa 2) prevede NIR-ul ca document de recepție obligatoriu pentru „bunurile materiale primite spre prelucrare, în custodie sau în păstrare”. La inventariere, pentru bunurile primite în custodie, o copie a listei de inventariere se trimite entității care deține bunurile. O evidență de gestiune care separă aceste bunuri de stocul propriu permite ca, în PhysicalStock, pozițiile terților să poarte OwnerID-ul proprietarului, nu pe al tău.

### Exemplu

Firma A (CUI 12345678) păstrează în depozitul „D1” 200 de bucăți de marfă ale firmei B (CUI 87654321), valoare din procesul-verbal de predare-primire 40.000 lei.

- Contabilitate: 8033 debit 40.000 lei.
- PhysicalStock: WarehouseID = D1, OwnerID = 0087654321, cantitățile de deschidere și închidere ale mărfii lui B.
- Owners: o intrare pentru 0087654321, cu numele și adresa firmei B.
- Stocurile proprii ale firmei A au OwnerID = 0012345678.

Dacă o parte din marfă este cumpărată ulterior de A, ieșirea din 8033 se corelează cu o intrare în stoc propriu, cu factură și NIR.

### Pași practici

1. Ține în gestiune bunurile în custodie separat de stocul propriu, pe baza NIR-ului de recepție.
2. Verifică dacă programul exportă OwnerID pe fiecare poziție de stoc, nu un CUI unic pentru tot depozitul.
3. Completează tabela Owners pentru fiecare deponent.
4. Reconciliază soldul contului 8033 cu totalul pozițiilor care au OwnerID diferit de al firmei.
5. La inventariere, listează separat bunurile terților și transmite o copie proprietarului, cum cer normele din OMFP 2634/2015.

### De reținut
- Mărfurile în custodie se raportează numai în D406 pentru „Stocuri”, depusă la cererea ANAF (OPANAF 1783/2021, anexa 4).
- Proprietarul se indică prin OwnerID (MF.PS.9), cu codul 00+CUI pentru deponenții români.
- Contabil, bunurile stau în 8033, nu în 371.
- Nu există un cod de mișcare dedicat custodiei, deci nu folosi codurile de achiziție și vânzare.
