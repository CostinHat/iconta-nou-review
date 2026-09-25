---
title: "Rambursarea TVA: termenele și condițiile de soluționare"
description: "Regula generală a rambursării TVA cu inspecție fiscală ulterioară, și situațiile explicit reglementate în care ANAF trece la inspecție fiscală anticipată, înainte de a rambursa suma."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Rambursarea TVA: termenele și condițiile de soluționare

Regula de bază pentru un decont de TVA cu sumă negativă și opțiune de rambursare e simplă: organul fiscal rambursează, iar inspecția fiscală vine ulterior. Dar legea listează explicit un set de situații de risc în care ordinea se inversează — inspecția fiscală devine anticipată, iar rambursarea se amână până la finalizarea ei.

## Temeiul legal

::: ghid-temei
„(1) Taxa pe valoarea adăugată [...] solicitată la rambursare prin deconturile cu sumă negativă de TVA cu opțiune de rambursare, depuse în cadrul termenului legal de depunere, se rambursează de organul fiscal central, cu efectuarea, ulterior, a inspecției fiscale.
(3) Prevederile alin. (1) nu se aplică deconturilor cu sume negative de TVA cu opțiune de rambursare, depuse de alți contribuabili/plătitori decât cei prevăzuți la alin. (2), care se soluționează după efectuarea inspecției fiscale anticipate, în cazul în care: a) contribuabilul/plătitorul are înscrise în cazierul fiscal fapte care sunt sancționate ca infracțiuni; b) organul fiscal central, pe baza informațiilor deținute, constată că există riscul unei rambursări necuvenite; c) pentru contribuabilul/plătitorul respectiv a fost declanșată procedura de lichidare voluntară sau a fost deschisă procedura de insolvență [...]; d) contribuabilul/plătitorul depune primul decont cu sume negative de TVA cu opțiune de rambursare, după înregistrarea în scopuri de TVA; e) soldul sumei negative de TVA solicitată la rambursare provine dintr-un număr de perioade mai mare decât numărul perioadelor de raportare utilizate într-o perioadă de 12 luni."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 169 alin. (1) și alin. (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Cele două regimuri, în practică:

- **Regula generală**: rambursare rapidă, cu inspecție fiscală **ulterioară** — se aplică majorității deconturilor depuse în termen legal.
- **Excepția**: inspecție fiscală **anticipată** (deci rambursarea vine după control), pentru cinci situații explicite — cazier fiscal cu fapte penale, risc de rambursare necuvenită semnalat de organul fiscal, lichidare/insolvență, primul decont cu opțiune de rambursare după înregistrarea în scopuri de TVA, sau un sold provenit dintr-un număr de perioade mai mare decât cele utilizate normal într-un an.
- Un decont depus **după termenul legal** de depunere nu mai urmează niciuna dintre aceste căi — suma negativă se preia direct în decontul perioadei următoare, fără procedură de rambursare separată.

## Ce se greșește în practică

- Se așteaptă rambursare rapidă pentru primul decont cu opțiune de rambursare depus imediat după înregistrarea în scopuri de TVA, deși acesta intră explicit sub inspecția fiscală anticipată.
- Se depune decontul de TVA cu întârziere față de termenul legal, pierzând astfel opțiunea de rambursare a perioadei respective — suma se reportează automat, fără procedură de rambursare.
- Se confundă riscul de rambursare necuvenită (o constatare a organului fiscal, pe bază de analiză) cu simpla existență a unui sold mare de recuperat — mărimea sumei, prin ea însăși, nu declanșează automat inspecția anticipată.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează soldul de TVA de rambursat din deconturile D300 generate (`core/d300.py`), dar **nu evaluează** dacă firma se încadrează în vreuna dintre situațiile de risc de la art. 169 alin. (2)-(3), care ar declanșa inspecția fiscală anticipată. Depunerea opțiunii de rambursare și urmărirea procedurii de soluționare rămân responsabilitatea contabilului.

[iConta.eu](/)
