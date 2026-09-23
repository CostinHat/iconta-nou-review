---
title: Cum se corelează D300 cu D390 pentru o achiziție din UE
description: O achiziție intracomunitară de bunuri apare pe rândul R5_1 din D300 și în baza A din D390 — cum le confruntă aplicația și pe ce perioadă anume.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se corelează D300 cu D390 pentru o achiziție din UE

O achiziție intracomunitară de bunuri lasă urme în două declarații: în decontul de TVA (D300), pe rândul de achiziții intracomunitare, și în declarația recapitulativă (D390), pe codul A. Cele două ar trebui să coincidă, pentru că se derivă din aceleași facturi — corelarea verifică exact asta.

## Temeiul legal

::: ghid-temei
**Art. 278 din Codul fiscal (Legea 227/2015)** — locul operațiunii și taxarea inversă pentru achizițiile intracomunitare de bunuri.

**Art. 325 din Codul fiscal** — obligația de a declara achizițiile intracomunitare taxabile în declarația recapitulativă (D390), lit. d.

Structura oficială a formularului D300 (validator ANAF, rândurile Rd.5 col.1 — **R5_1** — și Rd.18 col.1 — **R18_1**, oglindă deductibilă la taxare inversă) confirmă existența și corespondența acestor rânduri.
:::

Rândul **R5_1** din D300 e locul unde apare, colectat, TVA-ul aferent achizițiilor intracomunitare de bunuri — derivat automat din facturile cu partener din UE, cu taxare inversă (art. 278). Aceeași bază de facturi generează codul **A** din D390. Practic, cele două cifre pornesc din exact aceleași documente.

Verificarea nu se face pe un D300 recalculat pe loc, ci pe **D300-ul efectiv depus** — rândurile persistate la momentul depunerii prin aplicație. Iar fereastra comparată nu e neapărat luna curentă a ecranului: e **cea mai recentă perioadă pentru care există un D300 depus prin aplicație**, afișată explicit în etichetă (de exemplu „perioada 06/2026"), pentru că D300 se depune cu o lună întârziere față de perioada la care se referă.

## Ce se greșește în practică

- Se compară valoarea din D390 cu un D300 „calculat acum", nu cu cel efectiv depus — dacă între timp au apărut facturi noi sau corecții, cifrele curente nu mai reflectă ce a fost declarat atunci.
- Se caută comparația pe luna calendaristică a ecranului, deși D300 relevant e din perioada anterioară (cea mai recentă cu depunere prin aplicație), nu din luna curentă.
- Se ignoră faptul că R5_1 și R18_1 (oglinda deductibilă) trebuie să fie egale prin construcție (taxare inversă, net zero) — o diferență între ele indică o eroare de completare manuală, nu o problemă de corelare cu D390.

## Ce face iConta.eu

Pentru achizițiile intracomunitare, aplicația confruntă baza A din D390 (recalculată pe perioada relevantă) cu rândul R5_1 din D300-ul efectiv depus prin aplicație — nu cu un decont regenerat pe loc. Dacă nu există niciun D300 depus prin aplicație în fereastra respectivă, verificarea rămâne gri, cu mesajul explicit „nu există D300 depus" — nu inventează o valoare de referință.

Rezultatul e un semnal, nu o corecție: verde dacă valorile coincid (în limita unei toleranțe de rotunjire la leu), roșu dacă D390 arată o achiziție pe care D300 depus nu o confirmă (cu propunerea de rectificativă sau de corecție D390, confirmată de tine), gri pentru orice altă diferență de cifre — considerată posibil decalaj de exigibilitate (art. 284), regularizare sau rotunjire, nu eroare automat confirmată.

[iConta.eu](/)
