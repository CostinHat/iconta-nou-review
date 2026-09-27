---
title: Ce fac dacă nu am stornat avansul la factura finală?
description: Dacă factura finală nu a scăzut avansul facturat, TVA aferentă avansului a fost colectată de două ori; eroarea se corectează printr-o factură de corecție conform Codului fiscal art. 330 alin. (1) lit. b), declarată în decontul curent, iar clientul își corectează deducerea.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă nu am stornat avansul la factura finală?

Emite o factură de corecție care stornează avansul, cu trimitere la factura finală. Până la corecție, TVA aferentă avansului apare de două ori: o dată pe factura de avans și încă o dată pe factura finală, emisă la valoarea întreagă. Clientul are aceeași eroare în oglindă: a dedus TVA de două ori și figurează că datorează mai mult decât prețul contractului.

### Regula de la factura finală

TVA pentru avans devine exigibilă la încasarea avansului (Codul fiscal art. 282 alin. (2) lit. b)). La livrare, avansul facturat se scade. Normele metodologice aprobate prin HG nr. 1/2016, pct. 35, arată în exemple: „La data livrării se vor storna avansul și taxa pe valoarea adăugată aferentă acestuia [...] cu semnul minus.”

### Cum corectezi

Factura finală a fost deja transmisă clientului, deci se aplică Codul fiscal art. 330 alin. (1) lit. b). Ai două variante:
- o singură factură nouă, care cuprinde valorile facturii finale cu semnul minus, numărul și data ei și, pe de altă parte, valorile corecte, adică valoarea integrală și stornarea avansului;
- o factură cu valorile facturii finale cu semnul minus, cu numărul și data acesteia, emisă concomitent cu o factură finală corectă, care include stornarea avansului.

Pentru un client B2B, factura de corecție se transmite în RO e-Factura.

### Cum declari

- **Furnizorul** înregistrează factura de corecție în jurnalul de vânzări al lunii în care o emite. Dacă factura finală greșită a fost declarată într-un decont anterior, reducerea TVA colectate se declară la rândul 16 din D300. Instrucțiunile D300 (OPANAF nr. 174/2026) nu permit decontul rectificativ pentru corectarea deconturilor anterioare.
- **Clientul** își reduce TVA dedusă. Corecția taxei deduse din deconturile anterioare se face la rândul 33 din D300.

### Semnalul din contabilitate

Eroarea se vede ușor în balanță, după factura finală:
- contul 419 „Clienți - creditori” rămâne cu sold creditor egal cu avansul;
- soldul clientului în 4111 este mai mare decât ce are de încasat;
- TVA colectată pe operațiune depășește cota aplicată la prețul contractului.

La corecție, se stornează avansul: 419 = 4111 cu valoarea fără TVA, iar TVA avansului se stornează în roșu în 4427.

### Exemplu

Contract de 100.000 lei plus TVA 21%. În aprilie se încasează un avans de 30.000 lei plus 6.300 lei TVA, cu factură de avans. În iunie, factura finală este emisă la 100.000 lei plus 21.000 lei TVA, fără stornarea avansului. TVA colectată totală devine 27.300 lei, în loc de 21.000 lei.

În august se descoperă eroarea. Furnizorul emite o factură de corecție care reia factura din iunie cu minus (-100.000 lei și -21.000 lei TVA) și valorile corecte: 100.000 lei și 21.000 lei TVA, minus avansul de 30.000 lei și 6.300 lei TVA. Efectul net este de -6.300 lei TVA, declarat în D300 pe august la rândul 16. Clientul reduce TVA dedusă cu 6.300 lei, la rândul 33. În balanța furnizorului, 419 se închide, iar clientul rămâne cu 84.700 lei de plată.

### Ce verifici înainte

1. Dacă avansul a fost încasat în altă cotă de TVA, stornarea se face la cota aplicată avansului, iar factura finală se regularizează la cota de la livrare.
2. Dacă avansul a fost în valută, stornarea se face la cursul folosit pentru avans (HG nr. 1/2016, pct. 35 alin. (2)).

### De reținut
- La livrare, avansul și TVA aferentă se stornează cu semnul minus (HG nr. 1/2016, pct. 35).
- Omisiunea se corectează prin factură de corecție (Codul fiscal art. 330 alin. (1) lit. b)), nu prin anularea facturii finale.
- Furnizorul declară corecția la rândul 16 din D300, clientul la rândul 33. Nu se depune decont rectificativ.
- Soldul rămas în 419 după factura finală este principalul semn al erorii.
