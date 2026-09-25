---
title: "Comisionul plătit marketplace-ului: TVA și deductibilitate"
description: "Regulile generale din Codul fiscal privind deductibilitatea cheltuielilor efectuate în scopul activității economice și dreptul de deducere a TVA, aplicate comisionului de marketplace."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Comisionul plătit marketplace-ului: TVA și deductibilitate

Nu există, în sursele verificate, o prevedere specifică pentru „comisionul de marketplace" ca atare — tratamentul lui fiscal se stabilește prin regulile generale de deductibilitate a cheltuielilor și de deducere a TVA, aplicate acestei categorii de serviciu (comision de intermediere pentru vânzarea de bunuri/servicii pe o platformă online).

## Temeiul legal

::: ghid-temei
„Articolul 25 Cheltuieli
(1) Pentru determinarea rezultatului fiscal sunt considerate cheltuieli deductibile cheltuielile efectuate în scopul desfășurării activității economice, inclusiv cele reglementate prin acte normative în vigoare, precum și taxele de înscriere, cotizațiile și contribuțiile datorate către camerele de comerț și industrie, organizațiile patronale și organizațiile sindicale.
[...]
Articolul 297 Sfera de aplicare a dreptului de deducere
(1) Dreptul de deducere ia naștere la momentul exigibilității taxei."
— Legea nr. 227/2015 (Codul fiscal), art. 25 alin. (1) și art. 297 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din aceste reguli generale pentru comisionul de marketplace:

- Comisionul reținut de o platformă de tip marketplace pentru serviciile de intermediere este, prin natura lui, o cheltuială efectuată **în scopul desfășurării activității economice** (vânzarea produselor/serviciilor firmei prin acel canal) — deci se încadrează în principiu la art. 25 alin. (1), sub rezerva documentării corecte (factură/document justificativ de la platformă).
- TVA-ul aferent comisionului, dacă platforma facturează cu TVA (sau dacă se aplică taxare inversă, în funcție de statutul furnizorului), urmează regula generală de deducere de la art. 297 — dreptul de deducere ia naștere la exigibilitatea taxei, condiționat de deținerea unei facturi valabile.
- Codul fiscal are o prevedere specifică doar pentru comisionul reținut de platformele care facilitează **închirierea pe termen scurt a camerelor**, care nu se cuprinde în venitul brut al beneficiarului — regulă distinctă, care nu se extinde automat la comisioanele de marketplace pentru vânzarea de produse.

## Ce se greșește în practică

- Se dedu TVA-ul de pe comisionul de marketplace fără verificarea statutului furnizorului (platformă cu sediul în România vs. în alt stat UE/non-UE), ceea ce poate schimba regimul aplicabil (taxare directă vs. taxare inversă/reverse charge).
- Se înregistrează comisionul „net", direct scăzut din încasare, fără o factură/document justificativ separat, ceea ce face imposibilă demonstrarea deductibilității la un control.
- Se presupune că regula specifică pentru comisionul platformelor de cazare pe termen scurt (neinclus în venitul brut) se aplică prin analogie oricărui comision de marketplace — este o prevedere distinctă, limitată la acel tip de serviciu.

## Ce face iConta.eu

Nu am găsit în `core/` (grep pe „marketplace") un modul specific pentru tratamentul comisioanelor plătite platformelor de tip marketplace — comisioanele se înregistrează, la acest moment, ca orice altă cheltuială de intermediere/comision, folosind fluxurile generale de facturi primite și deduceri TVA din aplicație, fără o regulă automată dedicată acestui tip de serviciu.

[iConta.eu](/)
