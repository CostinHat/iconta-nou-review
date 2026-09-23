---
title: "Cum se contabilizează abonamentele SaaS plătite în avans de clienți?"
description: Dacă abonamentul e plătit înainte de a fi facturat, se tratează prin mecanismul de avans client (419). Dacă e deja facturat pentru o perioadă viitoare și trebuie „întins" pe lunile de livrare a serviciului, e o temă de venituri înregistrate în avans, care nu a fost verificată în acest dosar.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se contabilizează abonamentele SaaS plătite în avans de clienți?

Aici contează exact ce s-a întâmplat înainte de bani: clientul a plătit fără să existe încă o factură emisă pentru acea perioadă (avans propriu-zis), sau clientul a plătit pe baza unei facturi deja emise pentru o perioadă viitoare (situație diferită, de recunoaștere eșalonată a venitului)?

## Temeiul legal

::: ghid-temei
„Contul 419 «Clienți - creditori» [...] Cu ajutorul acestui cont se ține evidența clienților - creditori, reprezentând avansurile încasate de la clienți. Contul 419 «Clienți - creditori» este un cont de pasiv." — OMFP nr. 1802/2014 pentru aprobarea reglementărilor contabile
:::

## Cazul 1: plată fără factură emisă încă (avans propriu-zis)

Dacă clientul plătește abonamentul SaaS înainte de emiterea oricărei facturi pentru acea perioadă, tratamentul e cel al unui avans obișnuit: **4111 = 419 + 4427** la încasare, cu regularizare prin inversarea notei (**419 = 4111**, **4427 = 4111**) la momentul facturării efective a serviciului.

## Cazul 2: factură deja emisă pentru o perioadă viitoare de abonament

Dacă abonamentul a fost deja facturat integral pentru o perioadă viitoare (de exemplu un an de subscripție facturat dintr-o dată) și vrei ca venitul să fie recunoscut eșalonat, lună de lună, pe măsură ce serviciul se prestează, aceasta e o temă de **venituri înregistrate în avans** — un tratament contabil diferit de mecanismul de avans client descris mai sus (care lucrează pe contul de pasiv 419, nu pe conturile de eșalonare a veniturilor). Acest tratament specific **nu a fost verificat în acest dosar** — nu se inventează aici o descriere a lui; pentru contabilizarea corectă, verifică separat regulile aplicabile.

## Ce se greșește în practică

- Se tratează orice plată anticipată pentru un abonament ca „avans" pe contul 419, chiar și atunci când factura a fost deja emisă — dacă factura există deja, discuția nu mai e despre avans (o datorie față de client fără factură), ci despre eșalonarea recunoașterii venitului dintr-o factură deja emisă.
- Se recunoaște tot venitul din abonament în luna facturării, chiar dacă serviciul se prestează pe parcursul mai multor luni — fără o eșalonare corectă, veniturile lunare raportate nu reflectă prestarea reală a serviciului.
- Se presupune că mecanismul de avans (419) din F009 rezolvă automat și eșalonarea veniturilor din abonamente deja facturate — sunt mecanisme contabile diferite; avansul (419) privește sume încasate fără factură, nu eșalonarea unei facturi deja emise.

## Ce face iConta.eu

Pentru situația în care clientul plătește înainte de emiterea facturii, iConta.eu are mecanismul general de avans client (4111 = 419 + 4427, cu regularizare la facturare) — aplicabil și abonamentelor SaaS plătite anticipat, fără factură emisă încă. Pentru eșalonarea recunoașterii venitului dintr-o factură de abonament deja emisă pentru o perioadă viitoare (venituri înregistrate în avans), nu am verificat în acest dosar dacă există o funcționalitate dedicată — acest aspect trebuie confirmat separat înainte de a descrie un flux concret.

[iConta.eu](/)
