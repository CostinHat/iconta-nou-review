---
title: Cum se calculează numărul tichetelor de masă?
description: Numărul de tichete de masă este egal cu zilele efectiv lucrate din pontaj, nu cu zilele calendaristice — concediul de odihnă, delegația, absențele și învoirile nu dau drept la tichet, iar calculul se blochează dacă pontajul lunii nu e confirmat.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se calculează numărul tichetelor de masă?

Tichetele de masă nu se acordă „automat" pe fiecare zi din lună, ci strict pe zilele în care salariatul a lucrat efectiv, conform pontajului. Diferența dintre zile calendaristice, zile lucrătoare și zile efectiv lucrate este sursa celor mai multe greșeli de calcul.

## Temeiul legal

::: ghid-temei
HG nr. 1045/2018 (normele metodologice de aplicare a Legii 165/2018), Articolul 10:

> „(1) În cazul tichetelor de masă, angajatorii nu pot acorda mai mult de un tichet de masă pentru fiecare zi lucrătoare din luna pentru care se efectuează transferul valorii nominale a tichetelor de masă. În sensul prezentelor norme nu se consideră zile lucrate perioadele în care salariații: a) efectuează concediul de odihnă...; b) beneficiază de zile libere plătite...; c) sunt delegați sau detașați...; d) se află în concediu pentru incapacitate temporară de muncă, sunt absenți de la locul de muncă ori se află în alte situații stabilite de angajator..."

> „(3) Salariații beneficiază lunar de un număr de tichete de masă cel mult egal cu numărul de zile lucrate, iar acest număr nu poate depăși numărul de zile lucrătoare din luna pentru care se acordă tichetele."
:::

## Ce zile scad din numărul de tichete

Legea exclude explicit din „zile lucrate" perioadele de concediu de odihnă, zilele libere plătite, delegația/detașarea și absențele. Practic, pentru calculul tichetelor contează doar zilele în care salariatul a fost prezent la muncă, așa cum rezultă din pontaj — nu zilele lucrătoare din calendar, nici zilele calendaristice.

::: ghid-exemplu
O lună are 21 de zile lucrătoare. Un salariat a fost 3 zile în concediu de odihnă și o zi în delegație. Numărul de tichete de masă cuvenite pentru luna respectivă este 21 − 3 − 1 = 17 tichete, nu 21.
:::

## Ce se greșește în practică

- Se calculează tichetele pe numărul de zile lucrătoare din calendar, fără a scădea concediul de odihnă, delegația sau absențele.
- Se acordă tichet și pentru zilele de concediu medical, deși acestea se scad tot din baza de calcul (evidența CM este separată de restul zilelor „fără tichet").
- Se depune statul de plată cu tichete calculate pe un pontaj care încă nu e confirmat, ceea ce duce ulterior la corecții și rectificative.
- Se confundă „zile libere plătite" cu zile lucrate, deși legea le exclude explicit din baza de calcul a tichetelor.

## Ce face iConta.eu

Numărul de tichete nu este un câmp introdus manual: se calculează la generarea statului de plată, pe baza pontajului lunii. Funcția `zile_fara_tichet()` din modulul de pontaj exclude din numărul de zile lucrate stările `concediu_odihna`, `delegatie`, `absent_motivat`, `absent_nemotivat` și `invoire`, citând explicit HG 1045/2018 art. 10 alin. (3); concediul medical se scade separat, din evidența de concedii medicale. Dacă pontajul lunii nu este confirmat, aplicația blochează valoarea tichetului de masă la 0 pentru acea lună, tocmai pentru a nu genera un stat de plată pe date neconfirmate.

[iConta.eu](/)
