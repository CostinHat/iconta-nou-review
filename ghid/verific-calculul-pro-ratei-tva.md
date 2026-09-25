---
title: "Cum verific calculul pro-ratei TVA la control?"
description: "Ce documente și ce calcule cere legea pentru pro-rata de TVA, ca să le puteți verifica sau prezenta la un control fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific calculul pro-ratei TVA la control?

Când un inspector fiscal cere justificarea pro-ratei aplicate, întrebarea reală e dacă numărătorul și numitorul fracției au fost calculate corect, dacă excluderile obligatorii au fost respectate și dacă regularizarea de sfârșit de an a fost făcută la timp.

## Temeiul legal

::: ghid-temei
„(6) Pro rata prevăzută la alin. (5) se determină ca raport între: a) suma totală, fără taxă, dar cuprinzând subvențiile legate direct de preț, a operațiunilor constând în livrări de bunuri și prestări de servicii care permit exercitarea dreptului de deducere, la numărător; și b) suma totală, fără taxă, a operațiunilor prevăzute la lit. a) și a operațiunilor constând în livrări de bunuri și prestări de servicii care nu permit exercitarea dreptului de deducere, la numitor. [...]
(8) Pro rata definitivă se determină anual, iar calculul acesteia include toate operațiunile prevăzute la alin. (6), pentru care exigibilitatea taxei ia naștere în timpul anului calendaristic respectiv [...]. Pro rata definitivă se determină procentual și se rotunjește până la cifra unităților imediat următoare. La decontul de taxă [...], în care s-a efectuat ajustarea prevăzută la alin. (14), se anexează un document care prezintă metoda de calcul al pro ratei definitive."
— Cod fiscal, art. 300 alin. (6) și (8) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Pentru un control, verificați pe rând:

- **Documentul de metodă de calcul**: legea cere expres ca la decontul în care s-a efectuat regularizarea anuală să fie anexat un document care descrie metoda de calcul a pro-ratei definitive — absența acestui document, chiar dacă procentul e corect, e o vulnerabilitate formală.
- **Ce intră la numărător**: doar operațiunile cu drept de deducere (inclusiv subvențiile legate direct de preț), fără TVA.
- **Ce intră la numitor**: totalul operațiunilor cu drept de deducere PLUS cele fără drept de deducere — inclusiv sumele primite de la buget pentru finanțarea operațiunilor scutite fără drept de deducere.
- **Excluderile obligatorii** din calcul (art. 300 alin. (7)): valoarea livrărilor de bunuri de capital folosite în activitatea economică, valoarea livrărilor/prestărilor către sine, valoarea operațiunilor imobiliare accesorii activității principale — dacă acestea au fost incluse eronat în calcul, pro-rata rezultată e greșită.
- **Rotunjirea**: procentual, „până la cifra unităților imediat următoare" — adică întotdeauna în sus, nu prin rotunjire matematică obișnuită.
- **Comunicarea pro-ratei provizorii**: pentru anul curent, trebuia comunicată organului fiscal competent până la 25 ianuarie inclusiv — verificați dacă declarația de mențiuni respectivă a fost depusă la termen.
- **Regularizarea anuală efectivă**: verificați dacă diferența dintre pro-rata provizorie aplicată lunar/trimestrial și pro-rata definitivă a fost înscrisă ca regularizare în decontul aferent ultimei perioade fiscale a anului.

## Ce se greșește în practică

- Se prezintă la control doar procentul final de pro-rata, fără documentul de metodă de calcul cerut expres de lege pentru decontul de regularizare.
- Se include în numărător sau numitor valoarea unor operațiuni expres excluse de lege (de exemplu, vânzarea unui mijloc fix folosit în activitate), umflând sau diminuând artificial procentul.
- Nu se poate demonstra, la cerere, comunicarea la termen (25 ianuarie) a pro-ratei provizorii către organul fiscal — o obligație distinctă de calculul propriu-zis.

## Ce face iConta.eu

iConta.eu folosește pro-rata introdusă manual de contabil în profilul fiscal (`pro_rata`) pentru a calcula automat, la generarea D300, ajustarea corespunzătoare din rândul de regularizare, dacă procentul e sub 100%. La data acestui ghid, aplicația **nu generează documentul de metodă de calcul** cerut de art. 300 alin. (8) și **nu calculează ea însăși numărătorul/numitorul** din operațiunile firmei — contabilul rămâne responsabil să determine procentul corect și să pregătească separat documentația justificativă pentru control.

[iConta.eu](/)
