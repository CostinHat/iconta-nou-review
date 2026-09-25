---
title: "Cum se contabilizează plățile prin PayPal?"
description: "Regula contabilă de bază pentru încasările și plățile derulate prin PayPal: ce document justificativ stă la baza înregistrării și cum se tratează comisionul reținut."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează plățile prin PayPal?

PayPal nu are un regim contabil special în legislația românească — nu există un act normativ care să menționeze explicit acest procesator de plăți. Din punct de vedere fiscal, o încasare sau o plată prin PayPal e tratată la fel ca orice altă operațiune derulată printr-un cont — cu o particularitate: contul PayPal nu e un cont bancar clasic, iar extrasul lui e documentul justificativ pe baza căruia se înregistrează operațiunea.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ.
(2) Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea 82/1991 (legea contabilității), art. 6 alin. (1)-(2) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Nu există un temei ANAF care să numească PayPal, Stripe sau alt procesator de plăți — regula generală de mai sus e cea care guvernează orice astfel de operațiune:

- **Documentul justificativ** e extrasul de cont PayPal (sau raportul de tranzacții descărcat din contul PayPal), care atestă suma încasată/plătită și data operațiunii — la fel cum extrasul bancar stă la baza înregistrării unei încasări bancare.
- **Comisionul reținut de PayPal** la fiecare tranzacție e o cheltuială distinctă (cont 627 „Cheltuieli cu serviciile bancare și asimilate" sau echivalent), nu se scade „net" din încasare fără evidențiere separată — suma facturată către client trebuie să apară integral ca venit, iar comisionul ca o cheltuială aparte.
- **Contul PayPal însuși** se asimilă, contabil, unui cont curent la o instituție de plată (cont 5125 „Sume în curs de decontare" sau un analitic distinct de 512, în funcție de politica contabilă a entității) — nu se confundă cu casieria (5311), pentru că nu e numerar fizic.

## Ce se greșește în practică

- Se înregistrează în contabilitate doar suma netă primită în cont (după reținerea comisionului PayPal), fără să se evidențieze separat venitul brut și cheltuiala cu comisionul.
- Se tratează soldul din contul PayPal ca fiind în casierie (5311), deși nu e numerar fizic, ci o sumă în curs de decontare la un intermediar de plăți.
- Se omite reconcilierea periodică între extrasul PayPal și contul contabil — mai ales când banii stau o vreme în contul PayPal înainte de a fi transferați în contul bancar al firmei.

## Ce face iConta.eu

iConta.eu oferă contabilitate generală — nu are, la data acestui ghid, o integrare dedicată cu PayPal (import automat de extrase sau reconciliere automată a comisioanelor). Operațiunile derulate prin PayPal se introduc manual în aplicație, pe baza extrasului descărcat din contul PayPal, exact ca orice altă operațiune bancară sau de casă introdusă de contabil.

[iConta.eu](/)
