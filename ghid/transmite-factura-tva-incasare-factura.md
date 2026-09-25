---
title: "Cum se transmite o factură cu TVA la încasare în e-Factura?"
description: "Pașii de transmitere prin RO e-Factura a unei facturi emise de o firmă înscrisă la TVA la încasare, și mențiunea obligatorie pe care legea o cere pe factură."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se transmite o factură cu TVA la încasare în e-Factura?

O factură emisă de o firmă înscrisă în sistemul TVA la încasare se transmite prin RO e-Factura exact ca orice altă factură B2B — structura XML (UBL 2.1/CIUS-RO), încărcarea în sistemul național și urmărirea recipisei nu diferă tehnic după regimul de TVA al emitentului. Diferă însă conținutul obligatoriu al facturii: legea cere o mențiune specifică, pe care destinatarul trebuie să o poată citi direct pe document.

## Temeiul legal

::: ghid-temei
„Elementele facturii [...] p) în cazul în care exigibilitatea TVA intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, mențiunea «TVA la încasare»."
— Codul fiscal, art. 319 alin. (20) lit. p) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Mențiunea „TVA la încasare" e obligatorie pe orice factură emisă de o persoană impozabilă la care exigibilitatea taxei intervine la data încasării (art. 282 alin. 3) — nu e opțională și nu depinde de acordul cumpărătorului.
- Ea informează destinatarul că, dacă e plătitor de TVA, dreptul lui de deducere pentru achiziția respectivă e amânat până la plata facturii către furnizor (art. 297 alin. 2).
- Factura electronică transmisă prin RO e-Factura trebuie să respecte structura semantică din SR EN 16931-1 și regulile RO_CIUS (OUG 120/2021, art. 4 alin. 1) — inclusiv mențiunile obligatorii cerute de Codul fiscal, care fac parte din conținutul minim al facturii.

## Ce se greșește în practică

- Se presupune că "regimul de TVA al firmei" e o informație pe care sistemul RO e-Factura o cunoaște automat despre emitent și că nu mai trebuie scrisă pe factură — legea cere mențiunea explicit, indiferent de ce știe sau nu sistemul.
- Se pune mențiunea doar pe factura PDF trimisă pe e-mail, dar nu și pe factura electronică propriu-zisă (XML-ul UBL încărcat în SPV), care e exemplarul original din punct de vedere legal (OUG 120/2021, art. 4 alin. 6).
- Se confundă mențiunea „TVA la încasare" cu mențiunea „taxare inversă" — sunt reguli diferite, pentru situații diferite (art. 319 alin. 20 lit. m) vs. lit. p)), și codul lor de categorie TVA în UBL diferă.
- Se emite factura cu mențiunea corectă, dar destinatarul o ignoră la validare, deducând TVA imediat, deși dreptul lui de deducere e amânat până la plată.

## Ce face iConta.eu

iConta.eu are infrastructură funcțională de transmitere prin RO e-Factura (`core/efactura_send.py`, funcționalitatea F126): generează XML-ul UBL/CIUS-RO al facturii, îl validează pe schematronul oficial ANAF (standard FACT1), îl încarcă în SPV și urmărește recipisa. Generatorul construiește corect antetul, părțile, liniile și totalurile de TVA pe cote (categoriile UBL folosite azi sunt doar „S" — cotă standard — și „Z" — cotă zero).

Onest: la verificarea directă a codului generatorului (`genereaza_xml` din `efactura_send.py`), **acesta nu scrie nicăieri mențiunea legală „TVA la încasare"** — nu există niciun element `cbc:Note` sau echivalent în XML-ul produs, indiferent de regimul TVA al firmei emitente. Dacă firma e înscrisă la TVA la încasare, mențiunea obligatorie de la art. 319 alin. (20) lit. p) nu ajunge automat pe factura electronică transmisă — contabilul trebuie s-o adauge manual, printr-un alt canal (de exemplu pe descrierea unei linii sau printr-un câmp de observații al facturii, dacă există), până când generatorul o va include automat.

[iConta.eu](/)
