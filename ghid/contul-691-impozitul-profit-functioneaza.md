---
title: "Contul 691 și impozitul pe profit: cum funcționează"
description: De ce cheltuiala cu impozitul pe profit (cont 691) e nedeductibilă și trebuie adăugată înapoi la baza impozabilă, și cum verifică automat iConta.eu acest lucru.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Contul 691 și impozitul pe profit: cum funcționează

Contul 691 (cheltuiala cu impozitul pe profit) e unul dintre acele conturi în care o înregistrare contabilă perfect corectă poate ascunde o eroare fiscală tăcută, dacă nu e adăugată înapoi la calculul profitului impozabil.

## Temeiul legal

::: ghid-temei
„dacă soldul debitor al contului 691 (cheltuială cu impozitul pe profit) e >0 și rd.23 (P23, cheltuieli nedeductibile) e 0, se emite avertisment — cheltuiala e nedeductibilă (CF art.25 alin.(4) lit.a) și trebuie adăugată înapoi, altfel impozitul declarat iese subevaluat. Măsurat pe portofoliu (tenant_005, 2025): omisiunea a scăzut impozitul cu 2.432 lei fără niciun semn înainte de acest gard."
— sursă: `core/d101.py`, liniile 502–529, dosar de cercetare F027.
:::

Potrivit art.25 alin.(4) lit.a) din Codul fiscal, cheltuiala cu impozitul pe profit înregistrată în contul 691 este nedeductibilă fiscal. Practic, ea trebuie readăugată la profitul contabil brut atunci când se determină profitul impozabil — altfel impozitul rezultă subevaluat, pentru că firma și-ar scădea din bază propriul impozit pe care tocmai îl calculează.

Contul 691 mai are un al doilea rol în D101: soldul lui intră direct în formula de calcul automat al rezervei legale (profitul contabil brut plus cheltuiala cu impozitul din 691), deci o eroare aici se propagă în două locuri diferite din declarație.

## Ce se greșește în practică

Cea mai frecventă greșeală, confirmată chiar prin măsurători pe portofoliul de firme monitorizat, este omiterea completă a add-back-ului pentru contul 691: cheltuiala rămâne „ca atare" în calcul, fără să fie reintrodusă la rândul de cheltuieli nedeductibile din declarație. Consecința directă este subevaluarea impozitului datorat — o eroare care, fără un control dedicat, nu lasă niciun semn vizibil în declarația finală.

## Ce face iConta.eu

iConta.eu verifică automat, la generarea D101, dacă soldul debitor al contului 691 este pozitiv în timp ce rândul de cheltuieli nedeductibile (P23) este completat cu 0 — situație în care emite un avertisment explicit înainte de finalizarea declarației. Măsurat pe un portofoliu de firme monitorizat în 2025, această omisiune specifică a redus impozitul declarat cu 2.432 lei la o singură firmă, fără niciun semnal anterior introducerii acestui control — motivul pentru care iConta.eu tratează verificarea contului 691 ca pe un gard obligatoriu, nu opțional, în fluxul de generare.

[iConta.eu](/)
