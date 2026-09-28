---
title: Suma reportată și suma dedusă în D107: cum completez coloanele 5 și 6 pe fiecare beneficiar
description: În D107, coloana 5 cuprinde suma reportată din perioadele anterioare pentru fiecare beneficiar, iar coloana 6 suma dedusă efectiv în anul de raportare din impozitul pe profit sau din impozitul minim, aferentă sumelor acordate în an sau celor reportate (OPANAF 355/2024, anexa 2 pct. 10.5-10.6).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Suma reportată și suma dedusă în D107: cum completez coloanele 5 și 6 pe fiecare beneficiar

Coloanele 4, 5 și 6 din D107 răspund la trei întrebări diferite despre același beneficiar: cât i-ai dat în anul de raportare (col. 4), cât ai adus din anii anteriori ca sumă reportată (col. 5) și cât ai scăzut efectiv din impozit în anul de raportare (col. 6). Col. 6 nu este diferența dintre col. 4 și col. 5. Este suma scăzută efectiv, repartizată pe beneficiari.

### Ce spun instrucțiunile

OPANAF 355/2024, anexa 2:

- **pct. 10.5, coloana 5 „Suma reportată"**: valoarea sponsorizărilor, mecenatului și a bunurilor, mijloacelor financiare și serviciilor „reportată din perioada anterioară anului de raportare/perioadei de raportare";
- **pct. 10.6, coloana 6 „Suma dedusă"**: suma dedusă din impozitul pe profit sau din impozitul minim pe cifra de afaceri, după caz, în anul de raportare, corespunzătoare sumelor acordate fiecărui beneficiar în anul de raportare „sau corespunzătoare sumelor reportate în anul de raportare/perioada de raportare individualizate pe beneficiari".

Pct. 10.1 adaugă o regulă ușor de ratat: în secțiunea B apar și beneficiarii din anii precedenți pentru care s-au înscris sume reportate în col. 5, chiar dacă în anul curent nu au primit nimic. Excepție fac beneficiarii trecuți în anexă, adică sumele reportate dinainte de 2018 care nu pot fi individualizate.

### Rândurile de total

Structura XML publicată de ANAF pentru D107 calculează totalurile astfel:

- totalul col. 4 = suma col. 4 pe beneficiari;
- totalul col. 5 = suma col. 5 pe beneficiari + suma reportată neindividualizată;
- totalul col. 6 = suma col. 6 pe beneficiari + suma dedusă aferentă sumelor neindividualizate.

Suma de control a declarației este totalul celor trei coloane.

### Exemplu

O firmă plătitoare de impozit pe profit are din anii anteriori o sumă reportată potrivit legii de 12.000 lei, aferentă fundației X. În 2026:

- sponsorizează fundația X cu 10.000 lei;
- sponsorizează asociația Y cu 25.000 lei;
- limita de scădere din impozit pe 2026, calculată conform Codului fiscal art. 25 alin. (4) lit. i), este 30.000 lei.

Firma scade 30.000 lei din impozitul pe profit pe 2026. Cum această sumă acoperă o parte din reportul fundației X și o parte din sumele anului, firma își documentează în evidența proprie repartizarea pe beneficiari. Presupunem repartizarea: 12.000 lei din suma reportată a fundației X, 10.000 lei din sponsorizarea fundației X din 2026 și 8.000 lei din sponsorizarea asociației Y.

| Beneficiar | Col. 4 Suma | Col. 5 Suma reportată | Col. 6 Suma dedusă |
|---|---|---|---|
| Fundația X | 10.000 | 12.000 | 22.000 |
| Asociația Y | 25.000 | 0 | 8.000 |
| **Total** | 35.000 | 12.000 | 30.000 |

Totalul col. 6 (30.000 lei) coincide cu suma scăzută din impozit în declarația anuală de impozit pe profit.

### Greșeli frecvente

- Se trece la col. 6 suma acordată în an, nu suma scăzută efectiv.
- Se omite beneficiarul din anii anteriori care are sumă reportată, pe motiv că nu a primit nimic în anul curent.
- Totalul col. 6 nu corespunde cu suma scăzută în declarația anuală de impozit pe profit.

### Pași practici pentru contabil

1. Ține pe fiecare beneficiar evidența: sumă acordată, sumă scăzută, rest reportat.
2. Completează col. 5 și 6 pe fiecare beneficiar, inclusiv pentru cei cu sume reportate.
3. Verifică totalul col. 6 cu declarația anuală de impozit pe profit.

### De reținut
- Col. 4 cuprinde sumele acordate în anul de raportare, col. 5 sumele reportate, col. 6 suma scăzută efectiv din impozit (OPANAF 355/2024, anexa 2 pct. 10.4-10.6).
- Beneficiarii care au doar sume reportate apar și ei în secțiunea B (pct. 10.1).
- Totalul col. 6 trebuie să fie egal cu suma scăzută din impozitul pe profit sau din impozitul minim.
- Sumele dinainte de 2018 neindividualizabile au rând separat și anexă.
