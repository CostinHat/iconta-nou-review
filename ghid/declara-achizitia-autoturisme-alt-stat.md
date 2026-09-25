---
title: "Cum se declară achiziția de autoturisme din alt stat membru"
description: "Achiziția unui mijloc de transport nou din alt stat membru e întotdeauna impozabilă în România, indiferent de statutul cumpărătorului, și se declară prin decontul special de TVA înainte de înmatriculare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se declară achiziția de autoturisme din alt stat membru

Regimul TVA al unui autoturism adus din alt stat membru depinde decisiv de un singur criteriu legal: dacă mașina e considerată „nouă" în sensul Codului fiscal. Pentru mijloacele de transport noi, obligația de a declara achiziția e universală — se aplică oricui, indiferent dacă e sau nu înregistrat în scopuri de TVA.

## Temeiul legal

::: ghid-temei
„Sunt, de asemenea, operațiuni impozabile [...] următoarele operațiuni efectuate cu plată, pentru care locul este considerat a fi în România [...]: b) o achiziție intracomunitară de mijloace de transport noi, efectuată de orice persoană."
— Codul fiscal (Legea 227/2015), art. 268 alin. (3) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Decontul special de taxă se depune la organele fiscale competente de către persoanele care nu sunt înregistrate și care nu trebuie să se înregistreze conform art. 316, astfel: [...] b) pentru achiziții intracomunitare de mijloace de transport noi, de către orice persoană, indiferent dacă este sau nu înregistrată conform art. 317 [...] Prin excepție, persoanele care nu sunt înregistrate în scopuri de TVA, conform art. 316, indiferent dacă sunt sau nu înregistrate conform art. 317, sunt obligate să depună decontul special de taxă pentru achizițiile intracomunitare de mijloace de transport noi, înainte de înmatricularea acestora în România, dar nu mai târziu de data de 25 a lunii următoare celei în care ia naștere exigibilitatea taxei aferente respectivei achiziții intracomunitare."
— Codul fiscal, art. 324 alin. (1) lit. b) și alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din text:

- Achiziția unui mijloc de transport nou e impozabilă în România „efectuată de orice persoană" (art. 268 alin. (3) lit. b)) — inclusiv o persoană fizică fără nicio calitate de persoană impozabilă, nu doar o firmă.
- Persoanele neînregistrate în scopuri de TVA (nici conform art. 316, nici 317) plătesc taxa prin decontul special (D301), depus **înainte de înmatriculare**, nu mai târziu de 25 a lunii următoare exigibilității — termen mai strict decât regula generală de 25 a lunii următoare pentru celelalte tipuri de operațiuni.
- Persoanele înregistrate conform art. 317, care cumpără mijloace de transport care NU sunt considerate noi, au totuși obligația de a depune decontul special înainte de înmatriculare, dacă datorează taxa pentru acea achiziție (art. 324 alin. (2), a doua teză).
- Dacă mașina nu se încadrează în definiția de „mijloc de transport nou" (criterii de kilometraj și vechime de la art. 266 alin. (3)) și vânzătorul e o persoană impozabilă înregistrată în scopuri de TVA, achiziția urmează regimul obișnuit de achiziție intracomunitară taxabilă, cu taxare inversă, pentru cumpărătorii înregistrați.

## Ce se greșește în practică

- Se presupune că achiziția unui autoturism nou din alt stat membru scapă de TVA dacă cumpărătorul e o persoană fizică neînregistrată — art. 268 alin. (3) lit. b) o face impozabilă „de orice persoană", fără excepție.
- Se depune decontul special după înmatriculare, ca pe orice altă declarație lunară — pentru mijloacele de transport noi, termenul e legat explicit de momentul înmatriculării, nu doar de scadența generică de 25 a lunii următoare.
- Se confundă „mijloc de transport nou" cu „mașină nou-nouță din showroom" — criteriile legale (kilometraj, vechime de la prima punere în funcțiune) pot încadra drept „nou", fiscal, și un autoturism cu câteva mii de kilometri sau câteva luni vechime.

## Ce face iConta.eu

`core/d301.py`, modulul de decont special de TVA al iConta.eu, susține explicit tipul de operațiune 2 („achiziții intracomunitare de mijloace de transport noi"), inclusiv marcajul dedicat pe numărul de evidență al declarației (`mij_transp`), care semnalează prezența unei asemenea achiziții în perioada declarată. Calculul bazei (`calc_baza`) și al declarației urmează structura validată de ANAF pentru D301.

Aplicația nu determină ea însăși dacă un autoturism concret se încadrează în definiția fiscală de „mijloc de transport nou" (criteriile de kilometraj și vechime de la art. 266 alin. (3)) — încadrarea tipului de operațiune (2, pentru transport nou, sau 1, pentru achiziție obișnuită) rămâne o alegere manuală a contabilului la introducerea datelor.

[iConta.eu](/)
