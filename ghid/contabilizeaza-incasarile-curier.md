---
title: Cum se contabilizează încasările prin curier?
description: Ramburs-ul colectat de curier și decontat ulterior firmei nu are un flux automat de reconciliere în iConta.eu — se înregistrează manual, pe baza documentelor de decontare ale curierului.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se contabilizează încasările prin curier?

Când marfa se livrează cu ramburs (plata se colectează de curier la livrare, în numele firmei), banii nu ajung direct de la client în contul firmei — trec mai întâi prin curier, care îi decontează ulterior, de regulă periodic și cumulat pe mai multe comenzi, reținând propriul comision. În iConta.eu, reconcilierea bancară automată nu are un flux dedicat pentru acest canal — încasarea se înregistrează manual, pe baza documentelor de decontare puse la dispoziție de curier.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ."
— Legea contabilității nr. 82/1991, art. 6 alin. (1)
:::

::: ghid-temei
„Factura este document justificativ care stă la baza înregistrării în contabilitate a operațiunilor economice. Pentru operațiunile economice pentru care, conform prevederilor Codului fiscal, nu există obligația întocmirii facturii, înregistrarea în contabilitate a acestora se efectuează pe baza contractelor încheiate între părți și a documentelor financiar-contabile sau bancare care să ateste acele operațiuni, cum sunt: [...] extras de cont bancar, notă de contabilitate etc."
— OMFP 2634/2015, Anexa 1 „Norme generale", pct. 25
:::

Legea cere document justificativ pentru fiecare operațiune, dar nu impune o formă anume de procesare tehnică a decontărilor de la curieri — asta ține de fluxul aplicației, tratat mai jos.

## De ce nu e un flux automat în iConta.eu

Motorul de reconciliere bancară din iConta.eu caută, pe fiecare linie din extrasul bancar, un CUI de partener în descriere, pentru a o potrivi cu facturile deschise ale acelui partener. O decontare de la curier ajunge în extras ca o singură sumă cumulată, cu textul curierului (nu al clientului final) în descriere — motorul nu are de unde extrage CUI-ul fiecărui client care a plătit ramburs, deci linia respectivă nu se potrivește automat cu nicio factură.

În plus, decontarea de la curier e de regulă **netă de comisionul de colectare** reținut de curier, deci suma din extras nici nu coincide cu totalul facturilor livrate cu ramburs în perioada respectivă.

La data acestui ghid, iConta.eu nu are un modul dedicat de import al borderourilor de decontare de la curieri, care să despartă automat suma cumulată pe facturile individuale și să separe comisionul de colectare ca o cheltuială distinctă. O astfel de extensie a reconcilierii bancare este avută în vedere pentru viitor, dar nu e construită azi.

## Ce se greșește în practică

- Se așteaptă ca suma decontată de curier să apară automat potrivită pe facturile livrate cu ramburs, la fel ca o încasare directă cu CUI vizibil.
- Se contabilizează suma netă primită de la curier direct pe o singură factură, fără să se separă comisionul de colectare.
- Se pierde legătura dintre borderoul de livrări ramburs al curierului (care arată ce comenzi au fost efectiv colectate) și suma cumulată din extrasul bancar, dacă cele două documente nu se păstrează împreună.

## Ce face iConta.eu

Reconcilierea bancară automată (`core/reconciliere.py`) potrivește linii de extras pe facturi deschise ale unui partener, pe baza CUI-ului din descrierea liniei — mecanism care nu se aplică la o decontare cumulată de la curier, fără CUI de client individual. Pentru acest canal, iConta.eu nu oferă azi un import dedicat de borderouri de curier; încasarea prin ramburs se înregistrează manual, ca notă de jurnal, pe baza documentului de decontare al curierului (borderou/situație de decontare), cu separarea explicită a comisionului reținut de curier ca cheltuială.

[iConta.eu](/)
