---
title: "Cum se contabilizează cupoanele de reducere aplicate în WooCommerce?"
description: "O reducere de preț acordată direct clientului nu intră în baza de impozitare a TVA — iar prețul deja redus, așa cum îl calculează WooCommerce, e exact ce preia automat iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează cupoanele de reducere aplicate în WooCommerce?

Un cod de reducere aplicat la finalizarea comenzii (cupon de 10%, „reducere de bun venit" etc.) scade prețul plătit de client — întrebarea contabilă e cum se reflectă asta pe factură și în baza de impozitare a TVA.

## Temeiul legal

::: ghid-temei
„Baza de impozitare nu cuprinde următoarele: a) rabaturile, remizele, risturnele, sconturile și alte reduceri de preț, acordate de furnizori direct clienților la data exigibilității taxei."
— Legea 227/2015 (Codul fiscal), art. 286 alin. (4) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- O reducere de preț (rabat, discount, cupon) acordată direct clientului, la momentul vânzării, nu intră în baza de impozitare a TVA — TVA se calculează la prețul deja redus, nu la prețul de listă.
- Condiția e ca reducerea să fie acordată „direct clienților la data exigibilității taxei" — adică la momentul vânzării, nu ulterior, printr-un document separat (caz în care s-ar aplica alte reguli, de ajustare a bazei de impozitare după livrare).
- Practic, un cupon aplicat la checkout-ul unui magazin online se încadrează exact în această categorie: prețul final afișat pe comandă e deja net de reducere.

## Ce se greșește în practică

- Se calculează TVA la prețul inițial, dinainte de aplicarea cuponului, iar apoi se scade separat valoarea reducerii — ceea ce dublează, de fapt, tratamentul reducerii (o dată în preț, o dată în calculul separat).
- Se tratează cuponul ca pe o cheltuială de marketing distinctă, înregistrată separat de vânzare, în loc să fie recunoscut ca o simplă reducere a prețului de vânzare.
- Se așteaptă ca aplicația de contabilitate să „vadă" undeva, explicit, existența unui cupon aplicat — de fapt, informația relevantă contabil e deja încorporată în prețul final al liniei de produs.

## Ce face iConta.eu

Conectorul WooCommerce al iConta.eu calculează prețul unitar al fiecărei linii strict din valoarea totală a liniei împărțită la cantitate (`total / cantitate`), exact așa cum vine deja calculată de WooCommerce — adică deja netă de orice cupon aplicat la finalizarea comenzii. **Nu există niciun cod care să citească separat informațiile despre cupoane sau reduceri** din comandă (verificat exhaustiv: niciun apel către aceste date în conector). Nu e o funcționalitate lipsă în sensul strict — rezultatul e corect fiindcă reducerea a fost deja aplicată de WooCommerce înainte ca iConta să citească linia —, dar nu există nicio recunoaștere explicită, la nivel de aplicație, a conceptului de „cupon de reducere".

[iConta.eu](/)
