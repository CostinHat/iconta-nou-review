---
title: "NIR pentru mărfuri primite fără factură: se poate"
description: "Cazurile în care Nota de recepție și constatare de diferențe (NIR) e documentul obligatoriu pentru mărfuri primite fără factură sau aviz, conform OMFP 2634/2015."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# NIR pentru mărfuri primite fără factură: se poate

Da, se poate — și nu doar se poate, ci e chiar situația pentru care NIR-ul e prevăzut explicit ca document obligatoriu. Marfa nu așteaptă factura ca să intre în gestiune: intră pe baza recepției, iar factura se atașează ulterior.

## Temeiul legal

::: ghid-temei
„Nota de recepție și constatare de diferențe (NIR) servește ca: - document pentru recepția bunurilor aprovizionate; - document justificativ pentru încărcare în gestiune; - document justificativ de înregistrare în contabilitate. Nota de recepție și constatare de diferențe se folosește ca document de recepție obligatoriu numai în cazul: - bunurilor materiale cuprinse într-o factură sau aviz de însoțire a mărfii, care fac parte din gestiuni diferite; - bunurilor materiale primite spre prelucrare, în custodie sau în păstrare; - bunurilor materiale procurate de la persoane fizice; - bunurilor materiale care sosesc neînsoțite de documente de livrare; - bunurilor materiale care prezintă diferențe la recepție; - mărfurilor intrate în gestiunile la care evidența se ține la preț de vânzare. În cazurile în care nu este obligatorie întocmirea NIR-ului, recepția și încărcarea în gestiune, după caz, și înregistrarea în contabilitate se fac pe baza documentului de livrare care însoțește transportul (factura, avizul de însoțire a mărfii etc.)."
— OMFP 2634/2015 (norme specifice privind întocmirea și utilizarea documentelor financiar-contabile), Anexa 2, cod 14-3-1A (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Ce rezultă concret:

- **„Bunurile materiale care sosesc neînsoțite de documente de livrare"** e listată explicit ca unul dintre cele șase cazuri în care NIR-ul e documentul obligatoriu de recepție — marfa fără factură, fără aviz, fără niciun document de la furnizor la momentul livrării, intră totuși legal în gestiune, pe baza NIR-ului întocmit de firma primitoare.
- **Valoarea la recepție**, în absența unui document cu preț, se stabilește de firmă (de regulă pe baza comenzii, a contractului sau a unei estimări rezonabile), urmând ca, la sosirea facturii, să se facă regularizarea — norma nu impune o metodă unică de evaluare provizorie, dar cere ca datele valorice să se regăsească „într-un alt document justificativ" dacă nu sunt înscrise direct în NIR.
- **Când sosesc bunuri în tranșe**, se întocmește câte un NIR pentru fiecare tranșă, care se anexează ulterior la factură sau la avizul de însoțire, dacă acestea sosesc separat.
- **La diferențe constatate la recepție** (cantitate sau valoare, plus sau minus față de document), NIR-ul e din nou documentul obligatoriu, iar firma trebuie să stabilească prin proceduri proprii ce informații se înscriu (cine a făcut recepția, ce diferențe s-au constatat).

## Ce se greșește în practică

- Se amână înregistrarea mărfii în gestiune până la sosirea facturii, lăsând stocul „neînregistrat" pentru zile sau săptămâni — norma cere exact contrariul: recepția și încărcarea în gestiune se fac imediat, pe baza NIR-ului, indiferent dacă factura a sosit.
- Se folosește avizul de însoțire a mărfii ca document de recepție și atunci când marfa a sosit fără niciun document — avizul nu poate justifica o recepție care, prin definiție, nu are niciun document de însoțire; NIR-ul e singurul document valabil în acest caz.
- Se omite regularizarea ulterioară, la sosirea facturii reale, dacă valoarea de pe factură diferă de estimarea din NIR-ul inițial — diferența trebuie reflectată în contabilitate, nu lăsată nereconciliată.

## Ce face iConta.eu

Modulul de stocuri din iConta.eu (`core/stocuri_api.py`, funcția `adauga_nir`) acceptă introducerea unui NIR cu referință de factură **opțională** (`factura_ref?`) — confirmând că fluxul e pregătit exact pentru cazul mărfii primite fără factură: contabilul poate înregistra recepția pe baza NIR-ului, cu datele de furnizor și valoare disponibile la momentul respectiv, și poate completa ulterior referința facturii când aceasta sosește. Regularizarea automată a eventualelor diferențe de valoare între NIR-ul provizoriu și factura sosită ulterior rămâne o operațiune pe care contabilul o introduce manual, ca notă contabilă separată.

[iConta.eu](/)
