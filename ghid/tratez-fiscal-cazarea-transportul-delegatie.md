---
title: "Cum tratez fiscal cazarea și transportul în delegație?"
description: "Cheltuielile de transport și cazare decontate pe bază de documente justificative în delegație sunt neimpozabile integral, spre deosebire de diurnă, care are un plafon."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez fiscal cazarea și transportul în delegație?

Codul fiscal tratează diferit cele trei componente ale unei deplasări în interes de serviciu: diurna are un plafon neimpozabil peste care devine venit salarial impozabil, în timp ce cheltuielile de transport și cazare decontate pe bază de documente justificative sunt scoase explicit din calculul acestui plafon — practic, rambursarea lor integrală nu generează impozit, indiferent de sumă.

## Temeiul legal

::: ghid-temei
„Indemnizația de delegare, indemnizația de detașare, inclusiv indemnizația specifică detașării transnaționale, [...] precum și orice alte sume de aceeași natură, altele decât cele acordate pentru acoperirea cheltuielilor de transport și cazare, primite de salariați potrivit legislației în materie, pe perioada desfășurării activității în altă localitate, în țară sau în străinătate, în interesul serviciului, pentru partea care depășește plafonul neimpozabil [...]."
— Codul fiscal (Legea 227/2015), art. 76 alin. (2) lit. k) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Formularea legii este cheia: plafonul neimpozabil se aplică **doar indemnizației de delegare/detașare (diurnei) și sumelor similare**, nu și cheltuielilor de transport și cazare — acestea sunt exceptate explicit din text („altele decât cele acordate pentru acoperirea cheltuielilor de transport și cazare").
- Practic, dacă transportul și cazarea sunt decontate pe bază de documente justificative (bilete, facturi de hotel), suma respectivă **nu intră deloc în calculul venitului asimilat salariilor** și nu poate genera impozit sau contribuții, indiferent cât de mare e valoarea ei.
- Diurna, în schimb, e neimpozabilă doar până la plafonul stabilit prin hotărâre de Guvern pentru personalul instituțiilor publice (majorat de regulă cu un multiplicator pentru mediul privat) — partea care depășește acest plafon devine venit impozabil, asimilat salariilor.
- Regula de mai sus se aplică salariaților; pentru administratori și directori cu contract de mandat, legea prevede un text similar, dar cu un plafon calculat diferit (raportat la remunerația din contractul de mandat, nu la salariul de bază).

## Ce se greșește în practică

- Se plafonează și cheltuielile de transport și cazare la același nivel ca diurna, deși legea le exceptează explicit din calculul plafonului neimpozabil.
- Se decontează transport și cazare fără documente justificative, tratându-le ca diurnă — fără factură/bilet, suma riscă să fie reîncadrată de organul fiscal ca venit salarial impozabil.
- Se confundă plafonul aplicabil salariaților (raportat la salariul de bază) cu cel aplicabil administratorilor/directorilor cu contract de mandat (raportat la remunerația din contract) — cele două calcule nu sunt interschimbabile.
- Se omite recalcularea plafonului lunar al diurnei proporțional cu zilele lucrătoare din lună și cu numărul de zile efective de deplasare.

## Ce face iConta.eu

Aplicația are un modul dedicat deconturilor de deplasare, cu funcția `plafon_diurna`, care calculează plafonul neimpozabil al diurnei direct pe baza art. 76 alin. (2) lit. k) și alin. (4^1) din Codul fiscal (diurna bugetară x 2,5, cu ajustare pe zile lucrătoare). Modulul de decont susține și componentele de transport și cazare pe justificative, contate separat de diurnă (contul 625, cu TVA deductibil aferent facturilor de cazare/transport), tratându-le corect ca sume distincte de plafonul diurnei, conform textului de lege.

[iConta.eu](/)
