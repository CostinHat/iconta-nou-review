---
title: Cum verific dacă D390 a fost validată de ANAF?
description: Aplicația verifică D390 față de evidența contabilă și de D300 depus prin ea — nu față de statusul de validare la ANAF, care rămâne de confirmat în SPV.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum verific dacă D390 a fost validată de ANAF?

Merită spus direct, ca să nu cauți o funcție care nu există: aplicația nu verifică dacă D390 depusă a fost efectiv validată/acceptată de ANAF. Statusul de validare la ANAF se confirmă doar în portalul SPV, după depunere.

## Temeiul legal

::: ghid-temei
**Art. 325 din Codul fiscal (Legea 227/2015)** — obligația depunerii declarației recapitulative (D390), lunar, pentru livrările intracomunitare scutite (lit. a) și achizițiile intracomunitare taxabile (lit. d).

Depunerea și confirmarea recepției/validării unei declarații electronice se face prin portalul SPV, administrat de ANAF — pasul de confirmare a validării la ANAF nu are corespondent într-o verificare automată în cadrul aplicației.
:::

Ce face, de fapt, controlul din aplicație pentru D390: confruntă baza declarată (livrări/achiziții intracomunitare, calculată din facturi) cu două surse **interne**, nu cu ANAF —

- **evidența contabilă validată**: facturile intracomunitare cu notă contabilă având statusul „validată", legată de factura respectivă;
- **D300-ul efectiv depus prin aplicație**, pe rândurile corespunzătoare (R1_1 pentru livrări, R5_1 pentru achiziții).

Niciuna dintre aceste comparații nu interoghează ANAF sau SPV. Ele arată dacă ce ai declarat corespunde cu ce ai în contabilitate și cu ce ai depus anterior ca decont — nu dacă fișierul XML depus a trecut de validarea/procesarea din partea ANAF.

## Ce se greșește în practică

- Se interpretează un semnal verde pe controlul D390 ↔ D300/evidență ca dovadă că declarația a fost „validată la ANAF" — verdele arată doar coerența internă, nu confirmarea de la autoritate.
- Se presupune că depunerea prin aplicație include automat și confirmarea de acceptare ANAF, vizibilă undeva în ecranul de control fiscal — confirmarea rămâne de verificat separat, în SPV.
- Se amână verificarea în SPV pentru că „aplicația arată verde" — sunt două lucruri diferite: coerența cifrelor și statusul real de procesare la ANAF.

## Ce face iConta.eu

Pentru D390, aplicația nu are astăzi un mecanism care să confirme automat statusul de validare la ANAF — acesta rămâne o verificare separată, făcută de tine în portalul SPV, după depunere.

Ce oferă în schimb e un control încrucișat intern: D390 față de evidența contabilă validată (facturi cu notă validată) și față de D300-ul depus prin aplicație, cu semnal verde/gri/roșu pe fiecare comparație. E un instrument util pentru a prinde diferențe înainte de depunere sau imediat după, dar nu înlocuiește confirmarea de procesare din SPV.

[iConta.eu](/)
