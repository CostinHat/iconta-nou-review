---
title: De ce apare diferență între impozitul micro din contabilitate și D100?
description: O diferență între suma din evidența contabilă și suma din D100 apare de regulă din venituri înregistrate în perioada greșită, deduceri omise (contul 709) sau rulaje cumulate confundate cu rulaje trimestriale.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# De ce apare diferență între impozitul micro din contabilitate și D100?

Când suma pe care ați estimat-o „din contabilitate" nu se potrivește cu ce generează D100, cauza e aproape întotdeauna în modul în care au fost citite sau înregistrate veniturile trimestrului, nu o eroare a formulei de calcul.

## Temeiul legal

::: ghid-temei
**CF art. 53 alin. (1):**
> „Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie **veniturile din orice
> sursă**, din care se scad: a) veniturile aferente costurilor stocurilor de produse; b) veniturile
> aferente costurilor serviciilor în curs de execuție; ... j) valoarea reducerilor comerciale acordate
> ulterior facturării, înregistrate în contul «709»..."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt:6480-6519`

**CF art. 51 alin. (1):**
> „Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.html`
:::

## De unde vin, de fapt, diferențele

Formula legală e simplă (venituri trimestru × 1%), deci o diferență între suma calculată manual și suma din D100 aproape întotdeauna vine dintr-o diferență de bază, nu de cotă. Cele mai comune surse:

- **Perioadă greșită** — o factură înregistrată cu întârziere (de exemplu, o factură din martie contabilizată abia în aprilie) mută venitul într-un alt trimestru decât cel în care ar fi trebuit raportat.
- **Deducerea omisă a contului 709** — reducerile comerciale acordate ulterior facturării trebuie scăzute din baza impozabilă; dacă evidența „manuală" nu le scade, suma rezultă mai mare decât cea corectă din D100.
- **Rulaj cumulat vs. rulaj trimestrial** — o estimare făcută pe soldul cumulat de la începutul anului, în loc de rulajul strict al trimestrului, produce o diferență semnificativă, mai ales spre finalul anului.
- **Stornări/note contabile ulterioare** — o corecție contabilă făcută după generarea unei estimări manuale, dar înainte de generarea efectivă a D100, schimbă baza fără ca estimarea inițială să fie actualizată.

## Ce se greșește în practică

- Se compară suma din D100 cu o sumă calculată manual pe bază de rulaj cumulat, nu trimestrial.
- Se ignoră deducerile din art. 53 alin. (1) în calculul manual de control.
- Se generează D100 înainte ca toate notele contabile ale trimestrului să fie finalizate (facturi întârziate, corecții).
- Se presupune că orice diferență e o eroare a aplicației, fără a verifica întâi datele sursă din contabilitate.

## Ce face iConta.eu

Pentru fiecare declarație D100, `d100_reconciliere.verifica_reconciliere` recalculează suma pe o cale complet independentă — direct din SQL, pe tabela `inregistrari_linii` — și o confruntă cu suma produsă de generator (`deriva_obligatii`). Această reconciliere este o poartă obligatorie înainte de emiterea XML-ului: dacă cele două căi de calcul nu coincid, discrepanța e semnalată înainte ca declarația să poată fi depusă. Dacă totuși suma din D100 diferă de o estimare manuală, cauza e aproape sigur în datele contabile sursă (perioadă, deduceri, note ulterioare), nu în motorul de calcul.

[iConta.eu](/)
