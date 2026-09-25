---
title: "Diferențele de curs la casieria în valută 2026"
description: "Reevaluarea lunară a casieriei în valută (cont 5314) funcționează la fel ca pentru bancă; la decontări directe prin casierie, o limită reală din iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Diferențele de curs la casieria în valută 2026

Casieria în valută (cont 5314) urmează exact aceleași reguli de diferențe de curs ca disponibilul bancar — e un element monetar, deci se reevaluează lunar la cursul BNR și generează 665/765 la fel ca banca. Nu există în 2026 nicio regulă specială, mai blândă sau mai strictă, pentru casierie față de bancă.

## Temeiul legal

::: ghid-temei
„325. - (1) La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul de schimb al pieței valutare, comunicat de Banca Națională a României din ultima zi bancară a lunii în cauză. Diferențele de curs înregistrate se recunosc în contabilitate la venituri sau cheltuieli din diferențe de curs valutar, după caz."
— OMFP 1802/2014, pct. 325 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Textul pct. 325 vizează „creanțele și datoriile în valută" prin trimitere la elementele monetare de la pct. 315 alin. (1), care includ explicit **disponibilitățile bănești** — deci și numerarul din casieria în valută, nu doar conturile bancare.
- Regula de semn e cea a unui disponibil: dacă cursul BNR crește față de cursul din evidența casei, apare un câștig (765); dacă scade, o pierdere (665).
- Regula pentru decontare (pct. 322) se aplică la fel dacă apare o mișcare directă prin casă în valută (plată/încasare) la un curs diferit de cel de evidență.
- Nu există, în legislația actuală, un tratament diferit pentru numerarul în valută față de disponibilul bancar în valută — ambele sunt „disponibilități bănești" în sensul pct. 315.

## Ce se greșește în practică

- Se presupune, greșit, că doar contul bancar în valută se reevaluează lunar, iar casieria „se lasă cum e" — omisiune care denaturează rezultatul, mai ales la firme cu numerar în valută semnificativ (turism, transport internațional).
- Se amestecă soldul casei în valută cu soldul bancar în valută într-o singură notă de reevaluare, fără să se distingă clar contul (5314 vs. 5124), complicând ulterior controlul de gestiune al casei.
- Se omite recunoașterea diferenței la o plată/încasare directă în numerar valutar, tratând-o doar ca mișcare de casă, fără componenta de curs.

## Ce face iConta.eu

Pentru **reevaluarea lunară**, ecranul „Operațiuni speciale → Reevaluare valuta" din iConta.eu funcționează corect pentru casierie: câmpul „cont" e text liber, deci accepți 5314 la fel de bine ca 5124, iar motorul (`core/diferente_curs.py`, `reevaluare_sold`) calculează diferența cu aceeași regulă de semn ca pentru bancă. Pentru **decontări directe prin casierie** (o încasare sau plată de creanță/datorie efectuată prin casa în valută), există însă o limită reală: ecranul „Decontare în valută" nu are câmp pentru contul de bancă/casierie, iar backend-ul folosește implicit contul 5124 — deci o decontare care a avut loc de fapt prin 5314 se înregistrează automat pe 5124, greșit, fără niciun avertisment. Dacă lucrezi cu casierie în valută și faci decontări directe prin ea, corectează manual contul din nota generată înainte de a o confirma.

[iConta.eu](/)
