---
title: "Cum elimin un cod CAEN din actul constitutiv?"
description: "Ce majoritate de vot cere Legea 31/1990 pentru modificarea actului constitutiv al unei societăți, procedură prin care se elimină și un cod CAEN din obiectul de activitate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum elimin un cod CAEN din actul constitutiv?

Eliminarea unui cod CAEN din obiectul de activitate al firmei nu e o operațiune de sine stătătoare, cu procedură proprie — e, juridic, o modificare a actului constitutiv, supusă acelorași reguli de cvorum și majoritate ca orice altă schimbare a actului societății.

## Temeiul legal

::: ghid-temei
„Adunarea generală decide prin votul reprezentând majoritatea absolută a asociaților și a părților sociale, în afară de cazul când în actul constitutiv se prevede altfel."
— Legea 31/1990, art. 192 alin. (1) (sursă: anaf_surse/legea_31_1990_societatile.txt)

„Când pe ordinea de zi figurează propuneri pentru modificarea actului constitutiv, convocarea va trebui să cuprindă textul integral al propunerilor."
— Legea 31/1990, art. 117 alin. (7) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

Onest, despre limita acestei surse pentru întrebarea concretă: sursele disponibile pentru acest ghid **nu conțin un text dedicat explicit procedurii de eliminare a unui cod CAEN**, ca operațiune distinctă. Ce se poate confirma cu temei legal e principiul general aplicabil oricărei modificări a obiectului de activitate:

- La societatea cu răspundere limitată, modificarea actului constitutiv (deci și eliminarea unui cod CAEN din obiectul de activitate) se decide, potrivit art. 192 alin. (1), cu **majoritatea absolută a asociaților și a părților sociale**, dacă actul constitutiv nu prevede altfel — regula unanimității care exista anterior pentru modificări a fost abrogată în 2022, iar acum majoritatea absolută e regula implicită.
- La societatea pe acțiuni, art. 117 alin. (7) impune ca, ori de câte ori pe ordinea de zi figurează o propunere de modificare a actului constitutiv, **convocarea adunării generale să cuprindă textul integral al propunerii** — deci și textul exact al eliminării codului CAEN vizat.
- Procedura administrativă efectivă — depunerea cererii de mențiuni la Oficiul Registrului Comerțului, actualizarea certificatului constatator, eventuale radieri sau notificări către alte instituții (dacă activitatea eliminată era autorizată separat) — ține de legislația specifică registrului comerțului, care nu se regăsește în sursele disponibile pentru acest ghid. Acest ghid nu poate, deci, confirma cu citat exact pașii administrativi de depunere a mențiunii de eliminare a codului CAEN.

## Ce se greșește în practică

- Se tratează eliminarea unui cod CAEN ca pe o simplă actualizare administrativă, fără hotărâre formală a asociaților/acționarilor cu majoritatea cerută pentru modificarea actului constitutiv.
- Se convoacă adunarea generală fără a include în convocator textul integral al propunerii de modificare, deși legea impune explicit acest lucru atunci când pe ordinea de zi apare o modificare a actului constitutiv.
- Se elimină codul CAEN din actul constitutiv fără verificarea prealabilă dacă activitatea respectivă era autorizată separat (de exemplu prin declarație pe proprie răspundere privind îndeplinirea condițiilor de funcționare), caz în care pot fi necesare demersuri suplimentare, nereglementate în sursele disponibile pentru acest ghid.

## Ce face iConta.eu

iConta.eu preia codul CAEN principal al firmei din API-ul public ANAF, la momentul configurării profilului firmei (`core/anaf_api.py`, `core/tenant_provisioning.py`), pentru completarea automată a datelor de identificare. La data acestui ghid, iConta.eu **nu gestionează modificarea actului constitutiv** și nu inițiază sau urmărește cereri de mențiuni la Registrul Comerțului pentru adăugarea sau eliminarea unor coduri CAEN din obiectul de activitate — această procedură rămâne complet în afara aplicației, la nivelul asociaților/acționarilor și al registrului comerțului.

[iConta.eu](/)
