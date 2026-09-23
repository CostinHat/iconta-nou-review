---
title: "Generarea automată a D205: recomandări"
description: "Cum funcționează generarea automată a D205 din contul 457 și ce trebuie verificat manual înainte de a o folosi în siguranță."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Generarea automată a D205: recomandări

D205 pentru dividende nu se completează manual într-un formular din interfață — se generează automat, pornind din contabilitate. Câteva recomandări ajută la folosirea corectă a acestui flux.

## Temeiul legal

::: ghid-temei
"Acces UI: tab «Declarații» (D205) + tab «asociați» (fără ecran de completare manual dedicat — D205 se generează automat din contul 457 + cotele asociaților)."
— înregistrarea canonică a funcționalității F029, `/home/claude/iconta/FUNCTIONALITATI.csv`
:::

Termenul legal de depunere a declarației este ultima zi a lunii februarie a anului curent, pentru anul expirat (OPANAF 179/2022), distinct de termenul de virare a impozitului (25 a lunii, respectiv 25 ianuarie pentru dividendele distribuite dar neplătite).

## Ce se greșește în practică

Se generează declarația fără a verifica întâi dacă toate notele contabile relevante pe contul 457 au statutul "validată", sau fără a lua în calcul separat dividendele distribuite dar rămase neplătite la 31 decembrie.

## Ce face iConta.eu

Generatorul (`core/d205.py`) citește automat, pentru fiecare asociat cu cotă mai mare de zero, sumele din contul 457, dar **doar din notele contabile cu status "validata"** — o notă nevalidată nu intră în calcul. Înainte de generare, o verificare independentă (`core/d205_reconciliere.py`) recalculează separat baza și impozitul din contul 457 și blochează generarea dacă apare o divergență față de rezultatul motorului principal. Recomandări practice, bazate pe comportamentul confirmat al aplicației: (1) validați toate notele contabile pe contul 457 înainte de a genera declarația; (2) dacă există dividende distribuite dar neplătite la 31 decembrie, adăugați beneficiarul respectiv manual — generatorul automat nu îl include (vezi ghidul dedicat acestui subiect); (3) pentru dividende distribuite și plătite în ani diferiți, nu este nevoie de intervenție manuală asupra cotei — motorul aplică automat, pe tranșe, cota de la data fiecărei distribuiri.

[iConta.eu](/)
