---
title: "Cum se taxează indemnizația de delegare?"
description: "Mecanismul de impozitare a indemnizației de delegare/detașare (diurnă) atunci când depășește plafonul neimpozabil stabilit de Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se taxează indemnizația de delegare?

Indemnizația de delegare (diurna) nu e nici integral neimpozabilă, nici integral impozabilă „din start" — legea o tratează în două tranșe: partea de până la un plafon calculat legal rămâne neimpozabilă, iar partea care depășește plafonul se taxează exact ca salariul, cu impozit pe venit și contribuții sociale.

## Temeiul legal

::: ghid-temei
„k) indemnizația de delegare, indemnizația de detașare, inclusiv indemnizația specifică detașării transnaționale, [...] precum și orice alte sume de aceeași natură, altele decât cele acordate pentru acoperirea cheltuielilor de transport și cazare, primite de salariați potrivit legislației în materie, pe perioada desfășurării activității în altă localitate, în țară sau în străinătate, în interesul serviciului, pentru partea care depășește plafonul neimpozabil stabilit astfel: (i) în țară, 2,5 ori nivelul legal stabilit pentru indemnizație, prin hotărâre a Guvernului, pentru personalul autorităților și instituțiilor publice, în limita a 3 salarii de bază corespunzătoare locului de muncă ocupat."
— Codul fiscal (Legea 227/2015), art. 76 alin. (2) lit. k) pct. (i) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul de taxare, pas cu pas:

- Textul include indemnizația de delegare în categoria veniturilor asimilate salariilor (art. 76, care le tratează pe toate ca „venituri din salarii" pentru partea impozabilă) — deci nu e un venit de altă natură, tratat separat.
- Prima tranșă, până la plafonul de 2,5 ori nivelul bugetar (23 lei/zi din 2023, deci 57,5 lei/zi), cu limita suplimentară de 3 salarii de bază pentru toată deplasarea, rămâne **neimpozabilă** — nu intră în baza de calcul a impozitului pe venit, CAS sau CASS.
- Partea care depășește plafonul devine **venit salarial impozabil**: se adaugă la baza de calcul a impozitului pe venit (10%), CAS (25%) și CASS (10%), exact ca orice altă sumă din statul de plată al lunii respective.
- Cheltuielile de transport și cazare, decontate separat pe bază de documente justificative, **nu intră deloc** în acest calcul — plafonul vizează strict indemnizația (diurna), nu totalul decontului de deplasare.

## Ce se greșește în practică

- Se taxează integral diurna de la prima zi, ignorând partea neimpozabilă de sub plafon — sau, invers, se lasă neimpozabilă toată suma acordată, chiar și partea care depășește plafonul.
- Se include, în calculul plafonului, și transportul sau cazarea decontate cu documente — acestea sunt tratate distinct de indemnizația propriu-zisă.
- Se aplică plafonul lunar în loc de cel zilnic înmulțit cu numărul de zile de deplasare efective, ceea ce poate scădea artificial suma neimpozabilă admisă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează automat, din modulul `core/deconturi.py`, partea neimpozabilă și partea impozabilă a diurnei acordate, aplicând regula legală (minimul dintre 2,5× diurna bugetară și 3× salariul de bază raportat la zilele lucrătoare din lună), separat de transport și cazare, decontate pe justificative. Nota contabilă generată separă corect diurna neimpozabilă (contul 625) de cea impozabilă, care trece prin statul de plată (contul 641), astfel încât suma corectă ajunge în baza de calcul a impozitului și contribuțiilor.

[iConta.eu](/)
