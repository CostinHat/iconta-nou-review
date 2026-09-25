---
title: SAF-T la schimbarea anului fiscal
description: Ce se întâmplă cu obligația de raportare D406 (SAF-T) când firma trece la un an fiscal modificat (diferit de anul calendaristic) — cum se stabilesc perioadele de raportare și ce nu se schimbă.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# SAF-T la schimbarea anului fiscal

Trecerea la un an fiscal modificat (diferit de anul calendaristic) schimbă termenele pentru impozitul pe profit, dar nu schimbă mecanismul de bază al SAF-T: firma raportează D406 pentru fiecare perioadă fiscală de TVA (lună sau trimestru), la fel ca înainte.

### Ce este anul fiscal modificat

Potrivit art. 16 alin. (5) din Codul fiscal, contribuabilii care au optat, conform legislației contabile, pentru un exercițiu financiar diferit de anul calendaristic pot opta ca și anul fiscal (pentru impozit pe profit) să corespundă acestui exercițiu financiar. Primul an fiscal modificat include și perioada din anul calendaristic anterior începerii lui, ca un singur an fiscal. Opțiunea se comunică organului fiscal în 15 zile de la începerea anului fiscal modificat sau de la înregistrare.

Art. 16 alin. (5^1) reglementează situația inversă — revenirea la anul fiscal calendaristic: ultimul an fiscal modificat include perioada dintre ziua următoare ultimei zile a anului fiscal modificat și 31 decembrie, iar declarația anuală de impozit pe profit pentru acest ultim an fiscal modificat se depune până la 25 martie inclusiv a anului următor.

### Ce NU se schimbă la SAF-T

D406 (SAF-T) e o declarație informativă lunară sau trimestrială, legată de perioada fiscală de TVA a firmei (stabilită potrivit Codului fiscal, în funcție de cifra de afaceri), nu de anul fiscal pentru impozitul pe profit. Când firma trece la un an fiscal modificat:

- Perioadele de raportare SAF-T (luna/trimestrul calendaristic pentru TVA) rămân neschimbate — anul fiscal modificat afectează exclusiv calculul și declararea impozitului pe profit (plăți anticipate, declarația anuală), nu vectorul fiscal de TVA.
- Fișierul SAF-T aferent lunii/trimestrului în care are loc schimbarea de an fiscal se depune la termenul obișnuit stabilit prin OPANAF 1783/2021, Anexa 4, pct. 1 — ultima zi calendaristică a lunii următoare perioadei de raportare (lună sau trimestru). Termenul de minimum 30 de zile calendaristice de la data solicitării organului fiscal este o regulă separată, aplicabilă exclusiv secțiunii „Stocuri" a SAF-T, nu raportării generale.
- Secțiunea Header a fișierului XML raportează, ca și până acum, perioada calendaristică efectiv raportată (luna și anul), nu "anul fiscal modificat" al firmei — SAF-T nu are un câmp separat pentru anul fiscal modificat.

### Ce trebuie verificat practic

1. **Data de la care se aplică anul fiscal modificat** — se ia din decizia/comunicarea depusă la ANAF conform art. 16 alin. (5) CF, nu se presupune.
2. **Continuitatea vectorului fiscal de TVA** — schimbarea anului fiscal nu declanșează automat o schimbare de perioadă fiscală TVA (lunar/trimestrial); acestea rămân guvernate de regulile obișnuite de plafon.
3. **Situațiile financiare de închidere** — dacă firma revine la anul calendaristic (art. 16 alin. 5^1), ultimul an fiscal modificat generează o declarație de impozit pe profit distinctă, cu termen 25 martie anul următor; SAF-T-urile aferente lunilor din acea perioadă se depun separat, pe calendarul lor obișnuit.

### Concluzie practică

Pentru contabilitate, schimbarea anului fiscal e un eveniment care privește exclusiv impozitul pe profit (art. 16 CF). SAF-T continuă să fie depus lunar/trimestrial, pe perioadele calendaristice obișnuite de TVA, indiferent dacă anul fiscal al firmei coincide sau nu cu anul calendaristic.
