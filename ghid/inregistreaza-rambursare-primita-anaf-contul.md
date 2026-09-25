---
title: "Cum se înregistrează o rambursare primită de la ANAF în contul bancar?"
description: "Nota contabilă pentru rambursarea de TVA sau alte sume de la bugetul de stat, primită în contul bancar, conform planului de conturi din OMFP 1802/2014."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează o rambursare primită de la ANAF în contul bancar?

O sumă intrată în contul bancar cu descrierea "rambursare" de la Trezorerie sau ANAF nu e un împrumut restituit — e o creanță fiscală încasată, iar contul de contrapartidă e complet diferit.

## Temeiul legal

::: ghid-temei
„442. Taxa pe valoarea adăugată 4423. TVA de plată (P) 4424. TVA de recuperat (A) 4426. TVA deductibilă (A) 4427. TVA colectată (P) 4428. TVA neexigibilă (A/P) [...] 448. Alte datorii și creanțe cu bugetul statului 4481. Alte datorii față de bugetul statului (P) 4482. Alte creanțe privind bugetul statului (A)"
— OMFP 1802/2014, planul de conturi general, clasa 4 „Conturi de terți" (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Mecanismul aplicabil, în funcție de natura sumei rambursate:

- **Rambursare de TVA**: încasarea în bancă se înregistrează **5121 = 4424 "TVA de recuperat"**, stingând creanța constituită anterior prin decontul de TVA cu sumă negativă de rambursat.
- **Restituire de impozit/taxă plătită în plus** (impozit pe profit, impozit micro, alte obligații): contrapartida e contul de creanță bugetară corespunzător, de regulă **4482 "Alte creanțe privind bugetul statului"** (cont de activ), nu un cont de datorie sau de împrumut.
- În niciun caz suma nu se înregistrează prin conturile de împrumuturi (519x) — acestea sunt rezervate finanțărilor rambursabile propriu-zise (credite bancare, împrumuturi de la asociați), o categorie complet diferită de creanța fiscală de recuperat.

## Ce se greșește în practică

- Se lasă suma clasificată automat, pe baza cuvântului "rambursare" din descrierea extrasului bancar, sub o categorie de împrumut — o rambursare de TVA sau de impozit nu are nimic de-a face cu o rată de credit, deși ambele conțin cuvântul "rambursare".
- Se înregistrează suma direct ca venit, fără stingerea creanței constituite anterior în contul 4424/4481 — dublează eronat rezultatul, pentru că suma respectivă nu e un venit, ci încasarea unei creanțe deja existente în contabilitate.
- Se omite verificarea sumei încasate față de suma aprobată prin decizia de rambursare emisă de ANAF — o diferență (parțială, cu dobânzi, cu compensare) trebuie explicată, nu doar înregistrată brut.

## Ce face iConta.eu

La data acestui ghid, `core/banca.py` clasifică automat liniile din extrasul bancar pe baza unor cuvinte-cheie din descriere: cuvântul „rambursare" e încadrat în categoria **„credit"** (alături de „împrumut", „rata credit"), cu contrapartida contul **5191** (împrumuturi pe termen scurt) — nu contul 4424/4481 specific unei rambursări fiscale de la ANAF. Pentru o rambursare de TVA sau de impozit intrată în cont, această clasificare automată e **greșită** și trebuie corectată manual de contabil, reclasificând linia pe contul potrivit (4424 sau 4482, după caz) — aplicația nu distinge azi între o rambursare de credit și o rambursare de la bugetul de stat.

[iConta.eu](/)
