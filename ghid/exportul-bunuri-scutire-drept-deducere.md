---
title: "Exportul de bunuri: scutire cu drept de deducere"
description: Scutirea de export nu e automată — fără declarația vamală de export (DVE), operațiunea trebuie facturată cu TVA până la obținerea dovezii.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Exportul de bunuri: scutire cu drept de deducere

Livrarea de bunuri expediate în afara Uniunii Europene este scutită de TVA cu drept de deducere, dar scutirea nu se aplică automat doar pentru că bunul a părăsit teritoriul UE — legea o condiționează de existența dovezii vamale a exportului.

## Temeiul legal

::: ghid-temei
„Sunt scutite de taxă: a) livrările de bunuri expediate sau transportate în afara Uniunii Europene de către furnizor sau de altă persoană în contul său; ... b) livrările de bunuri expediate sau transportate în afara Uniunii Europene de către cumpărătorul care nu este stabilit în România sau de altă persoană în contul său [...]"

— Codul fiscal (Legea 227/2015 consolidat), art. 294 alin. (1) lit. a)-b)
:::

Textul acoperă două situații distincte: exportul organizat de furnizorul din România (lit. a) și exportul organizat de un cumpărător nestabilit în România, care preia bunul și îl scoate el însuși din UE (lit. b). În ambele cazuri, condiția de fond pentru scutire este dovada că bunul a ieșit efectiv din Uniunea Europeană — dovadă care, în practică, se materializează prin declarația vamală de export (DVE/EAD).

## Ce se greșește în practică

- Se emite factura fără TVA imediat, doar pe baza intenției de export, fără să existe încă declarația vamală de export — scutirea nu se justifică fără această dovadă, iar factura ar trebui, până la obținerea ei, emisă cu TVA.
- Se omite completarea țării clientului pe factura de export, deși aceasta este o informație obligatorie pentru validarea corectă a operațiunii ca export extracomunitar.
- Se tratează orice livrare către un client din afara României ca export scutit, fără să se distingă între livrarea intracomunitară (către alt stat membru UE, cu regim de TVA diferit) și exportul propriu-zis (în afara UE, sub art. 294).

## Ce face iConta.eu

Ecranul „Export extracomunitar (DVE)" (categoria Operațiuni speciale > Extern) cere data, valoarea, țara clientului (obligatorie) și dovada exportului (DVE, ca text/referință), plus o descriere opțională. Dacă nu se completează dovada exportului, aplicația respinge operațiunea cu un mesaj explicit: fără declarația vamală de export, scutirea prevăzută la art. 294 alin. (1) lit. a) nu se justifică, iar operațiunea trebuie facturată cu TVA până la obținerea dovezii.

Când dovada există, aplicația confirmă operațiunea ca fiind "scutită cu drept de deducere" în baza art. 294 alin. (1) lit. a) și generează automat nota contabilă corespunzătoare: contul de venit (implicit 707) față de contul de client (4111), doar cu valoarea operațiunii — fără nicio linie de TVA, tocmai pentru că scutirea cu drept de deducere înseamnă taxă colectată zero, nu absența dreptului de deducere pentru achizițiile legate de operațiune.

[iConta.eu](/)
