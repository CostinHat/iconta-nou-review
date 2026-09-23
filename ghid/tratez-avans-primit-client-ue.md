---
title: Cum tratez un avans primit de la un client din UE?
description: Avansul urmează regimul de TVA al operațiunii de bază — scutit dacă livrarea/prestarea e o operațiune intracomunitară eligibilă, altfel taxabil. Factura de avans se emite oricum, cel târziu în 15 zile de la încasare.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum tratez un avans primit de la un client din UE?

Un avans încasat de la un client dintr-un alt stat membru nu are un regim de TVA propriu, separat — el urmează exact regimul operațiunii pe care o anticipează. Dacă operațiunea de bază (livrare intracomunitară de bunuri scutită sau serviciu B2B neimpozabil în România) e eligibilă pentru scutire, avansul nu poartă TVA. Dacă nu, avansul e taxabil, la fel ca operațiunea finală.

## Temeiul legal

::: ghid-temei
Exigibilitatea TVA la avans: "b) la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine faptul generator. Avansurile reprezintă plata parțială sau integrală a contravalorii bunurilor și serviciilor, efectuată înainte de data livrării ori prestării acestora" — **art. 282 alin. (2) lit. b) Cod fiscal**.

Obligația de a emite factură pentru avans: "d) pentru orice avans încasat în legătură cu una dintre operațiunile menționate la lit. a) și b)" — **art. 319 alin. (6) lit. d) Cod fiscal**. Termenul: "persoana impozabilă trebuie să emită o factură pentru suma avansurilor încasate în legătură cu o livrare de bunuri/prestare de servicii cel târziu până în cea de-a 15-a zi a lunii următoare celei în care a încasat avansurile" — **art. 319 alin. (16) Cod fiscal**.
:::

Practic, tratamentul se stabilește în doi pași: (1) se verifică dacă operațiunea de bază e o livrare intracomunitară scutită (art. 294 alin. 2 lit. a — cod TVA valid al clientului + dovadă transport) sau un serviciu B2B neimpozabil în România (art. 278 alin. 2 — cod TVA valid al clientului); (2) avansul preia acest regim: dacă operațiunea e scutită/neimpozabilă, avansul nu generează TVA; dacă nu, avansul e taxabil cu TVA românesc, cu exigibilitate la data încasării (art. 282 alin. 2 lit. b).

Indiferent de regimul de TVA, obligația de a emite factura pentru avans rămâne — cel târziu în a 15-a zi a lunii următoare celei în care s-a încasat avansul (art. 319 alin. 16), dacă nu a fost deja emisă alta.

## Ce se greșește în practică

Greșeala cea mai frecventă: aplicarea implicită a TVA românesc pe orice avans de la un client din UE, fără să se verifice mai întâi dacă operațiunea de bază e eligibilă pentru scutire — sau, invers, tratarea automată a avansului ca scutit doar pentru că vine de la un client "din UE", fără o verificare VIES la momentul încasării.

## Ce face iConta.eu

Nota de avans încasat (`4111 = 419 + 4427`) cere explicit cota de TVA la fiecare generare — motorul nu are o cotă implicită "din motive de siguranță" (o cotă ascunsă în cod se rupe tăcut de lege la prima schimbare de reglementare). Dacă operațiunea de bază e scutită sau neimpozabilă (LIC eligibilă ori serviciu B2B validat prin VIES), se introduce cota 0, iar linia de TVA nu se generează. Motorul de avansuri e agnostic la proveniența clientului — regimul de scutire pentru operațiunile intracomunitare vine din verificarea VIES făcută la operațiunea de bază, nu dintr-o regulă separată pentru avansuri.

[iConta.eu](/)
