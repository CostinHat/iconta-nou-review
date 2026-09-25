---
title: "Controlul ANAF înainte de radierea unui SRL"
description: "Ce verificare face ANAF înainte ca un SRL să poată fi radiat din registrul comerțului și rolul certificatului de atestare fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Controlul ANAF înainte de radierea unui SRL

Radierea unui SRL nu e doar o formalitate la registrul comerțului — implică și partea fiscală, prin radierea înregistrării fiscale la ANAF. Legea nu prevede un "control obligatoriu de fond" declanșat automat de intenția de radiere, dar instituie mecanismul prin care ANAF verifică obligațiile restante: certificatul de atestare fiscală.

## Temeiul legal

::: ghid-temei
„(2) La încetarea calității de subiect de drept fiscal, persoanele sau entitățile înregistrate fiscal prin declarație de înregistrare fiscală potrivit art. 81 și 82 trebuie să solicite radierea înregistrării fiscale, prin depunerea unei declarații de radiere. Declarația se depune în termen de 30 de zile de la încetarea calității de subiect de drept fiscal și trebuie însoțită de certificatul de înregistrare fiscală în vederea anulării acestuia. [...]
(6) Prin excepție de la prevederile alin. (5), în situația contribuabilului/plătitorului supus unei inspecții fiscale și care solicită eliberarea unui certificat de atestare fiscală în scopul radierii din registrele în care a fost înregistrat, certificatul de atestare fiscală se emite în termen de 5 zile lucrătoare de la data emiterii deciziei de impunere sau a deciziei de nemodificare a bazei de impozitare, după caz."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 90 alin. (2) și art. 158 alin. (6) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- **Nu există un control fiscal "automat" la radiere** — selecția pentru inspecție fiscală se face, ca și în orice altă situație, pe bază de analiză de risc (art. 121), nu obligatoriu pentru fiecare radiere.
- **Certificatul de atestare fiscală e verificarea de facto**: el confirmă dacă firma are sau nu obligații fiscale restante, iar registrul comerțului îl cere de regulă la radiere.
- **Dacă firma e deja în inspecție fiscală în derulare**, legea leagă expres eliberarea certificatului de finalizarea acelei inspecții — practic, radierea așteaptă decizia de impunere sau de nemodificare a bazei de impozitare.

## Ce se greșește în practică

- Se depune declarația de radiere fără să se verifice în prealabil situația obligațiilor restante, iar procesul se blochează la emiterea certificatului de atestare fiscală.
- Se presupune că orice radiere declanșează automat o inspecție fiscală de fond — legea nu prevede asta, decizia rămâne la analiza de risc a organului fiscal.
- Se ignoră termenul de 30 de zile de la încetarea calității de subiect de drept fiscal pentru depunerea declarației de radiere, prevăzut la art. 90 alin. (2).

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are un modul dedicat procesului de radiere sau de lichidare care să genereze automat declarația de radiere fiscală sau să verifice eligibilitatea pentru certificatul de atestare fiscală — există un modul de lichidare (`core/lichidare.py`) în cod, dar procesul de radiere propriu-zis, inclusiv interacțiunea cu ANAF pentru certificatul de atestare fiscală, rămâne în sarcina contabilului sau a consultantului care gestionează dosarul de radiere.

[iConta.eu](/)
