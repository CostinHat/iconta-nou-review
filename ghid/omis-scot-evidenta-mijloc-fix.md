---
title: "Am omis să scot din evidență un mijloc fix vândut"
description: "Cum se corectează registrul de mijloace fixe atunci când un activ vândut a rămas activ în evidență."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Am omis să scot din evidență un mijloc fix vândut

Dacă un mijloc fix a fost vândut, dar a rămas marcat ca activ în registru, amortizarea continuă să se calculeze pentru el la fiecare interogare — trebuie corectat cât mai curând.

## Temeiul legal

::: ghid-temei
"Câștigurile sau pierderile rezultate din vânzarea ori din scoaterea din funcțiune a acestor mijloace fixe se calculează pe baza valorii fiscale a acestora, diminuată cu amortizarea fiscală, cu excepția celor prevăzute la alin. (14)."
— Codul fiscal, art.28 alin.(17)
:::

Corecția presupune scoaterea activului din evidență la data reală a vânzării, astfel încât amortizarea calculată să se oprească la acea dată, iar valoarea fiscală rămasă la momentul respectiv să poată fi folosită corect în calculul câștigului sau pierderii din vânzare.

## Ce se greșește în practică

Greșeala inițială — omiterea scoaterii din evidență — duce de obicei la o amortizare suplimentară calculată eronat pentru perioade ulterioare vânzării, care trebuie identificată și corectată retroactiv.

## Ce face iConta.eu

Ecranul de Casare este singura acțiune de ieșire din registru descrisă în acest dosar — o poți folosi pentru a dezactiva activul, iar amortizarea la zi (`amortizat_la_data`) se calculează automat, pe metoda reală a activului, până la data introdusă. Nota generată e ciornă, validată separat din Registrul jurnal, deci corecția nu se aplică direct fără validare contabilă.

[iConta.eu](/)
