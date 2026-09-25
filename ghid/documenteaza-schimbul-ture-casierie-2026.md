---
title: "Cum se documentează schimbul de ture la casierie 2026"
description: "Ce prevede legea privind respectarea plafoanelor de numerar și corecta ținere a registrului de casă între casieri, la schimbul de tură."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se documentează schimbul de ture la casierie 2026

Schimbul de tură la casierie e punctul cel mai expus la neconcordanțe: soldul de numerar trebuie să corespundă exact între ce predă o tură și ce preia următoarea, iar plafoanele legale de numerar continuă să se aplice cumulat pe zi, indiferent câte ture au avut loc.

## Temeiul legal

::: ghid-temei
„Articolul 3 (1) [...] c) plăți către persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei/persoană, dar nu mai mult de un plafon total de 10.000 lei/zi; [...]
(2) Sunt interzise încasările fragmentate în numerar de la beneficiari pentru facturile a căror valoare este mai mare de 5.000 lei [...], precum și fragmentarea facturilor pentru o livrare de bunuri sau o prestare de servicii a căror valoare este mai mare de 5.000 lei [...]"
— Legea 70/2015, art. 3 alin. (1) lit. c) și alin. (2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Ce înseamnă pentru un punct de vânzare cu mai multe ture pe zi:

- **Plafonul zilnic e cumulativ pe zi, nu pe tură.** Dacă o firmă face plăți către același furnizor de 3.000 lei în tura de dimineață și încă 3.000 lei în tura de după-amiază, suma cumulată de 6.000 lei depășește plafonul de 5.000 lei/persoană/zi — indiferent că au fost operate de casieri diferiți, în ture diferite.
- **Interdicția de fragmentare** (alin. (2)) se aplică la fel: împărțirea unei încasări mari între ture diferite, ca să pară sub plafon în fiecare tură, e interzisă exact ca fragmentarea în cadrul aceleiași ture.
- Documentarea schimbului de tură ține, tehnic, de registrul de casă (reglementat prin OMFP 2634/2015, normele generale privind documentele financiar-contabile) — soldul de numerar predat/preluat trebuie să corespundă exact între casierul care termină tura și cel care o începe, cu semnătură de predare-primire.

## Ce se greșește în practică

- Se calculează plafonul separat pentru fiecare tură, presupunând că fiecare casier „își" resetează plafonul zilnic — legea urmărește ziua calendaristică și partenerul, nu tura de lucru.
- Se omite documentarea explicită a predării-primirii soldului de numerar între casieri, ceea ce face imposibilă reconstituirea răspunderii în caz de diferență de casă.
- Se acceptă încasări fragmentate în mod deliberat între ture diferite, pentru a evita raportarea peste plafon — practică interzisă explicit de lege.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **calculează plafoanele de numerar la nivel de zi calendaristică**, cumulat pe toate operațiunile introduse din acea zi (modulul `core/casa.py`), nu separat pe tură — comportament aliniat cu logica legii, care nu recunoaște „tura" ca unitate de calcul al plafonului. Aplicația **nu are, la data acestui ghid, un proces dedicat de predare-primire de tură** (semnătură digitală, jurnal separat de schimb de tură) — soldul de casă rămâne o singură evidență continuă pe zi.

[iConta.eu](/)
