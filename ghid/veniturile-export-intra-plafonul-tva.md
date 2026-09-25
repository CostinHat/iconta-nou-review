---
title: "Veniturile din export intră în plafonul de TVA?"
description: "Dacă livrările la export contează în cifra de afaceri de referință pentru plafonul de scutire de TVA al întreprinderilor mici."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Veniturile din export intră în plafonul de TVA?

Exportul e scutit de TVA, cu drept de deducere — dar „scutit de taxă" nu înseamnă „scutit de calcul". Când verifici dacă o firmă a depășit plafonul de scutire pentru întreprinderile mici, veniturile din export nu se dau la o parte: intră direct în cifra de afaceri de referință.

## Temeiul legal

::: ghid-temei
„Cifra de afaceri care servește drept referință pentru aplicarea alin. (1) este constituită din valoarea totală, exclusiv taxa [...], a livrărilor de bunuri și a prestărilor de servicii efectuate de persoana impozabilă în cursul unui an calendaristic, taxabile sau, după caz, care ar fi taxabile dacă nu ar fi desfășurate de o mică întreprindere, a operațiunilor scutite cu drept de deducere și, dacă nu sunt accesorii activității principale, a operațiunilor scutite fără drept de deducere prevăzute la art. 292 alin. (2) lit. a), b), e) și f), cu locul în România. Prin excepție, nu se cuprind în cifra de afaceri prevăzută la alin. (1) livrările de active fixe corporale [...] și cesiunea/transferul de active necorporale, efectuate de persoana impozabilă."
— Codul fiscal (Legea 227/2015), art. 310 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Exportul (livrări de bunuri expediate în afara Uniunii Europene) e o operațiune **scutită cu drept de deducere**, conform art. 294 alin. (1) lit. a)-b) Cod fiscal — și textul de mai sus include explicit „operațiunile scutite cu drept de deducere" în cifra de afaceri de referință pentru plafon.
- Plafonul de scutire pentru întreprinderile mici este, la acest moment, de **395.000 lei** (art. 310 alin. 1), valabil pentru operațiuni cu locul în România — cifra de afaceri relevantă se calculează în lei, cumulat pe anul calendaristic.
- Singurele excluderi explicite din cifra de afaceri de referință sunt livrările de active fixe corporale și cesiunea/transferul de active necorporale — exportul de bunuri din activitatea curentă nu se încadrează la nicio excepție.
- Depășirea plafonului obligă la înregistrarea în scopuri de TVA cel târziu la data depășirii, cu aplicarea regimului normal de taxare de la tranzacția care a dus la depășire (art. 310 alin. 6).

## Ce se greșește în practică

- Se presupune, din faptul că exportul „nu are TVA de plată", că veniturile din export nu contează deloc pentru plafon — de fapt exact operațiunile scutite cu drept de deducere (categoria din care face parte exportul) sunt incluse explicit în calcul.
- Se confundă plafonul de scutire pentru întreprinderi mici (art. 310, azi 395.000 lei) cu plafonul pentru perioada fiscală trimestrială de TVA (art. 322, 100.000 euro) — sunt praguri diferite, cu scopuri diferite.
- Se scad din cifra de afaceri livrările de bunuri către export, presupunând că se aplică aceeași excludere ca la activele fixe corporale — excluderea din lege vizează strict vânzarea de active fixe/necorporale, nu vânzările curente către clienți din afara UE.

## Ce face iConta.eu

Modulul de import/export extracomunitar din iConta calculează corect baza de TVA la import și validează dovada de export (declarația vamală de export) pentru a confirma scutirea cu drept de deducere de la art. 294 — dar aplicația **nu are un modul dedicat care să urmărească plafonul cumulat anual de 395.000 lei** al regimului de scutire pentru întreprinderi mici. Nu există în cod niciun calcul care să adune veniturile anului (inclusiv cele din export) și să le compare automat cu acest prag. Verificarea depășirii plafonului de scutire, inclusiv includerea corectă a veniturilor din export, rămâne o decizie profesională a contabilului, făcută în afara aplicației.

[iConta.eu](/)
