---
title: Cum verific următorul termen fiscal al firmei?
description: Ecranul Termene din iConta.eu arată următoarea scadență a firmei, chiar dacă administrezi o singură firmă — plus o precizare despre ce nu intră în această fereastră.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum verific următorul termen fiscal al firmei?

Nu contează dacă administrezi o singură firmă sau un portofoliu întreg — ecranul „Termene" din iConta.eu funcționează la fel: citește vectorul fiscal, derivă declarațiile datorate în următoarele 60 de zile și le grupează pe dată. Pentru un singur cont conectat la o singură firmă, rezultatul e, practic, calendarul acelei firme.

## Temeiul legal

::: ghid-temei
„până la data de 25 inclusiv a lunii următoare celei în care se încheie perioada fiscală"
— Codul fiscal, art. 323 alin. (1) (termenul D300)
:::

Fiecare declarație are propriul temei de termen (D300 mai sus, D112 — 25 a lunii următoare, D406/SAF-T — ultima zi a lunii următoare, D101 — 25 iunie anul următor ș.a.m.d.) — ecranul „Termene" nu introduce o regulă proprie, doar le agregă pe toate, calculate din vectorul fiscal al firmei.

## Unde verifici

- **Cardul „Următoarea scadență"** de pe ecranul de start — arată direct data celei mai apropiate declarații datorate și tipul ei, fără să fie nevoie să intri în detaliu.
- **Ecranul „Termene"** — lista completă a scadențelor din următoarele 60 de zile, în ordine cronologică, cu detaliile fiecărei declarații.

Ambele funcționează la fel indiferent de câte firme ai — cu o singură firmă conectată la cont, calendarul se reduce, pur și simplu, la scadențele ei.

## Ce NU arată acest ecran

- **Restanțele** (declarații cu termen deja trecut) nu apar aici — fereastra e strict viitoare, [azi, azi+60 zile]. Pentru restanțe, verifică ecranul „Semafor" (control fiscal), care are o fereastră diferită și include explicit ce a trecut de termen.
- **Termenele mai îndepărtate de 60 de zile** nu apar încă — vor intra pe listă treptat, pe măsură ce se apropie.
- Dacă firma nu are vectorul fiscal completat (regim, statut TVA, tip decont, operațiuni intracomunitare), ecranul nu poate calcula nimic — firma apare separat, cu mesajul explicit „Vector fiscal necompletat — nu pot evalua obligațiile firmei.", nu tăcut, ca listă goală fără explicație.

## Ce se greșește în practică

- Se confundă „nicio scadență afișată" cu „nimic de depus" — poate fi, de fapt, un vector fiscal necompletat; se verifică mereu și secțiunea „neevaluate".
- Se caută restanțele pe acest ecran — ele apar pe „Semafor", nu pe „Termene".
- Se presupune că datele sunt live, recalculate instant după fiecare modificare — de fapt provin dintr-un model precalculat de un proces de fundal, actualizat la schimbările relevante, nu la fiecare afișare a ecranului.

## Ce face iConta.eu

Ecranul „Termene" derivă declarațiile datorate din vectorul fiscal și din faptele firmei (salariați, operațiuni intracomunitare), folosind același motor de mapare fiscală ca „Semafor", cu fereastra restrânsă la 60 de zile viitoare. Rezultatul e identic ca mecanism, indiferent dacă la contul respectiv sunt atașate una sau mai multe firme — nu există o cale separată pentru „cont individual".

[iConta.eu](/)
