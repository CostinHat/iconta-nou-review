---
title: Cum se ține evidența tichetelor în casierie 2026?
description: Tichetele de masă, voucherele de vacanță și tichetele cadou nu sunt numerar și nu trec prin evidența de casierie — ele sunt bilete de valoare urmărite ca beneficii per salariat și ca note contabile, nu ca intrări/ieșiri de casă.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se ține evidența tichetelor în casierie 2026?

Întrebarea „cum țin evidența tichetelor în casierie" pornește dintr-o presupunere greșită: că tichetele de masă, voucherele de vacanță și tichetele cadou ar fi echivalate cu numerarul și gestionate ca acesta, prin registrul de casă. Legal și contabil, ele nu funcționează așa.

## Temeiul legal

::: ghid-temei
Codul fiscal (Legea 227/2015, consolidat), Articolul 142 lit. r, care definește aceste beneficii ca fiind bilete de valoare, nu numerar:

> „r) biletele de valoare sub forma tichetelor de masă, voucherelor de vacanță, tichetelor de creșă, tichetelor culturale, acordate potrivit legii;"

HG nr. 1045/2018, Articolul 17 alin. (1), privind restituirea contravalorii biletelor neutilizate:

> „La sfârșitul fiecărei luni, la sfârșitul perioadei de valabilitate, la data stabilită de angajator sau la data încetării raporturilor de muncă, după caz, salariatul are obligația să restituie angajatorului contravaloarea biletelor de valoare, pentru luna în curs sau, după caz, pentru anul în curs și neutilizate ori necuvenite."
:::

## De ce tichetele nu sunt „casierie"

Legea le numește explicit „bilete de valoare" — o categorie distinctă de numerar, cu regim fiscal propriu (impozit, CASS, excludere CAS) și cu o obligație de restituire a contravalorii neutilizate, nu de predare fizică la casă. Evidența lor contabilă corectă se face prin cheltuiala cu biletele de valoare acordate (nota 642=5328) și, separat, prin achiziția biletelor de la emitent (5328=5121/401) — ambele independente de registrul de casă și de plafonul legal de sold în casierie (Legea 70/2015, aplicabil doar numerarului și avansurilor de trezorerie).

## Ce se greșește în practică

- Se caută un „registru de tichete" în casierie, deși tichetele nu sunt tratate contabil ca numerar.
- Se amestecă plafonul de casă (Legea 70/2015) cu plafonul valorii nominale a tichetelor de masă (45 lei) sau cu plafonul anual al voucherelor de vacanță — sunt reguli complet separate.
- Se așteaptă un flux de tip „intrare tichete în casierie → ieșire la salariați", pe care nicio aplicație de salarizare nu îl gestionează ca operațiune de casă.
- Nu se face distincția între achiziția biletelor de la emitent (operațiune de trezorerie, 5328=5121/401) și acordarea lor lunară către salariați (cheltuială, 642=5328).

## Ce face iConta.eu

iConta.eu nu are — și nu trebuie căutat — un ecran de „evidență a tichetelor în casierie". Tichetele de masă sunt o configurare per salariat (valoarea nominală aleasă, până la plafonul legal), iar voucherele de vacanță și tichetele cadou sunt intrări lunare per salariat, într-un tabel dedicat de beneficii. Din aceste date, aplicația generează automat: calculul CASS/impozit pe stat de plată, nota contabilă lunară 642=5328 pentru cheltuiala cu biletele acordate și declarația D112. Modulul de casierie al aplicației tratează exclusiv numerarul și avansurile de trezorerie (conform Legii 70/2015) și nu este conectat în niciun fel la tichetele de masă, vacanță sau cadou.

[iConta.eu](/)
