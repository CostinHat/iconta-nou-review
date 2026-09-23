---
title: Cum tratăm rezerva din reevaluare la scoaterea din evidență
description: La cedarea sau casarea unui activ reevaluat, soldul rămas al rezervei din reevaluare se transferă la rezultatul reportat (1175) — un transfer de capitaluri, calculat separat, nu un efect automat al notei de casare.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum tratăm rezerva din reevaluare la scoaterea din evidență

Un activ reevaluat care are un sold în rezerva din reevaluare (cont 105) nu "pierde" acel sold la cedare sau casare — surplusul rămas se realizează și se transferă la rezultatul reportat. E o operațiune de capitaluri proprii, separată de nota contabilă prin care activul iese efectiv din evidență.

## Temeiul legal

::: ghid-temei
"Surplusul din reevaluare inclus în rezerva din reevaluare este capitalizat prin transferul direct în rezultatul reportat (contul 1175 «Rezultatul reportat reprezentând surplusul realizat din rezerve din reevaluare»), atunci când acest surplus reprezintă un câștig realizat." — OMFP 1802/2014, pct. 109 alin. (1)
:::

Realizarea surplusului are loc fie la scoaterea din evidență a activului, fie eșalonat, pe măsura folosirii lui (diferența dintre amortizarea calculată pe valoarea reevaluată și amortizarea calculată pe costul inițial). La scoaterea din evidență (vânzare, casare), tot ce a mai rămas nerealizat din rezervă se transferă integral: 105 = 1175.

Important de separat: nota prin care activul iese fizic din evidență (de exemplu, la casare: 28xx + 6583 = 21x, pentru amortizarea rămasă și valoarea neamortizată) **nu conține** și transferul rezervei — sunt două operațiuni distincte, care se înregistrează separat. Suma de transferat la 1175 se stabilește pe baza soldului rezervei 105 aferente acelui activ specific, nu pe baza valorii nete rămase la casare.

Fiscal, acest moment contează dublu pentru contribuabilii care au constituit rezerva după 1 ianuarie 2004: soldul rămas al rezervei din reevaluare a mijloacelor fixe/terenurilor, dacă n-a fost deja consumat prin amortizarea fiscală, devine impozabil integral la scăderea din gestiune a activului (Legea 227/2015, art. 26 alin. (6)).

## Ce se greșește în practică

- Se presupune că nota de casare/cedare transferă automat rezerva din reevaluare rămasă la 1175 — sunt operațiuni separate; transferul trebuie inițiat și calculat distinct.
- Se calculează suma de transferat pornind de la valoarea neamortizată rămasă la casare, în loc de soldul real al rezervei 105 aferente activului respectiv.
- Se omite impozitarea soldului rămas al rezervei la scăderea din gestiune (Legea 227/2015, art. 26 alin. (6)), tratând transferul 105 = 1175 ca pe o simplă mutare de capitaluri fără consecințe fiscale.

## Ce face iConta.eu

Nota de casare generează corect notele specifice scoaterii din evidență (amortizarea rămasă și valoarea neamortizată), dar nu citește automat istoricul reevaluărilor aplicate ale activului și nu generează singură transferul surplusului la 1175. Transferul rămâne o operațiune manuală separată, disponibilă în același ecran de reevaluare (opțiunea "Transfer surplus la 1175"), în care contabilul introduce suma — calculată de el pe baza soldului rezervei 105 aferente acelui activ, nu preluată automat din aplicație.

[iConta.eu](/)
