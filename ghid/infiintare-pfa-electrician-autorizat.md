---
title: "Înființare PFA pentru un electrician autorizat"
description: "Procedura de înființare la registrul comerțului ține de OUG 44/2008, un act care nu se regăsește în sursele fiscale ale acestui ghid — dar Codul fiscal stabilește deja regimul fiscal pe care activitatea de electrician îl are, ca activitate independentă, o dată PFA-ul înființat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Înființare PFA pentru un electrician autorizat

Pașii concreți de înființare a unui PFA — dosarul depus la oficiul registrului comerțului, codurile CAEN eligibile, documentele care dovedesc calificarea de electrician autorizat (ANRE sau echivalent) — sunt reglementați de OUG nr. 44/2008 privind desfășurarea activităților economice de către persoanele fizice autorizate, întreprinderile individuale și întreprinderile familiale. Acest act nu se regăsește în sursele fiscale disponibile pentru acest ghid, deci nu putem descrie procedura de înregistrare fără să riscăm o invenție. Vă redirecționăm onest spre ce chiar putem documenta din Codul fiscal: regimul fiscal pe care activitatea unui electrician autorizat îl are **o dată PFA-ul înființat**.

## Temeiul legal

::: ghid-temei
„(1) Veniturile din activități independente cuprind veniturile din activități de producție, comerț, prestări de servicii și veniturile din profesii liberale, realizate în mod individual și/sau într-o formă de asociere, inclusiv din activități adiacente."
— Legea 227/2015 (Codul fiscal), art. 67 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„(1) Venitul net anual din activități independente se determină în sistem real, pe baza datelor din contabilitate, ca diferență între venitul brut și cheltuielile deductibile efectuate în scopul realizării de venituri, cu excepția situațiilor în care sunt aplicabile prevederile art. 68^1, 68^3 și 69."
— Legea 227/2015 (Codul fiscal), art. 68 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

O activitate de electrician autorizat (montaj, întreținere, reparații instalații electrice) se încadrează fiscal la categoria „prestări de servicii" din art. 67 alin. (1) — deci, ca PFA, generează venituri din activități independente:

- Venitul net anual se stabilește, ca regulă generală, **în sistem real** (venit brut minus cheltuieli deductibile), pe baza datelor din contabilitate — cu excepțiile de la art. 68^1 (norme de venit) și 68^3, unde legea prevede alt mod de determinare pentru anumite categorii de activități.
- Alegerea între sistemul real și normă de venit (acolo unde e permisă pentru activitatea desfășurată) e o decizie care se declară la ANAF, nu la registrul comerțului — deci separată de dosarul de înființare.
- Indiferent de sistemul ales, obligația de a ține evidența veniturilor rămâne (integrală în sistem real, doar pe partea de venituri la normă de venit) — vezi ghidul dedicat registrului de evidență fiscală.

## Ce se greșește în practică

- Se confundă înregistrarea la ONRC (act guvernat de OUG 44/2008) cu declararea la ANAF a regimului fiscal — sunt pași distincți, la instituții diferite, cu acte normative diferite.
- Se presupune că orice activitate PFA e automat impozitată la normă de venit — regula generală de la art. 68 alin. (1) este sistemul real; norma de venit se aplică doar unde legea o prevede explicit (art. 68^1) și, de regulă, pe bază de opțiune sau plafon.
- Se omite ținerea evidenței cheltuielilor deductibile (scule, materiale, deplasări legate de activitate) din primul an de activitate, sub motivul că „PFA-ul abia s-a înființat" — obligația de evidențiere curge de la începutul desfășurării activității, nu de la un termen ulterior.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu documentează și nu automatizează** procedura de înființare a PFA la registrul comerțului — aceasta ține de OUG 44/2008, în afara sursei de temeiuri fiscale a aplicației. Ce e deja acoperit, o dată PFA-ul înființat și activ fiscal: **Registrul de evidență fiscală pentru persoane fizice** (varianta „venituri_pf" din `core/registru_evidenta_fiscala.py`, cu temei la CF art. 68 alin. (8)-(9) și OMFP 3254/2017), pentru evidența anuală a venitului brut și a cheltuielilor deductibile pe sursă de venit, și generarea manuală a declarației D212 (`core/d212.py`), pe baza datelor furnizate de contabil.

[iConta.eu](/)
