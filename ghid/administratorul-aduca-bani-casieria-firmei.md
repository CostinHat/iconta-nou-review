---
title: "Poate administratorul să aducă bani în casieria firmei?"
description: "Regimul contului 455 vizează acționarii/asociații, nu administratorul ca atare; iar funcționalitatea din iConta pentru această operațiune generează nota prin bancă, nu prin casierie."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Poate administratorul să aducă bani în casieria firmei?

Întrebarea ascunde două lucruri diferite: cine aduce banii (administrator sau asociat) și pe ce cale intră (casierie sau bancă). Ambele contează pentru încadrarea corectă.

## Temeiul legal

::: ghid-temei
„Sumele depuse sau lăsate temporar de către acționari/asociați la dispoziția entității, precum și dobânzile aferente, calculate în condițiile legii, se înregistrează în contabilitate în conturi distincte (contul 4551 «Acționari/asociați - conturi curente», respectiv contul 4558 «Acționari/asociați - dobânzi la conturi curente»)." — OMFP 1802/2014, pct. 349
:::

Textul vorbește explicit despre acționari/asociați, nu despre administrator ca funcție. Dacă administratorul e și asociat (situația obișnuită la un SRL mic), suma pe care o aduce se încadrează la 4551, conform pct. 349. Dacă administratorul nu e asociat — o situație posibilă, mai ales la firme mai mari — sursele verificate pentru această funcționalitate nu documentează un regim contabil echivalent; tratamentul unei asemenea sume ar trebui stabilit separat, nu prin analogie automată cu 4551.

## Ce se greșește în practică

Greșeala tipică e tratarea oricărei sume aduse de „administrator” ca 4551, fără a verifica dacă persoana respectivă e și asociat. A doua greșeală e presupunerea că orice sumă adusă în firmă, indiferent pe ce cale (bancă sau casierie), se înregistrează identic — vezi mai jos limitarea aplicației pe acest punct.

## Ce face iConta.eu

Funcționalitatea de decontări cu asociații (F039) generează nota de primire a sumei pe contul curent de asociat prin transfer bancar (5121=4551); din câmpurile documentate pentru acest ecran nu rezultă o variantă separată pentru depunere prin casierie. Pentru sume aduse în numerar, contul corespunzător trebuie ajustat manual la introducerea notei. Funcționalitatea e gândită pentru asociați — pentru un administrator care nu e și asociat, iConta nu are o notă dedicată în acest modul.

[iConta.eu](/)
