---
title: "Descărcarea materialelor în producție după consum efectiv"
description: "Când și pe ce cont se descarcă gestiunea de materii prime la darea în consum pentru producție — regula inventarului permanent din OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Descărcarea materialelor în producție după consum efectiv

În metoda inventarului permanent (cea mai folosită de firmele care produc), materiile prime ies din stoc exact în momentul consumului efectiv în producție, pe baza bonului de consum — nu la o dată estimată sau la închiderea lunii pe o cifră globală.

## Temeiul legal

::: ghid-temei
„Contul 301 «Materii prime» [...] este un cont de activ. În situația aplicării inventarului permanent: [...] În creditul contului 301 «Materii prime» se înregistrează: – valoarea la preț de înregistrare a materiilor prime incluse pe cheltuieli, precum și a celor constatate lipsă la inventar sau distruse (601); [...] Soldul contului reprezintă valoarea materiilor prime existente în stoc."
— OMFP 1802/2014, Cap. 16 „Funcțiunea conturilor", Grupa 30, Contul 301 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Ce rezultă din text:

- Sub inventarul permanent, contul 301 e ținut la zi: fiecare intrare (achiziție) se înregistrează în debit, fiecare ieșire (consum, vânzare ca atare, lipsă constatată) în credit, iar soldul reflectă **în orice moment** stocul real existent.
- Darea în consum pentru producție se înregistrează prin nota **601 „Cheltuieli cu materiile prime" = 301 „Materii prime"**, la valoarea de preț de înregistrare a cantității efectiv consumate — nu la o cantitate estimată sau planificată.
- Documentul justificativ al acestei ieșiri e bonul de consum (sau echivalentul lui intern), emis la momentul consumului real, în atelier/secție — o descărcare „în avans", pe baza unei rețete de fabricație teoretice, nu respectă regula consumului efectiv dacă producția reală a folosit alte cantități.
- Diferența dintre inventarul permanent (descărcare la fiecare mișcare) și inventarul intermitent (descărcare estimată, la închiderea perioadei, pe baza inventarierii fizice) e explicită în text — cele două metode nu se amestecă pentru aceeași gestiune.

## Ce se greșește în practică

- Se descarcă gestiunea de materii prime pe baza rețetei standard de fabricație, fără ajustare la consumul real — diferențele (risipă, pierderi tehnologice peste normă, economii) rămân neînregistrate și denaturează costul de producție.
- Se face descărcarea o singură dată, la finalul lunii, cumulat, deși firma aplică inventar permanent — practica corectă cere înregistrarea la fiecare bon de consum, chiar dacă raportarea contabilă se citește lunar.
- Se confundă materiile prime „trimise spre prelucrare la terți" (ies din 301, dar rămân proprietatea firmei, prin contul 351) cu consumul efectiv în producție proprie (601) — regimul contabil e diferit.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un motor de producție (`core/productie.py`), cu funcțiile `nota_obtinere` (obținerea produselor finite la cost standard sau efectiv) și `nota_productie_in_curs`, dar **nu am găsit** în acest modul o funcție dedicată descărcării automate a materiilor prime consumate (nota 601 = 301) pe baza unui bon de consum. Aplicația oferă evidența contabilă generală și registrul de stocuri, în care contabilul înregistrează manual consumul efectiv de materii prime pe măsură ce apar bonurile de consum.

[iConta.eu](/)
