---
title: "Dispozitivul de marcat electronic: obligații 2026"
description: "Cine este obligat să utilizeze aparate de marcat electronice fiscale (AMEF), ce trebuie să emită la fiecare vânzare și obligația de conectare la sistemul ANAF de supraveghere."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Dispozitivul de marcat electronic: obligații 2026

Obligația de a folosi un aparat de marcat electronic fiscal (AMEF) nu depinde de forma juridică a operatorului economic, ci de modul în care încasează contravaloarea vânzărilor: dacă încasează, integral sau parțial, cu numerar sau cu cardul, contravaloarea bunurilor livrate cu amănuntul ori a serviciilor prestate direct către populație, are obligația legală de a utiliza AMEF.

## Temeiul legal

::: ghid-temei
„(1) Operatorii economici care încasează, integral sau parțial, cu numerar sau prin utilizarea cardurilor de credit/debit sau a substitutelor de numerar contravaloarea bunurilor livrate cu amănuntul, precum și a prestărilor de servicii efectuate direct către populație sunt obligați să utilizeze aparate de marcat electronice fiscale.
(2) [...] au obligația să emită bonuri fiscale cu aparate de marcat electronice fiscale și să le înmâneze clienților. La solicitarea clienților, utilizatorii vor elibera acestora și factură."
— OUG nr. 28/1999 (republicată), art. 1 alin. (1), (2) (sursă: anaf_surse/oug_28_1999.html)
:::

Din text rezultă obligațiile-cheie pentru 2026:

- Utilizarea AMEF este obligatorie la orice încasare, indiferent dacă e integrală sau parțială, cu numerar sau cu cardul/substitute de numerar, pentru vânzări cu amănuntul sau servicii către populație.
- La fiecare vânzare trebuie emis bonul fiscal și înmânat clientului; factura se eliberează suplimentar, doar la cererea clientului (excepție: pentru plăți cu cardul, utilizatorul nu are obligația să tipărească/înmâneze bonul fiscal, dar îl poate emite la cerere — art. 1 alin. (2^1)).
- Suplimentar față de utilizarea propriu-zisă a aparatului, operatorii economici au obligația de a asigura **conectarea la distanță** a AMEF, pentru transmiterea de date fiscale către ANAF, în cadrul sistemului informatic național de supraveghere și monitorizare (art. 3^1 alin. (4)).

## Ce se greșește în practică

- Se presupune că obligația AMEF există doar pentru încasările integral în numerar, ignorând că legea o extinde explicit și la plățile cu cardul sau substitute de numerar.
- Se omite emiterea bonului fiscal la plățile cu numerar sub pretextul că „se dă și factură" — factura nu înlocuiește bonul fiscal decât în situațiile expres reglementate; regula generală este emiterea bonului, factura fiind suplimentară, la cerere.
- Se ignoră obligația de conectare la distanță a aparatului la sistemul ANAF, considerând-o opțională sau „doar pentru case mari" — legea o impune tuturor utilizatorilor de la art. 1 alin. (1).

## Ce face iConta.eu

La data acestui ghid, iConta.eu poate importa Raportul Z (raportul fiscal de închidere zilnică) generat de aparatele de marcat electronice fiscale, în format p7b sau XML, conform structurii publicate de ANAF prin OPANAF 146/2018 (`core/amef_import.py`). Modulul extrage totalurile de vânzări pe modalități de plată (card, numerar, tichete, vouchere etc.) și pe cote de TVA, pentru a fi preluate în contabilitate. Aplicația nu gestionează însă înregistrarea/conectarea propriu-zisă a aparatului la sistemul ANAF de supraveghere și nici achiziția sau configurarea fizică a dispozitivului — acestea rămân proceduri realizate direct de operatorul economic, prin distribuitorul autorizat al AMEF.

[iConta.eu](/)
