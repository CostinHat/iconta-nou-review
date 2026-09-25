---
title: "Poate un SRL reveni la impozit micro după ce a trecut la impozit pe profit?"
description: "Condițiile și termenul în care o microîntreprindere care a devenit plătitoare de impozit pe profit poate reveni la sistemul de impunere pe veniturile microîntreprinderilor."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Poate un SRL reveni la impozit micro după ce a trecut la impozit pe profit?

Da, dar nu oricând și nu automat. Un SRL care a devenit plătitor de impozit pe profit — fie pentru că a depășit plafonul de venituri, fie pentru că a pierdut alt criteriu de la art. 47 din Codul fiscal — poate reveni la impozitul pe veniturile microîntreprinderilor, însă doar prin opțiune exprimată pentru anul fiscal următor celui în care redevine eligibil, nu în cursul aceluiași an.

## Temeiul legal

::: ghid-temei
„(1) Impozitul reglementat de prezentul titlu este opțional.
(2) Persoanele juridice române pot opta să aplice impozitul reglementat de prezentul titlu începând cu anul fiscal următor celui în care îndeplinesc condițiile de microîntreprindere prevăzute la art. 47 alin. (1). [...]
(2^1) Microîntreprinderile nu pot opta pentru plata impozitului pe profit în cursul anului fiscal, opțiunea putând fi exercitată începând cu anul fiscal următor, cu excepțiile prevăzute la art. 52. Opțiunea se comunică organelor fiscale competente, potrivit prevederilor Legii nr. 207/2015 privind Codul de procedură fiscală, cu modificările și completările ulterioare."
— Legea nr. 227/2015 (Codul fiscal), art. 48 alin. (1), (2), (2^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul funcționează astfel:

- Revenirea la impozitul micro este **opțională**, nu automată — firma trebuie să comunice organelor fiscale opțiunea, potrivit Codului de procedură fiscală.
- Opțiunea se poate exercita numai **începând cu anul fiscal următor** celui în care sunt din nou îndeplinite condițiile de la art. 47 alin. (1) — venituri sub 100.000 euro, capital social nedeținut de stat, cel puțin un salariat, situații financiare depuse la termen etc.
- Simetric, alin. (2^1) confirmă regula: nici trecerea de la micro la profit, nici revenirea de la profit la micro nu se pot face „din mers", în cursul anului fiscal curent — cu excepția situațiilor speciale de ieșire forțată reglementate la art. 52.

## Ce se greșește în practică

- Se crede că revenirea la impozitul micro se face imediat ce firma redevine eligibilă (de exemplu, imediat ce veniturile scad sub plafon), fără să se aștepte anul fiscal următor.
- Se omite depunerea declarației de mențiuni prin care se comunică organului fiscal opțiunea pentru sistemul micro, considerându-se că simpla îndeplinire a condițiilor e suficientă.
- Se confundă „ieșirea forțată" din sistemul micro (art. 52, în cursul anului, la depășirea plafonului) cu „revenirea" la impozitul micro, care are reguli proprii, de la art. 48.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu decide și nu recomandă automat momentul din care o firmă poate reveni la impozitul micro. Aplicația are, în profilul firmei, un câmp `regim_fiscal` cu valorile „micro" sau „profit" (vezi `core/vector_fiscal_api.py`), pe baza căruia motorul fiscal stabilește ce declarații sunt datorate — D100 trimestrial pentru regimul micro, D101 anual pentru regimul profit (`core/d100.py`, `core/d101.py`). Contabilul este cel care evaluează îndeplinirea condițiilor de la art. 47 și setează manual regimul corect în profilul firmei; iConta.eu nu validează eligibilitatea pentru revenirea la sistemul micro și nu depune declarația de mențiuni către ANAF.

[iConta.eu](/)
