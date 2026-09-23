---
title: Ce fac dacă am trecut marfa expirată direct pe cheltuieli fără documente?
description: "Fără verificare faptică, aprobarea administratorului și proces-verbal, marfa expirată trecută direct pe cheltuieli riscă recalificarea ca lipsă nejustificată în gestiune: cheltuială nedeductibilă și TVA datorată."
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă am trecut marfa expirată direct pe cheltuieli fără documente?

Marfa expirată trecută direct pe cheltuieli (607), fără verificare faptică, aprobarea administratorului și proces-verbal, nu are cum să fie recunoscută ca perisabilitate sau ca bun degradat/distrus dovedit — rămâne, din perspectiva legii, o lipsă în gestiune neimputabilă și nedocumentată, cu consecințe atât la impozitul pe profit, cât și la TVA.

## Temeiul legal

::: ghid-temei
„Următoarele cheltuieli nu sunt deductibile: [...] c) cheltuielile privind bunurile de natura stocurilor sau a mijloacelor fixe amortizabile constatate lipsă din gestiune ori degradate, neimputabile, precum și taxa pe valoarea adăugată aferentă, dacă aceasta este datorată potrivit prevederilor titlului VII. Aceste cheltuieli sunt deductibile în următoarele situații/condiții: [...] 3. bunurile/mijloacele fixe amortizabile degradate calitativ, dacă se face dovada distrugerii; [...] 7. alte bunuri decât cele aflate în situațiile/condițiile prevăzute la pct. 1-6, dacă termenul de valabilitate/expirare este depășit, potrivit legii;"

*(Codul fiscal — Legea nr. 227/2015, art. 25 alin. (4) lit. c), pct. 3 și pct. 7)*
:::

## Ce înseamnă practic lipsa documentelor

Regula chapeau de la lit. c) e clară: cheltuiala cu marfă constatată lipsă sau degradată, neimputabilă, **nu e deductibilă**, plus TVA-ul aferent e datorat — cu excepția situațiilor enumerate expres (printre care pct. 3, degradare calitativă cu dovada distrugerii, și pct. 7, expirare „potrivit legii"). Fără proces-verbal de constatare, aprobarea administratorului și dovada efectivă a distrugerii, marfa expirată trecută direct pe 607 nu se poate încadra la niciuna dintre excepții — rămâne, implicit, în regula generală: nedeductibilă, cu TVA de plată.

## Cum corectezi situația

1. **Reconstitui documentația, dacă marfa există fizic sau urmele ei pot fi dovedite** — proces-verbal de constatare (verificare faptică), aprobarea administratorului, dovada distrugerii (predare la o firmă autorizată de deșeuri, casare pe bază de proces-verbal etc.).
2. **Dacă documentația nu poate fi reconstituită**, cheltuiala rămâne nedeductibilă la impozitul pe profit, iar TVA-ul dedus la achiziție trebuie ajustat — nu există altă cale de a evita aceste consecințe retroactiv.
3. **Dacă marfa se încadrează în coeficientul de perisabilitate al grupei ei** (HG 831/2004), reface nota prin motorul de perisabilități, cu procentul de limită aplicabil, în loc de o simplă notă pe 607.

## Ce se greșește în practică

- Se trece marfa expirată direct pe cheltuieli de exploatare, fără notă de perisabilitate și fără proces-verbal, ca și cum condițiile documentare ar fi opționale.
- Se presupune că simpla expirare a termenului de valabilitate, fără dovada distrugerii sau a procedurii legale de eliminare, e suficientă pentru deducere.
- Nu se ajustează TVA-ul dedus la achiziție, deși cheltuiala a rămas nedeductibilă din lipsă de documentație.

## Ce face iConta.eu

Nota de perisabilități (`core/uc_tenants.py`, funcția `nota_perisabilitati`) scrie automat descrierea sufixată „ - HG 831/2004" și separă 607 deductibil de nedeductibil pe baza procentului introdus de contabil, dar condițiile documentare (verificare faptică, aprobarea administratorului, proces-verbal) nu sunt validate programatic de aplicație — rămân responsabilitatea contabilului, în afara motorului. O notă introdusă direct pe 607, fără să treacă prin acest ecran, nu beneficiază de separarea automată deductibil/nedeductibil și trebuie corectată manual.

[iConta.eu](/)
