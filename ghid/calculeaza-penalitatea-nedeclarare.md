---
title: "Cum se calculează penalitatea de nedeclarare?"
description: "Cum se calculează penalitatea de nedeclarare de 0,08% pe zi aplicată de ANAF pentru obligații fiscale nedeclarate sau declarate incorect, stabilite prin decizie de impunere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează penalitatea de nedeclarare?

Penalitatea de nedeclarare nu e aceeași cu penalitatea de întârziere — se aplică într-un caz specific: când o obligație fiscală principală nu a fost declarată deloc sau a fost declarată incorect, iar organul fiscal o stabilește ulterior printr-o decizie de impunere.

## Temeiul legal

::: ghid-temei
„Pentru obligațiile fiscale principale nedeclarate sau declarate incorect de contribuabil/plătitor și stabilite de organul fiscal prin decizii de impunere, contribuabilul/plătitorul datorează o penalitate de nedeclarare de 0,08% pe fiecare zi, începând cu ziua imediat următoare scadenței și până la data stingerii sumei datorate, inclusiv, din obligațiile fiscale principale nedeclarate sau declarate incorect de contribuabil/plătitor și stabilite de organul fiscal prin decizii de impunere."
— Legea 207/2015 (Codul de procedură fiscală), art. 181 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce presupune, mecanic, calculul:

- Baza de calcul e obligația fiscală principală nedeclarată sau declarată greșit, **stabilită de organul fiscal** — nu suma pe care contribuabilul crede că ar fi trebuit s-o declare, ci cea confirmată prin decizie de impunere.
- Rata e de 0,08% pe zi, calculată de la ziua imediat următoare scadenței inițiale și până la stingerea efectivă a sumei — perioada poate fi lungă dacă decizia de impunere vine la mult timp după scadență.
- Penalitatea de nedeclarare se aplică **în locul** penalității de întârziere obișnuite pentru sumele respective — cele două nu se cumulează pe aceeași sumă, spre deosebire de dobândă și penalitatea de întârziere, care se cumulează între ele.

## Ce se greșește în practică

- Se plătește doar impozitul suplimentar stabilit de inspector, fără penalitatea de nedeclarare aferentă — aceasta se calculează automat de organul fiscal pe toată perioada de la scadență.
- Se confundă cu penalitatea de întârziere (0,01%/zi) — rata e de 8 ori mai mare tocmai pentru că sancționează nedeclararea, nu doar plata cu întârziere a unei sume corect raportate.
- Se depune o declarație rectificativă chiar înainte de un control anunțat, sperând să evite penalitatea — legea prevede reduceri ale penalității de nedeclarare doar în condiții specifice de corectare din proprie inițiativă, nu o eliminare automată.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu calculează penalitatea de nedeclarare — aceasta se stabilește exclusiv de organul fiscal, prin decizie de impunere, ca urmare a unui control sau a unei verificări. Aplicația oferă evidența contabilă generală și motorul de urmărire a declarațiilor datorate (`core/control_fiscal_api.py`), care ajută la identificarea declarațiilor lipsă înainte ca acestea să devină obiectul unei decizii de impunere, dar nu simulează accesoriile pe care ANAF le-ar calcula într-un astfel de caz.

[iConta.eu](/)
