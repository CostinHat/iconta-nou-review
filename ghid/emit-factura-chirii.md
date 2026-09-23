---
title: Cum emit e-Factura pentru chirii?
description: Chiria e, din punct de vedere fiscal, o prestare de servicii — deci se facturează și se transmite prin RO e-Factura exact ca orice altă prestare. Modulul de chirii al iConta.eu generează nota contabilă, nu factura electronică propriu-zisă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum emit e-Factura pentru chirii?

Dacă închiriezi un spațiu, un utilaj sau orice alt bun unei alte firme din România, întrebarea despre e-Factura nu are un regim special „pentru chirii" — chiria intră în regulile generale de facturare electronică, la fel ca vânzarea de bunuri sau orice altă prestare de servicii.

## Temeiul legal

::: ghid-temei
„închirierea de bunuri sau transmiterea folosinței bunurilor în cadrul unui contract de leasing" — încadrează explicit chiria ca prestare de servicii.

— Codul fiscal (Legea 227/2015), art. 271 alin. (3) lit. a)
:::

## Ce înseamnă practic

Pentru că închirierea e calificată de Codul fiscal drept prestare de servicii, factura de chirie se emite după aceleași reguli ca orice altă factură de servicii: dacă relația e B2B, între două entități din România, factura intră sub obligația de transmitere prin sistemul RO e-Factura, cu regulile de termen și format (UBL, transmis prin SPV) aplicabile oricărei alte facturi de acest tip.

Mecanismul tehnic de emitere — generarea fișierului UBL, transmiterea prin SPV, urmărirea statusului de validare/respingere — nu ține de specificul chiriei, ci de fluxul general de facturare electronică al aplicației folosite. Nu există un „traseu separat" doar pentru facturile de chirie.

## Ce se greșește în practică

- Se presupune că o factură de chirie, fiind „recurentă" (aceeași sumă, lunar), nu trebuie transmisă separat prin e-Factura de fiecare dată — greșit, fiecare factură emisă intră sub aceleași obligații, indiferent de recurență.
- Se emite factura de chirie doar pe suport propriu (PDF, e-mail), fără transmitere prin SPV, din cauza confuziei că „închirierea" nu s-ar încadra ca prestare de servicii supusă e-Facturii.

## Ce face iConta.eu

Modulul de **Chirii** al iConta.eu (Operațiuni speciale) generează nota contabilă a chiriei — pentru chiria încasată, `4111 = 706` + `4111 = 4427`, cu cota de TVA introdusă explicit de utilizator. Acest modul **nu emite factura** și nu are legătură cu fluxul de transmitere prin RO e-Factura — emiterea propriu-zisă a facturii (inclusiv pentru chirii) se face din modulul de facturare al aplicației, nu din ecranul de comodat/chirii.

[iConta.eu](/)
