---
title: "Extras de cont pentru instanță: cum îl obțin"
description: "De ce extrasul de cont folosit ca probă în instanță trebuie cerut de la bancă, nu reconstituit din contabilitatea proprie, și ce obligație de păstrare are firma pentru documentele justificative."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Extras de cont pentru instanță: cum îl obțin

Într-un litigiu, o firmă are nevoie uneori de dovada unei plăți sau încasări bancare, într-o formă opozabilă în instanță. Aici trebuie separate două lucruri diferite: ce e valabil ca probă și ce păstrează firma din obligația ei contabilă.

## Temeiul legal

::: ghid-temei
„Articolul 25 Registrele de contabilitate obligatorii și documentele justificative care stau la baza înregistrărilor în contabilitatea financiară se păstrează în arhiva persoanelor prevăzute la art. 1 timp de 5 ani calculați de la data de 1 iulie a anului următor celui încheierii exercițiului financiar în care au fost întocmite, inclusiv pentru statele de salarii."
— Legea contabilității nr. 82/1991, art. 25 (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Ce rezultă din această obligație, aplicat la nevoia de probă pentru instanță:

- **Extrasul de cont ca probă opozabilă în instanță se obține de la bancă**, nu se reconstituie din evidența internă a firmei — banca emite documentul certificat, cu antetul și confirmarea ei, ca terț de încredere; o listă de tranzacții extrasă dintr-un program de contabilitate nu are aceeași forță probatorie.
- **Obligația legală a firmei** e alta: să **păstreze** documentele justificative (inclusiv extrasele bancare importate în contabilitate) timp de **5 ani** de la 1 iulie a anului următor încheierii exercițiului financiar în care au fost întocmite (art. 25) — o obligație de arhivare proprie, distinctă de emiterea unui document opozabil de către bancă.
- Practic, pentru un litigiu recent (în interiorul acestor 5 ani), firma poate, în paralel, să solicite băncii un duplicat/extras oficial pentru perioada respectivă, folosind exact intervalul și contul identificate din propria evidență — dar documentul depus la instanță rămâne cel emis de bancă.

## Ce se greșește în practică

- Se depune la instanță un export din programul de contabilitate al firmei, prezentat ca "extras de cont" — nu are aceeași valoare probatorie ca documentul emis direct de bancă.
- Se presupune că firma nu mai poate obține extrasul dacă a trecut mult timp — termenul de păstrare al documentelor firmei e 5 ani, dar băncile păstrează propriile evidențe conform normelor lor proprii, adesea pe perioade mai lungi; solicitarea se face direct la bancă.
- Se șterg sau nu se arhivează extrasele bancare importate în contabilitate înainte de expirarea celor 5 ani — chiar dacă nu sunt "documentul opozabil" pentru instanță, ele rămân document justificativ contabil obligatoriu de păstrat.

## Ce face iConta.eu

La data acestui ghid, `core/repo_banca.py` păstrează evidența importurilor de extrase bancare (`inregistreaza_import()`, cu hash-ul fișierului sursă) și liniile contabilizate din ele, iar aplicația poate afișa/lista aceste linii importate. Aplicația nu emite însă ea însăși un extras de cont certificat, opozabil în instanță — acel document rămâne, prin natura lui, unul care se obține direct de la banca emitentă.

[iConta.eu](/)
