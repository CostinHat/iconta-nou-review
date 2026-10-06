---
title: "Cum se limitează creditul fiscal extern la impozitul pe profit când firma are venituri din mai multe țări?"
description: "Limita creditului fiscal extern se calculează separat pe fiecare țară: minimul dintre impozitul plătit acolo și 16% din venitul/profitul din acea țară, după regulile române."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Cum se limitează creditul fiscal extern la impozitul pe profit când firma are venituri din mai multe țări?

Creditul fiscal extern se limitează **separat pentru fiecare țară**. Pentru fiecare stat străin compari două sume: impozitul efectiv plătit acolo și impozitul pe profit românesc calculat cu cota de 16% pe profitul sau venitul din acel stat, determinat după regulile române. Se acordă suma mai mică. Toate veniturile dintr-o singură țară se tratează ca aceeași sursă. Un plus de impozit plătit într-o țară nu poate acoperi limita neutilizată din altă țară.

## Temeiul legal

::: ghid-temei
„Creditul acordat pentru impozitele plătite unui stat străin într-un an fiscal nu poate depăși impozitul pe profit, calculat prin aplicarea cotei de impozit pe profit prevăzute la art. 17 la profitul impozabil obținut în statul străin, determinat în conformitate cu regulile prevăzute în prezentul titlu, sau la venitul obținut din statul străin.”
— Codul fiscal (Legea 227/2015), art. 39 alin. (6) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

::: ghid-temei
„Limitarea prevăzută la art. 39 alin. (6) din Codul fiscal va fi calculată separat pentru fiecare sursă de venit. În scopul aplicării acestei prevederi, toate veniturile persoanei juridice române a căror sursă se află în aceeași țară străină vor fi considerate ca având aceeași sursă.”
— HG 1/2016, Normele metodologice ale Codului fiscal, titlul II pct. 39 alin. (5) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))
:::

::: ghid-temei
„Rândul se completează cu valoarea cea mai mică dintre următoarele două valori, pe fiecare stat din care se obţin venituri prin intermediul unui sediu permanent sau venituri supuse impozitului cu reţinere la sursă, venituri impuse atât în România, cât şi în statul străin”
— OPANAF 206/2025, instrucțiunile D101, rândul 42.1 (sursă: [OPANAF nr. 206/2025 pentru aprobarea formularelor 101](https://legislatie.just.ro/Public/DetaliiDocument/294776))

„Suma care se înscrie la acest rând este mai mică sau cel mult egală cu suma înscrisă la rândul 41.”
— OPANAF 206/2025, instrucțiunile D101, rândul 42.1 (sursă: [OPANAF nr. 206/2025 pentru aprobarea formularelor 101](https://legislatie.just.ro/Public/DetaliiDocument/294776))
:::

Cum se calculează:

1. **Grupezi veniturile pe țări.** Profitul unui sediu permanent și dobânzile sau redevențele din aceeași țară intră în același calcul.
2. **Calculezi pentru fiecare țară limita românească.** Aplici cota de 16% (art. 17) pe profitul impozabil sau pe venitul din acea țară, determinat după regulile române, nu după cele ale statului străin.
3. **Compari cu impozitul plătit efectiv** acolo, dovedit cu documentul justificativ, și reții suma mai mică.
4. **Aduni creditele pe țări** și verifici că totalul nu depășește impozitul pe profit de la rândul 41 din D101.

Condiții prealabile: să existe convenție de evitare a dublei impuneri cu statul respectiv, convenția să prevadă metoda creditului, iar plata impozitului să fie dovedită.

::: ghid-exemplu
SC Exemplu SRL are în 2026:

- **Țara X:** un sediu permanent cu profit impozabil de 100.000 lei după regulile române. A plătit acolo un impozit de 25.000 lei. Limita românească: 100.000 × 16% = 16.000 lei. Credit acordat: **16.000 lei**.
- **Țara Y:** dobânzi de 20.000 lei, cu un impozit reținut la sursă de 2.000 lei. Limita: 20.000 × 16% = 3.200 lei. Credit acordat: **2.000 lei**.

Creditul fiscal extern total este de 18.000 lei. Plusul de 9.000 lei plătit în țara X nu se poate folosi pentru limita neutilizată de 1.200 lei din țara Y, pentru că limita se calculează separat pe fiecare țară. Dacă impozitul pe profit total al firmei (rândul 41) este de 60.000 lei, creditul de 18.000 lei se încadrează.
:::

## Ce se greșește în practică

- Se face o limită globală: tot impozitul străin se compară cu 16% din toate veniturile externe. Excedentul dintr-o țară cu impozitare mare ajunge astfel să acopere altă țară.
- Limita se calculează pe profitul determinat după regulile statului străin, nu după regulile române.
- În aceeași țară, veniturile sunt tratate separat pe tipuri, deși normele cer ca toate veniturile din aceeași țară să fie considerate aceeași sursă.
- Se acordă credit pentru o țară cu care convenția prevede metoda scutirii. Acolo profiturile sunt scutite, nu se acordă credit.

## Ce face iConta.eu

În D101 generat de iConta.eu, creditul fiscal extern de la rândul 42.1 e o valoare introdusă de contabil. Aplicația verifică să nu depășească impozitul pe profit de la rândul 41, apoi validează declarația pe validatorul oficial ANAF. Calculul limitei pe fiecare țară se face de contabil, pe baza documentelor de plată din străinătate. Aplicația nu îl face automat.

[iConta.eu](/)
