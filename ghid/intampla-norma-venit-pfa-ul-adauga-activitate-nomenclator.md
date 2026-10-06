---
title: "Ce se întâmplă cu norma de venit dacă PFA-ul adaugă o activitate care nu este în nomenclator?"
description: "PFA-ul trece în sistem real pentru toate veniturile, de la data completării obiectului de activitate; venitul anual se compune din fracțiunea de normă plus venitul net din evidență."
published: 2026-09-29
modified: 2026-10-03
poarta: v1
---

# Ce se întâmplă cu norma de venit dacă PFA-ul adaugă o activitate care nu este în nomenclator?

PFA-ul pierde norma de venit pentru toată activitatea, nu doar pentru activitatea nouă. De la data completării obiectului de activitate, toate veniturile se impun în sistem real, pe baza evidenței contabile. Pentru anul schimbării, venitul net anual se compune din două părți: fracțiunea din normă pentru perioada de dinainte și venitul net din evidență pentru perioada de după.

## Temeiul legal

::: ghid-temei
„În cazul în care un contribuabil desfășoară o activitate inclusă în nomenclatorul prevăzut la alin. (2) și o altă activitate independentă, venitul net anual se determină în sistem real, pe baza datelor din contabilitate, potrivit prevederilor art. 68"
— Codul fiscal (Legea 227/2015), art. 69 alin. (7) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

::: ghid-temei
„(13) În aplicarea prevederilor art. 69 din Codul fiscal, contribuabilii care în cursul anului fiscal își completează obiectul de activitate cu o altă activitate care nu este cuprinsă în nomenclator vor fi impuși în sistem real, pentru veniturile realizate din întreaga activitate, de la data respectivă, venitul net anual urmând să fie determinat prin însumarea, de către contribuabili, a fracțiunii din norma de venit aferentă perioadei de impunere pe bază de normă de venit cu venitul net rezultat din evidența contabilă."
— HG 1/2016 (normele Codului fiscal), Titlul IV, pct. 8 alin. (13) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))
:::

Concret:

- **De la ce dată:** de la data la care PFA-ul își completează obiectul de activitate cu activitatea din afara nomenclatorului, nu de la 1 ianuarie a anului următor.
- **Pentru ce venituri:** pentru toate veniturile, inclusiv cele din activitatea care era pe normă.
- **Venitul net al anului:** fracțiunea de normă pentru perioada impusă pe normă, plus venitul net în sistem real, adică venituri încasate minus cheltuieli deductibile, pentru perioada rămasă.
- **Evidența:** de la acea dată, PFA-ul ține evidență contabilă în partidă simplă pentru toată activitatea.

::: ghid-exemplu
PFA Exemplu are în 2026 o activitate din nomenclator, cu o normă anuală de 50.000 lei. Pe 1 iulie 2026 adaugă o activitate care nu este în nomenclator.

- Perioada pe normă: 1 ianuarie–30 iunie, adică 181 de zile.
- Fracțiunea de normă: 50.000 × 181 / 365 = 24.795 lei, rotunjit.
- Sistem real, 1 iulie–31 decembrie: venituri de 60.000 lei minus cheltuieli deductibile de 25.000 lei = 35.000 lei.
- Venitul net anual: 24.795 + 35.000 = 59.795 lei.
- Impozit pe venit: 59.795 × 10% = 5.980 lei, rotunjit.

Împărțirea pe zile urmează modul de recalculare din alin. (10) al aceluiași punct. Contabilul poate folosi alt criteriu de proporționalitate, dacă e justificat.
:::

## Ce se greșește în practică

- Norma se păstrează pentru activitatea veche și doar activitatea nouă trece în sistem real. Legea mută în sistem real întreaga activitate.
- Trecerea se amână la 1 ianuarie a anului următor. Norma o leagă de data completării obiectului de activitate.
- Se uită fracțiunea de normă pentru prima parte a anului și se declară doar venitul din sistem real.
- Registrul de încasări și plăți nu se deschide de la data schimbării, iar cheltuielile din a doua parte a anului rămân nejustificate.

## Ce face iConta.eu

Pentru partea în sistem real, iConta.eu are Registrul de încasări și plăți în partidă simplă, cu operațiunile pe lună și categoria de deductibilitate. Pe baza lui, motorul D212 calculează venitul net, CAS și CASS. Pentru perioada anterioară, pe normă, contabilul adaugă activitatea în lista „Venit pe normă de venit” a Declarației unice, cu data încetării; declarația calculează fracțiunea de normă proporțional cu zilele de activitate și o cumulează cu venitul net din registru.

[iConta.eu](/)
