---
title: "Care este monografia contabilă pentru descărcarea de gestiune?"
description: "Principiul contabil din spatele descărcării de gestiune (recunoașterea ieșirii din stoc odată cu vânzarea), cu temeiul din reglementările contabile aplicabile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Care este monografia contabilă pentru descărcarea de gestiune?

„Descărcarea de gestiune" e termenul folosit în practica contabilă pentru operațiunea prin care, la vânzarea unui bun, valoarea lui e scoasă din stoc și trecută pe cheltuială (607/601), în paralel cu recunoașterea venitului din vânzare (707/701). Termenul nu e definit ca atare în reglementările contabile, dar principiul din spatele lui — corelarea între ieșirea din gestiune și înregistrarea în contabilitate — este.

## Temeiul legal

::: ghid-temei
„În cazul unor decalaje între vânzarea și livrarea bunurilor, acestea se înregistrează ca ieșiri din entitate, nemaifiind considerate proprietatea acesteia, astfel: – bunurile vândute și nelivrate se înregistrează distinct în gestiune, iar în contabilitate în conturi în afara bilanțului; – bunurile livrate, dar nefacturate se înregistrează ca ieșiri din gestiune atât la locurile de depozitare, cât și în contabilitate, pe baza documentelor care confirmă ieșirea din gestiune potrivit legii [...]."
— OMFP nr. 1.802/2014, pct. 284 alin. (2) lit. c) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Cum se traduce principiul în monografia uzuală pentru vânzarea de marfă/produse:

- La vânzare, se înregistrează **simultan** venitul (4111 = 707 „Venituri din vânzarea mărfurilor" + 4427 TVA colectată) **și** descărcarea gestiunii (607 „Cheltuieli privind mărfurile" = 371 „Mărfuri", la costul de achiziție/producție al bunului ieșit) — cele două note contabile nu sunt independente, se fac în aceeași perioadă, pe baza aceluiași document.
- Pentru produse finite, corespondența e 711 „Variația stocurilor" = 345 „Produse finite" (dacă entitatea folosește metoda inventarului permanent cu evaluare la cost standard/producție), respectiv 701 „Venituri din vânzarea produselor finite" pentru venit.
- Reglementările confirmă explicit cazurile de **decalaj** între vânzare și livrare (bun vândut, dar nelivrat încă, respectiv livrat, dar nefacturat încă) — în ambele situații, ieșirea din gestiune se face pe baza documentului care confirmă efectiv ieșirea fizică a bunului, nu pe baza facturii dacă aceasta nu coincide cu livrarea.
- Documentul justificativ al ieșirii din gestiune (aviz de expediție, factură, proces-verbal de predare) trebuie să existe pentru fiecare descărcare — o notă contabilă de descărcare de gestiune fără document suport nu are acoperire legală.

## Ce se greșește în practică

- Se înregistrează venitul din vânzare fără descărcarea concomitentă a gestiunii, „amânând" ieșirea de stoc pentru o dată ulterioară — asta suprapune vânzarea cu un stoc contabil care nu mai există fizic.
- Se descarcă gestiunea la valoarea facturii (preț de vânzare) în loc de costul de achiziție/producție — descărcarea de gestiune se face la cost, nu la preț de vânzare; diferența e marja, reflectată separat prin venit.
- Se ignoră decalajele dintre vânzare și livrare (bunuri vândute dar nelivrate, sau livrate dar nefacturate), tratând mereu factura ca moment unic al ieșirii din gestiune, chiar și când livrarea fizică s-a produs în altă perioadă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu ține evidența stocurilor cantitativ-valoric prin metoda costului mediu ponderat (CMP), recalculat după fiecare intrare (OMFP 1802/2014, pct. 96) — la fiecare ieșire înregistrată în aplicație, valoarea descărcată din gestiune se calculează automat la CMP-ul curent al articolului, iar nota contabilă de descărcare (607=371 pentru marfă, 601=301 pentru materii prime) se generează în corespondență cu mișcarea de stoc, nu separat de ea.

[iConta.eu](/)
