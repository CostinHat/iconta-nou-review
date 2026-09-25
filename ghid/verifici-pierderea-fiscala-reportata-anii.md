---
title: "Cum verifici pierderea fiscală reportată din anii anteriori?"
description: "Regulile de recuperare a pierderii fiscale la impozitul pe profit — limita de 70%, orizontul de 5 sau 7 ani și ordinea cronologică de recuperare — conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verifici pierderea fiscală reportată din anii anteriori?

O pierdere fiscală înregistrată într-un an nu se „pierde" definitiv — dar nici nu se recuperează oricum, oricând. Codul fiscal fixează atât limita anuală până la care poate fi folosită, cât și orizontul de timp în care trebuie recuperată, iar cele două reguli diferă în funcție de anul în care a apărut pierderea.

## Temeiul legal

::: ghid-temei
„(1) Pierderile fiscale anuale stabilite prin declarația de impozit pe profit, începând cu anul 2024/anul fiscal modificat care începe în anul 2024, după caz, se recuperează din profiturile impozabile realizate, în limita a 70% inclusiv, în următorii 5 ani consecutivi. Recuperarea pierderilor se va efectua în ordinea înregistrării acestora, la fiecare termen de plată a impozitului pe profit.
(7) Pierderile fiscale anuale stabilite prin declarația de impozit pe profit, aferente anilor precedenți anului 2024/anului care începe în 2024, rămase de recuperat la data de 31 decembrie 2023, se recuperează din profiturile impozabile realizate începând cu anul 2024, în limita a 70% din profiturile impozabile respective, pe perioada rămasă de recuperat din cei 7 ani consecutivi ulteriori anului înregistrării pierderilor respective."
— Legea nr. 227/2015 (Codul fiscal), art. 31 alin. (1), (7) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Verificarea corectă a unei pierderi fiscale reportate trebuie să distingă între două regimuri:

- **Pierderile din 2024 încolo** se recuperează în limita a **70%** din profitul impozabil al fiecărui an, pe o perioadă de **5 ani consecutivi**, în ordinea cronologică a înregistrării lor — cea mai veche pierdere se recuperează prima.
- **Pierderile din anii anteriori lui 2024**, rămase nerecuperate la 31 decembrie 2023, se recuperează tot în limita a 70% din profitul impozabil, dar pe perioada **rămasă** din orizontul de **7 ani** de la anul în care au apărut — nu 5 ani, ca cele noi.
- Dacă firma recuperează simultan pierderi vechi (regimul de 7 ani) și pierderi noi (regimul de 5 ani), limita de 70% se aplică **cumulat** peste toate pierderile recuperate în acel an, nu separat pentru fiecare categorie.
- Verificarea „câtă pierdere mai poate fi recuperată" presupune reconstituirea, an de an, a pierderilor declarate prin D101, a sumelor deja recuperate și a anului-limită până la care fiecare tranșă mai poate fi folosită — o pierdere neutilizată până la expirarea orizontului (5 sau 7 ani, după caz) devine definitivă și nu mai poate fi recuperată.

## Ce se greșește în practică

- Se aplică regula de 5 ani și pierderilor vechi, din perioada anterioară lui 2024, ignorând regimul tranzitoriu de 7 ani care li se aplică acestora.
- Nu se urmărește ordinea cronologică de recuperare (cea mai veche pierdere întâi), riscând să se folosească limita de 70% pe o pierdere mai nouă, în timp ce una mai veche riscă să expire nerecuperată.
- Se presupune că o pierdere neutilizată la finalul orizontului legal (5 sau 7 ani) mai poate fi folosită ulterior, deși ea devine definitiv nerecuperabilă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează profitul/pierderea fiecărui trimestru cumulat prin D101 (`core/d101.py`), pe baza formulei venituri minus cheltuieli, cu impozitarea corectă a unui trimestru cu profit care urmează unui trimestru cu pierdere. Aplicația **nu ține un registru dedicat de urmărire multianuală** a pierderii fiscale reportate — care să calculeze automat, an de an, cât a mai rămas de recuperat din fiecare tranșă de pierdere și orizontul (5 sau 7 ani) aplicabil fiecăreia. Verificarea pierderii fiscale reportate din anii anteriori rămâne, la acest moment, o reconstituire manuală a contabilului, pe baza declarațiilor D101 depuse succesiv.

[iConta.eu](/)
