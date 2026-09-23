---
title: Cum verific data fiscală corectă a trecerii de la micro la profit?
description: Data corectă e prima zi a trimestrului în care veniturile cumulate de la 1 ianuarie au depășit 100.000 euro — nu un calcul automat, ci o verificare manuală a veniturilor.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific data fiscală corectă a trecerii de la micro la profit?

„Data trecerii" nu e o dată aleasă de contabil, ci rezultatul unui calcul strict: momentul din care veniturile cumulate ale firmei, de la începutul anului fiscal, au trecut pragul de 100.000 euro.

## Temeiul legal

::: ghid-temei
**Art. 52 alin. (1) CF**: „Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit **începând cu trimestrul în care s-a depășit această limită**." Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, linia 6414.

**Art. 47 alin. (1) lit. c) CF**: „a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile." Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, linia 6095.
:::

Calculul e cumulativ, de la 1 ianuarie: aduni veniturile firmei (conturile 70x, la data facturării, nu a încasării) trimestru după trimestru, și compari totalul cu echivalentul în lei a 100.000 euro. Data exactă a trecerii la profit e prima zi a trimestrului calendaristic în care acest total a depășit pragul — nu ziua exactă a depășirii în interiorul trimestrului, ci întregul trimestru respectiv.

Cursul de schimb de referință pentru echivalentul în lei nu e cel valabil la momentul depășirii, ci cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile — de obicei cursul BNR din 31 decembrie, pentru firmele cu an fiscal calendaristic.

Odată identificat trimestrul, data de aplicare a regimului „profit" în Vectorul fiscal trebuie setată la prima zi a acelui trimestru, nu la data la care faci efectiv corectarea în aplicație.

## Ce se greșește în practică

- Se folosește cursul de schimb de la data depășirii plafonului, în loc de cursul valabil la închiderea exercițiului financiar.
- Se setează data trecerii la profit ca fiind data efectivă a corectării în aplicație, nu prima zi a trimestrului în care s-a produs depășirea reală.
- Se calculează veniturile cumulate pe bază de încasări, nu pe bază de facturare (venituri contabile), ceea ce poate decala artificial momentul depășirii.

## Ce face iConta.eu

iConta nu calculează automat momentul depășirii plafonului micro — nu există nicio constantă de plafon (100.000 €) în motorul de calcul (`core/control_fiscal_api.py`), confirmat explicit prin comentariul de cod și prin căutare directă în sursă. Determinarea trimestrului corect rămâne un calcul manual al contabilului, pe baza rulajelor conturilor de venituri; aplicația doar reține data introdusă la salvarea Vectorului fiscal, fără s-o valideze împotriva pragului legal.

[iConta.eu](/)
