---
title: "Cum verific dacă o factură a fost transmisă corect în e-Factura?"
description: Ce înseamnă tehnic "transmisă și validată cu succes" în RO e-Factura, ce stări parcurge o factură emisă și cum e verificată corectitudinea transmiterii în iConta.eu.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum verific dacă o factură a fost transmisă corect în e-Factura?

O factură emisă și trimisă spre ANAF nu are un singur moment "transmis" — trece prin mai multe etape, de la încărcarea propriu-zisă până la verdictul final al sistemului. "Transmisă corect" înseamnă, tehnic, că factura a ajuns la un verdict favorabil, nu doar că a fost trimisă către ANAF.

## Temeiul legal

::: ghid-temei
"În situaţia în care factura electronică transmisă respectă structura prevăzută la alin. (1), se aplică semnătura electronică a Ministerului Finanţelor şi se comunică de îndată destinatarului. Aplicarea semnăturii electronice a Ministerului Finanţelor atestă primirea acesteia în sistemul naţional privind factura electronică RO e-Factura."
— OUG 120/2021, art. 4 alin. (4)
:::

Legea leagă confirmarea de aplicarea semnăturii electronice a Ministerului Finanțelor pe factura validată structural — asta e, în sensul legii, dovada că factura a fost primită și acceptată în sistemul RO e-Factura.

O factură emisă parcurge, în evidența internă a aplicației, o succesiune de stări: se pregătește, apoi se încarcă în SPV (upload reușit), apoi rămâne "în prelucrare" cât timp ANAF nu a dat un răspuns definitiv, iar la final ajunge fie la verdictul favorabil ("ok"), fie la unul nefavorabil ("nok"). Doar verdictul favorabil, obținut după interogarea periodică a stadiului la ANAF, înseamnă transmitere reușită și validată — nu faptul că factura a fost, la un moment dat, încărcată cu succes în sistem.

Un aspect important: fluxul descris aici privește exclusiv facturile pe care firma dumneavoastră le-a **emis și trimis** către ANAF. Facturile primite de la furnizori, prin e-Factura, urmează un alt flux (cu propriile stări), separat de cel discutat aici.

## Ce se greșește în practică

- Se consideră transmiterea "reușită" în momentul în care factura a fost încărcată în SPV (upload confirmat), fără a mai urmări dacă ANAF a dat, ulterior, un verdict favorabil sau nefavorabil. Un upload reușit nu e o validare — e doar pasul care deschide calea către validare.
- Se ignoră faptul că, între încărcare și verdictul final, poate trece un interval în care factura e "în prelucrare" la ANAF — un interval a cărui durată nu este stabilită legal.
- Se confundă starea unei facturi emise, aflate în curs de validare la ANAF, cu starea unei facturi primite de la un furnizor — sunt fluxuri diferite, cu logici diferite.

## Ce face iConta.eu

iConta.eu interoghează periodic ANAF (la fiecare 30 de minute) pentru stadiul fiecărei facturi emise care a fost deja încărcată în SPV și e încă în așteptarea unui verdict. La primirea unui verdict favorabil de la ANAF, aplicația descarcă automat recipisa (arhiva cu documentul semnat), calculează amprenta (hash) a fișierului XML semnat din interiorul recipisei și marchează factura ca finalizată cu succes. Această combinație — verdict favorabil primit de la ANAF + recipisă descărcată — este, tehnic, ce înseamnă "transmisă și validată" pentru o factură emisă prin iConta.eu.

Menționăm onest o limitare: interogarea periodică rulează pe intervale de 30 de minute, deci confirmarea automată a unui verdict nu e instantanee — poate exista o întârziere de până la un ciclu de interogare față de momentul real în care ANAF a emis verdictul.

[iConta.eu](/)
