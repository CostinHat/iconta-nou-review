---
title: Cum se contabilizează downgrade-ul unui abonament SaaS plătit în avans?
description: Tratamentul contului 472 „Venituri înregistrate în avans" (furnizor) și 471 „Cheltuieli înregistrate în avans" (beneficiar) când valoarea unui abonament plătit anticipat se reduce pe parcursul perioadei.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează downgrade-ul unui abonament SaaS plătit în avans?

Un abonament software plătit în avans (anual sau trimestrial) intră, la momentul încasării/plății, în conturile de regularizare pentru venituri/cheltuieli în avans, indiferent dacă e privit din perspectiva furnizorului sau a beneficiarului serviciului. Un downgrade pe parcursul perioadei plătite recalculează valoarea rămasă de eșalonat.

### Recunoașterea inițială

Reglementările contabile (OMFP nr. 1802/2014):

**La furnizorul SaaS** — pct. din grupa 47: Contul 472 "Venituri înregistrate în avans" — "Cu ajutorul acestui cont se ține evidența veniturilor efectuate în avans... În creditul contului 472 se înregistrează: veniturile înregistrate în avans, aferente perioadelor/exercițiilor financiare următoare, cum sunt: sumele facturate sau încasate din chirii, abonamente, asigurări, sume aferente prestării ulterioare de servicii... În debitul contului 472 se înregistrează: veniturile înregistrate în avans și aferente perioadei curente sau exercițiului financiar în curs (704, 705, 706, 708, 766)."

```
La facturare/încasare:  5121/4111 = 472 (valoarea totală a abonamentului pe perioada plătită)
Lunar, pe măsura consumării: 472 = 704/708 (cota-parte aferentă lunii)
```

**La beneficiar** (dacă abonamentul e semnificativ și entitatea recunoaște cheltuiala eșalonat) — contul simetric este 471 "Cheltuieli înregistrate în avans": "Cu ajutorul acestui cont se ține evidența cheltuielilor efectuate în avans care urmează a se suporta eșalonat pe cheltuieli, pe baza unui scadențar, în perioadele/exercițiile financiare viitoare."

```
La facturare/plată: 471 = 401/5121
Lunar: 628 (sau contul de cheltuială aferent) = 471
```

### Tratamentul downgrade-ului

Downgrade-ul reduce valoarea rămasă a abonamentului pentru perioada neconsumată încă — practic, se recalculează scadențarul de eșalonare pornind de la data efectivă a schimbării de plan:

1. **Se determină soldul rămas neconsumat** din 472 (la furnizor) sau 471 (la beneficiar), la data downgrade-ului.
2. **Dacă downgrade-ul presupune o rambursare parțială** a diferenței de preț către client: furnizorul stornează/reduce soldul din 472 cu suma rambursată (472 = 5121, ieșire de trezorerie) sau, dacă rambursarea se face sub formă de credit pentru perioade viitoare, soldul din 472 rămâne, dar eșalonarea ulterioară se face la noua valoare lunară (mai mică), pe perioada rămasă.
3. **Dacă downgrade-ul nu presupune rambursare**, ci doar reducerea nivelului de serviciu pentru restul perioadei deja plătite (fără ajustare de preț): nu apare o modificare contabilă — suma din 472/471 continuă să se eșaloneze conform scadențarului inițial, întrucât obligația contractuală de prestare a fost deja stinsă financiar prin plata inițială, indiferent de nivelul de funcționalități oferite ulterior.

### Punct de atenție fiscal

Dacă downgrade-ul generează o rambursare efectivă, iar factura inițială includea TVA, rambursarea parțială a prețului impune emiterea unei facturi de stornare/credit note pentru diferența de bază de impozitare, cu regularizarea corespunzătoare a TVA colectată/dedusă — nu doar o simplă mișcare între conturile de regularizare, fără document fiscal aferent.
