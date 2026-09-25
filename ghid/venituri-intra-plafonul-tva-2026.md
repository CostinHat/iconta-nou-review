---
title: "Ce venituri intră în plafonul de TVA în 2026"
description: "Ce se cuprinde și ce se exclude din cifra de afaceri care determină depășirea plafonului de scutire de TVA pentru întreprinderile mici."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce venituri intră în plafonul de TVA în 2026

Firmele neplătitoare de TVA urmăresc constant un singur indicator: cifra de afaceri anuală, raportată la plafonul de scutire. Depășirea lui declanșează obligația de înregistrare în scopuri de TVA. Problema practică nu e plafonul în sine, ci ce anume se cuprinde în calculul cifrei de afaceri relevante.

## Temeiul legal

::: ghid-temei
„(1) Persoana impozabilă stabilită în România [...], a cărei cifră de afaceri anuală, declarată sau realizată, nu depășește plafonul de 395.000 lei, poate aplica scutirea de taxă, denumită în continuare regim special de scutire, pentru operațiunile prevăzute la art. 268 alin. (1), cu excepția livrărilor intracomunitare de mijloace de transport noi, scutite conform art. 294 alin. (2) lit. b).
(2) Cifra de afaceri care servește drept referință pentru aplicarea alin. (1) este constituită din valoarea totală, exclusiv taxa [...], a livrărilor de bunuri și a prestărilor de servicii efectuate de persoana impozabilă în cursul unui an calendaristic, taxabile sau, după caz, care ar fi taxabile dacă nu ar fi desfășurate de o mică întreprindere, a operațiunilor scutite cu drept de deducere și, dacă nu sunt accesorii activității principale, a operațiunilor scutite fără drept de deducere prevăzute la art. 292 alin. (2) lit. a), b), e) și f) [...]. Prin excepție, nu se cuprind în cifra de afaceri prevăzută la alin. (1) livrările de active fixe corporale [...] și cesiunea/transferul de active necorporale, efectuate de persoana impozabilă."
— Legea nr. 227/2015 (Codul fiscal), art. 310 alin. (1)-(2), în forma în vigoare de la 1 septembrie 2025 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Plafonul de scutire pentru 2026 este **395.000 lei** (ridicat de la 300.000 lei prin OG nr. 22/2025, în vigoare din 1 septembrie 2025). Ce intră efectiv în calcul:

- **Se cuprind**: toate livrările de bunuri și prestările de servicii taxabile (sau care ar fi taxabile în regim normal), operațiunile scutite cu drept de deducere, plus operațiunile scutite fără drept de deducere de la art. 292 alin. (2) lit. a), b), e) și f) — dacă nu sunt accesorii activității principale.
- **Nu se cuprind**: livrările de active fixe corporale (de exemplu vânzarea unui utilaj sau a unei clădiri folosite în activitate) și cesiunea/transferul de active necorporale — acestea sunt excluse explicit, indiferent de valoare.
- Depășirea plafonului obligă la înregistrare în scopuri de TVA **cel târziu la data depășirii**, cu aplicarea regimului normal din tranzacția care a condus la depășire.

## Ce se greșește în practică

- Se include în calculul plafonului valoarea obținută din vânzarea unui mijloc fix (echipament, autoturism, clădire folosită de firmă) — deși legea îl exclude explicit din cifra de afaceri relevantă.
- Se ignoră operațiunile scutite fără drept de deducere care totuși trebuie cuprinse (de exemplu anumite servicii financiare, dacă nu sunt accesorii activității principale), considerându-se, greșit, că „scutit" înseamnă automat „exclus din plafon".
- Se aplică vechiul plafon de 300.000 lei, deși de la 1 septembrie 2025 plafonul de referință este 395.000 lei.

## Ce face iConta.eu

Verificat în cod: `core/common.py` ține un registru intern de plafoane fiscale cu temei citat (de exemplu plafonul TVA la încasare, plafoanele operațiunilor cu numerar), dar la data acestui ghid **nu conține pragul de 395.000 lei pentru regimul special de scutire pentru întreprinderile mici** — nu există în aplicație o funcție dedicată care să calculeze automat cifra de afaceri relevantă (cu excluderea activelor fixe cedate) și să semnaleze apropierea sau depășirea acestui plafon. Verificarea încadrării în plafonul de scutire de TVA rămâne, deocamdată, o urmărire manuală a contabilului, pe baza facturilor emise.

[iConta.eu](/)
