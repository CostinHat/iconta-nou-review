---
title: La ce bază se aplică impozitul pe venit pentru PFA în sistem real?
description: Impozitul de 10% nu se aplică pe tot venitul net, ci pe venitul net rămas după scăderea CAS și CASS datorate — dacă CASS e calculată greșit (de exemplu omisă), baza impozabilă iese artificial mai mare.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# La ce bază se aplică impozitul pe venit pentru PFA în sistem real?

O greșeală frecventă e să se calculeze impozitul de 10% direct pe venitul net (venit brut minus cheltuieli deductibile). Legal, baza impozabilă e mai mică: din venitul net se scad întâi CAS și CASS datorate, iar impozitul se aplică doar pe ce rămâne.

## Temeiul legal

::: ghid-temei
**Art. 118 alin.(2) lit.b):** "venitul net anual impozabil care se determină prin însumarea tuturor veniturilor nete anuale, recalculate... din care se deduc contribuția de asigurări sociale și contribuția de asigurări sociale de sănătate datorate potrivit prevederilor titlului V, cu excepția diferenței de contribuție de asigurări sociale de sănătate prevăzută la art. 174 alin. (6)."

**Art. 118 alin.(2^2):** "Contribuția de asigurări sociale deductibilă... se stabilește proporțional cu ponderea venitului net anual determinat în sistem real în total venituri cumulate potrivit prevederilor art. 148 alin. (3), aplicată asupra contribuției de asigurări sociale calculate potrivit art. 151 alin. (1)."

**Art. 118 alin.(2^3):** regulă identică pentru CASS, raportată la art. 170 alin.(1) / art. 174 alin.(1).
:::

## Formula corectă

```
baza impozabilă = venit net − CAS datorată − CASS datorată  (minim 0)
impozit = baza impozabilă × 10%
```

::: ghid-exemplu
Un PFA cu venit net de 70.000 lei (2025, salariu minim 4.050 lei) datorează CAS de 12.150 lei (bază 48.600 lei × 25%) și CASS de 7.000 lei (bază = venit net, calculată liniar, 70.000 × 10%, sub plafonul de 60 salarii minime). Baza impozabilă e 70.000 − 12.150 − 7.000 = 50.850 lei, iar impozitul e 50.850 × 10% = 5.085 lei — nu 70.000 × 10% = 7.000 lei, cum s-ar calcula greșit dacă s-ar ignora deducerea CAS/CASS.
:::

## Atenție la venituri cumulate din mai multe surse

Dacă PFA nu e singura sursă de venit independent a persoanei (de exemplu mai are și drepturi de proprietate intelectuală sau contracte de activitate sportivă cumulate la același plafon CAS/CASS), art. 118 alin. (2^2)-(2^3) cere ca CAS/CASS deductibile din baza impozabilă a PFA să fie calculate **proporțional cu ponderea venitului net al PFA în totalul veniturilor cumulate**, nu integral. Acest calcul de proporționalizare nu se face automat dacă se presupune că PFA e singura sursă de venit.

## Ce se greșește în practică

- Se aplică 10% direct pe venitul net, fără a scădea CAS și CASS datorate — impozitul iese supraevaluat.
- Se scade CASS calculată greșit (de exemplu zero, dacă venitul net e sub 6 salarii minime dar pozitiv) — baza impozabilă iese artificial mai mare, deci impozitul plătit e mai mare decât ar trebui, în timp ce CASS datorată legal ar fi trebuit inclusă la baza minimă de 6 salarii minime.
- Se ignoră proporționalizarea CAS/CASS când PFA cumulează venit cu alte surse independente la același plafon.
- Se confundă "diferența de CASS" de la art. 174 alin. (6) (care nu se deduce din baza impozabilă) cu CASS datorată obișnuit (care se deduce).

## Ce face iConta.eu

`core/d212_engine.py`, funcția `calculeaza_d212`, calculează baza impozabilă exact ca `venit_net − cas − cass` (minim 0), conform art. 118 alin. (2) lit. b). Important de reținut: dacă venitul net e pozitiv, dar sub 6 salarii minime, motorul curent calculează CASS ca opțională (0 lei, dacă nu se bifează manual opțiunea) — vezi ghidul despre obligativitatea CASS pentru detalii. Acest comportament nu reflectă corect regula legală pentru PFA (unde CASS e obligatorie la orice venit net pozitiv), iar consecința directă e că baza impozabilă calculată automat poate ieși mai mare decât ar trebui dacă CASS reală datorată nu e introdusă manual. Proporționalizarea CAS/CASS pentru surse cumulate (art. 118 alin. (2^2)-(2^3)) nu e automatizată — motorul presupune că venitul net al PFA e singura sursă la plafon.

[iConta.eu](/)
