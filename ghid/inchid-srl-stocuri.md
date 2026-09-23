---
title: Cum închid un SRL care mai are stocuri?
description: Cum se valorifică stocurile rămase la lichidarea unei societăți și de ce motorul de lichidare al iConta.eu nu are, deocamdată, o funcție dedicată pentru ele.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum închid un SRL care mai are stocuri?

Stocurile rămase în gestiune la data dizolvării — mărfuri, materii prime, produse finite — nu se pierd automat: lichidatorii au dreptul, ca la orice altă componentă a patrimoniului, să le valorifice pentru a stinge pasivul sau a le distribui prin partaj.

## Temeiul legal

::: ghid-temei
„lichidatorii pot [...] «să vândă, prin licitație publică, imobilele și orice avere mobiliară a societății» și «să lichideze și să încaseze creanțele societății»"
— L31/1990, art. 255 alin. (1) lit. c) și e) (citat în dosarul de cercetare F057)
:::

Formularea „orice avere mobiliară a societății" acoperă, în sens larg, și stocurile — nu doar mijloacele fixe sau imobilizările.

## Ce se greșește în practică

Se presupune adesea că orice vânzare de bun în perioada de lichidare trece prin ecranul dedicat „Lichidare / radiere firmă" din iConta.eu. Nu este cazul pentru stocuri: funcția de calcul din motorul de lichidare (`core/lichidare.py`, `nota_vanzare_activ`) este construită specific pentru **active imobilizate** — nota contabilă generată descarcă explicit un cont de imobilizare (implicit 2131 — mijloace fixe) și amortizarea cumulată aferentă (implicit 2813). Structura ei nu se potrivește cu ieșirea din gestiune a unui stoc (care nu are amortizare cumulată).

## Ce face iConta.eu

Dosarul de cercetare pentru F057 nu a găsit, în codul motorului de lichidare, o funcție separată pentru vânzarea stocurilor rămase la lichidare. Vânzarea acestora se înregistrează, cel mai probabil, ca o operațiune obișnuită de vânzare (factură de ieșire + descărcare de gestiune), prin ecranele normale de facturare și gestiune ale aplicației, nu prin operația specială de lichidare. TVA colectată la vânzare se tratează, în acest caz, ca la orice vânzare normală, nu prin câmpul de cotă TVA cerut explicit de funcția `nota_vanzare_activ` pentru activele imobilizate.

Dacă societatea în lichidare mai vinde active imobilizate (nu stocuri), consultați ghidul dedicat acestei situații, unde este descrisă exact monografia contabilă generată automat de aplicație.

[iConta.eu](/)
