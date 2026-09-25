---
title: "Cum înregistrez transferul banilor din PayPal în bancă?"
description: "De ce o sumă retrasă din PayPal, dar neapărută încă în extrasul de cont bancar, se înregistrează distinct, în contul de sume în curs de decontare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum înregistrez transferul banilor din PayPal în bancă?

Între momentul în care o firmă retrage bani din contul PayPal și momentul în care suma apare efectiv în extrasul băncii pot trece una-două zile lucrătoare. În acest interval, banii nu sunt „nicăieri" din punct de vedere contabil — există un cont dedicat exact acestei situații.

## Temeiul legal

::: ghid-temei
„(2) Sumele virate sau depuse la bănci ori prin mandat poștal, pe bază de documente prezentate entității și neapărute încă în extrasele de cont, se înregistrează distinct în contabilitate (contul 5125 «Sume în curs de decontare»)."
— OMFP nr. 1.802/2014 (Reglementările contabile privind situațiile financiare anuale individuale și consolidate), pct. 302 alin. (2) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat la un transfer din PayPal către contul bancar al firmei:

- În momentul retragerii din PayPal, pe baza documentului de confirmare a transferului emis de platformă, suma se înregistrează în contul **5125 „Sume în curs de decontare"**, nu direct în contul de disponibilități bancare (5121/5124) — pentru că suma nu a apărut încă în extrasul băncii.
- Abia când suma apare efectiv în extrasul de cont bancar, ea se transferă din 5125 în contul de disponibilități bancare corespunzător (5121 pentru lei, 5124 pentru valută), prin operațiunea de viramente interne.
- Dacă soldul din PayPal e ținut în valută (de exemplu euro sau dolari), operațiunile de încasare/plată se înregistrează la cursul de schimb BNR din ultima zi bancară anterioară operațiunii, iar la finalul fiecărei luni, soldul rămas neretras din PayPal se reevaluează la cursul BNR din ultima zi bancară a lunii, cu recunoașterea diferențelor de curs la venituri sau cheltuieli financiare.
- Contul PayPal însuși, atâta timp cât nu e retras, funcționează contabil similar unei disponibilități în valută/lei la o instituție de plată, distinctă de contul curent la bancă.

## Ce se greșește în practică

- Se înregistrează transferul direct în contul bancar la data retragerii din PayPal, ignorând intervalul de câteva zile în care suma e „în tranzit" și nu apare încă în extrasul băncii.
- Nu se recunosc diferențele de curs valutar pentru soldurile ținute în PayPal în valută, tratând conversia ca fiind identică la data retragerii și la data încasării în bancă.
- Se amestecă soldul PayPal cu numerarul din casierie sau cu alte disponibilități, în loc să fie urmărit distinct, ca element de trezorerie propriu.

## Ce face iConta.eu

La data acestui ghid, iConta.eu gestionează operațiunile bancare prin modulul `core/banca.py` și importul extraselor de cont prin `core/banca_parser.py`, dar **nu are un conector dedicat pentru PayPal** sau alte instituții de plată electronică. Înregistrarea sumelor aflate „în tranzit" între retragerea din PayPal și apariția lor în extrasul bancar — inclusiv folosirea contului 5125 și calculul eventualelor diferențe de curs — se face manual, prin notele contabile introduse de utilizator, pe baza documentelor de confirmare emise de platformă.

[iConta.eu](/)
