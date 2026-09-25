---
title: "Se poate încasa în numerar o factură mai mare de 5.000 lei?"
description: "Cât se poate încasa în numerar dintr-o factură care depășește 5.000 lei și de ce restul nu poate fi fragmentat, conform Legii 70/2015."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se poate încasa în numerar o factură mai mare de 5.000 lei?

O factură de 8.000 lei emisă către o altă firmă nu trebuie neapărat încasată integral prin virament — dar nici integral în numerar. Legea permite o încasare parțială în numerar, până la plafon, cu restul obligatoriu prin instrument fără numerar.

## Temeiul legal

::: ghid-temei
„(2) Sunt interzise încasările fragmentate în numerar de la beneficiari pentru facturile a căror valoare este mai mare de 5.000 lei și, respectiv, de 10.000 lei, în cazul magazinelor de tipul cash and carry, precum și fragmentarea facturilor pentru o livrare de bunuri sau o prestare de servicii a căror valoare este mai mare de 5.000 lei, respectiv de 10.000 lei."
— Legea 70/2015, art. 3 alin. (2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Mecanismul, coroborat cu plafonul zilnic general de la art. 3 alin. (1) lit. a):

- **Da, se poate încasa în numerar dintr-o factură mai mare de 5.000 lei** — dar limita rămâne 5.000 lei în numerar (10.000 lei la cash and carry); diferența peste acest plafon **trebuie încasată exclusiv prin instrumente de plată fără numerar** (virament, card, etc.), exact ca la regula simetrică de la plăți (art. 3 alin. (3)).
- Ce e **interzis** e **fragmentarea**: încasarea repetată, în tranșe succesive de numerar, special pentru a ocoli plafonul pe o singură factură mare — legea sancționează exact această manevră, indiferent de câte zile se întind tranșele.
- O încasare unică de maximum 5.000 lei în numerar dintr-o factură mai mare, urmată de o singură încasare a diferenței prin virament, respectă legea; două sau mai multe încasări în numerar care, împreună, depășesc 5.000 lei pe aceeași factură, nu.

## Ce se greșește în practică

- Se refuză complet încasarea în numerar a unei facturi peste 5.000 lei, din exces de prudență, deși legea permite o încasare parțială până la plafon.
- Se încasează 5.000 lei numerar azi și încă o tranșă de numerar mâine, pe aceeași factură, crezând că "zile diferite" înseamnă "operațiuni diferite" — legea vizează exact această fragmentare, indiferent de datele calendaristice.
- Se confundă plafonul pe factură (art. 3 alin. (2), interdicție de fragmentare) cu plafonul zilnic pe persoană (art. 3 alin. (1) lit. a)) — cele două se aplică simultan, iar respectarea unuia nu garantează respectarea celuilalt.

## Ce face iConta.eu

La data acestui ghid, `core/casa.py` are constanta `PLAFON_INCASARE_PJ = Decimal("5000")` (10.000 lei pentru cash and carry), folosită de `verifica_plafon()` pentru a semnala orice încasare cumulată de la un partener persoană juridică ce depășește plafonul într-o zi. Verificarea agregă operațiunile pe zi și pe partener, coerent cu regula de interzicere a fragmentării de la art. 3 alin. (2), dar rămâne un avertisment de control — decizia de a încasa parțial numerar și restul prin virament aparține contabilului.

[iConta.eu](/)
