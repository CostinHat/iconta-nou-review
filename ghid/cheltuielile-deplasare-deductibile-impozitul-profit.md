---
title: "Cheltuielile de deplasare sunt deductibile la impozitul pe profit?"
description: "Regula generală de deductibilitate la impozitul pe profit și cum se aplică ea cheltuielilor de transport, cazare și diurnă din deplasările de serviciu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cheltuielile de deplasare sunt deductibile la impozitul pe profit?

Aici e importantă o distincție pe care mulți contabili o amestecă: plafonul de diurnă neimpozabilă (art. 76 CF) spune ce parte din indemnizație nu e venit impozabil *pentru salariat*. O întrebare diferită, deși înrudită, este dacă cheltuiala respectivă e deductibilă *pentru firmă*, la calculul impozitului pe profit. Răspunsul la a doua întrebare nu vine din articolul despre diurnă, ci din regula generală de deductibilitate a cheltuielilor.

## Temeiul legal

::: ghid-temei
„(1) Pentru determinarea rezultatului fiscal sunt considerate cheltuieli deductibile cheltuielile efectuate în scopul desfășurării activității economice, inclusiv cele reglementate prin acte normative în vigoare, precum și taxele de înscriere, cotizațiile și contribuțiile datorate către camerele de comerț și industrie, organizațiile patronale și organizațiile sindicale."
— Codul fiscal, art. 25 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Aplicată la o deplasare de serviciu, regula generală înseamnă:

- Cheltuielile de transport, cazare și indemnizația de delegare/diurnă, **efectuate în scopul activității economice** și justificate cu documente, sunt cheltuieli deductibile la impozitul pe profit — se regăsesc firesc în sfera art. 25 alin. (1), fără să fie nevoie de o mențiune specială pentru „deplasare".
- Deductibilitatea la profit **nu depinde** de plafonul de neimpozabilitate al diurnei pentru salariat (art. 76 CF) — sunt două praguri independente, calculate cu reguli diferite, pentru contribuabili diferiți (firma, respectiv salariatul).
- Partea de diurnă care depășește plafonul neimpozabil rămâne, în continuare, o cheltuială a firmei efectuată în scopul activității — ea nu devine automat nedeductibilă la profit doar pentru că devine impozabilă la salariat; regimul de nedeductibilitate limitată de la art. 25 alin. (3) CF vizează alte categorii (protocol, cheltuieli sociale, tichete de masă, autovehicule etc.), nu indemnizația de delegare ca atare.
- Condiția reală care poate bloca deductibilitatea nu e plafonul de diurnă, ci lipsa documentelor justificative sau dovada că deplasarea a fost, de fapt, în interes personal, nu de serviciu.

## Ce se greșește în practică

- Se presupune că, dacă diurna depășește plafonul neimpozabil de la art. 76 CF, excedentul devine automat cheltuială nedeductibilă la impozitul pe profit — cele două reguli nu sunt legate în acest fel.
- Se caută în Codul fiscal un articol dedicat special „deplasării" pentru deductibilitatea la profit — nu există unul; cheltuiala intră sub regula generală de la art. 25 alin. (1), ca oricare altă cheltuială de exploatare.
- Se înregistrează cheltuieli de deplasare fără documente justificative (bonuri, facturi, ordin de deplasare), bazându-se doar pe decontul intern — fără documente, deductibilitatea poate fi contestată la control, indiferent de scopul real al deplasării.

## Ce face iConta.eu

Modulul de deconturi (`core/deconturi.py`) postează cheltuielile de deplasare — diurnă, transport, cazare — direct în contul de cheltuieli (625), fără nicio marcare de tip deductibil/nedeductibil și fără nicio verificare automată a condițiilor de la art. 25 CF. Aceasta reflectă corect regimul general al acestor cheltuieli: fiind cheltuieli de exploatare obișnuite, ele intră normal în calculul rezultatului fiscal, fără un tratament special de urmărit separat.

iConta.eu **nu are** o funcție dedicată de „verificare a deductibilității la impozitul pe profit" pentru cheltuielile de deplasare — și, de fapt, o astfel de funcție nu ar avea sens ca regulă automată, pentru că deductibilitatea generală ține de scopul economic real al deplasării (o chestiune de fapt, verificabilă la control), nu de un calcul care poate fi automatizat mecanic din datele decontului.

[iConta.eu](/)
