---
title: "Cum contabilizez diferența dintre cursul băncii și cursul BNR?"
description: Când o operațiune valutară se decontează la un curs diferit de cel folosit inițial în contabilitate (cursul BNR de evidență), diferența — favorabilă sau nefavorabilă — se recunoaște ca venit sau cheltuială din curs valutar, în luna în care apare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum contabilizez diferența dintre cursul băncii și cursul BNR?

Contabilitatea unei creanțe sau datorii în valută se ține la cursul BNR — dar decontarea efectivă (încasarea sau plata prin bancă) se face de multe ori la un curs diferit, fie pentru că banca aplică propriul curs comercial de schimb, fie pentru că timpul scurs între înregistrare și decontare a schimbat cursul BNR. Diferența dintre cele două nu se ignoră — se înregistrează explicit, ca rezultat financiar.

## Temeiul legal

::: ghid-temei
„Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate inițial pe parcursul lunii sau față de cele la care sunt înregistrate în contabilitate trebuie recunoscute în luna în care apar, ca venituri sau cheltuieli din diferențe de curs valutar." — OMFP 1802/2014 (Reglementările contabile), pct. 322 alin. (1).
:::

## Mecanismul de contabilizare

La decontarea unei creanțe (încasare de la client) sau a unei datorii (plată către furnizor) în valută:

- se compară cursul la care a fost înregistrată inițial suma (curs BNR de evidență, la data facturii sau a ultimei reevaluări) cu cursul la care are loc efectiv decontarea;
- dacă decontarea se face la cursul BNR curent (nu la un curs comercial diferit), diferența e pur o diferență de curs BNR între cele două date;
- dacă banca aplică propriul curs de schimb (de exemplu, pentru o plată din contul în valută sau o încasare convertită automat), diferența dintre suma contabilizată la cursul BNR de evidență și suma efectiv mișcată în bancă se recunoaște tot ca diferență de curs — favorabilă (cont 765), dacă rezultă un câștig, sau nefavorabilă (cont 665), dacă rezultă o pierdere.

Regula de semn: la o creanță sau la disponibilul din cont, o creștere a cursului generează câștig (765); la o datorie, o creștere a cursului generează pierdere (665) — și invers, pentru scăderea cursului.

## Ce se greșește în practică

- Se contabilizează decontarea direct la suma primită/plătită efectiv, fără să se compare cu valoarea inițială la cursul de evidență — diferența de curs rămâne „ascunsă", nerecunoscută separat.
- Se inversează sensul diferenței (se înregistrează cheltuială în loc de venit sau invers) — sensul depinde de tipul elementului (creanță/disponibil vs. datorie), nu doar de direcția mișcării cursului.
- Se amână recunoașterea diferenței pentru o lună ulterioară, deși regula (pct. 322) cere recunoașterea ei în luna în care apare decontarea.

## Ce face iConta.eu

`core/diferente_curs.py` calculează automat diferența de curs la decontarea unei creanțe sau datorii în valută, pe baza cursului de evidență și a cursului de decontare introduse, și determină automat sensul (765 câștig / 665 pierdere) în funcție de tipul elementului (creanță, disponibil sau datorie) — motorul e strict de calcul, cursurile efective (de evidență și de decontare) se introduc pentru fiecare operațiune, aplicația nu presupune un curs implicit pentru niciunul dintre ele.

[iConta.eu](/)
