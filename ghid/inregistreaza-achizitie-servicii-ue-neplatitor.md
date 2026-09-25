---
title: "Cum se înregistrează o achiziție de servicii UE la un neplătitor de TVA?"
description: "Taxare inversă cu TVA nedeductibilă în costul achiziției — mecanismul specific pentru firmele neplătitoare de TVA care cumpără servicii de la un prestator din alt stat membru UE."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează o achiziție de servicii UE la un neplătitor de TVA?

O firmă neplătitoare de TVA (înregistrată doar special, conform art. 317, pentru achiziții intracomunitare/servicii) care cumpără un serviciu de la un prestator din alt stat membru UE datorează totuși TVA la stat, prin taxare inversă — dar, spre deosebire de un plătitor de TVA, nu o poate deduce. Taxa rămâne, pentru ea, un cost.

## Temeiul legal

::: ghid-temei
„Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice."
— Codul fiscal (Legea 227/2015), art. 278 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din regula locului prestării, combinată cu regimul deducerii (art. 297):

- Pentru un serviciu B2B primit de la un prestator din alt stat membru, locul prestării e **România** (locul beneficiarului) — deci taxa se datorează în România, prin mecanismul de taxare inversă, indiferent dacă beneficiarul e plătitor de TVA sau nu.
- Un **plătitor de TVA** (înregistrat conform art. 316) înregistrează taxa inversă simultan ca taxă colectată și taxă deductibilă (4426 = 4427) — operațiunea e neutră, cu impact zero asupra TVA de plată.
- Un **neplătitor** (înregistrat doar conform art. 317, special pentru achiziții intracomunitare/servicii, fără drept general de deducere) datorează aceeași taxă, dar **nu o poate deduce** — deducerea cere înregistrarea conform art. 316 și îndeplinirea condițiilor de la art. 297. Taxa devine, pentru el, un cost efectiv, care intră în valoarea achiziției (contul principal), cu taxa de plată către stat evidențiată separat (cont 446).

## Ce se greșește în practică

- Se înregistrează achiziția ca taxă inversă neutră (4426 = 4427), copiind tratamentul unui plătitor de TVA — un neplătitor nu are cont de TVA deductibilă de folosit în acest fel.
- Se omite complet declararea taxei (prin D301, aplicabil neplătitorilor înregistrați conform art. 317), presupunând că „neplătitor" înseamnă „fără nicio obligație de TVA" pentru achiziții din UE.
- Se confundă regimul serviciilor B2B (locul prestării = beneficiarul, art. 278 alin. (2)) cu cel al bunurilor — condițiile de înregistrare și declarare diferă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu tratează diferit cele două situații direct în cod: modulul `core/intracomunitar.py` (funcția `note_taxare_inversa`) generează nota contabilă corectă în funcție de statutul beneficiarului — pentru un plătitor de TVA, taxare inversă neutră (4426 = 4427, deductibilă conform art. 297), iar pentru un neplătitor înregistrat conform art. 317, taxa nedeductibilă intră în costul achiziției, cu suma de plată către stat pe contul 446. Aplicația verifică și validitatea codului de TVA al partenerului direct în VIES (funcția `verifica_vies`), pentru a confirma că e vorba de o achiziție intracomunitară reală.

[iConta.eu](/)
