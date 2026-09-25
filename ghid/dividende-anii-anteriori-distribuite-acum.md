---
title: "Dividende din anii anteriori distribuite acum: D205"
description: "Ce cotă de impozit se aplică atunci când o firmă distribuie acum, printr-o hotărâre AGA nouă, profit acumulat din exerciții financiare anterioare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Dividende din anii anteriori distribuite acum: D205

O firmă nu e obligată să distribuie profitul chiar în anul în care l-a realizat — poate lăsa profitul „la rezultatul reportat" mai mulți ani și abia apoi să decidă, printr-o nouă hotărâre AGA, distribuirea lui ca dividende. Întrebarea care contează pentru D205 nu e din ce an provine profitul, ci în ce an se aprobă efectiv distribuirea lui acum.

## Temeiul legal

::: ghid-temei
„(7) Veniturile sub formă de dividende [...] se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor/sumelor reprezentând câștigul obținut ca urmare a deținerii de titluri de participare de către acționari/asociați/investitori. Termenul de virare a impozitului este până la data de 25 inclusiv a lunii următoare celei în care se face plata. În cazul dividendelor/câștigurilor obținute ca urmare a deținerii de titluri de participare, distribuite, dar care nu au fost plătite acționarilor/asociaților/investitorilor până la sfârșitul anului în care s-a aprobat distribuirea acestora, impozitul pe dividende/câștig se plătește până la data de 25 ianuarie inclusiv a anului următor distribuirii."
— Codul fiscal (Legea 227/2015), art. 97 alin. (7) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Distribuirea de dividende din profitul acumulat în anii anteriori (rezultatul reportat) e permisă legal: „Nu se vor putea distribui dividende decât din profituri determinate potrivit legii" (Legea 31/1990, art. 67 alin. (3), sursă: anaf_surse/legea_31_1990_societatile.txt) — condiția e ca profitul să fie determinat potrivit legii (situații financiare aprobate), nu ca el să provină din anul curent.
- Ce contează pentru impozitul pe dividende e momentul la care se APROBĂ distribuirea, nu exercițiul financiar din care provine profitul: CF art. 97 alin. (7) leagă obligația de reținere de „plata"/"distribuirea" dividendelor, nu de anul profitului distribuit.
- Cota aplicabilă e cea în vigoare la data distribuirii: dacă profitul din 2023 sau 2024 se distribuie acum, prin hotărâre aprobată în 2026, cota corectă e cea de la data acestei aprobări (16% de la 01.01.2026), nu cota din anul în care s-a realizat profitul.
- Dacă dividendul e distribuit acum, dar plata efectivă către asociați se face abia anul viitor, impozitul se virează până la 25 ianuarie al anului următor distribuirii — nu până la 25 a lunii următoare distribuirii.

## Ce se greșește în practică

- Se aplică din reflex cota din anul căruia îi aparține profitul distribuit (de exemplu cota de 8% valabilă în 2023), în loc de cota din anul în care se aprobă efectiv distribuirea acum.
- Se distribuie ca dividende sume care nu sunt, de fapt, profit determinat potrivit legii, ci rezerve care nu pot fi repartizate în acest fel (de exemplu rezerve legale).
- Se confundă data adunării generale care aprobă distribuirea cu data situațiilor financiare aferente profitului distribuit — cele două pot fi ani calendaristici diferiți, iar cota se leagă de prima, nu de a doua.

## Ce face iConta.eu

iConta.eu nu urmărește separat „din ce an provine" profitul distribuit — motorul de calcul citește cota aplicabilă din registrul central de cote (period-aware) pe baza datei reale la care nota contabilă creditează contul 457, adică data la care distribuirea e efectiv înregistrată în contabilitate. O distribuire înregistrată acum, în 2026, ia automat cota de 16% valabilă de la 01.01.2026, indiferent dacă profitul distribuit provine din 2023, 2024 sau 2025. Aplicația nu verifică și nu cere separat exercițiul financiar sursă al profitului — acea corectitudine (că suma distribuită chiar reprezintă profit legal determinat) rămâne responsabilitatea contabilului, la momentul aprobării și înregistrării distribuirii.

[iConta.eu](/)
