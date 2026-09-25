---
title: "Cum se descarcă gestiunea pentru materiale consumabile?"
description: "Documentul justificativ pentru eliberarea materialelor consumabile din magazie și scăderea lor din gestiune, conform normelor privind documentele financiar-contabile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se descarcă gestiunea pentru materiale consumabile?

Materialele consumabile intră în gestiune pe bază de recepție și ies din gestiune — adică se „descarcă" — pe bază de un document distinct, cu regim precis descris de normele metodologice ale documentelor financiar-contabile.

## Temeiul legal

::: ghid-temei
„BON DE CONSUM (Cod 14-3-4A) / BON DE CONSUM (colectiv - Cod 14-3-4/aA)
Bonul de consum servește ca:
- document de eliberare din magazie a materialelor;
- document justificativ de scădere din gestiune;
- document justificativ de înregistrare în contabilitate.
Se întocmește pe măsura eliberării materialelor din magazie pentru consum."
— OMFP 2634/2015, Anexa 2, Grupa a III-a „Bunuri de natura stocurilor" (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Concret, pentru materiale consumabile (spre deosebire de mărfurile din comerț, unde descărcarea de gestiune se face de regulă pe bază de factură/bon fiscal la vânzare):

- Documentul obligatoriu la eliberarea din magazie pentru consum este **bonul de consum** (cod 14-3-4A) sau, pentru eliberări către mai multe secții/comenzi deodată, **bonul de consum colectiv** (14-3-4/aA).
- Bonul de consum îndeplinește simultan trei roluri: document de eliberare fizică, document justificativ de scădere din gestiune și document de înregistrare contabilă (ieșire din contul de stocuri pe cheltuială).
- Evidența cantitativă zilnică a intrărilor/ieșirilor pe fiecare loc de depozitare se ține în **fișa de magazie** (cod 14-3-8), pe baza documentelor de intrare (notă de recepție) și de ieșire (bon de consum).
- Valoarea la care se descarcă gestiunea (costul consumat) depinde de metoda de evaluare a stocurilor la ieșire aleasă de entitate (FIFO, cost mediu ponderat etc.), stabilită prin politicile contabile proprii.

## Ce se greșește în practică

- Se înregistrează cheltuiala cu materialele direct la achiziție (la intrarea în gestiune), fără să se mai emită bon de consum la eliberarea efectivă din magazie.
- Se confundă bonul de consum cu avizul de însoțire a mărfii sau cu dispoziția de livrare — documente diferite, cu alt rol (transport, respectiv eliberare pentru vânzare).
- Nu se ține fișa de magazie pe fiecare loc de depozitare, ceea ce face imposibilă reconcilierea între stocul scriptic și cel faptic la inventariere.

## Ce face iConta.eu

La data acestui ghid, iConta.eu automatizează **descărcarea de gestiune pentru mărfuri** ținute în evidență global-valorică (metoda coeficientului K, pe baza rulajelor conturilor 371/378/4428 — vezi `core/stocuri.py` și `core/stocuri_api.py`, funcția `descarcare_gv`). Pentru **materiale consumabile**, care ies din gestiune pe bază de bon de consum și se evaluează prin metode de tip FIFO sau cost mediu ponderat, aplicația **nu are în prezent un flux dedicat** — nu există în cod o funcție care să genereze bonul de consum sau să calculeze automat descărcarea pe această cale. Emiterea bonului de consum și înregistrarea contabilă aferentă rămân, pentru acest tip de stoc, în sarcina contabilului.

[iConta.eu](/)
