---
title: "Amortizarea și taxa pe activele speciale: legătură"
description: "Impozitul pe construcții (Titlul X din Codul fiscal) se calculează pe valoarea netă a construcțiilor speciale — adică exact pe valoarea rămasă după amortizare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Amortizarea și taxa pe activele speciale: legătură

Nu există, ca termen legal distinct, o „taxă pe activele speciale" — dar există un impozit real, încă în vigoare în 2026, calculat direct pe baza valorii nete rămase după amortizare a unei categorii specifice de mijloace fixe: construcțiile speciale. Redirecționăm ghidul spre acest temei real, care este cel mai apropiat de întrebare.

## Temeiul legal

::: ghid-temei
„Impozitul pe construcții anual se calculează astfel: a) prin aplicarea unei cote de 0,5% asupra valorii nete a construcțiilor, altele decât cele prevăzute la lit. b), pentru care nu se datorează impozit pe clădiri/taxa pe clădiri potrivit prevederilor titlului IX, existente în patrimoniul contribuabililor la data de 31 decembrie a anului anterior [...]."
— Legea nr. 227/2015 (Codul fiscal), art. 498 alin. (1) lit. a), coroborat cu art. 497 („construcțiile sunt cele prevăzute în grupa 1 din Catalogul privind clasificarea și duratele normale de funcționare a mijloacelor fixe") (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Legătura directă cu amortizarea:

- Baza de calcul a impozitului este **valoarea netă** a construcțiilor — adică valoarea de intrare minus amortizarea cumulată înregistrată contabil. Cu cât o construcție e mai amortizată, cu atât valoarea netă (și implicit impozitul de 0,5%) e mai mică.
- Categoria de active vizată e definită prin trimitere directă la **Grupa 1 - Construcții** din Catalogul mijloacelor fixe (HG 2139/2004) — același catalog folosit pentru stabilirea duratelor normale de amortizare.
- Sunt vizate construcțiile speciale (rețele, platforme industriale, structuri tehnice) care nu intră sub incidența impozitului pe clădiri de la Titlul IX — pentru clădirile „obișnuite" se aplică regimul de impozit pe clădiri, nu acest impozit pe construcții.
- Important: potrivit unei ordonanțe de urgență recente, Titlul X - Impozitul pe construcții **se abrogă începând cu anul 2027**, deci obligația rămâne aplicabilă pentru anul fiscal 2026, dar are un termen clar de expirare.

## Ce se greșește în practică

- Se caută în lege o „taxă pe activele speciale" ca instituție separată, deși ceea ce leagă efectiv amortizarea de o obligație fiscală distinctă este impozitul pe construcții de la Titlul X, calculat pe valoarea netă contabilă.
- Se omite complet acest impozit din calculul anual, pentru că firma nu are „clădiri" în sensul comun, deși poate deține construcții speciale (platforme, rezervoare, rețele) încadrate în Grupa 1 a catalogului.
- Se calculează impozitul pe valoarea de intrare (brută) a construcției, nu pe valoarea netă rămasă după amortizarea cumulată, ceea ce duce la o sumă declarată eronat, de regulă mai mare decât cea reală.

## Ce face iConta.eu

iConta.eu ține evidența mijloacelor fixe și calculează amortizarea lunară pe baza duratei normale de funcționare alese la fiecare activ, inclusiv pentru generarea secțiunii de active din SAF-T (D406). Calculul distinct al impozitului pe construcții de la Titlul X (0,5% pe valoarea netă a construcțiilor speciale) **nu este automatizat** ca declarație separată în aplicație la data acestui ghid — utilizatorul poate extrage din evidența mijloacelor fixe valorile nete necesare, dar încadrarea activelor în Grupa 1 a catalogului și depunerea declarației aferente rămân manuale.

[iConta.eu](/)
