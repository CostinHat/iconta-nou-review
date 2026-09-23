---
title: "Cum se descarcă gestiunea la un magazin online?"
description: Facturile emise automat prin integrarea magazinului online trec prin aceeași poartă ca cele din ecran — un câmp dedicat, obligatoriu la orice factură cu marfă din stoc, fără valoare implicită.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se descarcă gestiunea la un magazin online?

Un magazin online integrat cu iConta.eu (care emite facturi automat, prin API, la fiecare comandă) folosește, pentru o firmă cu gestiune cantitativ-valorică, exact aceeași regulă ca facturarea manuală din ecran: dacă factura conține cel puțin o linie legată de un articol de stoc, trebuie transmisă explicit informația dacă marfa pleacă odată cu factura. Nu există o "descărcare implicită", nici în sensul "se descarcă tot automat", nici în sensul "stocul rămâne neatins" — integrarea trebuie să declare, la fiecare factură, ce se întâmplă.

## Temeiul legal

::: ghid-temei
"440. - În contabilitate, veniturile din vânzări de bunuri se înregistrează în momentul predării bunurilor către cumpărători, al livrării lor pe baza facturii sau în alte condiţii prevăzute în contract, care atestă transferul dreptului de proprietate asupra bunurilor respective, către clienţi."
— OMFP 1802/2014, pct. 440
:::

La un magazin online, predarea mărfii coincide adesea cu emiterea facturii (comandă onorată din stoc, expediată imediat), dar nu întotdeauna — o comandă poate fi facturată în avans, cu livrare ulterioară. Legea leagă recunoașterea vânzării de predare, nu automat de factură — de aici necesitatea ca integrarea să declare explicit momentul.

## Ce se greșește în practică

- Integrarea nu trimite deloc informația despre plecarea mărfii, presupunând un comportament implicit — la o factură cu linii de stoc, lipsa acestui câmp face ca cererea de emitere să fie respinsă, nu emisă cu o presupunere.
- Se folosește numele câmpului din interfața internă (`pleaca_marfa`) în cererea către API — API-ul public de integrare are un nume de câmp propriu, diferit.
- Se așteaptă ca produsele marcate ca servicii (fără legătură la un articol de stoc) să declanșeze și ele întrebarea — poarta se declanșează doar dacă există cel puțin o linie legată efectiv de un articol.

## Ce face iConta.eu

Pentru integrări externe (tipic, un magazin online care emite facturi automat), iConta.eu expune o rută API de emitere a facturilor. Dacă factura conține linii legate de articole de stoc, la o firmă cu gestiune cantitativ-valorică, cererea trebuie să conțină explicit câmpul care spune dacă marfa pleacă odată cu factura; în lipsa lui, cererea e respinsă cu un cod de eroare dedicat, cu mesaj explicativ. Când răspunsul e afirmativ, gestiunea se descarcă automat, în aceeași operațiune cu emiterea facturii, folosind exact același mecanism ca și emiterea din ecran.

Menționăm onest: mecanismul se aplică doar firmelor cu gestiune cantitativ-valorică — un magazin online al unei firme pe metoda global-valorică nu are această poartă; descărcarea rămâne cea lunară.

[iConta.eu](/)
