---
title: Cum calculez TVA exigibilă la o încasare parțială?
description: Din suma încasată se extrage TVA prin metoda sutei mărite — suma × cotă/(100+cotă) — nu prin aplicarea cotei peste sumă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum calculez TVA exigibilă la o încasare parțială?

Când încasezi doar o parte dintr-o factură, legea consideră că fiecare leu încasat conține deja și TVA-ul aferent — de aici rezultă o formulă de calcul specifică, diferită de „bază + TVA".

## Temeiul legal

::: ghid-temei
**Art. 282 alin. (8) CF**: „Pentru determinarea taxei aferente încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, care devine exigibilă potrivit prevederilor alin. (3), fiecare încasare totală sau parțială se consideră că include și taxa aferentă." Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, liniile 17727-17729.

**Pct. 26 alin. (16) din Normele metodologice de aplicare a Codului fiscal (HG 1/2016)**: „Persoana impozabilă care încasează/plătește parțial o factură cuprinzând contravaloarea unor livrări de bunuri/prestări de servicii care conțin mai multe cote de TVA și/sau mai multe regimuri de impozitare are dreptul să aleagă bunurile/serviciile care consideră că au fost încasate/plătite parțial pentru a determina suma taxei încasate/plătite în funcție de cote, respectiv regimul aplicabil." Sursă: `anaf_surse/hg_1_2016_norme_cod_fiscal.txt`, linia 6595.
:::

Formula rezultată din „sută mărită": TVA exigibilă = suma încasată × cotă / (100 + cotă). De exemplu, la o încasare de 1.000 lei dintr-o factură cu cota standard de 21%, TVA exigibilă e 1.000 × 21/121 ≈ 173,55 lei — nu 1.000 × 21% = 210 lei, greșeală frecventă, care ar presupune că suma încasată e o bază fără TVA.

Dacă factura conține mai multe cote de TVA sau regimuri diferite, iar plata primită nu acoperă integral toate liniile, legea îți lasă libertatea de a alege ce bunuri/servicii consideri încasate parțial, pentru a împărți suma pe cote.

## Ce se greșește în practică

- Se aplică cota direct peste suma încasată (suma × cotă), în loc de metoda sutei mărite (suma × cotă/(100+cotă)).
- Se calculează TVA exigibilă raportat la baza facturii, nu la suma efectiv încasată.
- La facturi cu cote multiple, se împarte suma încasată proporțional cu structura facturii, în loc să se aleagă explicit ce s-a considerat încasat, așa cum permite norma.

## Ce face iConta.eu

Funcția `tva_din_incasare(suma_incasata, cota)` din `core/tva_incasare.py` implementează exact metoda sutei mărite (`suma × cotă/(100+cotă)`), iar `tva_exigibil_alocari()` agregă rezultatul pe cote pentru încasări care ating mai multe facturi/cote simultan. Alegerea manuală a cotei aplicabile (când sunt implicate facturi/avansuri cu date diferite, conform art. 291 alin. 5) rămâne un pas separat, controlat de contabil — aplicația nu deduce automat ramura corectă, tocmai ca să nu producă „o cifră validă și falsă" (decizie de produs explicită în cod).

[iConta.eu](/)
