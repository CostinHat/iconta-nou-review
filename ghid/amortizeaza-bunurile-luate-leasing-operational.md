---
title: "Se amortizează bunurile luate în leasing operațional?"
description: "Nu, la firma utilizatoare — bunul rămâne extrabilanțier; amortizarea aparține exclusiv societății de leasing, care rămâne proprietarul lui contabil și fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se amortizează bunurile luate în leasing operațional?

Nu, nu la firma care folosește bunul. La leasingul operațional, amortizarea rămâne integral în sarcina societății de leasing (locatorul) — utilizatorul (locatarul) doar plătește o chirie și evidențiază bunul extrabilanțier, informativ.

## Temeiul legal

::: ghid-temei
„214. ‐ (1) Înregistrarea în contabilitate a amortizării bunului ce face obiectul contractului se efectuează în cazul leasingului financiar de către locatar/utilizator, iar în cazul leasingului operațional, de către locator/finanțator. [...] (3) În cazul leasingului operațional, bunurile sunt supuse amortizării de către locator, pe o bază consecventă cu politica normală de amortizare pentru bunuri similare ale acestuia."
— OMFP 1802/2014, pct. 214 alin. (1) și (3) (sursă: anaf_surse/omfp_1802_2014.txt)

„218. ‐ (1) În contabilitatea locatarului, bunurile luate în leasing operațional sunt evidențiate în conturi de evidență din afara bilanțului."
— OMFP 1802/2014, pct. 218 alin. (1) (sursă: anaf_surse/omfp_1802_2014.txt)
:::

- Răspunsul e clar: **nu**, la locatar (firma utilizatoare) — bunul nu intră niciodată în conturile lui de imobilizări.
- **Da**, la locator (societatea de leasing) — el rămâne proprietarul contabil și fiscal al bunului și îl amortizează după propria politică pentru bunuri similare.
- La locatar, bunul e evidențiat doar extrabilanțier, ca informație, nu ca activ propriu-zis.

## Ce se greșește în practică

- Se amortizează „din prudență" bunul și la firma utilizatoare, ca să nu rămână neînregistrat nicăieri — greșit, asta dublează nejustificat cheltuiala și contravine regulii legale.
- Se tratează evidența extrabilanțieră ca opțională — de fapt OMFP pct. 218 alin. (1) o cere explicit, ca informație despre bunurile folosite, nu deținute.

## Ce face iConta.eu

Funcția `nota_rata_operational` din F056 (Leasing financiar și operațional) confirmă exact această regulă în cod: nu există nicio linie de amortizare sau de imobilizare generată pentru bunurile luate în leasing operațional — doar chiria (612=401, plus TVA pe 4426). Aplicația e consecventă cu răspunsul „nu" de mai sus: nu propune, nu automatizează și nu permite din acest ecran nicio amortizare la firma utilizatoare.

[iConta.eu](/)
