---
title: "TVA trimestrial și impozit pe profit: obligații în 2026"
description: "Perioada fiscală trimestrială de TVA (plafon 100.000 euro, art. 322) e independentă de sistemul de declarare a impozitului pe profit — cele două se verifică separat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# TVA trimestrial și impozit pe profit: obligații în 2026

Faptul că o firmă depune deconturi de TVA trimestrial nu spune nimic despre cum își declară impozitul pe profit — sunt două obligații reglementate în titluri diferite ale Codului fiscal, cu plafoane și reguli complet independente.

## Temeiul legal

::: ghid-temei
„Perioada fiscală este luna calendaristică. Prin excepție [...], perioada fiscală este trimestrul calendaristic pentru persoana impozabilă care în cursul anului calendaristic precedent a realizat o cifră de afaceri din operațiuni taxabile [...] care nu a depășit plafonul de 100.000 euro al cărui echivalent în lei se calculează conform normelor metodologice, cu excepția situației în care persoana impozabilă a efectuat în cursul anului calendaristic precedent una sau mai multe achiziții intracomunitare de bunuri."
— Legea 227/2015, art. 322 alin. (1)-(2), Titlul VII (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Calculul, declararea și plata impozitului pe profit [...] se efectuează trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III. [...] Contribuabilii [...] pot opta pentru calculul, declararea și plata impozitului pe profit anual, cu plăți anticipate, efectuate trimestrial."
— Legea 227/2015, art. 41 alin. (1)-(2), Titlul II (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cele două „trimestriale" nu se sincronizează automat:

- **Perioada fiscală de TVA** (art. 322) — trimestrul e regula implicită pentru firmele sub plafonul de 100.000 euro cifră de afaceri anuală din operațiuni taxabile/scutite cu drept de deducere, cu excepția celor care fac achiziții intracomunitare. Depășirea plafonului trece firma la perioadă fiscală lunară.
- **Sistemul de declarare a impozitului pe profit** (art. 41) — trimestrul e regula implicită pentru toți contribuabilii, cu excepția celor care optează expres pentru sistemul anual cu plăți anticipate (opțiune valabilă minimum 2 ani fiscali consecutivi) sau a celor care intră obligatoriu în categorii speciale (instituții de credit — anual; agricultură — anual, conform art. 41 alin. 5 lit. b).

O firmă poate fi, simultan, plătitoare de TVA lunar (dacă a depășit plafonul de 100.000 euro cifră de afaceri) și plătitoare de impozit pe profit trimestrial (regimul implicit), sau invers — plătitoare de TVA trimestrial și de impozit pe profit anual (dacă a optat pentru sistemul anual). Cele două calendare nu sunt legate legal.

## Ce se greșește în practică

- Se presupune că regimul de TVA (lunar/trimestrial) determină automat și regimul de declarare a impozitului pe profit — sunt verificări separate, cu plafoane și declarații distincte (decontul de TVA vs. formularul 100/declarația anuală de profit).
- Se calculează plafonul de TVA de 100.000 euro folosind toate veniturile firmei, deși legea îl leagă strict de „operațiuni taxabile și/sau scutite cu drept de deducere și/sau neimpozabile [...] care dau drept de deducere", o categorie mai restrânsă decât veniturile totale.
- Se ignoră excepția privind achizițiile intracomunitare, care obligă la perioadă fiscală lunară de TVA chiar dacă cifra de afaceri rămâne sub plafonul de 100.000 euro.

## Ce face iConta.eu

iConta.eu calculează impozitul pe profit cumulat de la începutul anului fiscal, conform art. 41 (motorul D100), și generează separat decontul de TVA (D300) pe baza operațiunilor înregistrate în perioada respectivă, lunar sau trimestrial, conform configurării fiscale a firmei. La data acestui ghid, aplicația nu are o funcție automată care să verifice depășirea plafonului de 100.000 euro pentru trecerea de la perioadă fiscală trimestrială la lunară de TVA — configurarea perioadei fiscale de TVA, ca și a sistemului de declarare a impozitului pe profit, rămâne o setare pe care contabilul o actualizează manual în profilul firmei, pe baza verificării plafoanelor legale.

[iConta.eu](/)
