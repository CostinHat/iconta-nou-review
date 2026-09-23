---
title: "Monografia distribuirii dividendelor în 2026"
description: "De la 1 ianuarie 2026 cota de impozit pe dividende este 16%, iar distribuirea trimestrială atrage și restricții noi privind împrumuturile către asociați."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Monografia distribuirii dividendelor în 2026

Distribuirea dividendelor în 2026 aduce două schimbări față de anii anteriori: cota de impozit crește la 16%, iar firmele care distribuie trimestrial nu mai pot, în paralel, să împrumute asociații până nu regularizează diferențele din distribuirea în cursul anului.

## Temeiul legal

::: ghid-temei
„Veniturile sub formă de dividende [...] se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final." — Codul fiscal, art. 97 alin. (7), în forma dată de Legea 141/2025, art. II pct. 5, aplicabilă dividendelor distribuite începând cu 1 ianuarie 2026
:::

Monografia rămâne aceeași ca structură ca în anii anteriori, doar cota de impozit se schimbă:

- **Dividend anual (final)**: repartizare din profit — 1171 = 457 (brut); impozit reținut — 457 = 446 (16% din brut); plata netă — 457 = 5121.
- **Dividend interimar (trimestrial)**: 463 = 456 (brut); impozit — 456 = 446 (16%); plata netă — 456 = 5121.
- **Regularizare la final de an**: 1171 = 457 (dividend anual aprobat), compensare cu interimarul — 457 = 463; dacă interimarul distribuit depășește dividendul anual aprobat, excesul se restituie de la asociat — 5121 = 456, în termen de 60 de zile de la aprobarea situațiilor financiare anuale (Legea 31/1990, art. 67 alin. 2^2).

Nou pentru 2026: societățile care distribuie trimestrial dividende nu pot acorda împrumuturi asociaților până la regularizarea diferențelor rezultate din distribuirea din cursul anului (art. 67 alin. 2^3, introdus de Legea 239/2025, în vigoare din 18.12.2025). Restricția privește împrumuturile acordate **de firmă asociatului**, nu invers — un asociat poate în continuare credita firma fără nicio legătură cu acest alineat.

## Ce se greșește în practică

Cea mai frecventă greșeală e aplicarea cotei vechi (10%, valabilă în 2025) pentru dividende aprobate/distribuite după 1 ianuarie 2026 — cota se aplică la data distribuirii, nu la data la care s-a făcut profitul. A doua greșeală e ignorarea noii restricții de la alin. (2^3): o firmă care distribuie dividende trimestrial și, în paralel, acordă un împrumut asociatului înainte de regularizare, încalcă legea, indiferent dacă aplicația contabilă permite tehnic înregistrarea.

## Ce face iConta.eu

iConta citește cota de impozit pe dividende dintr-un registru intern, în funcție de data la care are loc distribuirea (16% de la 01.01.2026, 10% în 2025), și generează notele pentru dividendul anual, cel interimar și regularizarea de final de an, inclusiv cazul restituirii de exces. Motorul din spatele acestor note nu verifică însă restricția nouă de la art. 67 alin. (2^3): funcția care generează nota de restituire către asociat pe contul curent (4551=5121) nu verifică dacă firma are dividende interimare neregularizate în anul respectiv — respectarea acestei restricții rămâne în sarcina contabilului, nu e o validare automată în aplicație.

[iConta.eu](/)
