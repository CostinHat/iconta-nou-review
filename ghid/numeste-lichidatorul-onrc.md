---
title: "Cum se numește lichidatorul la ONRC"
description: "Procedura de numire a lichidatorului de către Oficiul Național al Registrului Comerțului, la dizolvarea unei societăți, potrivit Legii societăților 31/1990."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se numește lichidatorul la ONRC

Când o societate intră în dizolvare (fie prin hotărâre a asociaților, fie prin hotărâre judecătorească, fie din oficiu, pentru neîndeplinirea unor obligații), numirea lichidatorului nu se face automat de către asociați, ci — dacă nimeni nu depune cerere într-un anumit termen sau în anumite situații prevăzute de lege — de către Oficiul Național al Registrului Comerțului, prin registrator.

## Temeiul legal

::: ghid-temei
„După rămânerea definitivă a hotărârii judecătorești de dizolvare, Oficiul Național al Registrului Comerțului, prin registrator, la cererea societății, a oricărei persoane interesate sau din oficiu, numește, prin încheiere, un lichidator înscris în Tabloul practicienilor în insolvență. Remunerarea lichidatorului se face din averea societății dizolvate sau, în lipsă, din fondul de lichidare, constituit potrivit legii. Remunerația lichidatorului este în cuantum fix de 1.500 lei [...]"
— Legea 31/1990, art. 237 alin. (6) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

Cum funcționează, concret, numirea:

- **Lichidatorul trebuie să fie înscris în Tabloul practicienilor în insolvență** — nu poate fi numit lichidator orice persoană, ci doar un practician autorizat pentru acest tip de activitate.
- **Cererea de numire** poate veni de la societate, de la orice persoană interesată (de exemplu un creditor) sau **din oficiu**, la inițiativa ONRC.
- **Dacă în 3 luni de la rămânerea definitivă a hotărârii de dizolvare** nu s-a formulat nicio cerere de numire a lichidatorului, ONRC procedează, prin registrator, la radierea din oficiu a societății din registrul comerțului.
- **ANAF are un rol special**: dacă societatea în dizolvare are obligații bugetare restante sau este în curs de control fiscal, ANAF solicită ea însăși ONRC numirea unui lichidator, tocmai pentru a se evita radierea unei firme cu datorii nerecuperate.
- **Remunerația lichidatorului** e stabilită fix, prin lege, la 1.500 lei, plătită din averea societății dizolvate sau, în lipsă, din fondul de lichidare.
- Actul de numire se comunică electronic lichidatorului, se înregistrează în registrul comerțului și se publică în Buletinul electronic al registrului comerțului.

## Ce se greșește în practică

- Se presupune că lichidatorul poate fi orice contabil sau consultant al firmei — legea cere calitatea de practician înscris în Tabloul practicienilor în insolvență, indiferent cine formulează cererea de numire.
- Se lasă termenul de 3 luni de la dizolvare să treacă fără nicio cerere de numire, riscând radierea din oficiu a societății de către ONRC, cu toate consecințele asupra activelor și pasivelor rămase neclarificate.
- Se ignoră faptul că, dacă firma are datorii bugetare, ANAF poate cere ea însăși numirea unui lichidator — dizolvarea nu „stinge" automat obligațiile fiscale restante.

## Ce face iConta.eu

iConta.eu are un modul de calcul pentru operațiunile de lichidare (`core/lichidare.py`) — cota de lichidare aplicabilă, nota contabilă pentru vânzarea unui activ în cadrul lichidării și partajul capitalului social, rezervelor și profiturilor între asociați. La data acestui ghid, aplicația **nu are integrare cu ONRC** — nu depune cereri de numire a lichidatorului, nu urmărește termenul de 3 luni și nu interacționează cu Buletinul electronic al registrului comerțului. Procedura de numire a lichidatorului, cu depunerea cererii la ONRC, rămâne un demers separat, în afara aplicației.

[iConta.eu](/)
