---
title: Cum se declară profitul reinvestit în D101?
description: Scutirea pentru profitul reinvestit se trece în D101 la rândul 42.2.1, ca parte din creditul fiscal total. Ea micșorează și baza la care se calculează limita de 20% pentru sponsorizare (OPANAF 206/2025, instrucțiunile rândurilor 42-43).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se declară profitul reinvestit în D101?

În declarația 101, modelul aprobat prin OPANAF 206/2025, scutirea calculată potrivit Codului fiscal art. 22 se trece la **rândul 42.2.1 „Impozit pe profit scutit, potrivit art. 22 din Codul fiscal”**. Rândul se completează după ce s-a stabilit impozitul pe profit total de la rândul 41. Suma lui intră în „Total credit fiscal” de la rândul 42.

### Unde se află rândul în structura declarației

- **Rândul 41** – total impozit pe profit (rd. 41.1 + rd. 41.2);
- **Rândul 42** – total credit fiscal = rd. 42.1 + rd. 42.2 + rd. 42.3;
- **Rândul 42.1** – credit fiscal extern;
- **Rândul 42.2** – impozit pe profit scutit, din care:
  - **42.2.1** – scutirea pentru profitul reinvestit (art. 22);
  - **42.2.2** – scutirea pentru activitatea de inovare, cercetare-dezvoltare (art. 22^1);
- **Rândul 42.3** – alte scutiri și reduceri prevăzute de lege.

Instrucțiunile de completare spun că la rândul 42.2.1 „se înscrie suma reprezentând scutirea de la plată a impozitului pe profitul reinvestit”, potrivit art. 22. În fișierul XML, câmpul corespunzător este P4221.

### Controalele pe care le aplică validatorul

- Suma de la rândul 42.2 trebuie să fie mai mică sau cel mult egală cu diferența dintre rândul 41 și rândul 42.1. Creditul fiscal extern se scade primul, iar scutirea se aplică doar asupra impozitului care rămâne.
- Rândul 42.2 trebuie să fie cel puțin egal cu suma subrândurilor 42.2.1 și 42.2.2.
- Rândul 42.3 este plafonat la rd. 41 − rd. 42.1 − rd. 42.2.

Ordinea contează: dacă firma are și impozit plătit în străinătate, spațiul rămas pentru scutirea de la art. 22 se micșorează.

### Efectul asupra sponsorizării

Instrucțiunile pentru rândul 43 plafonează sponsorizarea care se scade din impozit la 20% din diferența dintre rândul 41 și rândul 42. Cu alte cuvinte, scutirea pentru profitul reinvestit reduce baza la care se aplică limita de 20% pentru sponsorizare.

Exemplu: impozitul total de la rândul 41 este 100.000 lei, iar scutirea pentru profitul reinvestit este 30.000 lei. Plafonul de 20% pentru sponsorizare se calculează la 70.000 lei, deci este 14.000 lei, nu 20.000 lei. Plafonul bazat pe cifra de afaceri, prevăzut la Codul fiscal art. 25 alin. (4) lit. i), se aplică în paralel și se reține valoarea mai mică dintre cele două.

### Pași practici

1. Calculează scutirea după art. 22 alin. (2)-(3), pentru fiecare trimestru sau pentru an, după sistemul de declarare pe care îl aplici.
2. Trece la rândul 42.2.1 suma totală a scutirii pentru anul fiscal și verifică dacă se încadrează în limita rd. 41 − rd. 42.1.
3. Recalculează după aceea plafonul pentru sponsorizare de la rândul 43.
4. Păstrează dosarul scutirii: procesele-verbale de punere în funcțiune, facturile, încadrarea activului în Catalog și calculul plafonului de profit.

### Când depui rectificativă

Dacă activul pentru care ai aplicat scutirea iese din patrimoniu înainte de termenul minim de păstrare, impozitul pe profit se recalculează. Codul fiscal art. 22 alin. (8) spune expres că în acest caz contribuabilul „are obligația depunerii declarației fiscale rectificative”. Practic, corectezi rândul 42.2.1 din D101 a anului în care ai beneficiat de scutire. Excepțiile sunt reorganizările, lichidarea sau falimentul, activele distruse sau furate dovedite și scoaterile din patrimoniu impuse de lege.

La grupul fiscal, formularul 101 Grup fiscal are un rând echivalent, 5.2.1. Pe el se trec scutirile determinate de fiecare membru și comunicate persoanei juridice responsabile.

### De reținut
- Scutirea pentru profitul reinvestit se declară la rândul 42.2.1 (câmpul P4221), în cadrul rândului 42.
- Rândul 42.2 poate fi cel mult rd. 41 − rd. 42.1.
- Scutirea micșorează baza plafonului de 20% pentru sponsorizare de la rândul 43.
- Dacă vinzi activul prea devreme, depui D101 rectificativă pentru anul scutirii.
