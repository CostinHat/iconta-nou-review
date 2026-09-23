---
title: "Vânzarea activelor unei firme aflate în lichidare"
description: "Cum se înregistrează contabil și fiscal vânzarea unui activ de către o societate aflată în lichidare, conform Legii 31/1990."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Vânzarea activelor unei firme aflate în lichidare

Odată deschisă procedura de lichidare, societatea își păstrează personalitatea juridică exact pentru astfel de operațiuni — inclusiv vânzarea activelor rămase, pentru transformarea lor în bani înainte de partajul final către asociați.

## Temeiul legal

::: ghid-temei
Legea 31/1990, art. 255 alin. (1): lichidatorii pot „să vândă, prin licitație publică, imobilele și orice avere mobiliară a societății" și „să lichideze și să încaseze creanțele societății" [lit. c) și e)].

Legea 31/1990, art. 233 alin. (4): „Societatea își păstrează personalitatea juridică pentru operațiunile lichidării, până la terminarea acesteia."
:::

Vânzarea unui activ în timpul lichidării nu este, așadar, o operațiune interzisă sau specială — este chiar una dintre atribuțiile lichidatorului, prevăzută expres de lege. Practic, activul este scos din patrimoniu prin vânzare, iar sumele încasate intră în masa care va fi, la final, folosită pentru stingerea datoriilor și apoi repartizată asociaților.

## Ce se greșește în practică

Cea mai frecventă greșeală nu ține de dreptul de a vinde, ci de TVA: cota de TVA aplicată la vânzare este obligatorie și trebuie stabilită corect pentru fiecare activ în parte, nu preluată automat dintr-o valoare implicită. O cotă „fixată" în prealabil, fără verificare la vânzare, se poate rupe tăcut de lege la prima schimbare de regim fiscal al activului sau al societății.

## Ce face iConta.eu

Motorul de lichidare al iConta.eu înregistrează vânzarea unui activ în lichidare prin nota contabilă `461 = 7583 + 4427` (creanța față de cumpărător, pe venitul din vânzarea activului și TVA colectat), urmată de descărcarea din gestiune `6583 + 28xx = 21x` (cheltuiala cu valoarea rămasă, plus amortizarea cumulată).

Aplicația **cere obligatoriu cota de TVA** la această operațiune și refuză explicit calculul dacă aceasta lipsește — tocmai pentru a evita o cotă „scrisă în cod" care nu mai corespunde legii la o schimbare ulterioară. Această notă este disponibilă în ecranul „Lichidare / radiere firmă", la operația „Vânzare activ la lichidare", și este sufixată automat cu referința „OMFP 897/2015".

[iConta.eu](/)
