---
title: "Tratamentul fiscal al mesei acordate angajaților"
description: Masa acordată angajaților poate însemna, fiscal, două lucruri diferite — tichete de masă sau contravaloarea hranei acordate de angajator (hrană preparată în unități proprii ori achiziționată de la unități specializate) — iar cele două au reguli separate care nu se aplică deodată aceleiași forme de acordare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Tratamentul fiscal al mesei acordate angajaților

Înainte de a stabili tratamentul fiscal, trebuie clarificat sub ce formă se acordă efectiv masa: ca **tichet de masă** (bilet de valoare, cu regim propriu) sau ca **contravaloare a hranei acordate de angajator** (art. 76 alin. (4^1) lit. b) din Codul fiscal — hrană preparată în unități proprii sau achiziționată de la unități specializate, nu o sumă în bani). Sunt două beneficii cu reguli fiscale distincte, care nu se cumulează pe aceleași zile.

## Temeiul legal

::: ghid-temei
Codul fiscal, art. 142 lit. r): „biletele de valoare sub forma tichetelor de masă, voucherelor de vacanță, tichetelor de creșă, tichetelor culturale, acordate potrivit legii;" — nu se cuprind în baza lunară de calcul al contribuțiilor de asigurări sociale.
:::

Pentru **tichetele de masă**, regimul e clar și complet documentat: scutite de CAS (art. 142 lit. r) din Codul fiscal), dar supuse CASS 10% (art. 157 alin. (2), care retrage explicit excepția de CASS pentru tichetele de masă și voucherele de vacanță) și impozitului de 10% pe venit, calculat pe baza rămasă după scăderea CASS. Plafonul legal pentru 2026 e de 45 lei/tichet (Legea 201/2025, art. I pct. 1), valabil din noiembrie 2025.

Pentru **contravaloarea hranei acordate de angajator** — o formă distinctă de beneficiu, prevăzută separat în Codul fiscal la art. 76 alin. (4^1) lit. b) — legea precizează că „prin hrană se înțelege hrana preparată în unități proprii sau achiziționată de la unități specializate", deci hrană în natură, nu o indemnizație în bani. Plafonul neimpozabil e limitat la valoarea maximă a unui tichet de masă/persoană/zi, iar textul de lege precizează explicit că prevederile nu se aplică angajaților care beneficiază deja de tichete de masă. Cele două forme sunt, deci, alternative reciproc excluzive pentru aceeași categorie de beneficiu, nu cumulative.

## Ce se greșește în practică

- Se tratează orice formă de „masă acordată" ca fiind automat tichet de masă, fără să se verifice dacă, de fapt, angajatorul plătește o indemnizație de hrană în bani, prevăzută separat în contractul de muncă — cele două au reguli de calcul al plafonului diferite.
- Se cumulează, pentru aceeași perioadă și același angajat, tichete de masă și indemnizație de hrană în bani, deși legea prevede că regula de excludere a plafonului pentru indemnizația de hrană nu se aplică celor care au deja tichete de masă — semn că cele două nu au fost gândite ca beneficii concurente, ci alternative.
- Se descrie beneficiul de la art. 76 alin. (4^1) lit. b) ca o „indemnizație de hrană în bani", deși textul reglementează contravaloarea hranei în natură (hrană preparată în unități proprii sau achiziționată de la unități specializate), nu o sumă acordată prin statul de plată.

## Ce face iConta.eu

Modulul de beneficii (`core/beneficii_api.py`, `core/salarizare.py`) tratează tichetele de masă ca flux dedicat: calcul CASS 10% pe valoarea nominală, apoi impozit 10% pe baza rămasă, fără CAS/CAM, cu plafonul de 45 lei/tichet valabil pentru 2026 și cu numărul de tichete derivat direct din pontajul lunii confirmat. Dacă firma acordă efectiv contravaloarea hranei (hrană preparată în unități proprii sau achiziționată de la unități specializate, art. 76 alin. (4^1) lit. b)), în loc de tichete de masă, acel flux fiscal e separat de F133 și trebuie configurat distinct în statul de plată — nu se poate presupune că regulile de calcul ale tichetelor de masă se aplică automat și acolo.

[iConta.eu](/)
