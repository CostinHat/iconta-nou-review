---
title: "Cum se marchează taxarea inversă în fișierul e-Factura"
description: Legea cere mențiunea „taxare inversă” pe factură și fără TVA colectată de furnizor; codificarea exactă în structura fișierului XML RO e-Factura nu e acoperită de sursele verificate pentru acest ghid.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se marchează taxarea inversă în fișierul e-Factura

Regula de fond, valabilă indiferent de formatul facturii, e clară: pentru operațiunile de la art. 331 CF, furnizorul nu înscrie TVA colectată, ci mențiunea „taxare inversă". Ce nu poate confirma acest ghid, pe baza surselor verificate, e exact în ce câmp al fișierului XML transmis prin sistemul RO e-Factura se codifică tehnic această mențiune.

## Temeiul legal

::: ghid-temei
„Pe facturile emise pentru livrările de bunuri/prestările de servicii prevăzute la alin. (2) furnizorii/prestatorii nu vor înscrie taxa colectată aferentă."
— Legea 227/2015, art. 331 alin. (3)
:::

::: ghid-temei
„Furnizorul/Prestatorul are obligația să înscrie pe factură mențiunea „taxare inversă"."
— HG 1/2016, pct. 109 alin. (1)
:::

Ce e verificat și confirmat, din sursele disponibile pentru acest ghid:
- obligația legală a mențiunii pe factură, în sarcina furnizorului (norme pct. 109 alin. (1));
- consecința gravă a lipsei ei — pierderea dreptului de deducere la beneficiar, dacă factura a fost greșit întocmită cu TVA (norme pct. 109 alin. (4));
- modul în care flagul de taxare inversă asociat facturii alimentează automat declarațiile D300 (rândurile dedicate) și D394 (tipurile „C"/„V").

Ce **nu** e acoperit de sursele verificate: structura exactă a schemei XML RO e-Factura — câmpul sau codul de scutire/simplificare specific prin care se marchează tehnic o factură ca fiind cu taxare inversă în fișierul transmis. Pentru acest detaliu tehnic, verifică documentația oficială RO e-Factura (schema UBL/CIUS-RO) sau ghidul tehnic al sistemului tău de facturare — nu presupune un cod anume doar din regula de fond citată mai sus.

## Ce se greșește în practică

- Se presupune că marcarea corectă a facturii pe hârtie/PDF e suficientă și că fișierul XML transmis prin RO e-Factura reflectă automat același lucru, fără verificare.
- Se confundă mențiunea legală obligatorie („taxare inversă") cu un simplu comentariu opțional pe factură.
- Se ignoră condițiile de fond (categorie validă din art. 331 alin. (2), ambele părți plătitoare de TVA, termen și prag) înainte de a marca factura, tratând marcarea ca pe o simplă bifă tehnică.

## Ce face iConta.eu

Odată ce o operațiune e marcată în aplicație cu flagul de taxare inversă, iConta.eu o reflectă automat în notele contabile (`4426=4427` la beneficiar) și în rândurile aferente din D300 și D394, cu o gardă care respinge introducerea manuală suplimentară a aceleiași sume (evitarea dublei numărări). Codificarea exactă a acestui flag în structura fișierului XML transmis prin RO e-Factura nu a fost verificată la nivel de câmp/schemă pentru acest ghid — dacă primești o eroare de validare la transmiterea facturii, verific-o direct în raport cu specificația tehnică RO e-Factura.

[iConta.eu](/)
