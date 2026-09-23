---
title: "Cum se tratează fiscal activele distribuite asociaților la lichidare?"
description: "Ce parte din partajul de lichidare este neimpozabilă și ce cotă se aplică pe câștigul distribuit asociaților, cu o atenționare importantă privind cota folosită azi de aplicație."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se tratează fiscal activele distribuite asociaților la lichidare?

La partajul final, nu tot ce se distribuie asociaților este impozabil — doar câștigul, nu și capitalul propriu depus inițial.

## Temeiul legal

::: ghid-temei
„Venitul impozabil obținut din lichidarea unei persoane juridice de către acționari/asociați persoane fizice sau din reducerea capitalului social, potrivit legii, care nu reprezintă distribuții în bani sau în natură ca urmare a restituirii cotei-părți din aporturi se impun cu o cotă de 10%, impozitul fiind final. Obligația calculării, reținerii și plății impozitului revine persoanei juridice. Impozitul calculat și reținut la sursă în cazul lichidării persoanei juridice se plătește până la data depunerii situației financiare finale la oficiul registrului comerțului, întocmită de lichidatori [...]." (Codul fiscal, Legea 227/2015, art. 97 alin. (5))
:::

Capitalul social restituit asociaților nu este un câștig — este returnarea propriei lor contribuții, deci nu se impozitează. Ceea ce rămâne peste capitalul social — rezervele și profiturile acumulate, nedistribuite până atunci — reprezintă câștig impozabil pentru asociații persoane fizice, iar impozitul trebuie calculat, reținut și plătit de firmă, nu de asociați direct.

## Ce se greșește în practică

- Se impozitează greșit și restituirea capitalului social, ca și cum ar fi un câștig.
- Se omite reținerea și plata impozitului de către firmă înainte de depunerea situației financiare finale la registrul comerțului — dovada acestei plăți este cerută la radiere.

## Ce face iConta.eu

La operația „Partaj către asociați" din ecranul „Lichidare / radiere firmă" se introduc capitalul social, rezervele (opțional) și profiturile (opțional). Aplicația generează automat nota contabilă: capitalul social se descarcă ca neimpozabil (1012 = 456), iar rezervele și profiturile se tratează drept câștig impozabil (1061/1171 = 456), din care se calculează și rețin impozitul (456 = 446) și netul cuvenit asociatului (456 = 5121). Operațiunea returnează și valorile calculate — câștigul impozabil, impozitul, netul asociatului și cota aplicată.

**Atenționare importantă:** în prezent, cota de impozit folosită de aplicație pentru acest calcul este preluată din același registru de cote folosit pentru dividendele obișnuite (16% de la 1 ianuarie 2026, cu o istorie de 5%→8%→10%→16% în anii anteriori), nu cota fixă de 10% prevăzută explicit, pentru câștigul din lichidare distribuit persoanelor fizice, la art. 97 alin. (5) din Codul fiscal citat mai sus. Nu am găsit în textul legii nicio modificare a alineatului (5) prin legile care au schimbat cota de dividende, deci cele două cote par a fi, la acest moment, diferite din punct de vedere legal. Până la clarificarea sau corectarea acestui aspect, verificați manual cota aplicată pe orice partaj de lichidare generat de aplicație și, la nevoie, ajustați impozitul calculat.

[iConta.eu](/)
