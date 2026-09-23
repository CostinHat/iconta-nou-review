---
title: Cum emit o factură de corecție în e-Factura
description: Corecția unei facturi în iConta.eu se face exclusiv prin stornare — un document nou, cu cantități negative, care copiază clasificarea fiscală a originalului; aplicația nu are o „factură de corecție" separată de acest mecanism.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum emit o factură de corecție în e-Factura

„Factură de corecție" nu e un tip distinct de document în circuitul contabil descris aici — mecanismul prin care se corectează o factură deja emisă e stornarea: un document nou, care anulează precis operațiunea inițială.

## Temeiul legal

::: ghid-temei
„69. — Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (**stornare în roșu**), fie prin înregistrarea inversă a acesteia (**stornare în negru**), în funcție de politica contabilă și programele informatice […]"

— OMFP 1802/2014, reglementări contabile consolidate, pct. 69
:::

De precizat un aspect terminologic: nomenclatorul oficial SAF-T al ANAF distinge mai multe coduri de tip de document pentru facturi — printre altele, codul 380 pentru factura inițială, 381 pentru „factură storno (factură cu semnul minus indiferent de motivul stornării)" și 384 pentru „factură corectată", ca tip distinct. Mecanismul verificat aici, cel pe care se bazează corecția facturilor, e stornarea (codul 381) — cantități negate, aceeași cotă, aceeași clasificare fiscală ca originalul. Dacă ai nevoie specific de tipul „factură corectată" (cod 384) pentru un scenariu particular, verifică separat dacă aplicația îl generează distinct — nu e ceva confirmat aici.

## Ce se greșește în practică

- Se caută în aplicație un tip separat de „factură de corecție", diferit de stornare — corecția standard, verificată aici, e stornarea.
- Se emite manual o factură nouă, independentă, cu semn pozitiv și descriere „corecție", în loc de o stornare cu cantități negative — o astfel de factură nu se raportează corect ca stornare în declarațiile care citesc facturile (D394, D406/SAF-T).

## Ce face iConta.eu

Butonul „Stornează" generează automat documentul de corecție: liniile facturii inițiale cu cantități negate, număr nou din aceeași serie, curs valutar și clasificare fiscală identice cu ale originalului. Documentul rezultat e marcat intern printr-o referință către factura corectată, iar în SAF-T (D406) e raportat automat cu codul oficial 381 „Notă de credit" — corespondentul confirmat pentru stornare.

[iConta.eu](/)
