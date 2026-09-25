---
title: "De ce nu se validează fișierul D406?"
description: "Procedura oficială de validare a Declarației informative D406 (SAF-T) prin validatorul Soft J și cele mai frecvente cauze pentru care fișierul nu trece validarea."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# De ce nu se validează fișierul D406?

Fișierul SAF-T (Declarația informativă D406) trece printr-o validare în doi pași — sintactică și, parțial, semantică — înainte de a putea fi transmis către ANAF. Când validarea eșuează, cauza e aproape întotdeauna una dintre etapele acestui proces documentate oficial, nu un „bug" izolat.

## Temeiul legal

::: ghid-temei
„2. [...] b) programul «Validator» pentru fişierul SAF-T în format XML - program independent, în format executabil, interpretat, scris în limbaj Java, cu care contribuabilii/plătitorii pot valida sintactic şi în parte semantic raportarea, înainte de a o încărca pe portalul ANAF. [...]
4. Declarantul poate genera fişierul SAF-T în format XML cu ajutorul validatorului (program Soft J), pus la dispoziţie de către ANAF. [...] Validatorul Soft J realizează verificările şi validările sintactice ale fişierului în format XML (formă, formatul datelor, conţinut etc.) şi o serie de verificări semantice doar asupra fişierului în format XML. [...]
10. Transmiterea unei Declaraţii informative D406 se face doar în situaţia în care procesarea a fost realizată cu succes.
11. Dimensiunea Declaraţiei informative D406 în format PDF cu XML ataşat nu trebuie să depăşească limita maximă specificată în «Ghidul contribuabilului [...]». Dacă Declaraţia informativă D406 are o dimensiune mai mare decât limita maximă, documentul nu va fi acceptat la încărcare [...]"
— OPANAF 1783/2021, Anexa privind procedura de depunere a Declarației informative D406, pct. 2, 4, 10-11 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Cele mai frecvente motive pentru care fișierul D406 nu se validează, așa cum rezultă din procedura oficială:

- **Erori de formă/sintaxă XML** (fișierul nu respectă structura schemei SAF-T publicate de ANAF) — validatorul Soft J semnalează aceste erori încă din prima etapă, înainte de a ajunge la verificările semantice.
- **Depășirea dimensiunii maxime** a declarației în format PDF cu XML atașat — documentul nu e acceptat la încărcare dacă depășește limita stabilită în ghidul contribuabilului, caz în care declarația trebuie împărțită în segmente, conform procedurii de raportare pe perioade parțiale.
- **Erori semantice** identificate de validator (de exemplu, sume care nu se corelează între secțiuni, coduri de referință inconsistente) — validatorul semnalează doar „o serie de" verificări semantice, nu toate, deci trecerea validării Soft J nu garantează absența oricărei probleme de conținut.
- **Lipsa semnăturii electronice** cu certificat digital calificat pe fișierul PDF cu XML atașat — fără semnătură, declarația nu poate fi încărcată în portalul ANAF, chiar dacă structura fișierului e corectă.

## Ce se greșește în practică

- Se încearcă transmiterea directă a fișierului XML fără trecerea prin validatorul Soft J, sărind etapa de verificare locală care ar semnala erorile înainte de încărcare.
- Se ignoră mesajele de eroare afișate de validator, presupunând că problema e temporară sau de la sistemul ANAF, deși procedura cere identificarea și corectarea cauzei semnalate, urmată de o nouă rulare a validării.
- Se generează fișierul programatic, fără Soft J, dar fără să se respecte cerințele exacte privind câmpurile de metadate obligatorii din PDF (cif, an_r, luna_r, d_rec, totalPlata_A, universalCode), ceea ce duce la respingerea documentului.

## Ce face iConta.eu

iConta.eu generează fișierul XML pentru Declarația informativă D406 din datele contabile ale firmei, structurat conform schemei SAF-T. Pentru validarea finală și încărcarea în portalul ANAF, procesul oficial trece prin validatorul Soft J pus la dispoziție de ANAF — dacă apar erori la această etapă, cauza exactă (sintactică, semantică sau de dimensiune) trebuie identificată din mesajele afișate de validator, conform procedurii descrise mai sus.

[iConta.eu](/)
