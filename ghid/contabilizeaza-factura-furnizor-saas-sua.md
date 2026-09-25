---
title: "Cum se contabilizează factura unui furnizor SaaS din SUA?"
description: "De ce achiziția unui abonament software de la un furnizor american se taxează prin taxare inversă în România, și ce presupune asta pentru firma cumpărătoare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează factura unui furnizor SaaS din SUA?

Un abonament la un serviciu software (SaaS) cumpărat de la un furnizor stabilit în SUA este, din perspectiva TVA, o prestare de servicii B2B. Regula de bază spune că locul prestării — și, implicit, statul care are dreptul să colecteze TVA — este statul unde este stabilit beneficiarul, adică România, chiar dacă furnizorul e american și nu emite TVA pe factură.

## Temeiul legal

::: ghid-temei
„(2) Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. [...]"
— Codul fiscal (Legea 227/2015), art. 278 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„(2) Taxa este datorată de orice persoană impozabilă, inclusiv de către persoana juridică neimpozabilă înregistrată în scopuri de TVA conform art. 316 sau 317, care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României sau nu este considerată a fi stabilită pentru respectivele prestări de servicii pe teritoriul României [...]"
— Codul fiscal (Legea 227/2015), art. 307 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul aplicat unui abonament SaaS de la un furnizor din SUA:

- Locul prestării este România (locul unde firma cumpărătoare, beneficiarul, este stabilită) — art. 278 alin. (2).
- Pentru că furnizorul nu este stabilit în România, obligația de a plăti TVA se mută de la furnizor la beneficiar — mecanismul de **taxare inversă**, art. 307 alin. (2). Firma din România calculează ea însăși TVA aferentă (colectată **și** deductibilă simultan, dacă are drept integral de deducere), fără ca furnizorul american să fi emis TVA pe factură.
- Contabil, operațiunea presupune înregistrarea facturii la valoarea din factura furnizorului (convertită în lei la cursul BNR din data facturii), cu calculul și evidențierea separată a TVA prin autolichidare (4426 = 4427, cu aceeași sumă, pentru firmele cu drept integral de deducere).
- Firma trebuie să raporteze operațiunea corespunzător în decontul de TVA (D300), la rândurile dedicate achizițiilor de servicii intracomunitare/din afara UE cu taxare inversă.

## Ce se greșește în practică

- Se așteaptă ca furnizorul american să emită o factură cu TVA românească — furnizorii nestabiliți în UE, în general, nu facturează TVA românesc; obligația de a calcula taxa revine beneficiarului, prin taxare inversă.
- Se omite complet înregistrarea TVA prin autolichidare, tratând factura ca fiind „fără TVA" din perspectiva firmei cumpărătoare, deși obligația de calcul al taxei există indiferent de conduita furnizorului.
- Se confundă regimul aplicabil serviciilor B2B (beneficiarul plătește TVA prin taxare inversă) cu regimul aplicabil vânzărilor de bunuri la distanță din afara UE, care are reguli complet diferite (import, taxe vamale).

## Ce face iConta.eu

iConta.eu determină locul prestării serviciilor conform art. 278 alin. (2) și marchează achizițiile de servicii de la furnizori nestabiliți în România (inclusiv din afara UE) pentru aplicarea taxării inverse, generând automat nota contabilă de autolichidare (colectare și deducere simultană a TVA) pe baza cotei standard aplicabile. Contabilul introduce factura furnizorului SaaS ca achiziție de servicii externe și confirmă încadrarea, iar aplicația calculează TVA prin autolichidare și o reflectă corespunzător în decontul de TVA.

[iConta.eu](/)
