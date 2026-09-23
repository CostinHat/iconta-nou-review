---
title: Cum corectez o factură înregistrată greșit în contabilitate?
description: iConta.eu nu are funcție de editare a unei facturi deja introduse. Corecția depinde de starea ei — fără notă contabilă, factura se șterge și se reintroduce corect; cu notă contabilă, corecția se face exclusiv prin stornare (document nou, cu sens opus) plus o factură nouă, corectă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez o factură înregistrată greșit în contabilitate?

Nu există, în iConta.eu, un buton „editează factura" pentru o factură deja introdusă — indiferent dacă greșeala e la furnizor, client, dată sau valoare. Ce se poate face depinde de un singur lucru: dacă factura are sau nu o notă contabilă asociată (adică dacă a fost deja contabilizată).

## Temeiul legal

::: ghid-temei
„În cazul completării documentelor prin utilizarea sistemelor informatice de prelucrare automată a datelor, corecturile sunt admise numai înainte de prelucrarea acestora. Documentele prezentate în listele de erori, anulări sau completări [...] trebuie să fie semnate de persoanele împuternicite de conducerea entității." — OMFP 2634/2015, pct. 16

„Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (stornare în roșu), fie prin înregistrarea inversă a acesteia (stornare în negru), în funcție de politica contabilă și programele informatice utilizate." — OMFP 1802/2014, Anexa 1 – Reglementări contabile, pct. 69
:::

„Prelucrarea" documentului electronic e, în fluxul iConta.eu, momentul în care factura primește o notă contabilă (contarea ei). Până atunci, orice corecție e liberă; după, singura cale prevăzută e stornarea.

## Cum corectez, în funcție de stare

- **Factura nu are notă contabilă** (nu a fost încă contată) → se șterge direct și se reintroduce corect, cu datele bune. Ștergerea e permisă necondiționat cât timp nu există o notă de contare legată.
- **Factura are notă contabilă** (a fost deja contabilizată) → ștergerea e refuzată explicit, cu mesajul din aplicație: „Factura are notă contabilă (#…) și nu se mai șterge: o notă ștearsă lasă o gaură în evidență. Corecția unei facturi contabilizate se face prin STORNO — un al doilea document, care își produce propria notă." Corecția se face prin stornare: se emite o factură de stornare (număr nou, din aceeași serie, cu liniile din original negate, legată de original prin `storno_din_id`), apoi se introduce factura nouă, corectă, cu propria notă contabilă.
- Stornarea automată din facturi (buton dedicat) e verificată în cod pentru **facturile emise** — funcția refuză explicit dacă factura nu e emisă. Pentru o factură primită deja contabilizată, corecția urmează același principiu contabil (stornare în roșu/negru, pct. 69), dar prin nota contabilă, nu prin acest buton specific facturilor emise.
- Dacă luna facturii sau a notei e închisă administrativ, nicio operație (ștergere, stornare, notă nouă) nu se poate face pe acea lună — aplicația refuză cu mesajul „Perioada e blocată (luna închisă). Cere-i administratorului cabinetului să o redeschidă sau înregistrează în luna curentă."

## Ce se greșește în practică

- Se caută un buton de editare pe o factură deja introdusă — nu există, indiferent de câmpul greșit.
- Se încearcă ștergerea unei facturi deja contate, ca să „dispară" greșeala — aplicația refuză, tocmai ca să nu rămână o notă contabilă fără document.
- Se stornează factura, dar nu se introduce și factura nouă, corectă — rămâne doar anularea, fără înlocuire, și evidența economică a operațiunii reale lipsește.

## Ce face iConta.eu

Aplicația nu permite modificarea unei facturi deja introduse. Cât nu are notă contabilă, o factură greșită se șterge și se reintroduce corect. Odată contabilizată, singura cale e stornarea — un document nou, cu efect opus, urmat de factura corectă — exact mecanismul de „stornare în roșu/negru" din pct. 69 al reglementărilor contabile. Perioada contabilă închisă blochează toate aceste operații deopotrivă.

[iConta.eu](/)
