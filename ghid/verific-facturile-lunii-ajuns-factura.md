---
title: "Cum verific dacă toate facturile lunii au ajuns în e-Factura?"
description: "Termenul legal de transmitere a facturilor în RO e-Factura și de ce verificarea lunară a stării fiecărei facturi transmise nu e opțională."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific dacă toate facturile lunii au ajuns în e-Factura?

O factură emisă nu e „gata" din perspectiva RO e-Factura decât atunci când sistemul a confirmat primirea și validarea ei — trimiterea nereușită sau respinsă rămâne, legal, o factură netransmisă, cu risc de sancțiune.

## Temeiul legal

::: ghid-temei
„(6) Termenul-limită pentru transmiterea facturilor prevăzute la alin. (1)-(3) în sistemul național privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită prevăzută pentru emiterea facturii la art. 319 alin. (16) din Legea nr. 227/2015, cu modificările și completările ulterioare.
(7) Nerespectarea prevederilor alin. (6) pentru una sau mai multe facturi al căror termen-limită de transmitere în sistemul național privind factura electronică RO e-Factura intervine în cursul unei luni calendaristice constituie contravenție și se sancționează cu amendă [...]"
— Legea 296/2023 (măsuri fiscal-bugetare), art. LIX, secțiunea a 2-a, cap. IV, alin. (6)-(7) (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

Ce înseamnă asta pentru verificarea de sfârșit de lună:

- **Sancțiunea se aplică pe factură**, nu pe firmă în ansamblu — alin. (7) vorbește explicit despre „una sau mai multe facturi" al căror termen a expirat într-o lună calendaristică. O singură factură ratată e deja o contravenție distinctă.
- **Termenul curge din două puncte diferite**: 5 zile lucrătoare de la emitere, dar nu mai târziu de 5 zile lucrătoare de la data-limită legală de emitere a facturii (art. 319 alin. 16 CF) — deci o factură emisă cu întârziere nu „câștigă" termen suplimentar pentru transmitere.
- **Verificarea propriu-zisă** înseamnă compararea a două liste: facturile emise în luna respectivă (din evidența contabilă/facturare) și mesajele de confirmare primite din sistemul RO e-Factura pentru fiecare dintre ele — o factură fără mesaj de confirmare, sau cu mesaj de eroare, nu e considerată transmisă.
- O factură **respinsă** de sistem (eroare de validare) și retrimisă ulterior corect rămâne supusă aceluiași termen de 5 zile de la emiterea inițială — corectarea nu prelungește termenul legal.

## Ce se greșește în practică

- Se verifică doar dacă factura a fost „încărcată" în sistem, fără să se urmărească și starea finală a validării — o încărcare urmată de respingere nu îndeplinește obligația de transmitere.
- Se face verificarea lunii o singură dată, la finalul lunii, fără reconciliere intermediară — dacă apar erori de validare, corectarea și retrimiterea în cadrul termenului de 5 zile devin imposibile dacă problema e descoperită prea târziu.
- Se presupune că toate facturile emise printr-un singur sistem de facturare ajung automat validate în RO e-Factura, fără verificare — o eroare tehnică de transmitere (conexiune, format XML) poate lăsa facturi „blocate" fără ca emitentul să observe.

## Ce face iConta.eu

Modulul e-Factura din iConta.eu (`core/repo_efactura.py`) ține evidența stării fiecărei transmiteri, cu funcția `ultima_trimitere_per_factura`, care întoarce, pentru fiecare factură din evidență, starea ultimei încercări de transmitere (reușită, în curs sau eroare) — exact mecanismul necesar pentru a compara facturile emise într-o lună cu cele efectiv confirmate de sistemul ANAF. Contabilul folosește acest raport pentru a identifica rapid facturile fără confirmare și a le retrimite în termenul legal de 5 zile lucrătoare.

[iConta.eu](/)
