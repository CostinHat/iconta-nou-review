---
title: "Cum se completează codul L în D390?"
description: Codul L identifică livrarea intracomunitară de bunuri, e mapat automat de aplicație și cere obligatoriu codul de TVA al cumpărătorului din alt stat membru.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se completează codul L în D390?

Codul **L** desemnează livrarea intracomunitară de bunuri din România către alt stat membru. Este primul tip de operațiune din nomenclatorul D390 și, în aplicație, este tipul implicit pentru orice factură emisă către un client dintr-un alt stat membru UE.

## Temeiul legal

::: ghid-temei
**OPANAF 705/2020, Anexa 2, Instrucțiuni pct. 1 lit. a)**:
> „Se completează cu tranzacţiile intracomunitare efectuate, în următoarea ordine: a) livrări intracomunitare de bunuri (L) [...]"

**Coloana „Cod operator intracomunitar" pentru L**:
> „în cazul livrărilor intracomunitare de bunuri (L) efectuate din România - codul de identificare în scopuri de TVA al persoanei care achiziţionează bunurile în alt stat membru decât România, pe baza căruia furnizorul din România i-a efectuat o livrare intracomunitară scutită de TVA conform art. 294 alin. (2) lit. a) şi d) din Codul fiscal."
:::

Codul de TVA trecut la L este deci al cumpărătorului din celălalt stat membru, cel pe baza căruia a fost aplicată scutirea de TVA la livrare — nu al firmei tale. Codul de operator este obligatoriu pentru tipul L.

## Ce se greșește în practică

O greșeală frecventă este să se creadă că orice factură emisă către un client UE trebuie completată manual în D390 — de regulă nu e cazul, pentru că orice factură intracomunitară emisă este mapată implicit pe L. Riscul apare invers: omiterea verificării codului de TVA al cumpărătorului înainte de depunere, pentru că o eroare aici trece adesea neobservată la introducere (vezi limitarea privind verificarea codurilor de TVA, mai jos).

## Ce face iConta.eu

Orice factură emisă către un partener dintr-un alt stat membru este clasificată implicit pe **L**, fără intervenție. Poți schimba tipul acesteia (de exemplu în T sau P) din panoul de clasificare D390 (pasul 2 al declarației), dacă operațiunea reală e alta decât o livrare simplă de bunuri.

**Atenție la o limitare curentă**: pentru facturile create prin ecranul dedicat „Livrare intracomunitară" (nu prin ecranul obișnuit de emitere), aplicația reține pe factură, la creare, axa bunuri/servicii — o decizie de cod recentă (16.09.2026), aterizată chiar înaintea ultimei verificări a acestui dosar. Pe baza codului citit, pentru astfel de facturi tipul D390 pare să fie determinat definitiv de axa înregistrată pe factură, iar reclasificarea din panoul D390 să nu mai producă efect asupra declarației generate — deși ecranul de clasificare rămâne, aparent, activ și salvarea pare reușită. Nu am găsit, la verificarea codului, niciun mesaj care să semnaleze această limitare în interfață, așa că recomandăm verificarea comportamentului curent din aplicație înainte de a te baza pe reclasificare pentru o factură emisă prin acest ecran dedicat. Pentru facturile emise prin ecranul obișnuit de facturare, reclasificarea funcționează fără nicio restricție cunoscută.

[iConta.eu](/)
