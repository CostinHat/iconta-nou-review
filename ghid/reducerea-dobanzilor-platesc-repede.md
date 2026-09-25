---
title: "Reducerea dobânzilor dacă plătesc mai repede"
description: "Precizare: nu e o reducere de dobânzi, ci o bonificație de 3% din impozitul pe profit/impozitul micro anual, condiționată de depunerea la timp a declarațiilor și plata integrală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Reducerea dobânzilor dacă plătesc mai repede

Titlul acestei întrebări se referă, în practică, la un mecanism care nu este propriu-zis o „reducere de dobânzi", ci o **bonificație** aplicată direct asupra impozitului pe profit sau a impozitului pe veniturile microîntreprinderilor, condiționată de disciplina declarativă și de plată integrală.

## Temeiul legal

::: ghid-temei
„Articolul 7 Acordarea unei bonificații în cazul impozitului pe profit și impozitului pe veniturile microîntreprinderilor
(1) Contribuabilii plătitori de impozit pe profit, indiferent de sistemul de declarare și plată prevăzut la art. 41 din Legea nr. 227/2015 privind Codul fiscal, cu modificările și completările ulterioare, precum și contribuabilii plătitori de impozit pe veniturile microîntreprinderilor, potrivit titlului III „Impozitul pe veniturile microîntreprinderilor“ din aceeași lege, beneficiază de o bonificație de 3% din impozitul pe profit anual/impozitul pe veniturile microîntreprinderilor, aferente anului fiscal 2025/anului fiscal modificat care începe în anul 2025, după caz."
— Ordonanța de urgență a Guvernului nr. 8/2026, art. 7 alin. (1), reprodus în nota la Legea nr. 227/2015 (Codul fiscal) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Precizări importante despre acest mecanism:

- Nu este o **reducere a dobânzilor de întârziere** — este o **bonificație de 3%** aplicată impozitului anual pe profit sau impozitului pe veniturile microîntreprinderilor, deci o reducere a impozitului însuși, nu a accesoriilor.
- Condiția de bază, potrivit textului sursă mai larg al articolului (a se vedea și cod_fiscal_227_2015_consolidat.txt, linia care detaliază condițiile), este ca firma să aibă **depuse toate declarațiile** conform vectorului fiscal — deci disciplina declarativă, nu doar viteza de plată, contează.
- Bonificația nu se restituie în bani — sumele se utilizează pentru compensare cu alte obligații fiscale ale contribuabilului.

## Ce se greșește în practică

- Se așteaptă o reducere a dobânzilor de întârziere pentru plata anticipată a unei datorii restante — mecanismul de mai sus nu vizează dobânzile, ci reduce direct impozitul anual, pentru contribuabili la zi.
- Se presupune că bonificația se aplică automat, fără verificare — organul fiscal constată din oficiu îndeplinirea condițiilor, dar o declarație rectificativă ulterioară care majorează obligația poate anula bonificația deja acordată.
- Se confundă bonificația de 3% cu o reducere generală, permanentă — textul citat o leagă explicit de un an fiscal determinat (2025, respectiv anul fiscal modificat aferent), nu de o regulă valabilă nelimitat.

## Ce face iConta.eu

Verificat în cod: nu am găsit în `core/` un modul dedicat calculului automat al bonificației de 3% la impozitul pe profit sau la impozitul micro — declarațiile D100/D101 generate de aplicație reflectă impozitul datorat calculat conform regulilor curente, dar aplicarea bonificației (verificarea condițiilor, compensarea) rămâne, la acest moment, un proces gestionat direct de organul fiscal, în afara automatizării din iConta.eu.

[iConta.eu](/)
