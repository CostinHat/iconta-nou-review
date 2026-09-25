---
title: "Ce verifică ANAF la facturile primite de la furnizori inactivi?"
description: "Ce pierde firma beneficiară, potrivit Codului fiscal, când deduce cheltuieli sau TVA pe baza facturilor primite de la un furnizor înscris ca inactiv în Registrul contribuabililor inactivi."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce verifică ANAF la facturile primite de la furnizori inactivi?

Din perspectiva firmei care primește factura, întrebarea nu e dacă furnizorul a greșit ceva, ci dacă ea, ca beneficiar, mai are dreptul de deducere. Legea răspunde clar: primirea unei facturi emise de un contribuabil deja înscris ca inactiv anulează, de regulă, atât deducerea cheltuielii, cât și a TVA-ului aferent.

## Temeiul legal

::: ghid-temei
„Beneficiarii care achiziționează bunuri și/sau servicii de la persoane impozabile stabilite în România, după înscrierea acestora ca inactivi în Registrul contribuabililor inactivi/reactivați conform Codului de procedură fiscală, nu beneficiază de dreptul de deducere a cheltuielilor și a taxei pe valoarea adăugată aferente achizițiilor respective, cu excepția achizițiilor de bunuri efectuate în cadrul procedurii de executare silită și/sau a achizițiilor de bunuri/servicii de la persoane impozabile aflate în procedura falimentului [...]"
— Legea 227/2015, art. 11 alin. (7) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Următoarele cheltuieli nu sunt deductibile: [...] j) cheltuielile înregistrate în evidența contabilă, care au la bază un document emis de un contribuabil declarat inactiv conform prevederilor Codului de procedură fiscală [...]"
— Legea 227/2015, art. 25 alin. (4) lit. j) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Punctul de control, pentru facturile primite de firmă:

- Criteriul decisiv e **data facturii**, raportată la **perioada în care furnizorul figura ca inactiv** în registru — nu contează dacă factura a fost plătită sau dacă marfa a fost efectiv livrată.
- Consecința e dublă: se pierde atât deductibilitatea cheltuielii la calculul rezultatului fiscal, cât și dreptul de deducere a TVA aferent, cu excepția executării silite și a achizițiilor de la furnizori în faliment.
- Dacă furnizorul e ulterior reactivat, beneficiarul poate recupera deducerea, dar mecanismul diferă: dacă inactivitatea și reactivarea sunt în același an fiscal, ajustarea se face în trimestrul reactivării; dacă sunt în ani fiscali diferiți, e nevoie de declarație rectificativă pentru anul la care se referă cheltuielile.

## Ce se greșește în practică

- Se presupune că buna-credință a beneficiarului (nu știa că furnizorul e inactiv) înlătură sancțiunea fiscală — legea nu prevede o astfel de excepție bazată pe buna-credință, ci doar excepțiile explicite de executare silită și faliment.
- Se tratează toate facturile primite de la un furnizor ulterior inactivat ca fiind afectate, deși doar cele emise **după** înscrierea în Registrul contribuabililor inactivi sunt vizate — cele anterioare rămân deductibile normal.
- Se omite ajustarea rezultatului fiscal la reactivarea furnizorului, deși legea oferă explicit calea recuperării deducerii pierdute, cu declarație rectificativă dacă reactivarea are loc într-un an fiscal diferit de cel al inactivării.

## Ce face iConta.eu

La căutarea sau introducerea unui furnizor după CUI, iConta.eu preia din API-ul public ANAF statusul curent de inactivitate al acestuia (`core/anaf_api.py`, câmpul `inactiv`), alături de denumire și plătitor de TVA. La data acestui ghid, iConta.eu **nu verifică automat, pentru fiecare factură primită și înregistrată în contabilitate, dacă furnizorul era inactiv exact la data emiterii acelei facturi** și nu recalculează deducerea la reactivare. Corelarea datei fiecărei facturi cu perioada exactă de inactivitate a furnizorului rămâne o verificare manuală.

[iConta.eu](/)
