---
title: "WooCommerce cu TVA la mai multe cote: cum se împarte pe iConta?"
description: "Un magazin online cu produse la cote de TVA diferite (21%, 11%, 5%) trebuie facturat linie cu linie, la cota corectă a fiecărui produs — exact așa procedează, azi, conectorul WooCommerce al iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# WooCommerce cu TVA la mai multe cote: cum se împarte pe iConta?

Un magazin online care vinde, de exemplu, atât produse alimentare (cotă redusă), cât și alte bunuri (cotă standard) nu poate factura toată comanda la o singură cotă de TVA — fiecare produs are cota lui, stabilită de lege, indiferent că apare în același coș de cumpărături.

## Temeiul legal

::: ghid-temei
„Cota standard se aplică asupra bazei de impozitare pentru operațiunile impozabile care nu sunt scutite de taxă sau care nu sunt supuse cotei reduse, iar nivelul acesteia este 21%. [...] Cota redusă de 11% se aplică asupra bazei de impozitare pentru următoarele prestări de servicii și/sau livrări de bunuri: [...] b) livrarea următoarelor bunuri: alimente, inclusiv băuturi, destinate consumului uman și animal, animale și păsări vii din specii domestice, ale căror coduri NC se stabilesc prin normele metodologice, cu excepția: [...] băuturilor alcoolice [...]"
— Legea 227/2015 (Codul fiscal), art. 291 alin. (1) și alin. (2) lit. b), forma în vigoare de la 01.08.2025 (modificată prin Legea 141/2025) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Cota standard de TVA e 21% și se aplică oricărei operațiuni care nu e scutită și nu se încadrează la o cotă redusă.
- Cota redusă de 11% se aplică, printre altele, alimentelor și băuturilor nealcoolice, medicamentelor, cazării hoteliere — categorii frecvente într-un magazin online mixt.
- Există și o cotă redusă de 5%, pentru categorii mai restrânse (cărți, manuale, acces la anumite evenimente culturale, locuințe sociale).
- Cota corectă se determină pe fiecare produs în parte, în funcție de natura lui, nu pe comandă ca întreg — o comandă cu produse la cote diferite generează o factură cu linii la cote diferite.

## Ce se greșește în practică

- Se presupune că toată comanda primește o singură cotă de TVA (de obicei cota standard), ignorând faptul că produsele diferite din același coș pot avea cote diferite.
- Se are încredere că valoarea de TVA calculată deja de WooCommerce e cea corectă din punct de vedere fiscal românesc — magazinul poate folosi o configurare veche sau greșită a cotelor, necorelată cu modificările legale.
- Se ignoră ce se întâmplă când un produs nu poate fi încadrat automat la o cotă — nu doar acea linie rămâne neprocesată, ci întreaga comandă (și, în cascadă, comenzile de după ea din aceeași rulare).

## Ce face iConta.eu

Conectorul WooCommerce al iConta.eu **nu preia niciodată cota de TVA din magazin** — fiecare linie de produs importată dintr-o comandă intră fără cotă atribuită, iar cota corectă e stabilită separat de iConta, prin potrivirea produsului cu nomenclatorul intern sau, dacă nu se găsește o potrivire, prin recunoaștere automată. Astfel, o comandă cu produse la 11% (alimente) și 21% (alte bunuri) e împărțită corect, linie cu linie, exact ca orice altă factură emisă manual în aplicație — mecanismul e comun, nu specific WooCommerce. Dacă totuși niciun mecanism nu poate stabili cota unui produs, aplicația **nu presupune o cotă implicită** (nu „ghicește" 21% sau altă valoare) — blochează explicit importul acelei comenzi, cerând declararea manuală a cotei pe produsul respectiv. Limita practică de reținut: acest blocaj oprește și comenzile rămase din aceeași rulare a cronului, nu doar comanda cu produsul neclasificat.

[iConta.eu](/)
