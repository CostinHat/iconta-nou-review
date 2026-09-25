---
title: "Confuzii frecvente între livrare intracomunitară și export"
description: "Diferența legală dintre o livrare intracomunitară de bunuri (către un stat membru UE) și un export (în afara Uniunii Europene), cu tratamentul TVA aferent fiecăreia."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Confuzii frecvente între livrare intracomunitară și export

Deși ambele operațiuni au un lucru în comun — bunurile părăsesc România — regimul lor de TVA se sprijină pe o distincție esențială: destinația. Dacă bunurile ajung într-un alt stat membru al Uniunii Europene, vorbim despre livrare intracomunitară; dacă ajung în afara Uniunii Europene, vorbim despre export. Documentele justificative, codurile de raportare și chiar riscurile de control diferă radical între cele două.

## Temeiul legal

::: ghid-temei
„(9) Livrarea intracomunitară reprezintă o livrare de bunuri, în înțelesul alin. (1), care sunt expediate sau transportate dintr-un stat membru în alt stat membru de către furnizor sau de persoana către care se efectuează livrarea ori de altă persoană în contul acestora."
— Legea nr. 227/2015 (Codul fiscal), art. 270 alin. (9) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„Sunt scutite de taxă: a) livrările de bunuri expediate sau transportate **în afara Uniunii Europene** de către furnizor sau de altă persoană în contul său; b) livrările de bunuri expediate sau transportate în afara Uniunii Europene de către cumpărătorul care nu este stabilit în România sau de altă persoană în contul său [...]"
— Legea nr. 227/2015 (Codul fiscal), art. 294 alin. (1) lit. a) și b) „Scutiri pentru exporturi sau alte operațiuni similare" (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Diferențele-cheie:

- **Destinația** e criteriul care separă cele două operațiuni: livrarea intracomunitară merge într-un alt stat membru UE, exportul merge într-un stat terț, în afara UE.
- Livrarea intracomunitară e reglementată la art. 270 (ca formă a livrării de bunuri) și beneficiază de scutire de TVA cu drept de deducere condiționată, printre altele, de validarea codului de TVA al cumpărătorului din alt stat membru și de dovada transportului.
- Exportul e scutit de TVA în baza art. 294, cu condiția dovedirii ieșirii efective a bunurilor din teritoriul UE — de regulă prin declarația vamală de export confirmată electronic (MRN).
- Documentele justificative diferă: pentru livrarea intracomunitară contează dovada transportului între state membre (CMR, confirmare de primire etc.) și codul valid de TVA al cumpărătorului; pentru export contează declarația vamală validată de autoritatea vamală.

## Ce se greșește în practică

- Se aplică scutirea de TVA specifică livrării intracomunitare (cu documente de transport intracomunitar) unei operațiuni care este, de fapt, export către un stat din afara UE — și invers.
- Se omite verificarea validității codului de TVA al cumpărătorului dintr-un alt stat membru (obligatorie pentru scutirea livrării intracomunitare), tratând orice livrare către un client UE ca automat scutită.
- Se consideră livrarea către Regatul Unit (post-Brexit) drept livrare intracomunitară, deși aceasta este, din punct de vedere al TVA, un export către un stat terț.

## Ce face iConta.eu

Pentru acest subiect nu am identificat, în modulele verificate (declarațiile D300, D301, D390), o funcție care să valideze automat coerența dintre tipul de operațiune declarat de contabil (livrare intracomunitară vs. export) și documentele/codul de TVA al partenerului — aplicația generează declarațiile pe baza operațiunilor introduse și clasificate de contabil, fără un mecanism separat de detectare a confuziei dintre cele două regimuri.

[iConta.eu](/)
