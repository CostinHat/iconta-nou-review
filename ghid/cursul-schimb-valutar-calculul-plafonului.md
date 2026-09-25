---
title: "Cursul de schimb valutar pentru calculul plafonului micro 2026"
description: "Ce curs BNR se folosește pentru a verifica dacă veniturile firmei depășesc echivalentul în lei a 100.000 euro, plafonul de ieșire din regimul microîntreprinderilor."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cursul de schimb valutar pentru calculul plafonului micro 2026

Plafonul de 100.000 euro care decide dacă o firmă rămâne microîntreprindere se verifică în lei, nu în euro. Legea fixează însă un singur curs de schimb pentru tot anul — nu cursul BNR al fiecărei zile în care s-a facturat, cum se întâmplă la TVA. Confuzia dintre cele două reguli e frecventă și produce calcule greșite ale plafonului.

## Temeiul legal

::: ghid-temei
„a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile."
— Codul fiscal, art. 47 alin. (1) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Limitele fiscale prevăzute la alin. (1) se verifică pe baza veniturilor înregistrate cumulat de la începutul anului fiscal. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar precedent."
— Codul fiscal, art. 52 alin. (5) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din cele două texte rezultă un mecanism clar, dar diferit de cel de la TVA:

- **La verificarea condiției de intrare/menținere** (art. 47 alin. (1) lit. c)), cursul folosit e cel **valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile** — de regulă, cursul BNR din 31 decembrie al anului respectiv.
- **La verificarea depășirii plafonului în cursul anului** (art. 52 alin. (5)), cursul e cel **valabil la închiderea exercițiului financiar precedent** — practic, cursul BNR de la 31 decembrie al anului anterior, fixat o singură dată și aplicat tuturor veniturilor cumulate din anul curent.
- Nu există aici un curs „al zilei operațiunii", ca la TVA (art. 290 alin. (2) Cod fiscal): plafonul micro folosește un curs unic, anual, nu unul zilnic.

## Ce se greșește în practică

- Se aplică din reflex cursul BNR al zilei fiecărei facturi (regula de la TVA) pentru a verifica plafonul micro, în loc de cursul fix de la 31 decembrie al anului anterior.
- Se calculează plafonul cu cursul de la data verificării (de exemplu, cursul din luna în care contabilul face controlul), nu cu cursul de închidere a exercițiului financiar precedent, cerut explicit de art. 52 alin. (5).
- Se ignoră că verificarea se face **cumulat de la începutul anului fiscal**, nu lună de lună sau trimestru de trimestru izolat.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu calculează și nu monitorizează automat plafonul de 100.000 euro** al microîntreprinderii. Nu există în aplicație nicio constantă sau logică de plafon micro (verificat: nicio implementare de acest tip în codul sursă, confirmat explicit chiar într-un comentariu intern despre blocajul de schimbare a regimului fiscal, care se bazează strict pe ce completează manual contabilul, nu pe un calcul propriu al plafonului).

Aplicația are un motor separat pentru cursul BNR (folosit la facturare și TVA, conform art. 290 Cod fiscal), dar acela aplică regula cursului zilei operațiunii — o regulă diferită de cea de mai sus și, prin construcție, nu poate fi refolosit pentru verificarea plafonului micro. Urmărirea plafonului de 100.000 euro, cu cursul corect de la 31 decembrie, rămâne azi în sarcina contabilului.

[iConta.eu](/)
