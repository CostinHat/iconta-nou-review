---
title: Cum corectez o factură înregistrată cu valoarea greșită?
description: O valoare greșită pe o factură deja introdusă nu se editează în iConta.eu. Fără notă contabilă, se șterge și se reintroduce cu suma corectă. Cu notă contabilă, corecția e exclusiv prin stornare — factura originală se anulează cu sumă negativă, apoi se introduce factura corectă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez o factură înregistrată cu valoarea greșită?

O sumă greșită pe o factură deja contabilizată nu e o cifră care se „rescrie" — pentru că schimbă efectiv operațiunea economică raportată. Ca la orice altă corecție de factură, nu există un câmp de valoare editabil pe un document deja introdus.

## Temeiul legal

::: ghid-temei
„Persoanele prevăzute la art. 1 alin. (1)-(4) au obligația să conducă contabilitatea în partidă dublă și să întocmească situații financiare anuale, potrivit reglementărilor contabile aplicabile." — Legea contabilității nr. 82/1991, art. 5 alin. (1)

„Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (stornare în roșu), fie prin înregistrarea inversă a acesteia (stornare în negru), în funcție de politica contabilă și programele informatice utilizate." — OMFP 1802/2014, Anexa 1 – Reglementări contabile, pct. 69
:::

Partida dublă cere ca fiecare sumă înregistrată să corespundă exact operațiunii reale — o valoare greșită dezechilibrează raportarea, indiferent de mărimea diferenței, de aceea corectarea ei nu poate fi o simplă suprascriere.

## Cum corectez în iConta.eu

- **Factura nu are încă notă contabilă** → se șterge și se reintroduce cu suma corectă.
- **Factura are notă contabilă** (a fost deja contată cu suma greșită) → ștergerea e refuzată explicit („Corecția unei facturi contabilizate se face prin STORNO"). Pentru facturile emise, `storneaza()` creează o factură nouă cu liniile din original **negate** (deci exact valoarea greșită, cu semn opus), legată de original, apoi se introduce factura nouă, cu suma corectă.
- Efectul net contabil e: suma greșită + suma stornată (negativă) = zero, plus suma corectă din factura nouă — exact mecanismul „stornării în roșu" din pct. 69, aplicat la nivel de document.
- Dacă doar nota contabilă are suma greșită (nu și factura), iar nota e încă ciornă, aceasta se poate corecta direct — `jurnal_api.editeaza` acceptă modificarea sumelor pe liniile unei note doar cât timp e ciornă; nota validează linii cu sumă strict pozitivă, deci suma corectă trebuie introdusă corect pe fiecare linie de debit/credit.
- Odată validată nota, aceeași regulă se aplică: nu există editare, doar o notă nouă de stornare.

## Ce se greșește în practică

- Se editează suma direct pe factură sau pe o notă deja validată, așteptând ca aplicația să permită — funcția refuză explicit orice modificare pe o notă/factură deja fixată în evidență.
- Se stornează doar parțial diferența (de exemplu se introduce o notă manuală cu diferența, fără să se treacă prin stornarea documentului) — riscul e ca legătura cu factura originală (`storno_din_id`) să se piardă, iar urmărirea corecției să devină greoaie.
- Se uită introducerea facturii corecte după stornare — rezultă doar anularea sumei greșite, fără înregistrarea operațiunii reale.

## Ce face iConta.eu

O sumă greșită pe o factură deja introdusă nu se editează. Fără notă contabilă, factura se șterge și se reintroduce cu valoarea corectă. Cu notă contabilă, corecția e exclusiv prin stornare: o factură nouă, cu liniile negate exact ca în original, legată de document prin identificator, urmată de factura corectă. Pentru o notă manuală neconfirmată încă (ciornă), suma se poate corecta direct pe linii, cu condiția ca fiecare sumă introdusă să rămână strict pozitivă.

[iConta.eu](/)
