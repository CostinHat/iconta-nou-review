---
title: "Care este monografia contabilă pentru casarea unui mijloc fix?"
description: "Nota de casare generată automat de iConta.eu folosește contul indicat în cod ca 'PV comisie' — ce calculează aplicația și ce rămâne responsabilitatea contabilului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Care este monografia contabilă pentru casarea unui mijloc fix?

Casarea generează o notă contabilă, dar aceasta rămâne o ciornă până e validată — nu o înregistrare automată definitivă.

## Temeiul legal

::: ghid-temei
"Câștigurile sau pierderile rezultate din vânzarea ori din scoaterea din funcțiune a acestor mijloace fixe se calculează pe baza valorii fiscale a acestora, diminuată cu amortizarea fiscală, cu excepția celor prevăzute la alin. (14)." — Codul fiscal, art. 28 alin. (17)
:::

Baza rezultatului e valoarea fiscală a activului diminuată cu amortizarea fiscală calculată la zi — adică valoarea rămasă la data casării.

## Ce se greșește în practică

Se presupune că nota de casare generată automat e deja o înregistrare finală în contabilitate, fără să fie validată din Registrul jurnal, sau se ignoră contul specific folosit de aplicație pentru această operațiune.

## Ce face iConta.eu

Când un mijloc fix e casat (cu `mijloc_fix_id`), aplicația calculează automat amortizarea la zi pe metoda reală a activului și generează o notă ciornă folosind, conform codului sursă, contul indicat ca "PV comisie". Nota trebuie validată separat din Registrul jurnal înainte de a deveni definitivă — dosarul de cercetare nu detaliază o monografie completă cu toate conturile implicate dincolo de acest cont.

[iConta.eu](/)
