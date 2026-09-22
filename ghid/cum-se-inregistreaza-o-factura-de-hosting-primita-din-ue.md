---
title: Cum se înregistrează o factură de hosting primită din UE?
description: O factură de hosting de la un furnizor stabilit în UE se declară, pentru firma română neplătitoare de TVA, în Secțiunea 4.1 a D301, prin taxare inversă conform art. 307 alin. (2); dacă lipsește factura, se emite autofactură.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se înregistrează o factură de hosting primită din UE?

Serviciile de hosting sunt adesea furnizate din alte state membre UE. Pentru o firmă română neplătitoare de TVA, primirea unei astfel de facturi nu este doar o operațiune contabilă obișnuită — ea declanșează obligația de taxare inversă și de declarare în D301, indiferent de valoarea facturii.

## Temeiul legal

::: ghid-temei
**Articolul 307 alin. (2)**: Taxa este datorată de orice persoană impozabilă [...] care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României [...]

**Articolul 290 alin. (2)**: Dacă elementele folosite pentru stabilirea bazei de impozitare a unei operațiuni, alta decât importul de bunuri, se exprimă în valută, cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României sau ultimul curs de schimb publicat de Banca Centrală Europeană ori cursul de schimb utilizat de banca prin care se efectuează decontările, **valabil la data la care intervine exigibilitatea taxei** pentru operațiunea în cauză [...]

**Articolul 320 alin. (1)**: Persoana impozabilă sau persoana juridică neimpozabilă, obligată la plata taxei în condițiile prevăzute la art. 307 alin. (2)-(4) și (6) [...], trebuie să autofactureze operațiunile respective până cel mai târziu în a 15-a zi a lunii următoare celei în care ia naștere faptul generator al taxei, în cazul în care persoana respectivă nu se află în posesia facturii emise de furnizor/prestator.
:::

## Pașii de urmat la primirea facturii de hosting

Odată primită factura de la furnizorul de hosting (stabilit în UE), firma română — beneficiar al serviciului — trebuie să determine baza de impozitare în lei, folosind cursul de schimb (BNR, BCE sau cursul băncii prin care se fac decontările) valabil la data exigibilității taxei, nu la data facturii, dacă cele două diferă. Pe baza acestei sume, se calculează TVA la cota validă pentru perioadă și se introduce operațiunea în Secțiunea 4.1 a D301, ca achiziție de serviciu intracomunitar cu taxare inversă.

Dacă factura de la furnizor nu ajunge la timp, legea nu permite amânarea nelimitată a declarării: firma este obligată să emită o autofactură până cel mai târziu în a 15-a zi a lunii următoare celei în care a luat naștere faptul generator al taxei (de regulă, luna în care serviciul a fost efectiv prestat).

::: ghid-exemplu
Factură hosting de 25 EUR, curs BNR la data exigibilității 4,9700 lei/EUR.

Baza = 25 × 4,9700 = 124,25 lei
TVA (21%, cotă standard din 01.08.2025) = 124,25 × 21% = 26,09 lei

Aceste sume se raportează în Secțiunea 4.1 din D301, pentru luna exigibilității.
:::

## Ce se greșește în practică

- Factura este introdusă în contabilitate fără a fi sesizată obligația de taxare inversă și de declarare în D301.
- Se folosește cursul valutar de la data facturii sau a plății, în loc de cursul valabil la data exigibilității taxei.
- Se așteaptă la nesfârșit primirea facturii de la furnizor, fără a emite autofactura obligatorie până în a 15-a zi a lunii următoare faptului generator.
- Se presupune, greșit, că există un plafon valoric sub care serviciul de hosting nu trebuie declarat — la servicii intracomunitare taxarea inversă se aplică de la prima factură.

## Ce face iConta.eu

Baza de impozitare se calculează automat de aplicație (`baza = round(val_valuta × curs, 0)`), cu rotunjire aritmetică (`ROUND_HALF_UP`), iar generarea declarației este refuzată explicit dacă lipsește cursul valutar sau acesta este introdus ca zero sau negativ — cursul valabil la data exigibilității trebuie introdus manual de contabil, aplicația nu are o integrare automată cu cursul BNR sau BCE.

Pentru operațiunile de tip servicii intracomunitare (Secțiunea 4.1), aplicația validează tipul, valuta (dintr-un nomenclator dedicat), valoarea în valută, cursul și cota aplicabilă perioadei, și face rollup-ul cerut de instrucțiunile OPANAF 592/2016 în totalul Secțiunii 4. Aplicația nu emite automat autofactura prevăzută de art. 320 și nu validează țara furnizorului împotriva unei liste de state membre UE — aceste verificări rămân responsabilitatea contabilului.

[iConta.eu](/)
