---
title: "Cum verific SAF-T cu D300?"
description: "De ce D300 și SAF-T (D406) pot avea cifre diferite fără să fie o eroare, și ce verificare există efectiv între ele."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific SAF-T cu D300?

D300 (decontul de TVA) și D406 (fișierul standard de control fiscal, SAF-T) au surse comune — facturile și notele contabile ale firmei — dar structuri și scopuri diferite: unul e o declarație fiscală agregată pe rânduri de TVA, celălalt e un export detaliat, tranzacție cu tranzacție, al evidenței contabile. „Verificarea" lor una față de alta nu e un instrument standard, ci o comparație de coerență pe care contabilul o face pe baza înțelegerii celor două structuri.

## Temeiul legal

::: ghid-temei
„Persoanele înregistrate conform art. 316 trebuie să depună la organele fiscale competente, pentru fiecare perioadă fiscală, un decont de taxă [...]"
— Codul fiscal (Legea 227/2015), art. 323 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- D300 se depune pe fiecare perioadă fiscală, conform art. 323 CF, cu sumele agregate de TVA colectată/dedusă pe rândurile din structura oficială a decontului.
- D406 (SAF-T) e o obligație declarativă distinctă, cu propriul temei (OPANAF privind aprobarea structurii fișierului standard de control fiscal) și propria periodicitate — un export detaliat al tranzacțiilor (facturi de vânzare, facturi de achiziție, plăți, mișcări de bunuri), nu un decont de TVA agregat.
- Ambele documente pornesc, în esență, din aceleași facturi ale firmei — dar D300 le agregă pe rânduri de TVA, în timp ce SAF-T le detaliază document cu document, cu informații suplimentare (linii de produs, coduri de taxă la nivel de linie).

## Ce se greșește în practică

- Se așteaptă o egalitate perfectă între o cifră din D300 și o cifră din SAF-T, ignorând faptul că cele două documente pot avea perioade de raportare sau granularități diferite.
- Se tratează o divergență de sumă ca fiind automat o eroare, fără să se verifice mai întâi dacă provine dintr-o diferență legitimă de structură (de exemplu, o operațiune care apare defalcat pe mai multe linii în SAF-T, dar agregat pe un singur rând în D300).
- Se presupune că o aplicație de contabilitate „reconciliază" automat cele două declarații — o astfel de verificare presupune compararea a două structuri XML complet diferite, nu doar o scădere de totaluri.

## Ce face iConta.eu

iConta.eu generează atât D300, cât și D406 (SAF-T) din aceeași sursă de date — facturile și notele contabile introduse în aplicație — ceea ce reduce riscul ca cele două declarații să diveargă din cauza unor date diferite introduse de două ori. Însă aplicația **nu are un instrument dedicat, automat, de comparare a D300 cu SAF-T** — nu există un ecran sau un raport care să confrunte explicit cifrele celor două declarații și să semnaleze discrepanțe. Contabilul care vrea să verifice coerența celor două documente trebuie să compare manual sumele relevante, ținând cont de diferența de structură dintre un decont agregat pe rânduri de TVA și un export detaliat tranzacție cu tranzacție.

[iConta.eu](/)
