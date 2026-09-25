---
title: "Cum verifici în vectorul fiscal dacă firma este micro sau plătitoare de impozit pe profit"
description: "Ce este vectorul fiscal, unde apare regimul de impozitare al firmei și cum se verifică dacă firma e corect încadrată la micro sau la impozit pe profit."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verifici în vectorul fiscal dacă firma este micro sau plătitoare de impozit pe profit

Regimul de impozitare — micro sau profit — nu e o alegere liberă în orice moment, ci rezultă din condiții legale verificate la 31 decembrie a anului anterior. Vectorul fiscal e locul unde ANAF ține evidența tuturor obligațiilor de declarare curente ale firmei, inclusiv acest regim, iar contabilul are nevoie să știe atât ce spune vectorul, cât și ce spune legea, pentru că nu sunt automat același lucru.

## Temeiul legal

::: ghid-temei
„39. vector fiscal - totalitatea tipurilor de obligații fiscale pentru care există obligații de declarare cu caracter permanent;"
— Legea 207/2015, art. 1 pct. 39 (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„(1) În sensul prezentului titlu, o microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent: [...] c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. [...] d) capitalul social al acesteia este deținut de persoane, altele decât statul și unitățile administrativ-teritoriale; [...] g) are cel puțin un salariat [...]"
— Legea 227/2015, art. 47 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din aceste două texte rezultă structura verificării:

- **Vectorul fiscal** e evidența ANAF a obligațiilor de declarare curente ale firmei (ce declarații e obligată să depună periodic) — regimul de impozit (micro sau profit) e una dintre componentele lui, alături de TVA, contribuții etc.
- **Încadrarea efectivă la micro** se verifică însă din Codul fiscal, la art. 47 — venituri sub 100.000 euro, capital social privat, minimum un salariat, situații financiare depuse la termen ș.a.
- Firma nu poate "alege" să fie micro dacă nu îndeplinește cumulativ toate condițiile de la art. 47; și invers, dacă le îndeplinește și nu se află la vreo excludere (bancă, asigurări, jocuri de noroc etc.), e obligată să aplice regimul micro, nu profit.

## Ce se greșește în practică

- Se verifică doar ce arată certificatul de atestare fiscală sau vectorul afișat în SPV, fără a reconfirma condițiile de fond din art. 47 — vectorul reflectă ce a fost declarat, nu garantează că declararea a fost corectă.
- Se presupune că regimul rămâne fix odată stabilit, ignorând că depășirea plafonului de 100.000 euro în cursul anului schimbă regimul de la trimestrul următor, nu de la anul următor.
- Se confundă vectorul fiscal (obligațiile de declarare) cu categoria de mărime a entității din situațiile financiare (micro-entitate/entitate mică din OMFP 1802/2014) — sunt două clasificări diferite, cu criterii diferite.

## Ce face iConta.eu

Regimul fiscal al firmei (`micro` sau `profit`) se completează manual de contabil în ecranul **Date firma**, ca parte a vectorului fiscal intern al aplicației (`regim_fiscal`, `platitor_tva`, `tip_decont`, `operatiuni_ic`) — câmp obligatoriu, fără valoare implicită tăcută. Pe baza acestei valori, motorul decide ce declarații datorează firma (D100 trimestrial pentru micro, D101 anual pentru profit). La data acestui ghid, iConta.eu **nu interoghează automat ANAF** pentru a confirma sau contrazice regimul introdus — verificarea față de condițiile art. 47 rămâne responsabilitatea contabilului.

[iConta.eu](/)
