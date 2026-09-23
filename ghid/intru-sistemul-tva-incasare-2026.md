---
title: Cum intru în sistemul TVA la încasare în 2026?
description: Intrarea în sistem nu e automată — presupune o notificare depusă la ANAF până la data de 20 a lunii anterioare începerii perioadei fiscale de aplicare, iar înscrierea produce efecte de la data de 1 a perioadei fiscale următoare depunerii.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum intru în sistemul TVA la încasare în 2026?

A fi eligibil pentru TVA la încasare nu te înscrie automat în sistem — trebuie parcursă o procedură de notificare la ANAF, cu termene precise, iar în 2026 se adaugă și câteva reguli tranzitorii, din cauza schimbării plafonului la 1 martie.

## Temeiul legal

::: ghid-temei
**Art. 324 alin. (12) CF** (rezumat din dosarul de cercetare, fără text exact citat în sursă): notificarea se depune până la data de 20 inclusiv a lunii anterioare începerii perioadei fiscale din care se va aplica sistemul; dacă firma a aplicat deja sistemul anul precedent și cifra de afaceri nu a depășit plafonul, opțiunea continuă tacit, fără o notificare nouă.

**Art. 324 alin. (16) CF**: *„A.N.A.F. organizează Registrul persoanelor impozabile care aplică sistemul TVA la încasare... Registrul este public și se afișează pe site-ul A.N.A.F."* (rezumat din dosar: înscrierea se face de organul fiscal pe baza notificării, cu efect de la data de 1 a perioadei fiscale următoare depunerii, sau de la data înregistrării în scopuri de TVA, pentru firmele nou-înregistrate.)
:::

## Pașii, în ordine

1. **Verifici eligibilitatea** — cifra de afaceri din anul precedent sub plafonul valabil pentru anul intrării, statut de plătitor de TVA, sediu al activității economice în România (art. 282 alin. (3^1)).
2. **Depui notificarea la ANAF**, până la data de 20 inclusiv a lunii anterioare începerii perioadei fiscale din care vrei să aplici sistemul.
3. **Organul fiscal te înscrie** în Registrul public al persoanelor care aplică TVA la încasare, cu efect de la data de 1 a perioadei fiscale următoare depunerii notificării.

Dacă ai aplicat deja sistemul anul precedent și cifra de afaceri n-a depășit plafonul, opțiunea continuă tacit — nu mai depui o notificare nouă.

## Ce e diferit în 2026

Plafonul de eligibilitate s-a schimbat la mijlocul anului (4.500.000 lei până la 29 februarie, 5.000.000 lei din 1 martie 2026, odată cu OUG 8/2026). Dosarul de cercetare semnalează o regulă tranzitorie explicită, prevăzută la art. 9 din OUG 8/2026: firmele care depășiseră 4.500.000 lei, dar nu 5.000.000 lei, în ianuarie 2026, nu au fost radiate din sistem; cele în aceeași situație în februarie 2026 nu au avut obligația unei notificări noi.

## Ce se greșește în practică

- **Se depune notificarea prea târziu**, fără să se respecte termenul de 20 a lunii anterioare începerii perioadei fiscale de aplicare.
- **Se presupune că opțiunea produce efect imediat**, din ziua depunerii, deși legea leagă efectul de data de 1 a perioadei fiscale următoare.
- **Se depune o notificare nouă în 2026 deși firma continua tacit din anul precedent**, fără să fi depășit plafonul.

## Ce face iConta.eu

Eligibilitatea de plafon se verifică automat pe baza plafonului valabil la data de referință (`plafon_la(data)`). Procedura de notificare la ANAF (art. 324) — depunerea propriu-zisă, termenele și confirmarea înscrierii în Registru — nu e implementată ca proces automatizat în motorul F097, conform codului cercetat pentru acest dosar; rămâne un pas administrativ realizat direct de contabil, în afara aplicației.

[iConta.eu](/)
