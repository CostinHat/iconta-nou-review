---
title: "Cum declar diferența de impozit rezultată la D101?"
description: "Diferența de impozit rezultă din definitivarea anuală la cota de 16%, dar D101 rectificativă nu este încă disponibilă în aplicație."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Cum declar diferența de impozit rezultată la D101?

Diferența de impozit pe profit rezultă din definitivarea anuală (P40 × 16% = P411). Dacă însă diferența apare pentru că a fost descoperită o eroare DUPĂ depunerea D101, situația e diferită — și trebuie tratată onest.

Pentru definitivarea normală, impozitul rezultat este cota de 16% (CF art.17) aplicată pe profitul impozabil final (P40 → P411), după deduceri, add-back-uri și rezerva legală.

Dacă însă apare o diferență pentru că declarația inițială conținea o eroare, trebuie spus clar: **aplicația nu generează, în prezent, o D101 rectificativă din interfață**. D710 — motorul de rectificativă din iConta — acoperă explicit doar D100 (cod 121 micro / cod 103 profit trimestrial), nu D101. Procedura de rectificare a D101 e stabilită de instrucțiunile de completare aprobate prin OPANAF 206/2025 (anexa nr. 1, cap. I pct. 3, citat mai jos): declarația rectificativă se întocmește pe același model de formular, înscriind „X” în spațiul special prevăzut în acest scop; căsuța „Declarație rectificativă ca urmare a unei notificări de conformare” se bifează când corectarea vine dintr-o notificare de conformare. Corectarea se poate face pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale (Codul de procedură fiscală, art. 105, citat mai jos).

## Temeiul legal

::: ghid-temei
„Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%.”
— Codul fiscal, art. 17 (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. [...] Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative.”
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 105 alin. (1) și (3) (sursă: [Legea nr. 207/2015 privind Codul de procedură fiscală](https://legislatie.just.ro/Public/DetaliiDocument/170007))

„În cazul în care plătitorul corectează declarația depusă, declarația rectificativă se întocmește pe același model de formular [...]”
— OPANAF nr. 206/2025, anexa nr. 1, Instrucțiuni de completare a formularului 101, cap. I pct. 3 (sursă: [OPANAF nr. 206/2025 pentru aprobarea formularelor 101](https://legislatie.just.ro/Public/DetaliiDocument/294776))
:::

## Ce se greșește în practică

Greșeala e să se aștepte ca o simplă redepunere prin aplicație, cu date corectate, să genereze automat o D101 rectificativă — flag-urile necesare nu sunt, în prezent, accesibile din interfață.

## Ce face iConta.eu

Pentru definitivarea inițială, aplicația calculează impozitul conform cotei de 16% și validărilor descrise în ghidurile dedicate. Pentru o eroare descoperită după depunere, corectarea trebuie făcută în prezent direct la ANAF sau printr-un flux din afara aplicației, aplicația neavând un parametru pentru a seta flag-urile de rectificare din structura D101.

[iConta.eu](/)
