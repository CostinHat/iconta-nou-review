---
title: Cum se acordă tichetele de masă și ce contribuții au?
description: Tichetele de masă se configurează per salariat, cu o valoare nominală de cel mult 45 lei/tichet din noiembrie 2025, se acordă pe zilele efectiv lucrate și sunt purtătoare de CASS 10% și impozit 10%, fără CAS și fără CAM.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se acordă tichetele de masă și ce contribuții au?

Tichetul de masă rămâne unul dintre cele mai folosite beneficii salariale, dar are un regim de contribuții aparte față de salariul de bază: nu toate contribuțiile obișnuite se aplică, iar plafonul valorii nominale s-a schimbat recent.

## Temeiul legal

::: ghid-temei
Legea nr. 201/2025 (MO nr. 1106/28.11.2025), privind plafonul valorii nominale:

> „Valoarea nominală a unui tichet de masă nu poate depăși suma de 45 lei."

Aplicare în timp, Articolul II alin. (1):

> „Prevederile art. I pct. 1 se aplică începând cu drepturile aferente lunii noiembrie 2025."

HG nr. 1045/2018, Articolul 10 alin. (3):

> „(3) Salariații beneficiază lunar de un număr de tichete de masă cel mult egal cu numărul de zile lucrate, iar acest număr nu poate depăși numărul de zile lucrătoare din luna pentru care se acordă tichetele."

Codul fiscal (Legea 227/2015, consolidat), Articolul 142 lit. r (excludere din baza CAS):

> „r) biletele de valoare sub forma tichetelor de masă, voucherelor de vacanță, tichetelor de creșă, tichetelor culturale, acordate potrivit legii;"

Articolul 157 alin. (2) (baza CASS):

> „(2) Nu se cuprind în baza lunară de calcul al contribuției de asigurări sociale de sănătate sumele prevăzute la art. 76 alin. (4) lit. d), art. 141 lit. d) și art. 142, cu excepția sumelor reprezentând valoarea nominală a biletelor de valoare sub forma tichetelor de masă și a voucherelor de vacanță, acordate potrivit legii."
:::

## Acordare și contribuții, pas cu pas

Acordarea se face în doi pași: întâi se stabilește o valoare nominală per salariat (până la plafonul legal de 45 lei), apoi, lunar, numărul de tichete rezultă din zilele efectiv lucrate din pontaj. Din valoarea totală a tichetelor acordate într-o lună se reține CASS 10%, iar impozitul de 10% se calculează pe ce rămâne după CASS — nu pe valoarea brută. Nu se aplică nici CAS, nici CAM.

::: ghid-exemplu
Un salariat are tichetul de masă configurat la 45 lei și a lucrat 21 de zile într-o lună. Valoare tichete = 45 × 21 = 945 lei. CASS 10% = 94,5 lei. Bază impozit = 945 − 94,5 = 850,5 lei. Impozit 10% = 85,05 lei. Total reținut din tichete = 179,55 lei, iar suma netă rezultată din tichete este 765,45 lei.
:::

## Ce se greșește în practică

- Se configurează o valoare nominală peste plafonul legal curent (45 lei), lucru pe care validarea la salvare ar trebui să-l blocheze.
- Se aplică impozitul de 10% pe valoarea brută a tichetelor, fără a scădea întâi CASS.
- Se reține CAS sau CAM pe tichetele de masă, deși legea le exclude explicit din aceste baze.
- Se generează statul de plată cu tichete calculate deși pontajul lunii nu este încă confirmat.

## Ce face iConta.eu

Valoarea nominală configurată per salariat (`tichet_masa_valoare`) este validată la salvare: trebuie să fie ≥0 și să nu depășească plafonul legal curent stocat central în cotele aplicației. Numărul de tichete rezultă din pontajul lunii, nu este introdus manual. Calculul de CASS și impozit pe tichete se face automat, fără CAS și fără CAM, iar dacă pontajul lunii nu este confirmat, valoarea tichetului de masă este blocată la 0 pentru acea lună, exact conform HG 1045/2018 art. 10 alin. (3).

[iConta.eu](/)
