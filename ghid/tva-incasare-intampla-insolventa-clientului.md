---
title: TVA la încasare: ce se întâmplă la insolvența clientului
description: Dacă un client persoană juridică intră în faliment sau reorganizare judiciară confirmată, TVA neexigibilă poate fi ajustată prin art. 287 lit. d) Cod fiscal; în lipsa unei asemenea proceduri, simpla neplată nu declanșează nicio exigibilitate forțată.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# TVA la încasare: ce se întâmplă la insolvența clientului

Un client care nu plătește o factură nu înseamnă automat „insolvență" în sensul legii TVA. Diferența contează enorm pentru o firmă aflată în sistemul TVA la încasare, pentru că răspunsul e complet diferit după cum clientul e doar în întârziere sau a intrat efectiv într-o procedură judiciară de insolvență.

## Temeiul legal

::: ghid-temei
**Art. 282 alin. (3) din Codul fiscal (Legea 227/2015)**: *„Prin excepție de la prevederile alin. (1) și alin. (2) lit. a), exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, în cazul persoanelor impozabile care optează în acest sens..."*

**Art. 287 lit. d) CF** (rezumat din dosarul de cercetare, fără text exact citat în sursă): ajustarea bazei de impozitare e permisă la intrarea în faliment a beneficiarului sau la un plan de reorganizare judiciară confirmat prin hotărâre judecătorească, în termen de 5 ani de la 1 ianuarie a anului următor hotărârii.

**Art. 287 lit. f) CF** (rezumat din dosar): ajustarea pentru neîncasare se aplică **doar pentru beneficiari persoane fizice**, în 12 luni de la termenul de plată sau de la emiterea facturii, condiționată de dovada unor măsuri de recuperare a creanței, cu termen de ajustare de 5 ani.
:::

## Ce înseamnă practic

Pentru un client **persoană juridică**, legea prevede o singură cale de ajustare: intrarea efectivă în faliment sau confirmarea judecătorească a unui plan de reorganizare (art. 287 lit. d)). Doar din acel moment poate fi ajustată baza de impozitare, ceea ce scoate practic TVA-ul din contul de „neexigibil" (4428) fără să mai aștepți încasarea efectivă.

Dacă clientul e doar în întârziere de plată — oricât de veche — dar nu a intrat într-o procedură de insolvență confirmată judiciar, nu există alt mecanism legal de ajustare pentru PJ. Excepția de la art. 287 lit. f) (ajustare după 12 luni de neîncasare) se aplică **strict clienților persoane fizice**, nu firmelor. TVA rămâne pur și simplu neexigibilă, cât timp firma ta rămâne înscrisă în sistem, indiferent cât timp a trecut.

## Ce se greșește în practică

- **Se aplică regula celor 12 luni de la art. 287 lit. f) și la clienți persoane juridice.** Textul se referă explicit doar la beneficiari persoane fizice.
- **Se confundă „clientul nu plătește" cu „clientul e insolvent".** Ajustarea de la art. 287 lit. d) presupune o procedură judiciară confirmată (faliment sau plan de reorganizare), nu o simplă restanță.
- **Se ajustează TVA-ul înainte de hotărârea judecătorească**, pe baza unei proceduri de insolvență doar deschise, nu confirmate.

## Ce face iConta.eu

Motorul de decont (`core/d300.py`) nu introduce în decont sumele neîncasate atât timp cât factura rămâne pe TVA la încasare — indiferent de vechime, ele rămân în 4428 până la momentul încasării. Pentru evenimentul de ajustare la faliment/reorganizare judiciară a clientului (art. 287 lit. d)), tratamentul rămâne, conform cercetării de față, o operațiune manuală a contabilului, pe baza hotărârii judecătorești — nu am confirmat în cod o ramură automată dedicată acestui eveniment.

[iConta.eu](/)
