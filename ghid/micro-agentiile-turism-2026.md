---
title: "Micro pentru agențiile de turism 2026"
description: "Condițiile de încadrare la impozitul pe veniturile microîntreprinderilor pentru o agenție de turism în 2026 și de ce acest regim e complet independent de regimul special de TVA al agențiilor de turism."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Micro pentru agențiile de turism 2026

O agenție de turism se poate încadra la impozitul pe veniturile microîntreprinderilor exact ca orice altă firmă — Codul fiscal nu prevede nicio condiție specială legată de codul CAEN de turism. Important de reținut e că acest regim (Titlul III, impozit pe venit) nu are nicio legătură cu regimul special de TVA pentru agențiile de turism (art. 311, marja de profit) — sunt două taxe diferite, cu temeiuri diferite, care se pot aplica simultan, independent una de cealaltă.

## Temeiul legal

::: ghid-temei
„(1) În sensul prezentului titlu, o microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent: [...]
c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. [...]
(1^1) În aplicarea prevederilor alin. (1) lit. c) limita privind veniturile realizate se verifică luând în calcul veniturile realizate de persoana juridică română, cumulate cu veniturile întreprinderilor legate cu aceasta, iar veniturile care se iau în calcul sunt cele care constituie cifra de afaceri definită potrivit reglementărilor contabile aplicabile [...]"
— Legea nr. 227/2015 (Codul fiscal), art. 47 alin. (1) lit. c) și alin. (1^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Pragul de 100.000 euro se verifică pe **cifra de afaceri definită contabil**, nu pe marja de profit din regimul special de TVA — cele două noțiuni ("venituri" la impozitul pe micro vs. "marjă" la TVA art. 311) au baze de calcul complet diferite și nu trebuie amestecate.
- Lista de exceptări explicite de la regimul micro (art. 47 alin. (3): bancar, asigurări, jocuri de noroc, explorare petrol și gaze) **nu include** agențiile de turism — deci nicio agenție de turism nu e exclusă din start de la regimul micro pe motiv de domeniu de activitate.
- Condiția de la lit. h) (asociat unic desemnat pentru grupuri de firme legate prin peste 25% din capital) și cea de la lit. g) (cel puțin un salariat) se aplică identic, indiferent de domeniu.

## Ce se greșește în practică

- Se caută o excepție CAEN specială pentru turism, ca la domeniile explicit excluse (bancar, asigurări, jocuri de noroc, petrol și gaze) — nu există niciuna pentru turism.
- Se calculează pragul de 100.000 euro pornind de la marja de profit taxabilă (baza de TVA din regimul special art. 311), în loc de veniturile/cifra de afaceri contabilă — sunt cifre diferite, iar legea la art. 47 alin. (1^1) e explicită: se ia în calcul cifra de afaceri, nu baza de TVA.
- Se presupune că regimul special de TVA (marja de profit, art. 311) și regimul micro (impozit pe venit, art. 47) sunt „aceeași facilitate" sau că unul îl exclude pe celălalt — sunt independente: o agenție poate fi simultan plătitoare de TVA în regim special art. 311 ȘI impozitată pe veniturile microîntreprinderilor.

## Ce face iConta.eu

Pentru o firmă de turism, iConta.eu tratează separat cele două regimuri: regimul de TVA (normal, special art. 311 sau intermediar, calculat prin motorul dedicat din `core/tva_marja_turism.py`) și regimul de impozit pe venit (micro sau profit), setat ca un câmp propriu al firmei, care determină generarea D100 (micro) sau D101 (profit). Aplicația nu unifică sau nu condiționează un regim de celălalt și nu verifică automat, pe baza cifrei de afaceri sau a codului CAEN, dacă agenția îndeplinește condițiile de la art. 47 pentru încadrarea la micro — alegerea și verificarea condițiilor rămân, ca pentru orice firmă, responsabilitatea contabilului.

[iConta.eu](/)
