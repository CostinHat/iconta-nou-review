---
title: "O firmă plătitoare de impozit pe profit trebuie să depună SAF-T?"
description: "Categoriile de contribuabili obligate să depună fișierul standard de control fiscal (SAF-T, declarația D406) și datele de referință, potrivit OPANAF 1783/2021."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# O firmă plătitoare de impozit pe profit trebuie să depună SAF-T?

Obligația de depunere a SAF-T (Declarația informativă D406) nu depinde de tipul de impozit plătit de firmă — pe profit sau pe veniturile microîntreprinderii — ci de forma juridică și de categoria de contribuabil (mare, mijlociu, mic) în care e încadrată firma.

## Temeiul legal

::: ghid-temei
„3. Următoarele categorii de contribuabili au obligația de depunere a fișierului standard de control fiscal (SAF-T), prin intermediul Declarației informative D406: [...] c) societățile pe acțiuni (S.A.); [...] g) societățile cu răspundere limitată (S.R.L.); [...] 4. Următoarele categorii de contribuabili nu au obligația de depunere a fișierului standard de control fiscal (SAF-T): a) persoanele fizice autorizate (PFA); b) întreprinderile individuale (II); c) întreprinderile familiale (IF); [...]"
— OPANAF 1783/2021 (modificat prin OPANAF 407/2025), Anexa nr. 5, pct. 3 lit. c) și g), pct. 4 lit. a)-c) (sursă: anaf_surse/opanaf_407_2025_saft_d406.txt)
:::

Ceea ce contează de fapt pentru obligativitate:

- **Forma juridică**, nu tipul de impozit: SRL-urile și SA-urile sunt în categoria obligată la SAF-T, indiferent dacă plătesc impozit pe profit sau, la microîntreprindere, impozit pe veniturile microîntreprinderii — obligația nu e legată de tipul de impozit, ci de faptul că sunt persoane juridice obligate să organizeze contabilitatea în partidă dublă.
- **Data de referință** diferă pe categorii de contribuabili: marii contribuabili din 1 ianuarie 2022, contribuabilii mijlocii din 1 ianuarie 2023, iar contribuabilii mici (categoria în care intră majoritatea SRL-urilor) din **1 ianuarie 2025**.
- **PFA, întreprinderile individuale și familiale** sunt explicit exceptate — pentru că nu au obligația legală de a organiza și ține contabilitatea în partidă dublă, spre deosebire de SRL/SA.
- Contribuabilii nou-înființați/încadrați după data de referință a categoriei lor depun D406 „începând cu data efectivă a înregistrării", prima depunere fiind în ultima zi a lunii care urmează perioadei de raportare.

## Ce se greșește în practică

- Se presupune că doar plătitorii de impozit pe profit (nu și microîntreprinderile) au obligația SAF-T — de fapt, criteriul e forma juridică și categoria de mărime a contribuabilului, nu tipul de impozit.
- Se ignoră faptul că firmele mici (majoritatea SRL-urilor) au intrat sub obligația de depunere abia din 1 ianuarie 2025, mult mai târziu decât marii și mijlociii contribuabili — o firmă înființată recent trebuie să verifice data de referință corectă pentru categoria ei.
- Se confundă PFA-ul cu SRL-ul la acest capitol: un PFA nu depune niciodată SAF-T, indiferent de cifra de afaceri, pentru că nu ține contabilitate în partidă dublă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **generează efectiv fișierul SAF-T (declarația D406)**, construit din schema XSD oficială publicată de ANAF (versiunea 2.4.9): Header, MasterFiles (conturi, clienți, furnizori, tabelul de TVA), GeneralLedgerEntries (notele contabile) și SourceDocuments (facturi de vânzare/achiziție cu linii reale pe produs, reconciliate cu antetul). Aplicația verifică structural fișierul înainte de depunere, potrivit regulilor din XSD-ul oficial. Rămâne responsabilitatea contabilului verificarea încadrării firmei în categoria de contribuabil corectă (mare/mijlociu/mic) și a datei de referință de la care obligația devine efectivă.

[iConta.eu](/)
