---
title: "Monografia casării unui mijloc fix complet amortizat"
description: "Pentru un mijloc fix complet amortizat, casarea în iConta.eu folosește contul 'PV comisie' — ce anume calculează și generează automat aplicația."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Monografia casării unui mijloc fix complet amortizat

Când mijlocul fix e complet amortizat, valoarea rămasă la data casării e zero — dar procesul de casare rămâne același.

## Temeiul legal

::: ghid-temei
"Câștigurile sau pierderile rezultate din vânzarea ori din scoaterea din funcțiune a acestor mijloace fixe se calculează pe baza valorii fiscale a acestora, diminuată cu amortizarea fiscală, cu excepția celor prevăzute la alin. (14)." — Codul fiscal, art. 28 alin. (17)
:::

Pentru un activ complet amortizat, diferența dintre valoarea fiscală și amortizarea fiscală e zero — deci nu rezultă niciun câștig sau pierdere fiscală suplimentară din casare, dincolo de eventualele costuri de dezmembrare/valorificare.

## Ce se greșește în practică

Se presupune eronat că, fiind complet amortizat, activul nu mai trebuie trecut prin fluxul de casare din registru — ceea ce lasă activul "activ" în evidență, deși nu mai există fizic.

## Ce face iConta.eu

Casarea unui mijloc fix (prin `mijloc_fix_id`) calculează automat amortizarea la zi, indiferent dacă activul e deja complet amortizat sau nu, și dezactivează activul. Nota generată e o ciornă și folosește contul indicat în cod ca "PV comisie" — validarea finală, cu conturile complete, se face separat din Registrul jurnal.

[iConta.eu](/)
