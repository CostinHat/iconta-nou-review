---
title: "Termenul de transmitere a facturii în e-Factura"
description: "Termenul legal actual de 5 zile lucrătoare pentru transmiterea facturilor prin RO e-Factura, cu modul de calcul conform regulamentului european."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Termenul de transmitere a facturii în e-Factura

Termenul de transmitere prin RO e-Factura s-a schimbat în timp — de la 5 zile calendaristice, la 5 zile lucrătoare. Confuzia dintre cele două variante este una dintre cele mai frecvente greșeli, mai ales pentru cine a reținut regula veche.

## Temeiul legal

::: ghid-temei
„Termenul-limită pentru transmiterea facturilor în sistemul naţional privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită pentru emiterea facturii prevăzută la art. 319 alin. (16) din Legea nr. 227/2015, cu modificările şi completările ulterioare. Calculul termenului-limită se efectuează conform Regulamentului (CEE, Euratom) nr. 1182/71 al Consiliului din 3 iunie 1971 privind stabilirea regulilor care se aplică termenelor, datelor şi expirării termenelor."
— OUG nr. 120/2021, art. 10 alin. (7) și art. 10^1 alin. (2^1), astfel cum au fost modificate prin OUG nr. 89/2025 (sursă: anaf_surse/oug_89_2025.txt)
:::

Regula are, de fapt, două componente care trebuie citite împreună:

- **5 zile lucrătoare de la data emiterii** facturii — nu de la data prestării serviciului sau a livrării bunului, ci de la data la care factura a fost efectiv emisă.
- **Nu mai târziu de 5 zile lucrătoare de la data-limită legală de emitere** a facturii (art. 319 alin. (16) Cod fiscal) — a doua limită, care intervine mai ales atunci când factura este emisă cu întârziere față de termenul legal de emitere.
- Calculul zilelor lucrătoare se face conform Regulamentului (CEE, Euratom) nr. 1182/71 — adică se exclud zilele de sâmbătă, duminică și sărbătorile legale, spre deosebire de vechea regulă de 5 zile calendaristice, în vigoare înainte de OUG 89/2025, care nu excludea aceste zile.
- Regula se aplică identic în relația B2B (art. 10 alin. (7)) și în relația B2C (art. 10^1 alin. (2^1)) — nu există un termen diferit pentru cele două tipuri de relații.

## Ce se greșește în practică

- Se calculează termenul în zile calendaristice, conform regulii vechi, ceea ce poate duce la depășirea reală a termenului actual de 5 zile lucrătoare, mai ales în preajma unui weekend prelungit.
- Se ignoră a doua limită a termenului (legată de data-limită de emitere), presupunând că singurul reper este data efectivă a emiterii facturii.
- Se confundă termenul de transmitere cu termenul de emitere a facturii — sunt două termene distincte, primul curgând de la momentul emiterii, nu invers.

## Ce face iConta.eu

iConta.eu transmite facturile prin RO e-Factura la inițiativa utilizatorului sau prin sincronizarea programată a facturilor recurente, folosind `core/efactura_send.py`. Aplicația nu afișează, la acest moment, un contor vizibil al termenului legal rămas pentru fiecare factură netransmisă — respectarea termenului de 5 zile lucrătoare rămâne în responsabilitatea utilizatorului, care vede însă starea fiecărei trimiteri (în așteptare, acceptată, respinsă) urmărită automat de `core/spv_poll.py`.

[iConta.eu](/)
