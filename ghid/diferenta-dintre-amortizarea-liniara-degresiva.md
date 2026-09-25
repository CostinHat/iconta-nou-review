---
title: "Care este diferența dintre amortizarea liniară, degresivă și accelerată?"
description: "Diferențele reale dintre cele trei regimuri de amortizare fiscală: ce mijloc fix are voie să folosească fiecare metodă și cum arată ritmul de deducere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Care este diferența dintre amortizarea liniară, degresivă și accelerată?

Cele trei metode nu diferă doar prin formulă, ci și prin **cine are voie să le folosească**: categoria mijlocului fix decide ce opțiuni sunt legale, nu preferința contabilului pentru un ritm de deducere mai rapid sau mai lent.

## Temeiul legal

::: ghid-temei
„(5) Regimul de amortizare pentru un mijloc fix amortizabil se determină conform următoarelor reguli: a) în cazul construcțiilor, se aplică metoda de amortizare liniară; b) în cazul echipamentelor tehnologice, respectiv al mașinilor, uneltelor și instalațiilor de lucru, precum și pentru computere și echipamente periferice ale acestora, contribuabilul poate opta pentru metoda de amortizare liniară, degresivă sau accelerată; c) în cazul oricărui altui mijloc fix amortizabil, contribuabilul poate opta pentru metoda de amortizare liniară sau degresivă.
(6) În cazul metodei de amortizare liniară, amortizarea se stabilește prin aplicarea cotei de amortizare liniară la valoarea fiscală de la data intrării în patrimoniul contribuabilului a mijlocului fix amortizabil.
(7) În cazul metodei de amortizare degresivă, amortizarea se calculează prin multiplicarea cotelor de amortizare liniară cu unul dintre coeficienții următori: a) 1,5, dacă durata normală de utilizare a mijlocului fix amortizabil este între 2 și 5 ani; b) 2,0, dacă durata normală de utilizare a mijlocului fix amortizabil este între 6 și 10 ani; c) 2,5, dacă durata normală de utilizare a mijlocului fix amortizabil este mai mare de 10 ani.
(8) În cazul metodei de amortizare accelerată, amortizarea se calculează după cum urmează: a) pentru primul an de utilizare, amortizarea nu poate depăși 50% din valoarea fiscală de la data intrării în patrimoniul contribuabilului a mijlocului fix; b) pentru următorii ani de utilizare, amortizarea se calculează prin raportarea valorii rămase de amortizare a mijlocului fix la durata normală de utilizare rămasă a acestuia."
— Legea 227/2015 (Codul fiscal), art. 28 alin. (5), (6), (7), (8) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Diferențele, punctual:

- **Cine are voie** — liniară: orice mijloc fix, fără excepție. Degresivă: orice mijloc fix, cu excepția construcțiilor (care sunt obligate la liniar). Accelerată: **doar** echipamente tehnologice, mașini, unelte, instalații de lucru, computere și echipamentele lor periferice — nu și construcții, nu și „orice alt mijloc fix" (mobilier, alte imobilizări).
- **Ritmul de deducere** — liniară: cotă constantă în fiecare an. Degresivă: deducere mai mare la început (cotă liniară × 1,5/2,0/2,5, în funcție de durată), care scade an de an. Accelerată: cea mai agresivă la început — până la 50% din valoare în primul an, restul liniar pe durata rămasă.
- **Fixarea metodei** — odată aleasă la intrarea în patrimoniu, metoda (și coeficientul degresiv, care depinde de durata stabilită atunci) nu se schimbă retroactiv pe parcursul amortizării.

Notă: pentru active noi puse în funcțiune în 2026, din subgrupele echipamente tehnologice (2.1) și animale/plantații (2.4), există temporar și o a patra metodă — **superaccelerata** (plafon 65% în primul an) — introdusă de OUG 8/2026 (CF art. 28 alin. (8^1)), separată de accelerata „obișnuită" de mai sus și limitată strict la fereastra 2026.

## Ce se greșește în practică

- Se alege accelerata pentru un mijloc fix din afara celor două categorii permise (de exemplu mobilier sau o construcție) — legea nu lasă alegerea liberă, doar echipamentele/computerele o pot folosi.
- Se compară metodele doar ca „mai rapidă" vs. „mai lentă", ignorând că degresivul are TREPTE fixe de coeficient (1,5/2,0/2,5) în funcție de durata normală de utilizare, nu un procent ales liber.
- Se presupune că metoda aleasă poate fi schimbată de la un an la altul, pentru a optimiza rezultatul fiscal — metoda se fixează la intrarea activului în patrimoniu.

## Ce face iConta.eu

Motorul de amortizare din `core/d406_active.py` verifică automat, pe fiecare mijloc fix, dacă metoda cerută e permisă pentru categoria lui de cont: construcțiile (212) acceptă doar liniar, echipamentele (2131) acceptă liniar/degresiv/accelerat, orice alt cont acceptă liniar/degresiv (fără accelerat), iar animalele/plantațiile (2134/217) acceptă și superaccelerata dacă activul a fost pus în funcțiune în 2026. Dacă se cere o metodă nepermisă, motorul refuză explicit calculul — nu calculează tacit pe liniar în locul metodei cerute. Coeficienții degresivi (1,5/2,0/2,5 pe treptele de durată) și plafonul de 50% al accelerării în primul an sunt implementați exact ca în text, iar motorul comută automat de la degresiv la liniar în anul în care liniarul devine mai avantajos — regulă standard de calcul, nu o opțiune separată de ales.

Acest motor e consumat de patru locuri din aplicație: fișa mijlocului fix, nota lunară de amortizare, casarea și reevaluarea unui activ, deci cifra de amortizare e aceeași, indiferent din ce ecran e privită.

[iConta.eu](/)
