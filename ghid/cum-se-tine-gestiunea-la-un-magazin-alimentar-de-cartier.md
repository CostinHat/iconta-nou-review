---
title: Cum se ține gestiunea la un magazin alimentar de cartier?
description: Un magazin alimentar cu sortiment numeros și marje similare poate ține mărfurile în regim global-valoric (metoda prețului cu amănuntul), dar sortimentul mixt de cote TVA (11%/21%) cere atenție la NIR și la descărcarea lunară.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se ține gestiunea la un magazin alimentar de cartier?

Un magazin alimentar de cartier are exact profilul pentru care legea permite metoda prețului cu amănuntul: multe articole, mișcare rapidă, marje similare pe categorii. Practic, magazinul nu ține o fișă de magazie pe fiecare produs, ci evidențiază mărfurile la valoare, în regim global-valoric (F088), cu adaosul comercial separat în contul 378 și TVA neexigibilă în 4428.

## Temeiul legal

::: ghid-temei
> "286. - (1) În funcție de specificul activității, pentru determinarea costului pot fi folosite,
> de asemenea, metoda costului standard, în activitatea de producție sau **metoda prețului cu
> amănuntul, în comerțul cu amănuntul**."
>
> "(8) În comerțul cu amănuntul poate fi utilizată metoda prețului cu amănuntul, pentru a determina
> costul stocurilor de articole numeroase și cu mișcare rapidă, care au marje similare și pentru
> care nu este practic să se folosească altă metodă. În această situație, **costul bunurilor
> vândute se calculează prin deducerea valorii marjei brute din prețul de vânzare al stocurilor**.
> Orice modificare a prețului de vânzare presupune recalcularea marjei brute."
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, pct. 286 alin. (1) și (8).

> "(5) Inventarul intermitent **nu se utilizează în comerțul cu amănuntul** în situația în care se
> aplică metoda global-valorică."
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, pct. 291 alin. (5).
:::

## Sortimentul mixt de cote TVA

Un magazin alimentar vinde de regulă atât produse la cota redusă (alimente, băuturi nealcoolice) cât și produse la cota standard (băuturi alcoolice, produse de igienă, alte nealimentare). La fiecare recepție (NIR), pentru fiecare linie de marfă trebuie declarată explicit cota de TVA cu care s-a vândut acea marfă — nu există o cotă implicită, tocmai pentru că un magazin alimentar lucrează efectiv cu cel puțin două cote în paralel.

::: ghid-exemplu
La un NIR cu 100 buc. suc la 5 lei/buc (cota 21%) și 200 buc. pâine la 4 lei/buc (cota 11%):
- linia suc: preț vânzare cu TVA = 500 lei, din care TVA = 500 × 21/121 ≈ 86,78 lei;
- linia pâine: preț vânzare cu TVA = 800 lei, din care TVA = 800 × 11/111 ≈ 79,28 lei.

Fiecare linie își păstrează propria cotă — nu se aplică o cotă „medie” la nivel de NIR.
:::

## Ce se greșește în practică

- Se lasă cota de TVA necompletată sau se presupune o cotă unică pentru tot magazinul, deși sortimentul e mixt.
- Se confundă inventarul permanent (obligatoriu la metoda global-valorică) cu inventarul intermitent, specific altor forme de comerț cu amănuntul — la global-valoric fiecare recepție trebuie înregistrată imediat în 371/378/4428, nu doar constatată la un inventar periodic.
- Se ține o singură sumă agregată pentru 378/4428, fără analitice pe cote, ceea ce face mai greu de verificat ulterior câtă TVA neexigibilă aparține produselor la 11% față de cele la 21%.
- Se schimbă prețul de vânzare fără recalcularea adaosului aferent stocului deja existent.

## Ce face iConta.eu

Recepția (NIR) în regim global-valoric trece prin două validări complementare: `adauga_nir` (stratul API) impune declararea explicită a cotei de TVA pe fiecare linie, iar `nir_gv` (motorul de calcul) refuză, la rândul lui, o cotă de TVA implicită nedeclarată la nivel de NIR — exact pentru a evita o cotă „scrisă în cod” care se rupe tăcut la o schimbare legislativă a cotelor (cum a fost trecerea 19%/9% → 21%/11%). Costul de achiziție se calculează din cantitate × preț achiziție, la care se adaugă transportul și taxele capitalizate, repartizate proporțional pe linii. TVA se extrage din prețul de vânzare cu formula „sută mărită”, iar adaosul rezultă ca diferență (preț vânzare − TVA − cost); aplicația nu permite adaos negativ.

La finalul lunii, `descarca_luna` calculează coeficientul de repartizare K din rulajele cumulate ale conturilor 371, 378 și 4428, apoi îl aplică la vânzările lunii (contul 707) pentru a obține automat costul mărfii vândute și adaosul de descărcat. TVA-ul descărcat din 4428 este însă o aproximare: se calculează dintr-o cotă medie ponderată, dedusă din structura stocului cumulat de la 1 ianuarie, nu din mixul real de cote vândute efectiv în lună. Pentru un magazin cu sortiment mixt, unde produsele la 11% și 21% se vând în proporții diferite lună de lună, contabilul trebuie să verifice separat — din Z-urile de casă pe cote — că soldul rămas în 4428 reflectă plauzibil marfa nevândută.

[iConta.eu](/)
