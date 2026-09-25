---
title: "Cum calculez obligațiile unui SRL micro care intră în lichidare?"
description: "Ce impozite datorează un SRL plătitor de impozit pe cifra de afaceri (micro) și asociații lui persoane fizice la intrarea în lichidare, conform Codului fiscal și Legii 31/1990."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum calculez obligațiile unui SRL micro care intră în lichidare?

Statutul de „micro" (impozit pe veniturile microîntreprinderilor, aplicat pe cifra de afaceri) nu dispare automat la deschiderea lichidării — firma continuă să datoreze acest impozit pe activitatea curentă până la încetarea ei efectivă, în timp ce lichidarea propriu-zisă declanșează un impozit separat, la nivelul asociaților.

## Temeiul legal

::: ghid-temei
„Venitul impozabil obținut din lichidarea unei persoane juridice de către acționari/asociați persoane fizice sau din reducerea capitalului social, potrivit legii, care nu reprezintă distribuții în bani sau în natură ca urmare a restituirii cotei-părți din aporturi se impun cu o cotă de 10%, impozitul fiind final. Obligația calculării, reținerii și plății impozitului revine persoanei juridice. Impozitul calculat și reținut la sursă în cazul lichidării persoanei juridice se plătește până la data depunerii situației financiare finale la oficiul registrului comerțului [...]."
— Legea 227/2015 (Codul fiscal), art. 97 alin. (5) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din combinația regimului micro cu regimul de lichidare rezultă două obligații distincte, de calculat separat:

- **impozitul pe veniturile microîntreprinderii** (pe cifra de afaceri) se calculează și se declară în continuare pentru toată perioada în care firma desfășoară efectiv activitate economică, până la data încetării/dizolvării — deschiderea lichidării nu suspendă acest impozit;
- **impozitul de 10% pe câștigul din lichidare**, final, se aplică doar asupra sumelor distribuite asociaților persoane fizice care **depășesc** restituirea aporturilor lor (adică pe rezerve, profituri reportate, alte sume din activul net rămas peste capitalul social vărsat) — restituirea capitalului social vărsat nu e impozabilă;
- **obligația de calcul, reținere și plată** a acestui impozit de 10% revine societății (nu asociatului), iar termenul de plată e legat de **depunerea situației financiare finale la registrul comerțului**, întocmită de lichidatori — nu de un termen calendaristic fix;
- dovada plății acestui impozit e, la rândul ei, o condiție pentru înregistrarea cererii de radiere a societății (art. 260 alin. 6 din Legea 31/1990).

## Ce se greșește în practică

- Se oprește depunerea declarației de impozit pe veniturile microîntreprinderii din luna deschiderii lichidării, deși firma continuă să genereze venituri din valorificarea activelor rămase — impozitul pe cifra de afaceri rămâne datorat până la încetarea efectivă a activității.
- Se calculează impozitul de 10% pe întreaga sumă distribuită asociaților, inclusiv pe restituirea capitalului social vărsat — doar excedentul peste aporturi e impozabil.
- Se confundă impozitul pe câștigul din lichidare (10%, final, art. 97 alin. 5) cu regimul dividendelor (16%, din 2026, art. 97 alin. 7) — sunt cote și articole distincte, chiar dacă ambele privesc sume distribuite asociaților.

## Ce face iConta.eu

iConta.eu are un motor de calcul dedicat lichidării (`core/lichidare.py`), care aplică explicit cota de 10%, impozit final, conform art. 97 alin. (5) din Codul fiscal — distinctă de regimul dividendelor (16%, alin. 7). Motorul acoperă etapele de valorificare a activelor, închiderea TVA/impozitelor curente și partajul între asociați (restituire capital social — neimpozabilă — vs. rezerve/profituri — impozabile cu 10%). Aplicația nu depune însă declarațiile la ANAF sau cererea de radiere la ONRC — acestea rămân pași manuali, pe baza calculelor produse.

[iConta.eu](/)
