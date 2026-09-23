---
title: "Cum se contabilizează costurile de inspecție și vămuire ale mărfurilor importate?"
description: "Costurile de vămuire și de inspecție atribuibile direct achiziției se capitalizează în costul mărfii, la fel ca transportul, nu se trec pe cheltuieli de exploatare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează costurile de inspecție și vămuire ale mărfurilor importate?

Comisionul plătit unui broker vamal pentru vămuire și costurile de inspecție a mărfii la import nu sunt cheltuieli separate de marfă — sunt costuri „atribuibile direct" achiziției și intră, la fel ca transportul, în costul de achiziție al mărfii.

## Temeiul legal

::: ghid-temei
„În costul de achiziție se includ, de asemenea, comisioanele, taxele notariale, cheltuielile cu obținerea de autorizații şi alte cheltuieli nerecuperabile, atribuibile direct bunurilor respective." — OMFP 1802/2014, Secțiunea 1.2, pct. 6
:::

Textul de mai sus vizează explicit comisioanele legate direct de achiziția bunurilor — categorie în care intră comisionul unui broker vamal pentru vămuire. Costurile de inspecție a mărfii (de exemplu, un control de calitate cerut la intrarea în țară) intră la aceeași regulă generală din pct. 6: „cheltuielile de transport, manipulare şi alte cheltuieli care pot fi atribuibile direct achiziției bunurilor respective" — atât timp cât costul e legat direct de aducerea acelei mărfi, se capitalizează, nu se trece pe cheltuială de exploatare.

## Ce se greșește în practică

- Se înregistrează costul de vămuire sau de inspecție direct pe o cheltuială de exploatare (ex. 628 „alte cheltuieli cu serviciile executate de terți"), în loc să fie inclus în costul mărfii.
- Se confundă acest tip de cost, atribuibil direct achiziției, cu un cost de finanțare (de exemplu comision de credit pentru finanțarea achiziției) — cele două sunt tratate diferit: costurile de îndatorare NU se capitalizează în costul mărfurilor cumpărate pentru revânzare (se capitalizează doar pentru active cu ciclu lung de fabricație), pe când comisionul de vămuire, fiind atribuibil direct bunurilor, se capitalizează.
- Se uită de TVA-ul aferent acestor costuri — doar valoarea netă (fără TVA) se capitalizează în costul mărfii; TVA-ul se tratează separat de contabil.
- După ce marfa a fost deja înregistrată (NIR validat), se caută un buton de „corectare" pentru un cost de vămuire introdus greșit — un NIR deja validat nu se poate edita sau șterge din aplicație; corectarea se face printr-o notă contabilă manuală de stornare.

## Ce face iConta.eu

Costurile de vămuire și de inspecție se introduc ca „taxe" accesorii pe NIR, alături de transport, dacă e cazul. Aplicația le **repartizează automat, proporțional cu costul de bază** al fiecărei linii din NIR, cu restul de rotunjire pe ultima linie, astfel încât suma repartizată să fie exact egală cu suma introdusă. Contul de credit este implicit 446, dar este un parametru vizibil în formular, pe care contabilul îl poate confirma sau schimba — de exemplu, atunci când vămuirea e facturată de un broker distinct de furnizorul mărfii, nu de vamă direct.

Costul rezultat (cu vămuirea și inspecția incluse) intră în verificarea prețului de vânzare: dacă prețul de vânzare introdus pentru un articol e sub costul de achiziție majorat cu aceste costuri, înregistrarea e blocată.

Limitări de care trebuie să ții cont: repartizarea automată este disponibilă doar pentru firmele care țin gestiunea de stocuri **global-valorică**, nu pentru cele cu gestiune cantitativ-valorică (CMP) — pentru acestea din urmă, calculul se face manual, în afara aplicației. De asemenea, aplicația **nu calculează automat TVA-ul** aferent acestor costuri accesorii — capitalizează doar valoarea netă, iar TVA-ul rămâne responsabilitatea contabilului, tratat separat. Iar odată ce NIR-ul e validat, nu există în aplicație o funcție dedicată de corectare a lui — orice eroare descoperită ulterior se rezolvă printr-o notă manuală de stornare în jurnal.

[iConta.eu](/)
