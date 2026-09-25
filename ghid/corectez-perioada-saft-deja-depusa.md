---
title: "Cum corectez o perioadă SAF-T deja depusă?"
description: "Regula ANAF prin care orice declarație D406 (SAF-T) depusă ulterior pentru aceeași perioadă devine automat declarație rectificativă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez o perioadă SAF-T deja depusă?

Corectarea unei declarații informative D406 (fișierul standard de control fiscal — SAF-T) nu presupune o cerere separată sau un formular special de rectificare: mecanismul este automat, bazat pe ordinea depunerilor pentru aceeași lună sau trimestru.

## Temeiul legal

::: ghid-temei
„18. Prima Declaraţie informativă D406 validată, depusă pentru o lună sau un trimestru de către un contribuabil/plătitor este considerată declaraţie iniţială. Declaraţiile ulterioare depuse pentru aceeaşi perioadă (lună/trimestru) sunt automat considerate declaraţii rectificative. [...] 21. Declaraţiile rectificative care se depun pentru corectarea unei erori materiale, omisiuni etc. trebuie să cuprindă toate informaţiile din declaraţia iniţială, plus cele asupra cărora s-au efectuat corecţii."
— OPANAF nr. 1783/2021, Instrucțiuni de completare a Declarației informative D406 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

- Nu există un formular distinct de „rectificare SAF-T": se generează un fișier XML nou, complet, pentru aceeași perioadă de raportare, și se transmite din nou prin ANAF sau e-guvernare.ro.
- Declarația rectificativă trebuie să conțină **toate** informațiile din declarația inițială, nu doar diferențele — un fișier care conține doar corecțiile este respins.
- Dacă ANAF identifică erori în declarația transmisă și comunică o recipisă cu semnalări, contribuabilul trebuie să **retransmită integral** Declarația informativă D406, cu fișierul SAF-T corectat; nu sunt admise corecții parțiale prin transmiterea selectivă a unor secțiuni.
- Sistemul de depunere validează identitatea contribuabilului/plătitorului la fiecare transmitere, indiferent dacă este declarație inițială sau rectificativă.

## Ce se greșește în practică

- Se încearcă transmiterea unui fișier XML care conține doar înregistrările modificate, crezând că se va face o „actualizare parțială" — ANAF respinge acest tip de fișier.
- Se ignoră mesajele de eroare din documentul „Validator" (fișierul SAFT.xml.err.txt) și se retransmite fișierul nemodificat.
- Se presupune că o rectificativă anulează sancțiunea pentru nedepunere în termen a declarației inițiale, chiar și atunci când termenul-limită a fost deja depășit.
- Se depun rectificative repetate pentru corecții minore, fără a recalcula întregul fișier de la sursă, ceea ce duce la inconsistențe între secțiuni (de exemplu GeneralLedgerEntries vs. MasterFiles).

## Ce face iConta.eu

Din verificarea codului sursă, iConta.eu **generează fișierul SAF-T (D406)** printr-un motor dedicat (`core/d406.py`, cu module complementare pentru active — `core/d406_active.py` — și pentru reconciliere — `core/d406_reconciliere.py`), pe baza datelor contabile din aplicație. Nu am găsit însă, în cod, un flux automatizat specific de „generare declarație rectificativă D406" distinct de generarea declarației inițiale — practic, aplicația produce fișierul SAF-T pentru perioada cerută, iar decizia de a-l retransmite ca rectificativă (conform regulii de mai sus) rămâne un pas realizat prin transmiterea repetată către ANAF.

[iConta.eu](/)
