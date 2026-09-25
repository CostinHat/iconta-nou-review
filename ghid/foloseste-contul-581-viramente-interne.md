---
title: "Când se folosește contul 581 Viramente interne?"
description: "Rolul contului 581 Viramente interne în evidența transferurilor de disponibilități între conturile de trezorerie ale firmei, conform reglementărilor contabile."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când se folosește contul 581 Viramente interne?

Contul 581 „Viramente interne" nu reprezintă o operațiune economică propriu-zisă, ci un cont tehnic, tranzitoriu: el servește exclusiv la urmărirea mutării banilor între diferitele conturi de trezorerie ale aceleiași firme (casă, bancă, acreditive), astfel încât fiecare transfer să fie vizibil ca pereche „ieșire dintr-un cont — intrare în celălalt".

## Temeiul legal

::: ghid-temei
„GRUPA 58 «VIRAMENTE INTERNE» [...] Contul 581 «Viramente interne» [...] Cu ajutorul acestui cont se ține evidența viramentelor de disponibilități între conturile de trezorerie. Contul 581 «Viramente interne» este un cont de activ. În debitul contului 581 «Viramente interne» se înregistrează: — sumele virate dintr‐un cont de trezorerie în alt cont de trezorerie (512, 531, 541). În creditul contului 581 «Viramente interne» se înregistrează: — sumele intrate într‐un cont de trezorerie din alt cont de trezorerie (512, 531, 541). De regulă, contul nu prezintă sold."
— OMFP 1802/2014, secțiunea Grupa 58 (sursă: anaf_surse/omfp_1802_2014.txt)
:::

- Contul 581 se folosește ori de câte ori banii trec dintr-un cont de trezorerie propriu în altul: ridicare numerar de la bancă (512 → 581 → 5311), depunere numerar la bancă (5311 → 581 → 512), transfer între două conturi bancare, mișcări prin acreditive (541).
- Fiind un cont de activ tranzitoriu, în mod normal el se debitează și se creditează cu aceeași sumă în cadrul aceleiași operațiuni de transfer, astfel încât la final **nu prezintă sold** — dacă rămâne sold pe 581, înseamnă că una dintre cele două note contabile ale transferului nu a fost încă înregistrată.
- Nu se folosește pentru încasări sau plăți către terți (clienți, furnizori, salariați) — acelea trec direct prin conturile de creanțe/datorii corespunzătoare, nu prin 581.

## Ce se greșește în practică

- Se lasă sold pe 581 la finalul lunii, semn că transferul a fost înregistrat doar pe o parte (de exemplu s-a scăzut banca, dar nu s-a majorat casa, sau invers).
- Se folosește contul 581 pentru operațiuni care nu sunt transferuri interne de trezorerie (de exemplu pentru a „parca" temporar o sumă neclarificată provenită de la un terț) — pentru astfel de situații există contul 473 „Decontări din operațiuni în curs de clarificare", nu 581.
- Se dublează înregistrarea unui transfer bancă-bancă prin două conturi 581 diferite fără să se coreleze sumele, ceea ce distorsionează rulajele de trezorerie din balanță.

## Ce face iConta.eu

iConta.eu folosește automat contul 581 pentru operațiunile de transfer intern de disponibilități: la ridicarea de numerar de la bancă și depunerea de numerar la bancă, aplicația generează perechile de note contabile prin 581 (de exemplu `5311 = 581` pentru ridicare, `581 = 5311` pentru depunere), la fel ca la transferurile de sume între casă și bancă gestionate din modulul de casierie. Astfel, contul rămâne, ca și în regula legală de mai sus, fără sold la final, iar contabilul nu trebuie să compună manual cele două note ale fiecărui transfer.

[iConta.eu](/)
