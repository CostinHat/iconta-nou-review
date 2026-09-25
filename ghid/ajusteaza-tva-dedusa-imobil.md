---
title: "Cum se ajustează TVA dedusă pentru un imobil?"
description: "Perioada de ajustare de 20 de ani pentru TVA dedusă la achiziția sau construcția unui imobil, conform Codului fiscal — regula bunurilor de capital."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se ajustează TVA dedusă pentru un imobil?

Un imobil nu e un stoc oarecare din perspectiva TVA — legea îl tratează ca „bun de capital", cu o perioadă de ajustare mult mai lungă decât la orice altă achiziție. O schimbare de destinație a imobilului (de la activitate taxabilă la scutită, sau invers) ani de zile după achiziție poate declanșa o ajustare a taxei deja deduse.

## Temeiul legal

::: ghid-temei
„Articolul 305 Ajustarea taxei deductibile în cazul bunurilor de capital
[...]
(2) Taxa deductibilă aferentă bunurilor de capital [...] se ajustează [...]: a) pe o perioadă de 5 ani, pentru bunurile de capital achiziționate sau fabricate, altele decât cele prevăzute la lit. b); b) pe o perioadă de 20 de ani, pentru construcția sau achiziția unui bun imobil, precum și pentru transformarea sau modernizarea unui bun imobil, dacă valoarea fiecărei transformări sau modernizări este de cel puțin 20% din valoarea totală a bunului imobil/părții de bun imobil după transformare sau modernizare."
— Codul fiscal (Legea 227/2015), art. 305 alin. (2) lit. a) și b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din text:

- **Pentru imobile, perioada de ajustare e de 20 de ani** — semnificativ mai lungă decât perioada standard de 5 ani, aplicabilă altor bunuri de capital (utilaje, echipamente).
- Perioada de 20 de ani se aplică nu doar la achiziția/construcția inițială, ci și la **transformări sau modernizări** ulterioare ale imobilului, dacă valoarea lucrării atinge cel puțin 20% din valoarea totală a imobilului după transformare.
- Ajustarea se calculează pentru o cincime sau o douăzecime din taxa dedusă inițial, **pentru fiecare an în care apare o modificare a destinației de utilizare** — nu integral, dintr-o dată, ci proporțional cu anii rămași din perioada de ajustare.
- Cazurile care declanșează ajustarea includ: modificarea gradului de utilizare a imobilului în scopuri economice, trecerea de la regim de scutire la regim de taxare (sau invers), ori situații în care dreptul de deducere a fost inițial limitat și ulterior operațiunea devine deductibilă.
- **Excepție:** dacă imobilul e vândut în regim de scutire sau firma trece la regimul de scutire pentru întreprinderile mici, ajustarea se face o singură dată, pentru toată perioada de ajustare rămasă, nu eșalonat an de an.

## Ce se greșește în practică

- Se aplică perioada standard de 5 ani și pentru imobile, ignorând regula specifică de 20 de ani prevăzută explicit de lege pentru bunurile imobile.
- Se ajustează integral taxa dedusă la prima modificare de destinație, în loc de a calcula proporția aferentă anilor rămași din perioada de 20 de ani.
- Se omite ajustarea pentru transformări/modernizări ulterioare care depășesc pragul de 20% din valoarea imobilului, tratând doar achiziția inițială ca eveniment relevant.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un modul dedicat de calcul al ajustării TVA pe 5/20 de ani pentru bunuri de capital** (art. 305 din Codul fiscal) — modulul existent pentru ajustarea TVA (`core/perisabilitati.py`) acoperă un caz diferit, ajustarea TVA la perisabilități peste limita legală (art. 304 din Codul fiscal), nu ajustarea multianuală specifică bunurilor de capital. Calculul ajustării pe 20 de ani pentru un imobil rămâne, la data acestui ghid, o operațiune realizată manual de contabil.

[iConta.eu](/)
