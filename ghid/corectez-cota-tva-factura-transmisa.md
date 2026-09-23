---
title: Cum corectez cota de TVA pe o factură transmisă în e-Factura?
description: O factură deja transmisă și semnată electronic de Ministerul Finanțelor nu se editează — corecția cotei se face exclusiv prin factură de stornare, urmată de o factură nouă, corectă, ambele transmise ca documente noi (art. 330 Cod fiscal).
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez cota de TVA pe o factură transmisă în e-Factura?

Odată ce o factură a fost transmisă în RO e-Factura, XML-ul cu semnătura electronică a Ministerului Finanțelor devine originalul legal al documentului — nu mai există „editare" pe el. Cota de TVA greșită se corectează exclusiv prin factură de stornare, urmată de una nouă, corectă.

## Temeiul legal

::: ghid-temei
**Art. 330 alin. (1) lit. b) din Codul fiscal**: „în cazul în care factura a fost transmisă beneficiarului, fie se emite o nouă factură care trebuie să cuprindă, pe de o parte, informațiile din factura inițială, numărul și data facturii corectate, valorile cu semnul minus sau, după caz, o mențiune din care să rezulte că valorile respective sunt negative, iar, pe de altă parte, informațiile și valorile corecte, fie se emite o nouă factură conținând informațiile și valorile corecte și concomitent se emite o factură cu valorile cu semnul minus sau, după caz, cu o mențiune din care să rezulte că valorile respective sunt negative, în care se înscriu numărul și data facturii corectate.”
:::

## Cei doi pași

**1. Stornarea facturii greșite.** Se emite o factură nouă, cu aceleași linii, dar cu cantitățile în semn negativ, care face trimitere explicită la numărul și data facturii corectate.

**2. Emiterea facturii corecte.** Cu cota de TVA corectă, ca document nou-nouț, numerotat secvențial.

Ambele documente — stornarea și factura corectă — se transmit în RO e-Factura ca facturi noi, în termenul-limită de 5 zile lucrătoare de la emiterea fiecăreia.

## Ce se greșește în practică

Cea mai frecventă confuzie: se crede că poți „retrimite" aceeași factură, cu cota modificată, ca și cum sistemul ar accepta un update pe documentul deja transmis. Nu se poate — nici tehnic (XML-ul original are deja semnătura electronică a Ministerului Finanțelor), nici legal (corectarea unei facturi transmise se face exclusiv prin document nou, conform art. 330). A doua greșeală: se emite doar factura corectă, fără stornarea celei greșite, ceea ce lasă în circuitul fiscal două documente cu cote diferite pentru aceeași operațiune, fără nicio legătură vizibilă între ele.

## Ce face iConta.eu

Generatorul intern de XML pentru e-Factura nu are, la acest moment, o rută de „editare" a unei facturi deja transmise — nu există în aplicație o operațiune de tip actualizare pe un document trimis prin sistem. Ce oferă aplicația e exact mecanismul legal: pe ecranul facturii emise există butonul **„Stornează"**, care generează automat o factură de stornare — cantități negative, referință directă la factura originală (numărul și data ei) și aceeași clasificare TVA copiată de pe original — cu o confirmare explicită înainte de execuție, pentru că acțiunea nu poate fi anulată ulterior. După stornare, se emite normal o factură nouă, cu cota corectă, care se transmite prin e-Factura ca orice altă factură, în termenul de 5 zile lucrătoare.

[iConta.eu](/)
