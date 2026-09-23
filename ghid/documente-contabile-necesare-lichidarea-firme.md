---
title: Ce documente contabile sunt necesare la lichidarea unei firme?
description: Ce documente cere legea la terminarea lichidării unei societăți — și ce anume generează, respectiv nu generează, iConta.eu din acestea.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce documente contabile sunt necesare la lichidarea unei firme?

Terminarea lichidării nu se încheie doar cu o decizie a asociaților — legea cere un set precis de documente, depuse la registrul comerțului, care să arate exact ce s-a întâmplat cu patrimoniul societății.

## Temeiul legal

::: ghid-temei
„În termen de 15 zile de la terminarea lichidării, lichidatorii vor depune la registrul comerțului cererea de radiere a societății [...], pe baza raportului final de lichidare și a situațiilor financiare de lichidare prin care se prezintă situația patrimoniului, a creanțelor și repartizarea activelor rămase, [...] inclusiv [...] dovada îndeplinirii obligației de calculare, reținere și plată a impozitului pe venit din lichidarea societății, prevăzută la art. 97 alin. (5) din [Codul fiscal] [...]."
— L31/1990, art. 260 alin. (6)
:::

Din acest text rezultă trei documente/dovezi obligatorii pentru cererea de radiere:

1. **raportul final de lichidare**;
2. **situațiile financiare de lichidare**, care prezintă situația patrimoniului, a creanțelor și repartizarea activelor rămase;
3. **dovada plății impozitului** pe venitul din lichidare (art. 97 alin. 5 din Codul fiscal).

Termenul legal general pentru terminarea lichidării este de maximum un an de la înregistrarea mențiunii de dizolvare, cu posibilitatea a maximum trei prelungiri de câte un an fiecare:

::: ghid-temei
„Lichidarea societății trebuie terminată în cel mult un an de la data înregistrării în registrul comerțului a mențiunii de dizolvare. [...] oficiul registrului comerțului poate prelungi acest termen de maximum trei ori, cu câte un an."
— L31/1990, art. 260 alin. (1)
:::

## Ce se greșește în practică

Se presupune uneori că un program de contabilitate „generează bilanțul de lichidare" ca document final, gata de depus. În realitate, așa cum reiese și din descrierea funcționalității F057 din iConta.eu, motorul de calcul este unul **pur**: produce notele contabile pentru fiecare etapă (vânzare de active, partaj), dar **nu generează el însuși un document/raport separat numit „bilanțul de lichidare"**. Situațiile financiare de lichidare rămân un document de întocmit distinct, pe baza înregistrărilor contabile rezultate din operațiuni.

## Ce face iConta.eu

Funcționalitatea „Lichidare/radiere societate" din iConta.eu acoperă motorul contabil al celor patru etape: valorificarea activelor, încasarea creanțelor și plata datoriilor, închiderea TVA și a impozitelor (cu rezultatul reflectat în contul 121), respectiv partajul final, pe baza bilanțului de lichidare. Notele contabile generate automat de aplicație (la vânzarea activelor și la partaj) sunt sufixate cu mențiunea „- OMFP 897/2015", pentru trasabilitate.

Ceea ce aplicația **nu** produce este documentul propriu-zis al raportului final de lichidare sau al situațiilor financiare de lichidare cerute de art. 260 alin. (6) — acestea se întocmesc separat, pe baza soldurilor rezultate din notele contabile generate în aplicație, și se depun manual la registrul comerțului, alături de dovada plății impozitului pe venitul din lichidare.

[iConta.eu](/)
