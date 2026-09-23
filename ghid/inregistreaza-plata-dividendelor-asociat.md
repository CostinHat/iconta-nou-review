---
title: "Cum se înregistrează plata dividendelor către asociat?"
description: "Monografia contabilă completă pentru dividendul aprobat și plătit unui asociat, pentru varianta anuală și pentru cea interimară."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează plata dividendelor către asociat?

Dividendul cuvenit unui asociat se înregistrează în două momente diferite, cu conturi diferite, după cum este vorba de dividendul anual, aprobat prin situațiile financiare, sau de dividendul interimar, distribuit trimestrial.

## Temeiul legal

::: ghid-temei
„Cota-parte din profit ce se plătește fiecărui asociat constituie dividend." — Legea 31/1990, art. 67 alin. (1)

„Sumele depuse sau lăsate temporar de către acționari/asociați la dispoziția entității, precum și dobânzile aferente, calculate în condițiile legii, se înregistrează în contabilitate în conturi distincte (contul 4551 «Acționari/asociați - conturi curente», respectiv contul 4558 «Acționari/asociați - dobânzi la conturi curente»)." — OMFP 1802/2014, pct. 349 (citat aici doar ca reper pentru distincția între conturile de decontare cu asociații — dividendul propriu-zis folosește contul 457, nu 4551)
:::

Pentru dividendul anual, aprobat prin hotărârea de repartizare a profitului pe baza situațiilor financiare anuale, monografia este: repartizare pe seama rezultatului reportat (1171=457), reținere impozit (457=446) și, la plată, viramentul net (457=5121). Pentru dividendul interimar, distribuit trimestrial înainte de aprobarea situațiilor anuale, OMFP 1802/2014 pct. 423^1 impune folosirea contului 463 în corespondență cu 456, iar impozitul și plata se înregistrează pe seama contului 456: 463=456 (brut), 456=446 (impozit), 456=5121 (net).

## Ce se greșește în practică

O confuzie frecventă este utilizarea contului de dividend (457) pentru sume care, de fapt, nu sunt încă un dividend aprobat, ci un avans sau o distribuire interimară — caz în care contul corect, conform OMFP 1802/2014, este 463/456, nu 1171/457. La regularizarea de la sfârșitul anului, dividendele interimare deja plătite trebuie compensate cu dividendul anual aprobat prin linia 457=463, nu recunoscute a doua oară la plata finală.

## Ce face iConta.eu

În ecranul Operațiuni speciale > Finanțare > Decontări asociați, funcția care generează nota de dividend primește suma brută, data plății și un indicator „interimar" (da/nu). Pentru dividendul anual generează liniile 1171=457 (brut) și 457=446 (impozit); pentru cel interimar, 463=456 (brut) și 456=446 (impozit). Cota de impozit este citită automat din registrul intern al aplicației, în funcție de data plății (16% de la 1 ianuarie 2026, 10% pentru plățile din 2025). Dacă operațiunea este marcată drept plătită, aplicația adaugă și linia de virament net către bancă (457=5121, respectiv 456=5121); dacă nu, dividendul rămâne evidențiat doar ca obligație de plată, fără linia de virament.

[iConta.eu](/)
