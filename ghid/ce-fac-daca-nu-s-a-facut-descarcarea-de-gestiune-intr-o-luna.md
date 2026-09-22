---
title: Ce fac dacă nu s-a făcut descărcarea de gestiune într-o lună?
description: O lună omisă nu se pierde definitiv — coeficientul de repartizare, calculat cumulat de la 1 ianuarie, o include automat la prima descărcare ulterioară, dar vânzările lunii omise trebuie descărcate explicit pentru acea lună anume, altfel rămân nedescărcate din 371/378/4428.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce fac dacă nu s-a făcut descărcarea de gestiune într-o lună?

La metoda global-valorică, descărcarea lunară nu e o simplă formalitate care „se pierde” dacă e omisă — coeficientul de repartizare se calculează cumulat de la începutul exercițiului financiar, ceea ce înseamnă că orice notă validată dintr-o lună anterioară, chiar omisă la momentul respectiv, va intra automat în calcul la următoarea descărcare. Dar asta nu înseamnă că nu mai trebuie făcut nimic — vânzările lunii omise au nevoie de o rulare separată, pentru acea lună anume.

## Temeiul legal

::: ghid-temei
> "(4) Repartizarea diferențelor de preț asupra valorii bunurilor ieșite și asupra stocurilor se
> efectuează cu ajutorul unui coeficient care se calculează astfel:
>
> Coeficient de repartizare = [Soldul inițial al diferențelor de preț + Diferențe de preț aferente
> intrărilor în cursul perioadei, cumulat de la începutul exercițiului financiar până la finele
> perioadei de referință] / [Soldul inițial al stocurilor de preț de înregistrare + Valoarea
> intrărilor în cursul perioadei la preț de înregistrare, cumulat de la începutul exercițiului
> financiar până la finele perioadei de referință] × 100"
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, pct. 286 alin. (4).

> "Articolul 6 (1) Orice operațiune economico-financiară efectuată se consemnează în momentul
> efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind
> astfel calitatea de document justificativ. (2) Documentele justificative care stau la baza
> înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și
> aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
>
> "Articolul 7 (1) Persoanele prevăzute la art. 1 au obligația să efectueze **inventarierea
> generală** a elementelor de natura activelor, datoriilor și capitalurilor proprii deținute la
> începutul activității, **cel puțin o dată în cursul exercițiului financiar**, precum și în cazul
> fuziunii, divizării ori transformării sau al lichidării și în alte situații prevăzute de lege."
>
> — sursă: `anaf_surse/legea_82_1991_consolidat.txt`, art. 6 și art. 7 alin. (1).
:::

## Ce se recuperează automat și ce nu

Rulajele conturilor 371, 378 și 4428 se cumulează de la 1 ianuarie până la sfârșitul lunii pentru care se face descărcarea, pe baza notelor deja validate — indiferent când au fost efectiv validate acele note. Așadar, dacă în februarie a existat un NIR validat cu întârziere, coeficientul K calculat pentru o descărcare ulterioară (de exemplu în aprilie) îl va include automat, pentru că rulajele cumulate „văd” toate notele validate din interval, nu doar pe cele înregistrate la timp.

Vânzările (contul 707), în schimb, se iau întotdeauna doar pe luna pentru care se rulează explicit descărcarea — nu cumulat. Dacă descărcarea lunii omise nu e rulată separat pentru acea lună anume, vânzările acelei luni nu vor fi niciodată descărcate din 371/378/4428, deși deja influențează coeficientul K al lunilor următoare prin soldurile și rulajele cumulate ale conturilor de marfă și diferențe de preț. Practic, se poate ajunge la o dublă influențare: luna omisă contribuie la K-ul lunilor viitoare, dar propriile ei vânzări rămân nedescărcate.

## Ce se greșește în practică

- Se sare direct la descărcarea lunii curente, presupunând că luna omisă „s-a recuperat singură” prin cumul — de fapt doar rulajele 371/378/4428 se recuperează automat, nu și descărcarea vânzărilor lunii respective.
- Se rulează descărcarea pentru luna omisă abia după ce s-au acumulat mai multe luni nedescărcate, fără să se verifice ordinea cronologică — descărcarea fiecărei luni omise trebuie făcută pentru luna ei exactă, nu contopită cu luna curentă.
- Se ignoră inventarierea anuală ca mecanism de corectare a erorilor acumulate — o eroare dintr-o lună omisă, dacă nu e corectată la timp, rămâne în soldurile 371/378/4428 până la următorul inventar fizic.
- Se presupune că absența unei descărcări lunare invalidează retroactiv NIR-urile deja validate din luna respectivă — de fapt NIR-urile rămân valide ca documente justificative (art. 6 Legea 82/1991), doar descărcarea contabilă a costului/adaosului/TVA a fost omisă.

## Ce face iConta.eu

`descarca_luna` calculează soldurile inițiale de exercițiu (371, 378, 4428) din `solduri_initiale`, apoi cumulează rulajele acestor conturi de la începutul anului până la sfârșitul lunii cerute, folosind toate notele validate din interval — indiferent de data la care au fost efectiv validate. Vânzările de mărfuri (contul 707) se iau însă doar pe luna curentă cerută la apel, filtrate pe sursele configurate.

Consecința practică: dacă o lună a fost omisă, rulajele cumulate ale lunilor următoare includ automat notele validate din luna omisă, dar vânzările acelei luni nu se descarcă decât dacă `descarca_luna` este rulată explicit pentru luna respectivă. Recomandarea e să se ruleze descărcarea pentru luna omisă înainte de a trece la luna curentă, în ordine cronologică — altfel vânzările lunii omise rămân permanent nedescărcate din 371/378/4428, deși deja influențează coeficientul K aplicat lunilor ulterioare.

[iConta.eu](/)
