---
title: "Contabilitatea unei farmacii: cotele de TVA la medicamente"
description: O farmacie vinde, sub același acoperiș, produse cu cel puțin trei cote diferite de TVA — medicamente la 11%, suplimente alimentare și cosmetice la 21% — și trebuie să le urmărească separat, linie cu linie, nu global pe bon.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Contabilitatea unei farmacii: cotele de TVA la medicamente

O farmacie nu vinde un singur tip de produs din punct de vedere fiscal. Pe același bon apar, de obicei, medicamente (cotă redusă), suplimente alimentare (cotă standard) și produse cosmetice sau dispozitive medicale (cotă standard, cu excepții punctuale). Contabilitatea corectă cere separarea acestor categorii pe fiecare linie vândută, nu aplicarea unei cote unice pe tot bonul.

## Temeiul legal

::: ghid-temei
Cota redusă de 11% se aplică pentru „livrarea de medicamente de uz uman" — Codul fiscal, art. 291 alin. (2) lit. a). Suplimentele alimentare definite de Legea nr. 56/2021 sunt excluse explicit de la cota redusă a alimentelor — art. 291 alin. (2) lit. b) pct. 4.
:::

## Cele trei categorii tipice dintr-o farmacie

- **Medicamentele de uz uman** (cu sau fără prescripție, compensate sau nu) — cota redusă de 11%, pe litera a) a listei de la art. 291 alin. (2).
- **Suplimentele alimentare** (vitamine, minerale, produse pe bază de plante cu statut de supliment, nu de medicament) — cota standard de 21%, excluse explicit din categoria alimentelor la cotă redusă.
- **Produsele cosmetice, dermato-cosmetice și dispozitivele medicale** care nu au statut legal de medicament — cota standard de 21%, ca regulă generală, dacă nu se încadrează la o altă categorie redusă din listă.

Diferența dintre „medicament" și „supliment alimentar" nu ține de raftul pe care stă produsul, ci de statutul lui legal (autorizație de punere pe piață ca medicament, respectiv notificare ca supliment alimentar) — un consultant, un farmacist sau furnizorul produsului confirmă această încadrare, nu aspectul comercial al ambalajului.

## Ce se greșește în practică

- Se aplică o singură cotă (de obicei 11%, din reflexul „e farmacie") pe întreg bonul, fără defalcarea pe categorii — greșeală frecventă mai ales la vânzările pe bon fiscal, unde nu există o linie de factură detaliată pentru fiecare produs.
- Se tratează suplimentele alimentare ca medicamente doar pentru că au fost recomandate de farmacist sau au ambalaj similar unui medicament.
- Se ignoră excepțiile din interiorul categoriei „alimente" (băuturi alcoolice, băuturi NC 2202, alimente cu zahăr ≥10g/100g) pentru produsele alimentare/dietetice vândute uneori și în farmacii, aplicându-se automat 11% fără verificarea excepțiilor.

## Ce face iConta.eu

`core/cote_tva.py` clasifică fiecare linie vândută separat: categoria „medicamente" intră în `CATEGORII_11` (litera a), iar suplimentele alimentare apar explicit în `EXCEPTII_21`, pentru a nu fi confundate cu medicamentele la potrivirea automată. Pentru vânzările pe bon fiscal, fără articol identificat individual la fiecare tranzacție, farmaciile pot ține gestiune global-valoric cu descărcare lunară — dar cota de TVA rămâne cea a fiecărei categorii de produs vândute, nu una singură pentru tot rulajul lunii. Când motorul de potrivire nu poate stabili cu certitudine categoria unui produs, aplicația nu presupune tăcut o cotă — semnalează cota ca nedeterminată, până la o clasificare manuală.

[iConta.eu](/)
