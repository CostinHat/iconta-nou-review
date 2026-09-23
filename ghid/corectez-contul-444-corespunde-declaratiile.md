---
title: Cum corectez contul 444 dacă nu corespunde cu declarațiile depuse?
description: Corectarea contului 444 depinde de cauza divergenței față de D112 — stat de salarii necontabilizat, notă în ciornă sau altă situație de investigat — și, dacă există un XML efectiv depus la ANAF, comparația se face cu acela, nu cu o regenerare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez contul 444 dacă nu corespunde cu declarațiile depuse?

Contul 444 (impozitul pe venituri din salarii) trebuie să corespundă, cu o mică toleranță de rotunjire, cu suma declarată sub codul 602 în D112. Când nu corespunde față de declarația efectiv depusă la ANAF — nu față de o simplă regenerare — remediul corect depinde de motivul divergenței, nu de o ajustare făcută „ca să dea bine".

## Temeiul legal

::: ghid-temei
„Articolul 147 — Depunerea Declarației privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate. (1) Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate." — Codul fiscal (Legea 227/2015), art. 147
:::

Cota de impozit aplicată codului 602 din D112 este 10%, conform art. 64 alin. (1) din Codul fiscal — soldul creditor al contului 444 trebuie să reflecte exact această sumă declarată, cu toleranța de rotunjire calculată (0,5 lei per salariat, minim 1 leu).

## Ce se greșește în practică

Cea mai frecventă greșeală este „ajustarea" soldului contului 444 printr-o notă manuală, doar pentru ca verificarea să dea verde, fără să se identifice de ce diferă de fapt de declarația depusă. A doua greșeală este ignorarea distincției dintre XML-ul efectiv depus la ANAF (persistat la momentul depunerii) și o regenerare calculată acum din datele curente — dacă declarația a fost depusă cu o variantă diferită de cea regenerată azi, o corecție bazată doar pe regenerare poate să nu reflecte ce s-a depus efectiv.

## Ce face iConta.eu

Funcția `compara_d112` (`core/control_incrucisat.py`) preferă, la stabilirea sumei declarate, XML-ul D112 efectiv depus și persistat la momentul depunerii; doar dacă acesta nu există, folosește o regenerare calculată acum — și comunică explicit în rezultat care variantă a folosit (depusă sau regenerată). Pe baza acestei sume, comparată cu rulajul creditor al contului 444 (citit doar din notele validate), aplicația indică motivul divergenței și remediul corespunzător:

- Contul 444 e la zero și nu există nicio notă (nici în ciornă) → statul de salarii nu a fost contabilizat; remediu executabil, „contabilizează statul de plată".
- Contul e la zero, dar există o notă de salarii în ciornă → remediu sugerat, „validează nota" — ciornele nu intră în evidența folosită la comparație.
- Orice altă divergență (de exemplu contul are deja o sumă, dar nu cea declarată) → remediu de investigație, cu posibile cauze enumerate explicit (salariați adăugați/șterși ulterior, note manuale pe cont, corecții de lună anterioară, concedii medicale înregistrate diferit) — nu o ajustare automată a contului.

[iConta.eu](/)
