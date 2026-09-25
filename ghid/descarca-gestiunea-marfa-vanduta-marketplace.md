---
title: "Cum se descarcă gestiunea pentru marfa vândută prin marketplace?"
description: "Momentul la care marfa vândută printr-un marketplace trebuie scoasă din gestiune — data transferului riscurilor și beneficiilor, nu data facturii sau a decontului primit de la platformă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se descarcă gestiunea pentru marfa vândută prin marketplace?

Vânzarea printr-un marketplace introduce un decalaj natural: curierul livrează marfa, dar comanda apare în contabilitate abia când vine factura sau decontul periodic al platformei. Regula contabilă însă e clară — momentul descărcării de gestiune nu așteaptă documentele administrative ale marketplace-ului.

## Temeiul legal

::: ghid-temei
„283. - (1) Înregistrarea în contabilitate a intrării stocurilor se efectuează la data transferului riscurilor și beneficiilor. (2) În general, datele de transfer al controlului, de transfer al proprietății și de livrare coincid. Totuși, pot exista decalaje de timp, de exemplu, pentru: [...] – bunuri livrate și nefacturate, care trebuie scoase din evidență, transferul de proprietate având loc [...]"
— OMFP nr. 1.802/2014 (Reglementările contabile privind situațiile financiare anuale individuale și consolidate), pct. 283 alin. (1), (2) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat la o vânzare prin marketplace:

- Regula funcționează simetric pentru intrări și ieșiri de stoc: dacă bunurile au fost **livrate**, dar factura nu a fost încă emisă (de exemplu marketplace-ul confirmă livrarea, dar firma facturează abia la finalul zilei sau al săptămânii), marfa trebuie scoasă din gestiune la data livrării, nu la data facturii.
- Momentul relevant e **transferul riscurilor și beneficiilor** către cumpărător — de regulă data la care curierul confirmă livrarea sau data la care marketplace-ul înregistrează comanda ca finalizată, nu data la care platforma virează banii firmei sau emite decontul periodic de comision.
- Dacă marketplace-ul funcționează cu retur (client refuză coletul), stocul nu s-a descărcat definitiv până nu se confirmă livrarea efectivă — un colet aflat în tranzit sau refuzat trebuie tratat distinct, ca stoc aflat încă la dispoziția firmei sau returnat.
- Decontul comercial primit periodic de la marketplace (cu comisioane reținute) e un document de decontare financiară, nu documentul care determină data descărcării de gestiune — acesta rămâne legat de livrarea efectivă a fiecărei comenzi.

## Ce se greșește în practică

- Se descarcă gestiunea abia la primirea decontului periodic al marketplace-ului, deși livrările individuale s-au produs, în realitate, zile sau săptămâni mai devreme.
- Se ignoră comenzile livrate dar nefacturate încă, lăsând stocul contabil „umflat" față de stocul fizic real, până la emiterea facturii.
- Nu se tratează separat coletele refuzate sau returnate de client, considerându-le vândute definitiv doar pentru că marketplace-ul le-a marcat inițial ca „expediate".

## Ce face iConta.eu

La data acestui ghid, iConta.eu descarcă gestiunea pe baza facturilor emise, folosind coeficientul de repartizare a diferențelor de preț pentru metoda global-valorică (`core/stocuri.py`, funcția `descarcare_gv`). Pentru magazinele conectate prin WooCommerce, comenzile importate automat (`core/woocommerce.py`) generează facturi pe baza cărora se face descărcarea de gestiune — dar pentru vânzările prin alte marketplace-uri (Amazon, eMAG și altele, fără conector dedicat), introducerea comenzii și, implicit, momentul descărcării de gestiune depind de data la care utilizatorul introduce manual factura, nu de data reală a livrării confirmate de platformă.

[iConta.eu](/)
