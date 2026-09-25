---
title: "Data limită pentru depunerea D112 în 2026"
description: "Declarația 112 se depune până la termenul de plată a impozitului pe salarii — data de 25 inclusiv a lunii următoare, sau a lunii următoare trimestrului pentru angajatorii eligibili la raportare trimestrială."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Data limită pentru depunerea D112 în 2026

Termenul de depunere a D112 (Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate) nu este stabilit independent — legea îl leagă direct de termenul de plată a impozitului pe salarii, care diferă în funcție de periodicitatea aplicabilă angajatorului.

## Temeiul legal

::: ghid-temei
„Plătitorii de salarii și de venituri asimilate salariilor au obligația de a calcula și de a reține impozitul aferent veniturilor fiecărei luni la data efectuării plății acestor venituri, precum și de a-l plăti la bugetul de stat până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc aceste venituri."
— Legea nr. 227/2015 (Codul fiscal), art. 80 alin. (1), coroborat cu art. 81 alin. (1): „Plătitorii de salarii și de venituri asimilate salariilor au obligația să completeze și să depună Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate pentru fiecare beneficiar de venit, până la termenul de plată a impozitului, inclusiv." (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă pentru termenul efectiv al D112 în 2026:

- Regula generală: D112 se depune până la **data de 25 inclusiv a lunii următoare** celei pentru care se datorează contribuțiile și impozitul pe salarii — același termen ca plata efectivă a impozitului.
- **Excepție pentru raportare trimestrială**: unii angajatori (asociații/fundații fără scop patrimonial, persoane juridice plătitoare de impozit pe profit cu venituri totale sub 100.000 euro și până la 3 salariați în anul anterior, microîntreprinderi cu până la 3 salariați, PFA/II și angajatori persoane fizice cu personal angajat) plătesc impozitul — și deci depun D112 — până la **data de 25 inclusiv a lunii următoare trimestrului** pentru care se datorează, nu lunar (art. 80 alin. (2)).
- Dacă data de 25 cade într-o zi nelucrătoare, se aplică regulile generale de calcul al termenelor din Codul de procedură fiscală (termenul se prorogă la următoarea zi lucrătoare) — verifică an de an calendarul specific.

## Ce se greșește în practică

- Se aplică automat termenul lunar (25 a lunii următoare) tuturor angajatorilor, fără verificarea condițiilor care permit raportarea trimestrială (număr mediu de salariați, venituri totale ale anului anterior).
- Se confundă termenul de depunere a D112 cu termenul de plată efectivă a contribuțiilor — legea le leagă direct („până la termenul de plată a impozitului, inclusiv”), dar orice eroare de calcul a termenului de plată se propagă automat și la declarație.
- Se ignoră faptul că eligibilitatea pentru raportare trimestrială se verifică an de an, pe baza numărului mediu de salariați și a veniturilor din anul anterior (art. 80 alin. (3), care trimite la art. 147 alin. (6)-(7)) — un angajator poate trece de la trimestrial la lunar dacă nu mai îndeplinește condițiile.

## Ce face iConta.eu

iConta.eu calculează statul de plată și generează D112 pe baza salariilor înregistrate în aplicație pentru fiecare lună, respectând structura oficială a declarației publicată de ANAF. Determinarea periodicității corecte (lunară sau trimestrială), în funcție de numărul de salariați și veniturile totale ale anului anterior, rămâne o verificare pe care utilizatorul o face la configurarea firmei, aplicația nefăcând automat această încadrare pe baza istoricului fiscal al firmei.

[iConta.eu](/)
