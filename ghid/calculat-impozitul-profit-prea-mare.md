---
title: "Ce fac dacă am calculat impozitul pe profit prea mare?"
description: "Identifică, pe baza dosarului, cauze documentate ale unei supraevaluări a impozitului pe profit, inclusiv aplicarea în 2026 a cotei IMCA de 1% în locul celei de 0,5%."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Ce fac dacă am calculat impozitul pe profit prea mare?

## Temeiul legal

::: ghid-temei
„Pentru anul fiscal 2026/anul fiscal modificat care începe în anul 2026, cota de impozit din cadrul formulei prevăzute la alin. (3) este 0,5%. [...] Prevederile prezentului articol se aplică până la data de 31 decembrie 2026 inclusiv/ultima zi a anului fiscal modificat care se încheie în anul 2027 inclusiv.”
— Codul fiscal (Legea nr. 227/2015), art. 18^1 alin. (16) și (17) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Pentru firmele mari (cifră de afaceri anul precedent peste 50.000.000 EUR), o cauză documentată de supraevaluare pentru anul fiscal 2026 este calculul impozitului minim pe cifra de afaceri (IMCA) cu cota de 1%, deși legea prevede explicit 0,5% pentru 2026 (art.18^1 alin.(16)). O altă cauză posibilă, pentru firme obișnuite, e omiterea unei deduceri legitime (amortizare fiscală P11, rezervă legală P13).

## Ce se greșește în practică

Verificați întâi dacă firma se încadrează la IMCA pentru 2026 — dacă da și s-a aplicat cota de 1%, impozitul minim calculat e dublu față de cel legal.

## Ce face iConta.eu

În D101, iConta.eu folosește cota IMCA a anului fiscal: 1% pentru 2024–2025 și 0,5% pentru anul fiscal 2026 (art.18^1 alin.(16) CF, introdus prin OUG 89/2025); de la 2027 IMCA nu se mai aplică (art.18^1 alin.(17)). Dacă cifra de afaceri a anului precedent (în EUR) transmisă depășește pragul IMCA de 50.000.000 EUR și rândul P47 nu a fost completat manual, iConta.eu cere explicit această valoare înainte de generare — nu subevaluează tacit impozitul unei firme mari. iConta.eu nu generează în prezent o D101 rectificativă din interfață: toate flagurile de stare din structura XML (`d_rec`, `d_reg`, `d_reglem`, `d_anulare`, `d_succ`, `d_prof`, `d_alte`) sunt fixate la `"0"` direct în cod („generarea XML-ului declarației (Declarații)”, aplicația), fără niciun parametru de intrare care să le poată seta. Modulul de rectificative din aplicație (D710) acoperă doar obligațiile declarate prin D100 (cod 121 micro / cod 103 profit trimestrial), nu și D101. Corectarea unei D101 deja depuse trebuie făcută astăzi direct la ANAF, în afara aplicației; nici sursele legale locale nu conțin un act normativ dedicat procedurii de rectificare a D101 (spre deosebire de D710, unde OPANAF 649/2025 e citat explicit), deși structura XML oficială (OPANAF 206/2025 (structura D101)) confirmă existența flagului `d_rec` la nivel de formular.

[iConta.eu](/)
