---
title: SAF-T pentru operațiuni intracomunitare: cum se raportează
description: SAF-T (declarația D406) raportează toate notele contabile ale perioadei, inclusiv formula taxării inverse generate de achizițiile intracomunitare, dar nu e un substitut al D390 — sunt două obligații separate, cu temeiuri și scopuri diferite.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# SAF-T pentru operațiuni intracomunitare: cum se raportează

SAF-T nu are o secțiune dedicată „operațiuni intracomunitare”. Fișierul raportează Cartea Mare și documentele sursă ale perioadei, așa cum sunt ele înregistrate în contabilitate — iar o achiziție sau o livrare intracomunitară intră acolo ca orice altă operațiune, prin conturile pe care le folosește.

## Temeiul legal

::: ghid-temei
„beneficiarul înregistrează… suma taxei aferente în următoarea formulă contabilă: 4426 = 4427. Prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă” — HG 1/2016, norme de aplicare a Codului fiscal, art. 331, pct. 109 alin. (1) (sursă: `anaf_surse/hg_1_2016_norme_cod_fiscal.txt`, L242, verificat în dosarul F050).
:::

Formula 4426 = 4427 e nota contabilă standard prin care se înregistrează taxarea inversă la achizițiile intracomunitare de bunuri și la serviciile primite din UE. Norma spune explicit că regula „e valabilă pentru orice alte situații în care se aplică taxarea inversă” — deci nu e o excepție de raportat separat, ci o operațiune contabilă obișnuită, care intră în Cartea Mare exact ca oricare alta.

De aceea, în măsura în care un fișier SAF-T raportează integral Cartea Mare a perioadei (`GeneralLedgerEntries`), o notă contabilă 4426 = 4427 provenită dintr-o achiziție intracomunitară apare acolo alături de restul înregistrărilor — nu lipsește și nu se dublează doar pentru că operațiunea e și raportată separat, prin D390.

## Ce se greșește în practică

Confuzia frecventă e că D390 „acoperă” și obligația SAF-T, sau invers — că o operațiune deja raportată în D390 nu mai trebuie să apară și în SAF-T. Sunt două declarații independente, cu baze legale și scopuri diferite: D390 corelează livrările și achizițiile intracomunitare între statele membre (art. 325 Cod fiscal), în timp ce SAF-T raportează evidența contabilă și documentele sursă ale firmei. O operațiune intracomunitară reală trebuie să fie consecventă în ambele — aceeași bază, aceeași perioadă — nu prezentă într-una și absentă din cealaltă.

## Ce face iConta.eu

Motorul F050 (`core/intracomunitar.py`) calculează taxa prin taxare inversă și generează nota contabilă 4426 = 4427, cu rotunjire `Decimal` și `ROUND_HALF_UP`, exact cum cere norma citată mai sus. Această cercetare (dosarul F050) nu a acoperit însă fișierele SAF-T ale iConta.eu (`core/d406.py` și modulele conexe) — nu am verificat la sursă dacă generatorul SAF-T tratează în vreun fel distinct liniile provenite din operațiuni intracomunitare, deci nu afirmăm aici un comportament de produs pe care nu l-am confirmat în cod. Ce putem confirma e doar latura contabilă amonte: nota 4426 = 4427 există și e corect calculată, iar de acolo intră în evidența pe care orice generator SAF-T o citește.

[iConta.eu](/)
