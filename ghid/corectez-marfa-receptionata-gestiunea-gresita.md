---
title: "Cum corectez marfa recepționată pe gestiunea greșită?"
description: Nu există un mecanism de "corectare a locației" separat - singurul instrument disponibil este transferul obișnuit între gestiuni, cu marfa mutată la costul mediu curent din gestiunea greșită în cea corectă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez marfa recepționată pe gestiunea greșită?

S-a întocmit NIR-ul, marfa a fost recepționată, dar pe gestiunea greșită. Nu există un formular sau o funcție separată de „corectare a locației" — soluția e un transfer obișnuit, din gestiunea unde a ajuns greșit spre gestiunea corectă.

## Temeiul legal

::: ghid-temei
„recepționarea tuturor bunurilor materiale intrate în entitate și înregistrarea acestora la locurile de depozitare"

— OMFP 1802/2014, Anexa 1 (Reglementări contabile), pct. 284 alin. (2) lit. a)

„În cazul utilizării ca bon de transfer între două gestiuni aflate în incinta entității, bonul de predare, transfer, restituire se întocmește pe măsură ce se efectuează transferul. Transferul se efectuează numai între gestiuni din incinta aceleiași entități. În cazul gestiunilor dispersate teritorial se întocmește Aviz de însoțire a mărfii (cod 14-3-6A)."

— OMFP 2634/2015, Anexa 2, pct. 189 (Bonul de predare, transfer, restituire, cod 14-3-3A)
:::

Primul text arată de ce contează locul de depozitare: recepția corectă a bunurilor materiale presupune înregistrarea lor la locul de depozitare real, nu doar cantitativ. Dacă marfa a fost recepționată pe gestiunea greșită, evidența nu mai reflectă realitatea fizică — trebuie corectată. Al doilea text dă instrumentul: același document folosit pentru un transfer obișnuit (14-3-3A dacă gestiunile sunt în aceeași incintă, 14-3-6A dacă sunt dispersate teritorial) servește și pentru corectarea unei recepții greșit alocate — din punct de vedere al mișcării de stoc, o corecție e tot un transfer.

## Ce se greșește în practică

- Se anulează și se reface NIR-ul integral pentru o simplă eroare de gestiune, deși mișcarea de intrare inițială a fost corectă cantitativ și valoric — singura problemă e locația.
- Se lasă marfa „pe hârtie" în gestiunea greșită, cu o notă informală în afara sistemului, fără nicio mișcare de corecție înregistrată — la o inventariere, stocul faptic din gestiunea corectă nu se potrivește cu evidența.
- Se face corecția fără niciun document/mențiune care să arate că e vorba de o corecție, nu de un transfer comercial obișnuit — util pentru trasabilitate la un control.

## Ce face iConta.eu

iConta.eu nu are o funcție dedicată „corectare locație recepție" — verificat direct în codul motorului de stocuri, nu există un asemenea tip de mișcare separat de transferul obișnuit. Instrumentul disponibil e funcția de transfer (F138): ieșire din gestiunea greșită + intrare în gestiunea corectă, ambele la costul mediu ponderat (CMP) curent al articolului, fără notă contabilă (nu modifică nimic în Registrul jurnal, doar realocă marfa între gestiuni). Câmpul de document al mișcării, text liber, poate purta o mențiune de tipul „corecție recepție NIR nr. X" pentru trasabilitate — dar sistemul nu marchează automat mișcarea ca „de corecție"; în evidența de stoc, va arăta identic cu orice alt transfer între gestiuni.

[iConta.eu](/)
