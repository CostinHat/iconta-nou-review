---
title: "Cum verific D390 cu contabilitatea?"
description: "Ce compară exact controlul automat dintre D390 și evidența contabilă, ce culoare primește fiecare situație și ce înseamnă de fapt „evidență validată" în acest control."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific D390 cu contabilitatea?

Controlul automat dintre D390 și contabilitate nu compară declarația cu balanța de verificare, ci cu notele contabile validate care sunt legate direct de facturile intracomunitare din perioadă.

## Temeiul legal

::: ghid-temei
„art. 325 Cod fiscal (Legea 227/2015)" — declarația recapitulativă (D390): obligație, conținut, depunere lunară; „OMFP 1802/2014" — temeiul pentru evidența contabilă / nota validată vs. ciornă (citate ambele în codul de control al aplicației, la fiecare constatare generată).
:::

## Ce se greșește în practică

- Se presupune că verificarea se face pe balanța de verificare (solduri/rulaje de cont) — nu e cazul; sursa „evidenței" în acest control e strict lista facturilor intracomunitare din perioadă, cu verificarea dacă au notă contabilă legată și **validată**.
- Se ia în calcul o notă aflată încă în ciornă ca dovadă de contare — ciorna e semnalată separat, dar nu contează ca evidență confirmată.
- Se așteaptă „roșu" pentru orice diferență de cifre — de fapt, o diferență de sumă între ce e declarat și ce e în evidență primește culoarea gri (posibil decalaj de perioadă, regularizări sau rotunjire), nu roșu; roșu apare doar când operațiunea e declarată la VIES dar nu are nimic în evidența validată.

## Ce face iConta.eu

Controlul ia bazele de livrări (L) și achiziții (A) intracomunitare calculate pentru D390 și le compară cu facturile intracomunitare din aceeași perioadă, verificând pentru fiecare dacă are o notă contabilă legată de acea factură, cu statusul „validată" — nu doar existența unei note oarecare, și nu ciorna.

Regulile de rezultat sunt fixe:
- dacă ambele valori sunt zero, nu se raportează nimic;
- dacă diferența e sub toleranța de rotunjire la leu, verde;
- dacă operațiunea e declarată (la VIES) dar evidența validată arată zero, roșu, cu remediu sugerat (fie contabilizează operațiunea, fie corectează D390) — dar corecția o confirmă întotdeauna omul, nu se aplică automat;
- dacă evidența arată mai mult decât declaratul, gri (posibil decalaj de perioadă, direcție considerată „mai puțin sigură" decât inversul);
- dacă ambele sunt peste zero dar cifrele diferă, tot gri — niciodată roșu doar pe diferență de cifre, pentru că decalajul de exigibilitate, regularizările sau rotunjirile sunt considerate motive legitime.

Onest: acest control nu citește balanța contabilă și nu are nicio interogare pe solduri sau rulaje de cont — verificarea e strict pe perechea factură intracomunitară + notă contabilă validată legată de ea.

[iConta.eu](/)
