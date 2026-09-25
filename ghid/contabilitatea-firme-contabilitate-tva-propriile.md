---
title: "Contabilitatea unei firme de contabilitate: TVA la propriile servicii"
description: "Regulile TVA nu au un regim special pentru firmele de contabilitate — un cabinet care își facturează propriile servicii aplică exact aceleași reguli de fapt generator și cotă ca orice alt prestator."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Contabilitatea unei firme de contabilitate: TVA la propriile servicii

Un cabinet de contabilitate nu are, din perspectiva TVA, un regim diferit față de orice altă firmă care prestează servicii cu plată. „Propriile servicii" ale unui cabinet — onorariile de contabilitate facturate clienților — se supun acelorași reguli de fapt generator, exigibilitate și cotă ca serviciile de consultanță, expertiză sau alte servicii similare cu decontări succesive.

## Temeiul legal

::: ghid-temei
„(7) Prestările de servicii care determină decontări sau plăți succesive, cum sunt serviciile de construcții-montaj, consultanță, cercetare, expertiză și alte servicii similare, sunt considerate efectuate la data la care sunt emise situații de lucrări, rapoarte de lucru, alte documente similare pe baza cărora se stabilesc serviciile efectuate sau, după caz, în funcție de prevederile contractuale, la data acceptării acestora de către beneficiari."
— Codul fiscal (Legea 227/2015), art. 281 alin. (7) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Serviciile de contabilitate, facturate lunar sau periodic pe bază de contract, se încadrează la „servicii similare" celor de consultanță — faptul generator intervine la data documentului pe baza căruia se stabilesc serviciile prestate (de regulă, factura sau raportul de activitate), nu la o dată fixă din contract, dacă nu există o asemenea clauză.
- Exigibilitatea taxei urmează faptul generator (art. 282 alin. (1) Cod fiscal), cu excepțiile generale (facturare anticipată, avansuri) aplicabile oricărui prestator.
- Cota aplicabilă e cea standard: „Cota standard se aplică asupra bazei de impozitare pentru operațiunile impozabile care nu sunt scutite de taxă sau care nu sunt supuse cotei reduse, iar nivelul acesteia este 21%" (art. 291 alin. (1) Cod fiscal) — serviciile de contabilitate nu se regăsesc pe lista operațiunilor scutite sau cu cotă redusă.
- Operațiunea e impozabilă în condițiile generale de la art. 268 Cod fiscal: livrare/prestare cu plată, cu locul în România, efectuată de o persoană impozabilă ce acționează ca atare, în cadrul unei activități economice — exact situația unui cabinet care își facturează serviciile către clienți.

## Ce se greșește în practică

- Se caută un regim special „pentru cabinete de contabilitate" care de fapt nu există în Codul fiscal — TVA la propriile servicii ale unui cabinet nu diferă de TVA la serviciile oricărei alte firme de consultanță sau prestări servicii.
- Se stabilește greșit faptul generator la data semnării contractului sau la o dată fixă de sfârșit de lună, ignorând regula specifică pentru servicii cu decontări succesive (art. 281 alin. (7)): faptul generator e legat de documentul care stabilește serviciile prestate, nu de o dată calendaristică arbitrară.
- Se confundă TVA pe onorariile facturate clienților cu eventuale situații de autoconsum de servicii (folosirea propriilor resurse ale cabinetului în beneficiul propriu) — sunt operațiuni diferite, cu tratament diferit, iar simpla facturare a unui serviciu de contabilitate către un client nu implică niciodată autoconsum.

## Ce face iConta.eu

Verificat direct în cod: nu există în iConta.eu nicio funcționalitate specifică pentru „TVA la propriile servicii ale unui cabinet de contabilitate" — subiectul nu apare nici în lista de funcționalități a aplicației, nici în motorul de control încrucișat **F169** (`core/control_incrucisat.py`), care compară D300 cu rulajele contabile pe conturile de TVA (4426/4427/4423/4424/4428) generic, pentru orice firmă, fără nicio ramură dedicată cabinetelor de contabilitate sau facturării serviciilor proprii. Un cabinet care își emite facturi de onorariu către clienți folosește, ca orice altă firmă prestatoare de servicii, modulul general de facturare al aplicației — cota, faptul generator și exigibilitatea se calculează după regulile standard descrise mai sus, nu printr-un mecanism separat.

[iConta.eu](/)
