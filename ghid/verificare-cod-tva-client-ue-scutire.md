---
title: Cum verific codul de TVA al clientului UE pentru scutirea de livrare intracomunitară
description: Scutirea de TVA la livrarea intracomunitară (art. 294 alin. (2) lit. a) Cod fiscal) cere un cod de TVA valabil comunicat de client și dovada transportului bunurilor în alt stat membru (art. 270 alin. (9) Cod fiscal); VIES e mijlocul uzual de verificare a codului, nu o cerință scrisă distinct în lege.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum verific codul de TVA al clientului UE pentru scutire?

Ca să facturezi fără TVA o livrare de bunuri către o firmă din alt stat membru UE, nu e suficient ca marfa să plece efectiv spre acel stat — clientul trebuie să aibă un cod de TVA valabil, comunicat ție înainte de livrare. Verificarea acestui cod nu e un formalism opțional: dacă se dovedește ulterior că era invalid, scutirea poate cădea, iar TVA-ul rămâne în sarcina ta.

## Temeiul legal

::: ghid-temei
**Art. 294 alin. (2) lit. a) Cod fiscal** — condiția codului valabil: *„Sunt, de asemenea, scutite de taxă următoarele: a) livrările intracomunitare de bunuri către o persoană impozabilă sau către o persoană juridică neimpozabilă care acționează ca atare în alt stat membru decât cel în care începe expedierea sau transportul bunurilor, care îi comunică furnizorului un cod valabil de înregistrare în scopuri de TVA, atribuit de autoritățile fiscale din alt stat membru, cu excepția: 1. livrărilor intracomunitare efectuate de o întreprindere mică..."*

**Art. 270 alin. (9) Cod fiscal** — condiția de transport (definiția livrării intracomunitare): *„Livrarea intracomunitară reprezintă o livrare de bunuri, în înțelesul alin. (1), care sunt expediate sau transportate dintr-un stat membru în alt stat membru de către furnizor sau de persoana către care se efectuează livrarea ori de altă persoană în contul acestora."*

**Art. 294 alin. (2^1) Cod fiscal** — condiție suplimentară legată de declarația recapitulativă: *„Scutirea prevăzută la alin. (2) lit. a) nu se aplică în cazul în care furnizorul nu a respectat obligația prevăzută la art. 325 alin. (1) de a depune o declarație recapitulativă sau declarația recapitulativă depusă de acesta nu conține informațiile corecte referitoare la această livrare, astfel cum se solicită în temeiul art. 325 alin. (3), cu excepția cazului în care furnizorul poate justifica în mod corespunzător deficiența într-un mod considerat satisfăcător de autoritățile fiscale competente."*
:::

## Ce trebuie verificat, de fapt

Scutirea de la livrarea intracomunitară nu depinde de un singur lucru, ci de trei condiții cumulative:

1. **Clientul e stabilit în alt stat membru UE**, nu în România.
2. **Clientul are un cod de TVA valabil**, comunicat furnizorului — condiția scrisă explicit la art. 294 alin. (2) lit. a).
3. **Bunurile sunt efectiv expediate sau transportate** dintr-un stat membru în altul — condiție care nu vine din art. 294, ci din chiar definiția livrării intracomunitare, la art. 270 alin. (9). Fără transport dovedit, nu există livrare intracomunitară, deci scutirea de la art. 294 nici nu se pune în discuție.

**Cum se verifică „cod valabil"?** Legea cere rezultatul — un cod valabil comunicat de client — nu impune literal „verificare pe portalul VIES". VIES (sistemul UE de schimb de informații privind TVA, reglementat prin cooperarea administrativă între statele membre) e mijlocul administrativ uzual și recomandat de a proba validitatea codului la data livrării, nu o obligație distinctă scrisă în Codul fiscal. În practică rămâne, totuși, dovada standard cerută la un control: captură/confirmare VIES păstrată la dosarul operațiunii, cu data verificării.

**O condiție suplimentară, ușor de omis**: art. 294 alin. (2^1) leagă scutirea și de depunerea corectă a declarației recapitulative (D390) de către furnizor pentru livrarea respectivă. Chiar dacă și codul clientului e valabil, și transportul e dovedit, scutirea poate cădea retroactiv dacă D390 nu a fost depusă corect sau nu conține informațiile cerute pentru acea livrare — cu excepția cazului în care furnizorul justifică satisfăcător deficiența.

## Ce se greșește în practică

- **Se verifică doar dovada de transport, fără codul de TVA (sau invers).** Cele trei condiții sunt cumulative — lipsa oricăreia dintre ele înseamnă că scutirea nu se aplică, iar factura trebuie emisă cu TVA.
- **Se tratează „verificarea VIES" ca pe o cerință legală de sine stătătoare**, ca și cum art. 294 ar spune explicit „verifică pe VIES" — de fapt legea cere codul valabil; VIES e doar mijlocul uzual de verificare, nu un termen scris în Codul fiscal.
- **Se uită de condiția D390 din art. 294 alin. (2^1).** Codul valid și transportul dovedit nu sunt suficiente dacă declarația recapitulativă pentru livrarea respectivă nu a fost depusă corect — e o a patra verificare, separată, ușor de omis pentru că nu ține de factura în sine.

## Ce face iConta.eu

Codul de TVA al clientului e analizat automat — prefixul de țară (cu mapare specială pentru Grecia, `GR → EL`) e verificat contra listei celor 27 de state membre UE plus `XI`; dacă prefixul lipsește sau nu e recunoscut, aplicația semnalează explicit eroarea, distingând „cod lipsă" de „prefix necunoscut". Scutirea de livrare intracomunitară e validată pe baza a trei condiții verificate în ordine: țara clientului diferită de România, cod valabil confirmat prin interogarea serviciului oficial VIES, și dovada transportului bunurilor — toate trei cumulative, altfel operațiunea se facturează cu TVA. Verificarea depunerii corecte a declarației recapitulative pentru livrarea respectivă (condiția de la art. 294 alin. (2^1)) nu face parte din această validare.

[iConta.eu](/)
