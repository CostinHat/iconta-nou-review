---
title: "Cum se completează D112 pentru un salariat part-time?"
description: "Ce date trebuie introduse corect pentru un salariat cu normă parțială, ca declarația 112 să reflecte corect baza minimă de contribuții, și ce limite are azi completarea din interfață."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se completează D112 pentru un salariat part-time?

Pentru un salariat cu contract cu timp parțial, completarea corectă a declarației 112 nu înseamnă doar trecerea salariului brut real — presupune și verificarea că baza de calcul a contribuțiilor nu coboară sub un prag minim legal, indiferent de câte ore lucrează efectiv salariatul. Diferența, dacă apare, intră tot în declarație, dar pe un rând separat, în sarcina angajatorului.

## Temeiul legal

::: ghid-temei
„Contribuția de asigurări sociale datorată de către persoanele fizice care obțin venituri din salarii sau asimilate salariilor, în baza unui contract individual de muncă cu normă întreagă sau cu timp parțial, calculată potrivit alin. (5), nu poate fi mai mică decât nivelul contribuției de asigurări sociale calculate prin aplicarea cotei prevăzute la art. 138 lit. a) asupra salariului de bază minim brut pe țară în vigoare în luna pentru care se datorează contribuția de asigurări sociale, corespunzător numărului zilelor lucrătoare din lună în care contractul a fost activ."
— Legea 227/2015 (Codul fiscal), art. 146 alin. (5^6) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

- Baza de comparație e salariul minim brut pe țară în vigoare în luna respectivă, nu salariul minim pe economie „de la începutul anului" — dacă minimul crește pe parcursul anului, pragul crește odată cu el.
- Proporționalizarea se face pe zilele lucrătoare din lună în care contractul a fost activ, nu pe număr de ore din normă.
- Dacă baza reală de calcul (venitul efectiv al salariatului) e mai mică decât acest prag minim proporțional, diferența de contribuție nu se pierde — ea trebuie totuși declarată, separat, pe seama angajatorului (vezi CF art. 146 alin. 5^9).

## Ce se greșește în practică

- Se introduce doar salariul brut contractual, fără verificarea explicită dacă acesta, proporționalizat, atinge pragul minim — riscul e ca declarația să iasă cu o bază de contribuții mai mică decât cea legal cerută.
- Se bifează „scutit de contribuție minimă" din reflex, fără verificarea reală a uneia din condițiile legale de excepție (elev/student sub 26 ani, ucenic, persoană cu dizabilități, pensionar la limită de vârstă, sau cumul de contracte cu bază lunară cumulată peste minim).
- Se presupune că orele lucrate efectiv (folosite, de exemplu, la calculul tichetelor de masă) sunt același lucru cu tipul de normă declarat oficial în formularul 112 — nu sunt aceleași câmpuri și nu au aceeași destinație.

## Ce face iConta.eu

Pentru un salariat marcat ca part-time, iConta calculează automat, corect, baza minimă proporțională și — dacă e cazul — diferența de contribuție suportată de angajator, folosind exact același motor de calcul ca statul de plată, ca sursă unică de adevăr între cele două documente. Din formularul de salariat se poate introduce salariul brut, orele/zi (folosite pentru proratarea facilităților/tichetelor) și se poate bifa „Scutit contribuție minimă" dacă se aplică vreuna dintre excepțiile legale.

Ce nu se poate completa azi din interfața aplicației: **motivul exact al scutirii** (1–5, cerut de nomenclatorul ANAF pentru a marca formal, în XML, care dintre cele cinci excepții se aplică — elev/student, ucenic, dizabilitate, pensionar sau cumul de contracte) nu are niciun câmp dedicat în formularul de salariat, deși structura de date din aplicație îl citește și l-ar emite corect dacă ar fi completat. La fel, tipul exact de normă (P1..P7, câte ore/zi are contractul parțial) nu e transmis distinct către declarație — câmpul respectiv iese azi cu valoarea de normă întreagă, indiferent de situația reală. Contabilul poate introduce corect toate datele de calcul, dar aceste două marcaje declarative rămân, la data acestui ghid, limitări reale ale aplicației.

[iConta.eu](/)
