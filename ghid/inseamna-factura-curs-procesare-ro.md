---
title: "Ce înseamnă factura în curs de procesare în RO e-Factura?"
description: Ce se întâmplă tehnic cu o factură emisă aflată "în prelucrare" la ANAF, când starea devine "investigație" și de ce pragul respectiv nu e un termen legal.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce înseamnă factura în curs de procesare în RO e-Factura?

O factură emisă, deja încărcată cu succes în SPV, intră într-o etapă de așteptare a verdictului ANAF — "în prelucrare". Este o stare intermediară, normală, nu o problemă: înseamnă doar că ANAF nu a răspuns încă definitiv.

## Temeiul legal

::: ghid-temei
"În situaţia în care factura electronică transmisă respectă structura prevăzută la alin. (1), se aplică semnătura electronică a Ministerului Finanţelor şi se comunică de îndată destinatarului. Aplicarea semnăturii electronice a Ministerului Finanţelor atestă primirea acesteia în sistemul naţional privind factura electronică RO e-Factura."
— OUG 120/2021, art. 4 alin. (4)
:::

Legea nu descrie explicit o stare intermediară de "procesare" — vorbește doar de rezultatul final (semnătura MF aplicată, care atestă primirea). Starea "în prelucrare" este modul în care sistemele care interoghează ANAF descriu perioada dintre încărcarea facturii și verdictul definitiv, pe baza răspunsului efectiv primit de la ANAF la interogarea stadiului.

Răspunsul ANAF poate indica, la interogare, că factura e încă "în prelucrare" — situație în care nu s-a luat încă o decizie finală. Dacă această stare persistă mai mult decât un anumit număr de zile, unele aplicații marchează factura într-un mod distinct ("investigație"), tocmai pentru a atrage atenția că a trecut mai mult timp decât de obicei fără un răspuns definitiv — nu pentru că legea ar impune un asemenea termen.

## Ce se greșește în practică

- Se interpretează starea "în prelucrare" ca fiind deja o problemă sau o respingere implicită. Nu este — înseamnă doar că ANAF nu a transmis încă un verdict.
- Se presupune că există un termen legal după care ANAF trebuie să dea un răspuns definitiv la o factură aflată în prelucrare. Nu există, în sursele legale verificate, un asemenea termen documentat.
- Se ignoră starea "investigație" (marcată după depășirea unui prag de zile) și factura e lăsată nesupravegheată la nesfârșit, deși acest marcaj e tocmai semnalul că merită verificare manuală suplimentară.

## Ce face iConta.eu

iConta.eu interoghează automat, la fiecare 30 de minute, stadiul fiecărei facturi emise aflate în așteptarea unui verdict de la ANAF. Cât timp răspunsul ANAF indică "în prelucrare", factura rămâne în această stare în evidența internă. Dacă starea "în prelucrare" persistă peste un prag intern de zile (implicit 2 zile), aplicația marchează factura ca "investigație" — un semnal vizual distinct, pentru a atrage atenția că a trecut mai mult decât de obicei fără un verdict și că merită verificare manuală direct în SPV.

Trebuie spus onest: acest prag de 2 zile este o valoare conservatoare, stabilită intern de iConta.eu, nu un termen legal sau un angajament de timp al ANAF — ANAF nu documentează public durata procesării. Pragul poate fi ajustat ca setare tehnică, dar nu reprezintă și nu trebuie interpretat ca o garanție legală de răspuns în acel interval.

[iConta.eu](/)
