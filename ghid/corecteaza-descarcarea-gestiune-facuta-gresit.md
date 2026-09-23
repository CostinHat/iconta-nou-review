---
title: "Cum se corectează descărcarea de gestiune făcută greșit într-un restaurant?"
description: O descărcare greșită (număr de porții greșit, dată greșită) nu se poate „edita" direct — se corectează printr-o operațiune inversă sau printr-o notă de regularizare, cu atenție la ordinea cronologică a mișcărilor de stoc.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se corectează descărcarea de gestiune făcută greșit într-un restaurant?

O descărcare de gestiune pe rețetă (înregistrarea consumului de ingrediente pentru un număr de porții vândute) generează simultan mișcări de ieșire din stoc și o notă contabilă. Dacă descărcarea a fost greșită — număr de porții greșit, rețetă greșită selectată sau dată greșită — corectarea trebuie să anuleze efectele exacte ale operațiunii greșite, nu doar să adauge una nouă peste ea.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ." — Legea contabilității nr. 82/1991, art. 6 alin. (1)
:::

## Pașii de corectare

1. **Identifică nota contabilă și mișcările de stoc generate de descărcarea greșită** — data operațiunii, ingredientele afectate și cantitățile scăzute din gestiune.
2. **Dacă nota e încă ciornă**, poate fi corectată sau ștearsă direct din jurnal — dar ștergerea notei nu anulează singură mișcările de stoc deja generate; ambele trebuie tratate împreună.
3. **Dacă nota a fost deja validată**, corectarea se face printr-o operațiune inversă (o notă de regularizare care repune în gestiune ingredientele scăzute greșit), urmată, dacă e cazul, de o nouă descărcare corectă, cu numărul real de porții sau rețeta corectă.
4. **Atenție la ordinea cronologică**: o corectare introdusă cu o dată anterioară altor mișcări de stoc deja înregistrate poate intra în conflict cu soldurile calculate ulterior — verificarea cronologică a stocului respinge o ieșire care ar „sparge" soldurile deja existente pe fișa de magazie.

## Ce se greșește în practică

- Se face o nouă descărcare „ca să compenseze" fără să se anuleze mai întâi efectele celei greșite — rezultatul e un stoc dublu distorsionat, nu unul corectat.
- Se corectează doar nota contabilă, fără să se atingă mișcările de stoc generate de aceeași descărcare — stocul rămâne greșit chiar dacă jurnalul contabil arată corect.
- Se introduce o corectare cu dată anterioară altor operațiuni deja înregistrate, fără să se verifice dacă asta ar afecta soldurile ulterioare deja calculate.

## Ce face iConta.eu

Fiecare descărcare de rețetă generează, împreună, mișcările de stoc și o notă contabilă ciornă — cele două sunt legate, nu independente. La orice ieșire nouă introdusă în stoc (inclusiv o corectare cu dată anterioară), aplicația reface fișa de magazie cronologic și respinge operațiunea dacă ar sparge soldurile deja înregistrate ulterior ei, afișând o eroare explicită în loc să înregistreze tacit o corectare inconsecventă. Ștergerea unei rețete din rețetar nu atinge însă mișcările de stoc deja generate de descărcări anterioare — corectarea unei descărcări greșite rămâne o operațiune manuală, prin notă de regularizare.

[iConta.eu](/)
