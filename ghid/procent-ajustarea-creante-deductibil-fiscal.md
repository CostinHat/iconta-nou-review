---
title: "Ce procent din ajustarea pentru creanțe este deductibil fiscal?"
description: "Trei procente posibile — 0%, 30% sau 100% — în funcție de vechimea creanței, starea debitorului, garantare și afiliere, aplicate în această ordine de verificare."
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce procent din ajustarea pentru creanțe este deductibil fiscal?

Procentul deductibil dintr-o ajustare pentru deprecierea creanțelor nu e fix — depinde de patru factori verificați într-o anumită ordine: garantarea creanței, afilierea debitorului, existența unei proceduri de faliment/insolvență declarate și, în lipsa acesteia, numărul de zile de la scadență. Rezultatul e întotdeauna unul din trei procente: 0%, 30% sau 100%.

## Temeiul legal

::: ghid-temei
„Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru depreciere, numai în conformitate cu prezentul articol, astfel: [...] c) ajustările pentru deprecierea creanțelor [...] în limita unui procent de 30% din valoarea acestor ajustări [...] dacă creanțele îndeplinesc cumulativ următoarele condiții: 1. sunt neîncasate într-o perioadă ce depășește 270 de zile de la data scadenței; 2. nu sunt garantate de altă persoană; 3. sunt datorate de o persoană care nu este persoană afiliată contribuabilului[...] j) ajustările pentru deprecierea creanțelor [...] în limita unui procent de 100% din valoarea creanțelor [...] dacă creanțele îndeplinesc cumulativ următoarele condiții: 1. sunt deținute la o persoană juridică asupra căreia este declarată procedura de deschidere a falimentului [...] sau la o persoană fizică asupra căreia este deschisă procedura de insolvență [...] 2. nu sunt garantate de altă persoană; 3. [neafiliate]"

*(Codul fiscal — Legea nr. 227/2015, art. 26 alin. (1) lit. c) și j))*
:::

## Ordinea de verificare, cu cele patru rezultate posibile

1. **Creanța e garantată sau debitorul e persoană afiliată** → 0%, necondiționat, indiferent de vechime sau de stadiul de insolvență.
2. **Debitorul (persoană juridică) are declarată procedura de faliment prin hotărâre judecătorească, sau (persoană fizică) e în procedură de insolvență**, iar creanța e negarantată și neafiliată → 100%.
3. **În lipsa falimentului/insolvenței, dacă au trecut peste 270 de zile de la scadență**, negarantată, neafiliată → 30%.
4. **Sub 270 de zile de la scadență, fără faliment declarat** → 0%, deocamdată — pragul nu e încă atins.

## Ce se greșește în practică

- Se aplică 30% direct, fără să se verifice întâi dacă debitorul e în faliment declarat (caz în care procentul corect e 100%, nu 30%).
- Se calculează zilele de întârziere de la data facturii, nu de la data scadenței.
- Se acordă un procent (30% sau 100%) unei creanțe garantate sau afiliate, deși legea le exclude explicit, indiferent de celelalte condiții.

## Ce face iConta.eu

`deductibilitate_creanta(zile_depasire_scadenta, garantata, afiliata, faliment_declarat)` din `core/provizioane.py` aplică exact ordinea de mai sus și întoarce procentul corect plus temeiul textual asociat (de exemplu „art. 26(1)c" pentru 30%, „art. 26(1)j" pentru 100%). Funcția nu calculează singură zilele de întârziere sau nu verifică automat starea de faliment a debitorului — aceste date sunt introduse de contabil, pe baza documentelor disponibile.

[iConta.eu](/)
