---
title: Ce înseamnă taxare inversă la achizițiile din Uniunea Europeană?
description: La achizițiile de bunuri sau servicii din UE nu se aplică taxarea inversă internă din art. 331, ci mecanismul distinct de autolichidare al beneficiarului prevăzut de art. 307 alin. (2)-(6) Cod fiscal.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce înseamnă taxare inversă la achizițiile din Uniunea Europeană?

Mulți contabili folosesc expresia "taxare inversă" și pentru achizițiile de bunuri sau servicii din alte state membre UE. Colocvial termenul e potrivit — și aici plata TVA se mută de la furnizor la beneficiar — dar din punct de vedere legal e vorba despre un mecanism diferit de cel reglementat la art. 331 Cod fiscal (taxare inversă internă, aplicabilă doar celor 12 categorii de bunuri/servicii de la art. 331 alin. (2), și doar pentru operațiuni în interiorul țării). Achizițiile din UE au alt temei: art. 307 alin. (2)-(6) Cod fiscal.

## Temeiul legal

::: ghid-temei
**Articolul 307 — Persoana obligată la plata taxei pentru operațiunile taxabile din România**

**(1)** Persoana obligată la plata taxei pe valoarea adăugată, dacă aceasta este datorată în conformitate cu prevederile prezentului titlu, este persoana impozabilă care efectuează livrări de bunuri sau prestări de servicii, cu excepția cazurilor pentru care beneficiarul este obligat la plata taxei conform alin. (2)-(6) și art. 331.

**(2)** Taxa este datorată de orice persoană impozabilă [...] care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României [...]

**Articolul 331 alin. (5):** Prevederile prezentului articol se aplică numai pentru livrările de bunuri/prestările de servicii în interiorul țării.
:::

## De ce nu e art. 331, ci art. 307

Art. 331 alin. (5) exclude explicit orice operațiune care nu are loc "în interiorul țării" — deci prin definiție nu poate acoperi o achiziție de la un furnizor stabilit în alt stat membru. Pentru bunuri cumpărate din UE, operațiunea e o achiziție intracomunitară; pentru servicii cumpărate de la un prestator stabilit în UE (locul prestării fiind în România, conform art. 278 alin. (2)), beneficiarul din România devine persoana obligată la plata TVA conform art. 307 alin. (2)-(6) — un mecanism de autolichidare, structurat diferit de cel de la art. 331 (categorii de bunuri limitate, prag de 22.500 lei la unele dintre ele, termen 31.12.2026), deși efectul practic pentru beneficiar — taxă colectată și deductibilă simultan — pornește din aceeași logică de simplificare.

## Ce se greșește în practică

- Se caută categoria achiziției (bun/serviciu) printre cele 12 litere de la art. 331 alin. (2), deși acestea nu au relevanță pentru o operațiune transfrontalieră.
- Se aplică din reflex pragul de 22.500 lei valabil la art. 331 alin. (7), deși acesta nu are legătură cu achizițiile din UE.
- Se confundă „taxare inversă" (art. 331, intern) cu „autolichidare TVA" (art. 307, transfrontalier) ca și cum ar fi aceeași procedură cu aceleași condiții de eligibilitate.
- Se omite verificarea codului de TVA valabil în VIES al furnizorului din UE, condiție practică pentru tratarea corectă a operațiunii ca intracomunitară.
- Se emite/înregistrează factura fără autolichidarea TVA-ului aferent, ca și cum furnizorul UE ar datora taxă românească.

## Ce face iConta.eu

Modulul de taxare inversă al iConta.eu (motorul care implementează art. 331) este construit explicit doar pentru taxare inversă **internă**: verifică natura bunului/serviciului contra celor 12 categorii din art. 331 alin. (2), statutul de plătitor de TVA al ambelor părți și, unde e cazul, pragul valoric și termenul de expirare. Acest motor nu tratează achizițiile intracomunitare, importurile sau serviciile primite de la prestatori din UE — acestea au alt temei legal (art. 307) și sunt gestionate separat de operațiunile prevăzute la art. 331.

[iConta.eu](/)
