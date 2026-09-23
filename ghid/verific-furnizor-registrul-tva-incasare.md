---
title: Cum verific un furnizor în Registrul TVA la încasare?
description: Bifa de pe factura de achiziție e declarativă — verificarea reală a unui furnizor se face în Registrul public al ANAF, iar de ea depinde momentul la care poți deduce TVA.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific un furnizor în Registrul TVA la încasare?

Dacă achiziționezi bunuri sau servicii de la un furnizor care aplică TVA la încasare, dreptul tău de deducere e amânat până plătești factura — de aceea verificarea furnizorului nu e un detaliu opțional.

## Temeiul legal

::: ghid-temei
**Art. 324 alin. (16) CF**: „A.N.A.F. organizează Registrul persoanelor impozabile care aplică sistemul TVA la încasare [...]. Registrul este public și se afișează pe site-ul A.N.A.F." Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, liniile 22087-22089.

**Art. 297 alin. (2) CF**: „Dreptul de deducere a TVA aferente achizițiilor efectuate de o persoană impozabilă de la o persoană impozabilă care aplică sistemul TVA la încasare [...] este amânat până la data la care taxa aferentă [...] a fost plătită furnizorului." Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, liniile 18732-18741.
:::

Pasul practic: cauți CUI-ul furnizorului în Registrul public al persoanelor care aplică sistemul TVA la încasare, de pe site-ul ANAF, înainte sau la momentul înregistrării facturii de achiziție. Dacă furnizorul e înscris, dreptul tău de deducere pentru acea factură apare abia când plătești (integral sau proporțional, la fiecare plată parțială) — nu la data facturii.

Mențiunea „TVA la încasare" de pe factură ar trebui să te avertizeze, dar nu înlocuiește verificarea în Registru: pot exista erori de facturare, întârzieri de înscriere sau situații tranzitorii (de exemplu firme radiate din eroare și reînscrise ulterior, cu efecte retroactive asupra dreptului tău de deducere, conform art. 324 alin. (13) și (15)).

## Ce se greșește în practică

- Se stabilește dreptul de deducere doar pe baza mențiunii de pe factură, fără verificare directă în Registrul ANAF.
- Se ignoră faptul că amânarea deducerii (art. 297 alin. 2) se aplică indiferent dacă beneficiarul însuși aplică TVA la încasare sau nu.
- Nu se reface calculul deducerii când furnizorul e radiat sau reînscris din eroare în Registru, deși legea prevede reguli explicite pentru aceste situații.

## Ce face iConta.eu

Pe factura de achiziție, contabilul bifează manual dacă furnizorul aplică TVA la încasare (`furnizor_tva_incasare`), iar aplicația folosește această informație pentru a amâna corect dreptul de deducere. Bifa este **declarativă** — iConta nu interoghează live Registrul public ANAF, verificarea rămâne responsabilitatea contabilului.

[iConta.eu](/)
