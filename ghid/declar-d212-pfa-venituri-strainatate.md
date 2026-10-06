---
title: "Cum declar în D212 dacă am PFA și venituri din străinătate?"
description: "Veniturile din străinătate se declară separat, pe capitolul dedicat al D212, cu regulile proprii fiecărei categorii de venit și, dacă e cazul, cu creditul fiscal extern aferent convenției de evitare a dublei impuneri."
published: 2026-09-26
modified: 2026-10-03
poarta: v1
---

# Cum declar în D212 dacă am PFA și venituri din străinătate?

Ca și la chirii, D212 tratează veniturile din străinătate ca sursă separată de PFA, dar cu o particularitate: baza de impozitare se stabilește după regulile proprii categoriei de venit, exact ca și cum ar fi fost realizat în România — diferența apare doar la creditul fiscal pentru impozitul deja plătit afară.

## Temeiul legal

::: ghid-temei
„Persoanele fizice prevăzute la art. 59 alin. (1) lit. a) și cele care îndeplinesc condițiile prevăzute la art. 59 alin. (2) și (2^1) datorează impozit pentru veniturile obținute din străinătate. [...] Veniturile realizate din străinătate se supun impozitării prin aplicarea cotelor de impozit asupra bazei de calcul determinate după regulile proprii fiecărei categorii de venit, în funcție de natura acestuia."
— Codul fiscal (Legea 227/2015), art. 130 alin. (1)-(2) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Ce rezultă pentru completarea D212:

- Rezidenții români (art. 59 alin. (1) lit. a)) datorează impozit pentru toate veniturile, indiferent de statul din care provin — inclusiv cele din activitatea de PFA desfășurată sau facturată din străinătate.
- Venitul din străinătate nu are un regim fiscal propriu, separat de categoriile interne — se încadrează în aceeași categorie de venit (activități independente, chirii, investiții etc.) și se supune acelorași reguli de determinare a bazei ca un venit similar realizat în România (art. 130 alin. (2)).
- Dacă România are încheiată o convenție de evitare a dublei impuneri cu statul din care provine venitul, iar impozitul a fost deja reținut acolo, contribuabilul poate solicita creditul fiscal extern — condiționat de documente justificative privind impozitul plătit în străinătate.
- Venitul din PFA realizat din România și cel din străinătate, chiar dacă provin din activități similare, se declară pe capitole distincte în D212 — cap11 (sistem real, în România) și cap14 (venituri realizate în străinătate).

## Ce se greșește în practică

- Se omite declararea veniturilor din străinătate, considerând că impozitul plătit acolo acoperă automat orice obligație în România — creditul fiscal extern trebuie solicitat explicit, cu documente, nu se aplică din oficiu.
- Se declară venitul din străinătate cumulat cu cel din România, pe același capitol, în loc de capitolul dedicat (cap14) — structura declarației cere separarea lor.
- Se aplică regulile de determinare a venitului net specifice altei categorii decât cea reală a venitului din străinătate — regula e „aceeași categorie, aceleași reguli", nu un regim special unic pentru toate veniturile externe.

## Ce face iConta.eu

Generatorul D212 al iConta.eu susține capitolul dedicat veniturilor din străinătate (`cap14`), cu câmpurile oficiale pentru venit brut, cheltuieli deductibile, impozit datorat în România, impozit plătit în străinătate și creditul fiscal aferent (`str_impozit_datorat_Ro`, `str_impozit_platit`, `str_credit_fiscal`). Contabilul introduce țara, categoria, metoda de evitare a dublei impuneri, sumele în lei și impozitul plătit acolo (dovada lui o păstrează contribuabilul); aplicația calculează impozitul datorat în România cu cota categoriei, creditul fiscal — cel mult cât impozitul român — și diferența de plată.

Aplicația nu verifică dacă România are convenție de evitare a dublei impuneri cu statul respectiv și ce metodă prevede — contabilul alege metoda (creditul fiscal sau scutirea), iar aplicația aplică regula metodei alese.

[iConta.eu](/)
