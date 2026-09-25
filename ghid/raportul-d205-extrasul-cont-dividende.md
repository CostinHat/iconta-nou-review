---
title: "Raportul între D205 și extrasul de cont pentru dividende"
description: "De ce D205 se generează din contul 457 din contabilitate, nu direct din extrasul de cont bancar, și ce document justificativ trebuie să stea totuși la baza fiecărei plăți."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Raportul între D205 și extrasul de cont pentru dividende

D205 nu se completează pe baza extrasului de cont — se generează din notele contabile care mișcă contul 457 (dividende distribuite și plătite). Extrasul de cont rămâne, totuși, documentul care dovedește că plata a avut loc așa cum a fost înregistrată, iar fără el nota contabilă nu are, de fapt, temei.

## Temeiul legal

::: ghid-temei
„(1) Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ. (2) Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea contabilității 82/1991, art. 6 alin. (1)-(2) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

- Plata unui dividend prin bancă are drept document justificativ extrasul de cont (sau ordinul de plată confirmat) — fără el, nota contabilă „457 = 5121" nu are, formal, la ce se sprijini.
- Contabilul e cel care răspunde, potrivit legii, pentru corespondența dintre suma și data înregistrate în contabilitate și cele din documentul justificativ (extrasul de cont) — nu declarația D205 în sine.
- D205, ca declarație informativă, preia date deja înregistrate în contabilitate; ea nu e locul unde se verifică dacă banca a virat efectiv suma corectă — acea verificare se face înainte, la momentul înregistrării plății.

## Ce se greșește în practică

- Se înregistrează plata dividendului în contabilitate înainte ca extrasul de cont să confirme efectiv operațiunea, iar diferențele (comisioane reținute, sume parțiale) rămân necorectate.
- Se presupune că o eventuală neconcordanță între contabilitate și extrasul bancar se poate „repara" direct în declarația D205, în loc să se corecteze nota contabilă sursă.
- Se amână reconcilierea dintre extrasul de cont și registrul de dividende plătite până la momentul depunerii declarației, când corectarea contabilă e mult mai greu de făcut retroactiv.

## Ce face iConta.eu

iConta.eu nu citește extrasul de cont bancar pentru a genera D205 și nu face nicio confruntare automată cu operațiunile bancare reale. Declarația se generează exclusiv din notele contabile de pe contul 457 aflate în starea „validată" — sursa ei e contabilitatea, nu banca. Un modul separat de reconciliere recalculează independent, tot din contabilitate (nu din extrasul de cont), aceleași sume per beneficiar și blochează generarea declarației la orice divergență internă între cele două căi de calcul.

Ce NU face aplicația: nu importă și nu compară automat notele de plată cu extrasul de cont bancar real. Corelarea dintre suma înregistrată pe 457 și ce arată efectiv banca rămâne un pas manual, de rutină contabilă curentă, pe care contabilul trebuie să-l facă înainte de a considera nota de plată validată.

[iConta.eu](/)
