---
title: "Mai poate o firmă în lichidare să plătească furnizorii?"
description: "Ce operațiuni comerciale poate face o societate aflată în procedură de lichidare, potrivit Legii societăților 31/1990."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Mai poate o firmă în lichidare să plătească furnizorii?

Dizolvarea unei societăți nu înseamnă că activitatea ei economică se oprește instant — lichidarea e tocmai perioada în care afacerile în curs se termină, creanțele se încasează și datoriile se sting, sub controlul unui lichidator. Plata furnizorilor rămași din perioada anterioară dizolvării intră exact în acest cadru.

## Temeiul legal

::: ghid-temei
„În afară de puterile conferite de asociați, cu aceeași majoritate cerută pentru numirea lor, lichidatorii vor putea: a) să stea în judecată în numele societății; [...] b) să execute și să termine operațiunile de comerț referitoare la lichidare; [...] f) să contracteze obligații cambiale, să facă împrumuturi neipotecare și să îndeplinească orice alte acte necesare."
— Legea 31/1990 a societăților, art. 255 alin. (1) lit. a), b) și f) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

- Odată numit, lichidatorul **preia conducerea societății** de la administratori și are, printre altele, puterea de a „executa și termina operațiunile de comerț referitoare la lichidare" — ceea ce include stingerea datoriilor curente, deci și plata furnizorilor.
- Legea permite explicit lichidatorului să „îndeplinească orice alte acte necesare" lichidării, alături de puterile enumerate expres, atâta vreme cât nu sunt operațiuni comerciale noi, nelegate de scopul lichidării.
- Există totuși o limită: „Lichidatorii care întreprind noi operațiuni comerciale ce nu sunt necesare scopului lichidării sunt răspunzători personal și solidar de executarea lor" (art. 255 alin. (3)) — plata unei datorii existente către un furnizor e o operațiune necesară lichidării; angajarea unor contracte comerciale noi, fără legătură cu finalizarea afacerilor curente, nu e.
- Prioritatea plăților din fondurile obținute din vânzarea bunurilor societății dizolvate merge întâi către taxe, timbre și cheltuielile de conservare/administrare a bunurilor și remunerația lichidatorului (art. 255^1), abia apoi urmând restul creditorilor, inclusiv furnizorii, potrivit ordinii legale de îndestulare a creditorilor.

## Ce se greșește în practică

- Se presupune că, odată intrată în dizolvare/lichidare, firma nu mai poate face nicio plată — de fapt, stingerea obligațiilor existente (inclusiv către furnizori) rămâne nu doar permisă, ci parte din atribuțiile lichidatorului.
- Se confundă „operațiuni de comerț necesare lichidării" cu interdicția de a începe activități economice noi — cele două nu sunt același lucru, iar lichidatorul răspunde personal doar pentru operațiuni noi, nenecesare scopului lichidării.
- Nu se respectă ordinea de prioritate a plăților din fondurile rezultate din vânzarea activelor (taxe și cheltuieli de lichidare întâi), plătindu-se furnizorii înaintea acestora.
- Se ignoră faptul că, până la numirea lichidatorului, administratorii continuă să-și exercite atribuțiile (cu excepția celor prevăzute la art. 233), deci plățile curente pot continua și în intervalul dintre hotărârea de dizolvare și numirea efectivă a lichidatorului.

## Ce face iConta.eu

iConta.eu are un modul dedicat lichidării (`core/lichidare.py`), dar acesta acoperă doar valorificarea activelor (nota de vânzare, cu descărcarea din gestiune și TVA aferentă) și partajul final către asociați (inclusiv impozitul pe câștigul din lichidare, 10% conform art. 97 alin. (5) din Codul fiscal). Nu am găsit însă în cod vreo funcție specifică pentru **gestiunea priorității plăților către creditori** în cursul lichidării (ordinea taxe/cheltuieli de lichidare înaintea furnizorilor, conform art. 255^1) — evidența operațiunilor curente (facturi, plăți către furnizori) rămâne disponibilă ca pentru orice firmă activă, prin fluxurile obișnuite ale aplicației, dar deciziile specifice lichidării — ce se plătește, în ce ordine, cu ce autorizare — rămân în sarcina lichidatorului și a contabilului.

[iConta.eu](/)
