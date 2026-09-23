---
title: De ce apare eroare de cod TVA în D390?
description: Codul de TVA al partenerului se verifică live prin VIES pentru majoritatea statelor UE, plus verificare offline a cifrei de control doar pentru Germania, Croația și Franța — un cod invalid apare ca avertisment, nu ca blocaj.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# De ce apare eroare de cod TVA în D390?

Eroarea poate avea mai multe cauze, în funcție de cum e verificat codul de TVA al partenerului în aplicație.

## Temeiul legal

::: ghid-temei
"Sunt, de asemenea, scutite de taxă următoarele: a) livrările intracomunitare de bunuri către o persoană impozabilă... care îi comunică furnizorului un cod valabil de înregistrare în scopuri de TVA, atribuit de autoritățile fiscale din alt stat membru…" — Codul fiscal, Legea nr. 227/2015, art. 294 alin. (2) lit. a)
:::

Cauzele cele mai frecvente pentru o eroare/avertisment de cod TVA:

- **codul e efectiv invalid în VIES** la momentul verificării — poate fi vorba de un cod expirat, suspendat sau introdus greșit;
- **codul are un prefix de țară scris greșit** — de exemplu Croația se codifică HR, nu CR (o eroare de mapare confirmată separat, ca regresie corectată);
- **serviciul VIES e temporar indisponibil** — verificarea live nu poate confirma sau infirma validitatea, iar aplicația nu poate concluziona automat;
- pentru majoritatea statelor UE, validarea cifrei de control se face **exclusiv online, prin VIES** — codul rămâne "neverificat" local dacă interogarea nu poate fi făcută; doar pentru Germania, Croația și Franța există și un algoritm de verificare offline suplimentar.

## Ce se greșește în practică

- Se presupune că orice avertisment de cod TVA blochează automat operațiunea — de regulă e doar un avertisment, operațiunea rămâne emisă, ca să nu dispară tăcut din declarație.
- Se ignoră avertismentul, presupunând că "așa arată mereu" — de fapt poate semnala un cod real invalid, cu impact asupra scutirii aplicate.
- Se scrie codul de țară al Croației ca CR, în loc de HR, cel corect conform validatorului ANAF.

## Ce face iConta.eu

Verificarea principală se face prin interogarea live a serviciului oficial VIES, pentru orice stat membru; pentru Germania, Croația și Franța, aplicația mai rulează și o verificare offline a cifrei de control. Un cod marcat invalid generează un avertisment vizibil, dar nu blochează introducerea operațiunii — decizia deliberată e ca operațiunea să rămână emisă, ca redactorul declarației să corecteze codul, nu ca acesta să dispară din declarație fără urmă.

[iConta.eu](/)
