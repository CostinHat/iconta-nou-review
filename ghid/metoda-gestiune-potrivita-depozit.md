---
title: "Ce metodă de gestiune este potrivită pentru un depozit?"
description: "Cele trei metode legale de evaluare a stocurilor la ieșirea din gestiune — CMP, FIFO, LIFO — și ce presupune fiecare pentru un depozit cu mișcare de mărfuri."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce metodă de gestiune este potrivită pentru un depozit?

Reglementările contabile românești nu impun o singură metodă de evaluare a stocurilor la ieșirea din gestiune — firma alege dintre trei metode permise legal, iar alegerea trebuie aplicată consecvent, nu schimbată după cum e mai convenabil de la o lună la alta.

## Temeiul legal

::: ghid-temei
„96. - (1) Costul de achiziție sau costul de producție al stocurilor din aceeași categorie și al tuturor elementelor fungibile se calculează prin aplicarea uneia din următoarele metode: a) metoda costului mediu ponderat - CMP; b) metoda primul intrat-primul ieșit - FIFO; c) metoda ultimul intrat-primul ieșit - LIFO. (2) Metoda «costului mediu ponderat» (CMP) presupune calcularea costului fiecărui element pe baza mediei ponderate a costurilor elementelor similare aflate în stoc la începutul perioadei și a costului elementelor similare produse sau cumpărate în timpul perioadei. Media poate fi calculată periodic sau după fiecare recepție. Perioada de calcul nu trebuie să depășească durata medie de stocare. (3) Potrivit metodei «primul intrat-primul ieșit» (FIFO), bunurile ieșite din gestiune se evaluează la costul de achiziție sau de producție al primei intrări (lot). Pe măsura epuizării lotului, bunurile ieșite din gestiune se evaluează la costul de achiziție sau de producție al lotului următor, în ordine cronologică. (4) Potrivit metodei «ultimul intrat-primul ieșit» (LIFO), bunurile ieșite din gestiune se evaluează la costul de achiziție sau de producție al ultimei intrări (lot). Pe măsura epuizării lotului, bunurile ieșite din gestiune se evaluează la costul de achiziție sau costul de producție al lotului anterior, în ordine cronologică."
— OMFP 1802/2014, pct. 96 alin. (1)-(4) (Reglementări contabile privind situațiile financiare anuale individuale) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Diferențele practice între metode, relevante pentru un depozit:

- **CMP** recalculează costul mediu la fiecare recepție (sau periodic), atenuând fluctuațiile de preț — potrivit pentru depozite cu mărfuri fungibile, achiziționate frecvent, la prețuri variabile, unde urmărirea loturilor individuale ar fi greoaie.
- **FIFO** presupune că bunurile cele mai vechi ies primele din gestiune, la costul lor real de achiziție — potrivit pentru depozite cu produse perisabile sau cu rotație rapidă, unde ordinea reală de vânzare urmează efectiv ordinea de intrare.
- **LIFO** evaluează ieșirile la costul ultimului lot intrat — mai rar folosită în practică pentru gestiunea fizică reală a unui depozit, pentru că poate lăsa în stoc, contabil, loturi vechi la costuri istorice depășite.
- **Metoda se alege pe categorie de stocuri**, nu neapărat una singură pentru toată firma — dar, odată aleasă pentru o categorie, trebuie aplicată consecvent (principiul permanenței metodelor, pct. 50 din aceleași reglementări), iar schimbarea ei se documentează în notele explicative.

## Ce se greșește în practică

- Se schimbă metoda de evaluare de la o lună la alta, în funcție de care dă rezultatul contabil mai convenabil — asta încalcă principiul permanenței metodelor și nu are susținere fără o justificare documentată.
- Se aplică FIFO „logic" (fizic, produsele vechi ies primele din depozit) dar se calculează costul contabil ca și cum ar fi CMP — mișcarea fizică reală a mărfii nu trebuie confundată cu metoda de evaluare contabilă folosită efectiv.
- Se presupune că metoda aleasă pentru o categorie de stocuri se aplică automat și la celelalte categorii din același depozit, fără o decizie și o documentare separată pentru fiecare.
- Se ignoră cerința ca perioada de calcul a CMP să nu depășească durata medie de stocare — o mediere pe un interval prea lung distorsionează costul de ieșire față de realitatea pieței.

## Ce face iConta.eu

La data acestui ghid, iConta.eu implementează **exclusiv metoda CMP** (costul mediu ponderat), recalculat după fiecare intrare, conform OMFP 1802/2014 pct. 96 — vezi `core/stocuri_cv.py` (`fisa_magazie()`, `valoare_iesire()`, constanta `TEMEI_CMP`). Aplicația nu oferă metodele FIFO sau LIFO ca opțiuni alternative de evaluare a stocurilor; firmele care aleg, prin politica lor contabilă, una din aceste două metode trebuie să țină evidența loturilor și calculul costurilor de ieșire prin alte mijloace, în afara acestui modul. Există separat un modul de gestiune la preț de vânzare cu amănuntul (`core/stocuri.py`, cu coeficientul de repartizare K), pentru firmele de retail care folosesc acest regim specific, diferit de CMP/FIFO/LIFO.

[iConta.eu](/)
