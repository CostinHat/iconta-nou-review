---
title: Ce greșeli apar la ajustările de depreciere a creanțelor?
description: Cele mai frecvente greșeli sunt ignorarea condiției de negarantare/neafiliere, confuzia dintre pragul de 270 de zile de la scadență (impozit pe profit) și pragurile de TVA, și aplicarea procentului greșit de deducere (30% vs. 100%).
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce greșeli apar la ajustările de depreciere a creanțelor?

Regimul fiscal al ajustărilor pentru deprecierea creanțelor (CF art. 26 alin. (1) lit. c) și j)) pare simplu la prima vedere — un procent și un termen — dar are trei condiții cumulative, două praguri diferite de deducere și o dată de aplicabilitate care contează. Cele mai frecvente greșeli apar exact la aceste detalii.

## Temeiul legal

::: ghid-temei
"ajustările pentru deprecierea creanțelor, înregistrate potrivit reglementărilor contabile aplicabile,
reprezentând sume datorate de clienții interni și externi pentru produse, semifabricate, materiale,
mărfuri vândute, lucrări executate și servicii prestate, în limita unui procent de 30% din valoarea
acestor ajustări, altele decât cele prevăzute la lit. d)-f), h) și i), dacă creanțele îndeplinesc
cumulativ următoarele condiții:
1. sunt neîncasate într-o perioadă ce depășește 270 de zile de la data scadenței;
2. nu sunt garantate de altă persoană;
3. sunt datorate de o persoană care nu este persoană afiliată contribuabilului;"

"Prevederile alin. (1) lit. c) și j) se aplică pentru creanțele, altele decât cele asupra clienților
reprezentând sumele datorate de clienții interni și externi pentru produse, semifabricate, materiale,
mărfuri vândute, lucrări executate și servicii prestate, înregistrate începând cu data de 1 ianuarie
2016."
:::

## Greșelile cele mai des întâlnite

- **Se ignoră caracterul cumulativ al condițiilor.** Nu e suficient ca o creanță să fie veche de peste 270 de zile — mai trebuie să nu fie garantată și să nu fie la o persoană afiliată. O singură condiție neîndeplinită anulează dreptul de deducere.
- **Se confundă negarantarea creanței cu bonitatea debitorului.** "Negarantată" înseamnă că nicio altă persoană nu garantează plata (ex. fidejusiune, garanție bancară), nu că debitorul pare solvabil.
- **Se aplică 30% direct la valoarea creanței, nu la valoarea ajustării contabile constituite.** Baza de calcul a procentului e ajustarea contabilă, nu creanța brută.
- **Se sare direct la 100%** de îndată ce debitorul are "probleme financiare", fără hotărâre judecătorească de deschidere a falimentului sau procedură de insolvență documentată — condiția de la lit. j) cere un act juridic concret, nu doar o suspiciune de insolvabilitate.
- **Se confundă pragul de 270 de zile (impozit pe profit) cu regulile de ajustare a bazei de TVA**, care au praguri complet diferite (12 luni pentru persoane fizice, sau evenimente de faliment/reorganizare judiciară — fără un prag exprimat în zile). Cele două regimuri sunt independente și au temeiuri legale diferite (art. 26 pentru profit, art. 287 pentru TVA).

::: ghid-exemplu
O creanță de 20.000 lei față de un client afiliat, neîncasată de 400 de zile: deși depășește pragul de 270 de zile, ajustarea rămâne 0% deductibilă, pentru că a doua condiție cumulativă (neafilierea) nu e îndeplinită — vechimea creanței devine irelevantă.
:::

## Ce face iConta.eu

Funcția `deductibilitate_creanta` din `core/provizioane.py` verifică explicit, în această ordine, garantarea și afilierea (care întorc 0% necondiționat), apoi falimentul declarat (100%), apoi pragul strict de 270 de zile (30%). Ordinea reflectă corect caracterul cumulativ al condițiilor din lege. Motorul nu verifică însă data înregistrării creanței față de pragul de aplicabilitate din 1 ianuarie 2016 (relevant azi doar pentru creanțe foarte vechi) și nu modelează deloc pragurile de TVA — acelea se verifică separat, conform ghidului dedicat ajustării TVA.

[iConta.eu](/)
