---
title: "Cum depun simultan SAF-T și celelalte declarații"
description: "D406 (SAF-T) nu depinde de celelalte declarații lunare și nu le blochează — dar legea nu prevede și nici aplicația nu oferă o depunere „într-un singur pas” a mai multor declarații deodată; fiecare se generează și se depune separat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum depun simultan SAF-T și celelalte declarații

Întrebarea presupune, implicit, că ar exista o modalitate de a trimite mai multe declarații „la pachet" într-o singură acțiune, sau că D406 (SAF-T) ar avea o relație specială cu celelalte declarații lunare, de tip precondiție sau blocaj. Niciuna dintre premise nu se confirmă: D406 e o declarație independentă, cu propria regulă de periodicitate, iar legea nu prevede și nu interzice nimic legat de „simultaneitate" cu D300, D394 sau D112.

## Temeiul legal

::: ghid-temei
„Contribuabilii/Plătitorii transmit Declarația informativă D406 lunar sau trimestrial, urmând perioada fiscală aplicabilă pentru taxa pe valoarea adăugată (TVA)."
— OPANAF 1783/2021, Anexa 4, pct. 2 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)

„Declarația informativă D406 se transmite în format electronic, data-limită de transmitere fiind: - ultima zi calendaristică a lunii următoare perioadei de raportare..."
— OPANAF 1783/2021, Anexa 4, pct. 1 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

- D406 are propriul termen (ultima zi calendaristică a lunii următoare perioadei raportate), diferit de termenul standard de 25 folosit de majoritatea celorlalte declarații — deci „simultan" nu înseamnă neapărat „în aceeași zi", chiar dacă cele două se depun pentru aceeași perioadă de raportare.
- Periodicitatea D406 urmează periodicitatea de TVA a firmei (pct. 2), la fel ca D300 și D394 — dar aceasta e o coincidență de sursă a regulii, nu o dependență funcțională: depunerea uneia nu condiționează validarea celeilalte.
- Legea nu prevede nicio secvență obligatorie de depunere (ex. „D300 înainte de D406" sau invers) și nicio validare încrucișată între cele două la nivel de organ fiscal, conform textelor citate.

## Ce se greșește în practică

- Se amână depunerea D406 „ca să nu se suprapună" cu D300/D394, dintr-o precauție nejustificată legal — cele trei sunt declarații independente, fiecare cu termenul ei.
- Se caută o funcție de „depunere în lot" care ar trimite mai multe declarații odată — nu există, nici la nivelul procedurii ANAF, nici ca funcție a aplicației.
- Se presupune că D406 „confirmă" sau „validează" cifrele din D300/D394, sau invers — sunt fluxuri separate, fără o legătură de validare automată între ele la depunere.

## Ce face iConta.eu

Aplicația **nu are o funcție de trimitere simultană** a mai multor declarații într-o singură acțiune. Fiecare cerere de generare sau validare de declarație (inclusiv D406) tratează exact un singur tip de declarație, pentru o singură perioadă — clientul face o cerere separată pentru fiecare tip, secvențial. D406 (SAF-T) e generat prin exact același mecanism ca D300, D301, D390 sau D394, fără nicio ordine impusă și fără ca una să blocheze sau să condiționeze cealaltă: generarea unui tip nu verifică dacă un altul a fost deja depus. Dacă întrebarea reală e „D406 interferează cu celelalte declarații lunare" — răspunsul, confirmat mai sus, e că nu interferează; se depun separat, fiecare din ecranul de Declarații, cu propriul termen.

[iConta.eu](/)
