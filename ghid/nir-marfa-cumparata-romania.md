---
title: "Trebuie făcut NIR pentru marfa cumpărată din România?"
description: "Cazurile în care Nota de recepție și constatare de diferențe (NIR) e obligatorie, conform OMFP 2634/2015, și cele în care recepția se face direct pe bază de factură."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Trebuie făcut NIR pentru marfa cumpărată din România?

Mulți contabili întocmesc NIR pentru orice marfă intrată în gestiune, indiferent de sursă, din prudență. Norma nu cere însă acest lucru în mod universal — obligativitatea NIR e limitată la un set precis de situații.

## Temeiul legal

::: ghid-temei
„Nota de recepție și constatare de diferențe se folosește ca document de recepție obligatoriu numai în cazul: - bunurilor materiale cuprinse într-o factură sau aviz de însoțire a mărfii, care fac parte din gestiuni diferite; - bunurilor materiale primite spre prelucrare, în custodie sau în păstrare; - bunurilor materiale procurate de la persoane fizice; - bunurilor materiale care sosesc neînsoțite de documente de livrare; - bunurilor materiale care prezintă diferențe la recepție; - mărfurilor intrate în gestiunile la care evidența se ține la preț de vânzare. În cazurile în care nu este obligatorie întocmirea NIR-ului, recepția și încărcarea în gestiune, după caz, și înregistrarea în contabilitate se fac pe baza documentului de livrare care însoțește transportul (factura, avizul de însoțire a mărfii etc.)."
— OMFP 2634/2015, Anexa 2, Cod 14-3-1A — Notă de recepție și constatare de diferențe (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Aplicat la marfa cumpărată din România, cu factură, de la un furnizor persoană juridică:

- **NIR nu e obligatoriu** dacă marfa vine însoțită de factură, corespunde cantitativ și valoric cu ce s-a comandat și nu se încadrează în niciuna dintre cele șase situații enumerate — recepția și încărcarea în gestiune se fac direct pe baza facturii.
- **NIR devine obligatoriu** dacă apare oricare dintre excepții: se constată diferențe cantitative sau calitative la recepție, marfa e cuprinsă într-o factură care acoperă mai multe gestiuni, sau gestiunea respectivă ține evidența la preț de vânzare (comerț cu amănuntul, metoda global-valorică).
- Chiar și fără NIR obligatoriu, dacă datele valorice nu se regăsesc integral pe documentul de livrare, ele trebuie să apară în alt document justificativ care stă la baza înregistrării contabile.

## Ce se greșește în practică

- Se întocmește NIR pentru fiecare recepție, "ca să fie sigur", deși norma nu-l cere — practică inofensivă, dar care nu înlocuiește verificarea reală a cazurilor obligatorii.
- Se sare peste NIR și în situațiile în care el e obligatoriu (ex. diferențe constatate la recepție), pe motiv că "există factură" — factura nu acoperă diferența constatată, doar comanda inițială.
- Se confundă absența NIR-ului cu absența oricărui document de recepție — chiar și fără NIR, factura/avizul rămân document justificativ obligatoriu de înregistrare.

## Ce face iConta.eu

La data acestui ghid, `core/stocuri_cv_api.py` oferă funcția `intrare_din_factura()`, care generează direct intrarea cantitativă în gestiune pe baza facturii de achiziție validate, fără a impune un NIR separat — coerent cu regula de mai sus pentru cazul fără diferențe. Pentru situațiile în care NIR-ul e obligatoriu (diferențe la recepție, evidență la preț de vânzare), `core/stocuri.py` conține motorul `nir_gv()` pentru NIR global-valoric, cu calcul de adaos și TVA neexigibilă. Alegerea între cele două fluxuri rămâne, azi, o decizie a contabilului la fiecare recepție, nu una automatizată în funcție de criteriile legale de mai sus.

[iConta.eu](/)
