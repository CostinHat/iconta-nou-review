---
title: Cum se raportează operațiunile cu taxare inversă în SAF-T?
description: Operațiunile cu taxare inversă internă (art. 331) se raportează prin declararea taxei simultan ca taxă colectată și deductibilă în decontul de TVA, pe baza facturii care poartă mențiunea obligatorie "taxare inversă" — inclusiv în structura de raportare SAF-T (D406).
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se raportează operațiunile cu taxare inversă în SAF-T?

O operațiune supusă taxării inverse interne (art. 331 Cod fiscal) nu presupune nicio plată de TVA între furnizor și beneficiar — furnizorul emite factura fără TVA, cu mențiunea obligatorie "taxare inversă", iar beneficiarul înregistrează taxa aferentă simultan ca taxă colectată și ca taxă deductibilă. Această înregistrare stă la baza raportării fiscale, inclusiv a celei prin fișierul standard de audit fiscal (SAF-T, declarația D406) — care preia, pentru fiecare document, tratamentul de TVA aplicat conform legii.

## Temeiul legal

::: ghid-temei
**Articolul 331 alin. (3):** Pe facturile emise pentru livrările de bunuri/prestările de servicii prevăzute la alin. (2) furnizorii/prestatorii nu vor înscrie taxa colectată aferentă. Beneficiarii vor determina taxa aferentă, care se va evidenția în decontul prevăzut la art. 323, atât ca taxă colectată, cât și ca taxă deductibilă. Beneficiarii au drept de deducere a taxei în limitele și în condițiile stabilite la art. 297-301.

**Norme, pct. 109 alin. (1):** Taxarea inversă prevăzută la art. 331 din Codul fiscal reprezintă o modalitate de simplificare a plății taxei. Prin aceasta nu se efectuează nicio plată de TVA între furnizorul/prestatorul și beneficiarul unor livrări/prestări [...] Furnizorul/Prestatorul are obligația să înscrie pe factură mențiunea "taxare inversă". [...] Din punct de vedere contabil, beneficiarul înregistrează în cursul perioadei fiscale în care taxa este exigibilă suma taxei aferente în următoarea formulă contabilă: 4426 = 4427.
:::

## Ce trebuie să conțină documentele pentru o raportare corectă

Punctul de plecare pentru orice raportare corectă — inclusiv în SAF-T — e factura emisă corect de furnizor: fără taxă colectată înscrisă, dar cu mențiunea "taxare inversă". Pe baza acestei facturi, beneficiarul înregistrează contabil formula 4426 = 4427 și declară taxa, atât ca taxă colectată, cât și ca taxă deductibilă, în decontul de TVA prevăzut la art. 323 — aceleași sume care alimentează ulterior structurile de raportare fiscală electronică, inclusiv fișierul D406.

Pentru mapările tehnice exacte ale operațiunilor cu taxare inversă în schema XML a SAF-T (coduri de nomenclator TVA, structuri specifice din OPANAF 1783/2021 și OPANAF 407/2025), contabilul trebuie să consulte documentația tehnică a schemei D406 — acest ghid tratează regimul de TVA aplicabil, care e temeiul pentru orice mapare tehnică ulterioară.

## Ce se greșește în practică

- Se omite mențiunea obligatorie "taxare inversă" pe factura emisă de furnizor, ceea ce poate duce, conform normelor de aplicare, la pierderea dreptului de deducere al beneficiarului dacă factura e emisă eronat cu TVA.
- Se raportează taxa doar ca deductibilă, fără componenta de taxă colectată (sau invers), rupând simetria 4426 = 4427 cerută de normele metodologice.
- Se confundă raportarea unei operațiuni cu taxare inversă internă (art. 331) cu cea a unei operațiuni cu autolichidare pentru achiziții din UE (art. 307) — regimul de TVA declarat trebuie să corespundă temeiului legal real al operațiunii.
- Se declară taxa în perioada facturii, nu în perioada exigibilității taxei — regula generală de exigibilitate (art. 280 alin. (7)) rămâne determinantă și pentru momentul raportării.

## Ce face iConta.eu

Motorul de taxare inversă al iConta.eu este strict un motor de decizie și calcul: verifică dacă o operațiune se încadrează la una din cele 12 categorii ale art. 331 alin. (2), statutul de plătitor TVA al ambelor părți, pragul valoric și termenul de expirare, apoi calculează suma de TVA pe care beneficiarul o înregistrează simultan ca taxă colectată și deductibilă (formula 4426 = 4427), pe baza cotei explicite a operațiunii. Modulul nu emite el însuși vreo structură XML sau SAF-T — rezultatul calculului stă la baza datelor raportate ulterior prin decontul de TVA și prin fișierele de raportare fiscală.

[iConta.eu](/)
