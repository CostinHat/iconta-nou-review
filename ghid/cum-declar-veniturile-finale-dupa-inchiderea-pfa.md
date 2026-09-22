---
title: Cum declar veniturile finale după închiderea PFA?
description: Sistemul real e pe bază de încasări efective, așa că orice sumă legată de activitate încasată în anul în care PFA a funcționat (chiar aproape de radiere) intră normal în venitul brut al acelui an, iar pragurile CAS/CASS rămân cele anuale, neprorate.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum declar veniturile finale după închiderea PFA?

Un PFA care își încetează activitatea în cursul anului tot depune D212 pentru anul respectiv, cu venitul net realizat efectiv până la data încetării. Pentru că sistemul real funcționează pe bază de încasări (nu pe facturare), tot ce a fost încasat efectiv legat de activitate în anul de venit — inclusiv sume încasate cu puțin timp înainte de radiere — intră în calcul normal, ca la orice alt PFA activ.

## Temeiul legal

::: ghid-temei
**Art. 68 alin.(2):** "Venitul brut cuprinde: a) sumele încasate și echivalentul în lei al veniturilor în natură din desfășurarea activității; b) veniturile sub formă de dobânzi din creanțe comerciale...; c) câștigurile din transferul activelor din patrimoniul afacerii...".

**Art. 151 alin.(2):** "Prevederile alin. (1), precum și cele ale art. 148 sunt aplicabile și în cazul contribuabililor care în cursul anului fiscal încep o activitate independentă și/sau încep să realizeze venituri din drepturi de proprietate intelectuală, precum și în cazul celor care intră în suspendare temporară a activității ... ori își încetează activitatea."

**Art. 151 alin.(3):** "baza anuală de calcul ... o reprezintă venitul ales ... care nu poate fi mai mic decât echivalentul salariului minim brut pe țară înmulțit cu numărul de luni calculat de la începutul anului ... până la luna în care contribuabilul se încadrează în categoria persoanelor exceptate."
:::

## Pragurile rămân anuale, nu se prorata la numărul de luni funcționate

Art. 151 alin. (3) prevede o proratare lunară, dar doar pentru situația specifică în care contribuabilul devine, în cursul anului, persoană exceptată de la plata CAS (art. 150) — nu pentru simpla încetare a activității. Asta înseamnă că pragurile de 12/24 salarii minime pentru CAS și de 6 salarii minime pentru CASS rămân valorile anuale întregi, indiferent dacă PFA a funcționat 2 luni sau 11 luni în anul respectiv.

::: ghid-exemplu
Un PFA radiat în luna aprilie 2025 a realizat un venit net de 55.000 lei până la radiere. Pragul CAS relevant tot este 12 salarii minime × 4.050 lei = 48.600 lei (nu proratat la 4 luni) — deci venitul net de 55.000 lei depășește pragul și CAS devine obligatorie, la bază de 12 salarii minime (48.600 lei), nu la bază proratată.
:::

## Ce se greșește în practică

- Se presupune că, pentru că PFA a funcționat doar câteva luni, pragurile de 12/24/6 salarii minime se împart proporțional — nu se întâmplă, cu excepția cazului specific al persoanelor exceptate de la CAS.
- Se omit sume încasate în ultimele săptămâni de activitate, pe motiv că "oricum s-a închis PFA-ul" — orice încasare validă legată de activitate, din anul de venit, intră în venitul brut.
- Se confundă data radierii cu data ultimei încasări — venitul brut se calculează pe tot anul fiscal, nu doar până la data radierii, dacă mai apar încasări legate de activitate ulterior în același an fiscal.
- Se declară cheltuielile deductibile doar până la radiere, deși unele cheltuieli plătite ulterior, dar aferente activității derulate, pot fi tot deductibile dacă îndeplinesc condițiile de justificare.

## Ce face iConta.eu

Motorul (`core/rip_api.py: fisa_d212`) însumează toate încasările validate cu categoria "activitate" din anul fiscal respectiv, indiferent de data exactă din lună — nu face distincție specială pentru operațiuni din perioada de dinaintea radierii. Calculul CAS și CASS (`core/d212_engine.py`) folosește pragurile anuale întregi (12/24 salarii minime pentru CAS, 6/60 sau 6/72 pentru CASS), fără nicio proratare la numărul de luni funcționate — ceea ce e conform art. 151 alin. (2)-(3), pentru că excepția de proratare se aplică doar persoanelor care devin exceptate de la CAS, nu simplei încetări de activitate.

[iConta.eu](/)
