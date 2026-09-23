---
title: "Când este deductibilă deprecierea creanțelor?"
description: "Condițiile cumulative în care ajustarea pentru deprecierea unei creanțe este deductibilă fiscal, 30% sau 100%."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când este deductibilă deprecierea creanțelor?

Ajustarea pentru deprecierea unei creanțe nu este automat deductibilă fiscal — depinde de vechimea creanței, de garantare, de afiliere și de starea juridică a debitorului.

## Temeiul legal

::: ghid-temei
„ajustările pentru deprecierea creanțelor […] în limita unui procent de 30% din valoarea acestor ajustări […] dacă creanțele îndeplinesc cumulativ următoarele condiții: 1. sunt neîncasate într-o perioadă ce depășește 270 de zile de la data scadenței; […] 2. nu sunt garantate de altă persoană; […] 3. sunt datorate de o persoană care nu este persoană afiliată contribuabilului” — Cod fiscal, art. 26 alin. (1) lit. c)
:::

::: ghid-temei
„ajustările pentru deprecierea creanțelor […] în limita unui procent de 100% din valoarea creanțelor […] dacă creanțele îndeplinesc cumulativ următoarele condiții: 1. sunt deținute la o persoană juridică asupra căreia este declarată procedura de deschidere a falimentului, pe baza hotărârii judecătorești prin care se atestă această situație, sau la o persoană fizică asupra căreia este deschisă procedura de insolvență […] 2. nu sunt garantate de altă persoană; 3. sunt datorate de o persoană care nu este persoană afiliată contribuabilului” — Cod fiscal, art. 26 alin. (1) lit. j)
:::

Legea distinge două praguri de deductibilitate, ambele condiționate de neîndeplinirea garantării și a afilierii cu debitorul: 30% din valoarea ajustării, dacă au trecut peste 270 de zile de la scadență; 100%, dacă debitorul (persoană juridică) are declarat falimentul printr-o hotărâre judecătorească, sau (persoană fizică) are deschisă procedura de insolvență. În orice altă situație — creanță garantată, debitor afiliat, sau creanță neajunsă încă la 270 de zile de întârziere — ajustarea nu este deductibilă.

## Ce se greșește în practică

Greșeala tipică este aplicarea automată a procentului de 30% pentru orice creanță restantă de peste 270 de zile, fără verificarea celorlalte două condiții cumulative (creanța să nu fie garantată, iar debitorul să nu fie afiliat) — sau deducerea integrală de 100% fără dovada declarării efective a falimentului ori a insolvenței.

## Ce face iConta.eu

Motorul F071 calculează automat procentul deductibil, pe baza datelor introduse (zile de întârziere față de scadență, dacă creanța e garantată, dacă debitorul e afiliat, dacă falimentul/insolvența e declarat(ă)): 0% dacă creanța este garantată sau debitorul este afiliat; 100% dacă este declarat falimentul sau insolvența; 30% dacă au trecut peste 270 de zile de la scadență, în celelalte cazuri; 0% dacă termenul de 270 de zile nu a trecut încă.

[iConta.eu](/)
