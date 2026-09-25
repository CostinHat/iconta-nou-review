---
title: SAF-T pentru retailerii cu volum mare de facturi
description: Explică particularitățile raportării D406 (SAF-T) pentru retaileri cu volum ridicat de tranzacții — perioada de grație, obligațiile pe secțiunea Products/Stocuri și regula rectificativelor integrale.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# SAF-T pentru retailerii cu volum mare de facturi

Un retailer cu mii de tranzacții zilnice nu are o versiune „simplificată" de SAF-T — dar are câteva praguri și reguli care contează mai mult pentru el decât pentru o firmă cu facturare redusă.

### Cine e deja obligat, la volum mare

Declarația informativă D406 (fișierul standard de control fiscal), reglementată prin OPANAF 1783/2021, cu Anexa 5 înlocuită prin OPANAF 407/2025, stabilește obligația de transmitere pe categorii de contribuabili, cu date de referință diferite:
- **marii contribuabili** — obligație de la 1 ianuarie 2022 (cei încadrați și în 2021), respectiv 1 iulie 2022 (noii mari contribuabili);
- **contribuabilii mijlocii** — obligație de la 1 ianuarie 2023;
- **contribuabilii mici** — obligație de la 1 ianuarie 2025.

Un retailer cu volum mare de facturi se încadrează, de regulă, la categoria mari sau mijlocii contribuabili — deci obligația D406 e deja activă, indiferent de anul curent, cu excepția firmelor nou-înregistrate, pentru care obligația începe „de la data efectivă a înregistrării", cu prima depunere în ultima zi a lunii care urmează perioadei de raportare (OPANAF 1783/2021, Anexa 5, pct.1).

### Perioada fiscală de raportare — lunar, aproape mereu

Retailerii cu volum mare sunt aproape întotdeauna plătitori de TVA cu perioadă fiscală lunară (cifra de afaceri le depășește pragul de 100.000 euro pentru decontul trimestrial, conform Codul fiscal art.322 alin.(2)) — deci raportarea D406 le e obligatorie **lunar**, urmând perioada fiscală de TVA (OPANAF 1783/2021, Anexa 4, pct.2).

### Secțiunea Products și Stocuri — relevanța directă pentru retail

Spre deosebire de o firmă de servicii, un retailer trebuie să completeze cu atenție subsecțiunile:
- **Products (Produse)** — cod produs, grupă, descriere, unitate de măsură, încadrare tarifară (cod NC), metoda de evaluare a stocurilor (FIFO, LIFO, CMP);
- **PhysicalStock (Stocuri)** — ID-ul depozitului, codul produsului, cantitatea și valoarea la început și final de perioadă.

Secțiunea „Stocuri" nu se raportează automat la fiecare declarație lunară/trimestrială — se transmite **doar la solicitarea specifică a organelor fiscale centrale**, cu un termen de minimum 30 de zile calendaristice de la data solicitării (OPANAF 1783/2021, Anexa 4, pct.9-10). Retailerii nu trebuie să pregătească această secțiune la fiecare raportare curentă, dar trebuie să aibă structura de date pregătită pentru a răspunde rapid când vine solicitarea.

### Volumul mare de tranzacții nu scutește de perioada de grație — dar nici nu o prelungește

Perioada de grație pentru sancțiuni contravenționale e aceeași indiferent de volumul de facturi: 6 luni pentru prima raportare lunară, 5 luni pentru a doua, 4 pentru a treia, 3 pentru a patra, 2 pentru a cincea (OPANAF 1783/2021, Anexa 4, pct.5). Pentru un retailer cu volum foarte mare, aceste luni de grație sunt cea mai bună fereastră de a identifica și corecta erorile sistematice de mapare (coduri de produs, conturi contabile, cote de TVA) înainte ca acestea să înceapă să conteze contravențional.

### Rectificativele — integrale, nu incrementale

Un volum mare de tranzacții amplifică riscul de erori punctuale — dar sistemul de corectare rămâne același: dacă declarația e transmisă cu erori identificate de ANAF (recipisă cu erori), contribuabilul **retransmite integral** fișierul SAF-T corectat, nu doar înregistrările afectate. Nu sunt admise corecții parțiale prin transmiterea selectivă a câmpurilor corectate (OPANAF 1783/2021, Anexa 4, pct.11-12) — pentru un retailer cu mii de linii de tranzacții, asta înseamnă că un proces de validare intern, înainte de transmitere, contează mult mai mult decât capacitatea de a corecta ulterior.

### Practic, pentru un retailer cu volum mare

1. Confirmă categoria de contribuabil (mare/mijlociu/mic) și data de referință aplicabilă — determină dacă obligația e deja activă.
2. Automatizează validarea internă a fișierului SAF-T înainte de transmitere — corecțiile parțiale nu sunt admise după ce ANAF a semnalat erori.
3. Pregătește structura de date pentru secțiunea Stocuri, chiar dacă nu se raportează curent — solicitarea ANAF vine cu termen strict de minimum 30 de zile.
4. Folosește perioada de grație (2-6 luni, în funcție de câte raportări ai depus) pentru a corecta erorile sistematice de mapare, nu doar pentru a evita sancțiunea imediată.
