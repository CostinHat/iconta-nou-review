---
title: "Cum verific dacă ANAF a validat factura electronică?"
description: Cum se traduce validarea ANAF a unei facturi electronice în stările tehnice folosite de iConta.eu și ce înseamnă, concret, "verdict favorabil".
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum verific dacă ANAF a validat factura electronică?

"Validarea" unei facturi de către ANAF nu este un termen definit ca atare în lege, cu o durată proprie — legea vorbește de aplicarea semnăturii electronice a Ministerului Finanțelor, care atestă primirea facturii în sistem. În practică, pentru o factură pe care ați emis-o și ați trimis-o, acest moment se traduce printr-un verdict primit de la ANAF în urma interogării stadiului trimiterii.

## Temeiul legal

::: ghid-temei
"În situaţia în care factura electronică transmisă respectă structura prevăzută la alin. (1), se aplică semnătura electronică a Ministerului Finanţelor şi se comunică de îndată destinatarului. Aplicarea semnăturii electronice a Ministerului Finanţelor atestă primirea acesteia în sistemul naţional privind factura electronică RO e-Factura."
— OUG 120/2021, art. 4 alin. (4)
:::

Legea nu descrie un proces de "validare" cu pași și durată proprie, ci un rezultat: dacă factura respectă structura cerută, se aplică semnătura MF, iar acest fapt atestă primirea în sistem. Când structura nu e respectată, legea prevede că emitentul primește un mesaj cu erorile identificate (art. 4 alin. (5)), fără să enumere coduri de eroare.

În fluxul tehnic urmărit de o aplicație precum iConta.eu, factura trece, după încărcare, printr-o etapă de interogare periodică a stadiului la ANAF, până la un verdict terminal: fie favorabil (echivalentul, pentru firma emitentă, al confirmării descrise de lege), fie nefavorabil. Cât timp verdictul nu a sosit, factura rămâne "în prelucrare" — asta nu înseamnă respingere, ci doar că răspunsul definitiv nu a fost încă primit.

## Ce se greșește în practică

- Se așteaptă o confirmare "instant" a validării, imediat după încărcarea facturii — deși legea vorbește de comunicare "de îndată" către destinatar, momentul la care verdictul e disponibil emitentului depinde de procesarea internă a ANAF, care nu are un termen legal documentat.
- Se interpretează starea "în prelucrare" ca fiind deja un eșec sau o problemă, deși ea înseamnă doar că ANAF nu a dat încă un răspuns definitiv.
- Se confundă validarea structurală (dacă factura e bine formată) cu validarea de fond a conținutului — legea și fluxul tehnic tratează doar rezultatul transmis de ANAF, nu criteriile de conținut pe care ANAF le verifică intern.

## Ce face iConta.eu

iConta.eu interoghează automat ANAF, la fiecare 30 de minute, pentru stadiul fiecărei facturi emise care așteaptă un verdict. Când ANAF răspunde cu un verdict favorabil, aplicația descarcă recipisa, calculează amprenta (hash) fișierului XML semnat din arhivă și marchează factura ca finalizată — acesta este, din punct de vedere tehnic, momentul în care puteți considera factura "validată".

Trebuie spus onest: durata reală până la un verdict terminal la ANAF nu este documentată public de ANAF și nu apare specificată în niciun act normativ verificat pentru această funcționalitate. iConta.eu nu poate promite și nu promite un termen fix de validare — doar interoghează periodic și raportează exact ce răspunde ANAF, la fiecare rulare de interogare.

[iConta.eu](/)
