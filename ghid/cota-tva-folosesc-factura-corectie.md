---
title: Ce cotă TVA folosesc pentru o factură de corecție dintr-o perioadă anterioară?
description: O corecție sau stornare păstrează cota de pe operațiunea originală, nu cota valabilă la data emiterii corecției — regulă confirmată explicit de motorul intern al iConta.eu, cu teste dedicate.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce cotă TVA folosesc pentru o factură de corecție dintr-o perioadă anterioară?

Când corectezi sau stornezi o operațiune facturată într-o perioadă anterioară, cota de TVA folosită nu este cea valabilă azi, ci cea în vigoare **la data operațiunii originale**. O corecție nu „reactualizează" cota — ea reflectă exact ce era legal la momentul faptei generatoare.

## Temeiul legal

::: ghid-temei
Regula cotelor de TVA este legată de data operațiunii, nu de data corecției: o cotă valabilă istoric (de exemplu 19%, cota standard până la 31.07.2025) rămâne corectă pentru o operațiune din acea perioadă, dar aceeași cotă e nelegală dacă e declarată pe o operațiune de azi — art. 291 din Codul fiscal.
:::

## De ce contează data operațiunii, nu data corecției

Cotele de TVA s-au schimbat în timp: 19% standard până la 31.07.2025, apoi 21%; 9%/5% reduse până la 31.07.2025, comasate în 11% de la 01.08.2025. O corecție sau o notă de stornare la o factură emisă, de exemplu, în iunie 2025 trebuie să păstreze cota de atunci (19% sau, după caz, 9%/5%), **nu** cota curentă de 21%/11% — chiar dacă document de corecție e emis fizic în 2026.

Stornarea (corecția prin sume negative, în același exercițiu financiar) nu recalculează cota — ea doar inversează semnul sumelor de pe operațiunea originală, păstrând integral cota, baza și temeiul de pe factura corectată.

## Ce se greșește în practică

- Se aplică automat cota curentă (21%/11%) pe o corecție a unei facturi vechi, pentru că „azi asta e cota" — greșit, cota trebuie să corespundă datei operațiunii corectate.
- Se emite o corecție fără să se verifice dacă operațiunea originală a fost înregistrată sub o cotă istorică diferită (19%, 9%, 5%), rezultând o corecție cu o cotă care nu a existat niciodată pentru acea dată.
- Se confundă „data emiterii corecției" cu „data operațiunii" în declarația de TVA, ceea ce poate duce la raportarea unei cote nelegale pentru perioada respectivă.

## Ce face iConta.eu

Validarea cotei (`core/common.py`, funcția `cota_ceruta`) cere obligatoriu data operațiunii și verifică cota introdusă față de cotele legale valabile **la acea dată**, nu la data curentă — o cotă existentă doar în altă perioadă e respinsă explicit, cu mesaj care citează art. 291. Testele interne confirmă mecanic acest comportament: 19% e acceptat pe o operațiune din iunie 2024, dar respins dacă e declarat pe o operațiune de azi. Funcția de stornare (`core/facturi.py`, `storno()`) inversează doar semnul sumelor de pe notele contabile originale, fără să recalculeze cota.

[iConta.eu](/)
