---
title: "Transferuri firmă/proprietar: cum se înregistrează"
description: Banii care circulă între firmă și asociat pot fi dividend, împrumut sau regularizare de dividend interimar — fiecare are contabilitate și impozitare diferite, sub același capitol de decontări cu asociații.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Transferuri firmă/proprietar: cum se înregistrează

„Transfer către proprietar" nu e o operațiune contabilă în sine — e o denumire generică sub care se ascund, de fapt, trei situații diferite, fiecare cu regim legal și fiscal propriu: distribuirea de dividende (anuale sau trimestriale/interimare), regularizarea dividendelor interimare la finalul anului și împrumuturile reciproce firmă-asociat. Confuzia dintre ele e cea mai frecventă sursă de erori contabile la firmele mici.

## Temeiul legal

::: ghid-temei
„Cota-parte din profit ce se plătește fiecărui asociat constituie dividend."
— Legea 31/1990, art. 67 alin. (1)
:::

Restul mișcărilor de bani către/de la asociat care nu reprezintă profit distribuit cad, contabil, fie sub regimul dividendelor interimare — „Entitățile care au optat [...] să repartizeze dividende în cursul exercițiului financiar evidențiază acea repartizare în contul 463 «Creanțe reprezentând dividende repartizate în cursul exercițiului financiar» (articol contabil 463 = 456 «Decontări cu acționarii/asociații privind capitalul»)" (OMFP 1802/2014, pct. 423^1) — fie sub regimul sumelor puse la dispoziție de asociat: „Sumele depuse sau lăsate temporar de către acționari/asociați la dispoziția entității [...] se înregistrează [...] (contul 4551 «Acționari/asociați - conturi curente»)" (OMFP 1802/2014, pct. 349).

## Ce se greșește în practică

- Se înregistrează orice transfer către asociat ca „dividend", chiar și atunci când e vorba de restituirea unui împrumut pe care asociatul l-a acordat firmei anterior — ceea ce duce la impozitare greșită (dividendul se impozitează, restituirea unui împrumut nu).
- Se confundă dividendul interimar (trimestrial, cont 463/456) cu dividendul anual aprobat (cont 1171/457), deși regularizarea dintre ele e obligatorie la finalul anului.
- Nu se ține cont, de la 18 decembrie 2025, de restricția introdusă prin Legea 239/2025: o firmă care distribuie dividende trimestrial nu mai poate acorda împrumuturi asociaților până nu regularizează diferențele („Societățile care distribuie trimestrial dividende, potrivit legii, nu pot acorda acționarilor sau asociaților [...] împrumuturi, până la regularizarea diferențelor rezultate din distribuirea dividendelor în cursul anului" — Legea 31/1990, art. 67 alin. (2^3)).

## Ce face iConta.eu

Funcționalitatea **Decontări asociați** (Operațiuni speciale > Finanțare) acoperă toate cele trei tipuri de transfer firmă-asociat, cu monografia corectă pentru fiecare: dividend (anual: `1171 = 457` brut, `457 = 446` impozit; interimar: `463 = 456` brut, `456 = 446` impozit), regularizare interimar-anual (`1171 = 457`, `457 = 463`, iar la eventuală restituire de la asociat `5121 = 456`) și împrumut asociat (`5121 = 4551` la primire, `4551 = 5121` plus dobândă și impozit la restituire). Cota de impozit pe dividend e preluată automat din anul operațiunii (16% din 2026, 10% în 2025). Restricția privind împrumuturile în paralel cu dividende trimestriale neregularizate nu e blocată automat de aplicație — rămâne responsabilitatea contabilului să o verifice înainte de a înregistra un împrumut.

[iConta.eu](/)
