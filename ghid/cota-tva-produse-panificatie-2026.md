---
title: "Cota de TVA la produse de panificație în 2026"
description: "Confirmarea că regula de TVA pentru produsele de panificație, stabilită prin reforma cotelor de la 01.08.2025, rămâne neschimbată în 2026, și cum o aplică automat iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cota de TVA la produse de panificație în 2026

Reforma cotelor de TVA de la 1 august 2025 a rescris regulile pentru numeroase categorii de produse alimentare, inclusiv panificația. Vestea bună pentru 2026: nu au mai intervenit modificări ulterioare ale art. 291 asupra acestei categorii — regula stabilită atunci este cea care se aplică și în continuare. Nu există niciun temei legal pentru o „cotă nouă 2026" diferită de cea intrată în vigoare în august 2025.

## Temeiul legal

::: ghid-temei
„Articolul 291 alin. (2) lit. b) livrarea următoarelor bunuri: alimente, inclusiv băuturi, destinate consumului uman și animal, animale și păsări vii din specii domestice, ale căror coduri NC se stabilesc prin normele metodologice, cu excepția: 1. băuturilor alcoolice; [...] 2. băuturilor nealcoolice care se încadrează la codul NC 2202; [...] 3. alimentelor cu zahăr adăugat, al căror conținut total de zahăr este de minimum 10 g/100 g produs, altele decât laptele praf pentru nou-născuți, sugari și copii de vârstă mică; [...] 4. suplimentelor alimentare definite de Legea nr. 56/2021 privind suplimentele alimentare, cu modificările și completările ulterioare;"
— Legea nr. 227/2015 (Codul fiscal), art. 291 alin. (2) lit. b), modificat prin Legea nr. 141/2025, în vigoare de la 01.08.2025 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Produsele de panificație (pâine, chifle, cozonac, covrigi și similare) rămân încadrate ca „alimente" la lit. b), fără să intre, de regulă, sub niciuna dintre cele patru excepții (alcool, băuturi NC 2202, zahăr adăugat ≥10 g/100 g, suplimente).
- Cota aplicabilă în 2026 este cea stabilită de la 01.08.2025: **11%** — cotă redusă unică, cotele istorice de 5% și 9% fiind abrogate prin Legea nr. 141/2025 și nereintroduse ulterior.
- Doar produsele de panificație/patiserie cu zahăr adăugat peste pragul de 10 g/100 g rămân la cota standard de **21%**, ca și în 2025.

## Ce se greșește în practică

- Se caută o „listă nouă de cote 2026", presupunând că legislația s-a schimbat din nou de la an la an — pentru panificație, regula din august 2025 nu a fost modificată.
- Se recalculează manual cote pe facturi vechi presupunând o schimbare care nu a avut loc, generând corecții inutile.
- Se confundă anunțuri sau propuneri legislative discutate în spațiul public cu modificări efectiv intrate în vigoare — doar textul consolidat al art. 291, așa cum a fost modificat prin Legea nr. 141/2025, este relevant pentru facturare.

## Ce face iConta.eu

Motorul de potrivire automată a cotelor din iConta.eu se bazează pe regula curentă din art. 291, reprodusă ca referință în codul aplicației și folosită ca instrucțiune pentru modelul AI (Claude, via API-ul Anthropic) care propune cota pentru fiecare produs nou introdus în **Nomenclatorul de produse**. Pentru că regula legală pentru panificație nu s-a schimbat între 2025 și 2026, comportamentul aplicației rămâne identic: la scrierea unei denumiri de tip „pâine" sau „produse de panificație", sistemul propune 11%, cu justificarea afișată, corectabilă manual dacă e cazul.

Dacă în viitor legea s-ar modifica din nou, actualizarea regulii aplicate de iConta.eu ar necesita o modificare explicită în codul sursă al aplicației (fișierul care conține regula oficială) — aplicația nu „învață" singură schimbări legislative, ci le reflectă doar pe măsură ce sunt actualizate de echipa de dezvoltare.

[iConta.eu](/)
