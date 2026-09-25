---
title: "Termenul de transmitere a D301 pentru achiziții intracomunitare"
description: "Data limită de depunere a decontului special de TVA (formularul 301) pentru achizițiile intracomunitare care generează obligație de taxare inversă în România."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Termenul de transmitere a D301 pentru achiziții intracomunitare

Formularul 301 „Decont special de taxă pe valoarea adăugată" este declarația pe care o depun, printre alții, persoanele care nu sunt înregistrate normal în scopuri de TVA (de exemplu, cele aflate sub plafonul de scutire) atunci când fac o achiziție intracomunitară de bunuri pentru care se datorează totuși TVA în România. Termenul de depunere depinde de tipul operațiunii, iar confuzia cea mai frecventă e legată de excepția mijloacelor de transport.

## Temeiul legal

```
::: ghid-temei
„Formularul se întocmeşte potrivit modelului din anexa nr. 1 la ordin şi se depune după cum urmează:
a) până la data de 25 inclusiv a lunii următoare celei în care ia naştere exigibilitatea operaţiunilor prevăzute la secţiunile 1, 3, 4 şi 4.1 din formularul (301) «Decont special de taxă pe valoarea adăugată», cu excepţia achiziţiilor intracomunitare de mijloace de transport care nu sunt considerate noi conform art. 266 alin. (3) din Codul fiscal, pentru care se datorează taxă pe valoarea adăugată în România;
b) înainte de înmatricularea în România a unui mijloc de transport nou sau a unui mijloc de transport care nu este considerat nou conform art. 266 alin. (3) din Codul fiscal şi pentru care se datorează taxa, dar nu mai târziu de data de 25 a lunii următoare celei în care ia naştere exigibilitatea taxei aferentă achiziţiei intracomunitare de astfel de mijloace de transport."
— OPANAF nr. 592/2016 pentru aprobarea formularului (301), pct. II (sursă: anaf_surse/opanaf_592_2016_d301.txt)
:::
```

Din instrucțiunile de completare rezultă două reguli practice:

- **Regula generală:** decontul special se depune **până la data de 25 inclusiv a lunii următoare** celei în care ia naștere exigibilitatea taxei — aceeași logică temporală ca la decontul obișnuit de TVA (D300), dar cu formular și scop diferite.
- **D301 se depune doar pentru perioadele în care apare efectiv exigibilitatea taxei** — nu e o declarație lunară obligatorie „pe zero", ca D300; dacă într-o lună nu există nicio operațiune de acest tip, nu se depune decont special.
- **Excepția mijloacelor de transport:** pentru achiziția intracomunitară a unui mijloc de transport nou, sau a unuia care nu e considerat nou dar pentru care se datorează TVA în România, decontul se depune **înainte de înmatriculare**, cu limita finală tot data de 25 a lunii următoare exigibilității.
- Exigibilitatea taxei, pentru achiziții intracomunitare, intervine la data facturii emise potrivit legislației statului membru al furnizorului sau, dacă nu s-a emis nicio factură, cel târziu în a 15-a zi a lunii următoare faptului generator.

## Ce se greșește în practică

- Se aplică regula generală (25 a lunii următoare) și în cazul unui mijloc de transport care trebuie înmatriculat mai devreme — decontul trebuie depus înainte de înmatriculare, chiar dacă asta înseamnă înainte de data de 25.
- Se depune D301 „preventiv", în fiecare lună, deși nu a existat nicio achiziție cu exigibilitate în acea perioadă — declarația se depune numai când apare efectiv obligația.
- Se calculează exigibilitatea taxei de la data primirii mărfii, ignorând regula facturii furnizorului extern sau, în lipsa ei, termenul de 15 zile de la faptul generator.

## Ce face iConta.eu

La data acestui ghid, `core/d301.py` există ca modul dedicat generării decontului special de TVA din operațiunile înregistrate, inclusiv logica de taxare inversă la achizițiile intracomunitare — confirmată prin validatorul oficial ANAF potrivit disciplinei de lucru a proiectului. Urmărirea termenului specific pentru mijloacele de transport (înainte de înmatriculare, nu neapărat la data de 25) rămâne o verificare pe care contabilul o face manual, în funcție de data reală de înmatriculare a fiecărui vehicul.

[iConta.eu](/)
