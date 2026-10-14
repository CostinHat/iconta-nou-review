---
title: Cum se tratează retururile la un magazin online
description: Un retur se tratează prin stornarea facturii de vânzare — document nou, cu valoare negativă — care reduce automat și venitul contabilizat, deci și baza de calcul a impozitului pe veniturile microîntreprinderilor, prin construcția firească a conturilor de venit.
published: 2026-09-25
modified: 2026-10-13
poarta: v1
---

# Cum se tratează retururile la un magazin online

Dincolo de mecanismul strict al stornării, un retur la un magazin online are un efect care merită văzut clar: reduce venitul deja contabilizat, cu toate consecințele care decurg din asta — inclusiv pentru firmele la regimul de impozit pe veniturile microîntreprinderilor.

## Temeiul legal

::: ghid-temei
„69. — Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (**stornare în roșu**), fie prin înregistrarea inversă a acesteia (**stornare în negru**), în funcție de politica contabilă și programele informatice […]"

— OMFP 1802/2014, reglementări contabile consolidate, pct. 69

**OPANAF 2194/2025 (instrucțiuni D394)**, pct. 2.2.1: factura stornată „reprezintă factura emisă de persoana impozabilă, a cărei valoare totală este negativă"; coloana bazei impozabile „se înscrie cu semnul (-)" pentru facturile de stornare.
:::

::: ghid-temei
„ajustările bazei de impozitare prevăzute la art. 287 din Codul fiscal pentru care exigibilitatea taxei intervine în perioada de raportare, conform art. 282 alin. (9) şi (10), după caz, din Codul fiscal, dacă au fost generate de operaţiuni pentru care cota de taxă pe valoarea adăugată aplicată este de 21%.”
— OPANAF 174/2026, Anexa 2, instrucțiunile pentru rândul 9 din decontul de TVA (D300) (sursă: [OPANAF nr. 174/2026 pentru aprobarea formularului 300 (Decont de TVA)](https://legislatie.just.ro/Public/DetaliiDocument/307258))
:::

Tratamentul corect al unui retur are două fețe: contabilă (stornarea facturii de vânzare, cu aceeași cotă de TVA ca originalul, conturile de venit creditate cu semn negativ) și declarativă — factura de stornare se raportează explicit în D394, cu valoare negativă la bază și la TVA, alături de factura pe care o corectează.

Factura de stornare nu e o factură independentă, cu clasificări introduse din nou, ci „oglinda” vânzării pe care o corectează: preia liniile facturii inițiale cu cantitățile negate, păstrează cursul valutar al originalului (dacă a fost în valută) și aceeași clasificare fiscală — cota de TVA și regimul operațiunii.

În decontul de TVA (D300), stornarea nu se trece pe rândul de regularizări, ci pe rândul cotei vânzării inițiale, cu bază și TVA negative: de exemplu, returul unei vânzări interne la 21% intră pe rândul 9, iar al uneia la 11% pe rândul 10. Excepția o fac ajustările generate de operațiuni la care s-a aplicat o cotă care nu mai e în vigoare (24%, 20%, 19%, 9% sau 5%) — acestea se înscriu, potrivit instrucțiunilor de completare, la rândul 16.

Pentru firmele la regimul micro, veniturile care intră în baza impozitului (contul de venituri din vânzarea de mărfuri, servicii etc.) sunt reduse aritmetic de valoarea negativă a stornării, pentru că nota de stornare creditează venitul cu o sumă negativă — un retur reduce direct suma pe care se calculează impozitul micro, prin simpla construcție a conturilor, nu printr-o regulă separată scrisă special pentru „retur" sau „plafon".

## Ce se greșește în practică

- Se lasă returul netratat contabil (doar rambursarea banilor clientului, fără factura de stornare) — venitul rămâne raportat greșit, iar impozitul micro se calculează pe o bază umflată.
- Se emite doar o „notă de ajustare stoc” pentru retur, fără factură de stornare — venitul rămâne necorectat, iar decontul de TVA nu mai corespunde realității.
- Se declară returul pe rândul de regularizări din D300 în loc de rândul cotei vânzării inițiale, sau se recalculează cota de TVA la data returului în loc să se păstreze cota facturii inițiale.
- Se omite declararea facturii de stornare în D394, deși ea reprezintă o factură cu valoare negativă care trebuie raportată explicit, alături de original.
- Se presupune, greșit, că un retur declarat cu întârziere afectează retroactiv o declarație deja depusă, fără o rectificare formală.

## Ce face iConta.eu

Butonul „Stornează” generează, pentru orice factură de vânzare, documentul de corecție cu cantitățile negate, aceeași cotă de TVA și aceeași clasificare fiscală ca originalul. Stornarea generată de iConta.eu creditează automat contul de venit cu suma negativă a returului, ceea ce reduce corect baza de calcul folosită pentru impozitul micro pe trimestrul respectiv. Facturile de stornare intră automat în calculul D394, cu valoare negativă la bază și la TVA, iar în D300 pe același rând ca vânzarea originală, cu valoare negativă — nu pe un rând distinct de regularizări. Dacă returul se înregistrează într-o lună ulterioară facturii inițiale, verificați înainte de depunere rândul din D300 pe care a intrat stornarea.

De precizat: aplicația nu are un modul separat care să urmărească plafonul anual cumulat de eligibilitate pentru regimul micro (calculul veniturilor de la 1 ianuarie comparate cu pragul legal) — regimul (micro sau profit) e un atribut setat manual de contabil, nu calculat automat din veniturile cumulate reduse de retururi.

[iConta.eu](/)
