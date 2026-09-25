---
title: "De ce diferă baza impozabilă din D394 față de D300?"
description: "D300 și D394 nu raportează aceeași masă de operațiuni — diferența e structurală, nu semn de eroare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# De ce diferă baza impozabilă din D394 față de D300?

O diferență între baza impozabilă totală din decontul de TVA (D300) și cea din declarația informativă D394 nu înseamnă automat o eroare de raportare. Cele două declarații acoperă mase de operațiuni diferite prin construcție: D300 e totalul de TVA al firmei, D394 e doar subsetul de operațiuni raportabile pe fiecare partener.

## Temeiul legal

::: ghid-temei
„Persoanele impozabile înregistrate în scopuri de TVA în România sunt obligate să declare livrările de bunuri, prestările de servicii şi achiziţiile de bunuri şi servicii realizate pe teritoriul României către/de la orice persoană [...]."
— OPANAF nr. 3.769/2015, art. 1 (sursă: anaf_surse/opanaf_3769_2015_d394_baza.txt)

„Nu se înscriu achiziţiile intracomunitare de bunuri şi servicii pentru care există obligativitatea înscrierii în declaraţia 390."
— OPANAF 2194/2025 (structura D394), Anexa 2 - Instrucțiuni de completare (sursă: anaf_surse/opanaf_2194_2025_d394.txt)
:::

Structural, cele două declarații nu au aceeași sferă:

- **D300** cuprinde TVA colectată și deductibilă din toate operațiunile taxabile ale perioadei, inclusiv cele fără partener identificabil individual (vânzări cu amănuntul, operațiuni către persoane fizice).
- **D394** raportează doar livrările/prestările și achizițiile efectuate pe teritoriul național de/către persoane înregistrate în scopuri de TVA, defalcate pe fiecare partener — exclude, structural, achizițiile intracomunitare (raportate prin D390) și operațiunile către persoane fizice neînregistrate.
- **Consecința logică**: totalul din D300 este, prin construcție, mai mare sau egal cu subsetul raportabil în D394 — o egalitate perfectă între cele două ar fi, de fapt, neobișnuită pentru o firmă cu clienți persoane fizice sau cu operațiuni intracomunitare.

## Ce se greșește în practică

- Se caută o egalitate exactă între totalul D300 și totalul D394, tratând orice diferență ca eroare, când diferența e așteptată de fiecare dată când firma are vânzări către persoane fizice sau operațiuni intracomunitare.
- Se omite din D394 o achiziție cu taxare inversă de la un partener român, care trebuie „pliată" pe aceeași categorie ca achizițiile obișnuite (A), nu tratată separat.
- Se raportează în D394 operațiuni cu cotă 0% fără TVA (livrări scutite cu taxare inversă, vânzări către persoane fizice) ca și cum ar avea aceeași structură cu operațiunile taxabile obișnuite.

## Ce face iConta.eu

iConta.eu verifică D394 printr-o „a doua cale" internă de reconciliere (`core/d394_reconciliere.py`): recalculează independent, direct din liniile brute ale facturilor, totalurile pe cotă de TVA și le confruntă cu cele produse de generatorul declarației — orice divergență blochează generarea, cu ambele valori afișate, fără reparare tăcută. Aplicația nu confruntă însă D394 cu D300 pe bază de egalitate: decizia documentată în cod arată explicit că o astfel de confruntare ar produce divergențe false, pentru că D300 e prin definiție TVA totală, iar D394 e doar subsetul raportabil — cele două nu sunt, și nu trebuie tratate ca fiind, aceeași cifră.

[iConta.eu](/)
