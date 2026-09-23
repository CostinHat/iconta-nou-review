---
title: "Cum tratez transportul facturat de un transportator din afara UE pentru marfă din UE?"
description: "Când transportatorul nu are cod de TVA UE, operațiunea nu e intracomunitară în sensul D390/VIES, chiar dacă marfa transportată circulă în interiorul UE."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez transportul facturat de un transportator din afara UE pentru marfă din UE?

Situația e ușor de confundat: marfa transportată circulă în interiorul Uniunii Europene, dar transportatorul care emite factura nu e stabilit și nu are cod de TVA într-un stat membru UE (de exemplu e o firmă din afara Uniunii). Contează cine emite factura, nu unde circulă marfa.

## Temeiul legal

::: ghid-temei
CF art. 278 alin. (2): „Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L17303-17420)
:::

Regula locului prestării pentru servicii B2B (locul beneficiarului) e o regulă generală de TVA, care nu depinde de statutul UE/non-UE al prestatorului. Dar mecanismul de declarare **D390/VIES**, descris în acest dosar, este specific operațiunilor cu parteneri înregistrați în scopuri de TVA în alte state membre UE — pentru că D390 e o declarație recapitulativă legată de sistemul VIES.

Dacă transportatorul nu are cod de TVA valid într-un stat membru UE (de exemplu are un cod fiscal dintr-un stat terț), factura primită **nu e o operațiune intracomunitară** în sensul acestui ghid — nu se verifică în VIES, nu se declară în D390. Asta nu înseamnă automat că TVA nu se datorează în România prin alt mecanism (regulile generale de taxare inversă pentru servicii primite de la persoane nestabilite pot rămâne relevante) — dar acel mecanism nu e cel descris în acest dosar (F050, operațiuni intracomunitare) și nu e detaliat aici.

## Ce se greșește în practică

- Se tratează orice transport legat de o marfă „din UE” ca fiind automat o operațiune intracomunitară, fără a verifica dacă transportatorul însuși are cod de TVA într-un stat membru UE.
- Se încearcă declararea în D390 a unei operațiuni cu un transportator fără cod de TVA UE — D390 e o declarație recapitulativă VIES, nu acoperă parteneri din afara UE.
- Se presupune, greșit, că lipsa unui cod de TVA UE al transportatorului scutește automat operațiunea de orice obligație de TVA în România — tratamentul rămâne de verificat, doar că nu prin mecanismul F050.

## Ce face iConta.eu

Verificarea VIES din iConta (folosită la emiterea facturilor și în formularele `achizitie_ic`/`vanzare_ic`) interoghează explicit sistemul VIES, aplicabil doar codurilor de TVA din statele membre UE (plus „XI” pentru Irlanda de Nord) — un cod de TVA dintr-un stat din afara UE nu poate fi verificat prin acest mecanism și nu poate fi clasificat ca operațiune intracomunitară pentru D390.

Pentru o factură de la un transportator fără cod de TVA UE, operațiunea nu se înregistrează prin formularele dedicate F050 (`achizitie_ic`/`vanzare_ic` cu clasificare D390) — tratamentul ei TVA e o temă diferită, neacoperită de cercetarea care stă la baza acestui ghid.

[iConta.eu](/)
