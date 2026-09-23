---
title: Cum configurez calendarul fiscal al firmei mele
description: Calendarul fiscal din iConta.eu se generează automat, pe baza tipului fiecărei declarații — nu există, în dosarul verificat, o configurare manuală a datelor. Ecranul „Termene" afișează scadențele deja calculate, inclusiv mutările pentru weekend și sărbători legale.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum configurez calendarul fiscal al firmei mele

Termenul „configurare" poate lăsa impresia unei setări manuale a datelor de scadență. Din verificarea codului sursă al funcționalității, calendarul fiscal nu se configurează manual — se **generează automat**, pentru fiecare tip de declarație relevant firmei, pe baza tipului declarației, anului și lunii sau trimestrului de raportare.

## Temeiul legal

::: ghid-temei
„...sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate." — Codul fiscal, art.147 alin.(1) (exemplu de temei pentru unul dintre tipurile calculate automat, D112)
:::

## Cum funcționează, concret

1. Pentru fiecare tip de declarație (D112, D205, D300, D301, D390, D394, D406), aplicația calculează automat data nominală a scadenței — de regulă ziua 25 a lunii următoare, cu excepțiile confirmate: D394 pe ziua 30, D406 pe ultima zi a lunii, D205 pe ultima zi a lunii februarie a anului următor.
2. Data nominală e verificată față de calendarul sărbătorilor legale (zile fixe plus cinci zile mobile derivate din Paștele ortodox, calculat pentru 2024–2099) și față de weekend — dacă e cazul, termenul se mută pe următoarea zi lucrătoare.
3. Rezultatul — scadența reală, deja mutată dacă a fost necesar — e afișat în ecranul „Termene" al aplicației.

**De semnalat onest**: nu am identificat, în dosarul verificat, un ecran sau o opțiune de configurare manuală a calendarului (de exemplu, activarea/dezactivarea unui tip de declarație, sau introducerea manuală a unei date). Ecranul „Termene" (`static/js/ecrane/termene.js`) apelează un serviciu (`GET /termene`) care returnează scadențele deja calculate — „configurarea" ține, cel mai probabil, de datele generale ale firmei (tipul de contribuabil, perioada fiscală de TVA lunară/trimestrială etc.), care determină ce tipuri de declarații i se aplică, nu de o setare separată a calendarului însuși. Dacă aplicația oferă totuși o opțiune de configurare explicită a calendarului, aceasta nu a fost confirmată în acest dosar.

## Ce se greșește în practică

- Se caută o opțiune de „adăugare manuală" a unui termen fiscal, deși calendarul e generat automat din tipul declarațiilor aplicabile firmei.
- Se presupune că datele de scadență afișate sunt fixe an de an — de fapt, mutările pentru weekend și sărbători legale mobile (calculate după Paștele ortodox) pot schimba data reală de la un an la altul.

## Ce face iConta.eu

Calendarul fiscal se generează automat din tipul de declarații aplicabile firmei, fără o configurare manuală separată a datelor de scadență — ecranul „Termene" afișează direct scadența reală, deja mutată pentru weekend sau sărbătoare legală, pentru fiecare tip de declarație relevant.

[iConta.eu](/)
