---
title: Cum se recalculează amortizarea după o reevaluare
description: Reevaluarea nu doar înlocuiește valoarea unui mijloc fix — elimină amortizarea cumulată, recalculează valoarea netă la valoarea justă, iar de la acel moment activul se amortizează din nou, pe durata rămasă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se recalculează amortizarea după o reevaluare

După o reevaluare, amortizarea nu continuă pur și simplu pe o valoare mai mare sau mai mică — mecanismul e altul: amortizarea cumulată până atunci se elimină din valoarea brută, iar activul intră într-o etapă nouă de amortizare, calculată de la zero pe valoarea justă și pe durata rămasă de utilizare.

## Temeiul legal

::: ghid-temei
"Dacă rezultatul reevaluării este o creștere față de valoarea contabilă netă, atunci aceasta se tratează astfel: ca o creștere a rezervei din reevaluare [...], dacă nu a existat o descreștere anterioară recunoscută ca o cheltuială aferentă acelui activ [...]. Dacă rezultatul reevaluării este o descreștere a valorii contabile nete, aceasta se tratează ca o cheltuială cu întreaga valoare a deprecierii [...] sau ca o scădere a rezervei din reevaluare [...]." — OMFP 1802/2014, pct. 111 alin. (1)-(2)
:::

Practic, recalcularea urmează trei pași — amortizarea cumulată la data reevaluării se elimină din valoarea contabilă brută, iar valoarea netă e recalculată la valoarea justă; valoarea astfel rezultată înlocuiește costul de achiziție/producție, iar regulile de amortizare se aplică în continuare pe baza ei (OMFP 1802/2014, pct. 103-104):

1. **Eliminarea amortizării cumulate** din valoarea brută a activului (28xx = 21x) — rămâne valoarea netă contabilă dinaintea reevaluării.
2. **Ajustarea la valoarea justă**, cu diferența tratată drept creștere sau scădere (pct. 111 alin. (1) și (2), după caz — vezi ghidul dedicat).
3. **Amortizare nouă, de la zero**, pe valoarea justă rezultată și pe durata rămasă de utilizare economică — nu pe durata inițială, nerecalculată.

Important pentru amortizarea din anul reevaluării: pentru că eliminarea amortizării cumulate ar distorsiona o simplă diferență între soldul de la 1 ianuarie și cel de la 31 decembrie (putând ieși chiar negativă), cheltuiala anuală corectă se obține însumând ratele lunare calculate separat pentru fiecare lună a anului, nu scăzând bornele.

Fiscal, tratamentul diverge de cel contabil când reevaluarea e o **descreștere**: baza de amortizare fiscală nu coboară sub costul istoric de achiziție/producție — ea "se recalculează până la nivelul celei stabilite pe baza costului de achiziție" (Legea 227/2015, art. 7 pct. 44 lit. c). Doar creșterile din reevaluare intră efectiv în valoarea fiscală amortizabilă.

## Ce se greșește în practică

- Se recalculează amortizarea pe noua valoare fără să se elimine mai întâi amortizarea cumulată din valoarea brută — se ajunge la o bază de amortizare greșită.
- Se aplică, după o descreștere din reevaluare, aceeași valoare mai mică și în evidența fiscală a amortizării — deși fiscal baza rămâne la costul istoric (art. 7 pct. 44 lit. c).
- Se calculează amortizarea anului reevaluării ca diferență simplă între soldul de la începutul și cel de la finalul anului, în loc să se însumeze ratele lunare pe cele două etape (înainte și după reevaluare).

## Ce face iConta.eu

Motorul de amortizare tratează reevaluarea ca o etapă distinctă în viața activului: consumă din durata normală lunile scurse până la data reevaluării, apoi pornește o etapă nouă pe valoarea justă și durata rămasă, iar amortizarea lunii reevaluării intră deja în etapa nouă. Înainte de a elimina amortizarea cumulată, aplicația verifică automat dacă amortizarea înregistrată în contabilitate coincide cu cea calculată din registrul mijlocului fix (durată, metodă, dată de punere în funcțiune) — dacă există o diferență, reevaluarea e blocată până când nota de amortizare lipsă e înregistrată, tocmai pentru a nu elimina o amortizare care n-a fost efectiv înregistrată.

[iConta.eu](/)
