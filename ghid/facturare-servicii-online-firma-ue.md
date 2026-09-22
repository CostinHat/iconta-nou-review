---
title: Cum facturez servicii online către o firmă din UE
description: Serviciile online prestate unei firme dintr-un alt stat membru UE se facturează fără TVA românesc — locul prestării e la sediul clientului (art. 278 alin. (2) Cod fiscal) — cu condiția ca acesta să aibă un cod de TVA valabil.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum facturez servicii online către o firmă din UE?

Dacă firma ta prestează servicii online — dezvoltare software, mentenanță, servicii SaaS, consultanță la distanță — unei firme înregistrate în scop de TVA în alt stat membru, factura nu poartă TVA românesc. Locul prestării se mută la sediul clientului, iar operațiunea se raportează ca prestare intracomunitară de servicii, neimpozabilă în România. Confuzia apare când clientul nu are, de fapt, un cod de TVA valabil comunicat — atunci regula B2B nu se mai aplică automat.

## Temeiul legal

::: ghid-temei
**Art. 278 alin. (2) Cod fiscal** — locul prestării pentru servicii B2B: *„Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. Dacă serviciile sunt furnizate către un sediu fix al persoanei impozabile, aflat în alt loc decât cel în care persoana își are sediul activității sale economice, locul de prestare a serviciilor este locul unde se află respectivul sediu fix al persoanei care primește serviciile. În absența unui astfel de loc sau sediu fix, locul de prestare a serviciilor este locul unde persoana impozabilă care primește aceste servicii își are domiciliul stabil sau reședința obișnuită."*
:::

## Condiția pentru factura fără TVA

Ca să emiți factura fără TVA românesc, pe temeiul art. 278 alin. (2), trebuie îndeplinite două condiții:

1. **Clientul e stabilit în alt stat membru UE**, nu în România.
2. **Clientul îți comunică un cod de TVA valabil**, atribuit de autoritatea fiscală din statul lui.

Legea cere „cod valabil de înregistrare în scopuri de TVA" — o obligație de rezultat, nu o procedură anume. VIES (portalul UE prin care se verifică validitatea codurilor de TVA ale firmelor înregistrate în statele membre) e mijlocul administrativ uzual și recomandat de a proba acest lucru, nu o cerință distinctă scrisă literal în Codul fiscal. În practică, însă, verificarea prin VIES rămâne dovada standard pe care o cere orice control ulterior, așa că merită făcută și păstrată (captură, dată, rezultat) la fiecare factură emisă fără TVA.

Dacă la momentul facturării codul clientului **nu** e valid în VIES, operațiunea nu se mai poate trata ca prestare intracomunitară B2B cu locul la sediul clientului — se tratează după regulile aplicabile beneficiarilor neimpozabili, care pot cere aplicarea TVA românesc pe factură, în funcție de natura exactă a serviciului.

## Ce se greșește în practică

- **Se emite factura fără TVA fără să se verifice deloc codul de TVA al clientului**, pe încrederea că „e firmă din UE, deci scapă de TVA" — regula depinde strict de existența unui cod valabil comunicat, nu de simpla localizare a clientului.
- **Se confundă „VIES valid" cu o cerință legală de sine stătătoare**, ca și cum legea ar spune explicit „verifică pe VIES" — de fapt legea cere codul valabil, iar VIES e doar mijlocul uzual de verificare.
- **Se aplică regula B2B și pentru clienți persoane fizice sau firme fără cod de TVA valabil**, deși pentru aceștia locul prestării poate rămâne la sediul prestatorului, cu TVA românesc datorat.

## Ce face iConta.eu

Codul de TVA al clientului e analizat automat — prefixul de țară (cu mapare specială pentru Grecia, `GR → EL`) e verificat contra listei celor 27 de state membre UE plus `XI`; dacă prefixul lipsește sau nu e recunoscut, aplicația semnalează eroarea explicit. Operațiunea e tratată ca prestare intracomunitară neimpozabilă în România doar dacă țara clientului nu e România și codul e valid — validitatea fiind verificată prin interogarea directă a serviciului oficial VIES.

[iConta.eu](/)
