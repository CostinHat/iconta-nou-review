---
title: "Am calculat greșit depășirea plafonului micro: ce fac"
description: Primul pas e refacerea corectă a calculului — venituri cumulate de la începutul anului, la cursul fix de la închiderea exercițiului financiar precedent — pentru a stabili trimestrul real al depășirii; abia apoi se corectează declarațiile afectate.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Am calculat greșit depășirea plafonului micro: ce fac

Dacă se descoperă ulterior că plafonul de 100.000 euro a fost calculat greșit — fie s-a concluzionat greșit că a fost depășit când nu era cazul, fie invers — primul pas nu e corectarea declarațiilor, ci refacerea corectă a calculului plafonului, ca să se stabilească exact trimestrul real al depășirii (dacă există).

## Temeiul legal

::: ghid-temei
„Limitele fiscale prevăzute la alin. (1) se verifică pe baza veniturilor înregistrate cumulat de la începutul anului fiscal. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar precedent." — Codul fiscal, art. 52 alin. (5). „Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită." — art. 52 alin. (1).
:::

## Pasul 1: refaceți calculul corect

Verificați, pentru fiecare trimestru cumulat de la începutul anului: veniturile luate în calcul (cele relevante potrivit art. 52 alin. (5)/(5^1), inclusiv veniturile persoanelor afiliate, dacă e cazul), cursul de schimb folosit (trebuie să fie cel fix, de la închiderea exercițiului financiar precedent, nu cursul zilnic), și suma cumulată rezultată în euro. Identificați exact trimestrul în care suma cumulată depășește, pentru prima dată, 100.000 euro — dacă un asemenea trimestru există.

## Pasul 2: acționați în funcție de rezultat

- **Dacă recalcularea arată că plafonul chiar a fost depășit**, dar firma a continuat să declare impozit micro peste acel trimestru — corectați trimestrele declarate greșit prin formularul 710 și treceți la impozit pe profit pentru perioada de la trimestrul depășirii încolo (a se vedea și procedura de corecție după depășirea plafonului).
- **Dacă recalcularea arată că plafonul NU a fost, de fapt, depășit** (eroarea inițială a fost de calcul, de exemplu cursul greșit folosit), iar firma a trecut greșit la impozit pe profit — verificați dacă declarațiile de impozit pe profit deja depuse trebuie corectate/anulate și dacă firma poate reveni la declararea impozitului micro, cu formularul 710 pentru obligațiile afectate.

## Ce se greșește în practică

- Se corectează direct declarațiile, fără să se refacă mai întâi calculul plafonului cu cursul și cumulul corecte — riscul e o corecție bazată pe același calcul greșit.
- Se folosește cursul zilnic BNR pentru recalculare, în loc de cursul fix de la închiderea exercițiului financiar precedent — o sursă frecventă chiar a erorii inițiale.
- Se ignoră, la recalculare, veniturile persoanelor afiliate, în situațiile în care legea le cere incluse.

## Ce face iConta.eu

Aplicația nu calculează sau monitorizează automat plafonul de 100.000 euro — verificat direct în cod, nu există în `core/` o constantă sau o logică dedicată acestui plafon. Recalcularea corectă a plafonului (venituri cumulate, curs fix corect, eventuale venituri afiliate) rămâne o verificare manuală a contabilului. Odată stabilit trimestrul corect al depășirii (sau lipsa acesteia), corectarea declarațiilor afectate se face prin ecranul formularului 710 (`core/d710.py`), pentru fiecare obligație greșit declarată.

[iConta.eu](/)
