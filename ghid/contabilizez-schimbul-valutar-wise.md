---
title: "Cum contabilizez schimbul valutar făcut în Wise?"
description: "Cum se înregistrează un schimb valutar făcut printr-un cont Wise, cu diferența de curs recunoscută ca venit sau cheltuială financiară, și de unde ia iConta.eu cursul BNR de referință."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum contabilizez schimbul valutar făcut în Wise?

Un schimb valutar făcut printr-un cont Wise (de exemplu conversia unor euro încasați de la un client extern în lei, sau invers) nu e o operațiune fiscală specială doar pentru că trece printr-un fintech, nu printr-o bancă tradițională — regulile de contabilizare sunt cele generale pentru operațiuni în valută din OMFP 1802/2014. Elementul de urmărit e diferența dintre cursul la care suma era deja înregistrată în contabilitate și cursul efectiv al conversiei.

## Temeiul legal

::: ghid-temei
„O tranzacție în valută trebuie înregistrată inițial la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii."
— OMFP 1802/2014, pct. 319 (sursă: anaf_surse/omfp_1802_2014.txt)
:::

Diferența care apare la momentul conversiei efective se tratează astfel:

::: ghid-temei
„(1) Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate inițial pe parcursul lunii sau față de cele la care sunt înregistrate în contabilitate trebuie recunoscute în luna în care apar, ca venituri sau cheltuieli din diferențe de curs valutar."
— OMFP 1802/2014, pct. 322 alin. (1) (sursă: anaf_surse/omfp_1802_2014.txt)
:::

Mecanic, un schimb valutar (de exemplu conversia soldului unui cont în valută, 5124, în lei, 5121, sau invers) se înregistrează astfel:

- suma convertită iese din contul sursă la valoarea ei contabilă curentă (cursul BNR la care era deja înregistrată, sau cursul zilei operațiunii anterioare);
- suma rezultată intră în contul destinație la valoarea efectiv primită (cursul real obținut la conversie, care poate diferi de cursul BNR al zilei);
- diferența dintre cele două se înregistrează la venituri (765 „Venituri din diferențe de curs valutar") dacă e favorabilă, sau la cheltuieli (665 „Cheltuieli din diferențe de curs valutar") dacă e nefavorabilă — indiferent de platforma prin care s-a făcut conversia (bancă tradițională sau fintech precum Wise).

## Ce se greșește în practică

- Se înregistrează suma rezultată din schimb direct la cursul BNR al zilei, ignorând cursul efectiv de conversie oferit de platformă — diferența reală dintre cursul de piață/platformă și cursul BNR e exact ceea ce trebuie recunoscut ca venit sau cheltuială financiară.
- Se tratează un cont Wise ca „numerar" în afara contabilității, fără să fie reflectat printr-un cont bancar corespunzător (de regulă 5124 pentru soldurile în valută) — orice sold deținut pe o astfel de platformă trebuie evidențiat contabil, la fel ca un cont bancar clasic.
- Se lasă diferența de curs neînregistrată „pentru că suma e mică" — pct. 322 nu prevede un prag de semnificație; diferența se recunoaște în luna în care apare, indiferent de mărime.

## Ce face iConta.eu

Motorul de curs valutar (F025, `core/curs_bnr.py`) preia și aplică automat cursul BNR pentru facturile în valută, conform regulii legale a ultimului curs comunicat, valabil la data operațiunii — sursă unică de conversie folosită de TVA, D300, D390, D394, D406 și de contarea facturilor din aplicație. Acesta e reperul legal de curs pe care contabilul îl poate folosi ca punct de plecare și pentru operațiunile de trezorerie, inclusiv un schimb valutar făcut printr-un cont Wise.

iConta.eu nu are însă un modul dedicat de „schimb valutar" sau de conectare la platforme de tip Wise — o astfel de operațiune se înregistrează ca **notă contabilă manuală** (ieșire din contul sursă, intrare în contul destinație, diferența de curs pe 665/765), folosind cursul de referință afișat de aplicație doar ca sprijin de verificare, nu ca sursă automată a operațiunii de schimb.

[iConta.eu](/)
