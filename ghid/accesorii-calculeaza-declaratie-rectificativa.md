---
title: "Ce accesorii se calculează după o declarație rectificativă?"
description: "Cum se calculează dobânzile datorate după o corecție de declarație fiscală, de la ce dată curg și ce nu automatizează astăzi iConta.eu pe acest calcul."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce accesorii se calculează după o declarație rectificativă?

O rectificativă care mărește suma datorată nu aduce doar diferența de impozit — aduce și dobânzi de întârziere, calculate nu de la data depunerii corecției, ci de la scadența inițială a obligației. Cu cât perioada corectată e mai veche, cu atât dobânda acumulată e mai mare.

## Temeiul legal

::: ghid-temei
„(2) Pentru diferențele suplimentare de creanțe fiscale rezultate din corectarea declarațiilor sau modificarea unei decizii de impunere, dobânzile se datorează începând cu ziua imediat următoare scadenței creanței fiscale pentru care s-a stabilit diferența și până la data stingerii acesteia, inclusiv."
— Codul de procedură fiscală (Legea 207/2015), art. 174 alin. (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Dobânda nu curge de la data depunerii rectificativei, ci de la **scadența inițială** a obligației corectate — o rectificativă depusă azi pentru o perioadă de acum doi ani aduce dobândă pe toți cei doi ani, nu doar de la momentul corecției.
- Regula funcționează și invers: dacă diferența rezultată din corectare e negativă față de suma stabilită inițial (adică s-a plătit în plus), „se datorează dobânzi pentru suma datorată după corectare ori modificare, începând cu ziua imediat următoare scadenței" — aceeași sursă, art. 174 alin. (3).
- Dobânda se calculează „pentru fiecare zi de întârziere, începând cu ziua imediat următoare termenului de scadență și până la data stingerii sumei datorate, inclusiv" — regula generală, art. 174 alin. (1), care se aplică și diferențelor din rectificative.

## Ce se greșește în practică

- Se calculează dobânda doar de la data depunerii declarației rectificative, ignorând că legea o leagă de scadența inițială — rezultat: o sumă de plătit subestimată, adesea semnificativ.
- Se uită complet de accesorii la o corecție veche, presupunând că „doar impozitul" se datorează — dobânda se aplică automat oricărei diferențe suplimentare, indiferent cât de veche e perioada.
- Se confundă dobânda (accesoriu automat, legat de întârziere) cu penalitatea de nedeclarare, care are reguli și cote proprii, distincte.

## Ce face iConta.eu

Motorul care generează declarația 710 (formularul de rectificare descris în acest ghid) produce doar XML-ul corecției — pereche sumă inițială/sumă corectată, pe codul de obligație ales (121 sau 103) — și **nu calculează** dobânzile aferente diferenței rezultate. Accesoriile fiscale datorate ca urmare a unei rectificative nu sunt, la acest moment, o funcție automatizată în fluxul D710 al iConta.eu: contribuabilul trebuie să estimeze sau să aștepte decizia ANAF privind obligațiile fiscale accesorii, calculate separat, pe baza scadenței inițiale a sumei corectate.

[iConta.eu](/)
