---
title: Se poate modifica durata de amortizare după punerea în funcțiune?
description: Nu, ca regulă - durata normală de funcționare, odată stabilită la punerea în funcțiune, rămâne neschimbată până la recuperarea integrală a valorii activului sau scoaterea lui din funcțiune. Singurele excepții reale sunt corectarea unei erori și reevaluarea.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Se poate modifica durata de amortizare după punerea în funcțiune?

Ca regulă, nu. Odată stabilită, durata normală de funcționare a unui mijloc fix rămâne fixă pe toată perioada de amortizare — legea nu permite schimbarea ei "din mers", doar pentru a ajusta cheltuiala unui anumit an.

## Temeiul legal

::: ghid-temei
Astfel stabilita, durata normala de funcționare a mijlocului fix rămâne neschimbata până la recuperarea integrală a valorii de intrare a acestuia sau scoaterea sa din funcțiune.

— HG 2139/2004, Catalogul privind clasificarea și duratele normale de funcționare a mijloacelor fixe, cap. II pct.4
:::

Textul e explicit: durata rămâne neschimbată până când se întâmplă unul dintre cele două lucruri — valoarea de intrare e complet recuperată prin amortizare, sau activul iese din funcțiune (casare, vânzare etc.). În afara acestor situații, durata nu se poate modifica liber.

Există, în practică, două situații care schimbă efectiv datele de calcul, fără să încalce această regulă:

- **corectarea unei erori reale** — dacă durata inițial aleasă s-a dovedit greșită față de plaja legală din catalog (nu doar "regândită"), corecția înseamnă recalcularea amortizării, nu o simplă schimbare de cifră pentru viitor;
- **reevaluarea activului** — o reevaluare nu schimbă doar valoarea contabilă a activului, ci poate tăia efectiv durata de amortizare rămasă în etape distincte (înainte/după reevaluare), pe baza raportului de evaluare; dacă durata normală era deja epuizată înainte de reevaluare, legea nu permite "prelungirea" ei artificială pentru a justifica o nouă amortizare.

## Ce se greșește în practică

- Se modifică durata unui activ deja pus în funcțiune doar pentru a reduce sau crește artificial cheltuiala cu amortizarea într-un anumit an — nu e o corectare de eroare, ci o schimbare de opțiune, fără acoperire legală.
- Se presupune că orice reevaluare "resetează" automat durata de amortizare la o valoare nouă, aleasă liber — durata rămasă după reevaluare vine din raportul de evaluare, nu dintr-o alegere discreționară.
- Se ignoră faptul că, odată ce durata normală s-a epuizat, ea nu mai poate fi "prelungită" doar pentru a permite o amortizare suplimentară după o reevaluare.

## Ce face iConta.eu

Motorul de amortizare tratează reevaluarea ca etapă distinctă: activul e recalculat "sintetic" pe fiecare etapă (înainte și după fiecare reevaluare aplicată), astfel încât amortizarea nu se recalculează retroactiv pe valoarea nouă de la data punerii inițiale în funcțiune — ceea ce ar produce o cifră care n-a fost niciodată înregistrată în evidență. Dacă durata normală s-a epuizat deja înainte de reevaluare, aplicația **refuză explicit** operațiunea, în loc să ghicească o durată rămasă — aceasta trebuie să vină din raportul evaluatorului, în afara registrului.

[iConta.eu](/)
