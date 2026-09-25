---
title: "Ce s-a schimbat în Codul fiscal la amortizare în 2026"
description: "Metoda de amortizare superaccelerată introdusă în Codul fiscal pentru activele noi puse în funcțiune în 2026, prin OUG 8/2026, și condițiile ei de aplicare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce s-a schimbat în Codul fiscal la amortizare în 2026

Pentru anumite categorii de mijloace fixe puse în funcțiune în 2026, Codul fiscal a introdus, prin OUG 8/2026, o metodă de amortizare accelerată chiar mai agresivă decât cea deja existentă — o creștere reală a procentului deductibil în primul an de utilizare, nu doar o modificare de formă.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile alin. (5) și (8), pentru activele noi, achiziționate/produse și puse în funcțiune, în perioada cuprinsă între 1 ianuarie 2026-31 decembrie 2026 inclusiv, respectiv în anul fiscal modificat care începe în anul 2026, după caz, din subgrupa 2.1 - Echipamente tehnologice, respectiv mașini, unelte și instalații de lucru și/sau subgrupa 2.4 - «Animale și plantații» se poate aplica o metodă de amortizare superaccelerată potrivit căreia amortizarea se calculează după cum urmează: a) pentru primul an de utilizare, amortizarea nu poate depăși 65% din valoarea fiscală de la data intrării în patrimoniul contribuabilului a activului; b) pentru următorii ani de utilizare, amortizarea se calculează prin raportarea valorii rămase de amortizare a activului la durata normală de utilizare rămasă a acestuia."
— Legea 227/2015, art. 28 alin. (8^1), introdus de OUG 8/2026 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce e nou, comparativ cu amortizarea accelerată „obișnuită" (unde primul an e limitat la 50%):

- Metoda **superaccelerată** ridică plafonul primului an de utilizare la **65%** din valoarea fiscală de intrare — cu 15 puncte procentuale peste procentul standard de amortizare accelerată.
- Se aplică exclusiv activelor **noi**, achiziționate/produse **și puse în funcțiune** strict în intervalul 1 ianuarie – 31 decembrie 2026 (sau în anul fiscal modificat corespunzător), și exclusiv din **subgrupa 2.1** (echipamente tehnologice, mașini, unelte, instalații de lucru) și **subgrupa 2.4** (animale și plantații).
- Pentru imobilizările în curs de execuție începute înainte de 31 decembrie 2025, regula superaccelerată se aplică **doar pentru valoarea** corespunzătoare activelor efectiv puse în funcțiune în 2026 — nu retroactiv pentru toată investiția.
- Este o **excepție opțională** de la regulile generale de amortizare accelerată (alin. 5 și 8) — textul spune „se poate aplica", nu obligă la utilizarea ei.

## Ce se greșește în practică

- Se aplică metoda superaccelerată oricărui mijloc fix pus în funcțiune în 2026, indiferent de subgrupa din Catalogul mijloacelor fixe — condiția strictă e încadrarea în subgrupa 2.1 sau 2.4, nu simpla noutate a activului.
- Se confundă procentul de 65% cu cel de 50% al amortizării accelerate generale (alin. 5) — sunt regimuri distincte, cu procente diferite pentru primul an, iar aplicarea greșită a procentului duce la o cheltuială de amortizare deductibilă incorectă.
- Se aplică regula retroactiv pentru toată valoarea unei investiții începute în 2025 și finalizate în 2026, deși legea limitează explicit efectul superaccelerării doar la valoarea pusă în funcțiune efectiv în 2026.

## Ce face iConta.eu

Motorul de amortizare al iConta.eu (`core/d406_active.py`, folosit atât pentru registrul mijloacelor fixe, cât și pentru D406) calculează amortizarea pe patru metode distincte, în funcție de metoda selectată pentru fiecare activ, conform prevederilor art. 28 din Codul fiscal — ecranul de mijloace fixe și notele lunare de amortizare consumă acest motor unic, astfel încât cifra de amortizare afișată reflectă metoda reală a activului, nu implicit liniară. Confirmarea că un anumit activ se încadrează în subgrupa 2.1 sau 2.4 și că a fost pus efectiv în funcțiune în 2026, condiții necesare pentru metoda superaccelerată de la art. 28 alin. (8^1), rămâne, la acest moment, o verificare manuală a contabilului la momentul înregistrării activului.

[iConta.eu](/)
