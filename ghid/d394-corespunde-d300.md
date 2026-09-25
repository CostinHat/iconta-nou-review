---
title: "Ce fac dacă D394 nu corespunde cu D300?"
description: "Ce verifici înainte de a depune D394, dacă observi singur o diferență față de suma din decontul de TVA."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă D394 nu corespunde cu D300?

Dacă observi, înainte de depunere, că totalurile din D394 nu se potrivesc cu D300, primul pas nu e să corectezi cifrele „ca să iasă" — e să verifici dacă diferența are o explicație legală, pentru că D394 nu e menită să reproducă întreg conținutul lui D300.

## Temeiul legal

::: ghid-temei
„Nu se înscriu achiziţiile intracomunitare de bunuri şi servicii pentru care există obligativitatea înscrierii în declaraţia 390."
— OPANAF 2194/2025, Anexa 2 pct.1 lit.b) (sursă: anaf_surse/opanaf_2194_2025_d394.txt:741-742)

„[...] se înscrie perioada fiscală declarată pentru depunerea decontului de taxă pe valoarea adăugată (formularul 300) [...] L - luna, T - trimestrul, S - semestrul, A - anul."
— OPANAF 2194/2025, Anexa 2, secțiunea 1 lit. a) (sursă: anaf_surse/opanaf_2194_2025_d394.txt:781-783)
:::

Punctele de verificat, în ordine:

1. **Perioada.** D394 se raportează pe aceeași perioadă fiscală ca decontul (formularul 300) — pentru declarația trimestrială, câmpul de lună se codifică pe ultima lună a trimestrului. O nealiniere de perioadă produce, aparent, o diferență care nu există în realitate.
2. **Conținutul exclus prin lege.** Achizițiile intracomunitare nu intră în D394 — merg în D390. Dacă D300 conține astfel de operațiuni (frecvent, la firmele cu furnizori din UE), diferența față de D394 e normală, nu o eroare.
3. **Livrările intracomunitare, spre deosebire de achiziții, NU sunt excluse** din D394 — apar ca tip L, la fel ca exporturile, la cotă 0. Dacă lipsesc din D394 deși există în D300, acolo poate fi o eroare reală de completare, nu o diferență structurală.

## Ce se greșește în practică

- Se tratează orice diferență între D300 și D394 ca fiind automat o eroare de aplicație sau de introducere a datelor, fără să se verifice întâi dacă diferența vine din operațiuni intracomunitare/importuri, excluse prin lege din D394.
- Se confundă regula pentru achiziții (excluse dacă sunt intracomunitare) cu regula pentru livrări (livrările intracomunitare și exporturile intră în D394, la cotă 0, ca tip LS).
- Se ignoră faptul că D394 e un subset structural al lui D300, nu o declarație independentă cu aceeași sferă de cuprindere.

## Ce face iConta.eu

Cele două declarații se generează prin module separate în aplicație, fiecare cu propria validare pe validatorul oficial ANAF (DUK) — nu există, la generarea efectivă, un mecanism care compară automat sumele din D300 cu cele din D394. Există, doar la nivel de dezvoltare (nu în fluxul folosit de contabil), un gard intern (`core/test_d300_d394_paritate.py`) care confruntă cele două calcule pe cotă — dar chiar acest gard e documentat în cod ca tautologic, fiindcă ambele generatoare citesc aceleași linii de factură și deduc cota identic, deci prinde doar o divergență între generatoare, nu o eroare reală de conținut. Singura verificare internă care rulează la generarea D394 e propria ei consistență: a doua cale de calcul (`core/d394_reconciliere.py`) recalculează totalurile pe cotă direct din liniile de factură și oprește generarea la divergență față de generatorul principal, dar nu confruntă rezultatul cu D300.

Practic, dacă observi o diferență înainte de depunere, verificarea rămâne manuală: separi din D300 operațiunile intracomunitare și importurile (absente din D394 prin lege), apoi compari doar restul cu ce a generat aplicația pentru D394 în aceeași perioadă.

[iConta.eu](/)
