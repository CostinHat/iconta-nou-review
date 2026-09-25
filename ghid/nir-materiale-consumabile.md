---
title: "Trebuie făcut NIR pentru materiale consumabile?"
description: "Cazurile în care Nota de recepție și constatare de diferențe (NIR) este obligatorie la achiziția de materiale consumabile, potrivit reglementărilor contabile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Trebuie făcut NIR pentru materiale consumabile?

Nu întotdeauna. Nota de recepție și constatare de diferențe (NIR) nu este obligatorie pentru orice intrare de bunuri în gestiune — reglementările contabile limitează obligativitatea ei la un set precis de situații, iar materialele consumabile intră sau nu sub această obligație în funcție de cum au fost livrate și facturate.

## Temeiul legal

::: ghid-temei
„Nota de recepție și constatare de diferențe se folosește ca document de recepție obligatoriu numai în cazul: - bunurilor materiale cuprinse într-o factură sau aviz de însoțire a mărfii, care fac parte din gestiuni diferite; - bunurilor materiale primite spre prelucrare, în custodie sau în păstrare; - bunurilor materiale procurate de la persoane fizice; - bunurilor materiale care sosesc neînsoțite de documente de livrare; - bunurilor materiale care prezintă diferențe la recepție; - mărfurilor intrate în gestiunile la care evidența se ține la preț de vânzare. În cazurile în care nu este obligatorie întocmirea NIR-ului, recepția și încărcarea în gestiune, după caz, și înregistrarea în contabilitate se fac pe baza documentului de livrare care însoțește transportul (factura, avizul de însoțire a mărfii etc.)."
— OMFP nr. 2.634/2015, Anexa 2, cod 14-3-1A (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Aplicat la materialele consumabile:

- Dacă materialele consumabile sosesc însoțite de **factură sau aviz de însoțire**, în cantitatea și la prețul comandat, **fără diferențe** și fac parte dintr-o singură gestiune, **NIR nu este obligatoriu** — recepția și înregistrarea se fac direct pe baza facturii sau avizului.
- Dacă materialele **prezintă diferențe la recepție** (cantitate, calitate, preț), sosesc **neînsoțite** de documente de livrare, sau sunt cumpărate **de la o persoană fizică**, NIR devine **obligatoriu**, indiferent de natura bunului.
- Dacă valorile nu se înscriu în NIR (chiar și atunci când acesta e întocmit), ele trebuie să se regăsească într-un alt document justificativ care stă la baza înregistrării contabile a valorii bunurilor.

## Ce se greșește în practică

- Se întocmește NIR pentru orice achiziție de consumabile, indiferent dacă factura/avizul acoperă deja complet recepția fără diferențe, dublând inutil documentația.
- Se omite NIR-ul tocmai în cazurile obligatorii — diferențe la recepție, bunuri neînsoțite de documente sau achiziții de la persoane fizice — recepționând marfa direct pe baza facturii, deși legea cere document separat.
- Se confundă gestiunea la preț de achiziție (unde NIR e obligatoriu doar în situațiile enumerate) cu gestiunea la preț de vânzare (unde NIR e întotdeauna obligatoriu pentru mărfurile intrate).

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un modul complet de NIR (`core/stocuri.py`, `core/stocuri_api.py`), care calculează adaosul comercial, TVA neexigibilă și coeficientul K, și generează notele contabile aferente pentru orice recepție introdusă — inclusiv pentru materiale consumabile. Aplicația **nu decide automat** dacă întocmirea unui NIR este obligatorie pentru o anumită recepție; contabilul este cel care alege, la fiecare achiziție, dacă înregistrează recepția direct pe bază de factură/aviz sau printr-un NIR complet, în funcție de situațiile prevăzute de normă.

[iConta.eu](/)
