---
title: "În câți ani se amortizează un calculator?"
description: "Durata normală de funcționare a calculatoarelor și echipamentelor periferice, conform catalogului oficial, și cum calculează iConta.eu amortizarea lunară odată ce durata e stabilită."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# În câți ani se amortizează un calculator?

Durata de amortizare a unui calculator nu se alege liber — vine dintr-un catalog oficial, care stabilește pentru fiecare categorie de mijloc fix un interval (minim-maxim) de ani, iar durata exactă, în interiorul intervalului, se fixează o singură dată, la punerea în funcțiune.

## Temeiul legal

::: ghid-temei
„2.2.9. Calculatoare electronice și echipamente periferice. Mașini și aparate de casă, control și facturat. 2-4 [ani]"

„În prezentul catalog pentru fiecare mijloc fix nou achiziționat se utilizează sistemul unor plaje de ani cuprinse între o valoare minima și una maxima, existând astfel posibilitatea alegerii duratei normale de funcționare cuprinsa între aceste limite. Astfel stabilita, durata normala de funcționare a mijlocului fix rămâne neschimbata până la recuperarea integrală a valorii de intrare a acestuia sau scoaterea sa din funcțiune."
— HG 2139/2004, Catalogul privind clasificarea și duratele normale de funcționare a mijloacelor fixe, poziția 2.2.9 și pct. I.4 (sursă: anaf_surse/hg_2139_2004_catalog_clasificare_durate_mijloace_fixe.txt)
:::

Ce rezultă de aici:

- Un **calculator electronic sau echipament periferic** are, potrivit catalogului, o **durată normală de funcționare între 2 și 4 ani**.
- Firma alege durata exactă (2, 3 sau 4 ani) **o singură dată, la punerea în funcțiune** — nu se poate schimba ulterior, decât prin epuizarea completă a amortizării sau scoaterea din funcțiune a mijlocului fix.
- Pentru a fi mijloc fix amortizabil (nu cheltuială directă), calculatorul trebuie să aibă o valoare fiscală de intrare peste pragul stabilit de Codul fiscal (art. 28 alin. (2) lit. b), actualizat periodic prin hotărâre a Guvernului) și o durată normală de utilizare mai mare de un an.

## Ce se greșește în practică

- Se aplică o durată de amortizare aleasă arbitrar, în afara intervalului 2-4 ani stabilit de catalog pentru calculatoare.
- Se schimbă durata de amortizare pe parcurs, pentru a accelera sau încetini recuperarea valorii, deși legea o fixează la punerea în funcțiune.
- Se amortizează ca mijloc fix un calculator sub pragul valoric minim, în loc să fie trecut direct pe cheltuială.

## Ce face iConta.eu

iConta.eu are un modul real de evidență a mijloacelor fixe (`core/repo_mijloace_fixe.py`, `core/d406_active.py`), care calculează automat amortizarea lunară — liniară sau accelerată, după caz — odată ce mijlocul fix e introdus cu valoarea, valoarea reziduală și durata normală de funcționare (exprimată în luni). Aplicația nu preia însă automat durata din catalogul HG 2139/2004 — contabilul introduce direct durata aleasă (de exemplu, 36 de luni pentru un calculator amortizat în 3 ani), iar aplicația nu verifică dacă acea durată se încadrează în intervalul legal al categoriei respective.

[iConta.eu](/)
