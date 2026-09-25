---
title: "Ce se întâmplă cu documentele contabile după radierea firmei?"
description: "Unde ajung registrele, situațiile financiare și documentele justificative ale unei firme radiate și pentru cât timp trebuie păstrate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce se întâmplă cu documentele contabile după radierea firmei?

Radierea unei firme din registrul comerțului nu înseamnă că documentele ei contabile dispar odată cu personalitatea juridică. Legea contabilității obligă la predarea lor către arhivele statului, exact pentru situațiile de încetare a activității — indiferent dacă radierea vine dintr-o lichidare voluntară sau dintr-o procedură de insolvență.

## Temeiul legal

::: ghid-temei
„În caz de încetare a activității persoanelor prevăzute la art. 1, situațiile financiare anuale, precum și registrele și celelalte documente la care se referă art. 25 se predau la arhivele statului, în conformitate cu prevederile legale în materie."
— Legea 82/1991 (Legea contabilității), art. 35 alin. (4) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Corelat cu regula generală de păstrare a documentelor (aplicabilă cât timp firma e activă, dar relevantă și pentru perioada premergătoare radierii):

- „Registrele de contabilitate obligatorii și documentele justificative care stau la baza înregistrărilor în contabilitatea financiară se păstrează în arhiva persoanelor [...] timp de 5 ani calculați de la data de 1 iulie a anului următor celui încheierii exercițiului financiar în care au fost întocmite, inclusiv pentru statele de salarii" (Legea 82/1991, art. 25).
- La reorganizare (fuziune, divizare), legea cere explicit ca persoanele juridice „să ia măsuri pentru păstrarea și arhivarea, potrivit legii, a documentelor justificative și a registrelor de contabilitate" (Legea 82/1991, art. 25^1) — deci arhivarea nu e opțională nici înainte de dispariția efectivă a persoanei juridice.
- La **încetarea activității** (inclusiv radiere), obligația trece de la firmă la stat: situațiile financiare anuale și registrele/documentele la care se referă art. 25 se predau arhivelor statului (art. 35 alin. (4)).

## Ce se greșește în practică

- Se distrug documentele contabile odată cu radierea, considerând că odată ce firma nu mai există, obligația de păstrare dispare — obligația nu dispare, ci se transformă în predare către arhivele statului.
- Se confundă termenul de păstrare curent (5 ani, art. 25) cu momentul radierii — chiar dacă termenul de 5 ani nu s-a împlinit la data radierii, documentele tot trebuie predate arhivelor statului, nu păstrate „acasă la fostul administrator".
- Se ignoră faptul că obligația vizează atât situațiile financiare anuale, cât și registrele și documentele justificative — nu doar bilanțurile depuse la ANAF.
- Se lasă predarea nefăcută din lipsă de proceduri clare, expunând administratorii/lichidatorii la riscul de a nu putea face dovada operațiunilor firmei dacă apare ulterior un control sau un litigiu.

## Ce face iConta.eu

iConta.eu păstrează, cât timp o firmă e activă în aplicație, întreaga evidență contabilă generată — facturi, note contabile, declarații depuse. Nu am găsit în cod o funcție dedicată procesului de predare a documentelor către arhivele statului la radierea firmei (procedura de predare e una administrativă, în afara aplicației, reglementată de legislația arhivelor). Modulul de lichidare din aplicație (`lichidare.py`) tratează calculul fiscal al lichidării — impozitarea câștigului distribuit asociaților — nu și arhivarea fizică/electronică a documentelor după radiere.

[iConta.eu](/)
