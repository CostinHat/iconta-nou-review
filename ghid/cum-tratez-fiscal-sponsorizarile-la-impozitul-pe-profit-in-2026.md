---
title: Cum tratez fiscal sponsorizările la impozitul pe profit în 2026?
description: În 2026 se aplică regimul în vigoare din 03.02.2022 — credit fiscal egal cu minimul dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit, condiționat de un contract scris și, pentru entitățile nonprofit/culte, de înscrierea beneficiarului în Registrul ANAF, cu spațiul neconsumat redirecționabil prin D177; facilitatea similară de la impozitul micro nu mai există din 01.01.2024.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum tratez fiscal sponsorizările la impozitul pe profit în 2026?

Dacă firma dumneavoastră plătește impozit pe profit în 2026 și acordă sau intenționează să acorde o sponsorizare, regimul aplicabil este cel în vigoare din 03.02.2022 — fără modificări ulterioare la procentele de calcul. Acest ghid strânge, într-un singur loc, condițiile pe care trebuie să le bifați, pentru anul fiscal curent.

## Temeiul legal

::: ghid-temei
„i) cheltuielile de sponsorizare și/sau mecenat, acordate potrivit legii; contribuabilii care efectuează sponsorizări și/sau acte de mecenat, potrivit prevederilor Legii nr. 32/1994 privind sponsorizarea, cu modificările și completările ulterioare, și ale Legii bibliotecilor nr. 334/2002, republicată, cu modificările și completările ulterioare, scad sumele aferente din impozitul pe profit datorat la nivelul valorii minime dintre următoarele:
1. valoarea calculată prin aplicarea a 0,75% la cifra de afaceri; pentru situațiile în care reglementările contabile aplicabile nu definesc indicatorul cifra de afaceri, această limită se determină potrivit normelor;
2. valoarea reprezentând 20% din impozitul pe profit datorat. În cazul sponsorizărilor efectuate către entități persoane juridice fără scop lucrativ, inclusiv unități de cult, sumele aferente acestora se scad din impozitul pe profit datorat, în limitele prevăzute de prezenta literă, doar dacă beneficiarul sponsorizării este înscris, la data încheierii contractului, în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale, potrivit alin. (4^1).”

— *Codul fiscal, art. 25 alin. (4) lit. i), forma actuală.*

„Contractul de sponsorizare se încheie în forma scrisă, cu specificarea obiectului, valorii și duratei sponsorizării, precum și a drepturilor și obligațiilor părților.”

— *Legea nr. 32/1994 privind sponsorizarea, art. 1 alin. (2).*

„Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale se organizează de A.N.A.F.... Registrul este public și se afișează pe site-ul A.N.A.F.”

— *Codul fiscal, art. 25 alin. (4^1).*

„1. Plătitorii de impozit pe profit pot dispune redirecţionarea unor sume din impozitul datorat, potrivit legii, până la termenele legale de depunere a declaraţiei anuale de impozit pe profit [D101].”

— *OPANAF nr. 3562/2024, procedura D177.*
:::

## Regimul complet, pentru 2026

- **Plafonul deductibil:** `min(0,75% × cifra de afaceri; 20% × impozitul pe profit datorat)`. Se ia întotdeauna valoarea mai mică dintre cele două.
- **Contract scris obligatoriu:** Legea nr. 32/1994 cere forma scrisă, cu obiectul, valoarea și durata sponsorizării — fără el, calificarea cheltuielii drept sponsorizare poate fi contestată, indiferent cum a fost înregistrată contabil.
- **Condiția de Registru:** dacă beneficiarul e o entitate fără scop lucrativ sau o unitate de cult, trebuie să fie înscris(ă) în Registrul entităților/unităților de cult **la data încheierii contractului**. Lipsa înscrierii face întregul credit nedatorat, nu doar excedentul peste plafon.
- **Declararea creditului:** creditul se reflectă în D101 a anului fiscal în care a fost acordată sponsorizarea.
- **Spațiul neconsumat, prin D177:** dacă sponsorizarea efectivă e sub plafon, diferența poate fi redirecționată separat, direct din impozitul pe profit datorat, prin formularul D177, până la termenul de depunere a D101.
- **Înregistrare contabilă:** nota contabilă uzuală este `6582 = 401` (sponsorizare pe bază de contract, cu obligație către beneficiar) sau `6582 = 5121` (plată directă). Contul 6582 poartă oficial numele „Donații acordate” în planul de conturi — nu există un cont dedicat „sponsorizare”.
- **TVA, dacă sponsorizarea e în bunuri sau servicii:** acordarea gratuită nu e asimilată unei livrări/prestări cu plată, dar numai „în condițiile stabilite prin normele metodologice” — verificați aceste condiții separat, mai ales dacă valoarea bunurilor e mare.

## Ce nu mai există în 2026

Facilitatea similară de la impozitul pe veniturile microîntreprinderilor (credit de 20% din impozitul micro trimestrial) a fost **abrogată de la 01.01.2024**, cu anul fiscal 2023 ca ultim an de aplicare. Dacă firma dumneavoastră e microîntreprindere în 2026, sponsorizarea nu mai reduce impozitul micro sub nicio formă — doar firmele plătitoare de impozit pe profit mai beneficiază de creditul descris în acest ghid.

::: ghid-exemplu
O firmă plătitoare de impozit pe profit are, în 2026, cifra de afaceri 8.000.000 lei și impozit pe profit datorat 60.000 lei. Plafonul de sponsorizare este `min(0,75% × 8.000.000; 20% × 60.000) = min(60.000; 12.000) = 12.000 lei`. Dacă firma sponsorizează efectiv 12.000 lei o entitate din Registru, întreaga sumă se scade din impozitul pe profit prin D101, fără spațiu rămas pentru D177.
:::

## Ce se greșește în practică

- Se calculează plafonul folosind un singur criteriu (doar cifra de afaceri sau doar impozitul pe profit), nu minimul dintre cele două.
- Se acordă sponsorizarea fără contract scris, ceea ce expune firma riscului ca deductibilitatea să fie contestată integral.
- Se omite verificarea Registrului la data încheierii contractului — o verificare ulterioară nu repară o neînscriere la data semnării.
- Se caută greșit un cont „sponsorizare” distinct în planul de conturi, deși practica uzuală folosește contul 6582 „Donații acordate”.
- Se aplică din obișnuință regula veche (0,5%, reportare 7 ani) unei sponsorizări din 2026, deși aceasta nu mai e valabilă din 03.02.2022.

## Ce face iConta.eu

Motorul `core/sponsorizari.py` implementează regula actuală prin `plafon_credit()` (calculul `min(0,75% × cifra de afaceri, 20% × impozit pe profit)`) și `credit_sponsorizare()` (aplică plafonul, verifică `beneficiar_in_registru` și calculează `redirectionabil_d177`). Pentru un an fiscal precum 2026, această regulă corespunde legii în vigoare. Ramura `tip_impozit="micro"` este dezactivată în afara intervalului 01.04.2019–31.12.2023, deci pentru 2026 returnează corect credit 0 pentru orice sponsorizare a unei microîntreprinderi.

Notele contabile se generează prin `nota_sponsorizare(suma, mod)`, dar doar pentru modurile `"contract"` și `"plata"` — sponsorizarea în natură nu are un mod dedicat și trebuie tratată manual, inclusiv sub aspectul TVA.

[iConta.eu](/)
