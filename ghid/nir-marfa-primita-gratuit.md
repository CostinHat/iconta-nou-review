---
title: "Se face NIR pentru marfa primită gratuit?"
description: "Când e obligatorie Nota de recepție pentru mărfurile primite cu titlu gratuit, conform OMFP 2634/2015, și ce document o poate înlocui."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se face NIR pentru marfa primită gratuit?

Marfa primită fără plată — mostre de la furnizor, bunuri cedate cu titlu gratuit între firme, stimulente de vânzare — trebuie totuși încărcată în gestiune și înregistrată în contabilitate. Întrebarea e dacă documentul obligatoriu e neapărat NIR-ul.

## Temeiul legal

::: ghid-temei
„Nota de recepție și constatare de diferențe se folosește ca document de recepție obligatoriu numai în cazul: - bunurilor materiale cuprinse într-o factură sau aviz de însoțire a mărfii, care fac parte din gestiuni diferite; - bunurilor materiale primite spre prelucrare, în custodie sau în păstrare; - bunurilor materiale procurate de la persoane fizice; - bunurilor materiale care sosesc neînsoțite de documente de livrare; - bunurilor materiale care prezintă diferențe la recepție; - mărfurilor intrate în gestiunile la care evidența se ține la preț de vânzare. [...] Avizul de însoțire a mărfii servește ca: [...] - document de descărcare din gestiune a bunurilor cedate cu titlu gratuit."
— OMFP 2634/2015, Anexa 2, Cod 14-3-1A și Cod 14-3-6A (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Rezultă:

- **NIR nu e obligatoriu doar pentru că marfa e primită gratuit** — "primirea cu titlu gratuit" nu apare ca atare printre cele șase cazuri obligatorii de NIR.
- Furnizorul care cedează marfa gratuit o însoțește, de regulă, cu un **Aviz de însoțire a mărfii cu mențiunea „Fără factură"** — document care, la beneficiar, poate sta la baza recepției și încărcării în gestiune, exact ca la o achiziție obișnuită fără diferențe.
- **NIR devine totuși obligatoriu** dacă la recepția mărfii gratuite apar diferențe cantitative/calitative, dacă marfa sosește neînsoțită de niciun document, sau dacă gestiunea beneficiarului ține evidența la preț de vânzare (comerț cu amănuntul) — exact aceleași criterii care se aplică oricărei alte recepții.

## Ce se greșește în practică

- Se presupune că orice marfă primită gratuit cere obligatoriu NIR, "pentru că nu are factură" — absența facturii nu e unul dintre criteriile care declanșează obligativitatea, dacă există avizul de însoțire.
- Se încarcă marfa în gestiune fără niciun document justificativ, pe motiv că "a fost cadou" — chiar și gratuită, marfa trebuie recepționată pe baza unui document (aviz sau NIR, după caz) și evaluată la valoare justă pentru înregistrarea în contabilitate.
- Se omite verificarea diferențelor la recepție doar pentru că marfa nu a costat nimic — dacă apar diferențe, NIR devine obligatoriu indiferent de valoarea plătită.

## Ce face iConta.eu

La data acestui ghid, `core/stocuri_cv_api.py` oferă funcția generală `intrare()` pentru încărcarea cantitativă în gestiune, indiferent de sursa documentului (factură, aviz sau NIR). Aplicația nu are un câmp sau flux dedicat „marfă primită gratuit" care să aplice automat criteriile de mai sus și să decidă dacă NIR e sau nu obligatoriu — alegerea documentului de recepție și verificarea diferențelor rămân, azi, în sarcina contabilului.

[iConta.eu](/)
