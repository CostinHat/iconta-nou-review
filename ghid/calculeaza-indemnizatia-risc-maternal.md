---
title: "Cum se calculează indemnizația de risc maternal?"
description: "Cota de 75% aplicată bazei de calcul pentru indemnizația de risc maternal, suportată integral din Fondul național unic de asigurări sociale de sănătate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează indemnizația de risc maternal?

Concediul de risc maternal nu e un concediu medical „obișnuit" — el intervine când angajatorul nu poate elimina un risc la locul de muncă pentru o salariată gravidă, lăuză sau care alăptează, și nu poate nici modifica programul, nici realoca postul. Indemnizația aferentă are un cuantum fix, stabilit direct de lege.

## Temeiul legal

::: ghid-temei
„(2) Pe durata concediului de risc maternal se acordă o indemnizație de risc maternal care se suportă integral din bugetul Fondului național unic de asigurări sociale de sănătate.
(3) Concediul și indemnizația de risc maternal se acordă fără condiție de stagiu de asigurare.
(4) Cuantumul indemnizației prevăzute la alin. (2) reprezintă 75% din baza de calcul stabilită conform prevederilor art. 10."
— OUG nr. 158/2005 privind concediile și indemnizațiile de asigurări sociale de sănătate, art. 31 alin. (2), (3), (4) (sursă: anaf_surse/oug_158_2005_consolidat.txt)
:::

Elementele de calcul, potrivit textului:

- Cuantumul indemnizației este **75% din baza de calcul** stabilită conform art. 10 din aceeași ordonanță (media veniturilor lunare din ultimele 6 luni asigurate, în limitele legale) — nu 100%, cum se aplică la unele concedii medicale speciale (de exemplu tuberculoză sau boli cardiovasculare).
- Indemnizația se suportă **integral din bugetul FNUASS**, nu din fondul de salarii al angajatorului — angajatorul plătește indemnizația salariatei, dar o recuperează de la casa de asigurări de sănătate.
- Dreptul la concediu și indemnizație se acordă **fără condiție de stagiu de asigurare** — spre deosebire de alte tipuri de concedii medicale, care pot cere un stagiu minim de cotizare, la risc maternal acest prag nu se aplică.
- Concediul se poate acorda integral sau fracționat, pe o perioadă de maximum 120 de zile, pe baza certificatului medical eliberat de medicul de familie sau specialist, potrivit OUG 96/2003.

## Ce se greșește în practică

- Se calculează indemnizația la 100% din baza de calcul, ca la alte concedii medicale speciale, în loc de cota specifică de 75%.
- Se cere stagiu minim de asigurare pentru acordarea concediului de risc maternal, deși legea îl exceptează explicit de la această condiție.
- Se confundă concediul de risc maternal cu concediul de maternitate sau cu cel pentru sarcină și lăuzie, care au reguli și cote de calcul diferite.

## Ce face iConta.eu

La data acestui ghid, iConta.eu recunoaște codul de concediu medical „15" (risc maternal) în modulul de salarizare, cu cota de calcul de 75% aplicată automat (`core/salarizare.py`) și raportarea corespunzătoare în D112, unde suma e marcată distinct cu indicativul „RM" (`core/d112.py`, `core/nomenclator_cm.py`). Sumele reprezentând indemnizația de risc maternal sunt tratate ca neimpozabile, conform art. 62 lit. c) din Codul fiscal. Introducerea certificatului medical și verificarea eligibilității salariatei pentru acest tip de concediu rămân, însă, o operațiune manuală a persoanei care întocmește statul de plată.

[iConta.eu](/)
