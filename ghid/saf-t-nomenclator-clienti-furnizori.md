---
title: SAF-T și nomenclatorul de clienți și furnizori
description: Secțiunile Customers și Suppliers din fișierul SAF-T (D406) preiau datele din nomenclatorul de parteneri — cod fiscal, denumire, adresă — potrivit OPANAF 1783/2021; când un partener lipsește din nomenclator, e reconstituit din facturi.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# De unde ia SAF-T datele de clienți și furnizori și ce faci dacă un partener lipsește din nomenclator?

Fișierul SAF-T are, în secțiunea de fișiere de bază (MasterFiles), câte o listă separată pentru clienți (Customers) și furnizori (Suppliers) — fiecare partener cu cod fiscal, denumire, oraș, țară și soldul lui la deschiderea și închiderea perioadei. Sursa firească a acestor date e nomenclatorul de parteneri ținut în aplicație. Dar ce se întâmplă când un partener a fost folosit pe o factură fără să fi fost introdus în nomenclator?

## Temeiul legal

::: ghid-temei
Structura fișierului SAF-T și obligativitatea secțiunilor Customers/Suppliers din MasterFiles sunt stabilite prin **OPANAF nr. 1783/2021**, care aprobă Declarația informativă D406 și schema tehnică (XSD) după care se validează fișierul. Fiecare client sau furnizor raportat trebuie identificat printr-un cod de înregistrare (RegistrationNumber/CustomerID/SupplierID) și legat de conturile contabile pe care apare (4111 pentru clienți, 401 pentru furnizori).

Schema tehnică ANAF (secțiunea „Structures" a documentației SAF-T) codifică identificatorul unui partener român ca **„00" urmat direct de CUI, fără prefixul RO** — nota oficială e explicită: *„Nu se trece atributul fiscal «RO» pentru plătitorii de TVA."* Prefixul RO se folosește doar la identificarea **firmei raportoare** (antetul propriu al fișierului), nu la partenerii din nomenclator.
:::

## Ce conțin efectiv secțiunile

Pentru fiecare client: codul fiscal (codificat **„00" + CUI, fără prefixul RO** pentru un partener român — regulă separată de codul propriei firme, care poartă RO), denumirea, orașul și țara, plus soldul contului 4111 la deschiderea și închiderea perioadei. Pentru fiecare furnizor, aceleași date pe contul 401. Identificatorul de pe fiecare partener (CustomerID/SupplierID) trebuie să fie **identic** cu cel folosit pe liniile de tranzacții din restul fișierului — altfel apare o neconformitate: un cod referit pe o factură dar absent din lista de bază.

## Ce se întâmplă când nomenclatorul e gol sau incomplet

Nomenclatorul de parteneri (ecranul de Clienți/Furnizori) e sursa recomandată — completă, cu adresă și date de identificare corecte. Dar dacă un partener a fost folosit direct pe o factură fără să existe și în nomenclator, SAF-T nu lasă golul: derivă partenerul direct din facturile emise/primite, cu codul fiscal și denumirea de pe factură, ca fiecare linie 4111/401 să aibă un CustomerID/SupplierID valid. E o soluție de rezervă, nu un înlocuitor — datele reconstituite din factură sunt mai sărace (fără oraș, fără adresă completă) decât cele dintr-un nomenclator îngrijit.

## Ce se greșește în practică

- **Se lasă nomenclatorul neactualizat** și se contează pe reconstituirea din facturi — funcționează pentru validarea SAF-T, dar pierde datele de adresă și complică verificarea partenerilor la un control.
- **Se șterge un partener din nomenclator** deși are facturi înregistrate — ștergerea e blocată tocmai ca să nu rămână facturi fără partenerul lor de referință; corect e marcarea ca inactiv, nu ștergerea.
- **Se adaugă prefixul RO la codul fiscal al unui partener român**, din reflex (așa se scrie pe factură) — pe SAF-T e greșit: partenerii români se codifică „00"+CUI, fără RO; prefixul e rezervat identificării firmei raportoare, nu partenerilor ei.

## Ce face iConta.eu

Nomenclatorul de clienți și furnizori e un ecran separat (listă, creare, editare), cu ștergerea protejată: un partener cu facturi înregistrate nu poate fi șters, ca să nu rămână o factură fără partenerul ei în evidență. La generarea SAF-T, secțiunile Customers și Suppliers se populează din acest nomenclator; pentru partenerii folosiți doar pe facturi și absenți din nomenclator, sistemul îi reconstituie automat din datele facturii, ca identificatorul de pe fiecare linie de tranzacție să aibă mereu un partener corespunzător în MasterFiles.

[iConta.eu](/)
