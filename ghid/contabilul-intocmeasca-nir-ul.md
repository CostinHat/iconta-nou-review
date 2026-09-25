---
title: "Poate contabilul să întocmească NIR-ul?"
description: "Cine poartă răspunderea pentru Nota de recepție și constatare de diferențe, potrivit Legii contabilității și normelor privind documentele financiar-contabile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Poate contabilul să întocmească NIR-ul?

Legea nu rezervă întocmirea Notei de recepție și constatare de diferențe (NIR) unei anumite funcții din firmă — dar responsabilitatea pentru conținutul documentului revine celui care îl întocmește, vizează și aprobă, nu doar celui care îl înregistrează în contabilitate.

## Temeiul legal

::: ghid-temei
„(1) Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ. (2) Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea nr. 82/1991, art. 6 alin. (1)-(2) (sursă: anaf_surse/legea_82_1991_consolidat.txt)

„Nota de recepție și constatare de diferențe (NIR) servește ca: document pentru recepția bunurilor aprovizionate; document justificativ pentru încărcare în gestiune; document justificativ de înregistrare în contabilitate."
— OMFP nr. 2.634/2015, Anexa 2 (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Ce rezultă din cele două texte:

- Norma privind NIR-ul (OMFP 2.634/2015) descrie **funcția documentului** — recepție, încărcare în gestiune, înregistrare contabilă — dar nu impune expres cine trebuie să-l semneze sau să-l întocmească, spre deosebire, de exemplu, de Lista de inventariere, unde norma cere explicit semnătura comisiei de inventariere **și** a gestionarului.
- Legea contabilității (art. 6) leagă răspunderea de **rolul efectiv jucat** în circuitul documentului: cine l-a întocmit, cine l-a vizat/aprobat, cine l-a înregistrat — nu de titulatura postului.
- Practic, contabilul **poate** întocmi tehnic NIR-ul (mai ales când primește factura sau avizul de însoțire și datele de recepție de la gestionar/depozit), dar asumarea corectitudinii **cantitative și calitative** a recepției fizice a mărfii rămâne, în mod firesc, a persoanei care a văzut efectiv marfa la sosire — de obicei gestionarul, nu contabilul.
- NIR devine document obligatoriu doar în situațiile enumerate explicit de normă (bunuri din gestiuni diferite, primite spre prelucrare, procurate de la persoane fizice, sosite fără documente sau cu diferențe la recepție) — în restul cazurilor, recepția se face pe baza documentului de livrare (factură, aviz).

## Ce se greșește în practică

- Se presupune că legea interzice contabilului să completeze NIR-ul — nu există o asemenea interdicție explicită în normele analizate; problema reală e cine răspunde pentru datele cantitative/calitative înscrise, nu cine apasă tasta.
- Contabilul întocmește NIR-ul „din birou", pe baza facturii, fără nicio confirmare de la persoana care a primit efectiv marfa — în caz de diferențe la recepție, documentul nu reflectă realitatea, deși poartă calitatea de document justificativ.
- Se întocmește NIR și pentru situații în care norma nu-l cere ca document obligatoriu, complicând inutil circuitul, în loc să se folosească direct documentul de livrare, așa cum permite norma.

## Ce face iConta.eu

Modulul de gestiune al iConta.eu (`core/facturi.py`, `core/contare_facturi.py`) generează înregistrările contabile la recepția bunurilor pe baza facturii sau a avizului de însoțire introdus în aplicație, indiferent cine face introducerea (contabil sau gestionar) — aplicația nu impune un rol separat pentru „confirmarea recepției fizice" și nu produce un formular NIR distinct de document justificativ; conformitatea cantitativă a recepției rămâne responsabilitatea profesională a celui care confirmă datele în sistem, așa cum prevede art. 6 din Legea nr. 82/1991.

[iConta.eu](/)
