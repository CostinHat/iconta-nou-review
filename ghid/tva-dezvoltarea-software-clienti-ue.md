---
title: "TVA pentru dezvoltarea de software pentru clienți din UE"
description: "Regula TVA aplicabilă serviciilor de dezvoltare software pentru clienți persoane impozabile din alte state membre UE."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# TVA pentru dezvoltarea de software pentru clienți din UE

Dezvoltarea de software (custom, la comandă, sau contract de mentenanță/suport) pentru un client dintr-un alt stat membru UE este, din perspectiva TVA, o prestare de servicii B2B intracomunitară — nu o categorie separată cu reguli proprii.

## Temeiul legal

::: ghid-temei
CF art. 278 alin. (2): „Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L17303-17420)
:::

Regula: locul prestării serviciului e considerat, legal, locul unde e stabilit beneficiarul (clientul), nu locul unde lucrează efectiv dezvoltatorii. Dacă clientul e o firmă cu cod de TVA valid, verificat în VIES, într-un alt stat membru, factura se emite **fără TVA românesc** — serviciul e neimpozabil în România, impozitarea revenind statului beneficiarului.

Dacă clientul nu are cod de TVA valid în VIES (persoană fizică, sau firmă neînregistrată încă), operațiunea devine B2C și se facturează **cu TVA românesc**.

## Ce se greșește în practică

- Se tratează dezvoltarea de software ca având un regim TVA „special”, diferit de alte servicii B2B — nu există o asemenea excepție în textul citat; regula e cea generală, art. 278 alin. (2).
- Se emite factura fără TVA fără verificare VIES efectivă a codului de TVA al clientului, la data fiecărei facturi (nu doar la prima).
- Se omite obligația de declarare D390 (cod P) pentru serviciile prestate, chiar dacă factura e emisă corect, fără TVA.

## Ce face iConta.eu

Formularul de vânzare intracomunitară (`vanzare_ic`) permite înregistrarea prestării de servicii către un client din UE, cu câmp pentru codul de TVA al acestuia. La emitere, aplicația verifică automat, live, în VIES statutul codului și afișează rezultatul (valid/invalid) direct în ecran; dacă VIES e indisponibil temporar, afișează avertisment explicit.

Validarea neimpozabilității se face pe baza a două condiții — client non-RO + cod valid VIES — iar operațiunea validă se clasifică automat spre D390, cod P.

[iConta.eu](/)
