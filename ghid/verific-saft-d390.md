---
title: "Cum verific SAF-T cu D390?"
description: "De ce D390 și SAF-T (D406) pot arăta diferit fără să fie o eroare, și ce verificare există efectiv între cele două."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific SAF-T cu D390?

D390 (declarația recapitulativă pentru operațiuni intracomunitare) și D406 (SAF-T) pornesc, în multe cazuri, din aceleași facturi — dar au scopuri și structuri complet diferite. D390 raportează operațiunile intracomunitare pe cod de tip (L/T/A/P/S/R) și pe partener, cu clasificări care pot fi corectate manual; SAF-T exportă detaliat, document cu document, toate facturile de vânzare și achiziție ale firmei, indiferent de natura lor. O „verificare" între ele nu e un instrument automat, ci o comparație de coerență.

## Temeiul legal

::: ghid-temei
„Se completează cu tranzacţiile intracomunitare efectuate [...]"
— OPANAF 705/2020, Anexa 2, Instrucțiuni pct. 1 (sursă: anaf_surse/opanaf_705_2020_d390.txt)
:::

- D390 se depune numai pentru lunile în care ia naștere exigibilitatea taxei pentru operațiuni intracomunitare — nu se depune pe zero.
- SAF-T (D406) e o obligație declarativă separată, cu structură XML proprie (secțiunile Header, MasterFiles, SourceDocuments — printre care SalesInvoices și PurchaseInvoices), care exportă liniile reale ale tuturor facturilor din perioada raportată, indiferent dacă operațiunea e sau nu intracomunitară.
- Codurile de clasificare specifice D390 (L, T, A, P, S, R) nu au un corespondent direct în structura SAF-T — SAF-T raportează facturile cu codurile lor de taxă (cotă TVA, tip de taxă), nu cu codurile de operațiune intracomunitară ale D390.

## Ce se greșește în practică

- Se așteaptă ca totalul operațiunilor intracomunitare din D390 să coincidă exact, linie cu linie, cu ceva din SAF-T — cele două documente au granularități și scopuri diferite, nu sunt construite pentru a fi comparate cifră cu cifră.
- Se tratează orice diferență de sumă între cele două rapoarte ca fiind automat o eroare, fără să se verifice mai întâi dacă provine dintr-o clasificare manuală (reclasificare L→P, de exemplu) reflectată în D390, dar care nu are un corespondent explicit în structura SAF-T.
- Se presupune că o divergență între D390 și SAF-T poate fi identificată automat de aplicație — o astfel de comparație ar presupune maparea manuală a două structuri declarative diferite, nu o simplă scădere de totaluri.

## Ce face iConta.eu

D390 și D406 (SAF-T) din iConta.eu pornesc din aceeași sursă de facturi ale firmei, ceea ce reduce riscul ca cele două declarații să diveargă din cauza unor date introduse separat. Pentru operațiunile intracomunitare clasificate manual în D390 (reclasificări de tip L→T/P/R, achiziții A→S sau linii pur manuale, prin panoul de clasificare), aplicația **nu are un instrument dedicat de comparare automată cu SAF-T** — nu există un ecran sau un raport care să confrunte explicit cifrele celor două declarații. Controlul încrucișat existent în aplicație verifică D390 doar în raport cu evidența contabilă validată și cu D300 depus, și doar pentru operațiuni de tip bunuri (L/A) — nu acoperă nici servicii/triangulație (P/S/T/R), nici comparația cu SAF-T. Orice verificare de coerență între D390 și SAF-T rămâne, la acest moment, o sarcină manuală a contabilului.

[iConta.eu](/)
