---
title: "TVA pentru achiziții de la persoane fizice: tratament"
description: "De ce achizițiile de bunuri de la persoane fizice nu generează TVA deductibilă și de ce nu intră sub taxare inversă, potrivit art. 331 din Codul fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# TVA pentru achiziții de la persoane fizice: tratament

O firmă care cumpără bunuri de la o persoană fizică — de exemplu cereale direct de la un producător agricol neînregistrat, sau deșeuri feroase de la un particular — nu primește o factură cu TVA. Întrebarea care revine des e dacă se poate aplica taxarea inversă, ca pentru achizițiile similare de la firme.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile art. 307 alin. (1), în cazul operațiunilor taxabile, persoana obligată la plata taxei este beneficiarul pentru operațiunile prevăzute la alin. (2). Condiția obligatorie pentru aplicarea taxării inverse este ca atât furnizorul, cât și beneficiarul să fie înregistrați în scopuri de TVA conform art. 316."
— Legea nr. 227/2015, art. 331 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Consecința practică pentru achizițiile de la persoane fizice:

- Taxarea inversă de la art. 331 — aplicabilă, printre altele, cerealelor, deșeurilor feroase/neferoase, masei lemnoase sau materialelor reciclabile — se aplică **doar** dacă **atât furnizorul, cât și beneficiarul** sunt înregistrați în scopuri de TVA conform art. 316.
- O persoană fizică neînregistrată în scopuri de TVA nu îndeplinește această condiție, indiferent de natura bunului vândut. Achiziția rămâne, din perspectiva TVA, o tranzacție fără taxă — nu există TVA de dedus, pentru că nu există TVA colectată de partea vânzătorului.
- Aceste achiziții rămân totuși supuse unei obligații de **raportare informativă** în D394 (secțiunea `op11`, defalcată pe cod de produs), tocmai pentru trasabilitatea circuitului la bunurile sensibile la fraudă (cereale, deșeuri metalice).

## Ce se greșește în practică

- Se aplică mecanic taxare inversă (autofactură cu TVA) pentru o achiziție de cereale sau deșeuri de la o persoană fizică, tratând-o ca pe o achiziție de la un furnizor înregistrat în scopuri de TVA — condiția de la art. 331 alin. (1) nu e îndeplinită.
- Se caută TVA deductibilă pe o astfel de achiziție, deși nu există TVA de dedus atâta vreme cât vânzătorul nu a colectat taxă.
- Se omite raportarea informativă în D394, considerând că absența TVA-ului înseamnă și absența oricărei obligații declarative.

## Ce face iConta.eu

La data acestui ghid, iConta.eu clasifică automat, la înregistrarea unei facturi de achiziție, partenerii fără CUI valid de TVA ca fiind neînregistrați, ceea ce rutează operațiunea corect (fără taxare inversă) în calculul TVA. Aplicația nu verifică însă independent dacă un partener cu CUI aparent valid este cu adevărat înregistrat în scopuri de TVA la data facturii — acest statut rămâne o informație introdusă/confirmată de utilizator.

[iConta.eu](/)
