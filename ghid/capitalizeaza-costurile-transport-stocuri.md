---
title: "Cum se capitalizează costurile de transport la stocuri"
description: Costul de transport direct atribuibil unei achiziții se capitalizează în costul mărfii, majorând valoarea de intrare în gestiune și reducând adaosul comercial ulterior — nu se înregistrează ca o cheltuială separată de exploatare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se capitalizează costurile de transport la stocuri

„A capitaliza" transportul înseamnă a-l adăuga la costul mărfii (cont 371), nu a-l lăsa pe o cheltuială de exploatare separată — cu efect direct asupra adaosului comercial calculat la vânzare.

## Temeiul legal

::: ghid-temei
OMFP 1802/2014, Secțiunea 1.2, pct. 6: „cheltuielile de transport sunt incluse în costul de achiziție și atunci când funcția de aprovizionare este externalizată."
:::

Legea tratează transportul ca parte a costului de achiziție al bunurilor, nu ca o cheltuială separată — indiferent dacă e realizat cu mijloace proprii sau externalizat către un transportator terț. Capitalizarea corectă majorează costul de intrare al mărfii cu partea de transport aferentă, ceea ce reduce automat adaosul comercial (diferența dintre prețul de vânzare și cost), dacă prețul de vânzare rămâne neschimbat.

## Ce se greșește în practică

- Se înregistrează factura de transport direct pe o cheltuială de exploatare, fără să fie capitalizată în costul mărfii — costul de achiziție rămâne subevaluat, iar adaosul comercial calculat ulterior e artificial mai mare decât cel real.
- Se capitalizează transportul, dar fără să se repartizeze pe articole atunci când o singură factură de transport acoperă mai multe produse — riscând ca unele articole să rămână la costul de bază, fără partea de transport aferentă.
- Se presupune că mecanismul de capitalizare automată e disponibil indiferent de metoda de gestiune a stocurilor — el există doar pentru gestiunea global-valorică, nu și pentru cea cantitativ-valorică (pe fișă de magazie, CMP).

## Ce face iConta.eu

Ecranul NIR (categoria Stocuri) are un câmp dedicat pentru transport, cu contul de credit implicit 401 (furnizor de transport), configurabil de contabil. Suma introdusă e capitalizată automat, proporțional cu costul de bază al fiecărei linii din NIR, cu restul de rotunjire alocat ultimei linii, ca suma repartizată să fie exact egală cu transportul introdus — verificat prin teste, inclusiv pentru cazul în care costul de bază al liniilor e zero, situație în care aplicația respinge explicit repartizarea. Mecanismul e disponibil doar pentru firmele care țin gestiunea global-valoric; pentru gestiunea cantitativ-valorică, transportul trebuie adăugat manual la prețul unitar înainte de introducerea intrării.

[iConta.eu](/)
