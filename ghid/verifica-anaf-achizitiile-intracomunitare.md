---
title: "Ce verifică ANAF la achizițiile intracomunitare?"
description: "Cum se confruntă declarația recapitulativă 390 cu decontul de TVA și cu evidența contabilă la o achiziție intracomunitară, și ce arată un rezultat neconcordant la VIES."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce verifică ANAF la achizițiile intracomunitare?

O achiziție intracomunitară de bunuri sau servicii lasă urme în trei locuri diferite — decontul de TVA, declarația recapitulativă 390 și registrul VIES al partenerului — iar controlul ANAF constă, în esență, în confruntarea acestor urme între ele.

## Temeiul legal

::: ghid-temei
„(1) Orice persoană impozabilă înregistrată în scopuri de TVA conform art. 316 sau 317 trebuie să întocmească și să depună la organele fiscale competente o declarație recapitulativă în care menționează: [...] d) achizițiile intracomunitare de bunuri taxabile, pentru care exigibilitatea de taxă a luat naștere în luna calendaristică respectivă; [...] e) achizițiile de servicii prevăzute la art. 278 alin. (2), efectuate de persoane impozabile din România care au obligația plății taxei conform art. 307 alin. (2), pentru care exigibilitatea de taxă a luat naștere în luna calendaristică respectivă, de la persoane impozabile nestabilite în România, dar stabilite în Uniunea Europeană."
— Codul fiscal, art. 325 alin. (1) lit. d) și e) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Trei confruntări concrete, pe care se bazează controlul:

- **D300 vs. evidența contabilă** — rândul de TVA colectată din decont (R17_2) se confruntă cu rulajul creditor al contului 4427 pe lună; rândul de TVA deductibilă (R27_2), cu rulajul debitor al contului 4426. La o achiziție intracomunitară, ambele mișcă simultan, prin taxare inversă (4426 = 4427).
- **D390 vs. evidența validată** — bazele din declarația recapitulativă (facturile intracomunitare, identificate automat sau clasificate manual) se confruntă cu operațiunile deja validate în contabilitate.
- **D390 vs. D300** — rândurile intracomunitare din decontul de TVA efectiv depus se confruntă cu ce a fost declarat pe D390 pentru aceeași lună.

Rezultatul acestor confruntări se citește pe un semafor cu trei culori, nu ca un blocaj automat: **roșu** înseamnă o operațiune declarată la VIES fără acoperire în evidență sau în D300; **gri** înseamnă o diferență care trebuie investigată (poate fi un decalaj legitim de exigibilitate — data facturii furnizorului nu coincide întotdeauna cu luna în care taxa devine exigibilă, cf. art. 284); **verde** înseamnă coincidență.

## Ce se greșește în practică

- Se presupune că orice diferență D390/D300 e automat o eroare — de multe ori e doar un decalaj de exigibilitate (faptul generator la AIC survine ca la o livrare similară în statul membru al achiziției, dar exigibilitatea e legată de data facturii furnizorului sau, cel târziu, de a 15-a zi a lunii următoare — art. 284 alin. (1)-(2)).
- Se confundă declarația recapitulativă 390 (bunuri/servicii intracomunitare) cu declarația 394 (operațiuni interne pe teritoriul României) — achizițiile intracomunitare sunt excluse explicit din D394, tocmai pentru că se declară deja în D390.
- Se ignoră verificarea VIES a codului de TVA al partenerului la momentul operațiunii, deși o eventuală neconcordanță ulterioară (cod invalid la data facturii) devine exact tipul de constatare „roșie" pe care controlul o caută.
- Se confundă pragul Intrastat (obligație declarativă statistică față de INS, cu prag și temei propriu) cu obligația de TVA/D390 — sunt raportări separate, către autorități diferite.

## Ce face iConta.eu

iConta rulează exact aceste trei confruntări automat, pe fiecare firmă: D300 vs. evidența 4426/4427, D390 vs. evidența validată și D390 vs. D300 efectiv depus, afișând rezultatul pe semaforul verde/gri/roșu descris mai sus, nu ca un blocaj rigid la depunere. De reținut, punctual: verificarea live în VIES există în aplicație, dar nu e legată de „emiterea unei facturi" în general, ci de ecranul dedicat „Livrare/prestare intracomunitară" (vânzare-ic) — acolo, codul de TVA al clientului e interogat live în VIES înainte de a accepta scutirea, cu eroare explicită dacă serviciul e indisponibil. La achiziția intracomunitară (achiziție-ic), aplicația doar deduce automat țara furnizorului din prefixul codului de TVA introdus — nu face o interogare live în VIES a codului furnizorului.

O limită de spus onest: D390 **nu se poate depune pe zero** — dacă luna nu are nicio operațiune intracomunitară, generarea e blocată, conform regulii că declarația recapitulativă se depune numai pentru lunile în care ia naștere exigibilitatea taxei. Iar dacă D301 arată achiziții intracomunitare într-o lună, dar D390 iese pe zero, aplicația semnalează explicit discrepanța, pentru că lipsește o informație obligatorie (de regulă țara furnizorului). În fine, iConta nu ține un cumul automat al pragului de 10.000 euro de achiziții intracomunitare (art. 268 alin. (4) lit. b), coroborat cu alin. (5)) care declanșează obligația de înregistrare specială art. 317 — acel flag (`inreg_art317`, boolean pe profilul firmei) rămâne o bifă manuală, nu un calcul urmărit automat de aplicație.

[iConta.eu](/)
