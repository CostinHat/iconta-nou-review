---
title: Cum se calculează impozitul de 10% pentru PFA?
description: Impozitul pe venit al unui PFA în sistem real e 10% aplicat pe venitul net rămas după scăderea CAS și CASS datorate, nu pe venitul net brut de contribuții — iar rotunjirea diferă între fișa de calcul (la bănuț) și declarația D212 efectivă (la leu întreg).
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se calculează impozitul de 10% pentru PFA?

Cota de impozit pentru veniturile din activități independente e fixă, 10%, dar baza pe care se aplică nu e venitul net brut — e venitul net din care s-au scăzut deja CAS și CASS datorate pentru anul respectiv.

## Temeiul legal

::: ghid-temei
**Art. 64 alin.(1):** "Cota de impozit este de 10% și se aplică asupra venitului impozabil corespunzător fiecărei surse din fiecare categorie pentru determinarea impozitului pe veniturile din: a) activități independente; ..."

**Art. 118 alin.(2) lit.b):** "venitul net anual impozabil care se determină prin însumarea tuturor veniturilor nete anuale, recalculate... din care se deduc contribuția de asigurări sociale și contribuția de asigurări sociale de sănătate datorate potrivit prevederilor titlului V, cu excepția diferenței de contribuție de asigurări sociale de sănătate prevăzută la art. 174 alin. (6)."
:::

## Pașii de calcul

```
1. venit net       = venit brut − cheltuieli deductibile        (minim 0)
2. CAS datorată     = conform pragurilor de 12/24 salarii minime
3. CASS datorată    = conform obligativității pentru activități independente
4. baza impozabilă  = venit net − CAS − CASS                    (minim 0)
5. impozit          = baza impozabilă × 10%
```

::: ghid-exemplu
Venit net 60.000 lei (2025, salariu minim 4.050 lei). CAS: în treapta 12–24 salarii minime, bază 48.600 lei × 25% = 12.150 lei. CASS: venit net între 6 și 60 salarii minime, bază = venitul net (liniar) = 60.000 × 10% = 6.000 lei. Baza impozabilă = 60.000 − 12.150 − 6.000 = 41.850 lei. Impozit = 41.850 × 10% = 4.185 lei.
:::

## Rotunjirea diferă între fișa de calcul și declarația D212

Fișa de calcul internă rotunjește sumele la bănuț (2 zecimale). Declarația D212 efectivă, la generarea XML, rotunjește sumele la leu întreg, pentru că formatul XSD al formularului cere valori întregi. E normal ca fișa de calcul afișată să conțină zecimale, iar suma finală depusă la ANAF să apară rotunjită la leu — nu e o eroare de calcul, ci o diferență de granularitate între cele două reprezentări.

## Ce se greșește în practică

- Se aplică 10% direct pe venitul net, fără a scădea CAS și CASS — impozitul rezultă supraevaluat.
- Se calculează CAS ca procent din venitul net efectiv, în loc de baza plafonată în trepte de 12/24 salarii minime, ceea ce denaturează și impozitul final.
- Se ignoră faptul că CASS trebuie inclusă în deducere chiar și la venituri sub 6 salarii minime, dacă venitul net e pozitiv — omiterea ei umflă artificial baza impozabilă.
- Se compară suma din fișa de calcul (cu zecimale) cu suma din declarația depusă (rotunjită la leu întreg) și se crede că există o eroare, când de fapt e doar o diferență de rotunjire.

## Ce face iConta.eu

`core/d212_engine.py`, funcția `calculeaza_d212`, implementează exact pașii de mai sus: `venit_net = venit_brut − cheltuieli_deductibile`, apoi CAS și CASS conform funcțiilor dedicate, `baza_impozit = max(0, venit_net − cas − cass)`, iar `impozit = baza_impozit × 10%`. Rotunjirea în motorul de calcul se face la bănuț (`Decimal` cu `ROUND_HALF_UP`); generatorul XML (`core/d212.py`, funcția `_lei()`) rotunjește separat la leu întreg pentru câmpurile declarației, folosind aceeași metodă de rotunjire, dar precizie diferită. Un aspect de verificat manual: dacă venitul net e pozitiv dar sub pragul de 6 salarii minime, CASS calculată automat de motor poate ieși zero — ceea ce afectează direct și impozitul final calculat aici (vezi ghidul despre obligativitatea CASS).

[iConta.eu](/)
