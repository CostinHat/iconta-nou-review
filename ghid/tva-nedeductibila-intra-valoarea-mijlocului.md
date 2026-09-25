---
title: "TVA nedeductibilă intră în valoarea mijlocului fix?"
description: "Regula contabilă care spune când taxa pe valoarea adăugată nerecuperabilă se adaugă la costul de achiziție al unui mijloc fix, în loc să rămână o cheltuială separată."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# TVA nedeductibilă intră în valoarea mijlocului fix?

Da. Când TVA aferentă achiziției unui mijloc fix nu poate fi recuperată de la buget (firmă neplătitoare, achiziție cu drept de deducere limitat sau exclus), acea taxă nu rămâne o cheltuială separată — se adaugă la costul de achiziție al activului și se amortizează împreună cu el.

## Temeiul legal

::: ghid-temei
„6. cost de achiziție înseamnă prețul datorat și eventualele cheltuieli conexe minus eventualele reduceri ale costului de achiziție. În acest sens, costul de achiziție al bunurilor cuprinde prețul de cumpărare, taxele de import și alte taxe (cu excepția acelora pe care persoana juridică le poate recupera de la autoritățile fiscale), cheltuielile de transport, manipulare și alte cheltuieli care pot fi atribuibile direct achiziției bunurilor respective. În costul de achiziție se includ, de asemenea, comisioanele, taxele notariale, cheltuielile cu obținerea de autorizații și alte cheltuieli nerecuperabile, atribuibile direct bunurilor respective."
— OMFP 1802/2014, pct. 8 subpct. 6 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Regula, aplicată la un mijloc fix:

- Costul de achiziție cuprinde prețul de cumpărare plus „taxele [...] cu excepția acelora pe care persoana juridică le poate **recupera** de la autoritățile fiscale". TVA e, prin natura ei, recuperabilă — dar numai când există drept de deducere.
- Când dreptul de deducere lipsește sau e limitat (firmă neplătitoare de TVA, vehicul cu deducere plafonată la 50%, achiziție pentru care legea exclude deducerea), taxa devine, pentru acea firmă, **nerecuperabilă** — și intră direct în costul de achiziție al mijlocului fix, alături de prețul de cumpărare și cheltuielile conexe (transport, montaj, comisioane, autorizații).
- Practic, TVA nedeductibilă nu se înregistrează separat pe un cont de cheltuială (635 sau echivalent) când e legată de un mijloc fix — se capitalizează în valoarea activului (contul de imobilizare) și se recuperează fiscal treptat, prin amortizare, nu dintr-o dată.

## Ce se greșește în practică

- Se înregistrează TVA nedeductibilă direct pe cheltuieli de exploatare (de exemplu contul 635), în loc să se includă în valoarea de intrare a mijlocului fix — rezultatul e o cheltuială integral deductibilă imediat, în loc de una recuperată treptat prin amortizare (și, la vehicule, plafonată la 1.500 lei/lună).
- Se presupune că doar firmele neplătitoare de TVA capitalizează taxa nedeductibilă — regula se aplică oricărei situații în care deducerea e limitată, inclusiv la o firmă plătitoare de TVA care cumpără un autoturism cu deducere de doar 50%, pentru partea nededusă.
- Se omite includerea în cost a taxei nedeductibile aferente cheltuielilor conexe achiziției (transport, montaj), nu doar a celei aferente prețului bunului în sine.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu calculează și nu include automat** TVA nedeductibilă în valoarea de intrare a unui mijloc fix — nu am găsit în cod o funcție dedicată acestui calcul în modulele de mijloace fixe. Aplicația oferă evidența contabilă generală (jurnal, fișă de cont, registrul mijloacelor fixe), în care contabilul stabilește manual valoarea de intrare a activului, inclusiv componenta de TVA nedeductibilă, atunci când situația o cere.

[iConta.eu](/)
