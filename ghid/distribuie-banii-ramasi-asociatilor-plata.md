---
title: "Cum se distribuie banii rămași asociaților după plata datoriilor?"
description: "Cum tratează legea și contabilitatea partajul sumelor rămase în lichidare: capitalul social, neimpozabil, față de rezerve și profituri, impozitate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se distribuie banii rămași asociaților după plata datoriilor?

După ce toate activele au fost valorificate, creanțele încasate și datoriile stinse, sumele rămase se împart între asociați — dar nu toate sumele au același regim fiscal.

## Temeiul legal

::: ghid-temei
Codul fiscal (Legea 227/2015), art. 97 alin. (5): „Venitul impozabil obținut din lichidarea unei persoane juridice de către acționari/asociați persoane fizice sau din reducerea capitalului social, potrivit legii, care nu reprezintă distribuții în bani sau în natură ca urmare a restituirii cotei-părți din aporturi se impun cu o cotă de 10%, impozitul fiind final. Obligația calculării, reținerii și plății impozitului revine persoanei juridice."
:::

Legea distinge, așadar, clar între partea din sumele distribuite care reprezintă restituirea aportului la capitalul social — neimpozabilă — și câștigul propriu-zis (rezerve, profituri acumulate), care este impozabil. Textul citat mai sus prevede pentru acest câștig o cotă fixă de 10%, impozitul fiind final și calculat, reținut și plătit de societate, nu de asociat.

## Ce se greșește în practică

- Se tratează întreaga sumă distribuită asociatului ca fiind impozabilă, inclusiv partea care reprezintă restituirea capitalului social vărsat.
- Se aplică, din reflex, aceeași cotă folosită la dividendele obișnuite, fără a verifica dacă acesta este regimul corect pentru câștigul din lichidare (vedeți nota de mai jos despre iConta.eu).

## Ce face iConta.eu

Motorul de lichidare al iConta.eu calculează partajul astfel: capitalul social este tratat ca **neimpozabil** (`1012 = 456`); rezervele și profiturile sunt tratate ca „câștig impozabil" (`1061/1171 = 456`, apoi `456 = 446` pentru impozit și `456 = 5121` pentru suma netă către asociat).

**Atenție**: pentru cota de impozit aplicată câștigului, motorul iConta.eu folosește în prezent același registru de cote ca la dividendele obișnuite (16% începând cu 01.01.2026). Textul citat mai sus, din art. 97 alin. (5) al Codului fiscal, prevede însă pentru câștigul din lichidare o cotă fixă de **10%**, distinctă de cea aplicabilă dividendelor (art. 97 alin. 7). Această diferență între cota calculată de aplicație și cota prevăzută explicit de lege pentru lichidare este un aspect pe care contabilul trebuie să îl verifice suplimentar, la fiecare partaj efectuat.

[iConta.eu](/)
