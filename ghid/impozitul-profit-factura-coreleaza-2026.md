---
title: "Impozitul pe profit și e-Factura: cum se corelează în 2026"
description: "De ce statutul unei facturi în sistemul RO e-Factura contează pentru deductibilitatea cheltuielilor la impozitul pe profit, potrivit Codului fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Impozitul pe profit și e-Factura: cum se corelează în 2026

Legătura dintre cele două nu e directă (nu există un articol care să spună „nedepunerea prin e-Factura anulează deductibilitatea"), dar e reală, prin definiția legală a noțiunii de „factură". Pentru operațiunile B2B între persoane impozabile stabilite în România, Codul fiscal spune că, din 2024, **numai facturile transmise prin RO e-Factura sunt considerate facturi**. Iar o cheltuială fără document justificativ valabil nu se poate înregistra corect în contabilitate — element de care depinde, la rândul lui, deductibilitatea la impozitul pe profit.

## Temeiul legal

::: ghid-temei
„(1) În înțelesul prezentului titlu sunt considerate facturi documentele sau mesajele pe suport hârtie ori în format electronic, dacă acestea îndeplinesc condițiile stabilite în prezentul articol.
(1^1) Prin excepție de la prevederile alin. (1), pentru operațiunile realizate între persoane impozabile stabilite în România conform art. 266 alin. (2), sunt considerate facturi numai facturile care îndeplinesc condițiile prevăzute de Ordonanța de urgență a Guvernului nr. 120/2021 privind administrarea, funcționarea și implementarea sistemului național privind factura electronică RO e-Factura [...]."
— Codul fiscal (Legea 227/2015), art. 319 alin. (1) și (1^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Coroborat cu:

::: ghid-temei
„(1) Pentru determinarea rezultatului fiscal sunt considerate cheltuieli deductibile cheltuielile efectuate în scopul desfășurării activității economice [...]."
— Codul fiscal (Legea 227/2015), art. 25 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„(1) Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ."
— Legea 82/1991 a contabilității, art. 6 alin. (1) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

- Pentru tranzacțiile B2B între firme stabilite în România, un document care nu a fost transmis (corect) prin RO e-Factura nu e, din punct de vedere legal, o „factură" — indiferent cum arată sau ce conține.
- Cheltuielile deductibile la impozitul pe profit trebuie efectuate în scopul activității economice (art. 25 alin. (1)) și, ca orice operațiune contabilă, au nevoie de un document justificativ (Legea 82/1991, art. 6).
- Dacă documentul de achiziție nu îndeplinește condițiile de „factură" din perspectiva RO e-Factura, riscul practic e ca acea cheltuială să nu poată fi susținută ca fiind justificată corespunzător, cu impact asupra recunoașterii ei fiscale.
- Termenul-limită pentru transmiterea facturii în sistemul RO e-Factura e de 5 zile lucrătoare de la data emiterii (sau de la data-limită legală de emitere, dacă e mai târzie) — corelarea contabilă/fiscală se face pe această fereastră.
- Regula se aplică relației B2B (persoană impozabilă-persoană impozabilă, ambele stabilite în România); pentru relația B2C, obligația de transmitere prin RO e-Factura e reglementată separat și nu redefinește noțiunea de „factură" în același mod.

## Ce se greșește în practică

- Se consideră că o factură pe hârtie sau un PDF trimis pe e-mail, deși nu a fost transmis prin RO e-Factura, e suficientă pentru deducerea cheltuielii la impozitul pe profit — riscant pentru operațiunile B2B, unde definiția legală a „facturii" a fost restrânsă.
- Se confundă obligația de transmitere prin RO e-Factura (o obligație de conformare, cu propriile sancțiuni) cu problema distinctă a deductibilității cheltuielii — cele două se leagă indirect, prin lipsa unui document justificativ valabil, nu printr-un articol care le unește explicit.
- Se ignoră termenul de 5 zile lucrătoare pentru transmiterea facturii, considerându-l o simplă formalitate administrativă, fără legătură cu momentul înregistrării cheltuielii în contabilitate.
- Se presupune că regula se aplică și facturilor simplificate sau operațiunilor exceptate explicit (de exemplu bonurile fiscale care îndeplinesc condițiile unei facturi simplificate) — acestea au regim propriu.

## Ce face iConta.eu

iConta.eu **generează și trimite facturi electronice conforme RO e-Factura** prin modulul `efactura_send.py` (generator XML UBL 2.1/CIUS-RO, cu upload prin OAuth către ANAF) și gestionează facturile emise prin `facturi_api.py`. Aplicația nu are însă, la data acestui ghid, o funcție care să **coreleze automat statutul de transmitere RO e-Factura al unei achiziții cu deductibilitatea ei la impozitul pe profit** — nu am găsit în cod niciun modul care să blocheze sau să semnaleze o cheltuială înregistrată pe baza unei facturi de la un furnizor ce nu a transmis-o (corect) prin sistemul RO e-Factura. Verificarea acestei corelații rămâne, în acest moment, o sarcină manuală a contabilului.

[iConta.eu](/)
