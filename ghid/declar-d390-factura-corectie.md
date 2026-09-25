---
title: "Cum declar în D390 o factură de corecție"
description: "În ce lună se raportează, în declarația recapitulativă, o operațiune intracomunitară corectată printr-o factură ulterioară."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum declar în D390 o factură de corecție

O livrare intracomunitară deja declarată în D390 se poate corecta ulterior — printr-o factură de stornare, o notă de credit sau o factură de corecție a valorii. Întrebarea practică e în ce lună trebuie să apară corecția: în luna operațiunii inițiale sau în luna în care s-a emis documentul corectiv.

## Temeiul legal

::: ghid-temei
„(1) Orice persoană impozabilă înregistrată în scopuri de TVA [...] trebuie să întocmească și să depună la organele fiscale competente o declarație recapitulativă în care menționează: a) livrările intracomunitare scutite de taxă [...], pentru care exigibilitatea taxei a luat naștere în luna calendaristică respectivă; [...]
(2) Termenul de depunere al declarației recapitulative și modelul acesteia se stabilesc prin ordin al președintelui Agenției Naționale de Administrare Fiscală. Declarația se întocmește pentru fiecare lună calendaristică în care ia naștere exigibilitatea taxei pentru operațiunile prevăzute la alin. (1) [...]"
— Legea nr. 227/2015 (Codul fiscal), art. 325 alin. (1) lit. a) și alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

**Limitare declarată:** textul stabilește principiul de fond — declarația recapitulativă raportează operațiunile în luna în care ia naștere **exigibilitatea taxei** pentru operațiunea respectivă, nu în luna emiterii documentului. Pentru mecanismul tehnic exact al corecției (dacă o factură de stornare/corecție se raportează în luna facturii inițiale, prin rectificarea acelei declarații, sau în luna proprie de exigibilitate a corecției), sursele verificate nu conțin un text explicit, punctual, care să detalieze această situație pentru D390. Ce se poate spune cu certitudine din structura generală a sistemului:

- Declarația recapitulativă însăși poate fi **rectificată** — procedura ANAF pentru declarațiile recapitulative rectificative prevede prelucrarea lor separat de cele inițiale, cu identificarea diferențelor față de declarația inițială depusă.
- Principiul de bază al legii (exigibilitatea taxei) sugerează că o corecție care schimbă baza impozabilă a unei operațiuni deja declarate se reflectă, de regulă, prin rectificarea declarației lunii în care a fost raportată operațiunea inițială — nu prin introducerea corecției ca operațiune nouă în luna curentă.

## Ce se greșește în practică

- Se introduce factura de corecție ca operațiune nouă în luna curentă, fără legătură cu declarația lunii în care a fost raportată livrarea inițială — riscă să dubleze sau să denatureze valorile deja transmise pentru luna respectivă.
- Se amână corectarea declarației recapitulative, considerând că e suficientă corectarea facturii în evidența internă — obligația de raportare corectă către ANAF rămâne separată de corectarea documentului comercial.
- Se ignoră faptul că declarațiile recapitulative rectificative au un regim de procesare distinct la ANAF, cu verificare separată a diferențelor față de declarația inițială.

## Ce face iConta.eu

Verificat în cod: modulul `core/d390.py` generează declarația D390 prin auto-derivare din facturile deja înregistrate în aplicație (livrări/achiziții intracomunitare, prestări de servicii art. 278 alin. (2)), validând coerența datelor (cod CUI, țară, temei) înainte de generare. Aplicația **nu are o rută dedicată explicit „factură de corecție"** — nu am găsit în cod un tratament separat pentru facturile de stornare sau de corecție a unei livrări intracomunitare deja declarate; o astfel de corecție trebuie reflectată de contabil prin ajustarea facturii corespunzătoare și, dacă e nevoie, prin depunerea manuală a unei declarații recapitulative rectificative pentru luna afectată.

[iConta.eu](/)
