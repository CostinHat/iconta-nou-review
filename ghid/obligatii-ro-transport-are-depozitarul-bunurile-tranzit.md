---
title: "Ce obligații RO e-Transport are depozitarul pentru bunurile în tranzit intracomunitar?"
description: "Depozitarul declară ambele segmente: intrarea în țară până la depozit și plecarea din depozit spre frontieră, după depozitare sau după formarea unui nou transport."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Ce obligații RO e-Transport are depozitarul pentru bunurile în tranzit intracomunitar?

Când bunurile dintr-o tranzacție între doi parteneri din alte state membre trec prin România și sunt descărcate aici pentru depozitare sau pentru formarea unui nou transport, **depozitarul** este cel care declară în RO e-Transport. Obligația privește **ambele segmente**: de la frontiera de intrare până la depozit și de la depozit, după depozitare sau regrupare, până la frontiera de ieșire.

Depozitarul nu e nici vânzător, nici cumpărător. Obligația lui vine din faptul că bunurile sunt descărcate și reîncărcate pe teritoriul României. Bunurile în tranzit care doar traversează țara nu pot fi descărcate în România, cu excepția depozitării sau a formării unui nou transport.

## Temeiul legal

::: ghid-temei
„Obligația declarării în Sistemul RO e-Transport a datelor prevăzute la art. 4 alin. (1) lit. a) referitoare la transportul internațional de bunuri revine următorilor utilizatori: [...] d) depozitarului, în cazul bunurilor care fac obiectul tranzacțiilor intracomunitare aflate în tranzit, atât pentru bunurile descărcate pe teritoriul României spre depozitare sau pentru formarea unui nou transport din una sau mai multe partide de bunuri, cât și pentru bunurile încărcate după depozitare sau după formarea unui nou transport pe teritoriul național din una sau mai multe partide de bunuri."
— OUG 41/2022, art. 8^1 lit. d) (sursă: [OUG nr. 41/2022 pentru instituirea Sistemului național RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/253801))

„(4) Este interzisă descărcarea pe teritoriul României a bunurilor care fac obiectul tranzacțiilor intracomunitare aflate în tranzit, cu excepția celor care fac obiectul depozitării sau formării unui nou transport din una sau mai multe partide de bunuri."
— OUG 41/2022, art. 11 alin. (4) (sursă: [OUG nr. 41/2022 pentru instituirea Sistemului național RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/253801))
:::

Obligațiile depozitarului, pe segmente:

- **Segmentul de intrare** (art. 2 pct. 9 lit. g)): de la punctul de frontieră la intrare până la locul de descărcare pentru depozitare sau regrupare. Codul UIT e valabil **15 zile** calendaristice (art. 11 alin. (2)).
- **Segmentul de ieșire** (art. 2 pct. 9 lit. h)): de la locul de încărcare din țară, după depozitare sau regrupare, până la punctul de frontieră la ieșire. Codul UIT e valabil **5 zile**.
- **Termenul de declarare**: cel mult 3 zile înainte de data declarată pentru începerea transportului, dar până la prezentarea în punctul de frontieră la intrare, respectiv până la plecarea din depozit (art. 11 alin. (1)).
- **Încadrare incertă**: pentru bunurile cu risc fiscal ridicat, dacă documentele depozitarului nu arată încadrarea bunurilor, acesta declară toate bunurile din partidă (art. 12 alin. (2)).

Descărcarea în România a bunurilor în tranzit, în afara depozitării sau a formării unui nou transport, este contravenție (art. 13^1 alin. (1) lit. a)). Amenda poate fi însoțită de confiscarea contravalorii bunurilor nedeclarate.

::: ghid-exemplu
SC Exemplu Logistic SRL operează un depozit lângă Oradea. Un furnizor din Ungaria vinde componente unui client din Bulgaria. Marfa intră în țară pe 5 paleți, stă 4 zile în depozit, apoi pleacă împreună cu alte trei partide într-un nou camion spre Bulgaria.

- Intrare: SC Exemplu Logistic SRL declară segmentul Borș → depozit, cu un cod UIT valabil 15 zile.
- Ieșire: SC Exemplu Logistic SRL declară segmentul depozit → Giurgiu pentru noul transport, cu un cod UIT nou, valabil 5 zile.
:::

## Ce se greșește în practică

- **Depozitarul presupune că declară vânzătorul sau cumpărătorul.** Niciunul nu e în România, iar legea numește expres depozitarul.
- **Se declară doar intrarea.** Plecarea după depozitare sau regrupare se declară separat.
- **Se aplică 15 zile și la segmentul de ieșire.** Termenul de 15 zile vizează lit. g), adică intrarea spre depozitare.
- **Se descarcă marfa în tranzit pentru alte scopuri** (de exemplu o livrare parțială în țară). Descărcarea e permisă doar pentru depozitare sau pentru formarea unui nou transport.

## Ce face iConta.eu

Pe cardul e-Transport, iConta.eu are tipurile de operațiune „Tranzacție intracom. – intrare” și „Tranzacție intracom. – ieșire” și generează XML-ul notificării cu bunurile, partenerul, vehiculul și traseul. Pentru ambele operațiuni aplicația afișează o fereastră de valabilitate de 5 zile. Valabilitatea legală de 15 zile pentru segmentul de intrare nu e încă reflectată în aplicație și rămâne de urmărit de contabil. Aplicația nu gestionează stocul din depozit al terților.

[iConta.eu](/)
