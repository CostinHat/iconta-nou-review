---
title: "Sediul fix înregistrat în scopuri de TVA este și sediu permanent desemnat la profit?"
description: "Da, dar numai dacă acel sediu fix este și sediu permanent în sensul art. 8 din Codul fiscal. Atunci el preia obligațiile de impozit pe profit ale tuturor sediilor permanente ale firmei străine."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Sediul fix înregistrat în scopuri de TVA este și sediu permanent desemnat la profit?

Da, cu o condiție: sediul fix care îndeplinește obligațiile de TVA trebuie să fie, în același timp, **sediu permanent în sensul art. 8** din Codul fiscal (Legea 227/2015). Dacă este, legea îl face direct sediul permanent desemnat la impozitul pe profit. Firma străină nu mai alege atunci un alt sediu pentru obligațiile din Titlul II.

Cele două noțiuni nu se suprapun automat. „Sediul fix" ține de TVA și se definește prin resursele tehnice și umane pentru livrări sau prestări regulate. „Sediul permanent" ține de impozitul pe profit și se definește prin locul prin care se desfășoară activitatea nerezidentului, cu excepțiile de la art. 8 alin. (4).

## Temeiul legal

::: ghid-temei
„În situația în care sediul fix care îndeplinește obligațiile fiscale potrivit titlului VII constituie și sediu permanent în sensul art. 8 [...] sediul fix este și sediul permanent desemnat pentru îndeplinirea obligațiilor care revin potrivit prezentului titlu."
— Codul fiscal (Legea 227/2015), art. 37 alin. (5) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„o persoană impozabilă care are sediul activității economice în afara României se consideră că este stabilită în România dacă are un sediu fix în România, respectiv dacă dispune în România de suficiente resurse tehnice și umane pentru a efectua regulat livrări de bunuri și/sau prestări de servicii impozabile;"
— Codul fiscal (Legea 227/2015), art. 266 alin. (2) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„În înțelesul prezentului cod, sediul permanent este un loc prin care se desfășoară integral sau parțial activitatea unui nerezident, fie direct, fie printr-un agent dependent."
— Codul fiscal (Legea 227/2015), art. 8 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cum se aplică regula:

- **Primul pas: există un sediu fix în sensul TVA.** Firma străină dispune în România de resurse tehnice și umane suficiente pentru livrări sau prestări regulate (art. 266 alin. (2) lit. b)) și e înregistrată în scopuri de TVA prin acest sediu (art. 316 alin. (2)).
- **Al doilea pas: sediul fix e și sediu permanent.** Se verifică art. 8: un loc prin care se desfășoară activitatea, de exemplu o sucursală, un birou sau un atelier (alin. (2)). Un loc fix folosit numai pentru activități pregătitoare sau auxiliare nu este sediu permanent (alin. (4) lit. f)).
- **Dacă ambele condiții sunt îndeplinite**, sediul fix devine prin lege sediul permanent desemnat. La el se cumulează veniturile și cheltuielile tuturor sediilor permanente ale firmei din România (art. 37 alin. (1)), iar el calculează, declară și plătește impozitul pe profit (alin. (4)).
- **Dacă sediul fix nu e sediu permanent**, alin. (5) nu se aplică. Pentru profit contează doar sediile permanente. Dacă sunt mai multe, firma desemnează unul dintre ele (alin. (1)). Dacă e unul singur, acela e desemnat (art. 36 alin. (5)).
- **Înregistrarea în scopuri de TVA nu creează singură un sediu permanent.** Hotărâtor e testul de la art. 8, nu codul de TVA.

::: ghid-exemplu
O societate din Austria are în România:
- o sucursală la Timișoara, cu angajați care vând marfă regulat, înregistrată în scopuri de TVA ca sediu fix. Este și sediu permanent (sucursală, art. 8 alin. (2));
- un șantier de construcții la Brașov, care durează 9 luni, deci tot sediu permanent (art. 8 alin. (3)).

Sucursala din Timișoara devine automat sediul permanent desemnat (art. 37 alin. (5)). Rezultate fiscale 2026: Timișoara 120.000 lei, Brașov 60.000 lei. Cumulat la Timișoara: 120.000 + 60.000 = 180.000 lei. Impozit pe profit: 180.000 × 16% = 28.800 lei, declarat și plătit de sucursala din Timișoara.
:::

## Ce se greșește în practică

- Se consideră că orice cod de TVA obținut în România înseamnă automat sediu permanent la profit, fără analiza de la art. 8.
- Firma desemnează la profit alt sediu decât sediul fix, deși sediul fix e și sediu permanent și alin. (5) îl impune.
- Șantierul care depășește 6 luni nu e cumulat la sediul desemnat, ci tratat separat sau ignorat.
- Un depozit folosit doar pentru stocare e tratat ca sediu permanent, deși art. 8 alin. (4) îl exclude.

## Ce face iConta.eu

iConta.eu ține evidența TVA a firmei (facturi, decont D300) și calculează declarația anuală de impozit pe profit (D101) din balanța entității, generând XML validat. Aplicația nu analizează dacă un sediu fix constituie sediu permanent și nu are o funcție de cumulare a rezultatelor mai multor sedii permanente. Încadrarea în art. 8 și art. 37 și alocarea rezultatelor le face contabilul.

[iConta.eu](/)
