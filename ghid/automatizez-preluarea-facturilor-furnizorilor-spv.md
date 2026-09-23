---
title: Cum automatizez preluarea facturilor furnizorilor din SPV?
description: Partea de preluare (interogare ANAF, descărcare, evitarea reimportului) e deja complet automată; contul de cheltuială și confirmarea finală rămân, prin decizie asumată, un pas manual.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum automatizez preluarea facturilor furnizorilor din SPV?

„Preluarea” facturilor de la furnizori are, de fapt, două părți diferite: aducerea lor din SPV și transformarea lor în cheltuială contabilizată. Prima e deja complet automată. A doua rămâne, intenționat, manuală.

## Temeiul legal

::: ghid-temei
„Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul naţional privind factura electronică RO e-Factura."

— OUG nr. 120/2021, art. 4 alin. (7)
:::

Legea consideră factura „primită” din momentul disponibilității ei în SPV, nu din momentul în care contabilul o confirmă. Aplicația respectă exact acest moment pentru partea de aducere a facturii — dar decizia de contabilizare (cont de cheltuială, deductibilitate) rămâne, corect, o decizie profesională separată, nu un efect automat al primirii legale.

## Ce e deja automat

Un proces programat interoghează ANAF la fiecare 30 de minute, pentru fiecare firmă al cărei cabinet are conexiune SPV activă, și aduce toate facturile noi de la furnizori. Fiecare factură nouă e descărcată, verificată să aparțină firmei corecte, parsată automat (furnizor, număr, dată, sume, linii) și salvată ca ciornă — fără nicio acțiune din partea ta. Facturile deja aduse nu se reimportă la rulările următoare.

Dacă ai deja facturi anterioare de la același furnizor, aplicația sugerează și contul de cheltuială folosit ultima dată — dar ca sugestie, nu ca alegere automată.

## Ce rămâne manual, și de ce

Transformarea ciornei într-o cheltuială înregistrată, cu notă contabilă, cere confirmarea contabilului la ecranul de validare — contul de cheltuială e obligatoriu de ales sau confirmat explicit, fără valoare implicită. Decizia nu e o limitare tehnică rămasă de rezolvat, ci una asumată: contul de cheltuială, și implicit deductibilitatea, depind de context (natura bunului/serviciului, destinația lui în firmă) și nu pot fi presupuse corect de fiecare dată doar din conținutul XML-ului.

## Ce se greșește în practică

- Se caută o opțiune de „auto-validare” a facturilor primite — nu există, pentru că validarea implică o decizie de cont contabil care rămâne responsabilitatea contabilului.
- Se așteaptă ca preluarea completă (inclusiv contabilizarea) să fie instantanee — descărcarea e automată, dar lista de „facturi de validat” tot trebuie parcursă periodic de cineva.
- Se ignoră lista de validat pentru perioade lungi, presupunând că „dacă a intrat automat, e deja gata” — ciornele nevalidate nu devin cheltuieli și nu apar în rapoarte până la confirmare.

## Ce face iConta.eu

Partea de preluare tehnică (interogare ANAF, descărcare, filtrare pe firmă, evitarea reimportului) rulează complet automat, la 30 de minute, fără nicio configurare din partea contabilului. Ultimul pas — transformarea în cheltuială, cu cont contabil confirmat — rămâne manual, prin decizie de produs, nu prin limitare tehnică.

[iConta.eu](/)
