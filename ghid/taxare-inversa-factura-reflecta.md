---
title: "Taxare inversă în e-Factura: cum se reflectă"
description: O factură marcată cu taxare inversă circulă fără TVA colectată de furnizor și e reflectată automat, la beneficiar, atât ca taxă colectată, cât și ca taxă deductibilă, prin declarațiile D300 și D394.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Taxare inversă în e-Factura: cum se reflectă

O factură cu taxare inversă nu poartă TVA înscrisă de furnizor — taxa se calculează la beneficiar și se reflectă simultan pe două direcții: contabil, la beneficiar, și, ulterior, în declarațiile de TVA ale ambelor părți.

## Temeiul legal

::: ghid-temei
„Pe facturile emise pentru livrările de bunuri/prestările de servicii prevăzute la alin. (2) furnizorii/prestatorii nu vor înscrie taxa colectată aferentă. Beneficiarii vor determina taxa aferentă, care se va evidenția în decontul prevăzut la art. 323, atât ca taxă colectată, cât și ca taxă deductibilă."
— Legea 227/2015, art. 331 alin. (3)
:::

::: ghid-temei
„Din punct de vedere contabil, beneficiarul înregistrează în cursul perioadei fiscale în care taxa este exigibilă suma taxei aferente în următoarea formulă contabilă: 4426 = 4427."
— HG 1/2016, pct. 109 alin. (1)
:::

Concret, o achiziție cu taxare inversă se reflectă:
- **Contabil, la beneficiar**: `4426 = 4427` (taxă deductibilă = taxă colectată, simultan, sumă netă zero pe TVA de plată).
- **În decontul de TVA (D300)**: la beneficiar, taxa apare atât la rândurile de taxă colectată, cât și la cele de taxă deductibilă aferente taxării inverse — impact net zero pe TVA de plată, dar suma rămâne vizibilă în totalurile de colectat/deductibil ale decontului, nu dispare din el. La furnizor, baza livrării apare pe rândul dedicat livrărilor cu taxare inversă.
- **În declarația D394**: operațiunea se declară cu un tip specific de operațiune — „C" (achiziție cu taxare inversă) la beneficiar, „V" (livrare cu taxare inversă) la furnizor, cu cotă declarată 0 la livrare.

Dacă factura nu poartă mențiunea „taxare inversă" deși ar fi trebuit, iar beneficiarul deduce totuși TVA înscrisă greșit pe factură, acesta **își pierde dreptul de deducere** pentru operațiunea respectivă (norme pct. 109 alin. (4)).

**Notă**: structura exactă a câmpurilor din fișierul XML RO e-Factura (dincolo de etichetele oficiale ale rândurilor de decont și tipurile de operațiune D394 de mai sus) nu a fost verificată separat pentru acest ghid.

## Ce se greșește în practică

- Se introduce manual, în decont, aceeași sumă care e deja preluată automat din factura marcată cu taxare inversă — riscul e dubla numărare a taxei colectate/deductibile.
- Se confundă rândurile D300 aferente taxării inverse interne (art. 331) cu cele aferente achizițiilor intracomunitare — sunt rânduri și mecanisme diferite.
- Se presupune că o comparație automată între D300 și D394 pe operațiunile de taxare inversă confirmă corectitudinea economică a tranzacției — de fapt, ambele declarații citesc din același flag de pe factură, deci coerența dintre ele arată doar consecvență internă, nu o verificare independentă.

## Ce face iConta.eu

Pentru o factură primită marcată cu taxare inversă, aplicația generează automat nota `4426=4427` și populează simultan rândurile de taxă colectată și deductibilă din D300, plus tipul „C" în D394; pentru o factură emisă, populează rândul de bază din D300 și tipul „V", cu cotă 0, în D394. Există o gardă anti-dublă-numărare: dacă aceeași sumă e introdusă și automat din factură, și manual într-un rând de decont, aplicația respinge operațiunea cu eroare explicită. Structura tehnică exactă a fișierului XML RO e-Factura nu a fost verificată separat pentru acest ghid.

[iConta.eu](/)
