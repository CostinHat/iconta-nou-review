---
title: "D205 pentru dividende plătite prin aplicarea de active"
description: "Ce spune legea despre dividendul distribuit în natură, printr-un transfer (predare) de active către asociat, și ce limite reale există în evaluarea și evidența lui pentru D205."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# D205 pentru dividende plătite prin aplicarea de active

Din punct de vedere fiscal, nu există o categorie de „plată prin aplicarea de active" — termenul corect din lege e distribuirea dividendului „în natură", adică prin predarea unui bun către asociat, în locul unei sume de bani. Legea nu limitează dividendul la o plată în bani — o firmă poate stinge obligația de dividend predând asociatului un bun (un mijloc fix, de exemplu), în loc să vireze sume. Fiscal, e tot dividend, cu aceleași obligații de reținere la sursă; ce diferă e modul în care se stabilește suma pe care se calculează impozitul.

## Temeiul legal

::: ghid-temei
„dividend - o distribuire în bani sau în natură, efectuată de o persoană juridică unui participant, drept consecință a deținerii unor titluri de participare la acea persoană juridică, exceptând următoarele: [...]"
— Codul fiscal (Legea 227/2015), art. 7 pct. 11 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Definiția fiscală a dividendului include explicit distribuirea „în natură", alături de cea „în bani" — un transfer de activ către asociat, drept consecință a deținerii de titluri de participare, se supune acelorași reguli fiscale ca un dividend plătit cash sau prin bancă.
- Cota de impozit și termenele de reținere/virare rămân cele din CF art. 97 alin. (7) — natura plății (bani sau bun) nu schimbă regimul fiscal al dividendului, doar modul de evaluare a bazei impozabile.
- Evaluarea corectă a bunului predat (de regulă la valoare justă/de piață, potrivit reglementărilor contabile aplicabile) e pasul care stabilește, de fapt, suma pe care se calculează impozitul — o evaluare greșită duce direct la un impozit reținut greșit.

## Ce se greșește în practică

- Se înregistrează transferul de activ la valoarea contabilă (rămasă neamortizată) a bunului, fără o evaluare separată la valoarea de piață, ceea ce poate subestima baza impozabilă a dividendului.
- Se tratează predarea de active ca pe o operațiune „în afara" circuitului obișnuit de dividende, uitând că impozitul pe dividende (reținere la sursă) se datorează la fel ca la o plată în bani.
- Se omite documentul justificativ care să ateste valoarea la care activul a fost predat (evaluare, proces-verbal de predare-primire), lăsând suma din contabilitate fără o bază verificabilă.

## Ce face iConta.eu

Motorul care generează D205 citește suma dividendului direct din notele contabile pe contul 457 (distribuit/plătit), fără să distingă natura plății — bani sau bun. Practic, dacă stingerea obligației de dividend printr-un transfer de activ e înregistrată contabil ca notă care debitează 457 (indiferent de contul de contrapartidă), suma respectivă intră în baza impozabilă din D205 la fel ca o plată în bani.

Aplicația nu conține însă nicio regulă proprie de evaluare a dividendului în natură — nu calculează și nu verifică dacă suma înregistrată corespunde valorii de piață a bunului predat. Această evaluare, cu tot ce presupune ea din reglementările contabile aplicabile, rămâne integral responsabilitatea contabilului: iConta.eu preia suma deja stabilită și înregistrată, nu o recalculează.

[iConta.eu](/)
