---
title: "Trebuie registru de casă separat pentru fiecare valută?"
description: "Norma contabilă distinge un formular separat pentru «Registrul de casă (în valută)» față de cel în lei, dar nu precizează explicit dacă fiecare monedă străină primește propriul registru."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Trebuie registru de casă separat pentru fiecare valută?

Da, cu o nuanță: legea separă clar registrul în lei de registrul în valută, ca formulare diferite — dar corpusul normativ verificat pentru acest ghid nu detaliază dacă „registrul în valută" înseamnă un singur registru pentru toate monedele străine sau câte unul pentru fiecare valută în parte (EUR, USD etc.).

## Temeiul legal

::: ghid-temei
„REGISTRUL DE CASĂ (Cod 14-4-7A și Cod 14-4-7bA) REGISTRUL DE CASĂ (în valută - Cod 14-4-7/aA și Cod 14-4-7/cA) Registrul de casă servește ca: - document de înregistrare operativă a încasărilor și plăților în numerar (lei sau valută), efectuate prin casieria entității; - document de stabilire, la sfârșitul fiecărei zile, a soldului de casă; - document de înregistrare în contabilitate a operațiunilor de casă. Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți."
— OMFP nr. 2634/2015, anexa 2, secțiunea „Registrul de casă" (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

- Norma numește explicit **două formulare distincte**, cu coduri diferite: „Registrul de casă" (cod 14-4-7A/7bA) pentru operațiunile în lei și „Registrul de casă (în valută)" (cod 14-4-7/aA/7cA) pentru cele în valută — deci răspunsul la „trebuie ținut separat de cel în lei?" e **da**, la nivel de formular.
- Textul nu detaliază **granularitatea pe monedă** — dacă o firmă încasează/plătește în mai multe valute (EUR și USD, de exemplu), corpusul verificat nu conține o precizare explicită dacă acestea intră într-un singur „registru în valută" sau necesită câte un registru pentru fiecare monedă. Practica uzuală separă evidența pe fiecare valută, ca să rămână clar soldul de casă pentru fiecare monedă deținută, dar aceasta e o interpretare practică, nu un citat direct din normă.
- Scopul declarat al registrului — stabilirea soldului de casă la sfârșitul fiecărei zile — are sens doar dacă soldul e calculat separat pe fiecare monedă; un sold „mixt" lei+valută sau valută+valută nu ar avea o interpretare contabilă coerentă.

## Ce se greșește în practică

- Se ține un singur registru „de casă", cu operațiuni în lei și în valută amestecate pe același rând — norma le tratează explicit ca formulare separate.
- Se convertesc operațiunile în valută în lei, la cursul zilei, direct în registrul de casă în lei, pierzând evidența soldului real rămas în valută la casierie.
- Se presupune că un singur „registru valutar" acoperă automat toate monedele străine folosite de firmă, fără o evidență clară, pe monedă, a soldului de casă.

## Ce face iConta.eu

Aici trebuie spusă direct limita produsului: **iConta.eu nu are, azi, suport pentru operațiuni de casă în valută**. Ecranul „card Casa" (`core/casa_api.py`) mapează toate operațiunile fix pe contul de casă în lei (`5311`), tabela din baza de date (`casa_operatiuni`) nu are nicio coloană de valută, iar formularul de introducere a unei operațiuni nu oferă opțiunea de a alege o monedă străină. Motorul de calcul intern (`core/casa.py`, funcția `regula_cont_casa`) conține, e drept, o ramură pregătită pentru conturile de casă în valută (5314/5124), dar acest cod **nu e apelat din nicio rută sau ecran** — e cod scris, dar neconectat la aplicația live.

Practic: dacă firma încasează sau plătește numerar în valută prin casierie, evidența acelor operațiuni trebuie ținută în afara ecranului „card Casa" din iConta.eu, cel puțin până la extinderea funcționalității.

[iConta.eu](/)
