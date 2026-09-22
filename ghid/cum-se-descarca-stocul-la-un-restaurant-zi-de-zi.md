---
title: Cum se descarcă stocul la un restaurant, zi de zi?
description: Vânzările zilnice ale unui restaurant alimentează rulajul lunar al contului 707, dar descărcarea de gestiune propriu-zisă (coeficientul de repartizare aplicat la costul mărfii vândute) se face lunar, nu în fiecare zi.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se descarcă stocul la un restaurant, zi de zi?

Un restaurant care aplică metoda global-valorică înregistrează vânzările în fiecare zi (bonuri fiscale, facturi), dar descărcarea de gestiune — trecerea costului mărfii vândute din 371 în 607, cu adaosul aferent din 378 și TVA neexigibilă din 4428 — nu se face zilnic. Legea cere calculul coeficientului de repartizare cumulat de la începutul exercițiului financiar, iar acest calcul, aplicat vânzărilor, se face de regulă la finalul fiecărei luni.

## Temeiul legal

::: ghid-temei
> "(4) Repartizarea diferențelor de preț asupra valorii bunurilor ieșite și asupra stocurilor se
> efectuează cu ajutorul unui coeficient care se calculează astfel:
>
> Coeficient de repartizare = [Soldul inițial al diferențelor de preț + Diferențe de preț aferente
> intrărilor în cursul perioadei, cumulat de la începutul exercițiului financiar până la finele
> perioadei de referință] / [Soldul inițial al stocurilor de preț de înregistrare + Valoarea
> intrărilor în cursul perioadei la preț de înregistrare, cumulat de la începutul exercițiului
> financiar până la finele perioadei de referință] × 100
>
> *2) La calcularea procentului mediu de adaos comercial, soldul inițial al contului de mărfuri și
> valoarea intrărilor de mărfuri nu vor include TVA neexigibilă. Acest coeficient se înmulțește
> cu valoarea bunurilor ieșite din gestiune la preț de înregistrare, iar suma rezultată se
> înregistrează în conturile corespunzătoare în care au fost înregistrate bunurile ieșite."
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, pct. 286 alin. (4) și nota *2).

> "(5) Inventarul intermitent **nu se utilizează în comerțul cu amănuntul** în situația în care se
> aplică metoda global-valorică."
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, pct. 291 alin. (5).
:::

## Ce se întâmplă zilnic și ce se întâmplă lunar

Zilnic: fiecare vânzare (bon de casă, notă de plată) alimentează rulajul creditor al contului 707 „Venituri din vânzarea mărfurilor”. Aceste înregistrări zilnice sunt cele care fac obligatorie evidența permanentă (nu intermitentă) la metoda global-valorică — stocul din 371 trebuie să reflecte, teoretic, situația reală în orice moment, chiar dacă descărcarea contabilă a costului nu se face zi de zi.

Lunar: se adună rulajul total al lui 707 pe luna respectivă, se calculează coeficientul K din soldurile și rulajele cumulate ale conturilor 371, 378 și 4428 de la 1 ianuarie, apoi K se aplică la vânzările lunii pentru a obține costul mărfii vândute (607) și adaosul descărcat (378).

## Ce se greșește în practică

- Se așteaptă ca aplicația să genereze o „descărcare zilnică” a gestiunii — de fapt, doar vânzările se înregistrează zilnic, descărcarea contabilă e un calcul lunar cumulat.
- Se face descărcarea lunii curente fără să se verifice dacă toate bonurile/facturile zilei au fost efectiv validate în sistem — o venituri din vânzări (707) neînregistrat la timp înseamnă un K aplicat la o bază incompletă.
- Se crede greșit că, neexistând descărcare zilnică, restaurantul poate ține inventar intermitent (doar la sfârșit de perioadă) — legea interzice explicit acest lucru la metoda global-valorică.
- Se ignoră lunile fără nicio vânzare (zile de închidere sezonieră, de exemplu) presupunând că „nu e nimic de făcut” — funcția de descărcare tot trebuie rulată, chiar dacă nu generează note contabile.

## Ce face iConta.eu

Fiecare vânzare zilnică alimentează rulajul contului 707, filtrat din sursele de vânzare configurate (ex. `horeca_z` pentru bonurile de casă din HoReCa, `stocuri`, `facturi_marfa`). La finalul lunii, `descarca_luna` adună soldurile inițiale de exercițiu ale conturilor 371, 378, 4428, cumulează rulajele acestor conturi de la 1 ianuarie până la sfârșitul lunii cerute, dar ia vânzările (rulajul creditor al 707) doar pe luna curentă. Dacă în luna respectivă nu există nicio vânzare de mărfuri (`rc_707 == 0`), funcția nu generează note contabile, ci întoarce un rezultat structurat care consemnează explicit acest fapt — nu o eroare.

Odată calculat, coeficientul K se aplică la vânzările lunii pentru a obține costul mărfii vândute (607=371) și adaosul descărcat (378=371). TVA-ul descărcat din 4428 rămâne însă o aproximare, calculată dintr-o cotă medie ponderată a stocului, nu din mixul real de cote al bonurilor emise în acea lună — relevant mai ales dacă restaurantul vinde atât produse la cotă redusă (mâncare/băuturi nealcoolice servite), cât și produse la cotă standard (băuturi alcoolice, vânzări la pachet).

[iConta.eu](/)
