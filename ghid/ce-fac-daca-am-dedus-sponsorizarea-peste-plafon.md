---
title: Ce fac dacă am dedus sponsorizarea peste plafon?
description: Trebuie identificat anul fiscal al erorii — plafonul a fost 0,5% din cifra de afaceri cu reportare pe 7 ani până la 02.02.2022 și 0,75% cu redirecționare D177 de atunci încolo — apoi recalculat plafonul corect și depusă o D101 rectificativă cu impozit pe profit suplimentar de plată.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce fac dacă am dedus sponsorizarea peste plafon?

Dacă ați observat, după depunerea declarației 101, că ați scăzut din impozitul pe profit o sumă de sponsorizare mai mare decât permitea plafonul legal, trebuie să corectați declarația — dar corectarea corectă depinde de **anul fiscal** vizat, pentru că plafonul legal a fost diferit de-a lungul timpului.

## Temeiul legal

::: ghid-temei
**Forma actuală (de la 03.02.2022):**

„scad sumele aferente din impozitul pe profit datorat la nivelul valorii minime dintre următoarele: 1. valoarea calculată prin aplicarea a 0,75% la cifra de afaceri; pentru situațiile în care reglementările contabile aplicabile nu definesc indicatorul cifra de afaceri, această limită se determină potrivit normelor; 2. valoarea reprezentând 20% din impozitul pe profit datorat.”

— *Codul fiscal, art. 25 alin. (4) lit. i), forma actuală.*

**Forma inițială (2015):**

„1. valoarea calculată prin aplicarea a 0,5% la cifra de afaceri...; 2. valoarea reprezentând 20% din impozitul pe profit datorat. Sumele care nu sunt scăzute din impozitul pe profit, potrivit prevederilor prezentei litere, se reportează în următorii 7 ani consecutivi. Recuperarea acestor sume se va efectua în ordinea înregistrării acestora, în aceleași condiții, la fiecare termen de plată a impozitului pe profit.”

— *Codul fiscal 227/2015, forma inițială, art. 25 alin. (4) lit. i).*

**Forma intermediară (Legea nr. 30/2019):**

„1. valoarea calculată prin aplicarea a 0,5% la cifra de afaceri...; 2. valoarea reprezentând 20% din impozitul pe profit datorat. ... doar dacă beneficiarul sponsorizării este înscris, la data încheierii contractului, în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale, potrivit alin. (4^1). Sumele care nu sunt scăzute din impozitul pe profit, potrivit prevederilor prezentei litere, se reportează în următorii 7 ani consecutivi.”

— *Legea nr. 30/2019, care aprobă OUG 25/2018.*
:::

## Pași pentru corectare

1. **Identificați anul fiscal al erorii** — plafonul se calculează cu regula valabilă în acel an, nu cu regula de azi.
   - Pentru 2015 – 19.01.2019: plafon 0,5% din cifra de afaceri, fără condiție de Registru.
   - Pentru 20.01.2019 – 02.02.2022: plafon 0,5% din cifra de afaceri, cu condiția ca beneficiarul să fie înscris în Registru la data încheierii contractului.
   - Pentru 03.02.2022 – prezent: plafon 0,75% din cifra de afaceri, cu aceeași condiție de Registru.
2. **Recalculați plafonul corect** ca `min(procentul din cifra de afaceri, 20% din impozitul pe profit datorat)` pentru anul respectiv.
3. **Comparați cu suma efectiv scăzută** din impozitul pe profit al acelui an. Dacă suma dedusă e mai mare decât plafonul corect, diferența a fost scăzută nejustificat.
4. **Depuneți o D101 rectificativă**, cu impozitul pe profit suplimentar de plată rezultat din diminuarea creditului, pentru anul fiscal respectiv.
5. **Tratați corect diferența**, în funcție de perioadă: pentru ani dinainte de 03.02.2022, excedentul real (calculat la 0,5%) se reporta pe 7 ani — verificați dacă nu cumva ați reportat deja greșit prin D177 o sumă care ar fi trebuit reportată pe cei 7 ani.

## Ce se greșește în practică

- Se calculează retroactiv plafonul cu 0,75% pentru un an anterior lui 2022, când plafonul legal era de fapt 0,5%, ceea ce duce la o corecție insuficientă.
- Se depune corecția fără a recalcula impozitul pe profit suplimentar de plată rezultat din diminuarea creditului.
- Se tratează excedentul dintr-un an anterior lui 2022 ca redirecționabil prin D177, deși procedura D177 nu exista atunci — mecanismul corect era reportarea pe 7 ani.
- Se omite verificarea Registrului entităților/unităților de cult la data încheierii contractului: dacă beneficiarul nu era înscris, întregul credit e nedatorat, nu doar excedentul peste plafon.
- Se confundă plafonul de la impozitul pe profit cu cel de la impozitul micro (care, cât a existat, era 20% din impozitul micro trimestrial, fără legătură cu cifra de afaceri).

## Ce face iConta.eu

Motorul din `core/sponsorizari.py` (`plafon_credit()`, `credit_sponsorizare()`) are o singură regulă înregistrată, datată „2018-01-01”, care calculează plafonul mereu ca `min(0,75% × cifra de afaceri, 20% × impozit pe profit)`, indiferent de parametrul `la_data` transmis. Niciun test din suita existentă nu verifică un `la_data` anterior lui 2022, iar acest comportament nu este garantat corect pentru astfel de date.

Dacă recalculați în iConta.eu o corecție pentru un an anterior lui 03.02.2022, aplicația va folosi tot 0,75%/D177, nu 0,5%/reportare 7 ani. Pentru aceste corecții, calculați manual plafonul cu procentul valabil în anul respectiv și nu vă bazați pe rezultatul automat al motorului.

[iConta.eu](/)
