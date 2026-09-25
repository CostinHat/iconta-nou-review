---
title: "Cum înregistrez cumpărarea de euro din contul în lei?"
description: "Cursul de schimb folosit la înregistrarea contabilă a unei operațiuni de vânzare-cumpărare de valută, conform reglementărilor contabile OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum înregistrez cumpărarea de euro din contul în lei?

Cumpărarea de valută printr-o bancă comercială are o particularitate contabilă adesea ignorată: nu se folosește cursul BNR al zilei, iar operațiunea nu generează, prin ea însăși, diferențe de curs valutar.

## Temeiul legal

::: ghid-temei
„Operațiunile de vânzare-cumpărare de valută, inclusiv cele derulate în cadrul contractelor cu decontare la termen, se înregistrează în contabilitate la cursul utilizat de banca comercială la care se efectuează licitația cu valută, fără ca acestea să genereze în contabilitate diferențe de curs valutar."
— OMFP 1802/2014, pct. 304 alin. (2) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Diferența față de tratamentul obișnuit al operațiunilor în valută este esențială:

- Pentru majoritatea operațiunilor în valută (facturi, plăți către furnizori etc.), regula generală este înregistrarea la **cursul de schimb comunicat de BNR** din ultima zi bancară anterioară operațiunii (pct. 304 alin. (1)).
- **Pentru cumpărarea/vânzarea efectivă de valută** printr-o bancă, regula e alta: se folosește **cursul utilizat de banca comercială** la tranzacție (cursul de vânzare/cumpărare afișat de bancă), nu cursul BNR al zilei.
- Norma prevede explicit că această operațiune **nu generează diferențe de curs valutar** în contabilitate — pentru că nu există un curs „oficial" de referință față de care să apară un câștig sau o pierdere; leii ieșiți din cont și valuta intrată se înregistrează direct la cursul comercial folosit.
- Eventualul cost al tranzacției (diferența dintre cursul BNR și cursul comercial al băncii, uneori numit generic „comision de schimb") se reflectă în valoarea de intrare a valutei cumpărate, nu ca o cheltuială financiară separată de diferențe de curs.

## Ce se greșește în practică

- Se înregistrează cumpărarea de valută la cursul BNR al zilei, generând artificial o „diferență de curs" între cursul BNR și suma efectiv plătită/încasată prin bancă — deși norma exclude explicit acest tratament pentru operațiunea de schimb propriu-zisă.
- Se contabilizează separat un „cost de schimb valutar" ca diferență de curs valutar, în loc să se recunoască pur și simplu la cursul comercial folosit de bancă.
- Se confundă cursul de la data efectuării operațiunii (folosit pentru facturi, plăți către terți) cu cursul comercial al băncii, aplicabil exclusiv operațiunilor de vânzare-cumpărare de valută.

## Ce face iConta.eu

Am verificat rapid modulele legate de bancă (`core/banca.py`, `core/banca_parser.py`, `core/curs_bnr.py`): nu am găsit o funcție dedicată care să identifice o operațiune de schimb valutar (cumpărare/vânzare de valută) din extrasul bancar și să o înregistreze la cursul comercial al băncii, fără diferență de curs, conform pct. 304 alin. (2) din OMFP 1802/2014. Tranzacțiile de schimb valutar se procesează, la acest moment, ca orice altă mișcare bancară, iar încadrarea lor corectă rămâne în sarcina contabilului.

[iConta.eu](/)
