---
title: D205 pentru dividende către o persoană juridică străină
description: D205 nu se aplică dividendelor plătite unei persoane juridice străine — declarația e construită exclusiv pentru beneficiari persoane fizice rezidente, identificate prin CNP.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# D205 pentru dividende către o persoană juridică străină

Răspuns scurt: dividendele plătite unei persoane juridice străine nu se raportează prin D205. Declarația 205 este construită, ca formular, exclusiv pentru beneficiari persoane fizice — și, în plus, exclusiv pentru cei rezidenți. O persoană juridică (română sau străină) nu poate fi, prin definiție, beneficiar pe D205.

## Temeiul legal

::: ghid-temei
"(1) O persoană juridică română care plătește dividende către o persoană juridică română are obligația să rețină, să declare și să plătească impozitul pe dividende reținut [...] (2) Impozitul pe dividende se stabilește prin aplicarea unei cote de impozit de 16% asupra dividendului brut plătit unei persoane juridice române."
— Codul fiscal, Legea 227/2015, art. 43 alin. (1)-(2)
:::

Acest text arată granița exactă a regimului pentru dividende plătite unor persoane juridice: art. 43 din Codul fiscal vizează explicit doar plățile **de la o persoană juridică română către o persoană juridică română**, și se raportează prin D100 (poziția 150 din nomenclatorul de obligații), nu prin D205. O persoană juridică străină nu se încadrează în acest text (nu e "persoană juridică română" beneficiară) și, evident, nu are nici CNP, condiție structurală pentru D205. Cercetarea legală care stă la baza acestui ghid nu a identificat, pentru dividende plătite persoanelor juridice străine, un temei sau o procedură specifică documentate pentru funcționalitatea D205 din iConta — subiectul (reținere conform convențiilor de evitare a dublei impuneri, eventuală declarație D207 pentru nerezidenți) depășește această funcționalitate și nu tratăm aici detalii pe care nu le putem susține cu o sursă verificată.

## Ce se greșește în practică

- Se încearcă introducerea unei persoane juridice (română sau străină) ca beneficiar pe D205 — formularul nu are structural acest caz; câmpul de rezidență (`Rezid`) e obligatoriu "1" (rezident, persoană fizică) pentru dividende, iar identificarea beneficiarului se face pe CNP, nu pe CUI.
- Se presupune că D205 acoperă, ca declarație "de dividende" în general, orice tip de beneficiar — de fapt e specifică persoanelor fizice rezidente; persoanele juridice române beneficiare intră pe D100 (poz. 150, art. 43), iar persoanele juridice străine ies complet din acest circuit de declarare.

## Ce face iConta.eu

Generatorul D205 din iConta.eu validează fiecare beneficiar pe cifra de control a CNP-ului; un beneficiar fără CNP românesc valid — situație în care se încadrează, structural, orice persoană juridică, română sau străină — este respins la generare, nu apare în declarație. Aplicația nu construiește, pentru F029, nicio declarație alternativă pentru dividende plătite persoanelor juridice străine; dacă vă aflați în acest caz, verificați separat, cu un consultant fiscal, regimul aplicabil (inclusiv o eventuală convenție de evitare a dublei impuneri) — nu e acoperit de această funcționalitate.

[iConta.eu](/)
