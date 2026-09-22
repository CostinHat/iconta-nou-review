---
title: Se aplică taxare inversă la abonamentele software cumpărate din UE?
description: Nu prin mecanismul art. 331 — un abonament software de la un furnizor stabilit în alt stat UE intră sub autolichidarea TVA de la art. 307 alin. (2) Cod fiscal, ca serviciu cu locul prestării în România.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Se aplică taxare inversă la abonamentele software cumpărate din UE?

Un abonament la un serviciu software (SaaS) facturat de un furnizor stabilit în alt stat membru UE — de exemplu un instrument de management de proiect sau o platformă de marketing — nu se încadrează în niciuna dintre cele 12 categorii de bunuri/servicii de la art. 331 alin. (2) Cod fiscal și, oricum, nu ar putea fi tratat prin acel articol, pentru că art. 331 se aplică exclusiv operațiunilor "în interiorul țării". Ceea ce se întâmplă efectiv, din punct de vedere fiscal, e autolichidarea TVA prevăzută la art. 307 alin. (2).

## Temeiul legal

::: ghid-temei
**Articolul 307 — Persoana obligată la plata taxei pentru operațiunile taxabile din România**

**(1)** Persoana obligată la plata taxei pe valoarea adăugată, dacă aceasta este datorată în conformitate cu prevederile prezentului titlu, este persoana impozabilă care efectuează livrări de bunuri sau prestări de servicii, cu excepția cazurilor pentru care beneficiarul este obligat la plata taxei conform alin. (2)-(6) și art. 331.

**(2)** Taxa este datorată de orice persoană impozabilă [...] care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României [...]

**Articolul 331 alin. (5):** Prevederile prezentului articol se aplică numai pentru livrările de bunuri/prestările de servicii în interiorul țării.
:::

## Cum funcționează, în practică

Un abonament software este un serviciu electronic. Când e cumpărat de o persoană impozabilă din România de la un furnizor stabilit în alt stat UE, locul prestării este, de regulă, în România, conform art. 278 alin. (2) Cod fiscal. Furnizorul din UE facturează fără TVA (menționând, tipic, "reverse charge" sau echivalentul din statul lui), iar beneficiarul din România are obligația să autolichideze TVA-ul aferent: îl înregistrează simultan ca taxă colectată și ca taxă deductibilă, similar mecanismului 4426 = 4427 folosit și la taxarea inversă internă, dar cu temei legal diferit (art. 307, nu art. 331).

## Ce se greșește în practică

- Se caută abonamentul software printre categoriile de bunuri de la art. 331 alin. (2) — nu are ce căuta acolo, pentru că nu e o categorie de bunuri fizice, ci un serviciu transfrontalier.
- Se așteaptă ca furnizorul din UE să înscrie TVA românesc pe factură, în loc ca beneficiarul să autolichideze taxa.
- Se omite complet înregistrarea TVA (nici colectată, nici deductibilă), tratând factura ca și cum ar fi scutită de TVA.
- Se verifică greșit pragul de 22.500 lei de la art. 331 alin. (7) — acesta nu are legătură cu serviciile din UE.
- Se confundă mențiunea de pe factura furnizorului (adesea "reverse charge" în engleză) cu taxarea inversă internă românească, deși e o operațiune diferită.

## Ce face iConta.eu

Motorul de taxare inversă al iConta.eu care implementează art. 331 este explicit limitat la operațiuni **interne**: verifică bunul/serviciul contra celor 12 categorii din art. 331 alin. (2) și statutul de plătitor TVA al ambelor părți stabilite în România. El nu tratează serviciile primite de la prestatori din UE — acestea au alt temei legal (art. 307) și ies din domeniul acestui motor prin construcție, nu prin omisiune.

[iConta.eu](/)
