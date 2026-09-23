---
title: Ce fac dacă am tratat greșit indemnizația administratorului?
description: Dacă indemnizația a fost trecută ca salariu clasic (cu CAM și D112), corecția înseamnă stornare, recalcul pe regulile de mandat și, separat, verificarea declarativă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă am tratat greșit indemnizația administratorului?

Cea mai frecventă formă a acestei greșeli e tratarea indemnizației de mandat exact ca pe un salariu de la un contract individual de muncă: cu CAM reținută și, eventual, deja raportată în D112 ca angajat cu CIM. Corecția presupune două lucruri separate: reface calculul și nota contabilă, apoi verifici ce s-a declarat deja.

## Temeiul legal

::: ghid-temei
„remunerația administratorilor societăților, companiilor/societăților naționale și regiilor autonome, desemnați/numiți în condițiile legii, precum și sumele primite de reprezentanții în adunarea generală a acționarilor și în consiliul de administrație"

*(Codul fiscal — Legea nr. 227/2015, art. 76 alin. (2) lit. o))*
:::

## Pașii de corecție

1. **Stornezi nota greșită.** Dacă indemnizația a fost trecută prin 641 (cheltuieli cu salariile) cu CAM reținută, storniezi întreaga notă.
2. **Reintroduci corect, ca mandat.** Recalculezi cu CAS 25% + CASS 10% + impozit 10% pe rest, fără CAM, și înregistrezi prin 621, nu 641.
3. **Verifici ce ai declarat deja la stat.** Dacă indemnizația greșit tratată a fost deja inclusă într-o declarație D112 ca salariat cu contract individual de muncă (tip asigurat 1), acea declarație trebuie rectificată — administratorul de mandat corespunde unui tip de asigurat diferit (tip 6, „Administratori ai SC/CN/SN/RA, membri CA/CS/CC", conform structurii oficiale D112).
4. **Verifici diferența de contribuții plătite în plus sau în minus** față de calculul corect (CAM plătită în plus, eventual CAS/CASS calculate pe altă bază) și regularizezi cu bugetul de stat.

## Ce se greșește în practică

- Se corectează doar nota contabilă internă, fără să se verifice dacă eroarea a ajuns și în declarațiile deja depuse.
- Se presupune că, odată corectată nota, D112 se „recalculează automat" — nu e cazul, rectificarea unei declarații deja depuse e un pas separat, manual.
- Se aplică, din inerție, aceleași reguli de exceptare/plafon minim ca la un salariat cu CIM (de exemplu pragul de contribuție minimă), deși acestea sunt gândite pentru raporturi de muncă, nu pentru mandat.

## Ce face iConta.eu

Modulul F021 (`core/contracte_speciale.py`) oferă calculul și nota corecte pentru mandat, prin funcțiile `calcul_mandat` și `nota(fel="mandat")`. O limitare importantă de reținut la corectare: generarea automată a D112 din aplicație (`core/d112.py`) citește exclusiv din tabela de salariați cu CIM — nu are, la acest moment, o punte funcțională spre notele de mandat/cenzor. Dacă indemnizația a fost declarată greșit la D112 ca salariat clasic, rectificarea acelei declarații rămâne un pas manual, în afara acestui modul.

[iConta.eu](/)
