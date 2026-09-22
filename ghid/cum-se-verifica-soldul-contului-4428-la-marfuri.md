---
title: Cum se verifică soldul contului 4428 la mărfuri?
description: Soldul 4428 ar trebui să reprezinte TVA neexigibilă aferentă mărfurilor rămase nevândute în stoc, dar TVA descărcată lunar din acest cont e o aproximare pe cotă medie, nu o valoare calculată exact din bonurile fiscale ale lunii — verificarea periodică pe cote reale e obligatorie.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se verifică soldul contului 4428 la mărfuri?

Contul 4428 „Taxa pe valoarea adăugată neexigibilă” e un cont bifuncțional care, la metoda global-valorică, ține evidența TVA cuprinsă în prețul de vânzare al mărfurilor, dar care nu a devenit încă exigibilă pentru că marfa nu s-a vândut. Teoretic, soldul lui 4428 la un moment dat ar trebui să corespundă exact cu TVA aferentă mărfurilor rămase nevândute în stoc. În practică, felul în care se descarcă lunar TVA din acest cont e o aproximare, nu un calcul exact — și tocmai de-aia soldul lui merită verificat periodic separat.

## Temeiul legal

::: ghid-temei
> "Contul 4428 «Taxa pe valoarea adăugată neexigibilă» [...] este un cont bifuncțional. Soldul
> contului reprezintă taxa pe valoarea adăugată neexigibilă."
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt` — funcțiunile conturilor 371,
> 378, 4428 (grupa 37 "Mărfuri" și grupa 44).

> "*2) La calcularea procentului mediu de adaos comercial, soldul inițial al contului de mărfuri și
> valoarea intrărilor de mărfuri nu vor include TVA neexigibilă."
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, pct. 286 alin. (4), nota *2).

> "Articolul 281 Faptul generator pentru livrări de bunuri și prestări de servicii (1) Faptul
> generator intervine **la data livrării bunurilor** sau la data prestării serviciilor, în
> conformitate cu regulile stabilite de prezentul articol."
>
> "Articolul 282 Exigibilitatea pentru livrări de bunuri și prestări de servicii (1) **Exigibilitatea
> taxei intervine la data la care are loc faptul generator.**"
>
> — sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, art. 281 alin. (1) și art. 282 alin. (1).
:::

## De ce descărcarea din 4428 e o aproximare

TVA colectată efectiv la o vânzare devine exigibilă la data livrării (art. 281-282 Cod fiscal) și se înregistrează real, per bon fiscal, prin contul 4427. Contul 4428, în schimb, funcționează diferit: la intrare, marfa aduce cu ea o TVA „neexigibilă” calculată pe prețul de vânzare estimat; la vânzare, această TVA trebuie „transferată” din 4428 către exigibil, proporțional cu marfa efectiv ieșită din gestiune.

Problema practică: descărcarea lunară nu recalculează TVA-ul pe fiecare bon emis în lună (ar însemna reluarea structurii reale de cote a vânzărilor), ci aplică o cotă medie, dedusă din compoziția stocului cumulat de la 1 ianuarie (`tva_stoc / baza_stoc`) la totalul vânzărilor lunii. Dacă structura stocului (de exemplu, ponderea produselor la 11% față de cele la 21%) diferă de structura reală a vânzărilor din luna respectivă, suma descărcată din 4428 nu va coincide exact cu TVA colectată real prin casa de marcat.

::: ghid-exemplu
Stocul cumulat conține, valoric, 70% produse la cotă 11% și 30% la cotă 21% — cota medie ponderată rezultată e undeva sub 15%. Dacă însă luna respectivă a avut vânzări concentrate pe produsele la 21% (de exemplu o promoție pe băuturi alcoolice), TVA reală colectată prin bonuri e mai mare decât ce rezultă din aplicarea cotei medii de 15% la vânzările lunii — diferența rămâne „ascunsă” în soldul 4428, care nu se descarcă complet.
:::

## Ce se greșește în practică

- Se consideră soldul 4428 „corect prin construcție”, fără nicio verificare separată, pentru că aplicația a generat automat nota de descărcare.
- Se compară soldul 4428 doar cu soldul contabil al lunii anterioare, fără să se confrunte cu Z-urile de casă pe cote de TVA, care arată structura reală a vânzărilor.
- Se ignoră inventarierea anuală ca mecanism de corectare — orice eroare acumulată în aproximare se reflectă, până la următorul inventar fizic, în soldurile 371/378/4428.
- Se presupune că un sold 4428 „plauzibil” (pozitiv, de mărime rezonabilă) înseamnă automat că suma e corectă — plauzibilitatea nu e același lucru cu exactitatea.

## Ce face iConta.eu

`descarca_luna` calculează TVA de descărcat din 4428 astfel: `tva_vanzari = rc_707 × (tva_stoc / baza_stoc)`, unde `tva_stoc` și `baza_stoc` provin din soldurile și rulajele cumulate ale conturilor 371 și 4428 de la 1 ianuarie până la sfârșitul lunii cerute. Cu alte cuvinte, aplicația aproximează TVA-ul de descărcat pe baza structurii medii a stocului, nu pe baza mixului real de cote vândute efectiv în luna respectivă — o alegere de proiectare asumată explicit în codul aplicației, care marchează repartizarea proporțională directă din 4427 drept „riscantă”, fără alt detaliu.

Formula K/adaos în sine e verificată legal exact (pct. 286 alin. 4-8), inclusiv excluderea TVA neexigibile din numitor conform notei *2). Problema e specifică extinderii ei la TVA pe cote multiple, subiect pe care OMFP 1802/2014 nu îl tratează explicit. Recomandarea practică pentru verificarea soldului 4428: contabilul trebuie să compare periodic, din Z-urile de casă pe cote, structura reală a vânzărilor lunii cu structura medie folosită la descărcare, și să ajusteze manual dacă diferența devine semnificativă — mai ales înainte de depunerea decontului de TVA pe cote (D300).

[iConta.eu](/)
