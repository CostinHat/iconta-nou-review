---
title: "Cum tratez TVA când factura vine dintr-un stat UE, dar marfa vine din alt stat?"
description: "Statul de pe factura furnizorului nu e neapărat statul din care pleacă marfa — locul livrării, deci tratamentul TVA, se stabilește după unde încep transportul bunurilor, nu după adresa furnizorului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez TVA când factura vine dintr-un stat UE, dar marfa vine din alt stat?

Firma românească primește o factură de la un furnizor înregistrat, de exemplu, în Olanda, dar marfa e expediată efectiv dintr-un depozit din Polonia. Situația e frecventă la furnizorii mari, cu depozite distribuite în mai multe state membre — iar tratamentul de TVA se stabilește după locul real de plecare a bunurilor, nu după sediul sau codul de TVA afișat pe factură.

## Temeiul legal

::: ghid-temei
„Se consideră a fi locul livrării de bunuri: a) locul unde se găsesc bunurile în momentul când începe expedierea sau transportul, în cazul bunurilor care sunt expediate sau transportate de furnizor, de cumpărător sau de un terț."
— Codul fiscal (Legea 227/2015), art. 275 alin. (1) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Locul livrării — și, prin urmare, statul membru din care e considerată achiziția intracomunitară a firmei românești — se leagă de mișcarea fizică reală a bunurilor, nu de identitatea juridică a furnizorului:

- Dacă marfa pleacă din **Polonia**, achiziția intracomunitară a firmei românești are loc, potrivit art. 276, în România (statul unde se încheie transportul) — dar furnizorul trebuie să factureze folosind codul lui de TVA valabil pentru operațiuni realizate din Polonia, care poate diferi de codul principal, olandez.
- Furnizorii cu depozite în mai multe state membre sunt, de regulă, **înregistrați în scopuri de TVA separat în fiecare stat** din care expediază efectiv marfă — factura corectă trebuie să poarte codul de TVA corespunzător statului de plecare real, nu al sediului principal.
- Pentru firma română, ceea ce contează la înregistrarea achiziției nu e „țara furnizorului" de pe factură, ci **din ce stat a plecat efectiv marfa** — informație de regulă vizibilă din documentul de transport.

## Ce se greșește în practică

- Se presupune că statul furnizorului (cel din antetul facturii) e și statul din care a plecat marfa, fără să se verifice documentul de transport.
- Se acceptă o factură cu codul de TVA „principal" al furnizorului, deși pentru livrarea din alt stat membru ar fi trebuit folosit codul de TVA local, valabil pentru operațiunile din acel stat.
- Se raportează achiziția intracomunitară cu un partener/țară greșite în declarația recapitulativă, ceea ce produce discrepanțe la reconcilierea automată VIES dintre state.

## Ce face iConta.eu

La introducerea unei facturi de achiziție intracomunitară, iConta.eu verifică prin **VIES** (serviciul oficial al Comisiei Europene) validitatea codului de TVA introdus pentru partener — dar nu determină singură dacă acel cod corespunde statului real din care a plecat marfa; asta rămâne de verificat de contabil, pe baza documentului de transport, înainte de a clasifica operațiunea pentru D390.

[iConta.eu](/)
