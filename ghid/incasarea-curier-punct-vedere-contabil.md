---
title: "Cum se face încasarea prin curier din punct de vedere contabil 2026"
description: "Plafonul legal pentru încasările în numerar de la persoane fizice (ramburs prin curier) și tratamentul lor contabil, conform Legii 70/2015."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se face încasarea prin curier din punct de vedere contabil 2026

Încasarea „ramburs" prin curier — clientul plătește cash curierului la livrare, iar suma ajunge apoi la firmă — e din punct de vedere legal o încasare în numerar de la o persoană fizică, supusă acelorași plafoane ca orice altă încasare cash.

## Temeiul legal

::: ghid-temei
„(1) Operațiunile de încasări în numerar efectuate de persoanele prevăzute la art. 1 alin. (1), de la persoane fizice, reprezentând cesiuni de creanțe, primiri de împrumuturi sau alte finanțări, precum și contravaloarea unor livrări de bunuri sau a unor prestări de servicii se efectuează în limita unui plafon zilnic de 10.000 lei de la o persoană. (2) Sunt interzise încasările fragmentate de la o persoană, pentru operațiunile de încasări în numerar prevăzute la alin. (1), cu o valoare mai mare de 10.000 lei, precum și [...] fragmentarea unei livrări de bunuri sau a unei prestări de servicii, cu valoare mai mare de 10.000 lei."
— Legea 70/2015, art. 4 alin. (1)-(2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Ce înseamnă pentru un magazin online care folosește ramburs prin curier:

- plafonul relevant e de **10.000 lei pe zi, de la aceeași persoană fizică** — pentru o comandă (sau mai multe comenzi ale aceluiași client în aceeași zi) care depășește această sumă, încasarea integrală în numerar prin curier nu mai e permisă legal;
- e interzisă **fragmentarea artificială** a unei comenzi peste 10.000 lei în livrări separate, tocmai pentru a încadra fiecare încasare sub plafon — legea sancționează atât fragmentarea plății, cât și fragmentarea livrării/prestării în sine;
- din punct de vedere contabil, suma încasată de curier și virată ulterior firmei se înregistrează ca **încasare în numerar la data la care curierul o colectează efectiv de la client** (nu la data virării către firmă) — de aici decurge și verificarea plafonului zilnic, raportată la data reală a încasării de la client, nu la data decontării cu operatorul de curierat;
- contravaloarea comenzii se recunoaște ca venit la data livrării/facturării, conform regulilor generale, indiferent de modalitatea de încasare (ramburs sau plată online în avans).

## Ce se greșește în practică

- Se verifică plafonul de 10.000 lei raportat la ziua în care firma primește decontul de la curier, nu la ziua în care curierul a încasat efectiv suma de la client — data relevantă pentru plafon e cea a încasării reale de la persoana fizică.
- Se emit mai multe facturi separate pentru aceeași comandă, doar pentru a menține fiecare încasare ramburs sub plafonul de 10.000 lei — aceasta constituie fragmentare interzisă explicit de lege.
- Se tratează suma ramburs virată de curier ca „venit din servicii de curierat" în loc de încasare a contravalorii mărfii — decontul de la operatorul de curierat e o mișcare de trezorerie (numerar colectat în numele firmei), nu un venit separat.

## Ce face iConta.eu

iConta.eu are un modul de casierie (`core/casa.py`) care aplică plafoanele legale de încasări/plăți în numerar prevăzute de Legea 70/2015 (actualizată prin Legea 239/2025), inclusiv plafonul de 10.000 lei de la persoane fizice. Aplicația nu are însă, la data acestui ghid, o integrare specifică cu decontul operatorilor de curierat care să reconcilieze automat sumele ramburs colectate zi cu zi de la fiecare client cu plafonul legal — verificarea acestei corelații rămâne, pentru moment, manuală.

[iConta.eu](/)
