---
title: "Un pensionar angajat plătește CAS?"
description: "Dacă un pensionar angajat cu contract individual de muncă datorează contribuția de asigurări sociale (CAS) pe salariu și ce excepție specială are față de contribuția minimă obligatorie."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Un pensionar angajat plătește CAS?

Da. Un pensionar care are un contract individual de muncă datorează contribuția de asigurări sociale (CAS) pe venitul din salarii, exact ca orice alt angajat — calitatea de pensionar nu scutește de CAS veniturile din salarii. Scutirea de CAS pentru pensionari, prevăzută de Codul fiscal, privește doar veniturile din activități independente și din drepturi de proprietate intelectuală, nu și salariul.

## Temeiul legal

::: ghid-temei
„Contribuabilii/Plătitorii de venit la sistemul public de pensii, prevăzuți la art. 136, datorează, după caz, contribuția de asigurări sociale pentru următoarele categorii de venituri realizate din România și din afara României [...]: a) venituri din salarii sau asimilate salariilor, definite conform art. 76; [...]
(Art. 150) (1) Persoanele fizice asigurate în sisteme proprii de asigurări sociale, care nu au obligația asigurării în sistemul public de pensii potrivit legii, precum și persoanele care au calitatea de pensionari nu datorează contribuția de asigurări sociale pentru veniturile prevăzute la art. 137 alin. (1) lit. b) și b^1)."
— Legea nr. 227/2015 (Codul fiscal), art. 137 alin. (1) lit. a) și art. 150 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Explicația mecanismului:

- Art. 137 alin. (1) enumeră categoriile de venituri supuse CAS: lit. a) venituri din salarii, lit. b) venituri din activități independente, lit. b^1) venituri din drepturi de proprietate intelectuală.
- Excepția pentru pensionari, de la art. 150 alin. (1), se referă **explicit doar** la veniturile de la lit. b) și b^1) — adică la activitățile independente (de exemplu, un pensionar PFA) și la drepturile de proprietate intelectuală. Veniturile din salarii, de la lit. a), **nu sunt incluse** în excepție.
- Există, totuși, o particularitate specifică pensionarilor angajați: potrivit art. 146 alin. (5^6)-(5^7) lit. d) din Codul fiscal, CAS calculată pe un salariu redus (de exemplu, la un contract cu timp parțial) nu poate fi mai mică decât CAS calculată la nivelul salariului minim brut pe țară — cu excepția, printre altele, a **pensionarilor pentru limită de vârstă** din sistemul public de pensii (cu unele excluderi, precum pensiile de serviciu speciale). Practic, pensionarul-angajat plătește CAS pe salariul efectiv realizat, fără să fie „ridicat" artificial la nivelul contribuției minime calculate la salariul minim pe economie, cum se întâmplă la ceilalți salariați cu normă parțială și venit redus.

## Ce se greșește în practică

- Se confundă scutirea de CAS pentru activități independente/drepturi de autor a pensionarilor (art. 150) cu o presupusă scutire generală de CAS pentru orice venit al unui pensionar, inclusiv salariul.
- Se aplică totuși contribuția minimă obligatorie (la nivelul salariului minim) și la salariile pensionarilor cu normă parțială, deși aceștia sunt expres exceptați de la art. 146 alin. (5^7) lit. d).
- Se omite solicitarea documentului justificativ (dovada calității de pensionar pentru limită de vârstă) cerut de art. 146 alin. (5^8) pentru a aplica excepția de la suprataxare.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează corect CAS pentru salariații pensionari ca pentru orice alt angajat, pe baza salariului brut introdus. În plus, modulul de salarizare (`core/salarizare.py`, funcția de calcul salariu) are un parametru dedicat `exceptat_suprataxare`, prin care contabilul poate marca un salariat aflat în una din situațiile de la art. 146 alin. (5^7) din Codul fiscal — printre care „elev/student <26, pensionar, multi-contract cu declarație" — astfel încât aplicația nu mai ridică artificial contribuția de asigurări sociale la nivelul corespunzător salariului minim brut pe țară, ci o calculează la salariul efectiv realizat.

[iConta.eu](/)
