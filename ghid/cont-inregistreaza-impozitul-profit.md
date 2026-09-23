---
title: În ce cont se înregistrează impozitul pe profit?
description: Cheltuiala în contul 691, datoria față de bugetul de stat în contul 441, plata din 5121. Contul 691 are un rol suplimentar în calculul D101 — soldul lui e verificat automat pentru a nu scăpa nedeductibil din baza impozabilă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# În ce cont se înregistrează impozitul pe profit?

Impozitul pe profit folosește două conturi principale: **691** pentru cheltuială și **441** pentru datoria față de bugetul de stat, plata efectuându-se ulterior din **5121**.

## Temeiul legal

::: ghid-temei
**Art. 17 din Codul fiscal**: „Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
:::

## Conturile folosite

- **691 „Cheltuieli cu impozitul pe profit"** — se debitează cu suma calculată, trimestrial sau la definitivarea anuală.
- **441 „Impozitul pe profit/venit"** — se creditează în contrapartidă cu 691, reprezentând datoria față de bugetul de stat.
- **5121 „Conturi la bănci în lei"** — se creditează la plata efectivă (debit 441 / credit 5121).

Contul 691 are un rol suplimentar, dincolo de simpla înregistrare: soldul lui debitor reprezintă o cheltuială **nedeductibilă** fiscal — trebuie adăugată înapoi la baza impozabilă la calculul propriu-zis al impozitului pe profit, altfel impozitul declarat iese subevaluat.

## Ce se greșește în practică

Se înregistrează corect cheltuiala în 691, dar suma nu ajunge și în rândul de cheltuieli nedeductibile din declarația de impozit pe profit — o eroare invizibilă în balanță, dar care reduce impozitul efectiv declarat.

## Ce face iConta.eu

Generatorul D101 verifică automat această legătură: dacă soldul contului 691 e pozitiv și rândul de cheltuieli nedeductibile din declarație e zero, aplicația emite un avertisment explicit înainte de generare. Măsurat pe portofoliu, omisiunea acestei corecții a redus impozitul declarat cu peste 2.400 lei într-un caz real, fără alt semnal vizibil înainte de acest gard.

[iConta.eu](/)
