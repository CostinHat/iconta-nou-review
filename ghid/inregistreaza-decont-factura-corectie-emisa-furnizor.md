---
title: "Cum se înregistrează în decont factura de corecție emisă de furnizor după inspecția fiscală?"
description: "Furnizorul o trece separat în jurnalul de vânzări și în secțiunea dedicată din D300, fără să mai colecteze TVA; clientul deduce taxa pe rândurile de achiziții, în cel mult un an."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Cum se înregistrează în decont factura de corecție emisă de furnizor după inspecția fiscală?

La inspecția fiscală se constată că furnizorul nu a colectat TVA pentru o operațiune taxabilă. Organul fiscal stabilește taxa prin decizie, furnizorul o plătește și apoi emite factură de corecție către client, ca să recupereze suma. Această factură nu se tratează ca una obișnuită în decont.

Pe scurt: furnizorul o raportează separat și **nu mai colectează** TVA-ul, deja plătit pe decizie. Clientul **deduce** taxa în condițiile generale.

## Temeiul legal

::: ghid-temei
„Persoanele impozabile care au fost supuse unui control fiscal și au fost constatate și stabilite erori în ceea ce privește stabilirea corectă a taxei colectate, fiind obligate la plata acestor sume în baza actului administrativ emis de autoritatea fiscală competentă, pot emite facturi de corecție conform alin. (1) lit. b) către beneficiari. Pe facturile emise se va face mențiunea că sunt emise după control și vor fi înscrise într-o rubrică separată în decontul de taxă."
— Codul fiscal (Legea 227/2015), art. 330 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Prin excepție, în cazul în care furnizorul emite facturi de corecție, fie din inițiativă proprie, fie în urma inspecției fiscale în cadrul căreia organul fiscal a stabilit TVA colectată pentru anumite operațiuni efectuate în perioada supusă inspecției fiscale, beneficiarul respectivelor operațiuni are dreptul să deducă taxa înscrisă în factura de corecție emisă de furnizor chiar dacă termenul de prescripție a dreptului de a stabili obligații fiscale s-a împlinit. În aceste situații, dreptul de deducere poate fi exercitat în cel mult un an de la data primirii facturii de corecție, sub sancțiunea decăderii."
— Codul fiscal (Legea 227/2015), art. 301 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„Furnizorii/Prestatorii care emit facturi de corecție după inspecția fiscală, în conformitate cu prevederile art. 330 alin. (3) din Codul fiscal, înscriu aceste facturi în jurnalul pentru vânzări într-o rubrică separată, iar acestea se preiau de asemenea într-o rubrică separată din decontul de taxă, fără a avea obligația să colecteze taxa pe valoarea adăugată înscrisă în respectivele facturi."
— Normele metodologice ale Codului fiscal (HG 1/2016), titlul VII, pct. 108 alin. (4) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)

„Beneficiarii au dreptul de deducere a taxei pe valoarea adăugată înscrise în aceste facturi în limitele și în condițiile stabilite la art. 297-301 din Codul fiscal, taxa fiind înscrisă în rubricile din decontul de taxă aferente achizițiilor de bunuri și servicii."
— Normele metodologice ale Codului fiscal (HG 1/2016), titlul VII, pct. 108 alin. (4) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

**La furnizor:**

- Factura poartă mențiunea că este emisă după inspecția fiscală.
- Se trece în jurnalul de vânzări, într-o rubrică separată.
- În D300 nu intră pe rândurile de livrări, ci în secțiunea „Facturi emise după inspecția fiscală, conform art. 330 alin. (3) din Codul fiscal" (număr de facturi, total bază, total TVA), potrivit instrucțiunilor din OPANAF 174/2026. Taxa nu se colectează a doua oară.

**La client:** TVA-ul se deduce pe rândurile obișnuite de achiziții din D300, în cel mult un an de la primirea facturii, chiar dacă perioada operațiunii inițiale e prescrisă.

::: ghid-exemplu
La inspecția fiscală la SC Furnizor Exemplu SRL se constată că o prestare de 100.000 lei către SC Exemplu SRL a fost facturată greșit fără TVA. Organul fiscal stabilește TVA colectată de 21.000 lei, pe care furnizorul o plătește pe baza deciziei. Furnizorul emite factura de corecție (100.000 lei bază, 21.000 lei TVA) și o raportează în secțiunea dedicată din D300, fără să colecteze din nou taxa. SC Exemplu SRL plătește cei 21.000 lei și îi deduce în cel mult un an de la primire.
:::

## Ce se greșește în practică

- Furnizorul trece factura pe rândurile de livrări taxabile și plătește TVA-ul de două ori: o dată pe decizie și încă o dată prin decont.
- Factura nu are mențiunea că este emisă după control, iar legătura cu decizia se pierde.
- Clientul amână deducerea și depășește termenul de un an de la primire, iar dreptul de deducere se pierde.
- Clientul trece factura în secțiunea „Facturi primite după inspecția fiscală". Aceea privește altă situație (pct. 108 alin. (6)): beneficiarul căruia inspecția i-a respins deducerea pentru operațiuni scutite sau din afara sferei TVA.

## Ce face iConta.eu

iConta.eu generează decontul D300 din facturile perioadei și permite adăugarea manuală a rândurilor care nu rezultă automat din facturi. Secțiunea informativă „Facturi emise după inspecția fiscală" nu se completează în prezent automat în XML-ul generat de aplicație, așa că datele ei se verifică și se completează de contabil. La client, factura de corecție primită se înregistrează ca achiziție, iar TVA-ul deductibil intră pe rândurile de achiziții.

[iConta.eu](/)
