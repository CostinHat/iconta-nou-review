---
title: "Cum se contabilizează factura Google Cloud?"
description: "Google Cloud e un serviciu B2B de la un prestator nestabilit în România — locul prestării e la beneficiar, iar TVA se datorează prin taxare inversă, nu se plătește furnizorului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează factura Google Cloud?

O factură de la Google Cloud (de regulă emisă de o entitate Google din alt stat membru UE sau din afara UE) e un serviciu prestat de un furnizor nestabilit în România către o firmă românească. Regula de bază pentru servicii B2B mută locul prestării la sediul beneficiarului, ceea ce înseamnă că firma din România datorează ea însăși TVA, prin taxare inversă — nu plătește TVA lui Google.

## Temeiul legal

::: ghid-temei
„Taxa este datorată de orice persoană impozabilă, inclusiv de către persoana juridică neimpozabilă înregistrată în scopuri de TVA conform art. 316 sau 317, care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României sau nu este considerată a fi stabilită pentru respectivele prestări de servicii pe teritoriul României [...]."
— Legea 227/2015, art. 307 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul contabil și declarativ:

- Locul prestării serviciilor cloud (către o persoană impozabilă) e la sediul beneficiarului, conform regulii generale B2B: „locul de prestare a serviciilor către o persoană impozabilă [...] este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității" (art. 278 alin. (2)).
- Firma din România înregistrează factura Google Cloud fără TVA de la furnizor, dar calculează și evidențiază ea însăși TVA prin taxare inversă: 4426 (TVA deductibilă) = 4427 (TVA colectată), aceeași sumă, cu efect neutru pe plata efectivă dacă firma are drept integral de deducere.
- Dacă firma e neplătitoare de TVA (înregistrată doar conform art. 317, cu cod special pentru achiziții intracomunitare), TVA prin taxare inversă e datorată, dar **nedeductibilă** — se raportează prin declarația D301, iar suma devine efectiv de plătit.
- Achiziția de servicii electronice de la un prestator din afara UE urmează aceleași reguli de loc al prestării (art. 278 alin. (2)) — nu contează dacă furnizorul e din UE sau dintr-un stat terț, ci faptul că beneficiarul e o persoană impozabilă stabilită în România.

## Ce se greșește în practică

- Se înregistrează factura Google Cloud ca o cheltuială simplă, fără taxare inversă, considerând că „nu are TVA românesc, deci nu-i treaba noastră" — de fapt obligația de TVA se mută la beneficiar tocmai pentru că furnizorul nu e stabilit în România.
- Se omite declararea achiziției în D301 pentru firmele neplătitoare de TVA (înregistrate doar art. 317), care datorează taxa prin taxare inversă, dar nu au dreptul s-o deducă.
- Se aplică taxare inversă și pentru serviciile facturate de o entitate Google stabilită în România (dacă există o astfel de relație contractuală locală) — taxarea inversă se aplică doar când furnizorul nu e stabilit în România pentru respectiva prestare.

## Ce face iConta.eu

iConta.eu are un modul dedicat de taxare inversă pentru achiziții intracomunitare de bunuri și servicii, care generează nota contabilă corectă (4426=4427 pentru plătitorii de TVA cu drept de deducere; TVA nedeductibilă, dar datorată, pentru firmele înregistrate doar conform art. 317) și separă corect cele două situații. Aplicația nu validează automat dacă un anumit furnizor (Google sau altul) e sau nu „stabilit în România" pentru o prestare concretă — această calificare, care depinde de contractul și de entitatea emitentă a facturii, rămâne o verificare a contabilului înainte de a introduce operațiunea.

[iConta.eu](/)
