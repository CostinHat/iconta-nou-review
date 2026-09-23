---
title: Cum închid un SRL care deține un imobil?
description: Ce spune legea despre vânzarea unui imobil în cursul lichidării și cum generează iConta.eu automat nota contabilă aferentă.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum închid un SRL care deține un imobil?

Un imobil rămas în patrimoniul societății la data dizolvării nu blochează lichidarea — legea permite explicit lichidatorilor să vândă imobilele, pentru a transforma acest activ în lichidități care apoi intră în circuitul de stingere a pasivului și, eventual, de partaj.

## Temeiul legal

::: ghid-temei
„lichidatorii pot [...] «să vândă, prin licitație publică, imobilele și orice avere mobiliară a societății»"
— L31/1990, art. 255 alin. (1) lit. c) (citat în dosarul de cercetare F057)
:::

Această prevedere se coroboră cu păstrarea personalității juridice a societății „pentru operațiunile lichidării, până la terminarea acesteia" (L31/1990, art. 233 alin. 4) — societatea în lichidare rămâne, deci, pe deplin capabilă să vândă imobilul, să emită factură și să încaseze prețul.

## Ce se greșește în practică

O greșeală frecventă este omiterea cotei de TVA la înregistrarea vânzării, considerând-o „implicită" ca la o vânzare obișnuită. Motorul de lichidare al iConta.eu nu are o cotă de TVA implicită pentru acest tip de operațiune — cota trebuie introdusă explicit, altfel nota contabilă nu poate fi generată.

## Ce face iConta.eu

Pentru vânzarea unui imobil (activ imobilizat) în cursul lichidării, operația „Vânzare activ la lichidare" din ecranul „Lichidare / radiere firmă" (categoria „Diverse") generează automat, pe baza prețului de vânzare, a valorii brute și a amortizării cumulate introduse, o notă contabilă combinată:

- venitul din vânzare și TVA colectată: `461 = 7583 + 4427`;
- descărcarea din gestiune a valorii rămase și a amortizării: `6583 + 28xx = 21x` (implicit 2131 pentru cont imobilizare și 2813 pentru amortizare, dacă nu se specifică altceva).

Cota de TVA este un parametru obligatoriu al funcției de calcul — aplicația nu aplică nicio cotă implicită, tocmai pentru ca nota să nu se „rupă" tăcut de lege dacă respectiva cotă se modifică ulterior. Introduceți deci explicit cota de TVA aplicabilă vânzării imobilului, în funcție de statutul de plătitor de TVA al societății.

[iConta.eu](/)
