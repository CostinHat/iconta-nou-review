---
title: "Ce verifică ANAF la tranzacțiile intracomunitare?"
description: "Ce controlează ANAF la operațiunile intracomunitare — validitatea codului de TVA prin VIES, condițiile scutirii pentru livrări și corelarea D390 cu decontul de TVA și evidența contabilă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce verifică ANAF la tranzacțiile intracomunitare?

Controlul pe operațiuni intracomunitare pornește, de regulă, de la declarația recapitulativă (D390) — dar verificarea nu se oprește acolo. ANAF confruntă D390 cu decontul de TVA depus și cu evidența contabilă a firmei, iar la livrări, caută dovada celor două condiții obligatorii ale scutirii.

## Temeiul legal

::: ghid-temei
„Sunt, de asemenea, scutite de taxă următoarele: a) livrările intracomunitare de bunuri către o persoană impozabilă sau către o persoană juridică neimpozabilă care acționează ca atare în alt stat membru decât cel în care începe expedierea sau transportul bunurilor, care îi comunică furnizorului un cod valabil de înregistrare în scopuri de TVA, atribuit de autoritățile fiscale din alt stat membru [...]."
— Cod fiscal (Legea 227/2015), art. 294 alin. (2) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce verifică efectiv ANAF, pe fiecare palier:

- **Scutirea la livrarea intracomunitară** (LIC): condiționată de un cod de TVA valid al cumpărătorului, comunicat furnizorului, ȘI de dovada transportului bunurilor în alt stat membru (Cod fiscal art. 294 alin. (2) lit. a)) — lipsa oricăreia dintre cele două înseamnă că livrarea trebuie facturată cu TVA românesc.
- **Validitatea codului de TVA al partenerului**: verificată prin sistemul **VIES**, la nivel european — un cod invalid sau o eroare de comunicare la momentul facturării poate anula retroactiv scutirea.
- **Declarația recapitulativă D390**: se depune **numai pentru lunile în care ia naștere exigibilitatea taxei** pentru o operațiune intracomunitară — o declarație pe zero, deși firma are activitate intracomunitară în alte luni, atrage atenția ANAF (OPANAF 705/2020, pct. 1.2; Cod fiscal art. 325).
- **Corelarea D390 cu decontul de TVA (D300) și cu evidența contabilă**: ANAF (și, în prealabil, orice control intern serios) confruntă baza declarată în D390 cu rândurile intracomunitare din D300 depus și cu rulajele conturilor de TVA aferente (4426/4427) din contabilitate — o operațiune apărută în VIES fără corespondent în evidență sau în D300 e un semnal de neconformitate.
- **Achizițiile intracomunitare, taxarea inversă**: obligatul la plata taxei e beneficiarul (Cod fiscal art. 308-309), cu formula contabilă 4426=4427 (HG 1/2016, norme la art. 331, pct. 109 alin. (1)) — o achiziție intracomunitară fără taxare inversă înregistrată corect e altă neconcordanță tipică urmărită.
- **Pragul de 10.000 euro pentru achiziții intracomunitare** (Cod fiscal art. 268 alin. (5)-(6)): peste acest plafon anual, neplătitorii de TVA au obligația înregistrării speciale (art. 317) — depășirea plafonului fără înregistrare e un alt punct verificat.

## Ce se greșește în practică

- Se aplică scutirea de TVA la o livrare intracomunitară doar pe baza codului de TVA valid al clientului, fără să se păstreze și dovada transportului bunurilor — ambele condiții sunt cumulative, nu alternative.
- Se depune D390 „pe zero" pentru o lună în care firma a avut efectiv operațiuni intracomunitare, din simplă eroare de clasificare (de exemplu o achiziție introdusă manual fără codul de TVA sau țara furnizorului completate) — declarația recapitulativă nu se poate depune pe zero când există obligație de exigibilitate în lună.
- Se confundă Intrastat (obligație declarativă statistică, către INS, cu prag și temei propriu) cu D390 (declarație fiscală, către ANAF) — sunt obligații diferite, verificate de autorități diferite.
- Se tratează codul special de TVA de la art. 317 ca opțional, fără să se urmărească cumulul anual al achizițiilor intracomunitare de bunuri față de plafonul de 10.000 euro.

## Ce face iConta.eu

Funcționalitatea **Operațiuni intracomunitare** separă automat codul de TVA pe țară și cifre, verifică validitatea lui în VIES (la emiterea facturii, direct din ecran) și validează condițiile scutirii LIC (cod TVA valid + dovadă transport) înainte de a permite facturarea fără TVA. Pentru achiziții și servicii intracomunitare primite, calculează taxarea inversă (4426=4427) pe baza cotei declarate explicit de contabil, fără cotă implicită hardcodată.

Pe partea de control, aplicația are un modul dedicat de **control încrucișat** care confruntă bazele din D390 cu evidența contabilă validată și cu D300 efectiv depus, semnalând (verde/gri/roșu) operațiunile fără corespondent — exact tipul de verificare descris mai sus, făcută intern înainte ca ANAF s-o facă. Totuși, aplicația **nu urmărește automat** cumulul anual al achizițiilor intracomunitare față de plafonul de 10.000 euro (art. 317) — câmpul de înregistrare specială e un flag manual, nu un calcul de cumul; nu generează formularul 700 și nu interoghează SPV pentru obținerea codului special. De asemenea, nu există un generator dedicat de „dosar de audit" pentru operațiuni intracomunitare — pregătirea completă pentru un control (facturi, dovezi VIES cu dată, dovezi de transport) rămâne o compunere manuală, pe baza rezultatului controlului încrucișat din aplicație.

[iConta.eu](/)
