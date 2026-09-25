---
title: "Producția în curs: evaluare și reprezentare 2026"
description: "Cum se evaluează producția în curs de execuție la cost de producție stabilit prin inventar și unde apare ea în bilanț."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Producția în curs: evaluare și reprezentare 2026

Producția în curs de execuție este stocul de produse care, la finalul unei perioade, nu au parcurs încă toate fazele procesului tehnologic. Ea se evaluează la cost de producție, stabilit pe bază de inventar, și apare distinct în bilanț, separat de produsele finite. Mai jos sunt regulile exacte, cu textul de lege.

## Temeiul legal

::: ghid-temei
„Contul 331 „Produse în curs de execuție" Cu ajutorul acestui cont se ține evidența stocurilor de produse în curs de execuție (care nu au trecut prin toate fazele de prelucrare prevăzute de procesul tehnologic, respectiv producția neterminată) existente la sfârșitul perioadei. Contul 331 „Produse în curs de execuție" este un cont de activ. În debitul contului 331 [...] se înregistrează: – valoarea la cost de producție a stocului de produse în curs de execuție la sfârșitul perioadei, stabilită pe bază de inventar (711). [...] În creditul contului 331 [...] se înregistrează: – scăderea din gestiune a valorii produselor în curs de execuție la începutul perioadei următoare (711). [...] Soldul contului reprezintă valoarea la cost de producție a produselor aflate în curs de execuție la sfârșitul perioadei."
— OMFP 1802/2014, Reglementările contabile, Cap. 16, funcțiunea contului 331 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Din text rezultă un mecanism clar, în doi timpi:

- **Evaluarea** se face la **cost de producție**, nu la o estimare arbitrară, și se stabilește obligatoriu **pe bază de inventar** la sfârșitul perioadei (lunii).
- **Constatarea** la închiderea perioadei se înregistrează în debitul contului 331, prin creditul contului 711 „Venituri aferente costurilor stocurilor de produse".
- **Reluarea**, la începutul perioadei următoare, se face invers: se scade din gestiune valoarea constatată anterior, prin creditul lui 331 și debitul lui 711.
- **Reprezentarea în bilanț** e distinctă de cea a produselor finite: formatul de bilanț de la pct. 132 din OMFP 1802/2014 listează, la „B. Active circulante I. Stocuri", separat „1. Materii prime și materiale consumabile", „2. Producția în curs de execuție" și „3. Produse finite și mărfuri" — trei poziții distincte, nu una singură.

## Ce se greșește în practică

- Se omite complet înregistrarea producției în curs la închiderea lunii, pentru că „oricum se reia luna viitoare" — dar fără constatare, bilanțul de lună subevaluează activele circulante.
- Se estimează valoarea „din ochi", fără un inventar efectiv la sfârșit de perioadă — legea cere explicit stabilirea pe bază de inventar.
- Se contopește producția în curs cu produsele finite într-o singură cifră în bilanț, deși pct. 132 le cere ca poziții separate.
- Se uită reluarea la începutul lunii următoare, ceea ce dublează valoarea producției în curs în perioada respectivă.

## Ce face iConta.eu

Din ecranul **Operațiuni speciale → Imobilizări**, operațiunea „Producție (711/345)" permite introducerea directă a sumei constatate la inventar pentru producția în curs, cu alegerea momentului — „constatare" (generează automat nota 331 = 711) sau „reluare" (generează automat nota 711 = 331), suma fiind introdusă manual de contabil pe baza inventarului. Motorul de calcul este pur (bazat pe `Decimal`, fără input incorect acceptat: o sumă invalidă e respinsă explicit) și acoperit de teste unitare. Notă onestă: iConta.eu **nu automatizează inventarierea** propriu-zisă a producției în curs — aplicația generează corect nota contabilă pe baza sumei pe care contabilul o introduce, dar stabilirea acelei sume, prin inventar fizic sau tehnic, rămâne un proces din afara aplicației.

[iConta.eu](/)
