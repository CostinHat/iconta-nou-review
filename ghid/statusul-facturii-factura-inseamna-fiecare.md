---
title: "Statusul facturii în e-Factura: ce înseamnă fiecare"
description: "Explică toate stările posibile ale unei facturi trimise prin e-Factura și cum le urmărește automat iConta.eu."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Statusul facturii în e-Factura: ce înseamnă fiecare

O factură trimisă prin RO e-Factura trece printr-o succesiune de stări bine definite, de la pregătire până la verdictul final al ANAF. Acest ghid explică fiecare stare și ce declanșează trecerea la următoarea.

Legea numește doar rezultatele-cheie: acceptarea (sigiliul electronic al Ministerului Finanțelor, comunicare imediată) sau respingerea (mesaj cu erorile identificate, de corectat și retrimis). Fluxul intern al aplicației urmărește exact acest traseu, dar cu stări intermediare explicite, pentru ca nicio factură să nu rămână "blocată" fără un status vizibil.

## Temeiul legal

::: ghid-temei
„(4) În situația în care factura electronică transmisă respectă structura prevăzută la alin. (1), se aplică sigiliul electronic al Ministerului Finanțelor și se comunică de îndată destinatarului. Aplicarea sigiliului electronic al Ministerului Finanțelor atestă primirea acesteia în sistemul național privind factura electronică RO e-Factura.”
— OUG nr. 120/2021, art. 4 alin. (4) (sursă: [OUG nr. 120/2021 privind sistemul național RO e-Factura](https://legislatie.just.ro/Public/DetaliiDocument/247243))

„(5) În situația în care factura electronică transmisă nu respectă structura prevăzută la alin. (1), emitentul primește mesaj cu erorile identificate. După corectarea erorilor identificate, factura electronică se transmite în cadrul aceluiași sistem național privind factura electronică RO e-Factura.”
— OUG nr. 120/2021, art. 4 alin. (5) (sursă: [OUG nr. 120/2021 privind sistemul național RO e-Factura](https://legislatie.just.ro/Public/DetaliiDocument/247243))
:::

## Ce se greșește în practică

Greșeala frecventă e tratarea oricărei stări diferite de "ok" ca fiind o respingere definitivă, deși "în prelucrare" e o stare normală, tranzitorie, de așteptare. O altă greșeală e confundarea unui eșec de încărcare (problemă tehnică la trimitere, factura nici n-a ajuns la ANAF) cu o respingere efectivă a conținutului facturii de către ANAF — sunt situații diferite, cu cauze și remedii diferite.

## Ce face iConta.eu

Fiecare trimitere are, în iConta.eu, o singură stare, dintr-o listă fixă. Înainte de încărcare, trimiterea e doar pregătită. După aceea, în ecranul facturii apare una din stările: **eroare la trimitere** (încărcarea către ANAF a eșuat tehnic — factura nici n-a ajuns la ANAF, nu înseamnă respingere de conținut), **încărcată, în prelucrare la ANAF** (încărcare reușită, ANAF a preluat factura — de aici încolo aplicația îi urmărește automat starea), **în prelucrare la ANAF** (ANAF procesează încă, verdictul nu e dat), **blocată la ANAF — verifică în SPV** (starea „în prelucrare” persistă peste un prag intern de 2 zile — prag conservator de produs, nu termen legal ANAF; aplicația semnalează explicit să verifici manual în SPV, în loc să tacă), **trimisă (recipișă primită)** (verdict final favorabil — aplicația descarcă automat recipisa, calculează amprenta SHA-256 a XML-ului semnat și marchează factura finalizată) și **respinsă de ANAF** (verdict final nefavorabil sau răspuns cu „eroare”/„erori” — aplicația descarcă recipisa dacă e disponibilă și păstrează mesajul primit de la ANAF, așa cum a venit).

Aplicația verifică automat la ANAF starea acestor facturi la fiecare 30 de minute (la minutul 07 și la minutul 37 al fiecărei ore); facturile ajunse într-o stare finală (trimisă, respinsă, eroare la trimitere) nu mai sunt verificate. Dacă autentificarea la ANAF eșuează temporar, aplicația nu marchează factura ca respinsă — reîncearcă la verificarea următoare.

[iConta.eu](/)
