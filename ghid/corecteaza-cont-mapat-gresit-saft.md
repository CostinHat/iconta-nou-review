---
title: Cum se corectează un cont mapat greșit în SAF-T?
description: O eroare de mapare descoperită după depunere se corectează prin declarație rectificativă pentru aceeași perioadă, nu printr-o cerere separată.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se corectează un cont mapat greșit în SAF-T?

Dacă un cont a fost mapat greșit într-o D406 deja depusă, corecția nu se face "pe loc", ci prin mecanismul general prevăzut de lege pentru orice eroare dintr-o declarație D406 deja transmisă: declarația rectificativă.

## Temeiul legal

::: ghid-temei
„Prima Declaraţie informativă D406 validată, depusă pentru o lună sau un trimestru de către un contribuabil/plătitor este considerată declaraţie iniţială. Declaraţiile ulterioare depuse pentru aceeaşi perioadă (lună/trimestru) sunt automat considerate declaraţii rectificative." — OPANAF nr. 1783/2021, Anexa 3, pct. 18.
:::

Legea nu tratează separat corectarea unui cont mapat greșit — orice corecție a datelor deja raportate pentru o perioadă (lună/trimestru) se face prin depunerea unei noi D406 validate pentru aceeași perioadă, care devine automat rectificativă. Nu există o procedură de "corectare punctuală" doar a secțiunii de conturi, în afara redepunerii declarației complete pentru perioada respectivă.

Rețineți și consecința sancționatorie, dacă maparea greșită a fost deja depusă: depunerea incorectă sau incompletă a fișierului SAF-T este contravenție, sancționată cu amendă de la 500 la 1.500 lei (Legea 207/2015, art. 337^1 alin. (2) lit. b)) — cu excepția prevăzută la alin. (3): corectarea până la termenul următoarei depuneri, sau corectarea ca urmare a unui fapt neimputabil, înlătură sancțiunea.

## Ce se greșește în practică

Greșeala frecventă este să se aștepte o modalitate "mai simplă" de corecție — de exemplu, o solicitare la ANAF pentru modificarea unei singure secțiuni — în loc de redepunerea integrală a declarației pentru perioada respectivă, cu maparea corectată. O altă greșeală este amânarea corecției peste termenul următoarei depuneri, ceea ce elimină exceptarea de la sancțiune prevăzută la art. 337^1 alin. (3).

## Ce face iConta.eu

Generatorul D406 (`core/d406.py`) produce fișierul pe baza planului de conturi curent al firmei din baza de date (`core/repo_d406.py`). Corectarea unei mapări greșite presupune actualizarea planului de conturi al firmei și regenerarea + revalidarea fișierului pentru perioada respectivă (cu `DUKIntegrator`, `core/duk.py`), înainte de a-l depune ca declarație rectificativă, conform procedurii legale de mai sus.

[iConta.eu](/)
