---
title: "Greșeala de a nu face ajustarea TVA pentru creanțe neîncasate"
description: "Ajustarea bazei de TVA la creanțe neîncasate e un regim separat de ajustarea de la impozitul pe profit, cu termene și condiții proprii (faliment/reorganizare, sau 12 luni de la scadență la persoane fizice) — omisă des tocmai pentru că e confundată cu ajustarea de 491."
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Greșeala de a nu face ajustarea TVA pentru creanțe neîncasate

O greșeală frecventă e tratarea unei creanțe neîncasate exclusiv prin ajustarea de la impozitul pe profit (constituirea provizionului 491) și omiterea completă a ajustării bazei de impozitare a TVA — un regim separat, cu temei legal, condiții și termene proprii, care nu decurge automat din ajustarea contabilă a creanței.

## Temeiul legal

::: ghid-temei
„Baza de impozitare se reduce în următoarele situații: [...] d) în cazul în care contravaloarea bunurilor livrate sau a serviciilor prestate nu se poate încasa ca urmare a intrării în faliment a beneficiarului sau ca urmare a punerii în aplicare a unui plan de reorganizare admis și confirmat printr-o sentință judecătorească, prin care creanța creditorului este modificată sau eliminată. Ajustarea este permisă începând cu data pronunțării hotărârii judecătorești de confirmare a planului de reorganizare, iar, în cazul falimentului beneficiarului, începând cu data sentinței [...] Ajustarea se efectuează în termen de 5 ani de la data de 1 ianuarie a anului următor [...] f) în cazul în care contravaloarea totală sau parțială a bunurilor livrate sau a serviciilor prestate nu a fost încasată de la beneficiarii persoane fizice în termen de 12 luni de la termenul de plată stabilit de părți [...] Ajustarea este permisă numai în cazul în care se face dovada că s-au luat măsuri comerciale pentru recuperarea creanțelor de până la 1.000 lei, inclusiv, respectiv că au fost întreprinse proceduri judiciare pentru recuperarea creanțelor mai mari de 1.000 lei."

*(Codul fiscal — Legea nr. 227/2015, art. 287 lit. d) și f))*
:::

## De ce se omite: două regimuri, confundate în unul

Ajustarea de la impozitul pe profit (art. 26 alin. (1) lit. c) și j)) și ajustarea bazei de TVA (art. 287) au fiecare condiții și momente proprii de aplicare — una nu declanșează automat pe cealaltă:

- La impozitul pe profit, ajustarea (491) devine deductibilă 30% peste 270 de zile de scadență sau 100% la faliment declarat/insolvență, cu condiția negarantării și neafilierii.
- La TVA, ajustarea bazei se aplică fie la intrarea beneficiarului în faliment sau la confirmarea planului de reorganizare (lit. d), fie, pentru clienți persoane fizice, după 12 luni de la scadență, dar numai cu dovada demersurilor de recuperare (lit. f) — și în termen de 5 ani de la 1 ianuarie a anului următor evenimentului relevant.

Omiterea ajustării de TVA înseamnă, practic, plata în continuare a unei taxe colectate pentru o sumă care nu va mai fi niciodată încasată — un cost pe care legea permite să fie recuperat, dar numai dacă termenul și condițiile specifice sunt respectate.

## Ce se greșește în practică

- Se constituie ajustarea de 491 la impozitul pe profit și se consideră, greșit, că TVA-ul s-a „rezolvat" automat prin aceeași notă.
- Se așteaptă termenul de 270 de zile (specific impozitului pe profit) înainte de a analiza ajustarea de TVA, deși la faliment declarat aceasta e disponibilă imediat, fără prag de zile.
- La clienți persoane fizice, se omite dovada demersurilor de recuperare (comerciale sub 1.000 lei, judiciare peste 1.000 lei), fără de care ajustarea de TVA nu e permisă.
- Se pierde termenul de 5 ani de la 1 ianuarie a anului următor evenimentului relevant, după care dreptul de ajustare se stinge.

## Ce face iConta.eu

`core/provizioane.py` calculează și contabilizează exclusiv ajustarea de la impozitul pe profit (`deductibilitate_creanta`, notă 6814=491/491=7814) — aplicația nu calculează și nu generează nota de ajustare a bazei de TVA (art. 287). Verificarea condițiilor de ajustare a TVA (faliment/reorganizare, sau cei 12 luni și dovada demersurilor de recuperare la persoane fizice) și înregistrarea corespunzătoare rămân operațiuni manuale, separate de motorul F071.

[iConta.eu](/)
