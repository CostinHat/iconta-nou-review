---
title: "Cum corectez TVA deductibilă înregistrată în perioada greșită?"
description: TVA deductibilă înregistrată în perioada fiscală greșită se corectează prin decontul unei perioade ulterioare, la rândurile de regularizări — nu prin depunerea unei rectificative peste decontul deja depus.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez TVA deductibilă înregistrată în perioada greșită?

Pentru TVA, mecanismul de corecție nu e cel „clasic" — nu depui o declarație rectificativă care înlocuiește decontul greșit. Corectezi prin decontul unei perioade ulterioare, la rândurile de regularizări.

## Temeiul legal

::: ghid-temei
**Art. 323 alin. (3) Cod fiscal (Legea 227/2015):** *„Datele înscrise incorect într-un decont de taxă se pot corecta prin decontul unei perioade fiscale ulterioare şi se vor înscrie la rândurile de regularizări."*

**Art. 105 alin. (4) Cod de procedură fiscală (Legea 207/2015):** *„... în cazul taxei pe valoarea adăugată, corectarea erorilor din deconturile de taxă se realizează potrivit prevederilor Codului fiscal [art. 323 alin. (3)]. Erorile materiale din decontul de TVA se corectează potrivit procedurii aprobate prin ordin al preşedintelui A.N.A.F."*
:::

## Mecanismul corect

Dacă ai înregistrat o TVA deductibilă într-o perioadă fiscală greșită (de exemplu, ai dedus într-o lună TVA-ul unei facturi care aparținea de fapt lunii anterioare), nu depui o rectificativă care să înlocuiască decontul deja depus. Corectezi în decontul unei **perioade ulterioare**, la rândurile de regularizări prevăzute în formular, unde înscrii diferența.

Excepția e eroarea materială (fără impact asupra cuantumului taxei — de exemplu o greșeală de transcriere care nu schimbă suma datorată) — aceasta se corectează printr-o procedură separată, aprobată prin ordin ANAF, nu prin rândurile de regularizări.

Termenul limită pentru orice corecție (fie prin regularizare, fie prin procedura erorilor materiale) e legat de prescripția dreptului organului fiscal de a stabili creanțe fiscale — 5 ani, calculați de la 1 iulie a anului următor celui pentru care se datorează obligația (art. 110 Cod de procedură fiscală).

## Ce se greșește în practică

- **Se depune o „rectificativă D300"** care încearcă să înlocuiască integral decontul greșit — pentru TVA, mecanismul specific e regularizarea în decontul unei perioade ulterioare, nu o rectificativă clasică peste decontul depus.
- **Se corectează eroarea în decontul curent, retroactiv**, modificând sumele perioadei deja închise — corecția trebuie făcută în decontul perioadei în care se descoperă eroarea, nu prin editarea retroactivă a unui decont deja depus.
- **Se tratează orice eroare ca fiind „materială"**, pentru a evita regularizarea — doar erorile fără impact asupra cuantumului taxei intră la procedura separată de erori materiale.

## Ce face iConta.eu

Rândurile manuale de regularizare TVA (intracomunitar, taxare inversă, corecții de perioadă) se introduc și se editează dintr-un panou dedicat (`core/d300_manual_api.py`), cu recalcularea automată a decontului („Regenerează D300") după fiecare modificare. Aplicația nu automatizează alegerea între „regularizare în perioadă ulterioară" și „procedura erorilor materiale" — încadrarea corectă a erorii rămâne o decizie a contabilului.

[iConta.eu](/)
