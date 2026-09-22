---
title: Ce reguli se aplică la descărcarea gestiunii unei farmacii?
description: O farmacie vinde tipic la două cote de TVA — medicamentele la cota redusă de 11%, o parte din restul produselor la cota standard de 21% — ceea ce face ca aproximarea prin cotă medie folosită la descărcarea TVA din 4428 să conteze mai mult decât la un magazin cu sortiment omogen.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce reguli se aplică la descărcarea gestiunii unei farmacii?

O farmacie care aplică metoda global-valorică respectă exact aceleași reguli ca orice alt comerț cu amănuntul cu sortiment numeros: recepție cu cotă de TVA explicită pe fiecare produs, inventar permanent (nu intermitent), descărcare lunară pe bază de coeficient de repartizare. Particularitatea unei farmacii e sortimentul: medicamentele beneficiază de cota redusă de TVA, în timp ce alte produse (cosmetice, suplimente, dispozitive medicale fără statut de medicament) pot fi la cota standard.

## Temeiul legal

::: ghid-temei
> "Articolul 291 Cotele (1) Cota standard [...] este **21%**. [...] (2) Cota redusă de **11%** se
> aplică asupra bazei de impozitare pentru [...] livrarea de medicamente de uz uman [...]
> alimente, inclusiv băuturi, destinate consumului uman și animal [...]"
>
> — sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, art. 291 alin. (1)-(2), formă în
> vigoare de la 01-08-2025 (Legea nr. 141/2025).

> "(5) Inventarul intermitent **nu se utilizează în comerțul cu amănuntul** în situația în care se
> aplică metoda global-valorică."
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, pct. 291 alin. (5).
:::

## Ce înseamnă sortimentul mixt pentru o farmacie

Codul fiscal menționează explicit medicamentele de uz uman la cota redusă de 11%. O farmacie tipică vinde însă și produse care nu se încadrează la medicamente — cosmetice, suplimente alimentare (uneori încadrate diferit), dispozitive medicale — care pot fi la cota standard de 21%. Practic, farmacia funcționează structural cu cel puțin două cote de TVA în paralel, la fel ca un magazin alimentar cu sortiment mixt, ceea ce face ca precizia descărcării TVA din 4428 să conteze mai mult decât la un magazin cu un singur tip de produs.

## Ce se greșește în practică

- Se presupune că toate produsele dintr-o farmacie au aceeași cotă de TVA, deși legea distinge explicit medicamentele (11%) de alte categorii de produse vândute în farmacie (de regulă 21%).
- Se omite declararea cotei de TVA per linie la NIR, presupunând o cotă „implicită” pentru farmacie, deși nu există o cotă unică valabilă pentru tot sortimentul.
- Se ține o singură sumă agregată pentru 378/4428 fără analitice pe cote, deși practica recomandă subconturi analitice (ex. 4428.11, 4428.21) tocmai pentru sortimentele mixte de cote.
- Se face inventar doar la final de perioadă (intermitent), deși legea impune inventar permanent pentru comerțul cu amănuntul care aplică metoda global-valorică.

## Ce face iConta.eu

Recepția fiecărui produs în farmacie trece prin două validări complementare: `adauga_nir` (stratul API) impune declararea explicită a cotei de TVA pe fiecare linie, iar `nir_gv` (motorul de calcul) refuză, la rândul lui, o cotă de TVA implicită nedeclarată la nivel de NIR — nu există o cotă implicită „de farmacie”, tocmai pentru că medicamentele (11%) și restul produselor (de regulă 21%) coexistă în același sortiment. Costul de achiziție se calculează inclusiv cu transportul și taxele capitalizate, iar adaosul rezultă din diferența față de prețul de vânzare, cu TVA extras prin formula sutei mărite pentru fiecare linie, la cota ei proprie.

La descărcarea lunară, `descarca_luna` calculează coeficientul K din rulajele cumulate ale conturilor 371, 378 și 4428, apoi îl aplică la vânzările lunii. TVA-ul descărcat din 4428 rămâne însă o aproximare: se calculează dintr-o cotă medie ponderată, dedusă din structura stocului cumulat de la 1 ianuarie, nu din mixul real de medicamente (11%) și alte produse (21%) vândute efectiv în lună. Pentru o farmacie, unde ponderea medicamentelor în vânzări poate varia sezonier (de exemplu creșterea vânzărilor de medicamente în lunile de iarnă), contabilul trebuie să verifice separat, din Z-urile de casă pe cote, că soldul 4428 rămas reflectă plauzibil marfa nevândută.

[iConta.eu](/)
