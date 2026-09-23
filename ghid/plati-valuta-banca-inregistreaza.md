---
title: "Plăți în valută prin bancă: cum se înregistrează"
description: O plată prin bancă în valută se înregistrează inițial la cursul BNR din data operațiunii, în contul de disponibil în valută (5124), iar orice diferență între suma contabilizată la evidență și suma efectiv plătită se recunoaște separat, ca diferență de curs.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Plăți în valută prin bancă: cum se înregistrează

O plată efectuată din contul bancar în valută al firmei — către un furnizor, pentru o factură în EUR, USD sau altă monedă — urmează aceeași regulă generală ca orice tranzacție în valută: se înregistrează la cursul BNR valabil la data operațiunii, iar contul de bancă folosit e distinct de cel în lei.

## Temeiul legal

::: ghid-temei
„O tranzacție în valută trebuie înregistrată inițial la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii." — OMFP 1802/2014 (Reglementările contabile), pct. 319.
:::

## Contul folosit și cursul aplicat

Disponibilul bancar în valută se ține în contul **5124** (distinct de 5121, pentru lei). La o plată efectuată din acest cont, suma se contabilizează la cursul BNR din data plății — care poate diferi de cursul folosit la înregistrarea inițială a datoriei către furnizor (de la data facturii). Diferența dintre valoarea datoriei la cursul de evidență și valoarea efectiv plătită la cursul din ziua plății se recunoaște ca diferență de curs (venit pe 765, dacă a scăzut cursul, sau cheltuială pe 665, dacă a crescut), în luna în care are loc plata.

Dacă banca aplică propriul curs comercial pentru conversia sumei (de exemplu, plată efectuată dintr-un cont în lei către un furnizor facturat în valută, cu schimb valutar automat), aceeași logică se aplică: suma contabilizată la cursul BNR de evidență se compară cu suma efectiv ieșită din cont, iar diferența intră tot pe 665/765.

## Ce se greșește în practică

- Se contabilizează plata direct la suma din extrasul bancar, fără compararea cu valoarea inițială a datoriei la cursul de evidență — diferența de curs rămâne neînregistrată separat.
- Se folosește contul 5121 (lei) pentru o plată efectuată din contul în valută, amestecând evidența — contul de bancă folosit trebuie să corespundă monedei reale a operațiunii (5124 pentru valută).
- Se aplică, pentru contabilizarea plății, cursul de la data facturii inițiale în loc de cursul BNR din data plății efective — cele două date pot să difere, iar diferența de curs rezultată din acest interval trebuie recunoscută.

## Ce face iConta.eu

Cursul BNR folosit pentru evaluarea în lei a operațiunilor în valută provine din motorul de curs (`core/curs_bnr.py`), care preia ultimul curs BNR comunicat, valabil la data operațiunii — fără fallback tăcut la o cotă implicită dacă cursul nu poate fi determinat. Diferența de curs dintre valoarea de evidență a datoriei și suma efectiv plătită se calculează separat, prin motorul de diferențe de curs (`core/diferente_curs.py`), pe baza cursurilor introduse pentru fiecare operațiune.

[iConta.eu](/)
