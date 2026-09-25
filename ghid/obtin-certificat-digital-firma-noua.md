---
title: "Cum obțin certificat digital pentru firma nouă?"
description: "Obligația legală de identificare prin certificat calificat pentru persoanele juridice care transmit documente electronic organului fiscal, potrivit Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum obțin certificat digital pentru firma nouă?

Pentru o firmă nou-înființată, obligația de a folosi un certificat digital calificat nu este opțională — legea o leagă direct de modul în care persoanele juridice trebuie să se identifice atunci când transmit documente pe cale electronică organului fiscal.

## Temeiul legal

::: ghid-temei
„ART. 80 Identificarea contribuabilului/plătitorului în mediul electronic
(1) Contribuabilul/Plătitorul care depune cereri, înscrisuri sau documente la organul fiscal, prin mijloace electronice de transmitere la distanță, se identifică în relația cu organul fiscal astfel:
a) persoanele juridice, asocierile și alte entități fără personalitate juridică, precum și persoanele fizice care desfășoară activități economice în mod independent ori exercită profesii libere se identifică numai cu certificate calificate."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 80 alin. (1) lit. a) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă din text pentru o firmă nouă:

- O persoană juridică (deci un SRL nou-înființat) se identifică **numai cu certificate calificate** atunci când transmite documente electronic organului fiscal — nu are, spre deosebire de unele persoane fizice, alternativa unui simplu cont de utilizator/parolă.
- Această identificare susține, în practică, înrolarea în sistemul de comunicare electronică al Ministerului Finanțelor/ANAF, obligatorie pentru persoanele juridice conform art. 79 alin. (1^1) din același cod — deci certificatul calificat nu e doar util, ci o condiție de acces la comunicarea electronică obligatorie.
- Documentele transmise fără îndeplinirea condițiilor de identificare din art. 80 nu se consideră legal semnate/comunicate în relația cu organul fiscal.
- Limitare onestă: pașii concreți de achiziție a unui certificat calificat (furnizori acreditați, proceduri de emitere) nu au un temei citabil în sursele verificate aici — legea stabilește doar obligația de folosire, nu procedura comercială de obținere.

## Ce se greșește în practică

- Se presupune că o firmă nou-înființată poate comunica electronic cu ANAF folosind doar un cont de utilizator/parolă, similar persoanelor fizice fără activitate economică — art. 80 alin. (1) lit. a) impune certificat calificat pentru persoanele juridice, fără alternativă.
- Se amână obținerea certificatului digital până la prima declarație scadentă, riscând să nu poată fi depusă la timp din lipsa mijlocului de identificare electronică obligatoriu.
- Se folosește certificatul digital al unei persoane fizice asociate/administrator ca înlocuitor al identificării firmei, deși textul distinge explicit persoana juridică de persoana fizică la lit. a), respectiv lit. b).

## Ce face iConta.eu

Verificat în cod: `core/spv_conector.py` și modulele `core/spv_*` gestionează conectarea firmei la Spațiul Privat Virtual al ANAF prin token OAuth, care presupune, la înrolarea inițială, autentificarea cu certificat calificat conform art. 80; iConta.eu nu emite și nu intermediază obținerea certificatului digital în sine — aplicația folosește conexiunea deja stabilită de firmă cu SPV pentru a trimite și primi declarații/facturi electronice.

[iConta.eu](/)
