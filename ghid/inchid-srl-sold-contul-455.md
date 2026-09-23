---
title: Cum închid un SRL cu sold în contul 455?
description: Ce se întâmplă cu un sold rămas în contul 455 „Sume datorate acționarilor/asociaților" la lichidarea unei societăți și de ce nu se stinge automat prin operațiunea de partaj din iConta.eu.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum închid un SRL cu sold în contul 455?

Contul 455 „Sume datorate acționarilor/asociaților" ține, de regulă, împrumuturile pe care asociații le-au acordat societății (sau alte sume pe care firma le datorează asociaților, altele decât capitalul social sau profitul repartizat). Un sold rămas pe acest cont la data dizolvării nu dispare singur — el face parte din **pasivul** pe care lichidatorii trebuie să îl stingă înainte de radiere.

## Temeiul legal

::: ghid-temei
„Prin votul unanim al asociaților se poate hotărî și asupra modului în care activele rămase după plata creditorilor vor fi împărțite între asociați, caz în care la cererea de radiere a societății se anexează și dovada îndeplinirii obligației de calculare, reținere și plată a impozitului pe venit din lichidarea societății, prevăzută la art. 97 alin. (5) din Legea nr. 227/2015 privind Codul fiscal [...]. În lipsa acordului unanim privind împărțirea bunurilor, va fi urmată procedura lichidării prevăzută de prezenta lege."
— L31/1990, art. 235 alin. (2) (temeiul art. 227 alin. (4) trimite, pentru lichidarea și radierea societății, la dispozițiile art. 237 alin. (6)-(13))
:::

Textul de mai sus confirmă principiul general: **lichidarea presupune întâi plata creditorilor** (inclusiv a asociaților-creditori, dacă e cazul) și abia apoi repartizarea a ceea ce rămâne. Art. 235 alin. (1) din aceeași lege leagă explicit acordul de lichidare simplificată de faptul că asociații „asigură stingerea pasivului sau regularizarea lui în acord cu creditorii" — un sold pe 455 intră în această categorie de pasiv, alături de datoriile către furnizori sau alți terți.

## Ce se greșește în practică

Cea mai frecventă confuzie este între contul **455** (datorii ale societății către asociați, de regulă împrumuturi) și contul **456** „Decontări cu acționarii/asociații privind capitalul" — cel folosit efectiv la partajul final. Contabilii care rulează direct operația de „Partaj către asociați" din iConta.eu se așteaptă uneori ca soldul din 455 să fie preluat automat de această operație. Nu este cazul: motorul de lichidare din iConta.eu (`core/lichidare.py`, funcția `partaj`) operează explicit pe capital social, rezerve și profituri, toate contra contului 456, nu pe 455.

## Ce face iConta.eu

Funcția `partaj` din motorul de lichidare al iConta.eu produce trei tipuri de note contabile: capitalul social, tratat ca neimpozabil (1012=456); rezervele și profiturile, tratate ca „câștig impozabil" cu cota de impozit pe dividend (1061/1171=456, apoi 456=446 pentru impozit și 456=5121 pentru netul plătit asociatului). Contul 455 nu apare în această monografie predefinită.

Un sold pe 455 rămas la data lichidării trebuie deci stins separat, prin operațiunile obișnuite de plată/încasare din aplicație (de exemplu restituirea împrumutului către asociat), **înainte** de a rula operația de partaj — nu există în F057 o funcție dedicată de stingere automată a contului 455. Dosarul de cercetare nu a găsit local (în Anexele OMFP 897/2015, indisponibile în corpusul verificat) o monografie contabilă oficială specifică pentru acest caz, așa că tratamentul exact rămâne o decizie profesională a contabilului, aplicată prin operațiunile standard, nu prin ecranul de lichidare.

[iConta.eu](/)
