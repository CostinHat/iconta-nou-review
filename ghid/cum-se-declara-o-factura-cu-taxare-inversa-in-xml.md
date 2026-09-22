---
title: Cum se declară o factură cu taxare inversă în XML?
description: Factura cu taxare inversă internă (art. 331) trebuie emisă fără taxă colectată înscrisă, dar cu mențiunea obligatorie "taxare inversă"; această informație de fond este cea care trebuie regăsită corect codificat în structura XML a facturii electronice.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se declară o factură cu taxare inversă în XML?

Indiferent de formatul facturii — pe hârtie sau electronic (XML) — regula de fond pentru o operațiune supusă taxării inverse interne (art. 331 Cod fiscal) e aceeași: furnizorul nu înscrie taxa colectată aferentă, dar are obligația să menționeze explicit "taxare inversă" pe factură. O factură electronică transpune corect această regulă doar dacă informația de fond (fără TVA colectat, cu mențiunea de taxare inversă) e reflectată corect în structura ei, indiferent de câmpul/codul tehnic folosit pentru asta.

## Temeiul legal

::: ghid-temei
**Norme, pct. 109 alin. (1):** Taxarea inversă prevăzută la art. 331 din Codul fiscal reprezintă o modalitate de simplificare a plății taxei. Prin aceasta nu se efectuează nicio plată de TVA între furnizorul/prestatorul și beneficiarul unor livrări/prestări [...] Această modalitate de simplificare a plății taxei se realizează prin emiterea de facturi în care furnizorul/prestatorul nu înscrie taxa aferentă, inclusiv pentru avansuri, aceasta fiind calculată de beneficiar și înregistrată atât ca taxă colectată, cât și ca taxă deductibilă în decontul de taxă prevăzut la art. 323 din Codul fiscal. Furnizorul/Prestatorul are obligația să înscrie pe factură mențiunea "taxare inversă".

**Articolul 331 alin. (3):** Pe facturile emise pentru livrările de bunuri/prestările de servicii prevăzute la alin. (2) furnizorii/prestatorii nu vor înscrie taxa colectată aferentă. Beneficiarii vor determina taxa aferentă, care se va evidenția în decontul prevăzut la art. 323, atât ca taxă colectată, cât și ca taxă deductibilă.
:::

## Ce trebuie să conțină factura, indiferent de format

Cerințele de fond, valabile și pentru factura electronică:

- fără sumă de TVA colectată înscrisă de furnizor pentru operațiunea în cauză;
- mențiunea explicită "taxare inversă" pe factură;
- baza de calcul (valoarea fără TVA) corectă, pentru ca beneficiarul să poată determina taxa aferentă (formula 4426 = 4427).

Codificarea tehnică exactă a acestor elemente în schema XML folosită pentru facturarea electronică (câmpul/codul de scutire sau de regim special de TVA folosit pentru marcarea taxării inverse) ține de standardul tehnic al facturii electronice, nu de Codul fiscal — pentru maparea corectă a codului tehnic, contabilul trebuie să consulte documentația tehnică a schemei XML folosite, plecând de la această regulă de fond.

## Ce se greșește în practică

- Se emite factura XML cu o sumă de TVA colectată calculată automat de sistemul de facturare, deși operațiunea e supusă taxării inverse — furnizorul nu trebuie să înscrie taxă colectată.
- Se omite mențiunea "taxare inversă" din corpul facturii (text liber sau echivalentul tehnic al acesteia), deși norma de aplicare o cere explicit.
- Se declară eronat regimul TVA pentru operațiuni cu temei diferit (de exemplu, achiziții din UE, supuse art. 307, nu art. 331), amestecând coduri tehnice care corespund unor regimuri fiscale diferite.
- Se emite factura cu TVA "din greșeală", iar apoi se corectează prin simpla anulare, în loc de factura de corecție prevăzută de lege pentru regimuri de taxare aplicate greșit.

## Ce face iConta.eu

Motorul de taxare inversă al iConta.eu determină dacă o operațiune se încadrează la una din cele 12 categorii ale art. 331 alin. (2), verifică statutul de plătitor TVA al ambelor părți, pragul valoric și termenul de expirare, apoi calculează suma de TVA pe care beneficiarul o înregistrează simultan ca taxă colectată și deductibilă. Este strict un motor de decizie și calcul, fără efecte secundare — nu emite el însuși structura XML a facturii electronice; rezultatul deciziei (eligibil/neeligibil și motivul, cu referire explicită la litera din art. 331 alin. (2)) e cel care stă la baza modului în care factura e generată și marcată ulterior.

[iConta.eu](/)
