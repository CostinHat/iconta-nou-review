---
title: Cele mai frecvente erori XML și cum le rezolv
description: Structura facturii electronice trebuie să respecte SR EN 16931-1 și regulile RO_CIUS (OUG 120/2021 art. 4 alin. (1)) — majoritatea erorilor de validare vin din nerespectarea acestor reguli operaționale, nu din formatul XML în sine.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cele mai frecvente erori XML și cum le rezolv

Când o factură sau o declarație informativă e respinsă cu un mesaj de eroare de validare, în majoritatea cazurilor nu e o problemă de "format greșit", ci de conținut care nu respectă regulile specifice ale schemei folosite. Iată cadrul legal și tiparele frecvente de eroare.

### Baza legală a structurii pentru e-Factura

Codul fiscal, respectiv OUG 120/2021 art. 4 alin. (1), stabilește explicit ce trebuie să respecte structura facturii electronice:

a) "specificațiile tehnice și de utilizare a elementelor de bază ale facturii electronice așa cum sunt prevăzute în standardul european SR EN 16931-1, care sunt aplicabile la nivel național";

b) "specificațiile tehnice și de utilizare a elementelor de bază ale facturii electronice - **RO_CIUS** - și regulile operaționale specifice aplicabile la nivel național."

Cele mai multe erori de validare vin din nerespectarea regulilor RO_CIUS (particularizarea românească a standardului european), nu din structura XML de bază — de aceea o factură care "arată bine" ca XML poate fi totuși respinsă.

### Tipare frecvente de eroare și de unde vin

| Tip de eroare | Cauza tipică |
|---|---|
| Cod de TVA / cotă lipsă sau inconsistentă | linia de factură are o cotă de TVA care nu corespunde categoriei fiscale declarate pe acea linie (ex. cotă 0% fără motiv de scutire specificat) |
| CIF/CUI cu format invalid | lipsa prefixului "RO" acolo unde e cerut, sau cifra de control incorectă — verifică întotdeauna cifra de control înainte de a considera CIF-ul "de test" ca valid |
| Sumă totală care nu se reconciliază | totalurile de pe linii nu însumează exact la totalul facturii, de regulă din rotunjiri aplicate inconsistent (nu conform regulii de rotunjire aritmetică, cu adăugare la partea întreagă când zecimala e ≥ 0,5) |
| Câmpuri obligatorii lipsă la partener | adresă incompletă, țară lipsă, sau identificator de partener neconform cu formatul cerut de schemă |
| Element repetat greșit poziționat | o secțiune care apare de mai multe ori acolo unde schema permite o singură apariție, sau invers |
| Referință la o factură/document anterior inexistentă sau incorectă | pe facturi de stornare/corecție, referința către factura inițială nu corespunde ca număr/serie |

### De ce validatorul raportează uneori eroarea în locul greșit

O eroare de structură într-o secțiune anterioară a documentului poate opri parsarea corectă, iar mesajul de eroare returnat de validator poate indica o secțiune ulterioară, aparent fără legătură — pentru că validarea automată se oprește la ultima secțiune parsată cu succes, nu neapărat la cauza reală. Când mesajul de eroare pare "fără sens" față de conținutul vizat, verifică întâi secțiunile anterioare din document, nu doar linia indicată.

### Cum se investighează sistematic

1. Citește întreg mesajul de eroare, nu doar prima linie — validatoarele oficiale includ de regulă codul regulii încălcate (ex. o regulă Schematron din SR EN 16931 sau RO_CIUS).
2. Verifică dacă documentul respectă structura minimă cerută (câmpuri obligatorii, cardinalitate corectă a secțiunilor) înainte de a investiga reguli de conținut mai fine (cote TVA, sume).
3. Construiește, dacă e nevoie, un document minim de test, cu toate câmpurile obligatorii completate corect, pentru a izola dacă eroarea ține de un caz particular sau de o problemă structurală generală în softul de generare.
4. Corectează o singură cauză odată și re-validează — mai multe corecții simultane fac imposibil de știut care a rezolvat efectiv eroarea.

### Checklist rapid înainte de transmitere

- CIF/CUI cu cifră de control validă pe toți partenerii implicați.
- Cotele de TVA de pe fiecare linie corespund categoriei fiscale declarate.
- Totalurile pe linii însumează exact totalul documentului, cu rotunjire aritmetică, nu bancară.
- Toate câmpurile obligatorii pentru identificarea părților (denumire, adresă completă, țară, identificator fiscal) sunt completate.
- Pentru documente de corecție/stornare, referința la documentul inițial e corectă și completă.
