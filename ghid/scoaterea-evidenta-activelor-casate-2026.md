---
title: "Scoaterea din evidență a activelor casate 2026"
description: "Casarea unui mijloc fix calculează automat amortizarea la zi și dezactivează activul din registru — cum funcționează în iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Scoaterea din evidență a activelor casate 2026

Casarea este operațiunea prin care un mijloc fix e scos din folosință (uzură, distrugere, decizie a firmei) și, implicit, din evidența activă a registrului.

## Temeiul legal

::: ghid-temei
"Câștigurile sau pierderile rezultate din vânzarea ori din scoaterea din funcțiune a acestor mijloace fixe se calculează pe baza valorii fiscale a acestora, diminuată cu amortizarea fiscală, cu excepția celor prevăzute la alin. (14)." — Codul fiscal, art. 28 alin. (17)
:::

Scoaterea din funcțiune presupune, ca și vânzarea, calculul rezultatului pe baza valorii fiscale diminuate cu amortizarea fiscală — adică valoarea rămasă a activului la data casării.

## Ce se greșește în practică

Se calculează manual amortizarea la data casării, riscând erori dacă activul are o metodă de amortizare mai complexă (degresivă, accelerată) decât liniara, sau se uită dezactivarea activului în evidență după casare.

## Ce face iConta.eu

Acțiunea **Casează** din registru pornește o operațiune de tip nota-inventariere: pentru un mijloc fix cu `mijloc_fix_id`, aplicația calculează automat amortizarea la zi (pe metoda reală a activului) și dezactivează activul (`activ=false`). Nota rezultată e generată ca **ciornă** și trebuie validată separat din Registrul jurnal — nu se aplică direct pe registrul de mijloace fixe.

[iConta.eu](/)
