---
title: "Cum se evaluează produsele finite la cost de producție"
description: "Regulile de evaluare a produselor finite la cost standard, cu repartizarea diferențelor de preț față de costul efectiv."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se evaluează produsele finite la cost de producție

Produsele finite obținute din producție proprie se evaluează la cost de producție. În practică, multe firme folosesc un cost standard (prestabilit) pentru intrarea în gestiune, pentru că el se cunoaște înainte de închiderea lunii, iar diferența față de costul efectiv se urmărește separat, printr-un cont distinct. Iată exact cum funcționează, conform legii.

## Temeiul legal

::: ghid-temei
„Contul 345 «Produse finite» Cu ajutorul acestui cont se ține evidența existenței și mișcării stocurilor de produse finite. Contul 345 «Produse finite» este un cont de activ. În debitul contului 345 «Produse finite» se înregistrează: – valoarea la preț de înregistrare a produselor finite intrate în gestiune și plusurile de inventar (711); [...] În creditul contului 345 «Produse finite» se înregistrează: – valoarea la preț de înregistrare a produselor finite vândute și lipsurile de inventar (711); [...]"
— OMFP 1802/2014, Reglementările contabile, Cap. 16, funcțiunea contului 345 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Când „prețul de înregistrare" folosit este un cost standard, diferența dintre acesta și costul efectiv se urmărește separat, prin contul 348 „Diferențe de preț la produse":

- „Cu ajutorul acestui cont se ține evidența diferențelor între prețul standard (prestabilit) și costul de producție al produselor. Contul 348 «Diferențe de preț la produse» este un cont rectificativ al valorii de înregistrare a produselor."
- **Diferență nefavorabilă** (costul efectiv e mai mare decât standardul): se înregistrează în debitul 348, prin creditul 711 — se adaugă la valoarea de intrare.
- **Diferență favorabilă** (costul efectiv e mai mic decât standardul): se înregistrează în creditul 348 (sau prin formulă în roșu), prin 711 — scade valoarea de intrare.
- La ieșirea (vânzarea) produselor, diferența acumulată în 348 se repartizează proporțional pe produsele ieșite din gestiune, printr-un coeficient de repartizare calculat din soldurile și rulajele conturilor 345 și 348.

## Ce se greșește în practică

- Se înregistrează produsele finite direct la cost efectiv, fără cost standard, deși costul efectiv al lunii nu se cunoaște decât la închidere — ceea ce blochează facturarea intermediară.
- Se calculează diferența de preț o singură dată, la intrare, și se uită complet repartizarea ei la ieșire (vânzare), prin coeficientul de repartizare — cea mai frecventă greșeală semnalată în practică.
- Se confundă sensul diferenței: o diferență „nefavorabilă" (cost efectiv mai mare) majorează valoarea produsului, nu o diminuează.

## Ce face iConta.eu

Din ecranul **Operațiuni speciale → Imobilizări**, operațiunea „Producție (711/345)" cu subtipul „Obținere" generează automat nota `345 = 711` la cost standard și, dacă se introduce și costul efectiv, calculează automat diferența și adaugă a doua linie corectă — `348 = 711` pentru diferența nefavorabilă sau `711 = 348` pentru cea favorabilă, exact conform funcțiunii contului 348 de mai sus.

Notă onestă, importantă: la operațiunea de **vânzare cu descărcare de gestiune**, motorul de calcul al aplicației știe să repartizeze coeficientul de diferențe de preț (348) pe produsele ieșite, dar **formularul din interfața iConta.eu nu are, la acest moment, niciun câmp pentru introducerea acestui coeficient** — ecranul de vânzare cere doar prețul de vânzare, costul standard ieșit și cota de TVA. În practică, descărcarea de gestiune se înregistrează azi la cost standard pur, fără repartizarea automată a diferențelor de preț din UI, deci exact greșeala „omiterea coeficientului 348" rămâne, momentan, comportamentul implicit al aplicației la vânzare — de urmărit manual până la completarea formularului.

[iConta.eu](/)
