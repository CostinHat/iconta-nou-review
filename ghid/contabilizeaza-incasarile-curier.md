---
title: Cum se contabilizează încasările prin curier?
description: Ramburs-ul colectat de curier și decontat ulterior firmei nu are un flux automat de reconciliere în iConta.eu — se înregistrează manual, pe baza documentelor de decontare ale curierului.
published: 2026-09-23
modified: 2026-10-13
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

::: ghid-temei
„Operațiunile de încasări și plăți în numerar efectuate între persoanele prevăzute la art. 1 alin. (1) și persoane fizice, reprezentând contravaloarea unor livrări ori achiziții de bunuri sau a unor prestări de servicii, dividende, cesiuni de creanțe sau alte drepturi, se efectuează cu încadrarea în plafonul zilnic de 10.000 lei către/de la o persoană.”
— Legea nr. 70/2015, art. 4 alin. (1) (sursă: [Legea nr. 70/2015 pentru întărirea disciplinei financiare privind operațiunile de încasări și plăți în numerar](https://legislatie.just.ro/Public/DetaliiDocument/167088))

„Sunt interzise încasările și plățile fragmentate de la/către o persoană, pentru operațiunile de încasări/plăți în numerar prevăzute la alin. (1), cu o valoare mai mare decât plafonul prevăzut la alin. (1) [...]”
— Legea nr. 70/2015, art. 4 alin. (2) (sursă: [Legea nr. 70/2015 pentru întărirea disciplinei financiare privind operațiunile de încasări și plăți în numerar](https://legislatie.just.ro/Public/DetaliiDocument/167088))
:::

Legea cere document justificativ pentru fiecare operațiune, dar nu impune o formă anume de procesare tehnică a decontărilor de la curieri — asta ține de fluxul aplicației, tratat mai jos.

## Plafonul de numerar la ramburs

Ramburs-ul înseamnă numerar colectat de la client. Pentru clienții persoane fizice — cazul tipic al comerțului online — plafonul din Legea nr. 70/2015 este de **10.000 lei pe zi de la o persoană** (art. 4 alin. (1)), iar fragmentarea unei livrări cu valoare mai mare decât plafonul este interzisă (art. 4 alin. (2)): mai multe comenzi ale aceluiași client în aceeași zi, fiecare sub plafon, dar care cumulate îl depășesc, sunt exact situația vizată. Plafonul de 5.000 lei pe zi de la o persoană (art. 3 alin. (1) lit. a)) privește încasările de la firme, PFA și celelalte entități enumerate la art. 1 alin. (1), nu de la persoane fizice. Legea nu tratează separat situația în care numerarul trece prin firma de curierat — de aceea e prudent ca ramburs-ul să fie urmărit pe client final, nu doar pe decontarea globală a curierului.

## De ce nu e un flux automat în iConta.eu

Reconcilierea bancară automată din iConta.eu caută, pe fiecare linie din extrasul bancar, un CUI de partener în descriere, pentru a o potrivi cu facturile deschise ale acelui partener. O decontare de la curier ajunge în extras ca o singură sumă cumulată, cu textul curierului (nu al clientului final) în descriere — motorul nu are de unde extrage CUI-ul fiecărui client care a plătit ramburs, deci linia respectivă nu se potrivește automat cu nicio factură.

În plus, decontarea de la curier e de regulă **netă de comisionul de colectare** reținut de curier, deci suma din extras nici nu coincide cu totalul facturilor livrate cu ramburs în perioada respectivă.

La data acestui ghid, iConta.eu nu are un modul dedicat de import al borderourilor de decontare de la curieri, care să despartă automat suma cumulată pe facturile individuale și să separe comisionul de colectare ca o cheltuială distinctă. O astfel de extensie a reconcilierii bancare este avută în vedere pentru viitor, dar nu e construită azi.

## Ce se greșește în practică

- Se așteaptă ca suma decontată de curier să apară automat potrivită pe facturile livrate cu ramburs, la fel ca o încasare directă cu CUI vizibil.
- Se contabilizează suma netă primită de la curier direct pe o singură factură, fără să se separă comisionul de colectare.
- Se aplică plafonul de 5.000 lei (încasări de la firme, art. 3 din Legea nr. 70/2015) în locul celui de 10.000 lei de la persoane fizice (art. 4), sau se ignoră cumulul comenzilor aceluiași client din aceeași zi.
- Se pierde legătura dintre borderoul de livrări ramburs al curierului (care arată ce comenzi au fost efectiv colectate) și suma cumulată din extrasul bancar, dacă cele două documente nu se păstrează împreună.

## Ce face iConta.eu

Reconcilierea bancară automată potrivește linii de extras pe facturi deschise ale unui partener, pe baza CUI-ului din descrierea liniei — mecanism care nu se aplică la o decontare cumulată de la curier, fără CUI de client individual. Pentru acest canal, iConta.eu nu oferă azi un import dedicat de borderouri de curier; încasarea prin ramburs se înregistrează manual, ca notă de jurnal, pe baza documentului de decontare al curierului (borderou/situație de decontare), cu separarea explicită a comisionului reținut de curier ca cheltuială. Aplicația nici nu urmărește automat plafonul zilnic de 10.000 lei pe clientul final din spatele unei livrări cu ramburs — verificarea rămâne în sarcina contabilului, mai ales când același client plasează mai multe comenzi.

[iConta.eu](/)
