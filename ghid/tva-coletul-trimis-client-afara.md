---
title: TVA la coletul trimis către un client din afara UE
description: Un colet trimis de o firmă din România unui client dintr-un stat din afara Uniunii Europene este, din punct de vedere al TVA, un export - scutit cu drept de deducere, condiționat de dovada vamală de ieșire a bunurilor, indiferent de valoarea coletului.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# TVA la coletul trimis către un client din afara UE

Un colet expediat dintr-o firmă românească către un client stabilit în afara Uniunii Europene este, fiscal, o **livrare la export** — nu o achiziție sau un import. Regimul de TVA e simplu în principiu (scutire cu drept de deducere), dar depinde integral de o singură condiție: dovada că bunul a ieșit efectiv din UE.

## Temeiul legal

::: ghid-temei
Sunt scutite de taxă: a) livrările de bunuri expediate sau transportate în afara Uniunii Europene de către furnizor sau de altă persoană în contul său; [...] b) livrările de bunuri expediate sau transportate în afara Uniunii Europene de către cumpărătorul care nu este stabilit în România sau de altă persoană în contul său, cu excepția bunurilor transportate de cumpărătorul însuși și care sunt folosite la echiparea ori alimentarea ambarcațiunilor și a avioanelor de agrement sau a oricărui altui mijloc de transport de uz privat.

— Codul fiscal (Legea 227/2015), art.294 alin.(1) lit.a)-b)
:::

Scutirea de TVA la export nu depinde de valoarea coletului și nu are un prag minim sau maxim — se aplică oricărei livrări de bunuri expediate în afara UE, indiferent dacă e vorba de un colet de câțiva lei sau de o expediție de mari dimensiuni. Singura condiție reală e dovada ieșirii bunurilor din UE: declarația vamală de export (DVE/EAD) sau actul constatator echivalent emis de autoritatea vamală. Fără această dovadă, livrarea nu se poate factura ca scutită — se facturează cu TVA românesc, până la obținerea dovezii.

**De reținut, ca să nu se creeze confuzie**: regimul special pentru "loturile cu valoare intrinsecă de maximum 150 euro" din Codul fiscal (art.270 alin.(15), art.315^2, art.315^3) se aplică bunurilor **importate din afara UE către un cumpărător din UE** (de exemplu, un colet cumpărat de pe o platformă dintr-o țară terță și adus în România) — nu situației inverse, a unui colet trimis de o firmă din România către un client din afara UE. Cele două regimuri au direcții opuse și nu trebuie confundate: pentru un colet **trimis** către un client din afara UE, regimul relevant e cel de export (art.294), fără plafon de valoare.

## Ce se greșește în practică

- Se aplică din eroare pragul de 150 euro (specific importului) unei livrări la export — un colet de export nu are un asemenea prag, scutirea se aplică indiferent de valoare.
- Se facturează fără TVA înainte de a avea dovada vamală de export, apoi nu se poate justifica scutirea la un control ulterior dacă dovada nu se obține niciodată.
- Se confundă expedierea unui colet prin curier/poștă (fără procedură vamală completă de export, în anumite situații de valoare mică, unde formalitatea de export poate fi simplificată de operatorul poștal/de curierat) cu absența oricărei obligații de a păstra dovada ieșirii bunului din UE.

## Ce face iConta.eu

Livrarea de bunuri către un client din afara UE se înregistrează ca operațiune de export extracomunitar: aplicația cere țara clientului și dovada declarației vamale de export înainte de a confirma scutirea. Fără această dovadă, operațiunea nu e validată ca scutită — mesajul aplicației este explicit: fără declarația vamală de export, scutirea nu se justifică, iar operațiunea trebuie facturată cu TVA până la obținerea dovezii. Odată validată, nota contabilă generată conține doar linia de venit către client, fără linie de TVA.

De reținut onest: regimul invers descris mai sus (loturi ≤150 euro importate din afara UE, regimul special de import IOSS, declarația D399) are un motor de calcul și generare XML în aplicație, dar acesta e într-un stadiu amânat — nu are încă ecran în selectorul de declarații al unei firme obișnuite; e vizibil doar în dispecerul intern de declarații. Regimul e gândit oricum pentru entități speciale (instituții financiare, operatori OSS, accize), nu pentru un SRL obișnuit. Dacă activitatea firmei implică totuși acest tip de operațiuni, D399 nu se poate genera încă din interfața firmei și situația trebuie tratată separat, pe baza temeiului legal.

[iConta.eu](/)
