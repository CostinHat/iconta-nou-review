---
title: "Cum se înregistrează plata cu cardul firmei?"
description: "Ce cont din planul de conturi reglementat prin OMFP 1802/2014 se folosește pentru sumele acordate și decontate prin cardul firmei."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează plata cu cardul firmei?

Plățile efectuate cu cardul firmei (de un administrator sau un angajat, pentru cheltuieli curente) nu se înregistrează direct ca o ieșire simplă din contul bancar — planul de conturi reglementat prevede explicit contul 542 „Avansuri de trezorerie" pentru evidențierea sumelor acordate prin sistemul de carduri, urmând același mecanism ca un avans de numerar clasic: acordare, apoi decontare pe bază de documente justificative.

## Temeiul legal

::: ghid-temei
„542. Avansuri de trezorerie*18) (A) [...] *18) În acest cont vor fi evidențiate și sumele acordate prin sistemul de carduri."
— OMFP 1802/2014 pentru aprobarea Reglementărilor contabile privind situațiile financiare anuale individuale și situațiile financiare anuale consolidate, planul de conturi general, contul 542 și nota *18) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Practic, mecanismul contabil pentru plata cu cardul firmei urmează pașii unui avans de trezorerie:

- **Acordarea sumei** pe card (alimentare/plafon disponibil pentru utilizarea cardului) se înregistrează în debitul contului 542, prin creditul contului de disponibilități bancare corespunzător.
- **Decontarea** se face pe măsură ce apar documentele justificative pentru cheltuielile plătite cu cardul (bonuri fiscale, facturi) — fiecare cheltuială se înregistrează pe contul de cheltuială corespunzător, în creditul contului 542, inclusiv TVA-ul deductibil aferent, dacă există document care să-l susțină.
- **Suma nedecontată** rămasă în soldul contului 542 la închiderea exercițiului se reclasifică, după caz, ca avans acordat personalului (cont 4282) sau ca alt debitor (cont 461), dacă nu a fost justificată prin documente.

## Ce se greșește în practică

- Se înregistrează plata cu cardul direct pe contul de cheltuială, în creditul contului bancar (5121), sărind peste contul 542 — chiar dacă rezultatul final pe cheltuială poate părea identic, se pierde evidența intermediară a sumelor acordate și nedecontate, cerută explicit de nota *18) din planul de conturi.
- Se lasă solduri nedecontate pe cont 542 la sfârșitul exercițiului financiar, fără reclasificare — un sold nejustificat rămas pe avansuri de trezorerie la închidere distorsionează bilanțul și poate atrage întrebări la un control.
- Se omite TVA deductibil aferent cheltuielilor plătite cu cardul, la decontare, deși există bonul fiscal/factura care îl susține — decontarea corectă separă baza de cheltuială de TVA-ul aferent, fiecare pe contul lui.

## Ce face iConta.eu

iConta.eu are o funcționalitate reală pentru avansurile de trezorerie, în `core/casa.py`: acordarea unui avans (inclusiv prin card, conform notei *18 din OMFP 1802/2014) generează nota contabilă pe cont 542, decontarea pe bază de documente justificative distribuie sumele pe conturile de cheltuială corespunzătoare (cu TVA separat, dacă e cazul), iar soldurile nedecontate la închidere se pot reclasifica automat pe 4282 (personal) sau 461 (alți debitori), cu temeiul citat direct în cod (`OMFP 1802/2014 pct. 302/306`).

[iConta.eu](/)
