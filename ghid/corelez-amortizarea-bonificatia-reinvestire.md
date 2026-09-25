---
title: "Cum corelez amortizarea cu bonificația pentru reinvestire"
description: "Scutirea de impozit pentru profitul reinvestit din Codul fiscal și legătura ei cu punerea în funcțiune a activelor amortizabile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum corelez amortizarea cu bonificația pentru reinvestire

Scutirea de impozit pentru profitul reinvestit nu e o facilitate separată de amortizare — ea se calculează în funcție de profitul contabil brut cumulat până în trimestrul (sau anul) **punerii în funcțiune** a activului, moment care e și cel de la care începe, de regulă, amortizarea fiscală a aceluiași activ.

## Temeiul legal

::: ghid-temei
„Profitul investit în echipamente tehnologice, active utilizate în activitatea de producție și procesare, activele reprezentând retehnologizare, calculatoare electronice și echipamente periferice, mașini și aparate de casă, de control și de facturare, în programe informatice, precum și pentru dreptul de utilizare a programelor informatice, produse și/sau achiziționate, inclusiv în baza contractelor de leasing financiar, și puse în funcțiune, folosite în scopul desfășurării activității economice, este scutit de impozit. [...] Profitul investit potrivit alin. (1) reprezintă soldul contului de profit și pierdere, respectiv profitul contabil brut cumulat de la începutul anului, obținut până în trimestrul sau în anul punerii în funcțiune a activelor prevăzute la alin. (1). Scutirea de impozit pe profit aferentă investițiilor realizate se acordă în limita impozitului pe profit calculat cumulat de la începutul anului până în trimestrul punerii în funcțiune a activelor [...]."
— Legea nr. 227/2015, art. 22 alin. (1)-(2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cum se leagă cele două mecanisme:

- Scutirea de profit reinvestit se calculează raportat la **momentul punerii în funcțiune** a activului — același moment de la care, în regulile generale ale art. 28, începe și amortizarea fiscală a mijlocului fix respectiv.
- Scutirea privește **profitul contabil**, nu direct cheltuiala cu amortizarea — dar activul care generează scutirea (echipament tehnologic, calculator, program informatic etc.) e, în marea majoritate a cazurilor, același activ pentru care firma va deduce ulterior amortizarea fiscală, an de an, conform art. 28.
- Activele corporale eligibile pentru scutire sunt limitate explicit la subgrupa 2.1 și clasa 2.2.9 din Catalogul mijloacelor fixe — deci corelarea cu amortizarea presupune verificarea acelorași coduri de clasificare atât pentru încadrarea la scutire, cât și pentru determinarea duratei normale de amortizare.
- Dacă în trimestrul punerii în funcțiune se înregistrează pierdere contabilă, iar profit apare abia ulterior, impozitul pe profitul investit **nu se recalculează** (art. 22 alin. (3)) — regulă separată de mecanismul obișnuit de amortizare, care nu depinde de profitabilitatea trimestrială.

## Ce se greșește în practică

- Se calculează scutirea pentru profitul reinvestit raportat la data facturii de achiziție, nu la data efectivă a punerii în funcțiune — cele două pot fi în trimestre fiscale diferite, cu impact direct asupra plafonului scutirii.
- Se presupune că scutirea de profit reinvestit „înlocuiește" amortizarea fiscală a activului — de fapt sunt mecanisme distincte, care coexistă: activul e amortizat normal în anii următori, indiferent că achiziția lui a beneficiat de scutire în anul punerii în funcțiune.
- Se aplică scutirea pentru active corporale din afara subgrupei 2.1/clasei 2.2.9 din catalog, fără verificarea prealabilă a încadrării exacte.

## Ce face iConta.eu

iConta.eu nu are, la data acestui ghid, un modul dedicat calculului automat al scutirii de impozit pentru profitul reinvestit conform art. 22 — modulul de amortizare a mijloacelor fixe (`core/d406_active.py`) calculează amortizarea de la data punerii în funcțiune, dar corelarea cu profitul contabil cumulat pentru determinarea plafonului scutirii rămâne un calcul separat, făcut de contabil în afara aplicației.

[iConta.eu](/)
