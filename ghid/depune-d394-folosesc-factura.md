---
title: "Se mai depune D394 dacă folosesc e-Factura"
description: "Trecerea facturilor prin RO e-Factura nu înlocuiește obligația de depunere a D394 — și cum verifică iConta.eu, structural, consistența dintre ele."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Se mai depune D394 dacă folosesc e-Factura

Da. D394 rămâne o obligație de sine stătătoare, indiferent dacă facturile emise sau primite trec prin sistemul RO e-Factura. Cele două sunt lucruri diferite: e-Factura e un canal de emitere și transmitere a facturii, D394 e o declarație informativă separată despre operațiunile efectuate pe teritoriul național.

## Temeiul legal

::: ghid-temei
„Persoanele impozabile înregistrate în scopuri de TVA în România sunt obligate să declare livrările de bunuri, prestările de servicii şi achiziţiile de bunuri şi servicii realizate pe teritoriul României către/de la orice persoană, aşa cum este definită la art. 266 alin. (1) pct. 24 din Legea nr. 227/2015 privind Codul fiscal, cu modificările şi completările ulterioare."
— OPANAF 3769/2015, art. 1 (sursă: anaf_surse/opanaf_3769_2015_d394_baza.txt)
:::

Obligația de a depune D394 e legată exclusiv de înregistrarea în scopuri de TVA (art. 316 din Codul fiscal), nu de metoda prin care a fost emisă sau primită factura:

- nu există niciun prag valoric care să scutească firma de D394 — obligația ține doar de faptul că e înregistrată în scopuri de TVA;
- e-Factura (RO e-Invoicing) e obligatorie separat, ca metodă de transmitere a facturii către ANAF/către partener, cu propriul temei legal — nu substituie și nu exceptează de la nicio altă declarație informativă;
- D394 se depune conform propriului termen (ziua 30 a lunii următoare perioadei de raportare, cu excepția lunii ianuarie), indiferent câte facturi au trecut sau nu prin e-Factura.

## Ce se greșește în practică

- Se presupune că, odată ce toate facturile trec prin RO e-Factura, ANAF „are deja toate datele" și D394 devine redundantă — legal, cele două rămân obligații distincte.
- Se ignoră depunerea D394 pentru o perioadă în care facturile au fost transmise corect prin e-Factura, crezând că declarația a fost implicit acoperită.
- Se presupune că aplicația verifică automat, factură cu factură, dacă tot ce a intrat în D394 corespunde cu ce a fost efectiv transmis/primit prin e-Factura.

## Ce face iConta.eu

D394 se generează din aceeași tabelă de facturi pe care o populează și importul e-Factura (parser UBL 2.1/CIUS-RO) — deci, în mod obișnuit, cele două coincid, pentru că au aceeași sursă de date. Dar corelarea e **structurală**, nu o funcție dedicată de verificare: nu există în aplicație un modul separat care compară explicit conținutul D394 cu ce a fost efectiv trimis sau primit prin e-Factura.

Practic, dacă o factură a fost introdusă manual (nu a trecut prin importul e-Factura) sau a fost corectată manual după import, aplicația nu o „reconfirmă" automat împotriva e-Factura — validarea rămâne cea generală a D394 (validatorul oficial ANAF rulat local, plus recalculul independent al totalurilor pe cotă din liniile brute ale facturilor), nu o comparație punctuală cu fluxul e-Factura.

[iConta.eu](/)
