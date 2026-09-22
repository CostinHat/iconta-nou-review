---
title: Cum se calculează salariul pentru 4 ore pe zi în 2026?
description: Contractul cu timp parțial (de exemplu 4 ore/zi) nu este scutit automat de regula CAS/CASS minim garantat - dacă venitul brut realizat e sub pragul minim proporțional, se aplică suprataxare, cu excepția a cinci categorii prevăzute expres de lege.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se calculează salariul pentru 4 ore pe zi în 2026?

Un contract cu normă parțială, de exemplu 4 ore pe zi, se calculează după aceleași reguli de bază (CAS, CASS, impozit, deducere) ca un contract cu normă întreagă, dar există o regulă suplimentară importantă: dacă venitul brut realizat este sub un anumit prag minim, angajatorul trebuie să suporte o contribuție de asigurări sociale suplimentară — regulă care se aplică inclusiv contractelor cu timp parțial, nu doar celor cu normă întreagă.

## Temeiul legal

::: ghid-temei
**Codul fiscal, Articolul 146, alin.(5^6):** *"Contribuția de asigurări sociale datorată de către persoanele fizice care obțin venituri din salarii sau asimilate salariilor, în baza unui contract individual de muncă cu normă întreagă sau cu timp parțial, calculată potrivit alin. (5), nu poate fi mai mică decât nivelul contribuției de asigurări sociale calculate prin aplicarea cotei prevăzute la art. 138 lit. a) asupra salariului de bază minim brut pe țară în vigoare în luna pentru care se datorează contribuția de asigurări sociale, corespunzător numărului zilelor lucrătoare din lună în care contractul a fost activ."*
:::

## Cum funcționează suprataxarea la timp parțial

Legea nu leagă suprataxarea de tipul de normă (întreagă sau parțială), ci de nivelul VENITULUI realizat. Practic: dacă venitul brut lunar al unui salariat cu 4 ore/zi este sub nivelul salariului minim brut pe țară proporțional cu zilele lucrătoare active din lună, contribuția de asigurări sociale (CAS) nu poate fi mai mică decât cea calculată la cota de 25% aplicată salariului minim brut, proporțional cu perioada activă a contractului în lună. Diferența este suportată de angajator, nu se scade din salariul net al angajatului.

Există însă cinci categorii de salariați exceptate expres de la această regulă, prevăzute de Codul fiscal, art.146 alin.(5^7):

- elevi și studenți cu vârsta sub 26 de ani, aflați în școlarizare;
- ucenici cu vârsta sub 18 ani;
- persoane cu dizabilități sau alte categorii pentru care legea prevede un program de lucru redus sub 8 ore/zi;
- pensionari pentru limită de vârstă (cu excepțiile prevăzute de lege);
- salariați cu venituri cumulate din 2 sau mai multe contracte, a căror bază însumată atinge nivelul salariului minim.

::: ghid-exemplu
Un salariat cu 4 ore/zi (jumătate de normă) are un venit brut lunar contractual de 2.162,5 lei, adică jumătate din salariul minim de 4.325 lei. Dacă acest nivel corespunde exact proporției de 4 ore din 8 ore, iar salariatul nu se încadrează în niciuna dintre cele 5 categorii exceptate, CAS nu se calculează la 2.162,5 lei, ci la nivelul minim garantat — proporțional cu zilele lucrătoare active ale contractului în lună — diferența fiind suportată de angajator.
:::

## Ce se greșește în practică

- Se presupune că un contract cu timp parțial este automat scutit de regula suprataxării, pentru simplul fapt că nu are normă întreagă — legea vizează explicit ambele situații ("normă întreagă SAU timp parțial").
- Se aplică suprataxarea și salariaților din categoriile exceptate expres de lege (elevi, studenți, ucenici, persoane cu dizabilități, pensionari, multi-contract), fără verificarea încadrării în una din cele cinci categorii.
- Se scade diferența de CAS din salariul net al angajatului, deși legea prevede că suprataxarea este suportată de angajator, nu de salariat.
- Se calculează proporția salariului minim pe zile calendaristice, în loc de zilele lucrătoare active ale contractului în lună.
- Se ignoră una sau mai multe dintre cele cinci categorii de excepție, aplicând mecanic doar 2-3 dintre ele (de exemplu doar elevi/studenți și pensionari, omițând ucenicii, persoanele cu dizabilități sau situația multi-contract).

## Ce face iConta.eu

Motorul de calcul verifică, pentru fiecare contract, dacă baza de contribuție (venitul brut, redus eventual de facilitatea salariului minim) este sub pragul minim proporțional — calculat pe zilele lucrătoare active ale contractului în luna respectivă, nu pe zile calendaristice. Dacă da, se calculează și se evidențiază separat suprataxarea (CAS/CASS suplimentare, suportate de angajator, care NU se scad din salariul net al angajatului). Aplicația expune un singur parametru boolean pentru exceptarea de la suprataxare, decizia încadrării într-una dintre cele cinci categorii legale rămânând responsabilitatea celui care introduce datele contractului.

[iConta.eu](/)
