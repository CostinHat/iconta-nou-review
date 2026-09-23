---
title: Ce fac dacă extrasul bancar nu corespunde cu contul 5121?
description: F073 nu compară niciodată soldul contului 5121 cu extrasul — potrivește doar liniile de extras cu facturi. O diferență are de regulă o cauză identificabilă printre liniile necontate, ignorate sau duplicate.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce fac dacă extrasul bancar nu corespunde cu contul 5121?

Motorul de reconciliere bancară din iConta.eu nu calculează și nu compară niciodată soldul contului 5121 din contabilitate cu soldul din extrasul bancar — el potrivește, linie cu linie, sumele din extras cu facturile deschise ale partenerilor. O diferență între cele două solduri nu e semnalată automat; ea trebuie investigată separat, printre cauzele de mai jos.

## Temeiul legal

::: ghid-temei
„Disponibilitățile aflate în conturi la bănci sau la unitățile Trezoreriei Statului se inventariază prin confruntarea soldurilor din extrasele de cont emise de acestea cu cele din contabilitatea entității."
— OMFP 2861/2009, pct. 29 alin. (2)
:::

::: ghid-temei
„Pentru verificarea înregistrării corecte în contabilitate a operațiunilor efectuate, lunar se întocmește balanța de verificare."
— Legea contabilității nr. 82/1991, art. 22
:::

Confruntarea explicită a soldului bancar cu extrasul de cont e prevăzută ca procedură de inventariere (de regulă la finalul exercițiului financiar), iar disciplina lunară de verificare a înregistrărilor rezultă din obligația de a întocmi balanța de verificare lunar — legea nu leagă explicit cele două, dar împreună susțin practica de a verifica periodic soldul 5121.

## Cauze verificate ale diferenței

Pentru că F073 nu ține un calcul de sold, o diferență între contul 5121 și extras poate proveni din:

- **Linii de extras nepotrivite sau necontate încă** — rămase în starea „nou", „potrivit parțial" (galben) sau „fără potrivire" (roșu) pe ecranul Bancă, deci neînregistrate contabil.
- **Linii marcate „Ignorată"** — un utilizator poate exclude explicit o linie din contabilizare; suma ei rămâne în extras, dar nu ajunge în 5121.
- **Reimportarea aceluiași extras** — dacă un fișier de extras se importă de două ori (sau două fișiere cu perioade suprapuse), liniile duplicate pot fi contate separat, ceea ce dublează o operațiune în 5121 fără să existe o dublare reală în bancă.
- **Un fișier de extras citit greșit** — parserul de extrase e validat pe formatul unei anumite bănci; un format de export diferit poate fi interpretat incorect, cu sume sau linii omise.
- **Operațiuni fără factură asociată** — comisioane bancare, dobânzi, viramente interne, avansuri — nu trec prin motorul de matching pe facturi și trebuie contabilizate separat, prin contabilizarea generală a extrasului.

## Ce se greșește în practică

- Se caută diferența doar în ecranul de reconciliere (unde apar doar liniile legate de facturi), ignorând operațiunile fără factură (comisioane, dobânzi) care afectează tot soldul 5121.
- Se reimportă un extras „ca să fie sigur" fără să se verifice dacă liniile lui au fost deja contate, riscând dubluri.
- Se presupune că, dacă toate liniile din extras apar „Contat ✓", soldul 5121 e automat corect — fără să se verifice separat dacă vreo linie a fost marcată „Ignorată" din greșeală.

## Ce face iConta.eu

Ecranul „Bancă" arată starea fiecărei linii de extras (nepotrivită, potrivire parțială, contată, ignorată), astfel încât liniile necontate să fie ușor de găsit. Contabilizarea generală a extrasului (`core/banca.py`), separată de motorul de matching pe facturi, tratează operațiunile fără factură (comisioane, dobânzi, credite). iConta.eu nu are însă un raport dedicat de comparație automată „sold 5121 vs. sold bancă" — verificarea finală rămâne pe fișa de cont 5121 și balanța de verificare, comparată manual cu soldul din extras.

[iConta.eu](/)
