---
title: Cum închid un SRL care mai are stocuri?
description: Cum se valorifică stocurile rămase la lichidarea unei societăți și de ce motorul de lichidare al iConta.eu nu are, deocamdată, o funcție dedicată pentru ele.
published: 2026-09-24
modified: 2026-10-13
poarta: v1
---

# Cum închid un SRL care mai are stocuri?

Stocurile rămase în gestiune la data dizolvării — mărfuri, materii prime, produse finite — nu se pierd automat: lichidatorii au dreptul, ca la orice altă componentă a patrimoniului, să le valorifice pentru a stinge pasivul sau a le distribui prin partaj.

Formularea „orice avere mobiliară a societății" acoperă, în sens larg, și stocurile — nu doar mijloacele fixe sau imobilizările.

## Temeiul legal

::: ghid-temei
„În afară de puterile conferite de asociați, cu aceeași majoritate cerută pentru numirea lor, lichidatorii vor putea: [...] c) să vândă, prin licitație publică, imobilele și orice avere mobiliară a societății;”
— Legea nr. 31/1990 privind societățile, art. 255 alin. (1) lit. c) (sursă: [Legea nr. 31/1990 privind societățile](https://legislatie.just.ro/Public/DetaliiDocument/798))
:::

## Ce se greșește în practică

Se presupune adesea că orice vânzare de bun în perioada de lichidare trece prin ecranul dedicat „Lichidare / radiere firmă" din iConta.eu. Nu este cazul pentru stocuri: funcția de calcul din motorul de lichidare („nota de vânzare a activului”) este construită specific pentru **active imobilizate** — nota contabilă generată descarcă explicit un cont de imobilizare (implicit 2131 — mijloace fixe) și amortizarea cumulată aferentă (implicit 2813). Structura ei nu se potrivește cu ieșirea din gestiune a unui stoc (care nu are amortizare cumulată).

## Ce face iConta.eu

Ecranul „Lichidare / radiere firmă” nu are o operație separată pentru vânzarea stocurilor rămase la lichidare. Vânzarea acestora se înregistrează, cel mai probabil, ca o operațiune obișnuită de vânzare (factură de ieșire + descărcare de gestiune), prin ecranele normale de facturare și gestiune ale aplicației, nu prin operația specială de lichidare. TVA colectată la vânzare se tratează, în acest caz, ca la orice vânzare normală, nu prin câmpul de cotă TVA cerut explicit de funcția „nota de vânzare a activului” pentru activele imobilizate.

Dacă societatea în lichidare mai vinde active imobilizate (nu stocuri), consultați ghidul dedicat acestei situații, unde este descrisă exact monografia contabilă generată automat de aplicație.

[iConta.eu](/)
