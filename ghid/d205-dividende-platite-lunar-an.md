---
title: D205 pentru dividende plătite lunar într-un an
description: Fiecare plată lunară de dividend are propriul termen de virare a impozitului — 25 a lunii următoare acelei plăți. Cum tratează iConta.eu plățile eșalonate în mai multe tranșe.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# D205 pentru dividende plătite lunar într-un an

Un dividend distribuit printr-o singură hotărâre poate fi plătit efectiv în mai multe tranșe lunare, pe parcursul unui an. Legea nu leagă reținerea impozitului de momentul distribuirii, ci de fiecare plată în parte — ceea ce înseamnă că, la plăți lunare, apar mai multe momente succesive de reținere, fiecare cu propriul termen de virare.

## Temeiul legal

::: ghid-temei
"Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor/sumelor reprezentând câștigul obținut ca urmare a deținerii de titluri de participare de către acționari/asociați/investitori. Termenul de virare a impozitului este până la data de 25 inclusiv a lunii următoare celei în care se face plata."
— Codul fiscal, Legea 227/2015, art. 97 alin. (7)
:::

Textul leagă explicit reținerea și scadența de virare de **luna plății**, nu de o dată unică pe an. Dacă un dividend e plătit în tranșe lunare, fiecare tranșă e o "plată" în sensul acestui text și generează propriul termen de 25 a lunii următoare.

O mențiune separată: acest ghid tratează scenariul unor **plăți eșalonate lunar ale unui dividend deja distribuit** printr-o singură hotărâre. Dacă vă referiți, în schimb, la **distribuiri interimare** repetate în cursul anului (aprobate periodic, nu doar plătite eșalonat), rețineți că legea societăților reglementează distribuirea de dividende interimare pe bază **trimestrială**, nu lunară — cercetarea care stă la baza acestui ghid nu a confirmat, pentru distribuiri interimare cu o cadență strict lunară, un temei legal specific; nu îl inventăm aici.

## Ce se greșește în practică

- Se calculează și se virează un singur impozit, la finalul anului, pentru toate plățile lunare cumulate — corect e ca fiecare plată lunară să genereze propriul calcul și propria scadență de virare (25 a lunii următoare acelei plăți).
- Se aplică aceeași cotă tuturor tranșelor plătite în cursul anului, chiar dacă distribuirea de bază s-a făcut într-o perioadă cu altă cotă în vigoare — cota corectă e cea valabilă la data **distribuirii**, nu a fiecărei plăți.
- Se confundă plățile eșalonate ale unui dividend deja distribuit cu distribuiri interimare noi, aprobate lunar — cele două situații au premise diferite și, pentru a doua, temeiul legal obișnuit citat vizează o cadență trimestrială, nu lunară.

## Ce face iConta.eu

Pentru dividende plătite în mai multe tranșe (inclusiv lunare), motorul de calcul din iConta.eu potrivește fiecare tranșă de plată cu distribuirile deschise, în ordine (FIFO), și calculează impozitul folosind cota valabilă la data fiecărei distribuiri corespunzătoare — nu o cotă unică aplicată la finalul anului. Într-un test confirmat pe acest mecanism, un dividend distribuit integral (10.000 lei) dar plătit parțial (6.000 lei) generează `baza1 = 6.000` și impozit calculat la cota în vigoare pentru distribuirea respectivă, rămânând valid la validarea oficială a formularului. Fiecare plată efectivă din contul 457 (debit) alimentează separat baza de impozitare din D205.

[iConta.eu](/)
