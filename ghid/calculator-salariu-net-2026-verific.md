---
title: "Calculator salariu net 2026: cum verific reținerile"
description: "Cele trei rețineri legale din salariul brut — CAS 25%, CASS 10%, impozit 10% — și cum le calculează și le afișează iConta.eu pe fluturașul de salariu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Calculator salariu net 2026: cum verific reținerile

Din salariul brut lunar, un angajat cu normă întreagă și fără facilități speciale are, în 2026, exact trei rețineri obligatorii: contribuția de asigurări sociale (CAS), contribuția de asigurări sociale de sănătate (CASS) și impozitul pe venit. Toate trei se calculează pe cote fixe, în cascadă — nu simultan pe brut.

## Temeiul legal

::: ghid-temei
„Cotele de contribuții de asigurări sociale sunt următoarele: a) 25% datorată de către persoanele fizice care au calitatea de angajați [...]."

„Cota de contribuție de asigurări sociale de sănătate este de 10% și se datorează de către persoanele fizice care au calitatea de angajați [...]."

„Impozitul lunar [...] se determină astfel: a) la locul unde se află funcția de bază, prin aplicarea cotei de 10% asupra bazei de calcul determinată ca diferență între venitul net din salarii calculat prin deducerea din venitul brut a contribuțiilor sociale obligatorii aferente unei luni [...] și [...] deducerea personală acordată pentru luna respectivă [...]."
— Codul fiscal, art. 138 lit. a), art. 156 și art. 78 alin. (2) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ordinea de calcul, exact așa cum rezultă din text:

- **CAS = 25% din salariul brut.**
- **CASS = 10% din salariul brut.**
- **Impozitul = 10%**, dar nu din brut, ci din **venitul net** rămas după scăderea CAS și CASS, din care se mai scade și **deducerea personală** (dacă salariatul are dreptul la ea, în funcție de venit și de persoanele aflate în întreținere).
- **Salariul net = brut − CAS − CASS − impozit.**

## Ce se greșește în practică

- Se calculează impozitul de 10% direct din salariul brut, nu din venitul net rămas după CAS, CASS și deducerea personală.
- Se aplică deducerea personală mecanic, fără să se verifice pragurile de venit de la care aceasta scade sau dispare.
- Se omit alte elemente care intră în baza de calcul a contribuțiilor (tichete de masă, tichete de vacanță impozabile), tratându-se salariul de bază ca singura sumă supusă reținerilor.

## Ce face iConta.eu

Calculul brut-net e o funcție reală, folosită curent: `core/salarizare.py` (`calcul_salariu`) aplică exact cascada de mai sus — CAS 25%, CASS 10%, apoi impozitul 10% pe venitul net rămas, cu deducerea personală calculată automat din numărul de persoane aflate în întreținere. Rezultatul apare direct pe fluturașul de salariu, din ecranul Stat de plată, cu fiecare reținere afișată pe rândul ei (CAS, CASS, deduceri, impozit, salariu net), plus costul total pentru angajator (inclusiv contribuția asiguratorie pentru muncă de 2,25%, suportată separat de angajator). La fiecare reținere generată, aplicația scrie automat și nota contabilă corespunzătoare (641/421, 421/4315, 421/4316, 421/444).

[iConta.eu](/)
