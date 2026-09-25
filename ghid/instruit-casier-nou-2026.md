---
title: "Cum instruit un casier nou 2026"
description: "Plafoanele legale de numerar pe care un casier trebuie să le respecte în 2026, conform Legii 70/2015, actualizată prin Legea 239/2025."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum instruit un casier nou 2026

Instruirea unui casier nou nu ține doar de manevrarea casei de marcat — cea mai frecventă sursă de sancțiuni pentru operațiunile cu numerar e necunoașterea plafoanelor legale. Un casier care nu știe plafoanele zilnice expune firma la amenzi, indiferent cât de bine cunoaște aparatul de marcat.

## Temeiul legal

::: ghid-temei
„Articolul 3 (1) Prin excepție de la prevederile art. 1 alin. (1) se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: a) încasări de la persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei de la o persoană; [...]
(2) Sunt interzise încasările fragmentate în numerar de la beneficiari pentru facturile a căror valoare este mai mare de 5.000 lei [...], precum și fragmentarea facturilor pentru o livrare de bunuri sau o prestare de servicii a căror valoare este mai mare de 5.000 lei [...]"
— Legea 70/2015, art. 3 alin. (1) lit. a) și alin. (2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Ce trebuie să știe, minimal, un casier nou:

- **Plafonul de 5.000 lei/zi de la aceeași persoană juridică**, respectiv **10.000 lei/zi** dacă firma e magazin de tip cash and carry.
- **Plafonul de 10.000 lei/zi de la o persoană fizică** (art. 4 alin. (1)), pentru încasări legate de cesiuni de creanțe, împrumuturi sau contravaloarea unor livrări/prestări.
- **Interdicția fragmentării** — încasarea unei facturi mari „în tranșe", în aceeași zi sau în zile diferite, ca să pară că fiecare tranșă respectă plafonul, e explicit interzisă și nu scapă de sancțiune doar pentru că fiecare încasare individuală pare sub plafon.
- Obligația de a emite bon fiscal/chitanță pentru fiecare încasare și de a înregistra corect operațiunea în registrul de casă, ținut potrivit normelor generale din OMFP 2634/2015.

## Ce se greșește în practică

- Se instruiește casierul doar pe manevrarea aparatului de marcat, fără explicarea plafoanelor legale de numerar — sancțiunile vin, de regulă, din depășirea plafonului, nu din erori de operare a casei.
- Se acceptă încasări fragmentate de la același client, în aceeași zi, crezând că respectă legea pentru că fiecare tranșă e sub 5.000 lei — practică interzisă explicit.
- Se ignoră diferența de plafon între persoane juridice (5.000 lei) și persoane fizice (10.000 lei), aplicând din eroare aceeași limită pentru toate încasările.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **aplică plafoanele de numerar din Legea 70/2015 (actualizată prin Legea 239/2025)** în modulul de casierie (`core/casa.py`), cu constante explicite pentru fiecare tip de plafon (persoană juridică, cash and carry, persoană fizică). Aplicația nu înlocuiește însă instruirea propriu-zisă a casierului — verifică și semnalează depășirile de plafon la introducerea operațiunilor, dar cunoașterea regulilor rămâne responsabilitatea persoanei care operează casieria.

[iConta.eu](/)
