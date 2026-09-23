---
title: "Deducerea cheltuielilor cu debitorii în insolvență"
description: "La un debitor în faliment/insolvență declarată, ajustarea de 100% e disponibilă imediat, fără prag de zile — dar pierderea finală, la închiderea procedurii, are propriul regim de deductibilitate, cu condiții separate."
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Deducerea cheltuielilor cu debitorii în insolvență

Un debitor aflat în faliment declarat sau insolvență generează, pentru creditor, dreptul la deducere în două momente diferite: imediat, prin constituirea unei ajustări de 100%, și ulterior, la închiderea procedurii, prin deducerea eventualei pierderi finale rămase neacoperite.

## Temeiul legal

::: ghid-temei
„Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru depreciere, numai în conformitate cu prezentul articol, astfel: [...] j) ajustările pentru deprecierea creanțelor [...] în limita unui procent de 100% din valoarea creanțelor [...] dacă creanțele îndeplinesc cumulativ următoarele condiții: 1. sunt deținute la o persoană juridică asupra căreia este declarată procedura de deschidere a falimentului, pe baza hotărârii judecătorești prin care se atestă această situație, sau la o persoană fizică asupra căreia este deschisă procedura de insolvență [...]; 2. nu sunt garantate de altă persoană; 3. sunt datorate de o persoană care nu este persoană afiliată contribuabilului."

*(Codul fiscal — Legea nr. 227/2015, art. 26 alin. (1) lit. j))*
:::

## Cele două momente ale deducerii

1. **La deschiderea procedurii** — din momentul hotărârii judecătorești prin care se declară falimentul sau se deschide insolvența, ajustarea contabilă a creanței (491) devine deductibilă 100%, fără să fie nevoie de vechimea de 270 de zile cerută la regimul general — cu condiția ca aceeași creanță să nu fie garantată și să nu fie la o persoană afiliată.
2. **La închiderea procedurii** — dacă rămâne o parte din creanță neacoperită de ajustare, pierderea respectivă e deductibilă doar dacă procedura de faliment a fost efectiv închisă prin hotărâre judecătorească (una din cele șase situații enumerate la art. 25 alin. (4) lit. h)); în lipsa acestei hotărâri, partea rămasă neacoperită nu se deduce.

## Ce se greșește în practică

- Se așteaptă pragul de 270 de zile de la scadență și pentru un debitor deja aflat în faliment declarat, deși la faliment/insolvență deducerea de 100% e disponibilă imediat, fără prag de zile.
- Se deduce toată pierderea rămasă înainte de închiderea efectivă a procedurii de faliment prin hotărâre judecătorească.
- Se acordă deducerea de 100% unei creanțe garantate, deși condiția de negarantare e obligatorie, indiferent de stadiul procedurii debitorului.

## Ce face iConta.eu

`deductibilitate_creanta(..., faliment_declarat=True)` din `core/provizioane.py` întoarce 100% (cu condiția negarantării și neafilierii) și generează nota `6814=491`. Aplicația nu modelează scoaterea din evidență a creanței la închiderea procedurii de faliment — pierderea finală rămasă neacoperită, condiționată de hotărârea judecătorească de închidere, se tratează separat, manual.

[iConta.eu](/)
