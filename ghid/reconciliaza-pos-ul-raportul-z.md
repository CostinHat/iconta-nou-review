---
title: Cum se reconciliază POS-ul cu raportul Z la restaurant?
description: Suma de card din Raportul Z ar trebui să corespundă cu ce arată terminalul POS și extrasul de bancă — aplicația nu face automat această comparație, e o verificare manuală, mai importantă la introducerea manuală decât la import.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se reconciliază POS-ul cu raportul Z la restaurant?

Suma de „card" din Raportul Z și suma decontată de banca ce procesează POS-ul ar trebui să coincidă — dar în practică pot apărea diferențe (comisioane reținute, decontare pe altă zi, tranzacții refuzate care apar totuși pe Z). Reconcilierea rămâne un pas manual.

## Temeiul legal

::: ghid-temei
„Registrul de casă servește ca: [...] document de stabilire, la sfârșitul fiecărei zile, a soldului de casă [...]" — OMFP 2634/2015, Anexa 2 (Norme specifice), Registrul de casă (Cod 14-4-7A)
:::

## Ce compari

- **Suma de card din Raportul Z** — parte din notă (`5125 = 707`), extrasă fie din fișierul AMEF importat (secțiunea de plăți pe tip, orice categorie electronică), fie din câmpul „Card" completat manual.
- **Suma decontată de banca ce operează POS-ul** — de regulă pe extrasul bancar, cu o zi sau două decalaj față de ziua vânzării, și de multe ori netă de comision.

Diferența dintre cele două nu e neapărat o eroare — poate fi doar decalajul de decontare sau comisionul bancar, care se înregistrează separat (cheltuială bancară), nu se scade din 707.

## Legătura cu calea de înregistrare

Dacă Raportul Z a intrat prin **import de fișier AMEF**, nota rămâne **ciornă** până la verificare — momentul potrivit să faci și reconcilierea cu extrasul, înainte de a valida definitiv.

Dacă a intrat prin **introducere manuală**, nota e deja **validată** din momentul salvării — reconcilierea ulterioară nu mai poate opri intrarea sumei greșite în evidență, doar o poate corecta după fapt, printr-o notă de ajustare separată.

## Ce se greșește în practică

Compararea directă, zi cu zi, a sumei de card din Z cu suma din extrasul bancar al aceleiași zile, ignorând decalajul de decontare — asta produce „diferențe" false care de fapt se lămuresc peste o zi-două. A doua greșeală: netarea comisionului bancar direct din suma de card înregistrată din Z, în loc să se contabilizeze separat ca și cheltuială — Raportul Z arată încasarea brută, așa cum a văzut-o clientul, nu netul primit de firmă.

## Ce face iConta.eu

Aplicația nu are momentan o reconciliere automată POS-extras-Z — separă corect suma de card în nota contabilă (`5125 = 707`), dar confruntarea cu extrasul bancar rămâne un control manual al contabilului. Calea de import AMEF ajută prin statutul de ciornă, care lasă timp pentru verificare înainte ca nota să intre definitiv în rulaj.

[iConta.eu](/)
