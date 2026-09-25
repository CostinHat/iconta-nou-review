---
title: "Software pentru gestiunea numerarului 2026"
description: "Când sunt operatorii economici obligați să folosească aparate de marcat electronice fiscale pentru încasările în numerar și cum se integrează datele lor în contabilitate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Software pentru gestiunea numerarului 2026

Orice firmă care încasează, integral sau parțial, cu numerar sau cu cardul, contravaloarea bunurilor vândute cu amănuntul sau a serviciilor prestate direct către populație intră sub obligația de a folosi aparate de marcat electronice fiscale (AMEF) — „gestiunea numerarului" nu înseamnă, în acest caz, un simplu registru de casă ținut manual, ci un sistem fiscal reglementat, ale cărui date (rapoarte Z) trebuie apoi integrate corect în contabilitate.

## Temeiul legal

::: ghid-temei
„Articolul 1 (1) Operatorii economici care încasează, integral sau parțial, cu numerar sau prin utilizarea cardurilor de credit/debit sau a substitutelor de numerar contravaloarea bunurilor livrate cu amănuntul, precum și a prestărilor de servicii efectuate direct către populație sunt obligați să utilizeze aparate de marcat electronice fiscale."
— Ordonanța de urgență nr. 28/1999 privind obligația operatorilor economici de a utiliza aparate de marcat electronice fiscale, art. 1 alin. (1) (sursă: anaf_surse/oug_28_1999.html)
:::

Ce rezultă concret din text:

- **Obligația vizează încasările de la populație** — vânzarea cu amănuntul și prestările de servicii efectuate direct către persoane fizice, indiferent dacă plata se face cash, cu cardul sau cu alte substitute de numerar (tichete, vouchere).
- **Bonul fiscal e obligatoriu** pentru fiecare încasare (art. 1 alin. 2), cu excepții limitate (de exemplu, pentru încasările prin card, unde nu mai există obligația de imprimare/înmânare fizică a bonului, conform alin. 2^1).
- Fiecare zi de funcționare a AMEF generează un **raport Z**, care centralizează încasările pe tip de plată (numerar, card, tichete etc.) și pe cotă de TVA — acest raport e documentul-sursă pentru înregistrarea contabilă a vânzărilor cu amănuntul din ziua respectivă.

## Ce se greșește în practică

- Se ține evidența încasărilor cu numerar doar printr-un registru de casă întocmit manual, fără AMEF, deși firma vinde cu amănuntul sau prestează servicii direct către populație — obligația de la art. 1 alin. (1) nu are o excepție generală pentru firmele mici.
- Se înregistrează în contabilitate direct suma totală din raportul Z, fără să se separe corect pe tipuri de plată (numerar vs. card vs. tichete) — fiecare tip de plată trebuie reflectat pe contul corespunzător (casă, bancă/tranzit card, tichete), nu cumulat generic.
- Se pierde/nu se arhivează raportul Z zilnic, considerând suficientă doar centralizarea lunară — raportul Z e documentul justificativ pentru fiecare zi de activitate, cerut de reglementările contabile pentru susținerea înregistrărilor.

## Ce face iConta.eu

iConta.eu are o funcționalitate reală de import al rapoartelor Z din fișierele AMEF (`core/amef_import.py`), pe structura oficială definită prin OPANAF 146/2018, anexa 2, secțiunea II.7 — citește fișierul semnat (XML sau p7b), extrage totalurile pe fiecare tip de plată (card, numerar, tichete de masă, bonuri valorice, voucher, credit, alte) și pe fiecare cotă de TVA, pregătindu-le pentru înregistrarea contabilă corespunzătoare. Ce nu automatizează astăzi aplicația: verificarea faptului că firma respectă obligația legală de a deține și folosi un AMEF acolo unde legea o cere — asta rămâne o decizie și o responsabilitate a firmei, anterioară folosirii aplicației.

[iConta.eu](/)
