---
title: "Ce verificări trebuie făcute înainte de depunerea D406?"
description: "Etapele și controalele obligatorii de validare a fișierului XML înainte de transmiterea Declarației informative D406 (SAF-T) la ANAF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce verificări trebuie făcute înainte de depunerea D406?

Declarația informativă D406 (fișierul standard de control fiscal, SAF-T) nu se transmite direct la ANAF — procedura oficială presupune mai întâi validarea fișierului XML cu un program dedicat, corectarea eventualelor erori și abia apoi generarea și semnarea documentului final. Sărirea acestor pași duce fie la respingerea declarației, fie, mai grav, la o declarație acceptată, dar cu date incorecte.

## Temeiul legal

::: ghid-temei
„12. În situația în care, ca urmare a încercării de transmitere a Declarației D406, sunt primite mesaje de eroare/erori, utilizatorul trebuie să verifice cauza erorii prin analiza documentului generat de programul «Validator», fișierul SAFT.xml.err.txt. Odată identificată eroarea sau identificate erorile, se corectează problema semnalată de către utilizator și se generează un nou fișier XML. [...]
13. Transmiterea Declarației informative D406 se poate face de către contribuabilii/plătitorii cu obligație de depunere, începând cu prima zi calendaristică a lunii următoare perioadei pentru care obligația devine activă, până la data-limită de depunere — ultima zi a lunii care urmează perioadei pentru care se face raportarea."
— OPANAF 1783/2021, Anexa 3 — Procedura și condițiile de transmitere a fișierului standard de control fiscal (SAF-T), pct. 12-13 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

- Fișierul XML generat trebuie mai întâi trecut prin programul „Validator" pus la dispoziție de ANAF; dacă apar erori, acestea sunt listate într-un fișier separat (`SAFT.xml.err.txt`), care trebuie analizat și corectat înainte de a reface fișierul XML — declarația nu se transmite direct fără această etapă.
- Dimensiunea declarației (PDF cu XML atașat) nu trebuie să depășească limita maximă publicată de ANAF; dacă o depășește, documentul trebuie împărțit în segmente, altfel platforma nu îl acceptă la încărcare.
- Termenul de transmitere este fix: ultima zi a lunii care urmează perioadei de raportare — o depunere depusă corect din punct de vedere tehnic, dar în afara acestui interval, nu este considerată depusă în termen.
- Declarația trebuie semnată electronic cu certificat digital calificat, de către contribuabilul/plătitorul cu obligație de depunere sau de reprezentantul legal/împuternicitul înrolat cu drept de depunere.

## Ce se greșește în practică

- Se generează fișierul XML o singură dată și se încearcă transmiterea directă, fără a trece prin programul „Validator" pus la dispoziție de ANAF, ceea ce duce la respingere sau la erori de structură nedescoperite din timp.
- Se ignoră fișierul de erori (`SAFT.xml.err.txt`) generat de validator și se retrimite același fișier fără corecturi, presupunând că eroarea a fost „trecătoare".
- Se lasă generarea și transmiterea pentru ultima zi a termenului legal, fără să se lase timp pentru eventuale corecturi în caz de erori de validare sau probleme de dimensiune a fișierului.

## Ce face iConta.eu

Generarea Declarației D406 în iConta.eu (`d406.py`) este construită direct din structura oficială XSD publicată de ANAF, cu o a doua verificare independentă înainte de emitere: modulul `d406_reconciliere.py` recalculează separat, direct din notele contabile din baza de date, balanța de rulaje pe fiecare cont și o compară cu totalurile emise în fișierul SAF-T, blocând generarea („hard-block") dacă apare o divergență sau un dezechilibru între debit și credit. Această verificare internă completează, dar nu înlocuiește, trecerea fișierului XML final prin programul „Validator" al ANAF, obligatorie conform procedurii de mai sus.

[iConta.eu](/)
