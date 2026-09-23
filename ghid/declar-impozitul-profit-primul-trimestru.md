---
title: "Cum declar impozitul pe profit în primul trimestru după ieșirea de la micro?"
description: "Primul trimestru de impozit pe profit după ieșirea de la micro se declară prin D100, cu codul de obligație 103, nu prin D101."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum declar impozitul pe profit în primul trimestru după ieșirea de la micro?

Declararea propriu-zisă a primului trimestru de impozit pe profit, după depășirea plafonului de microîntreprindere, nu se face prin D101 — D101 este exclusiv declarația anuală de definitivare.

## Temeiul legal

::: ghid-temei
"«121»: «5503XXXXXX», poz.5 Nomenclator: impozit pe veniturile microîntreprinderilor; «103»: «5503XXXXXX», poz.2 Nomenclator: impozit pe profit/plăți anticipate PJ române [...] Deci plățile trimestriale/anticipate de impozit pe profit (cod_oblig 103) se depun prin D100, nu prin D101." — dosarul de cercetare F027, pe baza `core/d100.py`, nomenclator `COD_BUGETAR`.
:::

Pentru primul trimestru în care firma datorează deja impozit pe profit (conform art.52 alin.(1) și (6): de la trimestrul depășirii plafonului de 100.000 EUR, nu retroactiv), declarația folosită este D100, cu codul de obligație 103. Elementele de curs valutar din acel trimestru se tratează ca venituri similare, conform art.53 alin.(2) lit.b).

## Ce se greșește în practică

Greșeala tipică e căutarea acestei declarații trimestriale în fluxul D101 — D101 nu are rol trimestrial, indiferent de momentul din an în care firma a trecut la impozit pe profit.

## Ce face iConta.eu

Declararea trimestrială, inclusiv pentru primul trimestru după ieșirea din regimul micro, se face prin D100 (cod 103). D101 intervine abia la finalul anului, pentru definitivarea perioadei în care firma a fost efectiv plătitoare de impozit pe profit.

[iConta.eu](/)
