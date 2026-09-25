---
title: "Noutăți fiscale 2026 pe industrii: HoReCa, construcții, IT, e-commerce"
description: "Schimbările din OUG 8/2026 care ating pragurile de bază — plafonul micro, valoarea mijlocului fix, plafonul de TVA — și cum se răsfrâng pe fiecare tip de activitate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Noutăți fiscale 2026 pe industrii: HoReCa, construcții, IT, e-commerce

Modificările fiscale importante ale anului 2026 nu sunt, în cea mai mare parte, reguli specifice unei industrii — sunt praguri și cote generale, ajustate prin OUG 8/2026, care ajung diferit la firme în funcție de mărimea și profilul lor de venituri. HoReCa, construcțiile, IT-ul și comerțul online resimt aceleași reguli generale, dar cu greutăți diferite.

## Temeiul legal

::: ghid-temei
„o microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent: [...] c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro."
— Legea 227/2015 (Codul fiscal), art. 47 alin. (1) lit. c), modificat de OUG 8/2026 art. 6 pct. 15 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

Trei praguri generale schimbate de OUG 8/2026, cu impact diferit pe industrii:

- **Plafonul de venituri pentru microîntreprindere a coborât la 100.000 euro** (art. 47 alin. 1 lit. c) — o firmă IT sau de e-commerce cu creștere rapidă îl poate depăși mult mai repede decât una din construcții, unde ciclul de facturare e mai lent.
- **Pragul de la care un activ devine mijloc fix amortizabil** a fost modificat de la art. 28 alin. (2) lit. b) prin OUG 8/2026 art. 6 pct. 7 — relevant mai ales pentru construcții și industrii cu echipamente scumpe, unde pragul schimbă direct ce se amortizează și ce se trece pe cheltuială integrală.
- **Plafonul de scutire de TVA pentru întreprinderile mici a urcat la 395.000 lei** de la 1 septembrie 2025 (art. 310 alin. 1-2, modificat prin OG 22/2025), aplicabil oricărei industrii, inclusiv comerțului online cu volum mare de tranzacții mici.

Fiecare industrie resimte aceste praguri diferit doar prin structura veniturilor ei, nu prin reguli separate: HoReCa are cicluri lunare rapide și atinge plafonul micro devreme în sezon; construcțiile au facturări mari, rare, care pot depăși dintr-o singură factură plafonul de TVA; IT-ul și e-commerce-ul cresc adesea cel mai rapid procentual, deci ating primele plafonul micro de 100.000 euro.

## Ce se greșește în practică

- Se caută „legea specifică HoReCa" sau „legea specifică IT" pentru praguri care sunt, de fapt, generale în Codul fiscal — și se ratează modificarea reală, aplicabilă tuturor.
- Se aplică vechiul plafon de TVA (300.000 lei) după 1 septembrie 2025, când plafonul valabil e deja 395.000 lei (art. 310 alin. 1).
- Se presupune că pragul mijlocului fix amortizabil e neschimbat de ani buni, fără verificarea modificării aduse de OUG 8/2026.

## Ce face iConta.eu

iConta.eu oferă evidența contabilă generală (facturi, jurnale, declarații D100/D101/D300/D390 etc.) și nu are module separate pe industrie (HoReCa, construcții, IT, e-commerce) — cu excepția motorului dedicat de bacșiș pentru restaurante și baruri (`core/bacsis.py`, vezi ghidul „Ce verifică ANAF la un restaurant?"). Cota de impozit micro (1%) e urmărită în cod cu temei citat explicit (art. 51 alin. 1), dar aplicația nu calculează automat, pe baza veniturilor cumulate, momentul în care o firmă depășește plafonul de 100.000 euro și trece la impozit pe profit în cursul anului — regimul fiscal se stabilește manual, în profilul firmei.

[iConta.eu](/)
