---
title: "Cum se repartizează transportul pe mai multe produse din aceeași factură?"
description: Transportul aferent mai multor produse din aceeași factură se repartizează proporțional cu costul de bază al fiecărui produs, cu restul de rotunjire alocat ultimei linii, ca suma repartizată să fie exact egală cu transportul facturat.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se repartizează transportul pe mai multe produse din aceeași factură?

Când o singură factură de transport acoperă mai multe articole dintr-o achiziție, legea cere doar ca acest cost să fie atribuit achiziției bunurilor respective, fără să impună o formulă exactă de repartizare pe mai multe articole cumpărate simultan.

## Temeiul legal

::: ghid-temei
OMFP 1802/2014, Secțiunea 1.2, pct. 6: „costul de achiziție al bunurilor cuprinde prețul de cumpărare, taxele de import și alte taxe [...] cheltuielile de transport, manipulare și alte cheltuieli care pot fi atribuibile direct achiziției bunurilor respective."
:::

Legea nu detaliază o cheie de repartizare (proporțional cu valoarea, cu greutatea sau cu cantitatea) pentru cazul în care transportul acoperă mai multe articole — cere doar atribuirea directă a costului la achiziția bunurilor. Repartizarea proporțional cu costul de bază al fiecărui articol e o interpretare rezonabilă, larg folosită în practică, dar nu un citat exact de lege — de reținut mai ales pentru mărfuri cu greutăți foarte diferite, unde o repartizare pe greutate ar putea da un rezultat diferit de cel proporțional-valoric.

## Ce se greșește în practică

- Se repartizează transportul în mod egal pe toate articolele, indiferent de valoarea lor, deși o repartizare proporțional-valorică (sau, după caz, pe greutate) reflectă mai bine costul real atribuibil fiecărui articol.
- Se lasă un rest de rotunjire nealocat, astfel încât suma repartizată pe articole nu mai coincide exact cu valoarea totală a transportului facturat.
- Se ignoră repartizarea complet atunci când marfa e introdusă în gestiune cantitativ-valorică (pe fișă de magazie), unde nu există o funcție automată de repartizare — riscul e ca transportul să rămână necapitalizat, ca o cheltuială separată, nu în costul mărfii.

## Ce face iConta.eu

Pentru firmele care țin gestiunea global-valoric, ecranul NIR repartizează automat transportul introdus, proporțional cu costul de bază al fiecărei linii din NIR, cu restul de rotunjire alocat explicit ultimei linii — verificat prin teste care confirmă, de exemplu, că un transport de 10 lei pe 3 linii cu costuri de bază egale se repartizează 3,33 + 3,33 + 3,34 lei, sumă exact egală cu transportul introdus. Pentru firmele care țin gestiunea cantitativ-valorică (pe fișă de magazie, tipic la comerțul en-gros), acest mecanism de repartizare automată nu există — contabilul trebuie să calculeze manual partea de transport pe fiecare articol și să o adauge direct la prețul unitar înainte de a introduce intrarea în gestiune.

[iConta.eu](/)
