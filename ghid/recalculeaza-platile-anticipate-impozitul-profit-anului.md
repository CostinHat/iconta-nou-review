---
title: "Se recalculează plățile anticipate dacă impozitul pe profit al anului precedent se corectează?"
description: "Da. Dacă impozitul pe profit al anului precedent se corectează, plățile anticipate din trimestrul corecției se calculează pe impozitul recalculat; trimestrele anterioare rămân la fel."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Se recalculează plățile anticipate dacă impozitul pe profit al anului precedent se corectează?

Da, dar numai înainte, nu și înapoi. Firma poate aplica sistemul anual de declarare, cu plăți anticipate trimestriale. Dacă în cursul anului impozitul pe profit al anului precedent se modifică, printr-o declarație rectificativă sau printr-o decizie de impunere după control, plățile anticipate **datorate începând cu trimestrul în care are loc modificarea** se calculează pe impozitul recalculat. Plățile trimestrelor deja scadente nu se refac.

Regula privește doar firmele în sistemul anual cu plăți anticipate. Cele în sistemul trimestrial obișnuit plătesc pe profitul cumulat al anului curent, nu pe impozitul anului precedent.

## Temeiul legal

::: ghid-temei
„În situația în care, în cursul anului pentru care se efectuează plățile anticipate, impozitul pe profit aferent anului precedent se modifică și se corectează în condițiile prevăzute de Codul de procedură fiscală, plățile anticipate care se datorează începând cu trimestrul efectuării modificării se determină în baza impozitului pe profit recalculat.”
— HG 1/2016, Normele metodologice ale Codului fiscal, titlul II pct. 41 alin. (3) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

::: ghid-temei
„Impozitul pe profit pentru anul precedent, pe baza căruia se determină plățile anticipate trimestriale, este impozitul pe profit anual, conform declarației privind impozitul pe profit.”
— Codul fiscal (Legea 227/2015), art. 41 alin. (8) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Prin excepție de la prevederile alin. (8) [...] plata anticipată pentru trimestrul I al fiecărui an fiscal/an fiscal modificat se calculează prin aplicarea cotei de impozit asupra profitului contabil al perioadei pentru care se efectuează plata anticipată.”
— Codul fiscal (Legea 227/2015), art. 41 alin. (10^1), aplicabil din anul fiscal 2026 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cum se aplică în 2026:

- **Baza obișnuită:** plățile anticipate sunt, fiecare, o pătrime din impozitul pe profit al anului precedent, actualizat cu indicele prețurilor de consum (art. 41 alin. (8)).
- **Trimestrul I e o excepție din 2026.** Plata pentru trimestrul I se calculează aplicând cota de impozit pe profitul contabil al trimestrului (alin. (10^1)), nu pe impozitul anului precedent. Recalcularea după o corecție afectează, deci, doar plățile trimestrelor II-IV.
- **Momentul contează.** Recalcularea pornește cu trimestrul în care se face modificarea. O rectificativă depusă în august, adică în trimestrul III, schimbă plățile pentru trimestrele III și IV. Plățile trimestrelor I și II rămân neschimbate.
- **În ambele sensuri.** Dacă impozitul corectat e mai mare, plățile cresc. Dacă e mai mic, scad.
- **Regularizarea finală** se face tot prin D101 pe anul curent. Plățile anticipate sunt doar avansuri.

::: ghid-exemplu
SC Exemplu SRL aplică sistemul anual cu plăți anticipate. D101 pe 2025 arată un impozit de 40.000 lei. Pentru simplitate, presupunem un indice al prețurilor de consum care nu modifică suma. Plata pentru trimestrul II 2026 este 40.000 / 4 = 10.000 lei.

În august 2026, firma depune D101 rectificativă pe 2025, cu un impozit corectat de 60.000 lei.

- Trimestrul II: rămâne 10.000 lei, deja datorat.
- Trimestrul III, în care s-a făcut modificarea: 60.000 / 4 = 15.000 lei.
- Trimestrul IV: 15.000 lei, până la 25 decembrie 2026.

Plata pentru trimestrul I 2026 a fost calculată pe profitul contabil al trimestrului, deci corecția nu o afectează.
:::

## Ce se greșește în practică

- Plățile anticipate continuă pe vechea bază după o rectificativă sau după o decizie de impunere.
- Se refac retroactiv și plățile trimestrelor deja scadente, deși recalcularea privește doar trimestrele de la modificare încolo.
- Se aplică în 2026 regula veche și la trimestrul I, calculat tot pe impozitul anului precedent, deși alin. (10^1) cere profitul contabil al trimestrului.
- Regula e aplicată firmelor în sistemul trimestrial, unde plata nu depinde de impozitul anului precedent.

## Ce face iConta.eu

iConta.eu generează D100 pentru impozitul pe profit în sistemul trimestrial, pe baza profitului cumulat de la începutul anului, și D101 anual. Declarațiile se validează pe validatorul oficial ANAF. Pentru sistemul anual cu plăți anticipate, aplicația nu are, la acest moment, un calcul dedicat al plăților pe baza impozitului anului precedent, deci nici recalcularea automată după o corecție. Stabilirea acestor sume rămâne a contabilului.

[iConta.eu](/)
