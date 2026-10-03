---
title: "Cum declar în D212 dacă am PFA și venituri din chirii?"
description: "PFA-ul și chiriile se completează în D212 ca surse separate, în cadrul unor categorii diferite de venit — iar chiriile nu intră în cumulul care declanșează CAS, ci doar în cel pentru CASS."
published: 2026-09-26
modified: 2026-10-03
poarta: v1
---

# Cum declar în D212 dacă am PFA și venituri din chirii?

D212 nu obligă la alegerea între cele două surse — se completează amândouă, în secțiuni distincte ale aceleiași declarații, iar tratamentul fiscal al fiecăreia rămâne separat, chiar dacă rezultatul final apare pe același formular.

## Temeiul legal

::: ghid-temei
„Declarația unică privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice se completează pentru fiecare sursă din cadrul fiecărei categorii de venit, indiferent de modalitatea de determinare a venitului net anual/câștigului net anual, după caz, în vederea stabilirii și declarării impozitului pe venit, respectiv a pierderii fiscale anuale."
— Codul fiscal (Legea 227/2015), art. 122 alin. (4) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă practic pentru cele două surse:

- Venitul din PFA (categoria „activități independente", art. 122 alin. (1) lit. a)) și venitul din chirii (categoria „cedarea folosinței bunurilor", lit. c)) sunt categorii de venit distincte — fiecare cu regulile ei proprii de determinare a venitului net și fiecare cu impozitul calculat separat.
- Chiriile NU intră în cumulul care stabilește obligația de CAS (art. 148 alin. (3)) — acel cumul privește exclusiv activități independente, activitate sportivă și drepturi de proprietate intelectuală.
- Chiriile intră însă în cumulul separat pentru CASS pe venituri pasive (art. 170 alin. (4) lit. c)), alături de dividende, dobânzi și alte surse similare, cu plafonare pe trepte de 6/12/24 salarii minime brute — un cumul complet diferit de cel al CASS pe activități independente.
- Un contribuabil poate ajunge astfel să datoreze CAS/CASS pe PFA (calculat pe cumulul de activități independente) ȘI, separat, CASS pe chirii (calculat pe cumulul de venituri pasive) — cele două nu se anulează și nu se substituie una pe alta.

## Ce se greșește în practică

- Se însumează venitul din PFA cu cel din chirii într-un singur total, pentru a verifica un singur prag CAS/CASS — cele două categorii au cumuluri separate, cu praguri și reguli proprii.
- Se omite complet declararea chiriilor în D212, considerând că impozitul reținut (dacă plătitorul e persoană juridică) acoperă toată obligația — regula se aplică doar chiriilor plătite de persoane juridice care conduc contabilitate, nu tuturor.
- Se calculează CAS pe suma PFA + chirii, deși chiriile nu fac parte din categoria de venituri supuse cumulului pentru CAS.

## Ce face iConta.eu

D212 se generează în iConta.eu (`core/d212.py`) cu mai multe capitole de venit deodată: activitatea independentă, preluată din Registrul-jurnal de încasări și plăți, și — în lista „Alte venituri” a formularului — chiriile, pentru care aplicația aplică cota forfetară de cheltuieli de 20% și impozitul de 10%. Fișa D212 (`core/rip_api.py`, `fisa_d212`) rămâne doar pentru venitul din PFA.

Declarația calculează contribuțiile pe cumulurile lor distincte: CAS pe activitatea independentă, CASS pe activitatea independentă și, separat, CASS pe chirii și celelalte venituri de aceeași natură, pe trepte de 6, 12 sau 24 de salarii minime. Contabilul verifică datele introduse (contractele, sumele).

[iConta.eu](/)
