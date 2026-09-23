---
title: Unde găsești durata normală de funcționare pentru un mijloc fix?
description: Duratele normale de funcționare pentru fiecare tip de mijloc fix sunt publicate în catalogul oficial aprobat prin HG 2139/2004, organizat pe trei grupe și coduri de clasificare, fiecare cu un interval minim-maxim de ani.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Unde găsești durata normală de funcționare pentru un mijloc fix?

Sursa oficială e un singur document: **catalogul privind clasificarea și duratele normale de funcționare a mijloacelor fixe**, aprobat prin HG 2139/2004. Fiecare tip de activ are alocat un cod de clasificare, iar fiecărui cod îi corespunde un interval (plajă) de ani, nu o singură cifră fixă.

## Temeiul legal

::: ghid-temei
Astfel mijloacele fixe amortizabile au fost clasificate în trei grupe principale și anume: – Grupa 1 - Construcții; [...] – Grupa 2 - Instalații tehnice, mijloace de transport, animale și plantații; [...] – Grupa 3 - Mobilier, aparatura birotica, echipamente de protecție a valorilor umane și materiale și alte active corporale.

— HG 2139/2004, Catalogul privind clasificarea și duratele normale de funcționare a mijloacelor fixe, cap. I pct.3
:::

Catalogul organizează activele în trei grupe mari — Construcții (Grupa 1), Instalații tehnice/mijloace de transport/animale și plantații (Grupa 2), respectiv Mobilier, aparatură birotică și alte active corporale (Grupa 3) — fiecare subîmpărțită în coduri mai fine, cu propriul interval de ani. Câteva exemple concrete, pentru orientare:

- **codul 2.2.9** ("Calculatoare electronice și echipamente periferice. Mașini și aparate de casă, control și facturat"): durată **2-4 ani**;
- **codul 2.3.2.1.1** ("autoturisme, în afară de taxiuri"): durată **4-6 ani**; taxiurile (codul 2.3.2.1.1.1) au un interval separat, **3-5 ani**;
- construcțiile (Grupa 1) au plaje mult mai largi, în funcție de tipul construcției (de exemplu, clădirile de transport pot ajunge la 32-48 ani, iar infrastructura de drum asfaltat la 20-30 ani).

Aceste cifre sunt orientative — pentru activul concret al firmei, catalogul trebuie consultat direct pentru codul de clasificare potrivit, deoarece diferențele între subcategorii pot fi semnificative.

## Ce se greșește în practică

- Se preia o durată "din memorie" sau "așa cum a folosit-o altcineva", fără să se verifice codul de clasificare exact al activului în catalog — categorii aparent similare (ex. autoturisme vs. taxiuri) pot avea intervale diferite.
- Se confundă durata contabilă (stabilită de politica de amortizare a firmei, conform reglementărilor contabile) cu durata fiscală — pentru calculul amortizării fiscale conform Codului fiscal, punctul de plecare rămâne catalogul HG 2139/2004.
- Se presupune că orice interval din catalog e valabil pentru orice metodă de amortizare — durata (din catalog) și metoda permisă (din Codul fiscal, în funcție de categoria activului) sunt două verificări separate, ambele necesare.

## Ce face iConta.eu

Câmpul cu durata normală de funcționare (în luni) se introduce manual pentru fiecare mijloc fix, la achiziție sau la import/migrarea registrului. De reținut onest: catalogul HG 2139/2004 nu e integrat în aplicație — nu există un lookup care să sugereze automat intervalul corect pe baza codului de clasificare, nici o validare care să semnaleze o durată aleasă în afara plajei legale. Contabilul poartă întreaga responsabilitate de a consulta catalogul și de a introduce o durată corectă; aplicația calculează apoi amortizarea exact pe baza acelei durate, indiferent dacă e sau nu conformă cu plaja oficială.

[iConta.eu](/)
