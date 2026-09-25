---
title: "Ce fac dacă ANAF semnalează diferențe între SAF-T și declarațiile fiscale?"
description: "De ce SAF-T (D406) și declarațiile fiscale trebuie să provină din aceeași evidență contabilă și cum se abordează o diferență semnalată de ANAF."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă ANAF semnalează diferențe între SAF-T și declarațiile fiscale?

O diferență între SAF-T și declarațiile fiscale (D300, D100, D101 etc.) înseamnă, aproape întotdeauna, că cele două rapoarte nu au fost generate din exact aceeași sursă de evidență contabilă — și, pentru că amândouă decurg din aceleași documente justificative, o divergență e un semnal că undeva evidența a fost alterată, incompletă sau reconstituită diferit pentru fiecare raport.

## Temeiul legal

::: ghid-temei
„Articolul 6 (1) Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ. (2) Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea 82/1991 (Legea contabilității), art. 6 alin. (1), (2) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Ce presupune, practic, rezolvarea unei asemenea diferențe:

- Pentru că atât SAF-T, cât și declarațiile fiscale trebuie să reflecte aceleași documente justificative, primul pas e identificarea **sursei** discrepanței: o tranzacție înregistrată în declarație dar omisă din SAF-T (sau invers), o perioadă de referință diferită, sau o mapare greșită a unui cont.
- Firma are dreptul, în cadrul căilor de atac administrative sau judiciare, la accesul la fișierul standard de control fiscal folosit de organul fiscal, potrivit obligației acestuia de a pune la dispoziție „o copie sau un link care să asigure accesul la varianta electronică" a SAF-T-ului relevant.
- Corectarea unei divergențe reale (nu doar aparentă) se face, de regulă, prin declarații rectificative pentru declarația fiscală afectată și/sau prin redepunerea SAF-T-ului pentru perioada respectivă, nu prin explicații informale către organul de control.

## Ce se greșește în practică

- Se ignoră semnalarea inițială, presupunând că e o eroare de sistem a ANAF, fără a verifica efectiv dacă SAF-T și declarația provin din aceeași bază contabilă pentru perioada respectivă.
- Se corectează doar declarația fiscală, fără a redepune și SAF-T-ul aferent perioadei, lăsând cele două rapoarte în continuare divergente pentru acea lună.
- Se răspunde organului fiscal cu argumente generale, fără o reconciliere concretă, linie cu linie, care să arate exact de unde vine diferența semnalată.

## Ce face iConta.eu

iConta.eu generează atât declarațiile fiscale, cât și SAF-T-ul (D406) din aceeași evidență contabilă a firmei, iar pentru D406 aplicația are un gard intern care blochează generarea declarației dacă balanța per cont din SAF-T nu se leagă de rulajul independent din baza de date — reducând astfel riscul ca cele două rapoarte să diveargă chiar din construcție. Aplicația **nu gestionează** însă corespondența cu ANAF în cazul unei diferențe deja semnalate și nu generează automat declarațiile rectificative necesare — analiza diferenței concrete și redepunerea documentelor corectate rămân, la acest moment, sarcina contabilului.

[iConta.eu](/)
