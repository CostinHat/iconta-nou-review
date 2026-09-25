---
title: "Cum retransmit un SAF-T respins"
description: "Regula obligatorie de retransmitere integrală a Declarației informative D406 după o recipisă cu erori, potrivit OPANAF 1783/2021 — fără corecții parțiale."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum retransmit un SAF-T respins

Când ANAF trimite o recipisă cu erori pentru o Declarație informativă D406, corectarea nu se face „la fața locului", cu doar câmpurile greșite — norma cere retransmiterea **integrală** a fișierului SAF-T corectat.

## Temeiul legal

::: ghid-temei
„Pentru declarația informativă D406 transmisă cu erori identificate de Agenția Națională de Administrare Fiscală și pentru care a fost comunicată recipisa ce le semnalează, contribuabilul retransmite integral Declarația informativă D406, care trebuie să cuprindă fișierul SAF-T corectat. Nu este admisă transmiterea unor corecții parțiale prin transmiterea selectivă a înregistrărilor sau câmpurilor corectate pentru Declarația informativă D406 anterior transmisă și pentru care au fost primite recipise ce semnalau erori."
— OPANAF nr. 1.783/2021, Anexa 5, pct. 11-12 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Ce rezultă din regulă:

- Singura cale de corectare permisă e retransmiterea **completă** a declarației D406, cu fișierul SAF-T corectat de la un capăt la altul — nu doar zona/secțiunea unde ANAF a semnalat eroarea.
- Este **expres interzisă** transmiterea unor corecții parțiale: nu se pot trimite doar înregistrările sau câmpurile corectate, separat de restul fișierului deja depus.
- Practic, orice eroare, oricât de mică (de exemplu un singur rând dintr-un jurnal de sute de tranzacții), obligă la regenerarea și retransmiterea **întregii** perioade raportate, nu doar a porțiunii afectate.
- Recipisa cu erori de la ANAF e declanșatorul acestei obligații — fără o recipisă care semnalează erori, contribuabilul nu are temei să retransmită integral o declarație deja acceptată.

## Ce se greșește în practică

- Se încearcă transmiterea unui „patch" cu doar tranzacțiile corectate, crezând că sistemul ANAF le va suprapune peste depunerea anterioară — norma interzice explicit acest tip de corecție selectivă.
- Se amână retransmiterea integrală, considerând-o disproporționată pentru o eroare mică — dar fără ea, declarația rămâne, din perspectiva ANAF, în starea „cu erori semnalate".
- Se regenerează fișierul corectat fără a verifica dacă recipisa de eroare viza o singură secțiune sau întregul fișier — indiferent de sfera erorii, obligația de retransmitere e pentru declarația D406 completă.

## Ce face iConta.eu

Generatorul de SAF-T din iConta.eu (`core/d406.py` și modulele conexe) reconstruiește fișierul complet de fiecare dată când e rulat pentru o perioadă dată, pe baza datelor curente din aplicație — nu produce fișiere „delta" cu doar corecțiile. Această modalitate de lucru e compatibilă cu regula de la pct. 11-12: o retransmitere din iConta.eu e, prin construcție, o declarație D406 integrală, nu o corecție parțială. Marcarea declarației ca „retransmisă în urma unei recipise cu erori" rămâne, la data acestui ghid, o notă pe care contabilul o gestionează la depunere, în afara aplicației.

[iConta.eu](/)
