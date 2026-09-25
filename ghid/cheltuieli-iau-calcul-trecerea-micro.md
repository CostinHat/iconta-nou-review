---
title: "Ce cheltuieli se iau în calcul după trecerea de la micro la profit?"
description: "Regula din Codul fiscal privind veniturile și cheltuielile luate în calcul la impozitul pe profit, atunci când o microîntreprindere trece în cursul anului la impozit pe profit."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce cheltuieli se iau în calcul după trecerea de la micro la profit?

Când o microîntreprindere depășește plafonul de venituri sau nu mai îndeplinește condițiile de la art. 47, trece la impozit pe profit în cursul anului fiscal, nu de la 1 ianuarie. Întrebarea practică e imediată: cheltuielile din trimestrele anterioare trecerii mai intră în calculul impozitului pe profit sau nu?

## Temeiul legal

::: ghid-temei
„(6) Calculul și plata impozitului pe profit de către microîntreprinderile care se încadrează în prevederile alin. (1), (2), (4) și (7) se efectuează luând în considerare veniturile și cheltuielile realizate începând cu trimestrul respectiv."
— Legea 227/2015 (Codul fiscal), art. 52 alin. (6) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Consecința e directă: **doar veniturile și cheltuielile din trimestrul în care are loc trecerea, și cele din trimestrele următoare, intră în baza de calcul a impozitului pe profit.** Situațiile care declanșează trecerea, conform art. 52:

- **alin. (1)** — venituri peste 100.000 euro în cursul anului (calculate cumulat de la începutul anului fiscal, alin. 5): impozit pe profit de la trimestrul în care s-a depășit plafonul.
- **alin. (2)** — nedepunerea în termen a situațiilor financiare anuale pentru exercițiul precedent: impozit pe profit de la trimestrul în care condiția nu mai e îndeplinită.
- **alin. (3)** — pierderea condiției privind angajatul (art. 47 alin. 1 lit. g), cu excepția înlocuirii salariatului în 30 de zile: impozit pe profit de la trimestrul următor încetării raportului de muncă.
- **alin. (4)** — începerea, în cursul unui trimestru, a unei activități dintre cele excluse de la regimul micro (art. 47 alin. 3 lit. f)-i), de regulă activități din domenii reglementate: impozit pe profit de la trimestrul respectiv.
- **alin. (7)** — deținerea a peste 25% din mai multe microîntreprinderi de către același asociat: una dintre firme trebuie să iasă din regim, de la trimestrul în care se constată situația.

Practic, cheltuielile din trimestrele anterioare trecerii — cele în care firma era încă microîntreprindere și plătea impozit pe cifra de afaceri — **nu se recuperează** și nu intră retroactiv în calculul impozitului pe profit. Contribuabilul „pornește de la zero" cu veniturile și cheltuielile contabilizate începând cu trimestrul trecerii.

## Ce se greșește în practică

- Se cumulează cheltuielile de la 1 ianuarie la calculul impozitului pe profit, deși legea limitează explicit baza la veniturile și cheltuielile „realizate începând cu trimestrul respectiv" (alin. 6) — nu de la începutul anului fiscal.
- Se confundă trimestrul de referință pentru cheltuieli cu trimestrul în care s-a depășit plafonul de venituri la alin. (1) — de fapt trecerea e efectivă chiar din trimestrul depășirii, nu din trimestrul următor.
- Se tratează diferit trimestrul de referință în funcție de motivul trecerii, deși pentru alin. (1), (2) și (4) impozitul pe profit se calculează de la trimestrul respectiv, în timp ce pentru alin. (3) e de la trimestrul următor — o confuzie frecventă care duce la o declarație greșită.

## Ce face iConta.eu

iConta.eu calculează Declarația 100/101 pornind de la regimul fiscal (micro sau profit) configurat pentru firmă în vector fiscal, cu cota implicită de 1% pentru micro și 16% pentru profit (`core/d100.py`, `core/d101.py`) — regim pe care contabilul îl setează la nivel de firmă. La data acestui ghid, aplicația **nu automatizează recalcularea automată a trimestrului de tranziție** conform art. 52 alin. (6): dacă o firmă trece de la micro la profit în cursul anului, contabilul trebuie să schimbe manual regimul fiscal începând cu trimestrul corect și să se asigure că veniturile și cheltuielile introduse pentru calculul de profit pornesc de la acel trimestru, nu de la 1 ianuarie.

[iConta.eu](/)
