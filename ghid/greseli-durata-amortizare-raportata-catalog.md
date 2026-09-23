---
title: "Greșeli la durata de amortizare raportată la catalog"
description: "Catalogul de clasificare a mijloacelor fixe nu este validat automat — durata aleasă rămâne responsabilitatea contabilului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Greșeli la durata de amortizare raportată la catalog

Cea mai frecventă sursă de erori la durata de amortizare e alegerea unei valori din afara plajei legale prevăzute de catalogul de clasificare pentru categoria activului.

## Temeiul legal

::: ghid-temei
"pentru fiecare mijloc fix nou achiziționat se utilizează sistemul unor plaje de ani cuprinse între o valoare minima și una maxima, existând astfel posibilitatea alegerii duratei normale de funcționare cuprinsa între aceste limite."
— HG 2139/2004, Catalogul privind clasificarea și duratele normale de funcționare a mijloacelor fixe, cap.II pct.4
:::

Catalogul stabilește plaje minim-maxim de durată pe fiecare categorie de clasificare (de exemplu 2-4 ani pentru calculatoare, 4-6 ani pentru autoturisme, plaje largi pe tip de construcție pentru clădiri). Durata aleasă trebuie să se încadreze în plaja corespunzătoare categoriei reale a activului.

## Ce se greșește în practică

Greșeala tipică e alegerea unei durate "convenabile" (de exemplu cea mai scurtă posibilă, pentru deducere rapidă) fără verificarea plajei corecte pentru categoria specifică, sau clasificarea greșită a activului într-o categorie cu plajă diferită de cea reală.

## Ce face iConta.eu

**Catalogul HG 2139/2004 nu este cablat deloc în aplicație.** Câmpul de durată (`dnf_luni`) e complet liber, fără nicio validare a intervalului minim-maxim din catalog pentru categoria de clasificare a activului — aplicația nu oferă un lookup și nu avertizează dacă durata aleasă e în afara plajei legale. Responsabilitatea alegerii corecte a duratei din catalog revine integral contabilului.

[iConta.eu](/)
