---
title: "Cum verific D394 cu jurnalul de TVA înainte de control?"
description: "Mecanismele reale de verificare a D394 înainte de depunere în iConta.eu — validare pe validatorul oficial și recalcul independent din liniile brute ale facturilor."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific D394 cu jurnalul de TVA înainte de control?

D394 se generează din aceleași facturi care alimentează jurnalul de vânzări și cumpărări, așa că o verificare de fond înainte de un control fiscal înseamnă, în esență, confirmarea că totalurile pe cotă din declarație corespund exact cu ce arată evidența brută a facturilor din perioada respectivă.

## Temeiul legal

::: ghid-temei
„În cazul în care, după depunerea declaraţiei, persoana impozabilă constată existenţa unor omisiuni/erori în datele declarate, aceasta trebuie să depună o nouă declaraţie corect completată cu operaţiunile care necesită modificarea şi/sau operaţiunile care nu au fost declarate, declaraţie care înlocuieşte declaraţia informativă depusă iniţial."
— OPANAF 2194/2025, Anexa 2 pct. 3 (sursă: anaf_surse/opanaf_2194_2025_d394.txt)
:::

Textul confirmă un punct important pentru orice verificare făcută înainte de un control: D394 nu are o „rectificativă" separată ca formular — o eroare descoperită se corectează prin depunerea unei **noi declarații complete**, care înlocuiește integral declarația inițială pentru acea perioadă, nu doar prin corectarea unei linii.

Din această regulă rezultă ce merită verificat concret, cotă cu cotă, înainte de un eventual control:

- dacă baza impozabilă și TVA-ul aferent fiecărei cote din declarația D394 corespund exact cu suma liniilor brute ale facturilor emise/primite din perioada de raportare;
- dacă vreo factură a fost corectată sau anulată **după** ce declarația inițială a fost depusă, fără ca redepunerea completă să fi fost făcută ulterior;
- dacă operațiunile intracomunitare (excluse corect din D394) nu au fost, din greșeală, incluse sau, invers, dacă vreo operațiune națională taxabilă lipsește nemotivat.

## Ce se greșește în practică

- Se presupune că o singură linie greșită poate fi „corectată" separat în D394, ca într-un decont de TVA rectificativ — corect e să se redepună întreaga declarație, completă, pentru acea perioadă.
- Se verifică doar totalul general al declarației, nu defalcarea pe fiecare cotă de TVA — o eroare poate fi „ascunsă" dacă două cote compensează valoric o greșeală de clasificare.
- Se ignoră facturile introduse manual (bonuri, borderouri), care nu trec întotdeauna prin aceleași verificări automate ca facturile obișnuite.

## Ce face iConta.eu

Înainte ca fișierul D394 să fie considerat gata de depus, aplicația rulează **local** validatorul oficial ANAF (DUK) pe declarație. Separat de această validare structurală, aplicația recalculează **independent** totalurile pe cotă de TVA direct din liniile brute ale facturilor perioadei, cu un cod de calcul distinct de generatorul principal, și **oprește** generarea dacă cele două căi de calcul nu coincid — arătând explicit valorile care diferă și câmpul afectat.

Limitele acestui mecanism sunt declarate explicit în aplicație: nu acoperă operațiunile manuale (bonuri/borderouri, fără ecran propriu la data acestui ghid) și nu poate prinde o eroare de intrare care apare identic pe ambele căi de calcul (de exemplu o cotă de TVA greșit tastată o singură dată, direct pe factura sursă). Pentru acestea, verificarea rămâne una manuală a contabilului, direct pe jurnalul de TVA.

[iConta.eu](/)
