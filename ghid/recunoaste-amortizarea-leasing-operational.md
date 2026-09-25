---
title: "Cum se recunoaște amortizarea în leasing operațional"
description: "La leasingul operațional, locatarul nu recunoaște nicio amortizare — bunul rămâne evidențiat extrabilanțier; amortizarea aparține exclusiv locatorului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se recunoaște amortizarea în leasing operațional

Întrebarea presupune că firma utilizatoare (locatarul) ar trebui, la un moment dat, să recunoască o amortizare pentru bunul luat în leasing operațional. Regula spune contrariul: la locatar, această amortizare nu se recunoaște niciodată — bunul rămâne extrabilanțier.

## Temeiul legal

::: ghid-temei
„214. ‐ (1) Înregistrarea în contabilitate a amortizării bunului ce face obiectul contractului se efectuează în cazul leasingului financiar de către locatar/utilizator, iar în cazul leasingului operațional, de către locator/finanțator. [...] (3) În cazul leasingului operațional, bunurile sunt supuse amortizării de către locator, pe o bază consecventă cu politica normală de amortizare pentru bunuri similare ale acestuia."
— OMFP 1802/2014, pct. 214 alin. (1) și (3) (sursă: anaf_surse/omfp_1802_2014.txt)

„218. ‐ (1) În contabilitatea locatarului, bunurile luate în leasing operațional sunt evidențiate în conturi de evidență din afara bilanțului."
— OMFP 1802/2014, pct. 218 alin. (1) (sursă: anaf_surse/omfp_1802_2014.txt)
:::

- La locatar, bunul luat în leasing operațional nu intră niciodată în conturile de imobilizări — e evidențiat doar **extrabilanțier**, informativ.
- Recunoașterea amortizării aparține integral locatorului (societatea de leasing), pe propria politică de amortizare pentru bunuri similare.
- O firmă care doar plătește chirie pentru un bun în leasing operațional nu are, în propria contabilitate, nicio operațiune de amortizare legată de acel bun.

## Ce se greșește în practică

- Contabilul locatarului caută o „notă de amortizare" pentru bunul în leasing operațional — nu există, pentru că bunul nu e în patrimoniul lui.
- Se confundă evidența extrabilanțieră (informativă) cu o înregistrare de amortizare propriu-zisă.
- Se presupune greșit că, din moment ce firma plătește chirie, poate recunoaște și o amortizare paralelă — asta ar dubla nejustificat cheltuiala.

## Ce face iConta.eu

Din perspectiva locatarului — singura implementată în F056 (Leasing financiar și operațional) — funcția `nota_rata_operational` înregistrează doar chiria (612=401, plus TVA pe 4426), fără nicio linie de amortizare, consecvent cu regula legală de mai sus. Partea de locator, care ar recunoaște efectiv amortizarea bunului dat în leasing operațional, nu e implementată deloc în aplicație — o societate de leasing care ar căuta acest ecran pentru propria contabilitate nu găsește niciun suport aici.

[iConta.eu](/)
