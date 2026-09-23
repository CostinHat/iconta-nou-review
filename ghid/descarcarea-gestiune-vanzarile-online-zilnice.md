---
title: "Descărcarea de gestiune pentru vânzările online zilnice"
description: Nu există o agregare automată, o dată pe zi, a vânzărilor online — fiecare factură emisă prin integrare descarcă individual gestiunea, în momentul emiterii ei.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Descărcarea de gestiune pentru vânzările online zilnice

Pentru un magazin online cu volum mare de comenzi zilnice, e firesc să se caute un mecanism de descărcare "pe lot", o dată pe zi. La acest moment, un asemenea mecanism nu există în aplicație: fiecare factură emisă prin integrare, dacă are marfă din stoc, trece individual prin aceeași poartă ca oricare altă factură — răspunsul afirmativ descarcă gestiunea în chiar momentul emiterii facturii respective, nu la o rulare de sfârșit de zi.

## Temeiul legal

::: ghid-temei
"441. - (1) Veniturile din vânzarea bunurilor se recunosc în momentul în care sunt îndeplinite următoarele condiții: a) entitatea a transferat cumpărătorului riscurile şi avantajele semnificative care decurg din proprietatea asupra bunurilor;"
— OMFP 1802/2014, pct. 441 alin. (1)
:::

Recunoașterea vânzării e legată de fiecare tranzacție în parte, la momentul transferului riscurilor și avantajelor — nu de o agregare artificială pe zi. De aici și tratarea individuală, per factură, a fiecărei descărcări.

## Ce se greșește în practică

- Se așteaptă un "raport Z" sau o rulare de închidere de zi care să descarce gestiunea pentru toate vânzările online ale zilei dintr-o dată — un asemenea mecanism nu există pentru vânzările online facturate prin API; raportul Z din aplicație privește exclusiv casele de marcat (HoReCa, AMEF), nu descărcarea gestiunii.
- Se emit facturile fără să se răspundă la poartă, în ideea că "se rezolvă oricum la agregarea de seară" — fără răspunsul explicit la poartă, la o factură cu marfă din stoc, cererea de emitere e respinsă, indiferent de volum.
- Se presupune că, la volum mare, e mai eficient să se dezactiveze poarta pentru vânzările online — poarta rămâne obligatorie la fiecare factură cu marfă din stoc, indiferent de câte facturi se emit pe zi; nu există un mod "agregat" care s-o ocolească.

## Ce face iConta.eu

Pentru fiecare factură emisă prin integrare (magazin online, comenzi automate), dacă firma are gestiune cantitativ-valorică și factura conține linii legate de articole de stoc, aplicația cere explicit, la fiecare factură în parte, dacă marfa pleacă odată cu ea. La răspuns afirmativ, gestiunea se descarcă imediat, în aceeași operațiune cu emiterea acelei facturi — nu există o coadă sau o agregare care să amâne descărcarea până la o rulare ulterioară.

Menționăm onest: dacă un integrator dorește să trateze vânzările zilei ca un singur lot (de exemplu, o singură factură recapitulativă la finalul zilei, în locul uneia per comandă), acest lucru e o decizie de business a integratorului, tratată la nivelul modului în care emite facturile — aplicația nu are, ea însăși, un job automat care agregă și descarcă gestiunea o singură dată pe zi pentru vânzările online.

[iConta.eu](/)
