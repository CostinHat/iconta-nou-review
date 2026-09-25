---
title: "Cum se înregistrează încasările prin casa de marcat în registrul de casă?"
description: "Documentul care stă la baza înregistrării în registrul de casă a încasărilor zilnice prin aparatul de marcat electronic fiscal, conform OMFP 2634/2015."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează încasările prin casa de marcat în registrul de casă?

Vânzările cu numerar către populație, prin aparatul de marcat electronic fiscal, nu se înregistrează în registrul de casă bon cu bon — legea prevede un singur document centralizator pentru toată ziua.

## Temeiul legal

::: ghid-temei
„Chitanța și chitanța pentru operațiuni în valută sunt documente justificative de înregistrare în registrul de casă/registrul de casă în valută și în contabilitate a încasărilor și plăților efectuate în numerar (lei/valută) [...]. În condițiile utilizării aparatelor de marcat electronice fiscale, în conformitate cu prevederile legale, documentul în baza căruia se înregistrează în contabilitate veniturile aferente încasărilor zilnice este Raportul fiscal de închidere zilnică, respectiv Registrul special întocmit în condițiile defectării aparatelor de marcat electronice fiscale."
— OMFP 2634/2015, Anexa 2, Cod 14-4-1 — Chitanța (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Ce rezultă pentru registrul de casă:

- **Documentul de bază nu e chitanța individuală**, ci **Raportul fiscal de închidere zilnică (raportul Z)**, emis de AMEF la sfârșitul programului — el centralizează toate încasările zilei și e cel care intră în registrul de casă și în contabilitate ca sumă unică.
- Chitanța rămâne documentul justificativ pentru încasările fără AMEF (cazuri scutite fără drept de deducere, situații particulare) — dar pentru vânzările prin casa de marcat, raportul Z o înlocuiește ca bază de înregistrare.
- Dacă aparatul se defectează, obligația de raportare nu dispare: se folosește **Registrul special** întocmit pentru perioada de defectare (OUG 28/1999, art. 1 alin. (8)), cu aceeași funcție de document-suport pentru înregistrarea veniturilor zilei.
- Registrul de casă (Cod 14-4-7A) se completează zilnic, pe baza documentelor justificative de încasări și plăți, și stabilește soldul de casă la sfârșitul fiecărei zile.

## Ce se greșește în practică

- Se încearcă introducerea în registrul de casă a fiecărui bon fiscal în parte — corect e o singură sumă zilnică, preluată din raportul Z, nu suma bon cu bon.
- Se omite complet raportul Z din contabilitate, considerându-l "doar pentru control fiscal" — el e chiar documentul justificativ de înregistrare a veniturilor din vânzările cu numerar.
- Se ignoră obligația registrului special la defectarea AMEF — fără el, veniturile din perioada de defectare rămân fără document-suport pentru contabilitate.

## Ce face iConta.eu

La data acestui ghid, `core/amef_import.py` conține `parseaza_raport_z()`, care preia raportul fiscal de închidere zilnică (XML) exportat de aparatul de marcat, iar `core/uc_tenants.py` (`horeca_import_amef()`) generează automat o singură notă contabilă zilnică din acel raport Z (5311/5125 = 707, cu TVA colectată pe 4427), nu bon cu bon. Nota generată din AMEF intră direct ca înregistrare contabilă; ea nu trece prin `casa_operatiuni`/`registru_casa()` din `core/casa.py`, care rămâne motorul soldului rulant al casei doar pentru operațiunile introduse manual (încasare client, plată furnizor, ridicare/depunere bancă, avans). Rezultatul practic respectă totuși mecanismul din normă: raportul Z e documentul-sumă a zilei, nu chitanța bon cu bon.

[iConta.eu](/)
