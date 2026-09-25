---
title: "Care este diferența dintre reparație și modernizare la un mijloc fix?"
description: "Criteriul contabil care decide dacă o cheltuială ulterioară asupra unui mijloc fix se trece pe cheltuieli ale perioadei sau majorează valoarea activului, potrivit reglementărilor OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Care este diferența dintre reparație și modernizare la un mijloc fix?

Distincția nu e una de bun-simț sau de sumă cheltuită — legea contabilă dă un singur criteriu: efectul cheltuielii asupra beneficiilor economice viitoare ale activului, nu natura fizică a intervenției.

## Temeiul legal

::: ghid-temei
„227. - (1) Cheltuielile ulterioare efectuate în legătură cu o imobilizare corporală sunt cheltuieli ale perioadei în care sunt efectuate sau majorează valoarea imobilizării respective, în funcție de beneficiile economice aferente acestor cheltuieli (de exemplu, influența asupra duratei de viață rămase a imobilizărilor), potrivit criteriilor generale de recunoaștere."
— OMFP nr. 1802/2014 (Reglementări contabile), pct. 227 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Criteriul de decizie, aplicat practic:

- Dacă intervenția **readuce activul la parametrii funcționali inițiali**, fără să-i extindă durata de viață sau performanța (de exemplu, înlocuirea unei piese uzate), este o **reparație** — cheltuială a perioadei, deductibilă imediat.
- Dacă intervenția **modifică parametrii tehnici inițiali** și generează beneficii economice viitoare suplimentare (durată de viață mai lungă, capacitate mai mare, consum mai redus), este o **modernizare** — se capitalizează, majorând valoarea contabilă a mijlocului fix, și se amortizează pe durata rămasă.
- Criteriul se aplică și inspecțiilor sau reviziilor generale regulate: costul poate fi recunoscut drept cheltuială sau capitalizat ca înlocuire a unei componente, în funcție de aceleași criterii de recunoaștere.

## Ce se greșește în practică

- Se decide capitalizarea sau trecerea pe cheltuieli în funcție de valoarea facturii (facturi mari → capitalizate, facturi mici → cheltuieli), fără legătură cu criteriul real din reglementare — efectul asupra beneficiilor economice viitoare.
- Se capitalizează sistematic orice lucrare la un mijloc fix aflat încă în garanție sau recent achiziționat, deși o simplă reparație de întreținere rămâne cheltuială a perioadei, indiferent de vechimea activului.
- Se omite, la investiții efectuate asupra unor mijloace fixe cu durata normală de utilizare deja expirată fiscal, stabilirea unei noi durate de utilizare (prin comisie tehnică sau expert independent), necesară pentru amortizarea investiției.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează amortizarea pentru mijloacele fixe înregistrate ca atare, cu metodele permise (liniară, degresivă, accelerată) pe durata normală de funcționare introdusă (`core/d406_active.py`). Aplicația **nu decide automat** dacă o cheltuială ulterioară asupra unui mijloc fix trebuie capitalizată sau trecută pe cheltuieli — această clasificare, pe baza criteriilor de la pct. 227 din OMFP 1802/2014, rămâne o evaluare a contabilului, care apoi introduce corect fie o cheltuială curentă, fie o majorare a valorii activului.

[iConta.eu](/)
