---
title: "Cota de TVA la pâine și produse de panificație"
description: "De ce pâinea și produsele de panificație intră la cota redusă de TVA conform art. 291 Cod fiscal și cum recunoaște automat iConta.eu această categorie la introducerea unui produs nou."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cota de TVA la pâine și produse de panificație

Pâinea și celelalte produse de panificație (chifle, cozonac, covrigi, produse de patiserie simplă) fac parte din categoria „alimente" pentru care legea prevede cotă redusă de TVA. Spre deosebire de alte produse alimentare, panificația nu se lovește, în practică, de excepțiile care readuc unele alimente la cota standard — nu conțin de regulă alcool, nu sunt băuturi și, în forma lor clasică, nu depășesc pragul de zahăr adăugat care ar schimba încadrarea.

## Temeiul legal

::: ghid-temei
„Articolul 291 alin. (2) lit. b) livrarea următoarelor bunuri: alimente, inclusiv băuturi, destinate consumului uman și animal, animale și păsări vii din specii domestice, ale căror coduri NC se stabilesc prin normele metodologice, cu excepția: 1. băuturilor alcoolice; [...] 2. băuturilor nealcoolice care se încadrează la codul NC 2202; [...] 3. alimentelor cu zahăr adăugat, al căror conținut total de zahăr este de minimum 10 g/100 g produs, altele decât laptele praf pentru nou-născuți, sugari și copii de vârstă mică; [...] 4. suplimentelor alimentare definite de Legea nr. 56/2021 privind suplimentele alimentare, cu modificările și completările ulterioare;"
— Legea nr. 227/2015 (Codul fiscal), art. 291 alin. (2) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Pâinea și produsele de panificație intră direct sub „alimente" din lit. b), fără să se lovească, de regulă, de niciuna din cele patru excepții (nu sunt băuturi alcoolice, nu sunt băuturi NC 2202, nu conțin tipic zahăr adăugat ≥10 g/100 g, nu sunt suplimente alimentare).
- Cota redusă aplicabilă, de la 01.08.2025 (Legea nr. 141/2025), este unică — **11%** — cotele vechi de 5% și 9% au fost abrogate.
- Excepția rămâne posibilă pentru produsele de patiserie/panificație cu adaos mare de zahăr (de exemplu unele produse de cofetărie asimilate panificației) — dacă zahărul adăugat atinge sau depășește 10 g/100 g produs, produsul respectiv trece la cota standard de **21%**.

## Ce se greșește în practică

- Se presupune că orice produs de patiserie sau cofetărie e automat la 11% doar pentru că e vândut lângă pâine, fără a verifica dacă rețeta îl califică drept „aliment" clasic sau dacă depășește pragul de zahăr adăugat.
- Se folosește încă mental cota veche de 9% pentru pâine, deși de la 01.08.2025 cota redusă unică este 11%.
- Se emit facturi cu denumiri generice de tip „produse panificație" fără să se distingă între articole individuale care ar putea avea încadrări diferite (de exemplu un produs de patiserie dulce cu zahăr peste prag).

## Ce face iConta.eu

Pâinea apare explicit ca exemplu în lista de referință folosită de motorul de potrivire a cotelor din iConta.eu: la introducerea denumirii unui produs nou în ecranul **Nomenclator produse**, un model AI (Claude, via API-ul Anthropic) propune automat cota de TVA pe baza regulii oficiale din art. 291, afișând și justificarea alocării. Pentru pâine și produse de panificație uzuale, propunerea va fi, în mod normal, 11%.

Cota propusă e mereu un preview corectabil manual (selector 21% / 11% / scutit), nu o decizie finală impusă. Dacă produsul există deja salvat în nomenclator, la o factură nouă cota vine direct din nomenclator, fără interogare AI repetată. Iar dacă AI-ul nu poate produce un răspuns valid pentru o denumire nouă și ambiguă, aplicația nu completează tacit 21% — marchează cota ca nedeterminată și blochează emiterea facturii până la introducerea manuală a cotei corecte.

[iConta.eu](/)
