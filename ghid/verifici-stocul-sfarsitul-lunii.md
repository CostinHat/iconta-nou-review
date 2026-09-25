---
title: "Cum verifici stocul la sfârșitul lunii?"
description: "Pașii de verificare a stocului contabil la finalul lunii: reconcilierea cu documentele sursă și, la final de exercițiu, cu inventarierea faptică."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verifici stocul la sfârșitul lunii?

Verificarea lunară a stocului nu înseamnă o inventariere fizică completă (care e obligatorie, de regulă, anual), ci o reconciliere între ce arată evidența contabilă (rulaje de intrări și ieșiri, sold) și documentele sursă din care acele mișcări au fost generate — facturi de achiziție, NIR-uri, facturi de vânzare, bonuri de consum.

## Temeiul legal

::: ghid-temei
„Registrul-inventar se completează pe baza inventarierii faptice a fiecărui cont de activ și de pasiv. [...] În cazul în care inventarierea are loc pe parcursul anului, în Registrul-inventar se înregistrează soldurile existente la data inventarierii, la care se adaugă rulajele intrărilor și se scad rulajele ieșirilor de la data inventarierii până la data încheierii exercițiului financiar."
— OMFP 2634/2015, Norme generale privind documentele financiar-contabile (sursă: anaf_surse/omfp_2634_2015.txt)
:::

Pașii utili pentru verificarea lunară:

- **Compară soldul final calculat cu suma dintre soldul inițial și rulajele lunii** (intrări minus ieșiri), pe fiecare gestiune și, dacă e relevant, pe fiecare articol — o diferență între calcul și soldul afișat indică fie o eroare de introducere, fie o operațiune netratată corect.
- **Verifică stocurile negative** — orice cantitate sub zero la finalul lunii e, prin definiție, o eroare de descărcare (vezi ghidul dedicat), nu o situație validă de raportat.
- **Reconciliază facturile de achiziție/vânzare cu mișcările de stoc generate** — o factură emisă fără mișcare de stoc corespunzătoare (sau invers) semnalează o problemă de flux, nu doar de cifre.
- **Pentru gestiunile cu costuri medii ponderate (CMP)**, verifică dacă recalcularea costului s-a făcut la fiecare intrare, nu doar la finalul lunii — o recalculare tardivă poate deforma costul de ieșire al vânzărilor din timpul lunii.
- Verificarea lunară nu înlocuiește inventarierea faptică obligatorie (de regulă anuală) — e un control intermediar, util tocmai pentru a limita erorile care ar ieși la iveală abia la inventarul de final de exercițiu.

## Ce se greșește în practică

- Se verifică doar soldul valoric total al gestiunii, fără a coborî pe articole individuale, ceea ce ascunde compensări între un articol cu stoc negativ și altul cu stoc supraevaluat.
- Se amână verificarea lunară „până la inventarul anual", acumulând astfel erori nedepistate pe parcursul mai multor luni, mai greu de urmărit retroactiv.
- Se confundă reconcilierea lunară (un control intern, pe bază de rapoarte) cu inventarierea faptică (numărarea fizică efectivă a stocului), tratând-o ca înlocuitor al acesteia.

## Ce face iConta.eu

Modulul de stocuri din iConta.eu (`core/stocuri_api.py`, `core/repo_stocuri.py`) oferă rapoarte de sold pe gestiune și articol, iar reconcilierea automată dintre facturi și mișcările de stoc e acoperită prin `core/stocuri_cv_api.py` (funcția `intrare_din_factura`), care creează intrarea cantitativă în fișa de magazie la validarea facturii de marfă, legată de aceasta prin `factura_id`. La data acestui ghid, aplicația **nu generează automat un raport lunar de excepții** (stocuri negative, diferențe de reconciliere) fără să fie cerut explicit — verificarea lunară a stocului rămâne un pas activ pe care contabilul îl parcurge, folosind rapoartele de stoc și de reconciliere oferite de aplicație.

[iConta.eu](/)
