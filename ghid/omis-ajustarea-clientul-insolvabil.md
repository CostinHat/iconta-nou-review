---
title: "Am omis ajustarea pentru clientul insolvabil"
description: "Ajustarea de 100% pentru un client aflat în faliment declarat sau insolvență nu are prag de vechime — se poate constitui imediat ce procedura e declarată, cu condiția ca creanța să nu fie garantată sau la o persoană afiliată."
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Am omis ajustarea pentru clientul insolvabil

Dacă un client a intrat în faliment declarat sau insolvență și ajustarea pentru deprecierea creanței nu a fost constituită, corectarea e directă: nu se așteaptă vechimea de 270 de zile, specifică altei situații — la faliment/insolvență declarate, deducerea de 100% e disponibilă imediat, din momentul hotărârii judecătorești.

## Temeiul legal

::: ghid-temei
„Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru depreciere, numai în conformitate cu prezentul articol, astfel: [...] j) ajustările pentru deprecierea creanțelor [...] în limita unui procent de 100% din valoarea creanțelor [...] dacă creanțele îndeplinesc cumulativ următoarele condiții: 1. sunt deținute la o persoană juridică asupra căreia este declarată procedura de deschidere a falimentului, pe baza hotărârii judecătorești prin care se atestă această situație, sau la o persoană fizică asupra căreia este deschisă procedura de insolvență pe bază de: – plan de rambursare a datoriilor; – lichidare de active; – procedură simplificată; 2. nu sunt garantate de altă persoană; 3. sunt datorate de o persoană care nu este persoană afiliată contribuabilului."

*(Codul fiscal — Legea nr. 227/2015, art. 26 alin. (1) lit. j))*
:::

## Cum corectezi omisiunea

1. **Verifici data hotărârii judecătorești** care declară falimentul (persoană juridică) sau deschide procedura de insolvență (persoană fizică) — de la acea dată e disponibilă deducerea de 100%, nu de la data scadenței inițiale a creanței.
2. **Verifici negarantarea și neafilierea** — dacă oricare din cele două condiții nu e îndeplinită, procentul deductibil rămâne 0%, indiferent de stadiul procedurii de insolvență.
3. **Constitui ajustarea contabilă (491) integral**, apoi aplici procentul de 100% ca deductibil fiscal — nota generată e 6814=491.
4. **Corectezi retroactiv rezultatul fiscal** al perioadei în care ajustarea trebuia constituită, dacă omisiunea privește un exercițiu deja închis.

## Ce se greșește în practică

- Se așteaptă trecerea a 270 de zile de la scadență înainte de a constitui ajustarea, deși la faliment declarat pragul de zile nu se aplică deloc.
- Se constituie ajustarea la doar 30%, prin confuzie cu regimul general al creanțelor neîncasate, deși condiția de faliment/insolvență declarată justifică 100%.
- Se omite verificarea garantării/afilierii creanței, aplicând 100% și unei creanțe care, de fapt, nu îndeplinește aceste condiții.

## Ce face iConta.eu

Funcția `deductibilitate_creanta(zile_depasire_scadenta, garantata, afiliata, faliment_declarat=True)` din `core/provizioane.py` întoarce direct 100% (cu condiția negarantării și neafilierii) și generează nota `6814=491`. Aplicația nu detectează singură intrarea unui client în insolvență — introducerea corectă a stării debitorului (`faliment_declarat`) rămâne o verificare a contabilului, pe baza hotărârii judecătorești.

[iConta.eu](/)
