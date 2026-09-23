---
title: Cum se înregistrează impozitul pe profit în contabilitate?
description: Cheltuiala cu impozitul pe profit se înregistrează în contul 691, cu contrapartidă la datoria față de bugetul de stat, iar plata se face din 5121. Contul 691 e verificat explicit de motorul D101 pentru a nu ieși nedeductibil scăpat din calcul.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se înregistrează impozitul pe profit în contabilitate?

Impozitul pe profit se înregistrează ca o cheltuială a exercițiului, în contul 691, cu contrapartidă la contul de datorie față de bugetul de stat, indiferent dacă e vorba de o plată anticipată trimestrială sau de definitivarea anuală.

## Temeiul legal

::: ghid-temei
**Art. 17 din Codul fiscal**: „Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
:::

## Înregistrarea

- **Recunoașterea cheltuielii**: debit 691 „Cheltuieli cu impozitul pe profit" / credit contul de datorie către bugetul de stat pentru impozitul pe profit, cu suma calculată (trimestrial, ca plată anticipată, sau anual, la definitivare prin D101).
- **Plata**: debit contul de datorie / credit 5121 „Conturi la bănci în lei", la data plății efective către bugetul de stat.

Important: cheltuiala cu impozitul pe profit înregistrată în 691 este ea însăși **nedeductibilă fiscal** — la calculul profitului impozabil, această sumă trebuie adăugată înapoi la bază. Dacă e omisă, impozitul declarat iese subevaluat.

## Ce se greșește în practică

Se lasă soldul contului 691 „în aer" — înregistrat corect ca cheltuială contabilă, dar fără să fie preluat și la ajustările fiscale (cheltuieli nedeductibile) din declarația de impozit pe profit. Rezultatul e un impozit declarat mai mic decât cel real datorat, fără ca eroarea să fie vizibilă direct în balanță.

## Ce face iConta.eu

Motorul de generare a D101 verifică explicit soldul contului 691: dacă e pozitiv (există cheltuială cu impozitul pe profit înregistrată) și rândul de cheltuieli nedeductibile din declarație e zero, aplicația emite un avertisment — pentru că această cheltuială trebuie adăugată înapoi la baza impozabilă conform regulilor de deductibilitate din Codul fiscal. Măsurat pe un portofoliu real de firme, omisiunea acestei corecții a scăzut impozitul declarat cu peste 2.400 lei într-un singur caz, fără niciun alt semnal vizibil înainte de acest gard de validare.

[iConta.eu](/)
