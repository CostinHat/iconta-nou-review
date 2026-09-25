---
title: "Poate un PFA la normă de venit să deducă amortizarea?"
description: "De ce un PFA impozitat pe bază de normă de venit nu poate deduce amortizarea mijloacelor fixe, conform art. 69 din Codul fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Poate un PFA la normă de venit să deducă amortizarea?

Un PFA care plătește impozit pe baza normei anuale de venit, nu în sistem real, se întreabă frecvent dacă poate scădea din venitul impozabil amortizarea unui utilaj, a unei mașini sau a unui echipament folosit în activitate. Răspunsul ține de însăși natura acestui regim de impozitare.

## Temeiul legal

::: ghid-temei
„(8) Contribuabilii care desfășoară activități pentru care venitul net se determină pe bază de norme de venit au obligația să completeze numai partea referitoare la venituri din Registrul de evidență fiscală și nu au obligații privind evidența contabilă."
— Codul fiscal (Legea 227/2015), art. 69 alin. (8) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Consecința e directă:

- La normă de venit, **venitul net anual e o sumă fixă**, stabilită de administrația fiscală pe activitate și zonă (art. 69 alin. (1)-(4)), independentă de cheltuielile reale ale PFA-ului. Nu există un calcul „venituri minus cheltuieli" în care amortizarea să intre ca linie de cheltuială.
- Legea spune expres că acest contribuabil **nu are obligații privind evidența contabilă** — deci nici obligația, nici posibilitatea de a conduce un registru de mijloace fixe și de a calcula amortizare fiscal deductibilă, pentru că nu există niciun venit net „în sistem real" din care să se deducă ceva.
- Singura cale prin care amortizarea ar deveni relevantă e **opțiunea pentru sistemul real**, prevăzută la art. 69^1: PFA-ul poate opta să determine venitul net în sistem real, pe baza datelor din contabilitate, potrivit art. 68 — opțiune obligatorie apoi pentru minimum 2 ani fiscali consecutivi.

## Ce se greșește în practică

- Se completează un registru de mijloace fixe și se scade "amortizarea" din venitul brut al unui PFA la normă de venit, deși legea nu prevede niciun mecanism de deducere pentru acest regim.
- Se confundă norma de venit cu un regim forfetar de cheltuieli (gen cotă forfetară de 40%) — la normă de venit nu există nicio cheltuială dedusă, fixă sau reală; venitul net e chiar norma, ajustată eventual cu coeficienți de corecție (art. 69 alin. (10)).
- Se ignoră pragul de 25.000 euro venit brut anual (art. 69 alin. (9)): peste el, trecerea la sistemul real devine obligatorie din anul următor, moment din care amortizarea devine, în sfârșit, relevantă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un Registru de evidență fiscală dedicat persoanelor fizice (`core/registru_evidenta_fiscala.py`, temei art. 68 alin. (8)-(9) din Codul fiscal și OMFP 3254/2017), cu un mod distinct pentru „normă de venit": la acest mod, aplicația **refuză** înscrierea oricărei cheltuieli deductibile în registru — inclusiv, deci, orice amortizare —, exact regula de la art. 69 alin. (8). Pentru amortizarea propriu-zisă a mijloacelor fixe (utilă unui PFA în sistem real sau unei firme cu contabilitate în partidă dublă), aplicația oferă motorul general din `core/repo_mijloace_fixe.py`, dar acesta nu e legat de modul „normă de venit" al registrului — pentru un PFA la normă de venit, care prin lege nu are obligații de evidență contabilă, aplicarea unui calcul de amortizare nu are corespondent legal, indiferent de instrumentul folosit.

[iConta.eu](/)
