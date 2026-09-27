---
title: Cum se raportează compensările în SAF-T?
description: O compensare între parteneri apare în D406 în două locuri. În GeneralLedgerEntries apare nota contabilă de compensare, pe conturile de clienți și furnizori. În Payments apare o înregistrare cu PaymentMethod 02 (Compensare) și, de preferat, PaymentMechanism 97. Structura e stabilită prin schema aprobată la OPANAF 1783/2021.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se raportează compensările în SAF-T?

Compensarea stinge datorii reciproce fără mișcare de bani. Pentru SAF-T însă, compensarea este tot o formă de plată. Schema D406 are un cod dedicat pentru ea în subsecțiunea Payments, iar înregistrarea contabilă corespunzătoare apare în registrul-jurnal.

### Temeiul juridic

Codul civil reglementează compensarea la art. 1616-1623 (Legea 287/2009). Datoriile reciproce se sting până la concurența celei mai mici dintre ele. Din punct de vedere contabil, compensarea se înregistrează pe baza documentului de compensare, ca notă între contul de furnizor și contul de client.

### Unde apare în D406

Anexa 1 la OPANAF 1783/2021 descrie subsecțiunea **Payments (Plăți)** ca informații despre „perioada, ID-ul tranzacţiei, data tranzacţiei, descriere, liniile de plăţi etc.”. Nomenclatorul de mecanisme de plată din schema ANAF (Nom_Mecanisme_plati) prevede, pentru câmpul **PaymentMethod** (SD.P.10, obligatoriu):

- 01, pentru numerar;
- **02, pentru compensare**;
- 03, pentru plăți fără numerar;
- 98, pentru un mecanism definit de comun acord;
- 99, pentru un instrument nedefinit.

Pentru câmpul opțional **PaymentMechanism** (SD.P.32), nomenclatorul enumeră codurile de folosit cu prioritate. Printre ele este **„codul 97 - pentru Compensarea între parteneri (offset/netting)”**.

Schema cere ca PaymentMethod și PaymentMechanism să fie corelate „așa cum sunt definite în nomenclator”. Atenție: în tabelul nomenclatorului, rândul pentru mecanismul 97 are în coloana de metodă codul 03, nu 02. Dacă folosiți ambele câmpuri, verificați combinația cu validatorul ANAF înainte de depunere. Dacă validatorul respinge perechea 02 cu 97, raportați doar PaymentMethod 02, pentru că PaymentMechanism este opțional.

### Cum se construiește înregistrarea

O compensare cu un partener care vă este și client, și furnizor are două fețe:

1. **În GeneralLedgerEntries**: nota contabilă de compensare. Pentru fiecare linie se trec contul analitic (AccountID), partenerul (CustomerID sau SupplierID) și suma pe debit sau pe credit.
2. **În Payments**: o înregistrare cu PaymentMethod 02. Liniile de plată au contul analitic (SD.P.20), partenerul, indicatorul debit sau credit (SD.P.26) și suma (SD.P.27). Pe fiecare linie, completați partenerul în câmpul corespunzător sensului: CustomerID pentru încasare, SupplierID pentru plată. Celălalt câmp primește valoarea 0, conform observațiilor din schemă.

### Exemplu

Societatea A are de încasat de la B 12.000 lei (contul 4111) și îi datorează lui B 8.000 lei (contul 401). Se compensează 8.000 lei.

- În registrul-jurnal: 401 = 4111, 8.000 lei, cu codul lui B pe ambele linii.
- În Payments: o plată cu PaymentMethod 02 și descrierea „compensare cu B”. O linie pe 401 (debit, SupplierID = B) și o linie pe 4111 (credit, CustomerID = B), fiecare de 8.000 lei.
- Soldul rămas, de 4.000 lei, se încasează ulterior și se raportează ca plată obișnuită (de regulă 03).

### Greșeli frecvente

- Compensarea apare doar în registrul-jurnal, fără înregistrare în Payments. Soldurile de parteneri nu se mai explică prin plăți.
- Se raportează PaymentMethod 03 („fără numerar”) din comoditate, deși nomenclatorul are codul 02 pentru compensare.
- Se folosesc coduri de partener diferite în Payments față de MasterFiles.

### De reținut

- Compensarea este o plată pentru D406: PaymentMethod 02.
- PaymentMechanism 97 descrie compensarea între parteneri. Corelarea cu metoda se verifică la validator.
- Nota contabilă de compensare apare și în GeneralLedgerEntries.
- Temeiul juridic al stingerii obligațiilor este în Codul civil art. 1616-1623.
