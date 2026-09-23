---
title: "Ce trebuie să depună o firmă cu TVA trimestrial și când"
description: "Ce scadențe apar pe ecranul Termene pentru o firmă plătitoare de TVA cu perioadă fiscală trimestrială, și ce nu arată acest ecran."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce trebuie să depună o firmă cu TVA trimestrial și când

Pentru o firmă plătitoare de TVA cu perioadă fiscală trimestrială, declarația de bază este D300 (decontul de TVA). Ecranul „Termene” din iConta.eu (agregarea de scadențe pe portofoliu) o include, alături de alte declarații pe care le poate datora firma, în funcție de vectorul ei fiscal.

## Temeiul legal

::: ghid-temei
D300 (decontul de TVA): „până la data de 25 inclusiv a lunii următoare celei în care se încheie perioada fiscală” — Codul fiscal (Legea 227/2015), art. 323 alin. (1)
:::

Formula legală e generică pentru perioada fiscală — lunară sau trimestrială — și se aplică exact la fel unei firme cu TVA trimestrial: decontul aferent unui trimestru se depune până pe 25 a lunii următoare încheierii acelui trimestru.

Dacă firma a avut, în perioada respectivă, operațiuni intracomunitare, se poate adăuga și D390 (Declarația recapitulativă), cu termen tot 25 a lunii următoare (OPANAF 705/2020). Pentru luna/perioada curentă, încă deschisă, D390 poate apărea marcat ca incert („posibil”), nu ca obligație fermă, până se confirmă operațiunile.

## Ce se greșește în practică

- Se așteaptă ca D300 să apară „pe zero” dacă firma n-a avut activitate în trimestru — aplicația nu ascunde declarația doar pentru că nu a avut operațiuni; termenul continuă să fie calculat normal, pe baza vectorului fiscal.
- Se ia ecranul de scadențe viitoare drept o listă completă a tuturor obligațiilor firmei — ecranul arată strict ce e scadent în următoarele 60 de zile, nu și eventualele restanțe din trecut.

## Ce face iConta.eu

Ecranul „Termene” (disponibil doar conturilor de cabinet cu portofoliu de firme, nu contului individual) derivă, pentru fiecare firmă, declarațiile datorate în următoarele 60 de zile calendaristice, pornind de la vectorul fiscal al firmei (inclusiv periodicitatea TVA). D300 apare cu data calculată conform regulii de mai sus, mutată automat pe prima zi lucrătoare dacă termenul cade în weekend sau sărbătoare legală.

Important de știut: acest ecran nu recalculează scadențele live la fiecare afișare, ci citește un model precalculat periodic de un proces de fundal — o depunere recentă poate să nu dispară instant din listă. De asemenea, ecranul nu arată restanțele (declarații deja scadente în trecut) — pentru acelea, aplicația are un ecran separat, „Semafor conformare fiscală”.

O declarație precum D205 (dividende) nu apare deloc pe acest ecran de scadențe viitoare, chiar dacă firma ar datora-o — e urmărită doar prin ecranul de semafor.

[iConta.eu](/)
