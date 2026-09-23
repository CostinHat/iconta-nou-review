---
title: "La ce dată se face descărcarea de gestiune: factură sau livrare?"
description: Când se răspunde DA la poartă, mișcarea de stoc se datează cu data facturii — nu există un câmp separat de "dată livrare" pe factura cu marfă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# La ce dată se face descărcarea de gestiune: factură sau livrare?

Când, la emiterea unei facturi cu marfă din stoc, se răspunde "DA" la poarta "pleacă marfa acum?", mișcarea de stoc rezultată se datează cu data facturii (data de emitere aleasă), nu cu o dată de livrare separată. Nu există, în fluxul de emitere a facturii, un câmp distinct în care să se introducă o dată de livrare diferită de data facturii — poarta e o întrebare DA/NU, nu o programare la o dată viitoare.

## Temeiul legal

::: ghid-temei
"441. - (1) Veniturile din vânzarea bunurilor se recunosc în momentul în care sunt îndeplinite următoarele condiții: a) entitatea a transferat cumpărătorului riscurile şi avantajele semnificative care decurg din proprietatea asupra bunurilor;"
— OMFP 1802/2014, pct. 441 alin. (1)
:::

Criteriul legal e transferul riscurilor și avantajelor, care de regulă coincide cu predarea mărfii. Când operatorul confirmă "DA, marfa pleacă acum" la emiterea facturii, declară practic că acest transfer are loc chiar atunci — de aceea data descărcării coincide cu data facturii, nu cu o dată separată.

## Ce se greșește în practică

- Se caută pe factura cu marfă un câmp de "dată livrare" separat de data facturii — nu există un asemenea câmp în mecanismul poartă DA/NU; data descărcării e mereu data facturii (sau data curentă, dacă data de emitere lipsește).
- Se răspunde "DA" la poartă chiar și atunci când livrarea reală va avea loc la o dată ulterioară — răspunsul "DA" înseamnă explicit că marfa pleacă acum, deci descărcarea se datează cu ziua facturii; dacă livrarea e ulterioară, răspunsul corect e "Nu", urmat de descărcare manuală ulterioară, la data reală.
- Se presupune că data descărcării poate fi corectată ulterior, direct pe mișcarea generată prin poartă, ca și cum ar fi un câmp editabil separat — data provine din data facturii la momentul emiterii, nu dintr-un formular independent.

## Ce face iConta.eu

La răspunsul "DA" dat la poarta obligatorie, iConta.eu descarcă gestiunea în aceeași operațiune cu emiterea facturii, iar mișcarea de stoc rezultată primește data de emitere a facturii (sau data curentă, dacă data de emitere nu a fost completată). Același principiu se aplică identic și facturilor emise prin API, pentru integratori: data descărcării e data facturii trimise în cerere, nu o dată de livrare separată.

Menționăm onest: dacă data reală a livrării diferă de data facturii, mecanismul poartă DA/NU nu are cum să reflecte asta direct pe factură — soluția corectă e răspunsul "Nu, doar factură" la emitere, urmat de descărcarea manuală a stocului, la data reală de livrare, din ecranul de stocuri.

[iConta.eu](/)
