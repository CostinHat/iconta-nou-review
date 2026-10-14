---
title: "Cum estimez impozitul pe profit la bugetul anual"
description: "Regula legală prin care firmele plătitoare de impozit pe profit determină plățile anticipate trimestriale, ca bază pentru un buget anual realist."
published: 2026-09-24
modified: 2026-10-13
poarta: v1
---

# Cum estimez impozitul pe profit la bugetul anual

Firmele care aplică sistemul de declarare anuală a impozitului pe profit, cu plăți anticipate trimestriale, nu estimează impozitul „din burtă" pentru bugetul anual — Codul fiscal dă o formulă exactă, legată de impozitul anului precedent, actualizat cu indicele prețurilor de consum.

## Temeiul legal

::: ghid-temei
„(8) Contribuabilii care aplică sistemul de declarare și plată a impozitului pe profit anual, cu plăți anticipate efectuate trimestrial, determină plățile anticipate trimestriale în sumă de o pătrime din impozitul pe profit datorat pentru anul precedent, actualizat cu indicele prețurilor de consum, estimat cu ocazia elaborării bugetului inițial al anului pentru care se efectuează plățile anticipate, până la data de 25 inclusiv a lunii următoare trimestrului pentru care se efectuează plata, cu excepția plății anticipate aferente trimestrului IV care se declară și se plătește până la data de 25 decembrie (...). Impozitul pe profit pentru anul precedent, pe baza căruia se determină plățile anticipate trimestriale, este impozitul pe profit anual, conform declarației privind impozitul pe profit."
— Legea 227/2015, art. 41 alin. (8) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„(10^1) Prin excepție de la prevederile alin. (8) , plata anticipată pentru trimestrul I al fiecărui an fiscal/an fiscal modificat se calculează prin aplicarea cotei de impozit asupra profitului contabil al perioadei pentru care se efectuează plata anticipată. Aceasta se declară și se plătește până la data de 25 inclusiv a lunii următoare trimestrului I.”
— Legea 227/2015, art. 41 alin. (10^1) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Prevederile art. 6 pct. 1-14 se aplică începând cu anul fiscal 2026, iar pentru contribuabilii care intră sub incidența prevederilor art. 16 alin. (5) începând cu anul fiscal modificat care începe în anul 2026.”
— OUG 8/2026, art. 10 alin. (2) (sursă: [OUG nr. 8/2026 privind instituirea unor măsuri de relansare economică](https://legislatie.just.ro/Public/DetaliiDocument/307580))
:::

Pentru bugetul anual, formula de estimare e, deci:

- **Plata anticipată trimestrială = 1/4 din impozitul pe profit anual al anului precedent**, actualizată cu indicele prețurilor de consum folosit la elaborarea bugetului inițial al anului curent.
- **Excepție, începând cu anul fiscal 2026: trimestrul I.** Plata anticipată pentru trimestrul I nu mai e 1/4 din impozitul anului precedent, ci se calculează aplicând cota de impozit asupra profitului contabil al trimestrului I (art. 41 alin. (10^1), introdus prin OUG 8/2026). Regula 1/4 rămâne pentru trimestrele II-IV. Pentru buget, plata din trimestrul I se estimează deci din profitul contabil estimat pentru primul trimestru.
- Termenul de plată pentru trimestrele I-III este **25 a lunii următoare trimestrului**; pentru trimestrul IV, termenul este **25 decembrie**, nu 25 ianuarie anul următor.
- Firmele care aplică IFRS calculează plățile anticipate la fel, dar **fără influența** din regularizările specifice art. 21 (alin. (9)).
- Contribuabilii **nou-înființați**, cei cu **pierdere fiscală** în anul precedent, cei ieșiți din **inactivitate temporară** sau cei care în anul precedent au fost **plătitori de impozit micro** nu folosesc formula 1/4 — ei aplică sistemul trimestrial pe profitul contabil efectiv al perioadei (alin. (6)-(7)).

## Ce se greșește în practică

- Se estimează bugetul anual pornind de la profitul contabil **curent**, nu de la impozitul pe profit **anual al anului precedent** — formula legală de la alin. (8) e explicit legată de anul precedent, actualizat cu inflația, nu de o proiecție a anului curent.
- Se bugetează și trimestrul I la 1/4 din impozitul anului precedent, deși din anul fiscal 2026 plata pentru trimestrul I se calculează pe profitul contabil al trimestrului (alin. (10^1)).
- Se ignoră excepția trimestrului IV (termen 25 decembrie) și se bugetează plata cu o lună întârziere, ca și cum ar urma regula generală de 25 a lunii următoare.
- Se aplică formula standard (1/4 din anul precedent) și la firme nou-înființate sau ieșite din inactivitate temporară, deși acestea intră sub regimul de plată pe profitul trimestrial efectiv, nu pe baza anului anterior.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un modul de bugetare sau de estimare a impozitului pe profit** pentru anul în curs — aplicația generează declarațiile pe baza datelor contabile efective introduse (facturi, note contabile), nu proiecții. Impozitul pe profit se calculează și se declară pe baza rezultatelor reale ale firmei, nu a unei estimări bugetare anticipate: în D100, aplicația calculează impozitul în sistemul trimestrial, cumulat de la începutul anului, iar D101 pentru declarația anuală. Aplicația nu calculează plățile anticipate din sistemul anual (nici cea din trimestrul I după alin. (10^1), nici cele de 1/4 după alin. (8)); construirea unui buget anual pe aceste reguli rămâne un calcul pe care contabilul îl face separat.

[iConta.eu](/)
