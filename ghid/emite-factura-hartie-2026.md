---
title: "Se mai poate emite factură pe hârtie în 2026"
description: "Obligația de transmitere a facturilor prin sistemul RO e-Factura pentru operațiunile B2B stabilite în România, și ce mai rămâne, totuși, în afara ei."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Se mai poate emite factură pe hârtie în 2026

Întrebarea „mai pot da factură pe hârtie?" ascunde, de fapt, două întrebări diferite: poate firma să tipărească fizic un document pentru client, și poate firma să evite transmiterea facturii prin sistemul RO e-Factura? Răspunsul la a doua întrebare e, pentru marea majoritate a operațiunilor B2B din România, nu.

## Temeiul legal

::: ghid-temei
„În relația comercială B2B, între persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015, cu modificările și completările ulterioare, emitentul facturii electronice are obligația de transmitere a acesteia către destinatar utilizând sistemul național privind factura electronică RO e-Factura, cu respectarea prevederilor art. 4 alin. (1). Fac excepție facturile simplificate emise conform art. 319 alin. (12) din Legea nr. 227/2015, cu modificările și completările ulterioare."
— Ordonanța de urgență nr. 120/2021, art. 10 alin. (1), astfel cum a fost modificat prin Legea nr. 296/2023 (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)

„În cazul în care emitentul facturii electronice a optat pentru utilizarea sistemului național privind factura electronică RO e-Factura, utilizarea facturii electronice este considerată acceptată la data comunicării în acest sistem."
— Ordonanța de urgență nr. 120/2021, art. 11, astfel cum a fost modificat prin Legea nr. 296/2023 (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

**Notă de precizie:** o formă anterioară a acestei reguli (art. LIX alin. (1) din Legea 296/2023) a fost o regulă tranzitorie, valabilă strict 1 ianuarie–30 iunie 2024; citatele de mai sus sunt forma permanentă, în vigoare din 1 iulie 2024.

Ce înseamnă, concret, pentru „factura pe hârtie":

- Pentru operațiunile **B2B**, cu locul livrării/prestării în România, între operatori economici stabiliți în România, obligația de transmitere prin **RO e-Factura** se aplică **indiferent** dacă firma e sau nu înregistrată în scopuri de TVA — deci nici măcar statutul de neplătitor de TVA nu scutește de această obligație.
- „Factura pe hârtie", ca document fizic dat clientului, poate încă exista ca **anexă practică** (de exemplu, un exemplar tipărit atașat mărfii la livrare) — dar documentul cu valoare fiscală, exemplarul original, e fișierul XML transmis prin sistemul RO e-Factura, semnat electronic de Ministerul Finanțelor, nu hârtia.
- Există o excepție de transmitere **directă** către destinatar: dacă **ambele părți** (emitent și destinatar) sunt înregistrate în Registrul RO e-Factura, transmiterea facturii direct de la furnizor la beneficiar (de exemplu, prin e-mail sau curier) nu mai e obligatorie separat — dar factura tot trebuie să fi trecut prin sistemul RO e-Factura, nu doar emisă pe hârtie/PDF în afara lui.
- Pentru operațiunile care nu intră sub incidența acestei obligații (de exemplu, cele către persoane care nu sunt stabilite și nici înregistrate în scopuri de TVA în România, sau anumite categorii scutite expres), regulile generale de facturare din art. 319 al Codului fiscal rămân aplicabile, inclusiv posibilitatea unei facturi clasice, pe hârtie sau PDF, în afara sistemului național.

## Ce se greșește în practică

- Se emite factura ca document Word/PDF, semnat și trimis direct clientului, fără transmitere prin RO e-Factura, considerând că „a ajuns la client, deci e valabilă" — pentru operațiunile B2B care intră sub obligație, lipsa transmiterii prin sistem face factura neconformă, indiferent că a fost primită de destinatar.
- Se presupune că neplătitorii de TVA sunt scutiți de obligația RO e-Factura — obligația de transmitere prin sistem se aplică indiferent de statutul de TVA al furnizorului.
- Se confundă exemplarul fizic/PDF dat clientului la livrare cu „exemplarul original" al facturii — pentru operațiunile din sistem, originalul e fișierul XML semnat de Ministerul Finanțelor, nu documentul tipărit.

## Ce face iConta.eu

La data acestui ghid, iConta.eu emite și transmite facturile prin sistemul RO e-Factura (`core/efactura_send.py`, `core/efactura_trimitere.py`) pentru operațiunile care intră sub această obligație — aplicația nu oferă o opțiune de emitere „doar pe hârtie", în afara sistemului național, pentru operațiunile B2B supuse obligației de facturare electronică.

[iConta.eu](/)
