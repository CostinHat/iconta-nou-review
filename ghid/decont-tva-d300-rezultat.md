---
title: Decontul de TVA (D300): de plată, de recuperat sau report
description: Cum rezultă din decontul D300 TVA de plată sau suma negativă, ce faci cu soldul negativ — report sau rambursare — și de ce sub 5.000 lei rambursarea nu se poate cere.
published: 2026-08-12
modified: 2026-08-12
---

# Cum rezultă din decontul de TVA suma de plată sau de recuperat și ce faci cu soldul negativ?

Decontul confruntă, pentru fiecare perioadă, TVA-ul colectat din facturile emise cu TVA-ul deductibil din facturile primite. Din confruntare iese un singur rezultat: ori ai de plată la buget, ori ai un excedent. Excedentul nu dispare — îl reporți în perioada următoare sau ceri rambursarea, dar nu pe amândouă, și nu sub un anumit prag.

## Temeiul legal

::: ghid-temei
**Art. 323 din Codul fiscal (Legea 227/2015) — Decontul de taxă.** *„(1) Persoanele înregistrate conform art. 316 trebuie să depună […] pentru fiecare perioadă fiscală, un decont de taxă, până la data de 25 inclusiv a lunii următoare celei în care se încheie perioada fiscală respectivă. (2) Decontul […] va cuprinde suma taxei deductibile pentru care ia naștere dreptul de deducere în perioada fiscală de raportare […], suma taxei colectate a cărei exigibilitate ia naștere în perioada fiscală de raportare […]. (3) Datele înscrise incorect într-un decont de taxă se pot corecta prin decontul unei perioade fiscale ulterioare și se vor înscrie la rândurile de regularizări."*

**Art. 303 din Codul fiscal — Rambursările de taxă.** *„(1) În situația în care taxa aferentă achizițiilor […] care este deductibilă într-o perioadă fiscală, este mai mare decât taxa colectată pentru operațiuni taxabile, rezultă un excedent în perioada de raportare, denumit […] sumă negativă a taxei."*

*„(6) […] Dacă taxa de plată cumulată este mai mare decât suma negativă a taxei cumulată, rezultă un sold de taxă de plată. Dacă suma negativă a taxei cumulată este mai mare decât taxa de plată cumulată, rezultă un sold al sumei negative a taxei."*

*„(7) Persoanele impozabile […] pot solicita rambursarea soldului sumei negative […] prin bifarea casetei corespunzătoare din decontul de taxă, decontul fiind și cerere de rambursare, sau pot reporta soldul sumei negative în decontul perioadei fiscale următoare. Dacă persoana impozabilă solicită rambursarea […], acesta nu se reportează […]. Nu poate fi solicitată rambursarea soldului sumei negative […] mai mic de 5.000 lei inclusiv, acesta fiind reportat obligatoriu în decontul perioadei fiscale următoare."*
:::

## Regula concretă

Decontul adună întâi două totaluri: **TVA colectată** din livrările taxabile ale perioadei și **TVA dedusă** din achizițiile deductibile. Din ele iese rezultatul perioadei:

- **Colectată mai mare decât dedusă** → **TVA de plată** (colectată − dedusă).
- **Dedusă mai mare decât colectată** → **sumă negativă a taxei**, adică excedent de recuperat.

Peste rezultatul perioadei se aplică regularizările — soldul de plată neachitat din decontul precedent și soldul negativ reportat — și abia atunci rezultă **soldul final**.

Ce faci cu soldul negativ e alegerea ta, în două variante care se exclud:

- **Report** în decontul perioadei următoare. Opțiunea implicită, fără formalități.
- **Rambursare**, prin bifarea casetei din decont. Decontul devine cerere de rambursare, iar soldul **nu se mai reportează**.

Sub pragul de **5.000 lei inclusiv**, rambursarea nu se poate cere: soldul se reportează obligatoriu.

**Termenul:** până la data de 25 inclusiv a lunii următoare perioadei fiscale, lunară sau trimestrială.

## Un exemplu

::: ghid-exemplu
**SC Exemplu SRL**, plătitoare de TVA cu regim lunar, cota standard 21%.

**Luna cu TVA de plată.** Livrări taxabile 100.000 lei → **TVA colectată 21.000 lei**. Achiziții deductibile 60.000 lei → **TVA dedusă 12.600 lei**.

**TVA de plată = 21.000 − 12.600 = 8.400 lei**, de achitat până la 25 ale lunii următoare.

**Luna cu sold negativ.** Firma cumpără mult și vinde puțin: livrări 30.000 lei → colectată **6.300 lei**; achiziții 70.000 lei → dedusă **14.700 lei**.

**Sumă negativă = 14.700 − 6.300 = 8.400 lei.**

Fiind peste 5.000 lei, firma alege: **reportează** cei 8.400 lei în luna următoare, sau **bifează rambursarea** și cere banii de la ANAF. Dacă bifează rambursarea, suma nu se mai reportează — altfel ar fi numărată de două ori.

Dacă soldul negativ ar fi fost 4.000 lei, sub prag, rambursarea nu s-ar fi putut cere: report obligatoriu.
:::

## Ce se greșește în practică

- **Se confundă baza cu taxa.** Rezultatul decontului nu e diferența dintre vânzări și cumpărături. 100.000 lei livrări față de 60.000 lei achiziții nu dau „40.000 de plată", ci 8.400 lei — diferența de TVA la cota 21%.
- **Se cere rambursarea sub prag.** Un sold negativ de 5.000 lei inclusiv nu poate fi rambursat.
- **Se reportează și se cere rambursarea în același timp.** Odată bifată rambursarea, soldul nu se mai reportează. Trecut și în decontul următor, e numărat de două ori.
- **Se corectează decontul depus în loc de a regulariza.** Datele înscrise greșit se corectează prin decontul unei perioade ulterioare, la rândurile de regularizări — nu prin retrimiterea celui vechi.

## Ce face iConta.eu

Decontul se construiește direct din facturile perioadei: fiecare factură emisă intră la colectată, fiecare factură primită la deductibilă, pe cota ei, și parcurge apoi tot lanțul de regularizări până la rezultat. Îți arată dacă perioada se închide cu TVA de plată sau cu sold negativ.

Facturile care nu se pot clasifica automat — cote atipice, taxare inversă, scutiri — sunt semnalate, ca să nu dispară tăcut din decont. Tipul de decont, lunar sau trimestrial, se alege din vectorul fiscal, iar fișierul XML e validat pe validatorul oficial ANAF (DUKIntegrator).

Alegerea dintre report și rambursare rămâne a ta — e o decizie de trezorerie, nu de calcul.

Vezi și: [D394 și legătura cu decontul](/ghid/d394-ce-declari-reconciliere) și [controlul încrucișat D390 față de decont](/ghid/control-incrucisat-d390).

[iConta.eu](/)
