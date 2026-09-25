---
title: "Cum leagă contabilul D205 de D101 la final de an"
description: "Impozitul pe dividende declarat prin D205 trebuie să corespundă cu evidența impozitului pe profit din D101 — o reconciliere pe care Codul de procedură fiscală o susține prin obligația de exactitate a declarațiilor."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum leagă contabilul D205 de D101 la final de an

D205 (declarația informativă privind impozitul reținut la sursă, inclusiv pe dividende) și D101 (impozitul pe profit anual) nu sunt declarații izolate — sumele din D205 pentru dividendele distribuite trebuie să fie coerente cu profitul distribuibil raportat prin D101, iar orice diferență nejustificată e un semnal de eroare.

## Temeiul legal

::: ghid-temei
„Contribuabilul/Plătitorul are obligația de a completa declarația fiscală înscriind corect, complet și cu bună-credință informațiile prevăzute de formular, corespunzătoare situației sale fiscale."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 102 alin. (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce trebuie corelat, practic, la final de an:

- Profitul contabil rămas după impozitare (reflectat, la nivel fiscal, prin D101) este sursa din care se pot distribui **dividende** — sumele efectiv distribuite și impozitul reținut pe ele se raportează separat, prin **D205**.
- O diferență mare între profitul distribuibil raportat prin D101 și volumul dividendelor declarate prin D205 (fără o explicație clară, precum rezerve legale sau pierderi reportate neacoperite) atrage, în practică, atenția organului fiscal la o eventuală verificare încrucișată.
- Termenele de depunere ale celor două declarații nu coincid (D101 are termen anual specific impozitului pe profit, D205 are propriul termen anual), ceea ce impune o reconciliere internă separată, nu doar o verificare la momentul depunerii fiecăreia.

## Ce se greșește în practică

- Se depune D205 fără a verifica dacă sumele distribuite ca dividende sunt acoperite de profitul distribuibil real, așa cum rezultă din D101 și din situațiile financiare aprobate de AGA.
- Se tratează cele două declarații ca procese complet separate, gestionate de departamente sau persoane diferite, fără un punct unic de reconciliere la final de an.
- Se ignoră faptul că distribuirile de dividende contrar prevederilor legale (din profituri nedeterminate potrivit legii) trebuie restituite societății, cu impact direct asupra corectitudinii ambelor declarații.

## Ce face iConta.eu

iConta.eu generează atât D101, cât și D205, pe baza acelorași date contabile din firmă, iar modulul de control încrucișat al aplicației realizează o reconciliere automată între cele două declarații (verificând, printre altele, coerența sumelor la nivel de perioadă și sursă). Interpretarea eventualelor diferențe semnalate — de exemplu, dacă provin din rezerve legale constituite sau din decalaje de calendar — rămâne o decizie a contabilului, aplicația oferind doar semnalul de discrepanță, nu explicația de fond.

[iConta.eu](/)
