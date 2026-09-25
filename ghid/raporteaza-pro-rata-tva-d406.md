---
title: "Cum se raportează pro-rata TVA în D406?"
description: "Ce este pro-rata TVA pentru persoanele impozabile cu regim mixt și cum se reflectă ea în evidența fiscală raportată prin SAF-T (D406)."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se raportează pro-rata TVA în D406?

O firmă care desfășoară atât operațiuni cu drept de deducere a TVA, cât și operațiuni fără drept de deducere (de exemplu, o parte din activitate scutită fără drept de deducere) nu poate deduce integral TVA de pe achizițiile pe care nu le poate aloca clar unei singure categorii. Pentru acestea se aplică pro-rata — un procent care limitează deducerea. Regula e stabilită de Codul fiscal; D406 (fișierul standard de audit fiscal, SAF-T) o raportează printr-un câmp XML dedicat, `BaseRate`, atașat fiecărui cod de taxă din secțiunea de nomenclatoare (`TaxTable`).

## Temeiul legal

::: ghid-temei
„Dreptul de deducere a taxei deductibile aferente achizițiilor efectuate de către o persoană impozabilă cu regim mixt sau de către o persoană parțial impozabilă se determină conform prezentului articol. [...] Persoana parțial impozabilă poate aplica pro rata în situația în care nu poate ține evidențe separate pentru activitatea desfășurată în calitate de persoană impozabilă și pentru activitatea pentru care nu are calitatea de persoană impozabilă."
— Codul fiscal (Legea 227/2015), art. 300 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul, pe scurt:

- Taxa aferentă achizițiilor destinate **exclusiv** operațiunilor cu drept de deducere se deduce integral (art. 300 alin. (3)); cea aferentă operațiunilor **fără** drept de deducere nu se deduce deloc (alin. (4)).
- Doar taxa pentru achizițiile pentru care destinația nu poate fi determinată se deduce pe bază de pro-rata.
- Pro-rata aplicabilă în cursul anului e provizorie (pro-rata definitivă din anul precedent, sau estimată), iar la final de an se calculează pro-rata definitivă și se regularizează deducerile.
- Persoana impozabilă trebuie să comunice organului fiscal, până la 25 ianuarie, pro-rata provizorie pe care o va aplica în anul respectiv.

**Cum apare concret în structura SAF-T**: câmpul `BaseRate` din `MasterFiles > TaxTable` e o fracție în intervalul [0,0000 – 1,0000], unde 1,0000 înseamnă 100% drept de deducere pentru codul de taxă respectiv — nu procent întreg (100), ci fracție zecimală. Un cod de taxă pentru o achiziție cu pro-rata de deducere de 50% s-ar raporta cu `BaseRate = 0.5`.

## Ce se greșește în practică

- Se aplică pro-rata pe TOATE achizițiile, inclusiv pe cele pentru care destinația e clară (exclusiv operațiuni deductibile sau exclusiv operațiuni nedeductibile) — pro-rata se aplică doar acolo unde destinația e nedeterminată.
- Se uită comunicarea către organul fiscal a pro-ratei provizorii până la 25 ianuarie, obligație distinctă de depunerea deconturilor de TVA.
- Se lasă regularizarea de sfârșit de an (pro-rata provizorie → pro-rata definitivă) neefectuată, ceea ce lasă deducerea de TVA incorectă în evidență.
- Se confundă `BaseRate` (fracție 0–1) cu un procent întreg (0–100) — o valoare precum „60" în loc de „0.6" încalcă restricția de format SAF-T și declarația e respinsă de validator.

## Ce face iConta.eu

Modulul de generare D406 din iConta.eu are câmpul `BaseRate` implementat structural, dar la data acestui ghid valoarea e fixată la 1 (100% drept de deducere) pentru toate codurile de taxă — pentru că motorul intern emite azi doar coduri de taxă pentru livrări (operațiuni de ieșire), care nu au pro-rata de deducere. Un cod de taxă pentru o achiziție cu deducere parțială (de exemplu, 50%) ar necesita `BaseRate = 0.5`, dar acest tip de cod nu e încă emis de motorul de calcul al cotelor — e o limitare cunoscută și documentată în cod, nu o funcționalitate finalizată. Practic: o firmă cu regim mixt de TVA nu poate încă să-și reflecte automat, prin iConta.eu, pro-rata de deducere în D406.

[iConta.eu](/)
