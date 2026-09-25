---
title: "Ce se consideră mijloc fix și ce se consideră obiect de inventar"
description: "Cele trei condiții cumulative din Codul fiscal care separă mijlocul fix amortizabil de obiectul de inventar, cu pragul valoric actualizat din 2026."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce se consideră mijloc fix și ce se consideră obiect de inventar

Distincția dintre mijloc fix și obiect de inventar nu ține de cât de „important" pare un bun, ci de trei condiții legale precise, care trebuie îndeplinite **toate odată**. Dacă lipsește măcar una, bunul nu poate fi mijloc fix — și, în practică, ajunge înregistrat ca obiect de inventar, pe contul 303.

## Temeiul legal

::: ghid-temei
„(2) Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții: a) este deținut și utilizat în producția, livrarea de bunuri sau în prestarea de servicii, pentru a fi închiriat terților sau în scopuri administrative; [...] b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei; această limită se actualizată anual, în funcție de indicele de inflație, prin hotărâre a Guvernului; [...] c) are o durată normală de utilizare mai mare de un an."
— Codul fiscal (Legea 227/2015), art. 28 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

Cele trei condiții, desfăcute:

- **a) Destinația** — bunul trebuie folosit efectiv în activitatea entității (producție, livrare, servicii, închiriere către terți) sau administrativ, nu deținut fără scop.
- **b) Valoarea** — la data intrării în patrimoniu, valoarea fiscală trebuie să fie **cel puțin egală** cu pragul legal. Pragul e **5.000 lei din 25.02.2026** (modificat prin OUG 8/2026 art. 6 pct. 7), anterior fiind **2.500 lei** (HG 276/2013).
- **c) Durata** — durata normală de utilizare trebuie să fie **mai mare de un an**. Un bun cu durată sub un an nu e mijloc fix **indiferent de cât de scump e**.

Un bun care nu îndeplinește oricare dintre cele trei condiții — cel mai adesea pentru că valoarea e sub prag sau durata e sub un an — e tratat contabil ca **obiect de inventar**: nu se amortizează, ci se trece integral pe cheltuială la darea în folosință (cont 603), cu o evidență extracontabilă separată (contul 8035) până la scoaterea din uz.

## Ce se greșește în practică

- Se verifică doar valoarea (condiția b) și se ignoră complet condiția duratei (c) — un bun scump, dar cu durată de utilizare sub un an, nu e mijloc fix, oricât ar costa.
- Se aplică pragul vechi de 2.500 lei după 25.02.2026, sau invers, pragul nou pentru achiziții făcute înainte de această dată.
- Se presupune că „obiect de inventar" înseamnă automat „bun ieftin sau mărunt" — de fapt criteriul legal e strict cumulativ, nu o apreciere subiectivă.
- Se uită regimul tranzitoriu: mijloacele fixe deja existente la 31.12.2025 cu valoare între 2.500 și 5.000 lei **nu se reclasifică** drept obiecte de inventar — ele continuă să se amortizeze pe durata rămasă (Codul fiscal art. 45 alin. 21^3).

## Ce face iConta.eu

iConta.eu implementează în motorul obiectelor de inventar (`core/obiecte_inventar.py`) exact criteriul din lege: verifică dacă valoarea bunului e sub pragul valabil la data operațiunii **sau** dacă durata de utilizare declarată e sub un an — oricare din cele două condiții e suficientă pentru încadrarea ca obiect de inventar. Pragul e citit dintr-un registru unic de cote, sensibil la dată (5.000 lei din 25.02.2026, 2.500 lei anterior), astfel încât o achiziție veche și una recentă sunt evaluate corect, fiecare cu pragul din perioada ei.

De reținut: formularul „Obiecte de inventar (303)" din ecranul „Operațiuni speciale" verifică automat doar criteriul de **valoare**. Câmpul pentru durata de utilizare sub un an există în motorul de calcul și e testat unitar, dar **nu apare încă în formularul din interfață** — deci, pentru moment, o achiziție peste prag cu durată reală sub un an nu poate fi înregistrată corect ca obiect de inventar direct din acest ecran.

[iConta.eu](/)
