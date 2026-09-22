---
title: Cum se calculează salariul minim pentru un angajat part-time?
description: Salariul minim se proratează pe fereastra activă a contractului în lună, iar facilitatea de 200/300 lei se acordă doar dacă salariul de bază contractual este egal cu salariul minim și sunt îndeplinite cumulativ toate condițiile din lege.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se calculează salariul minim pentru un angajat part-time?

Pentru un contract cu timp parțial, salariul minim brut pe țară nu se aplică ca valoare fixă, ci proporțional cu norma de lucru și cu perioada activă a contractului în lună. Dacă venitul realizat scade sub acest nivel proporțional, se aplică o regulă de suprataxare, iar facilitatea de 200/300 lei pentru salariul minim are propriile condiții stricte.

## Temeiul legal

::: ghid-temei
**Codul fiscal, Articolul 146, alin.(5^6):** *"Contribuția de asigurări sociale datorată de către persoanele fizice care obțin venituri din salarii sau asimilate salariilor, în baza unui contract individual de muncă cu normă întreagă sau cu timp parțial, calculată potrivit alin. (5), nu poate fi mai mică decât nivelul contribuției de asigurări sociale calculate prin aplicarea cotei prevăzute la art. 138 lit. a) asupra salariului de bază minim brut pe țară în vigoare în luna pentru care se datorează contribuția de asigurări sociale, corespunzător numărului zilelor lucrătoare din lună în care contractul a fost activ."*

**OUG 89/2025, Articolul III, alin.(1):** *"...pentru suma de 300 lei/lună din veniturile din salarii... aferente perioadei 1 ianuarie-30 iunie 2026, respectiv pentru suma de 200 lei/lună... aferente perioadei 1 iulie-31 decembrie 2026, nu se datorează impozit pe venit și contribuții sociale obligatorii dacă sunt îndeplinite cumulativ următoarele condiții: a) nivelul salariului de bază brut lunar stabilit potrivit contractului individual de muncă, fără a include sporuri și alte adaosuri, este egal cu nivelul salariului minim brut pe țară...; b) venitul brut realizat din salarii... fără a include contravaloarea tichetelor de masă, voucherelor de vacanță, respectiv indemnizația de hrană... nu depășește nivelul de 4.300 lei inclusiv în perioada... 1 ianuarie 2026-30 iunie 2026, respectiv nivelul de 4.600 lei inclusiv în perioada... 1 iulie 2026-31 decembrie 2026."*

**OUG 89/2025, Articolul III, alin.(4):** *"Suma de 300 lei, respectiv suma de 200 lei... se diminuează în funcție de: a) perioada din lună în care salariul de bază... este menținut(ă) la nivelul salariului minim...; b) data de la care angajații noi sunt încadrați...; c) fracția din lună...; d) data de la care încetează contractul..."*
:::

## Cum se aplică practic pentru un contract part-time

Pentru un contract cu timp parțial, salariul de bază contractual este de obicei mai mic decât salariul minim brut pe țară — proporțional cu norma lucrată. Acest lucru este normal și nu declanșează automat nicio problemă. Regula de suprataxare intervine doar dacă VENITUL realizat este sub pragul minim proporțional cu zilele lucrătoare active ale contractului în lună, calculat prin aplicarea cotei CAS (25%) asupra salariului minim brut, proporțional cu perioada activă. Diferența, dacă apare, este suportată de angajator, nu de salariat.

Există însă cinci categorii de salariați exceptate expres de la regula de suprataxare, prevăzute de Codul fiscal, art.146 alin.(5^7) — relevante mai ales pentru contractele part-time, unde riscul de suprataxare e cel mai frecvent:

- elevi și studenți cu vârsta sub 26 de ani, aflați în școlarizare;
- ucenici cu vârsta sub 18 ani;
- persoane cu dizabilități sau alte categorii pentru care legea prevede un program de lucru redus sub 8 ore/zi;
- pensionari pentru limită de vârstă (cu excepțiile prevăzute de lege);
- salariați cu venituri cumulate din 2 sau mai multe contracte, a căror bază însumată atinge nivelul salariului minim.

Facilitatea de 200/300 lei/lună are condiții mult mai stricte decât regula de suprataxare: se acordă doar dacă salariul de bază CONTRACTUAL (nu venitul proporțional cu ore reduse) este EGAL cu nivelul salariului minim brut pe țară, angajatul lucrează cu funcție de bază, iar venitul brut total nu depășește plafonul aferent perioadei (4.300 lei pentru ianuarie-iunie 2026, 4.600 lei pentru iulie-decembrie 2026). Pentru un contract part-time cu salariu de bază redus proporțional cu norma (nu la nivelul integral al salariului minim), această facilitate specifică nu se aplică, decât dacă salariul de bază contractual în sine este stabilit la nivelul salariului minim (situație posibilă, dar diferită de simpla proporționalitate a orelor lucrate).

Suma facilității se proratează, conform legii, în funcție de: perioada din lună în care salariul de bază e menținut la nivelul salariului minim, data angajării pentru angajați noi, fracția din lună lucrată și data încetării contractului.

::: ghid-exemplu
Un angajat cu 4 ore/zi are salariul de bază contractual stabilit exact la nivelul salariului minim orar corespunzător (deci salariul minim brut pe țară, proporțional cu norma). Dacă venitul brut lunar realizat nu depășește 4.600 lei (H2 2026) și celelalte condiții cumulative sunt îndeplinite, poate beneficia de facilitatea de 200 lei/lună, proporțional cu perioada activă din lună.
:::

## Ce se greșește în practică

- Se aplică facilitatea de 200/300 lei automat oricărui contract part-time, fără verificarea condiției ca salariul de bază contractual să fie EGAL cu salariul minim (nu doar proporțional cu norma redusă).
- Se calculează pragul de suprataxare pe zile calendaristice, în loc de zilele lucrătoare active ale contractului în lună.
- Se ignoră proratarea facilității în funcție de fracția din lună lucrată, data angajării sau data încetării contractului.
- Se scade eventuala suprataxare din salariul net al angajatului, deși legea prevede că este suportată de angajator.

## Ce face iConta.eu

Motorul de calcul determină baza de suprataxare (baza_podea) ca salariul minim minus facilitatea aplicabilă, proratată pe fereastra activă a contractului în lună, și compară venitul brut realizat cu acest prag. Dacă venitul e sub prag, calculează suplimentar CAS/CASS suportate de angajator, evidențiate separat, fără să afecteze salariul net al angajatului. Pentru facilitatea de 200/300 lei, aplicația verifică cele patru condiții cumulative din lege (nivel salariu de bază egal cu minimul, funcție de bază, venit brut total sub plafonul perioadei) și aplică proratarea prevăzută explicit de lege pentru fracția de lună activă a contractului.

[iConta.eu](/)
