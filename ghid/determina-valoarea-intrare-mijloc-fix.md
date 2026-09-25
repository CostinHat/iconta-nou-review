---
title: "Cum se determină valoarea de intrare a unui mijloc fix în leasing"
description: "Pentru un mijloc fix luat în leasing financiar, valoarea de intrare este costul de achiziție al finanțatorului, nu suma totală a ratelor de leasing."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se determină valoarea de intrare a unui mijloc fix în leasing

Când o firmă ia un utilaj sau un mijloc de transport în leasing financiar, apare frecvent o confuzie: se crede că valoarea de intrare în contabilitate ar trebui să fie suma totală a ratelor din graficul de leasing (capital plus dobândă). Reglementările contabile spun altceva.

## Temeiul legal

::: ghid-temei
„d) valoarea totală a ratelor de leasing, mai puțin cheltuielile accesorii, este mai mare sau egală cu valoarea de intrare a bunului, reprezentată de valoarea la care a fost achiziționat bunul de către finanțator, respectiv costul de achiziție."
— OMFP 1.802/2014, Reglementările contabile, pct. 213 alin. (2) lit. d) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

::: ghid-temei
„(1) Înregistrarea în contabilitate a amortizării bunului ce face obiectul contractului se efectuează în cazul leasingului financiar de către locatar/utilizator [...]. (2) În cazul leasingului financiar, achizițiile de către locatar de bunuri imobile și mobile sunt tratate ca investiții în imobilizări, fiind supuse amortizării pe o bază consecventă cu politica normală de amortizare pentru bunuri similare ale locatarului."
— OMFP 1.802/2014, Reglementările contabile, pct. 214 alin. (1)-(2) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Din aceste prevederi rezultă regula practică:

- Valoarea de intrare a unui mijloc fix preluat în leasing financiar este **costul de achiziție al bunului la finanțator** (societatea de leasing) — adică valoarea din capitalul finanțat, fără dobândă și fără celelalte costuri accesorii (comisioane, asigurări) din graficul de rambursare.
- Dobânda de leasing NU intră în valoarea de intrare a mijlocului fix — ea se recunoaște separat, periodic, ca o cheltuială financiară (cont 666), pe măsura scadenței fiecărei rate.
- Amortizarea se calculează de către locatar (utilizator), nu de societatea de leasing, exact ca pentru un mijloc fix cumpărat direct — pe baza acestei valori de intrare (costul de achiziție al finanțatorului), nu pe baza sumei totale de plătit conform contractului.
- Distincția între leasing financiar și leasing operațional se face la începutul contractului, în funcție de criteriile legale (transferul riscurilor și beneficiilor), și determină cine amortizează bunul — locatarul, la financiar, respectiv locatorul, la operațional.

## Ce se greșește în practică

- Se înregistrează mijlocul fix la valoarea totală de plătit conform graficului de leasing (capital + dobândă totală), umflând artificial valoarea de intrare și, implicit, amortizarea anuală deductibilă.
- Se amortizează bunul la nivelul societății de leasing, nu la utilizator, într-un contract de leasing financiar unde utilizatorul e cel care trebuie să recunoască amortizarea.
- Se tratează toate contractele de leasing la fel, fără a verifica la începutul contractului dacă îndeplinesc criteriile de leasing financiar sau sunt, de fapt, leasing operațional — ceea ce schimbă complet tratamentul contabil.
- Se include TVA-ul aferent ratelor în valoarea de intrare a mijlocului fix, deși TVA-ul deductibil urmează regimul obișnuit, separat de valoarea contabilă a activului.

## Ce face iConta.eu

iConta.eu chiar acoperă acest caz: aplicația generează automat notele contabile pentru intrarea unui mijloc fix prin leasing financiar, pornind de la valoarea capitalului finanțat (nu de la totalul ratelor), separă corect dobânda aferentă fiecărei rate ca element de cost financiar distinct, și calculează separat notele contabile atât pentru leasingul financiar, cât și pentru cel operațional, inclusiv pentru valoarea reziduală la finalul contractului.

[iConta.eu](/)
