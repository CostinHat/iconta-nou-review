---
title: "Amortizarea activelor deținute în coproprietate"
description: "Ce condiție pune Codul fiscal pentru ca un activ să fie mijloc fix amortizabil și de ce coproprietatea nu are o regulă fiscală explicită de amortizare, spre deosebire de impozitele locale."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Amortizarea activelor deținute în coproprietate

Când o firmă deține un activ în coproprietate — de exemplu un utilaj cumpărat împreună cu un alt operator economic — întrebarea firească e cât din valoarea lui poate amortiza fiecare coproprietar. Codul fiscal nu are, pentru amortizare, o regulă la fel de explicită precum are pentru impozitele locale pe clădiri, terenuri sau mijloace de transport aflate în coproprietate.

**Limitare declarată**: sursele ANAF consultate pentru acest ghid nu conțin o normă explicită privind amortizarea fiscală a activelor deținute în coproprietate. Codul fiscal reglementează separat, cu text expres, situația coproprietății pentru scutiri de impozite locale (clădiri, terenuri, mijloace de transport) și pentru repartizarea venitului din cedarea folosinței bunurilor — dar nu și pentru amortizarea unui mijloc fix folosit în activitatea economică. Ce se poate cita cu certitudine e condiția generală care definește un mijloc fix amortizabil.

## Temeiul legal

::: ghid-temei
„(2) Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții: a) este deținut și utilizat în producția, livrarea de bunuri sau în prestarea de servicii, pentru a fi închiriat terților sau în scopuri administrative; b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei; această limită se actualizată anual, în funcție de indicele de inflație, prin hotărâre a Guvernului; c) are o durată normală de utilizare mai mare de un an."
— Legea 227/2015 (Codul fiscal), art. 28 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce se poate desprinde, cu prudență, din text și din structura generală a Codului fiscal:

- **Condiția de bază e „deținut și utilizat"**, nu „deținut în proprietate exclusivă" — textul nu exclude coproprietatea, dar nici nu o reglementează expres pentru amortizare.
- **Legea tratează explicit coproprietatea în alte contexte fiscale** — la scutirile de impozit pe clădiri/terenuri/mijloace de transport, principiul aplicat constant e alocarea „corespunzător cotei-părți din dreptul de proprietate"; la venitul din cedarea folosinței bunurilor deținute în coproprietate, repartizarea se face proporțional cu cotele deținute (sau egal, pentru devălmășie).
- **Aplicarea acestui principiu (cotă-parte) și la amortizare e o interpretare prin analogie**, nu o regulă explicită — coerentă cu felul în care legea tratează coproprietatea în restul Codului fiscal, dar fără text expres care să o transeze pentru amortizare. Fiecare coproprietar amortizează, în practică, partea din valoarea de intrare corespunzătoare cotei sale, dar firma trebuie să documenteze clar cota deținută și utilizarea reală în scop economic.
- **Valoarea fiscală minimă (5.000 lei) și durata de utilizare de peste un an** se verifică la nivelul întregului activ, nu la nivelul cotei individuale a fiecărui coproprietar — condițiile de la lit. b) și c) privesc mijlocul fix ca atare.

## Ce se greșește în practică

- Se amortizează integral, de către un singur coproprietar, valoarea unui activ deținut în coproprietate, fără nicio documentare a cotei reale deținute.
- Se presupune că regula „cotă-parte" din impozitele locale (clădiri, terenuri, mijloace de transport) se aplică automat, ca text explicit, și la amortizarea fiscală — de fapt e o extensie prin analogie, nu o prevedere directă, și trebuie tratată ca atare, cu documentare suplimentară.
- Se ignoră condiția generală a art. 28 alin. (2) lit. a) — utilizarea efectivă în activitatea economică a fiecărui coproprietar — presupunând că simpla deținere a unei cote justifică amortizarea, indiferent de utilizare.

## Ce face iConta.eu

La data acestui ghid, iConta.eu gestionează mijloacele fixe și amortizarea lor prin `core/repo_mijloace_fixe.py` și modulele conexe (`reevaluare.py`, `d406_active.py`), dar nu are un câmp dedicat cotei de coproprietate a unui activ — fiecare mijloc fix e înregistrat cu o valoare de intrare unică, amortizată integral pentru firma care îl are în evidență. Determinarea și documentarea cotei-părți pentru un activ deținut în coproprietate cu un alt operator economic rămân, la acest moment, în afara aplicației.

[iConta.eu](/)
