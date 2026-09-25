---
title: "Cum documentez diferențele fiscale pentru un control viitor"
description: "Obligația de păstrare a evidențelor contabile și fiscale, inclusiv a datelor arhivate electronic și a aplicațiilor cu care au fost generate, potrivit Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum documentez diferențele fiscale pentru un control viitor

Documentarea diferențelor fiscale — de la simple corectări la interpretări asumate ale unor prevederi neclare — se sprijină pe o obligație legală mai largă: păstrarea evidențelor contabile și fiscale în forma și pe durata cerute de lege, astfel încât acestea să poată fi prezentate la un control ulterior.

## Temeiul legal

::: ghid-temei
„ART. 109 Reguli pentru conducerea evidențelor contabile și fiscale
(1) Evidențele contabile și fiscale se păstrează, după caz, la domiciliul fiscal al contribuabilului/plătitorului, la sediul social ori la sediile secundare ale acestuia, inclusiv pe suport electronic, sau pot fi încredințate spre păstrare unei societăți autorizate, potrivit legii, să presteze servicii de arhivare.
[...]
(4) în cazul în care evidențele contabile și fiscale sunt ținute cu ajutorul sistemelor electronice de gestiune, pe lângă datele arhivate în format electronic contribuabilul/plătitorul este obligat să păstreze și să prezinte aplicațiile informatice cu ajutorul cărora le-a generat."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 109 alin. (1) și (4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă din text pentru pregătirea unui control fiscal viitor:

- Nu ajunge să existe cifrele finale — evidențele contabile și fiscale **complete** trebuie păstrate, la domiciliul fiscal, sediul social/secundar sau la un arhivator autorizat, accesibile la cerere.
- Dacă evidențele sunt ținute electronic, obligația nu se limitează la datele arhivate — trebuie păstrate și **prezentate aplicațiile informatice** cu care acestea au fost generate, nu doar exporturi statice.
- Nerespectarea obligației de a păstra și prezenta datele arhivate electronic și aplicațiile aferente este contravenție distinctă (art. 336 alin. (1) lit. f) din același cod).

## Ce se greșește în practică

- Se păstrează doar rapoartele finale (balanțe, declarații depuse), fără evidența analitică din care acestea au fost generate — insuficient dacă organul de control cere detalii pe tranzacție.
- Se schimbă sistemul informatic de contabilitate fără a păstra accesul la aplicația veche folosită pentru perioadele anterioare, deși art. 109 alin. (4) cere explicit prezentarea aplicațiilor cu care au fost generate datele.
- Se documentează o poziție fiscală discutabilă abia în timpul controlului, nu la momentul tranzacției — o notă internă contemporană cu operațiunea are o valoare probatorie mult mai mare decât o explicație construită ulterior.

## Ce face iConta.eu

Verificat în cod: `core/control_incrucisat.py` compară în mod explicit datele declarate cu evidența contabilă și marchează fiecare constatare cu trei stări posibile — verde (coerent), roșu (divergent) sau gri (nu s-a putut verifica) — declarând totodată temeiul și limita fiecărei verificări, potrivit docstringului modulului; iConta.eu păstrează în platformă evidența contabilă și declarațiile generate pentru firmă, ceea ce sprijină documentarea unui eventual control, dar nu constituie el însuși un serviciu de arhivare autorizat în sensul art. 109 alin. (1).

[iConta.eu](/)
