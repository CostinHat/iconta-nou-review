---
title: "Stocuri ca gaj pentru un credit: tratament contabil"
description: "Ce se întâmplă contabil cu stocurile puse drept gaj pentru un credit bancar, chiar dacă sunt fizic predate creditorului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Stocuri ca gaj pentru un credit: tratament contabil

Când o firmă obține un credit bancar și pune drept garanție anumite stocuri (de exemplu mărfuri depozitate într-un antrepozit controlat de bancă, sau produse gajate în favoarea unui creditor), apare întrebarea firească: mai rămân aceste bunuri „stocul" firmei, sau trec în evidența creditorului odată predate fizic? Reglementările contabile dau un răspuns clar și diferit de intuiția „cine deține bunul îl și înregistrează".

## Temeiul legal

::: ghid-temei
„Înregistrarea în contabilitate a intrării stocurilor se efectuează la data transferului riscurilor și beneficiilor. [...] Totuși, pot exista decalaje de timp, de exemplu, pentru: – bunuri vândute în consignație sau stocurile la dispoziția clientului; [...] – stocuri gajate livrate creditorului beneficiar al gajului, care rămân în evidența debitorului până la vânzarea lor [...]"
— OMFP 1802/2014, Reglementări contabile, pct. 283 alin. (1)-(2) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Regula-cheie pentru acest caz specific:

- Criteriul de recunoaștere a stocului nu e „cine deține fizic bunul", ci **cine păstrează riscurile și beneficiile** aferente lui — proprietatea juridică asupra bunului gajat rămâne la debitor, chiar dacă bunul e predat fizic creditorului drept garanție.
- Stocurile gajate și livrate efectiv creditorului beneficiar al gajului **rămân în evidența (gestiunea) debitorului**, tocmai pentru că debitorul continuă să poarte riscurile asociate (deprecierea, pierderea de valoare) și beneficiile (dreptul de a le vinde și de a recupera diferența peste valoarea garantată) până la eventuala lor vânzare.
- Abia la vânzarea efectivă a bunurilor gajate (de exemplu, în caz de executare a garanției de către creditor pentru neplata creditului) are loc și transferul contabil — scoaterea din gestiunea debitorului și recunoașterea vânzării, cu toate consecințele fiscale aferente (TVA, venit din vânzare).

## Ce se greșește în practică

- Se scot din evidența contabilă bunurile gajate din simplul motiv că au fost predate fizic creditorului (de exemplu, depuse într-un depozit al băncii) — ceea ce e greșit atâta timp cât proprietatea și riscurile rămân la debitor.
- Se omite menționarea în notele explicative a activelor grevate de garanții reale (gaj, ipotecă) în favoarea creditorilor — o informație relevantă pentru cititorii situațiilor financiare, chiar dacă bunul rămâne înregistrat ca stoc propriu.
- Se confundă tratamentul stocurilor gajate cu cel al bunurilor vândute în consignație — ambele sunt excepții de la coincidența dintre livrare și transferul de proprietate, dar au consecințe juridice și fiscale diferite.

## Ce face iConta.eu

Acest subiect ține de tratamentul contabil al garanțiilor reale asupra stocurilor, nu de funcționalitatea F086 (sponsorizări și credit fiscal) documentată pentru acest ghid — sunt două sensuri complet diferite ale cuvântului „credit" (garanție bancară vs. reducere de impozit pentru sponsorizare). Cercetarea disponibilă a verificat direct în cod exclusiv motorul de sponsorizări și garda de plafon din D101 (`core/sponsorizari.py`, `core/d101.py`); nu avem o verificare a vreunui modul din iConta.eu pentru gestiunea stocurilor gajate sau pentru evidența garanțiilor reale, așa că nu facem nicio afirmație — pozitivă sau negativă — despre o astfel de funcție, pentru a nu inventa ce nu am verificat.

[iConta.eu](/)
