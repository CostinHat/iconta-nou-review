---
title: "Ce fac dacă ANAF semnalează diferențe între e-Factura și D394?"
description: "De ce RO e-Factura și declarația informativă D394 sunt două obligații separate, care pot ajunge să nu se potrivească dacă nu sunt alimentate din aceleași date."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă ANAF semnalează diferențe între e-Factura și D394?

RO e-Factura și declarația D394 nu sunt, din punct de vedere legal, același lucru raportat de două ori. Sunt două obligații distincte, cu temeiuri și scopuri diferite — iar diferențele dintre ele apar de regulă pentru că una din cele două nu reflectă toate operațiunile reale ale firmei.

## Temeiul legal

::: ghid-temei
„ART. 1 Persoanele impozabile înregistrate în scopuri de TVA în România sunt obligate să declare livrările de bunuri, prestările de servicii şi achiziţiile de bunuri şi servicii realizate pe teritoriul României către/de la orice persoană, aşa cum este definită la art. 266 alin. (1) pct. 24 din Legea nr. 227/2015 privind Codul fiscal, cu modificările şi completările ulterioare."
— OPANAF nr. 3.769/2015 privind declararea livrărilor/prestărilor și achizițiilor efectuate pe teritoriul național de persoanele înregistrate în scopuri de TVA, art. 1 (sursă: anaf_surse/opanaf_3769_2015_d394_baza.txt)
:::

Din text rezultă că D394 are un obiect de raportare distinct de RO e-Factura:

- D394 e o declarație **informativă**, care centralizează livrările, prestările și achizițiile realizate pe teritoriul național de orice persoană înregistrată în scopuri de TVA, indiferent de canalul prin care au fost facturate — e-Factura sau altă modalitate.
- RO e-Factura e sistemul de **transmitere** a facturilor pentru operațiunile B2B între persoane stabilite în România, obligatoriu potrivit OUG 120/2021, dar nu acoperă neapărat toate operațiunile care trebuie declarate în D394 (de exemplu unele achiziții de la neplătitori de TVA sau operațiuni B2C).
- O diferență între cele două nu înseamnă automat o eroare — poate reflecta pur și simplu operațiuni raportate corect în D394, dar care nu trec (sau nu trebuie să treacă) prin fluxul RO e-Factura, ori invers, facturi transmise prin e-Factura dar omise din D394 din cauza unei erori de raportare.
- Corectarea diferenței presupune identificarea sursei — factură lipsă din D394, factură lipsă din e-Factura sau doar o eroare de perioadă de raportare — nu presupunerea că unul din cele două sisteme „are dreptate" automat.

## Ce se greșește în practică

- Se presupune că tot ce e transmis prin RO e-Factura apare automat și corect în D394, fără verificare, deoarece „sunt aceleași facturi".
- Nu se verifică separat facturile de achiziție/prestare care nu trec prin e-Factura (de exemplu de la furnizori neplătitori de TVA), dar care trebuie totuși incluse în D394.
- Se corectează D394 fără să se identifice mai întâi dacă diferența semnalată de ANAF vine dintr-o factură efectiv omisă sau dintr-o eroare de încadrare pe perioada de raportare.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează atât declarația D394 (`core/d394.py`), cu module de reconciliere dedicate (`core/d394_reconciliere.py`), cât și fluxul de transmitere prin RO e-Factura (`core/efactura_send.py`). Aplicația are și un modul de control încrucișat (`core/control_incrucisat.py`), care compară rulajele contabile cu datele raportate în declarații, pentru a semnala neconcordanțe interne înainte de depunere. Aplicația **nu primește și nu interpretează automat** mesajele de discrepanță transmise direct de ANAF între e-Factura și D394 — investigarea sursei exacte a diferenței semnalate de organul fiscal rămâne o verificare manuală a contabilului.

[iConta.eu](/)
