---
title: "Cum se contabilizează încasările prin Stripe?"
description: Contabilizarea unei încasări prin Stripe nu e o funcție automată în iConta.eu, ci o înregistrare manuală în două pași — sumă netă în bancă, comision ca cheltuială — pornind de la extrasul de cont.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se contabilizează încasările prin Stripe?

Contabilizarea unei încasări prin Stripe are două componente care nu trebuie amestecate: suma efectiv intrată în contul bancar al firmei (netă, după comision) și comisionul reținut de Stripe (o cheltuială separată, deductibilă). Factura emisă către client rămâne, contabil, la valoarea brută.

## Temeiul legal

::: ghid-temei
„Sumele virate sau depuse la bănci ori prin mandat poștal, pe bază de documente prezentate entității și neapărute încă în extrasele de cont, se înregistrează distinct în contabilitate (contul 5125 «Sume în curs de decontare»)." — OMFP 1802/2014, Reglementările contabile, pct. 302 alin. (2)

„Cu ajutorul acestui cont se ține evidența cheltuielilor cu serviciile bancare și asimilate. În debitul contului 627 [...] se înregistrează: – valoarea serviciilor bancare și asimilate plătite (471, 512)." — OMFP 1802/2014, Reglementările contabile, funcțiunea contului 627 „Cheltuieli cu serviciile bancare și asimilate"
:::

Schematic, pentru o factură de 1.000 lei, cu un comision Stripe ipotetic de, să spunem, 30 lei (comisionul real depinde de contractul cu Stripe și nu e o mărime fixă normată legal):

- **Dacă se ține o evidență intermediară** (client plătește, dar decontarea nu a apărut încă în extras): suma brută trece prin **5125 „Sume în curs de decontare"**, în corespondență cu contul de clienți (4111).
- **La decontarea efectivă** (extrasul arată virarea Stripe): suma netă (970 lei, în exemplul de mai sus) intră în **5121 „Conturi la bănci în lei"**, pe seama sumei aflate în 5125.
- **Comisionul** (30 lei, în exemplul de mai sus) se înregistrează ca o cheltuială, în **627 „Cheltuieli cu serviciile bancare și asimilate"** (sau, alternativ, **622 „Cheltuieli privind comisioanele și onorariile"** — reglementările contabile definesc ambele conturi generic, fără să prevadă explicit care e „corect" pentru comisionul unui procesator de plăți online; alegerea între ele e o convenție internă de firmă).

Important: valoarea de referință pentru reconciliere rămâne factura pe brut (1.000 lei, în exemplu), nu suma netă din extras. Dacă se contabilizează încasarea direct pe suma netă, ca și cum ar reprezenta toată valoarea facturii, apare o diferență nereconciliată în soldul clientului, egală exact cu comisionul.

## Ce se greșește în practică

- Se contabilizează suma netă din extras ca fiind întreaga încasare a facturii, fără să se separe comisionul — rezultă solduri de clienți care nu se sting corect.
- Se omite complet înregistrarea comisionului ca o cheltuială (627 sau 622), tratându-l ca pe o simplă „lipsă" din contul bancar, nedocumentată — comisionul e o cheltuială reală și trebuie să apară în contabilitate pentru a fi corect calculată deductibilitatea.
- Se așteaptă generarea automată a acestor înregistrări din aplicație, pe baza unei presupuse integrări cu Stripe — fără o sursă de date (API, webhook sau fișier de decontare) care să citească automat tranzacțiile Stripe, contabilizarea rămâne manuală.

## Ce face iConta.eu

iConta.eu nu are, azi, o integrare automată care să citească tranzacțiile sau decontările Stripe — funcționalitatea de link de plată pe factură a fost închisă (decizie din 06.09.2026: „nu se integrează niciun procesator — fluxul real e transfer bancar, confirmat din extras"), iar butonul aferent a fost scos din interfață. Contabilizarea încasărilor prin Stripe se face manual: suma netă din extras se înregistrează în 5121 (eventual prin 5125, pentru intervalul de decontare), iar comisionul se înregistrează separat, în 627 sau 622, conform politicii contabile a firmei.

[iConta.eu](/)
