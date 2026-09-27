---
title: Cum verific e-Factura cu jurnalul de vânzări?
description: Fiecare factură din jurnalul de vânzări care intră sub obligația RO e-Factura trebuie să aibă un mesaj validat în sistem, transmis în 5 zile lucrătoare (OUG nr. 120/2021, art. 10, cu modificările din OUG nr. 89/2025); reconcilierea lunară pe număr, dată, client, bază și TVA previne amenzile din art. 13^2 și diferențele față de RO e-TVA.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific e-Factura cu jurnalul de vânzări?

Faci o reconciliere lunară, factură cu factură, între jurnalul de vânzări și lista facturilor emise din SPV. Cheia de legătură este seria și numărul facturii. Compari data, codul fiscal al clientului, baza de impozitare și TVA. Orice factură din jurnal fără corespondent validat în e-Factura, sau invers, trebuie explicată înainte de depunerea D300.

### De ce trebuie să coincidă

Jurnalul de vânzări este evidența din care se completează D300. Instrucțiunile D300 precizează că prin jurnal se înțelege orice evidență pe care persoana impozabilă trebuie să o țină potrivit Codului fiscal art. 321 și pct. 101 din Normele metodologice (OPANAF nr. 174/2026).

De cealaltă parte, facturile B2B dintre persoane impozabile stabilite în România se transmit obligatoriu prin RO e-Factura. Excepție fac facturile simplificate (OUG nr. 120/2021, art. 10 alin. (1)). Din 2025, obligația se aplică și facturilor B2C, cu excepția bonurilor fiscale care îndeplinesc condițiile de factură simplificată (art. 10^1 alin. (2), introdus prin OUG nr. 138/2024). Decontul precompletat RO e-TVA este construit și din datele RO e-Factura (OUG nr. 70/2024, art. 2 alin. (1) lit. a)).

Termenul de transmitere este de 5 zile lucrătoare de la emitere, dar nu mai târziu de 5 zile lucrătoare de la data-limită de emitere (OUG nr. 120/2021, art. 10 alin. (7), modificat prin OUG nr. 89/2025).

### Ce riști dacă nu coincid

- O factură B2B netransmisă prin sistem: amendă egală cu 15% din valoarea totală a facturii (art. 13^2 alin. (1) lit. a) și alin. (2)).
- O factură transmisă după termen: amendă de la 1.000 la 2.500 lei pentru persoanele juridice care nu sunt contribuabili mari sau mijlocii (art. 13^2 alin. (3)).
- Diferențe între D300 și decontul precompletat, care pot atrage verificări.

### Pașii reconcilierii

1. **Descarcă lista facturilor emise** din SPV pentru luna respectivă, cu starea fiecărui mesaj.
2. **Exportă jurnalul de vânzări** din contabilitate pe aceeași lună.
3. **Potrivește pe serie și număr.** Pune deoparte:
   - facturi în jurnal fără mesaj în e-Factura: netransmise, respinse la validare sau exceptate;
   - facturi în e-Factura care lipsesc din jurnal: neînregistrate sau înregistrate pe altă lună;
   - facturi prezente în ambele, dar cu alte valori.
4. **Verifică respingerile.** Factura respinsă la validare nu are sigiliul Ministerului Finanțelor și nu se consideră primită în sistem (art. 4 alin. (4)). Emitentul primește mesajul cu erori și retransmite factura corectată (art. 4 alin. (5)), în termen.
5. **Verifică excepțiile.** Bonurile fiscale cu valoare de factură simplificată și unele livrări intracomunitare apar în jurnal, dar nu trebuie să fie în e-Factura.
6. **Verifică datele.** Factura intră în jurnalul lunii în care e exigibilă TVA, nu neapărat în luna transmiterii.
7. **Verifică storno-urile.** Factura de corecție trebuie să fie și ea în e-Factura și în jurnal, cu semnul minus.

### Exemplu

În aprilie, jurnalul are 214 facturi, cu bază totală de 612.000 lei și TVA de 128.520 lei. În SPV sunt 211 mesaje validate. Diferența: două bonuri fiscale cu valoare de factură simplificată, exceptate, și o factură de 4.000 lei plus TVA respinsă pentru cod fiscal greșit și neretransmisă. Factura respinsă se corectează și se transmite imediat. Dacă termenul de 5 zile lucrătoare a trecut, riscul este amenda din art. 13^2 alin. (3).

### De reținut
- Reconciliezi lunar, pe serie și număr, înainte de D300.
- Factura respinsă la validare nu este transmisă. Retransmite-o corect și în termen (OUG nr. 120/2021, art. 4 alin. (4)-(5)).
- Netransmiterea B2B se sancționează cu 15% din valoarea facturii, iar transmiterea tardivă cu amendă fixă (art. 13^2).
- Nu toate facturile din jurnal trebuie să fie în e-Factura: verifică excepțiile.
