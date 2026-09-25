---
title: "Cum afectează o factură anulată plafonul micro?"
description: "Ce venituri intră, potrivit Codului fiscal, în calculul plafonului de 100.000 euro pentru încadrarea la microîntreprindere și de ce o factură anulată corect nu ar trebui să-l afecteze."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum afectează o factură anulată plafonul micro?

Plafonul de venituri pentru microîntreprindere nu se verifică pe numărul de facturi emise, ci pe cifra de afaceri înregistrată contabil. O factură anulată corect, prin stornare, nu ar trebui deci să tragă firma mai aproape de plafon — dar „corect" înseamnă respectarea unei anumite ordini contabile, nu doar ștergerea facturii din listă.

## Temeiul legal

::: ghid-temei
„În sensul prezentului titlu, o microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent: [...] c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro [...]
(1^1) În aplicarea prevederilor alin. (1) lit. c) limita privind veniturile realizate se verifică luând în calcul veniturile realizate de persoana juridică română, cumulate cu veniturile întreprinderilor legate cu aceasta, iar veniturile care se iau în calcul sunt cele care constituie cifra de afaceri definită potrivit reglementărilor contabile aplicabile [...]"
— Legea 227/2015, art. 47 alin. (1) lit. c) și alin. (1^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă de aici:

- Plafonul de 100.000 euro se verifică pe **cifra de afaceri definită potrivit reglementărilor contabile**, nu pe totalul brut al facturilor emise în cursul anului.
- O factură anulată corect, prin stornarea integrală a înregistrării în conturile de venituri (clasa 7), nu mai face parte din cifra de afaceri — pentru că reglementările contabile nu recunosc drept venit o operațiune stornată complet.
- Codul fiscal nu tratează explicit „factura anulată" ca instituție separată — efectul ei asupra plafonului micro depinde integral de cum a fost înregistrată și stornată în contabilitate, nu de simplul fapt că a fost marcată "anulată" în sistemul de facturare.

## Ce se greșește în practică

- Se anulează factura doar la nivelul aplicației de facturare (se marchează "anulată"), fără storno efectiv al veniturilor în contabilitate — caz în care suma rămâne, involuntar, în baza de calcul a plafonului.
- Se scade suma facturii anulate direct din cifra de afaceri a lunii curente, chiar dacă factura fusese emisă și înregistrată ca venit într-o lună anterioară — stornarea trebuie să corecteze perioada în care venitul a fost inițial recunoscut.
- Se presupune că o factură anulată nu are niciun efect fiscal, deși, dacă TVA a fost deja colectată sau declarată, anularea impune și corectarea declarațiilor aferente, nu doar a evidenței de venituri.

## Ce face iConta.eu

Baza impozabilă a impozitului micro din iConta.eu se determină din veniturile efectiv înregistrate în conturile de clasa 7 (70x, 75x, 76x), din care se scad reducerile comerciale acordate ulterior facturării (contul 709), conform art. 53 din Codul fiscal — motorul intern al declarațiilor citește direct rulajele acestor conturi, nu lista de facturi emise. O factură anulată prin storno corect în contabilitate nu mai apare, deci, în baza de calcul; dacă anularea se face doar la nivelul facturii, fără stornarea înregistrării contabile aferente, suma rămâne inclusă — verificarea că stornarea a fost făcută corect rămâne responsabilitatea contabilului. Plafonul de 100.000 euro pentru încadrarea ca microîntreprindere e o verificare distinctă, pe care aplicația nu o automatizează.

[iConta.eu](/)
