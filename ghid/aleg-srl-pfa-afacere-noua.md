---
title: "Cum aleg între SRL și PFA pentru o afacere nouă în 2026"
description: "Dincolo de răspundere, SRL și PFA diferă în sarcina fiscală asupra veniturilor: PFA plătește CAS pe un venit ales de contribuabil, cu praguri de 12 și 24 de salarii minime brute, iar SRL impozitează separat profitul firmei și dividendele ridicate de asociat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum aleg între SRL și PFA pentru o afacere nouă în 2026

Odată lămurită chestiunea răspunderii, a doua întrebare practică e cât rămâne efectiv „în buzunar" din venitul realizat — iar mecanismele de calcul al contribuțiilor și impozitelor sunt structural diferite între PFA și SRL.

## Temeiul legal

::: ghid-temei
„(1) Persoanele fizice care în anul fiscal pentru care se depune Declarația unică [...] au realizat venituri din activitățile prevăzute la art. 137 alin. (1) lit. b) și b^1), din una sau mai multe surse și/sau categorii de venituri, a căror valoare anuală cumulată este cel puțin egală cu 12 salarii minime brute pe țară, datorează contribuția de asigurări sociale la o bază de calcul stabilită potrivit alin. (2).
(2) Baza anuală de calcul al contribuției de asigurări sociale [...] o reprezintă venitul ales de contribuabil, care nu poate fi mai mic decât: a) nivelul de 12 salarii minime brute pe țară, în cazul veniturilor realizate cuprinse între 12 salarii minime brute pe țară inclusiv și 24 de salarii minime brute pe țară; b) nivelul de 24 de salarii minime brute pe țară, în cazul veniturilor realizate cel puțin egale cu 24 de salarii minime brute pe țară."
— Codul fiscal (Legea 227/2015), art. 148 alin. (1)-(2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă, practic, în comparație cu un SRL:

- Un PFA datorează CAS doar dacă venitul anual cumulat din activități independente atinge pragul de **12 salarii minime brute pe țară**; sub acest prag, CAS nu e obligatorie (poate fi plătită opțional). Peste prag, baza de calcul e un venit ales de contribuabil, minimum 12 sau 24 de salarii minime, în funcție de nivelul veniturilor realizate — nu venitul net efectiv.
- Un SRL nu are acest mecanism: firma plătește impozit pe profit sau pe veniturile microîntreprinderii asupra rezultatului firmei, separat de contribuțiile sociale ale asociatului, care apar abia dacă acesta se autoangajează (salariu) sau ridică dividende (impozitate separat, cu o cotă proprie).
- Diferența practică: la venituri mici, PFA poate ieși mai avantajos (CAS opțională sub prag), dar la venituri mari sarcina CAS/CASS a PFA e plafonată la 24 de salarii minime, în timp ce la SRL antreprenorul poate structura mai flexibil ce ridică drept salariu vs. dividend, cu regimuri fiscale diferite pentru fiecare componentă.

## Ce se greșește în practică

- Se compară doar cota de impozitare nominală (10% impozit pe venit la PFA vs. 1%/3%/16% la SRL), fără să se ia în calcul CAS/CASS-ul datorat de PFA peste pragul de 12 salarii minime.
- Se presupune că plafonul CAS pentru PFA se calculează pe venitul net efectiv realizat, deși legea permite alegerea unei baze de calcul (minimum 12 sau 24 de salarii minime), diferită de venitul net.
- Se ignoră, la SRL, faptul că un antreprenor care se plătește doar din dividende nu datorează CAS/CASS pe acea sumă (regim diferit de venit din salarii), ceea ce schimbă complet calculul comparativ.

## Ce face iConta.eu

Pentru PFA, iConta.eu are motorul D212 (F030) live: calculează venitul net în sistem real, CAS și CASS pe plafoanele legale (6/12/24 salarii minime), alimentând Fișa D212. Pentru SRL, aplicația calculează impozitul pe profit sau pe veniturile microîntreprinderii (D101/D100) și impozitul pe dividende (D205). Aplicația **nu oferă însă o comparație directă**, pe același venit ipotetic, între sarcina fiscală totală a unui PFA și cea a unui SRL — fiecare calcul rulează separat, în funcție de forma juridică deja aleasă și introdusă în aplicație.

[iConta.eu](/)
