---
title: "Cum verific ce facturi emise nu au fost încă trimise în SPV?"
description: "Legea impune un termen fix de 5 zile lucrătoare pentru transmiterea facturilor emise în RO e-Factura, termen util ca reper pentru orice verificare a facturilor netrimise."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific ce facturi emise nu au fost încă trimise în SPV?

Emiterea unei facturi și transmiterea ei efectivă în sistemul RO e-Factura (SPV) sunt doi pași distincți, iar între ei există un termen legal strict. O factură emisă dar netrimisă la timp expune firma la o contravenție, așa că verificarea periodică a „coșului" de facturi netransmise e o rutină de igienă contabilă, nu un moft.

## Temeiul legal

::: ghid-temei
„Termenul-limită pentru transmiterea facturilor în sistemul național privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită pentru emiterea facturii prevăzută la art. 319 alin. (16) din Legea nr. 227/2015, cu modificările și completările ulterioare. Calculul termenului-limită se efectuează conform Regulamentului (CEE, Euratom) nr. 1182/71 al Consiliului din 3 iunie 1971 privind stabilirea regulilor care se aplică termenelor, datelor și expirării termenelor."
— OUG 120/2021, art. 10 alin. (7) (text modificat prin OUG 89/2025, art. X pct. 2) (sursă: anaf_surse/oug_89_2025.txt)
:::

- Termenul curge de la **data emiterii facturii**, nu de la data prestației/livrării, și se numără în **zile lucrătoare**, nu calendaristice.
- Există și o limită absolută: transmiterea nu poate depăși 5 zile lucrătoare de la data-limită legală de emitere a facturii (a 15-a zi a lunii următoare celei în care ia naștere faptul generator, potrivit art. 319 alin. (16) din Codul fiscal) — deci termenul nu poate fi „împins" la infinit doar pentru că factura însăși a fost emisă târziu.
- O verificare corectă a facturilor „nedecontate" în SPV presupune compararea, pentru fiecare factură emisă, a datei emiterii cu data confirmată de transmitere/validare în sistem, semnalând orice factură care depășește pragul de 5 zile lucrătoare fără status de transmitere.

## Ce se greșește în practică

- Se numără termenul în zile calendaristice, nu lucrătoare, ceea ce duce fie la panică nejustificată, fie la depășiri reale nesesizate la timp.
- Se presupune că o factură „arătată" clientului sau trimisă pe e-mail echivalează cu transmiterea legală în RO e-Factura — cele două nu sunt același lucru.
- Se ignoră erorile de validare: o factură respinsă de sistem pentru neconformități de structură rămâne, de fapt, netransmisă până la corectare și retransmitere, chiar dacă a fost „încărcată" o dată.

## Ce face iConta.eu

Dosarul de cercetare care stă la baza acestui ghid documentează în detaliu o singură funcționalitate legată de exportul facturilor emise — F171, exportul XML către programul de contabilitate SAGA, complet separat de sistemul RO e-Factura/SPV. Aplicația are, potrivit acestui dosar, și un modul distinct pentru transmiterea facturilor către e-Factura (`core/efactura_send.py`), dar acest dosar nu a verificat dacă și cum oferă acel modul o listă sau un raport al facturilor emise încă netransmise în SPV. Nu facem, așadar, nicio afirmație despre existența unei astfel de funcții de verificare în iConta.eu, pentru a nu inventa un comportament neconfirmat în cod.

[iConta.eu](/)
