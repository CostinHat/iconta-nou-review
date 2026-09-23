---
title: "Se aplică taxare inversă la comisioanele platformelor de livrare din UE?"
description: Comisionul unei platforme de livrare stabilite în alt stat membru e un serviciu primit de la un prestator nestabilit în România — regimul corect e autolichidarea de la art. 307 alin. (2), nu taxarea inversă internă de la art. 331.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Se aplică taxare inversă la comisioanele platformelor de livrare din UE?

Da, dar nu prin mecanismul de taxare inversă internă (art. 331 CF), care e limitat expres la operațiuni în interiorul României. Comisionul reținut de o platformă de livrare stabilită în alt stat membru e un serviciu primit de la un prestator nestabilit în România — regimul corect e cel de la art. 307 alin. (2), colocvial numit tot „taxare inversă" sau autolichidare.

## Temeiul legal

::: ghid-temei
„Taxa este datorată de orice persoană impozabilă [...] care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României."
— Legea 227/2015, art. 307 alin. (2)
:::

::: ghid-temei
„Prevederile prezentului articol [art. 331] se aplică numai pentru livrările de bunuri/prestările de servicii în interiorul țării."
— Legea 227/2015, art. 331 alin. (5)
:::

Mecanismul contabil rămâne același ca la taxarea inversă internă — norma îl extinde explicit la orice situație de autolichidare, nu doar la art. 331: „prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă" (HG 1/2016, pct. 109 alin. (1)). Practic, primești factura de comision fără TVA de la platformă, iar tu, ca beneficiar înregistrat în scopuri de TVA în România, calculezi și înregistrezi taxa aferentă: `4426 = 4427`.

**Notă**: sursele verificate pentru acest ghid confirmă temeiul legal (art. 307 alin. (2)) și formula contabilă generală de autolichidare, dar nu au examinat în detaliu, la nivel de cod, modulul aplicației dedicat operațiunilor cu prestatori din UE/non-UE (distinct de motorul de taxare inversă internă, care acoperă doar categoriile de la art. 331). Dacă ai nevoie de detalii tehnice suplimentare despre acest flux, verifică separat ecranul dedicat serviciilor primite din UE/non-UE.

## Ce se greșește în practică

- Se caută opțiunea „Taxare inversă internă" (art. 331) pentru comisioane de la platforme UE, deși acest mecanism e limitat legal la operațiuni interne.
- Se plătește TVA-ul reținut de platformă ca și cum ar fi corect, fără să se verifice dacă factura ar fi trebuit emisă fără TVA, cu autolichidare în sarcina beneficiarului din România.
- Se omite complet autolichidarea, considerând că, din moment ce platforma e din UE, operațiunea „nu are TVA în România" fără nicio altă obligație.

## Ce face iConta.eu

Categoriile motorului de „Taxare inversă internă" din iConta.eu (deșeuri, cereale, clădiri/terenuri și celelalte de la art. 331 alin. (2)) sunt construite pentru operațiuni interne și nu includ serviciile primite de la prestatori din UE/non-UE. Pentru comisioanele platformelor de livrare stabilite în alt stat membru, folosește fluxul dedicat serviciilor primite din UE/non-UE — acest modul nu a fost verificat linie cu linie pentru acest ghid, așa că recomandăm să confirmi direct în ecranul respectiv cum se generează nota de autolichidare înainte să te bazezi pe ea fără verificare.

[iConta.eu](/)
