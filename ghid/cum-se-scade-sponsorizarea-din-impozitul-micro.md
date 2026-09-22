---
title: Cum se scade sponsorizarea din impozitul micro?
description: Facilitatea a existat între 01.04.2019 și 31.12.2023, cu un plafon de 20% din impozitul micro datorat pe trimestrul respectiv; a fost abrogată prin OUG 115/2023 și nu se mai aplică începând cu 01.01.2024, deci în 2026 microîntreprinderile nu mai pot deduce sponsorizări din impozitul pe venit.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se scade sponsorizarea din impozitul micro?

Mulți contribuabili micro știu că, la un moment dat, se putea scădea o sponsorizare direct din impozitul pe veniturile microîntreprinderilor. Este adevărat — dar facilitatea a fost **abrogată** și, în 2026, nu mai există. Explicăm mai jos atât mecanismul istoric (pentru cine corectează perioade vechi), cât și de ce, astăzi, răspunsul corect este „nu se mai scade”.

## Temeiul legal

::: ghid-temei
**Mecanismul (în vigoare 2019–2023), CF art. 56 alin. (1^1):**

„Microîntreprinderile care efectuează sponsorizări, potrivit prevederilor Legii nr. 32/1994, cu modificările și completările ulterioare, pentru susținerea entităților nonprofit și a unităților de cult, care la data încheierii contractului sunt înscrise în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale potrivit art. 25 alin. (4^1), precum și microîntreprinderile care acordă burse elevilor școlarizați în învățământul profesional-dual... scad sumele aferente din impozitul pe veniturile microîntreprinderilor până la nivelul valorii reprezentând 20% din impozitul pe veniturile microîntreprinderilor datorat pentru trimestrul în care au înregistrat cheltuielile respective.”

**Abrogarea (OUG 115/2023), în textul consolidat al Codului fiscal:**

„(1^1) Abrogat. (la 01-01-2024, Alineatul (1^1), Articolul 56, Titlul III a fost abrogat de Punctul 43., Articolul LIII, Capitolul II din ORDONANȚA DE URGENȚĂ nr. 115 din 14 decembrie 2023...)”

„(2^5) Ultimul an fiscal în care sumele reprezentând sponsorizări/burse și sumele reprezentând achiziția de aparate de marcat electronice fiscale, rămase de reportat, potrivit legii, se scad din impozitul pe veniturile microîntreprinderilor este anul fiscal 2023.”
:::

## De ce, în 2026, nu se mai aplică

Facilitatea de credit fiscal pentru sponsorizări la impozitul micro a fost activă doar **01.04.2019 – 31.12.2023**. De la 1 ianuarie 2024, alin. (1^1) al art. 56 a fost abrogat prin OUG 115/2023, iar **2023 a fost ultimul an fiscal** în care sumele de sponsorizare (inclusiv cele rămase de reportat din anii anteriori) se mai puteau scădea din impozitul micro. Practic, dacă în 2026 o microîntreprindere face o sponsorizare, aceasta **nu mai reduce impozitul pe veniturile microîntreprinderilor** — cheltuiala rămâne una obișnuită, fără tratament fiscal special la acest impozit.

*Notă de prudență privind data „01.04.2019”*: capătul de început al intervalului este cel folosit de motorul iConta.eu și de materialele informative ANAF/DGRFP consultate, dar nu am identificat, în sursele verificate, un text de lege citat cu dată explicită de intrare în vigoare „01.04.2019” — Legea nr. 30/2019, care a generalizat regula, a fost publicată la 17.01.2019, iar 01.04.2019 pare să provină din aplicarea pe trimestrul calendaristic următor, nu dintr-o dată de intrare în vigoare confirmată direct din Monitorul Oficial. Capătul final (31.12.2023) rămâne confirmat explicit de lege; dacă aveți o sponsorizare exact la granița martie/aprilie 2019, recomandăm reconfirmarea la sursă înainte de a aplica regula veche sau cea nouă.

Cât timp a fost activă, regula funcționa astfel: plafonul era **20% din impozitul micro datorat pe trimestrul** în care s-a înregistrat cheltuiala de sponsorizare — nu 20% dintr-un impozit anual, și fără niciun plafon raportat la cifra de afaceri (spre deosebire de sponsorizarea la impozitul pe profit). Condiția era, ca și la profit, ca beneficiarul să fie înscris, la data încheierii contractului, în Registrul entităților/unităților de cult.

::: ghid-exemplu
În trimestrul II din 2023, o microîntreprindere datora impozit micro de 3.000 lei și a făcut o sponsorizare de 1.000 lei către o asociație înscrisă în Registru. Plafonul deductibil era 20% × 3.000 = 600 lei, deci firma putea scădea doar 600 lei din impozitul micro al trimestrului, restul de 400 lei nemaiavând, la vremea respectivă, tratament de credit fiscal la acest impozit. Din 2024, un astfel de calcul nu se mai efectuează deloc — orice sponsorizare din 2024 încoace este, pentru impozitul micro, o cheltuială obișnuită.
:::

## Ce se greșește în practică

- Se crede că facilitatea încă există în 2024–2026 și se încearcă scăderea unei sponsorizări curente din impozitul micro — nu mai e posibil, a fost abrogată.
- Se aplică plafonul raportat la impozitul micro **anual** în loc de cel **trimestrial**, așa cum cerea legea cât timp facilitatea era activă.
- Se confundă plafonul de la micro (20% din impozitul micro trimestrial, fără legătură cu cifra de afaceri) cu plafonul de la impozitul pe profit (0,75% din cifra de afaceri / 20% din impozitul pe profit).
- Se omite verificarea înscrierii beneficiarului în Registrul entităților/unităților de cult la data încheierii contractului, pentru sponsorizările din perioada 2019–2023.

## Ce face iConta.eu

În `core/sponsorizari.py`, funcția `credit_sponsorizare(..., tip_impozit="micro", ..., la_data=None)` este activă **doar pentru `la_data` în intervalul 01.04.2019 – 31.12.2023**; în afara acestui interval, motorul returnează credit 0, cu o notă explicită de inaplicabilitate — deci pentru orice calcul făcut azi, în 2026, aplicația respinge corect deducerea. În interval, plafonul se calculează ca `plafon_m = 20% × impozit_profit`, unde parametrul `impozit_profit` este folosit, pentru ramura micro, ca fiind **impozitul micro datorat pe trimestrul respectiv** — atenție la această denumire, pentru a nu introduce din greșeală un impozit anual sau un impozit pe profit.

[iConta.eu](/)
