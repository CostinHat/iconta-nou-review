---
title: "Pot deduce TVA dacă furnizorul are codul de TVA anulat?"
description: "Ce spune Codul fiscal despre dreptul de deducere a TVA la achizițiile de la un furnizor al cărui cod de TVA a fost anulat, și care sunt excepțiile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Pot deduce TVA dacă furnizorul are codul de TVA anulat?

Regula generală e clară și restrictivă: dacă furnizorul tău a rămas fără cod valid de TVA din motivele „grele" prevăzute de lege, riști să pierzi dreptul de deducere pentru achizițiile făcute în acea perioadă — cu două excepții precise și un mecanism de recuperare ulterioară.

## Temeiul legal

::: ghid-temei
„Beneficiarii care achiziționează bunuri și/sau servicii de la persoane impozabile stabilite în România, cărora li s-a anulat înregistrarea în scopuri de TVA conform prevederilor art. 316 alin. (11) lit. c)-e) și lit. h), și au fost înscriși în Registrul persoanelor impozabile a căror înregistrare în scopuri de TVA conform art. 316 a fost anulată, nu beneficiază de dreptul de deducere a taxei pe valoarea adăugată aferente achizițiilor respective, cu excepția achizițiilor de bunuri efectuate în cadrul procedurii de executare silită și/sau a achizițiilor de bunuri de la persoane impozabile aflate în procedura falimentului potrivit Legii nr. 85/2014, cu modificările și completările ulterioare."
— Codul fiscal, art. 11 alin. (9) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt:1464-1469)

„A.N.A.F. organizează Registrul persoanelor impozabile înregistrate în scopuri de TVA conform art. 316 și Registrul persoanelor impozabile a căror înregistrare în scopuri de TVA conform art. 316 a fost anulată. Registrele sunt publice și se afișează pe site-ul A.N.A.F."
— Codul fiscal, art. 316 alin. (15) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Câteva puncte esențiale, care rezultă direct din text:

- Interdicția de deducere se aplică **doar** pentru anulările din motivele de la art.316 alin.(11) **lit. c)-e) și h)** — practic, situațiile „grele": cazier fiscal cu infracțiuni al asociaților/administratorilor, nedepunerea deconturilor timp de 6 luni consecutive, deconturi fără achiziții/livrări timp de 6 luni consecutive, respectiv risc fiscal ridicat. Anulările din alte motive (de exemplu, inactivitate fiscală, tratată separat la alin.6-7, sau ieșirea voluntară din scopuri de TVA pentru un regim special, lit.g) au alt tratament.
- Există **două excepții explicite** de la pierderea dreptului de deducere: achizițiile de bunuri făcute în cadrul unei proceduri de executare silită și achizițiile de la un furnizor aflat în procedură de faliment.
- Legea prevede un **mecanism de recuperare**: dacă furnizorul se reînregistrează ulterior în scopuri de TVA (art.316 alin.12), beneficiarul își poate exercita dreptul de deducere pentru achizițiile din perioada „fără cod", prin înscrierea taxei în primul decont depus după reînregistrarea furnizorului sau într-un decont ulterior.
- Verificarea statutului furnizorului se face pe **Registrul public al ANAF** al persoanelor cu codul de TVA anulat — un registru accesibil oricui, pe site-ul ANAF.

## Ce se greșește în practică

- Se presupune că orice furnizor cu codul de TVA anulat, indiferent de motiv, blochează automat dreptul de deducere — restricția se aplică specific anulărilor din lit. c)-e) și h), nu tuturor cazurilor de anulare.
- Se renunță definitiv la deducerea TVA-ului pierdut, fără să se verifice dacă furnizorul s-a reînregistrat ulterior — legea permite recuperarea deducerii după reînregistrare, prin decontul curent sau unul ulterior.
- Se omite verificarea directă pe Registrul public ANAF al codurilor de TVA anulate înainte de a încheia o tranzacție cu un furnizor nou sau mai puțin cunoscut.

## Ce face iConta.eu

Acest subiect ține de perspectiva **cumpărătorului** care verifică statutul de TVA al unui furnizor — o temă diferită de declarația D311, funcționalitatea cercetată pentru acest ghid, care privește obligația de raportare a **firmei căreia i s-a anulat codul de TVA**, ca vânzător. Nu am găsit în aplicație o funcționalitate dedicată care să verifice automat, la salvarea unui partener sau la introducerea unei facturi, dacă furnizorul respectiv are codul de TVA anulat conform art.316 alin.(11) — verificarea rămâne, astăzi, un pas manual, pe Registrul public al ANAF.

[iConta.eu](/)
