---
title: Cum se marchează taxarea inversă în fișierul e-Factura
description: Taxarea inversă se aplică doar operațiunilor enumerate expres de Codul fiscal (deșeuri reciclabile, construcții/terenuri, laptopuri, console, telefoane mobile ș.a.) și numai între doi plătitori de TVA înregistrați — factura electronică trebuie să reflecte o bază impozabilă fără TVA colectată, cu mențiunea taxării inverse.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se marchează taxarea inversă în fișierul e-Factura

Taxarea inversă nu e o opțiune liberă a părților — se aplică doar pentru operațiunile expres enumerate de lege, iar factura electronică trebuie construită astfel încât să reflecte corect faptul că obligația de plată a TVA trece de la furnizor la beneficiar.

### Când se aplică — lista e închisă

Codul fiscal, art. 331, prevede măsurile de simplificare (taxarea inversă): prin excepție de la regula obișnuită (furnizorul e persoana obligată la plata TVA), pentru operațiunile enumerate la alin. (2), persoana obligată la plata taxei este **beneficiarul**. Condiția obligatorie: atât furnizorul, cât și beneficiarul trebuie să fie înregistrați în scopuri de TVA. Printre operațiunile la care se aplică taxarea inversă:

| Categorie | Exemplu |
|---|---|
| Deșeuri și materiale reciclabile | fier vechi, deșeuri de plastic/hârtie/sticlă |
| Masă lemnoasă și materiale lemnoase | conform Codului silvic |
| Cereale și plante tehnice | grâu, floarea-soarelui, sfeclă de zahăr, nedestinate ca atare consumatorului final |
| Construcții, terenuri și părți de construcție | livrări pentru care se aplică taxare prin efectul legii sau prin opțiune |
| Telefoane mobile, console de jocuri, tablete PC și laptopuri | livrări către un cumpărător plătitor de TVA |
| Certificate de emisii de gaze cu efect de seră, certificate verzi | transferuri între persoane impozabile |
| Energie electrică/gaze naturale către un comerciant | doar dacă cumpărătorul are calitatea de comerciant, dovedită prin declarație/licență |

Dacă operațiunea nu se regăsește pe această listă, taxarea inversă nu se poate aplica prin simplă înțelegere între părți — factura trebuie emisă cu TVA colectată normal.

### Cum ajunge asta în fișierul XML al e-Facturii

Sistemul RO e-Factura (OUG nr. 120/2021) cere ca structura facturii electronice să respecte standardul european SR EN 16931-1 și specificațiile naționale RO_CIUS (Codul fiscal, art. 4 alin. (1) din ordonanță). În practică, o factură cu taxare inversă se construiește cu:

- **bază impozabilă înscrisă, dar TVA colectată = 0**, pe linia/liniile de factură vizate de taxarea inversă;
- **mențiunea expresă "taxare inversă"** pe factură, alături de temeiul legal (Codul fiscal, art. 331), obligatorie și pe factura pe hârtie/PDF, nu doar convenție internă;
- **codul de categorie de TVA din setul de coduri standard folosit de RO_CIUS** pentru operațiuni cu taxă inversată, distinct de codurile pentru scutire propriu-zisă sau operațiuni neimpozabile — utilizarea codului greșit (de exemplu cel de scutire, în loc de taxare inversă) produce erori de validare sau, mai rău, o factură validată tehnic dar cu regim fiscal incorect.

### Practic

- Verificați, înainte de emitere, atât natura bunului/serviciului (se regăsește pe lista din art. 331?), cât și calitatea beneficiarului (înregistrat în scopuri de TVA, conform art. 316) — lipsa oricăreia dintre cele două condiții exclude taxarea inversă.
- Nu combinați pe aceeași factură linii cu regim normal de TVA și linii cu taxare inversă fără să marcați distinct fiecare linie — validarea globală a facturii nu înlocuiește marcajul corect per linie.
- Pentru operațiunile condiționate de o declarație a cumpărătorului (energie electrică, gaze naturale către comercianți), verificați lista publicată de ANAF cu persoanele care au depus declarația pe propria răspundere înainte de a aplica taxarea inversă — altfel furnizorul rămâne obligat la plata TVA normală.
