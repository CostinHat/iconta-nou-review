---
title: "Când se colectează TVA pentru un voucher?"
description: "Regula din Codul fiscal privind exigibilitatea TVA la avansuri și cum se aplică ea vânzării unui voucher sau tichet valoric înainte de livrarea efectivă a bunului sau serviciului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Când se colectează TVA pentru un voucher?

Un voucher vândut înainte ca bunul sau serviciul să fie efectiv livrat funcționează, din punct de vedere al TVA, ca o plată în avans — iar Codul fiscal are o regulă clară pentru momentul în care taxa devine exigibilă într-o astfel de situație.

## Temeiul legal

::: ghid-temei
„(2) Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine:
a) la data emiterii unei facturi, înainte de data la care intervine faptul generator;
b) la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine faptul generator. Avansurile reprezintă plata parțială sau integrală a contravalorii bunurilor și serviciilor, efectuată înainte de data livrării ori prestării acestora;
c) la data extragerii numerarului, pentru livrările de bunuri sau prestările de servicii realizate prin mașini automate de vânzare, de jocuri sau alte mașini similare."
— Legea 227/2015 (Codul fiscal), art. 282 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Aplicat la un voucher (tichet valoric, bon cadou, card preplătit pentru un serviciu concret):

- Dacă la momentul vânzării voucherului **se cunoaște deja** bunul sau serviciul concret care va fi livrat, cota de TVA aplicabilă și locul livrării — adică vânzarea voucherului îndeplinește condițiile unei plăți în avans pentru o operațiune determinată — TVA devine exigibilă **la data încasării contravalorii voucherului**, conform art. 282 alin. (2) lit. b).
- Dacă la momentul vânzării voucherului **nu se cunosc** aceste elemente (de exemplu, un voucher cu valoare fixă, utilizabil pentru orice produs dintr-un magazin, la cote de TVA diferite), nu există încă o „livrare de bunuri sau prestare de servicii" determinabilă — condiția de aplicare a excepției de la alin. (2) lit. b) nu e îndeplinită, iar taxa devine exigibilă abia la utilizarea efectivă a voucherului, când faptul generator poate fi identificat (regula generală, art. 282 alin. (1)).
- Distincția depinde așadar de cât de determinată este operațiunea la momentul vânzării voucherului, nu de forma lui (hârtie, card, cod electronic).

## Ce se greșește în practică

- Se colectează TVA la vânzarea oricărui voucher, indiferent dacă bunul/serviciul e determinat sau nu — ceea ce înseamnă colectarea taxei înainte ca exigibilitatea să intervină legal, în cazul voucherelor cu utilizare generică.
- Se amână colectarea TVA până la utilizarea voucherului chiar și atunci când, la vânzare, bunul/serviciul și cota erau deja cunoscute — situație în care art. 282 alin. (2) lit. b) cere colectarea la încasare, ca la orice avans.
- Se ignoră cota de TVA aplicabilă la data vânzării voucherului (relevantă când operațiunea e determinată) și se aplică, greșit, cota de la data utilizării lui.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un modul dedicat vânzării de vouchere sau tichete valorice** cu calcul automat al momentului de exigibilitate a TVA în funcție de gradul de determinare a operațiunii. Aplicația tratează exigibilitatea TVA pentru avansuri și facturi în general (inclusiv sistemul TVA la încasare, prin modulul `tva_incasare`), dar încadrarea unui voucher concret ca „avans pentru operațiune determinată" sau „instrument nedeterminat" rămâne o evaluare pe care contabilul trebuie s-o facă manual, înainte de înregistrare.

[iConta.eu](/)
