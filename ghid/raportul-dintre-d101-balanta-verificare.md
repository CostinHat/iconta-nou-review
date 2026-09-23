---
title: Raportul dintre D101 și balanța de verificare
description: Cum reconciliază D101 baza contabilă din balanță — inclusiv verificarea independentă a sumei de plată emisă — și ce înseamnă asta pentru contabil.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Raportul dintre D101 și balanța de verificare

D101 nu e doar un formular completat cu cifre din balanță — motorul de generare rulează și o reconciliere separată a bazei contabile, ca să prindă eventualele neconcordanțe înainte ca declarația să ajungă la ANAF.

## Temeiul legal

::: ghid-temei
La generare, aplicația „rulează reconciliere independentă a bazei contabile (`core/d101_reconciliere.py`) și verifică `totalPlata_A` emis (`core/reconciliere_emis.py`)"
— sursă: `core/d101.py`, funcția `genereaza()`, liniile 470–538, dosar de cercetare F027.

Tot funcția `genereaza()` „cere explicit P47 dacă `ca_an_precedent_eur` transmis depășește pragul IMCA și P47 nu a fost furnizat manual — nu subevaluează tacit impozitul unei firme mari"
— sursă: `core/d101.py`, liniile 484–489, dosar de cercetare F027.
:::

Legea impune ca declarația D101 să reflecte corect rezultatul fiscal calculat din evidența contabilă (balanță), fără o procedură normativă separată de „reconciliere" tehnică — aceasta din urmă e un control intern al aplicației, nu o cerință legală distinctă. Ceea ce contează legal este ca baza de calcul (venituri, cheltuieli, deduceri, add-back-uri) să corespundă exact înregistrărilor contabile din balanța de verificare la data generării declarației.

## Ce se greșește în practică

Greșeala frecventă e generarea D101 dintr-o balanță „provizorie", înainte de închiderea definitivă a exercițiului, urmată de modificări ulterioare ale balanței care nu mai sunt reflectate în declarația deja generată/transmisă. A doua greșeală e ignorarea pragului IMCA la firmele mari — omiterea introducerii manuale a valorii P47 atunci când cifra de afaceri a anului precedent depășește 50.000.000 EUR, ceea ce poate subevalua tacit impozitul datorat.

## Ce face iConta.eu

La generarea D101, iConta.eu rulează o reconciliere independentă a bazei contabile față de balanță și verifică suma totală de plată emisă, înainte de a produce declarația finală. Pentru firmele mari, dacă cifra de afaceri a anului precedent depășește pragul IMCA de 50.000.000 EUR și valoarea P47 nu a fost introdusă manual, aplicația o cere explicit — exact pentru a nu lăsa impozitul subevaluat tacit. Această reconciliere tehnică nu înlocuiește, însă, verificarea manuală a contabilului asupra corectitudinii datelor din balanță înainte de generare.

[iConta.eu](/)
