---
title: "Cum se tratează fiscal un mijloc fix furat?"
description: "Ce se întâmplă cu TVA-ul dedus la achiziția unui mijloc fix furat, conform Codului fiscal, și ce documente sunt necesare pentru a evita ajustarea deducerii."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se tratează fiscal un mijloc fix furat?

Furtul unui mijloc fix ridică imediat o întrebare de TVA: dacă bunul a dispărut din gestiune fără să mai genereze venituri, trebuie „întoarsă" taxa dedusă la achiziția lui? Legea răspunde explicit — cu o singură condiție esențială.

## Temeiul legal

::: ghid-temei
„bunurile de capital reprezintă toate activele corporale fixe, definite la art. 266 alin. (1) pct. 3 [...]."
— Legea 227/2015 (Codul fiscal), art. 305 alin. (1) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Ajustarea taxei deductibile prevăzute la alin. (1) lit. d) se efectuează: [...] d) în situația în care bunul de capital își încetează existența, cu următoarele excepții: 1. bunul de capital a făcut obiectul unei livrări sau unei livrări către sine pentru care taxa este deductibilă; 2. bunul de capital este pierdut, distrus sau furat, în condițiile în care aceste situații sunt demonstrate sau confirmate în mod corespunzător. În cazul bunurilor furate, persoana impozabilă demonstrează furtul bunurilor pe baza actelor doveditoare emise de organele judiciare; [...]."
— Legea 227/2015 (Codul fiscal), art. 305 alin. (4) lit. d) pct. 2 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Un mijloc fix e, din perspectiva TVA, un „bun de capital" (art. 305 alin. (1) lit. a) din Codul fiscal), nu un bun oarecare — de aceea regula de ajustare aplicabilă e cea de la art. 305, cu regim de ajustare eșalonat pe 5 ani (bunuri mobile) sau 20 de ani (imobile), nu regula generală de ajustare imediată de la art. 304, care vizează explicit „bunurile, altele decât bunurile de capital".

Condiții și consecințe practice:

- **TVA-ul dedus** la achiziția mijlocului fix **nu se ajustează** (nu trebuie „restituit", nici măcar eșalonat, pe restul perioadei de ajustare) dacă furtul e demonstrat corespunzător — condiția obligatorie e existența unor **acte doveditoare emise de organele judiciare** (plângere penală înregistrată, proces-verbal al poliției, dovada demarării cercetărilor), nu doar o declarație internă a firmei sau un proces-verbal de constatare a lipsei din gestiune întocmit unilateral;
- fără aceste acte, lipsa din gestiune se tratează ca o **lipsă neimputabilă fără justificare**, caz în care regula generală de ajustare a deducerii TVA pentru bunuri de capital se aplică — practic, furtul nedocumentat penal riscă să fie tratat fiscal ca și cum bunul ar fi fost folosit în scopuri fără drept de deducere;
- la nivelul **impozitului pe profit**, valoarea rămasă neamortizată a mijlocului fix furat, scoasă din gestiune pe baza documentelor justificative (proces-verbal de constatare, dosar penal), urmează regulile generale de deductibilitate a cheltuielilor efectuate în scopul activității economice (art. 25 alin. 1) — o pierdere din furt documentat corespunzător e, în principiu, o cheltuială aferentă activității, spre deosebire de o lipsă nejustificată din gestiune;
- dacă bunul e recuperat ulterior sau despăgubit de o asigurare, sumele respective urmează regimul lor fiscal propriu (venit din despăgubire, reintrarea bunului în gestiune), distinct de tratamentul inițial al furtului.

## Ce se greșește în practică

- Se scade mijlocul fix din gestiune doar pe baza unui proces-verbal intern de inventariere, fără sesizarea organelor de poliție — fără actul doveditor emis de organele judiciare, condiția legală pentru neajustarea TVA nu e îndeplinită.
- Se ajustează „preventiv" TVA-ul dedus la achiziție, de teama unui control, chiar dacă furtul e documentat corespunzător — legea exclude explicit ajustarea în acest caz, iar restituirea nejustificată a TVA reprezintă ea însăși o eroare.
- Se amână sesizarea penală până la o dată ulterioară constatării lipsei, ceea ce complică demonstrarea corelației temporale dintre constatarea lipsei din gestiune și momentul furtului.

## Ce face iConta.eu

iConta.eu importă și gestionează registrul de mijloace fixe (`core/mijloace_fixe_import_api.py`, `core/repo_mijloace_fixe.py`), cu valoarea de intrare, amortizarea cumulată și valoarea reziduală. Aplicația nu are, la data acestui ghid, o funcție dedicată scoaterii din gestiune a unui mijloc fix furat și verificării condiției de neajustare a TVA (existența actelor doveditoare emise de organele judiciare) — această verificare și decizia de tratament fiscal rămân în sarcina contabilului, pe baza documentelor obținute.

[iConta.eu](/)
