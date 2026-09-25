---
title: "Casierie la întreprinderea familială 2026: se aplică"
description: "Confirmarea că plafoanele legale de încasări și plăți în numerar se aplică și întreprinderilor familiale, nu doar SRL-urilor și PFA-urilor."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Casierie la întreprinderea familială 2026: se aplică

Da — întreprinderea familială intră explicit sub incidența legii care limitează operațiunile cu numerar. Legea nu face nicio distincție de formă juridică între societăți, PFA-uri, întreprinderi individuale sau întreprinderi familiale: toate sunt obligate să respecte aceleași plafoane de încasări și plăți în numerar.

## Temeiul legal

::: ghid-temei
„Operațiunile de încasări și plăți efectuate de persoane juridice, persoane fizice autorizate, întreprinderi individuale, întreprinderi familiale, liber profesioniști, persoane fizice care desfășoară activități în mod independent, asocieri și alte entități cu sau fără personalitate juridică de la/către oricare dintre aceste categorii de persoane se vor realiza numai prin instrumente de plată fără numerar, definite potrivit legii."
— Legea nr. 70/2015 pentru întărirea disciplinei financiare privind operațiunile de încasări și plăți în numerar, art. 1 (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

- Întreprinderea familială este menționată explicit, alături de PFA și întreprinderea individuală, printre entitățile vizate — nu există o excepție pentru forma organizatorică simplificată.
- Regula generală este plata prin instrumente fără numerar; numerarul rămâne permis doar în condițiile și plafoanele expres prevăzute de lege (de exemplu, plafonul de 5.000 lei/10.000 lei pentru încasări de la o persoană, respectiv plafonul zilnic de 10.000 lei pentru plăți către o persoană fizică).
- Sunt interzise **încasările sau plățile fragmentate** în numerar, folosite pentru a evita plafonul legal — fracționarea unei facturi peste plafon în mai multe tranșe încasate cash este ea însăși o încălcare a legii, distinctă de depășirea plafonului în sine.
- Membrii întreprinderii familiale rămân obligați, ca și un SRL sau un PFA, să țină un registru de casă pentru operațiunile în numerar efectiv realizate.

## Ce se greșește în practică

- Se presupune că doar societățile comerciale (SRL, SA) sunt vizate de Legea 70/2015, iar formele mai simple (întreprindere familială, PFA) ar fi scutite — fals, legea le include expres.
- Se fragmentează încasările de la același client, în aceeași zi sau săptămână, pentru a rămâne „tehnic" sub plafon — practică interzisă explicit ca „încasare fragmentată".
- Se confundă plafonul aplicabil între entități cu personalitate juridică/fără personalitate juridică (5.000/10.000 lei) cu plafonul aplicabil plăților către persoane fizice (10.000 lei/zi/persoană), care sunt reguli distincte.
- Nu se ține un registru de casă actualizat zilnic, considerându-se că formalitățile de casierie „nu se aplică" la o structură atât de mică precum întreprinderea familială.

## Ce face iConta.eu

Din verificarea codului, iConta.eu are în modulul de casierie (`casa.py`/`casa_api.py`) o funcție de **verificare automată a plafonului legal de numerar** pentru operațiunile înregistrate în registrul de casă, iar aceasta se aplică indiferent de tipul de firmă. Trebuie spus onest, însă, că modelul intern al aplicației distinge firmele doar pe două tipuri, „srl" și „pfa" (care decid regimul contabil — partidă dublă, respectiv partidă simplă) — nu există un tip distinct „întreprindere familială" în aplicație. O întreprindere familială, care ține contabilitate în partidă simplă la fel ca un PFA, ar fi operată în iConta.eu sub regimul de partidă simplă; verificarea plafonului de casă din Legea 70/2015 se aplică în continuare, dar denumirea exactă a formei juridice nu este reflectată ca atare în profilul firmei.

[iConta.eu](/)
