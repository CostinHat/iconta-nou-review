---
title: "O firmă nou-înființată trebuie să depună SAF-T din prima lună?"
description: "Ce spune ordinul ANAF despre obligația de depunere D406 (SAF-T) pentru firmele nou-înregistrate, în funcție de categoria de contribuabil."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# O firmă nou-înființată trebuie să depună SAF-T din prima lună?

Da, dar nu chiar din prima zi de activitate — obligația începe de la data efectivă a înregistrării firmei, iar prima depunere efectivă se face ceva mai târziu: în ultima zi a lunii care urmează perioadei pentru care se raportează. Important de reținut: pentru contribuabilii mici (categoria în care se încadrează majoritatea firmelor nou-înființate), data de referință generală (1 ianuarie 2025) a trecut deja, deci o firmă înființată acum intră direct sub obligație, fără perioada de grație de care au beneficiat firmele mici înființate înainte de acea dată.

## Temeiul legal

::: ghid-temei
„g) pentru contribuabilii nou-înregistraţi/încadraţi după data de referinţă pentru fiecare categorie în parte, obligaţia de depunere a Declaraţiei informative D406 începe de la data efectivă a înregistrării, prima depunere a Declaraţiei informative D406 urmând să se facă în ultima zi a lunii care urmează perioadei pentru care se face raportarea, ulterior datei de referinţă pentru categoria în care au fost înregistraţi/încadraţi."
— OPANAF 407/2025, Anexa nr. 5 la OPANAF 1.783/2021, pct. 1.1 lit. g) (sursă: anaf_surse/opanaf_407_2025_saft_d406.txt)
:::

Concret, pentru un SRL nou-înființat în 2026 (deci după data de referință pentru contribuabilii mici, 1 ianuarie 2025):

- **Obligația începe de la data înregistrării** la Registrul Comerțului — nu există o perioadă de grație de câteva luni, așa cum au avut firmele mici înainte de 2025.
- **Prima depunere efectivă** se face totuși la un termen mai relaxat: ultima zi calendaristică a lunii care urmează perioadei de raportare (lună sau trimestru, în funcție de perioada fiscală de TVA aplicabilă firmei).
- Excepție de la calendarul general de referință (pct. 1.1): firmele care se încadraseră deja în altă categorie la 31 decembrie 2021 au termene proprii, dar acestea nu se aplică unei firme înființate ulterior.

## Ce se greșește în practică

- Se presupune că o firmă nou-înființată e automat scutită de SAF-T pentru primul an de activitate — nu există o astfel de scutire generală în ordin; excepțiile de la pct. 4 al anexei vizează forme juridice specifice (PFA, II, IF, cabinete individuale de avocat/notar etc.), nu vechimea firmei.
- Se confundă termenul primei depuneri (ultima zi a lunii următoare perioadei raportate) cu data de la care „curge" obligația (data efectivă a înregistrării) — cele două nu coincid.
- Se ignoră faptul că SRL-urile sunt explicit în lista celor obligate (art. 3 lit. g din anexă), indiferent de mărimea firmei sau de numărul de angajați.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu calculează automat** data de la care o firmă nou-înregistrată intră sub obligația D406, pe baza categoriei de contribuabil și a datelor de referință din OPANAF 1783/2021. Generarea propriu-zisă a fișierului SAF-T există și e funcțională (`core/d406.py`, cu reconciliere independentă în `core/d406_reconciliere.py`), dar decizia „de când trebuie depus D406 pentru firma X" rămâne o verificare pe care contabilul o face manual, pe baza datei de înregistrare și a categoriei firmei.

[iConta.eu](/)
