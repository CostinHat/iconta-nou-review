---
title: "Cum se cumulează veniturile din salarii pentru plafoane 2026"
description: "Regula de cumulare a bazei lunare de calcul din mai multe contracte de muncă, folosită pentru a stabili dacă se aplică plafonul CAS/CASS la nivelul salariului minim în 2026."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se cumulează veniturile din salarii pentru plafoane 2026

Pentru salariile sub nivelul salariului minim brut pe țară, legea impune un „plafon minim" de contribuții sociale — CAS și CASS nu pot fi mai mici decât cele calculate la nivelul salariului minim, chiar dacă venitul brut real e mai mic. Regula are însă excepții, iar una dintre ele privește exact salariații cu mai multe contracte de muncă part-time: dacă veniturile lor cumulate de la toți angajatorii ating salariul minim, plafonul nu se mai aplică separat, la fiecare angajator.

## Temeiul legal

::: ghid-temei
„(5^6) Contribuția de asigurări sociale datorată de către persoanele fizice care obțin venituri din salarii sau asimilate salariilor, în baza unui contract individual de muncă cu normă întreagă sau cu timp parțial, calculată potrivit alin. (5), nu poate fi mai mică decât nivelul contribuției de asigurări sociale calculate prin aplicarea cotei prevăzute la art. 138 lit. a) asupra salariului de bază minim brut pe țară în vigoare în luna pentru care se datorează contribuția de asigurări sociale, corespunzător numărului zilelor lucrătoare din lună în care contractul a fost activ."
— Codul fiscal (Legea 227/2015), art. 146 alin. (5^6) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„(5^7) Prevederile alin. (5^6) nu se aplică în cazul persoanelor fizice aflate în una dintre următoarele situații: [...] e) realizează în cursul aceleiași luni venituri din salarii sau asimilate salariilor în baza a două sau mai multe contracte individuale de muncă, iar baza lunară de calcul cumulată aferentă acestora este cel puțin egală cu salariul de bază minim brut pe țară."
— Codul fiscal, art. 146 alin. (5^7) lit. e) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„(6^1) Prevederile art. 146 alin. (5^6)-(5^9) se aplică în mod corespunzător."
— Codul fiscal, art. 168 alin. (6^1) (CASS — sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cum funcționează, pas cu pas:

- **Regula de bază** (art. 146 alin. 5^6): dacă un salariat, cu normă întreagă sau cu timp parțial, are un venit brut mai mic decât salariul minim, angajatorul îi calculează CAS (și, prin trimitere, CASS — art. 168 alin. 6^1) **ca și cum** ar fi câștigat salariul minim, nu la venitul efectiv realizat.
- **Excepția pentru mai multe contracte** (art. 146 alin. 5^7 lit. e): dacă în aceeași lună salariatul are venituri din **două sau mai multe** contracte individuale de muncă, iar **suma bazelor lunare de calcul** de la toți angajatorii e cel puțin egală cu salariul minim, plafonul nu se mai aplică separat la fiecare angajator — fiecare plătește contribuții doar la venitul efectiv pe care îl acordă.
- **Alte excepții** din același alineat: elevi/studenți sub 26 de ani, ucenici sub 18 ani, persoane cu dizabilități care pot lucra mai puțin de 8 ore/zi, pensionari pentru limită de vârstă.
- Aplicarea excepției cere documente justificative din partea salariatului (art. 146 alin. 5^8) — pentru cazul „mai multe contracte", procedura se stabilește prin ordin al ministrului finanțelor și, în practică, se bazează pe declarația pe propria răspundere a salariatului, fiindcă niciun angajator nu are vizibilitate directă asupra contractelor de la celelalte firme.
- Salariul de bază minim brut pe țară în vigoare din 1 iulie 2026 este de **4.325 lei/lună** (HG 146/2026) — nivelul la care se raportează atât plafonul, cât și pragul cumulat din excepție.

## Ce se greșește în practică

- Se aplică suprataxarea la nivelul salariului minim și pentru salariați care lucrează cu normă parțială la doi sau mai mulți angajatori, fără să se verifice dacă baza cumulată de la toate contractele atinge deja salariul minim.
- Se presupune că angajatorul poate verifica singur cumulul — de fapt, fiecare angajator vede doar propriul contract; excepția se aplică pe baza declarației salariatului, nu a unei verificări automate încrucișate între angajatori.
- Se confundă plafonul CAS/CASS la salariul minim (art. 146/168 CF) cu facilitatea de scutire a primilor 300 lei din salariul minim (OUG 89/2025) — sunt două mecanisme diferite, cu condiții separate.

## Ce face iConta.eu

Motorul de salarizare (`core/salarizare.py`) calculează automat, pentru fiecare salariat, „suprataxarea sub salariul minim" descrisă mai sus: dacă baza de contribuții e sub salariul minim din luna respectivă, CAS și CASS se recalculează la nivelul podelei legale, proporțional cu zilele lucrate din contract. Excepția pentru cumul de contracte există în cod ca parametru dedicat (`exceptat_suprataxare`, populat din câmpul `scutit_contrib_minim` al salariatului), dar aplicarea lui rămâne **manuală**: contabilul bifează excepția pe baza declarației salariatului, fiindcă aplicația unei singure firme nu are acces la veniturile plătite de ceilalți angajatori și nu poate calcula singură cumulul real.

[iConta.eu](/)
