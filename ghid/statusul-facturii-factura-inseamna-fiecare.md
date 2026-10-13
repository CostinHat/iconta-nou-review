---
title: "Statusul facturii în e-Factura: ce înseamnă fiecare"
description: "Explică toate stările posibile ale unei facturi trimise prin e-Factura și cum le urmărește automat iConta.eu."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Statusul facturii în e-Factura: ce înseamnă fiecare

O factură trimisă prin RO e-Factura trece printr-o succesiune de stări bine definite, de la pregătire până la verdictul final al ANAF. Acest ghid explică fiecare stare și ce declanșează trecerea la următoarea.

Legea numește doar rezultatele-cheie: acceptarea (semnătura MF, comunicare imediată) sau respingerea (mesaj cu erorile identificate, de corectat și retrimis). Fluxul intern al aplicației urmărește exact acest traseu, dar cu stări intermediare explicite, pentru ca nicio factură să nu rămână "blocată" fără un status vizibil.

## Ce se greșește în practică

Greșeala frecventă e tratarea oricărei stări diferite de "ok" ca fiind o respingere definitivă, deși "în prelucrare" e o stare normală, tranzitorie, de așteptare. O altă greșeală e confundarea unui eșec de încărcare (problemă tehnică la trimitere, factura nici n-a ajuns la ANAF) cu o respingere efectivă a conținutului facturii de către ANAF — sunt situații diferite, cu cauze și remedii diferite.

## Ce face iConta.eu

Fiecare trimitere are, în iConta.eu, o stare unică, dintr-o listă fixă: **pregătit** (rândul creat înainte de upload), **eroare la transmitere** (upload-ul către ANAF a eșuat tehnic — factura nici n-a ajuns la ANAF, nu înseamnă respingere de conținut), **încărcat** (upload reușit, ANAF a preluat factura — de aici încolo intră în lucru cron-ul de urmărire), **în_prelucrare** (ANAF procesează încă, verdict neterminat), **investigație** (starea "în prelucrare" persistă peste un prag intern de 2 zile — prag conservator de produs, nu termen legal ANAF; aplicația semnalează explicit "verifică manual în SPV" în loc să tacă), **ok** (verdict terminal favorabil — aplicația descarcă automat recipisa, calculează SHA-256 al XML-ului semnat și marchează factura finalizată) și **nok** (verdict terminal nefavorabil sau text cu "eroare"/"erori" — aplicația descarcă recipisa dacă e disponibilă și salvează mesajul brut primit de la ANAF).

Aceste stări sunt urmărite automat de un cron care interoghează ANAF la fiecare 30 de minute (orele fixe `:07`/`:37`); stările terminale (ok/nok/eroare_upload) nu mai sunt reinterogate. Dacă tokenul de autentificare la ANAF eșuează temporar, aplicația nu marchează factura ca respinsă — reîncearcă la rularea următoare.

[iConta.eu](/)
