---
title: Cum calculez taxele pentru un PFA înființat în cursul anului?
description: Pragurile de 12/24 salarii minime pentru CAS și de 6 salarii minime pentru CASS rămân valorile anuale întregi și pentru un PFA înființat în cursul anului — legea nu prevede proratare lunară pentru simplul început de activitate.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum calculez taxele pentru un PFA înființat în cursul anului?

O confuzie frecventă: un PFA înființat, de exemplu, în septembrie crede că pragurile de la care devin obligatorii CAS și CASS se împart proporțional cu numărul de luni de activitate din anul respectiv. Legea nu prevede acest lucru pentru simplul început de activitate — pragurile rămân cele anuale întregi.

## Temeiul legal

::: ghid-temei
**Art. 151 alin.(2):** "Prevederile alin. (1), precum și cele ale art. 148 sunt aplicabile și în cazul contribuabililor care în cursul anului fiscal încep o activitate independentă și/sau încep să realizeze venituri din drepturi de proprietate intelectuală, precum și în cazul celor care intră în suspendare temporară a activității ... ori își încetează activitatea."

**Art. 151 alin.(3):** "baza anuală de calcul ... o reprezintă venitul ales ... care nu poate fi mai mic decât echivalentul salariului minim brut pe țară înmulțit cu numărul de luni calculat de la începutul anului ... până la luna în care contribuabilul se încadrează în categoria persoanelor exceptate."
:::

## Excepția de proratare e limitată la un singur caz

Art. 151 alin. (3) prevede o proratare lunară, dar strict pentru situația unei persoane care, în cursul anului, devine exceptată de la plata CAS (art. 150) — de exemplu cineva care se angajează și obține statutul de persoană exceptată. Pentru simplul început de activitate al unui PFA nou-înființat, alin. (2) spune clar că regulile de la art. 148 (și, prin extensie, pragurile echivalente de la art. 170 pentru CASS) se aplică "și" în acest caz — adică fără nicio ajustare specială. Pragurile rămân cele anuale: 12 și 24 de salarii minime pentru CAS, 6 salarii minime pentru CASS.

::: ghid-exemplu
Un PFA înființat în septembrie 2025 realizează, în cele 4 luni rămase din an, un venit net de 55.000 lei. Cu salariul minim de referință 4.050 lei, pragul de 12 salarii minime este tot 48.600 lei (nu proratat la 4/12 din an) — deci venitul de 55.000 lei depășește pragul, iar CAS devine obligatorie, la bază de 48.600 lei.
:::

## Ce se greșește în practică

- Se împarte pragul de 12 salarii minime la numărul de luni de activitate, calculând greșit un prag proporțional mai mic.
- Se presupune, invers, că un PFA înființat spre finalul anului e automat scutit de CAS/CASS pentru că "nu a lucrat tot anul" — dacă venitul net cumulat trece pragul anual, obligația există integral.
- Se confundă excepția de proratare de la art. 151 alin. (3) (specifică persoanelor exceptate de la CAS) cu o regulă generală valabilă pentru orice PFA nou.
- Se declară venitul net doar pentru "lunile funcționate", deși ce contează e suma efectiv încasată în anul fiscal respectiv, indiferent în câte luni a fost realizată.

## Ce face iConta.eu

Motorul de calcul (`core/d212_engine.py`) nu ajustează pragurile de 12/24 salarii minime (CAS) sau de 6 salarii minime (CASS) în funcție de câte luni a funcționat PFA în anul respectiv — le aplică integral, la valoarea anuală. Acest comportament e conform art. 151 alin. (2): excepția de proratare din alin. (3) se aplică doar situației specifice a persoanelor care devin exceptate de la CAS în cursul anului, nu simplului început de activitate. Venitul brut folosit în calcul e suma tuturor încasărilor validate din anul fiscal, indiferent de luna în care au avut loc.

[iConta.eu](/)
