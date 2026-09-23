---
title: "Ce cotă de TVA folosesc la taxarea inversă pentru o achiziție intracomunitară?"
description: Taxarea inversă schimbă cine calculează și înregistrează TVA, nu cota aplicabilă — se folosește aceeași cotă (standard sau redusă) pe care ar avea-o bunul sau serviciul respectiv la o achiziție internă, declarată explicit, fără o valoare implicită presupusă automat.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce cotă de TVA folosesc la taxarea inversă pentru o achiziție intracomunitară?

Taxarea inversă e o regulă despre **cine** calculează și înregistrează TVA — cumpărătorul, nu furnizorul —, nu despre **cât de mare** e cota. Cota aplicabilă la o achiziție intracomunitară e aceeași pe care ar avea-o bunul sau serviciul respectiv dacă ar fi fost cumpărat de la un furnizor din România: standard, pentru majoritatea bunurilor și serviciilor, sau redusă, pentru categoriile care beneficiază de ea conform regulilor generale.

## Temeiul legal

::: ghid-temei
HG 1/2016, norme la CF art. 331, pct. 109 alin. (1): „beneficiarul înregistrează… suma taxei aferente în următoarea formulă contabilă: 4426 = 4427. Prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă.”

— confirmat prin dosarul F050, `core/intracomunitar.py`
:::

**Notă de onestitate:** acest ghid nu citează articolul din Codul fiscal care stabilește nivelul exact al cotelor de TVA (standard/reduse) — dosarul de cercetare F050 (operațiuni intracomunitare) nu a extras verbatim acel text, fiind centrat pe mecanismul de taxare inversă, nu pe nivelul cotelor. Cota corectă pentru un bun sau serviciu concret se verifică separat, după regulile generale aplicabile oricărei operațiuni taxabile din România, aceleași reguli aplicându-se indiferent dacă achiziția e internă sau intracomunitară.

## Ce se greșește în practică

- Se presupune că taxarea inversă înseamnă automat cota standard, fără verificarea naturii bunului sau serviciului achiziționat.
- Se lasă cota "moștenită" dintr-o operațiune anterioară similară, fără verificare punctuală — riscant mai ales la schimbări legislative de cotă.
- Se aplică o cotă redusă doar pentru că bunul "pare" eligibil, fără confirmarea explicită a încadrării lui în categoriile care beneficiază de cotă redusă.

## Ce face iConta.eu

Motorul de calcul al taxării inverse (folosit la achizițiile intracomunitare de bunuri și servicii) **nu are o cotă de TVA implicită** — dacă nu e declarată explicit, calculul nu poate fi efectuat. Ecranul de achiziție intracomunitară afișează o sugestie de 21% în câmpul de cotă, dar aceasta e doar un ajutor vizual, nu o valoare aplicată automat — contabilul trebuie să confirme sau să schimbe cota pentru fiecare operațiune, exact pentru ca o cotă "scrisă undeva" să nu rămână desincronizată tacit de o eventuală schimbare legislativă.

[iConta.eu](/)
