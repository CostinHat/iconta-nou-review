---
title: "Ce fac dacă am folosit baza de calcul greșită pentru contribuții?"
description: "Procedura de corectare a unei declarații fiscale (inclusiv D112) când baza de calcul a contribuțiilor a fost stabilită greșit, conform art. 105 din Codul de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă am folosit baza de calcul greșită pentru contribuții?

O bază de calcul greșită la contribuțiile sociale (CAS, CASS) sau la impozitul pe venit din salarii înseamnă, practic, o declarație D112 depusă cu sume incorecte. Legea nu tratează asta ca pe o infracțiune, ci ca pe o situație normală, cu o procedură dedicată: corectarea prin declarație rectificativă.

## Temeiul legal

::: ghid-temei
„ART. 105 Corectarea declarației fiscale
(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale.
[...]
(3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative.
[...]
(5) Declarația de impunere nu poate fi depusă și nu poate fi corectată după anularea rezervei verificării ulterioare.
(6) Prin excepție de la prevederile alin. (5), declarația de impunere poate fi depusă sau corectată după anularea rezervei verificării ulterioare în următoarele situații:
a) în situația în care corecția se datorează îndeplinirii sau neîndeplinirii unei condiții prevăzute de lege care impune corectarea bazei de impozitare și/sau a creanței fiscale aferente;"
— Legea 207/2015 (Codul de procedură fiscală), art. 105 alin. (1), (3), (5), (6) lit. a) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce înseamnă asta concret pentru o eroare de bază de calcul la contribuții:

- **Termenul de corectare** e cel al prescripției dreptului organului fiscal de a stabili creanțe fiscale — în regulă generală, **5 ani** de la 1 iulie a anului următor celui pentru care se datorează obligația (art. 110). Nu există un termen scurt de câteva zile sau luni în care corecția „mai e permisă" — dincolo de asta, nu.
- **Instrumentul** e declarația rectificativă — se depune o nouă D112 pentru luna/perioada afectată, cu bazele de calcul corectate, nu o „cerere de îndreptare" separată.
- **Limita** e alin. (5): odată anulată rezerva verificării ulterioare pentru acea perioadă (de regulă, după o inspecție fiscală finalizată), declarația nu mai poate fi corectată decât în situațiile de excepție de la alin. (6) — de exemplu, dacă apare o hotărâre judecătorească ce modifică baza de impozitare.
- Dacă din corecție rezultă sume suplimentare de plată, se datorează dobânzi de la scadența inițială (art. 173 și urm.), nu de la data depunerii rectificativei — corectarea nu „resetează" ceasul dobânzilor.

## Ce se greșește în practică

- Se așteaptă până la finalul anului sau până la un eventual control pentru a corecta, deși legea permite (și, practic, recomandă) corectarea imediat ce eroarea e descoperită — cu cât întârzie corecția, cu atât cresc dobânzile aferente diferenței de plată.
- Se depune o declarație rectificativă doar pentru luna curentă, deși baza de calcul greșită a fost folosită consecutiv pe mai multe luni — fiecare lună afectată are nevoie de propria rectificativă, pentru perioada fiscală respectivă.
- Se presupune că declarația nu mai poate fi corectată deloc după o inspecție fiscală, ignorând excepțiile explicite de la art. 105 alin. (6).

## Ce face iConta.eu

Generatorul XML pentru D112 din iConta.eu (`core/d112.py`) marchează în prezent, la nivel de cod, declarația exclusiv ca inițială (`d_rec="0"`, valoare fixă în funcția de generare a antetului) — nu există încă suport pentru marcarea unei declarații D112 ca rectificativă (`d_rec="1"`). Alte declarații din aplicație (de exemplu D119, D120, D201, D212, D213, D318) au acest flag implementat dinamic; D301 are, la rândul ei, `d_rec="0"` fix în generarea XML, ca și D112. Până la extinderea suportului și la D112, o corecție de bază de calcul pentru contribuții se pregătește în afara acestui flux automat, cu marcarea manuală a caracterului rectificativ conform procedurii ANAF.

[iConta.eu](/)
