---
title: "Cum se reconciliază tranzacțiile Revolut cu contabilitatea"
description: "De ce extrasul de cont Revolut are aceeași valoare de document justificativ ca extrasul unei bănci tradiționale, în reconcilierea bancară."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se reconciliază tranzacțiile Revolut cu contabilitatea

Un cont Revolut folosit pentru activitatea firmei nu are un regim contabil special față de un cont bancar "clasic" — legea contabilă nu face distincție după emitentul instrumentului de plată. Ce contează e ca fiecare operațiune din extrasul contului să fie consemnată pe baza unui document justificativ, exact ca la orice altă bancă.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ.
(2) Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea contabilității nr. 82/1991, art. 6 (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Legea contabilă nu menționează Revolut sau alte instituții de plată/monedă electronică drept categorie separată — regula de la art. 6 se aplică identic, indiferent de furnizorul contului. Extrasul de cont emis de Revolut e documentul justificativ pentru operațiunile bancare respective, la fel cum ar fi extrasul unei bănci tradiționale.

- **Fiecare tranzacție din extrasul Revolut trebuie să aibă un document justificativ corespunzător** (factură, chitanță, contract) care să explice operațiunea — extrasul confirmă mișcarea de bani, nu explică singur natura ei.
- **Reconcilierea bancară** presupune potrivirea fiecărei sume din extras cu documentul-sursă aferent (factură emisă, factură primită, transfer intern), indiferent dacă banca e Revolut, o bancă românească sau alta.
- **Particularitățile tehnice ale Revolut** (conturi multi-valută, carduri virtuale multiple, conversii valutare instant) nu schimbă principiul de bază — fiecare astfel de operațiune (inclusiv comisioanele de conversie valutară) rămâne o operațiune economico-financiară care trebuie consemnată separat, cu propriul document justificativ.

## Ce se greșește în practică

- Se tratează Revolut ca "bani de buzunar" ai firmei, fără reconciliere riguroasă, presupunând greșit că regimul contabil ar fi mai relaxat decât la o bancă tradițională — legea nu face această distincție.
- Se omit comisioanele de conversie valutară din extrasul Revolut la reconciliere, tratând doar suma netă ca operațiune relevantă, deși fiecare comision e o cheltuială separată care trebuie înregistrată.
- Se amestecă operațiuni personale cu cele ale firmei pe același cont Revolut, ceea ce complică grav reconcilierea și poate ridica probleme de justificare a naturii economice a fiecărei tranzacții.

## Ce face iConta.eu

Modulul de parsare a extraselor bancare din iConta.eu (`core/banca_parser.py`) importă extrase de cont pentru reconciliere pe baza formatului fișierului furnizat, fără un conector dedicat specific pentru Revolut — dacă extrasul Revolut poate fi exportat într-un format tabelar/CSV compatibil, importul și reconcilierea cu facturile emise/primite funcționează la fel ca pentru orice altă bancă, dar potrivirea automată depinde de structura fișierului exportat de Revolut, verificată de utilizator la import.

[iConta.eu](/)
