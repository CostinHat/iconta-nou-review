---
title: "Cum se contabilizează un contract IT cu facturare în funcție de orele lucrate?"
description: "Principiul contabil care guvernează recunoașterea veniturilor dintr-un contract IT facturat pe ore lucrate (time and material), în lipsa unei reglementări specifice pentru acest tip de contract."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează un contract IT cu facturare în funcție de orele lucrate?

Contractele „time and material" — frecvente în IT, unde clientul plătește pe baza orelor efectiv lucrate, nu a unui preț fix — nu au un articol dedicat în reglementările contabile românești. Nu există un OMFP separat pentru „contracte IT pe ore". Ceea ce există, și se aplică oricărui astfel de contract, e principiul general al contabilității de angajamente.

## Temeiul legal

::: ghid-temei
„Principiul contabilității de angajamente. Efectele tranzacțiilor și ale altor evenimente sunt recunoscute atunci când tranzacțiile și evenimentele se produc (și nu pe măsură ce numerarul sau echivalentul său este încasat sau plătit) și sunt înregistrate în contabilitate și raportate în situațiile financiare ale perioadelor aferente."
— OMFP nr. 1.802/2014 pentru aprobarea reglementărilor contabile, pct. 53 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Nu am găsit în corpusul de legislație verificat un articol specific pentru recunoașterea veniturilor din contracte de servicii facturate pe ore lucrate (gen „time and material" în IT) — citatul de mai sus e principiul general de recunoaștere aplicabil oricărei tranzacții, aplicat aici prin extensie firească:

- Venitul dintr-un astfel de contract se recunoaște **pe măsură ce serviciul e prestat** (orele sunt lucrate), nu la momentul facturării și nu la încasare — asta impune principiul contabilității de angajamente.
- Practic, dacă facturarea se face lunar pe baza pontajului/raportului de ore, iar luna de facturare coincide cu luna de prestare, recunoașterea venitului urmează firesc facturarea.
- Dacă există decalaj între prestare și facturare (ex. ore lucrate în decembrie, facturate abia în ianuarie), venitul trebuie recunoscut în luna prestării, prin factură neîntocmită/venituri în avans, nu în luna facturării.
- Cheltuielile aferente (salarii, subcontractare) trebuie corelate în aceeași perioadă cu venitul recunoscut, conform principiului conectării cheltuielilor cu veniturile.

## Ce se greșește în practică

- Se recunoaște venitul strict la data facturii, ignorând perioada reală în care orele au fost lucrate, mai ales la contracte cu facturare lunară decalată.
- Se omite înregistrarea de venituri realizate, dar nefacturate încă (contul 418 „Clienți — facturi de întocmit"), pentru orele lucrate la finalul unei luni și facturate abia ulterior.
- Se tratează greșit avansurile primite de la client drept venit imediat, deși ele corespund unor ore care nu au fost încă prestate.
- Se aplică mecanic un model de recunoaștere „la procent de finalizare" gândit pentru contracte de construcții/lucrări pe termen lung, deși contractul time&material se decontează, de regulă, periodic și nu necesită estimarea unui grad de finalizare global.

## Ce face iConta.eu

iConta.eu are un modul de facturare și contracte (`facturi`, `contracte_api.py`, `contracte_speciale.py`) care permite emiterea de facturi și gestionarea șabloanelor de contract, dar nu am găsit în cod o funcție dedicată de recunoaștere automată a veniturilor pe bază de ore lucrate/decontare time-and-material — contarea automată existentă (`test_contare_automata.py`) urmează regulile generale de facturare, nu un model specific de recunoaștere pe stadii pentru contracte IT. Alocarea corectă a veniturilor pe perioada de prestare, atunci când există decalaj față de factură, rămâne, în prezent, o notă contabilă manuală.

[iConta.eu](/)
