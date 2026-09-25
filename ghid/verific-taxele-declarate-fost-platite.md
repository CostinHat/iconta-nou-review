---
title: "Cum verific dacă toate taxele declarate au fost și plătite?"
description: "Diferența dintre a depune la termen o declarație fiscală și a stinge efectiv obligația — și de ce cele două se verifică separat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific dacă toate taxele declarate au fost și plătite?

A depune o declarație fiscală și a plăti suma din ea sunt două obligații distincte, cu propriile termene și propriile consecințe la nerespectare. O firmă poate avea toate declarațiile depuse la timp și, în același timp, restanțe la plată — cele două nu se confirmă reciproc.

## Temeiul legal

::: ghid-temei
„Dobânzile se calculează pentru fiecare zi de întârziere, începând cu ziua imediat următoare termenului de scadență și până la data stingerii sumei datorate, inclusiv."
— Legea 207/2015, art. 174 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Structura de verificare corectă are două straturi separate:

- **Depunerea** — se verifică dacă declarația (D100, D112, D300, D390, D101 etc.) a fost transmisă la termenul legal, pe fiecare tip și fiecare perioadă.
- **Stingerea obligației** — se verifică dacă suma declarată a fost efectiv plătită. Neplata la scadență, chiar cu declarația depusă corect, generează dobânzi de 0,02%/zi (art. 174 alin. 5) și, separat, penalități de întârziere de 0,01%/zi (art. 176 alin. 2), calculate de la scadență, nu de la data depunerii declarației.
- **Ordinea stingerii** — când o plată nu acoperă toate obligațiile, legea impune o ordine strictă: mai întâi obligațiile principale în ordinea vechimii, apoi accesoriile în ordinea vechimii (art. 165 alin. 1), astfel încât aceeași sumă plătită poate stinge o obligație diferită de cea la care contribuabilul credea că a plătit.
- **Confirmarea plății reale** se face doar la sursă, în fișa pe plătitor din Spațiul Privat Virtual (SPV) — nicio evidență internă a firmei nu poate confirma singură că suma a ajuns la buget.

## Ce se greșește în practică

- Se consideră „în regulă" o obligație pentru că declarația apare depusă, fără a verifica separat dacă plata corespunzătoare a fost efectiv făcută și decontată.
- Se ignoră faptul că dobânda curge de la scadență (art. 174), nu de la data la care contabilul își dă seama de restanță — o restanță „descoperită" târziu poartă deja accesorii.
- Se presupune că o plată făcută stinge exact obligația vizată de contabil, fără să se țină cont de ordinea legală de stingere (art. 165), care poate aloca suma altei datorii mai vechi.

## Ce face iConta.eu

iConta.eu are un semafor de conformare fiscală per firmă (`core/control_fiscal_api.py`) care derivă, din profilul firmei, ce declarații sunt datorate pe fiecare perioadă trecută și le compară cu evidența declarațiilor efectiv depuse — semnalând lipsurile, cu termenul depășit sau apropiat. Acest semafor verifică însă **depunerea**, nu **plata**: aplicația nu are, la data acestui ghid, o integrare cu fișa pe plătitor din SPV care să confirme dacă sumele declarate au fost efectiv încasate de bugetul de stat. Confirmarea stingerii reale a obligațiilor rămâne o verificare separată, făcută direct în SPV.

[iConta.eu](/)
