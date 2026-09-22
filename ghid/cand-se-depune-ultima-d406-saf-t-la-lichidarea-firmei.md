---
title: Când se depune ultima D406 SAF-T la lichidarea firmei?
description: Nu există un temei legal identificat explicit, în actele OPANAF care reglementează D406, pentru termenul ultimei declarații la lichidare/radiere — subiectul necesită verificare suplimentară directă la ANAF sau în Codul de procedură fiscală înainte de a fi tratat ca regulă certă.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Când se depune ultima D406 SAF-T la lichidarea firmei?

Această întrebare vine frecvent de la contabilii care gestionează dizolvarea sau radierea unei firme și vor să știe dacă mai există o obligație D406 de închis înainte de radiere. Răspunsul scurt, onest: actele normative de bază care reglementează D406 (OPANAF 1783/2021 și OPANAF 407/2025) **nu tratează explicit** acest caz.

## Temeiul legal

::: ghid-temei
Textele OPANAF 1783/2021 și OPANAF 407/2025 privind Declarația D406 (SAF-T) nu conțin nicio
prevedere care să reglementeze termenul ultimei declarații D406 la lichidarea, încetarea
sau radierea firmei — o verificare directă a acestor două acte pentru termenii
"lichidare", "încetare", "radiere" sau "radiat" nu a găsit nicio potrivire.
:::

**Notă importantă**: acest ghid nu poate afirma o regulă certă, pentru că temeiul legal specific pentru acest caz nu a fost identificat în sursele verificate (OPANAF 1783/2021 și OPANAF 407/2025, cu Anexele lor). Este posibil ca la lichidare/radiere să se aplice regula generală din Codul de procedură fiscală (Legea 207/2015) privind încetarea obligațiilor declarative la radierea din registrul contribuabililor (posibil relevant: art. 59^1), dar acest temei **nu a fost citit și confirmat** — nu trebuie tratat ca sursă până la o verificare separată, directă, a textului de lege.

## Ce se știe cu certitudine și ce nu

Ce este confirmat, din regulile generale ale D406:

- Termenul obișnuit de depunere este ultima zi calendaristică a lunii următoare perioadei de raportare.
- O declarație rectificativă corectă se retransmite integral, nu parțial.

Ce **nu** este confirmat, pentru cazul specific al lichidării:

- Dacă ultima D406 trebuie depusă la o dată anume raportată la momentul radierii (de exemplu, în termenul obișnuit, calculat de la ultima lună de activitate) sau dacă există un termen special, mai scurt, legat de procedura de radiere.
- Dacă obligația de depunere D406 încetează automat la data radierii, sau dacă mai există o declarație finală de transmis ulterior radierii, pentru ultima perioadă de activitate.
- Dacă secțiunile "Active" (depusă la termenul situațiilor financiare) au un tratament diferit în context de lichidare, având în vedere că situațiile financiare de lichidare au propriile termene.

## Ce se greșește în practică

- Se presupune, fără verificare, că ultima D406 se depune "ca de obicei", cu termen pe ultima zi a lunii următoare, fără a verifica dacă procedura de radiere impune un termen diferit.
- Se ignoră complet obligația D406 la lichidare, considerând că radierea suspendă automat toate declarațiile, fără confirmare legală directă.
- Se tratează acest subiect ca fiind acoperit de OPANAF 1783/2021 sau 407/2025, deși aceste acte nu îl menționează.

## Ce face iConta.eu

Codul motorului D406 (`core/d406.py`) și modulul de lichidare al aplicației (`core/lichidare.py`) nu conțin, în verificarea efectuată, nicio logică specifică pentru generarea sau blocarea D406 la lichidarea firmei — subiectul nu este cablat separat în cod. Recomandarea, până la clarificarea temeiului legal exact: contabilul verifică direct la ANAF sau la un consultant fiscal termenul aplicabil ultimei D406 în contextul specific al lichidării firmei sale, înainte de a se baza pe o presupunere.

[iConta.eu](/)
