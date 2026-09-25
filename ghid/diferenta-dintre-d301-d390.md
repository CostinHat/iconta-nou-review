---
title: "Care este diferența dintre D301 și D390?"
description: "D301 și D390 nu sunt variante ale aceleiași declarații — se adresează unor categorii diferite de contribuabili, cu scopuri diferite. Diferența explicată pe text oficial."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Care este diferența dintre D301 și D390?

D301 și D390 sunt adesea confundate pentru că amândouă privesc operațiuni intracomunitare — dar se adresează unor categorii diferite de persoane impozabile, cu scopuri diferite: una e un decont de plată a TVA, cealaltă e o declarație pur informativă.

## Temeiul legal

::: ghid-temei
„I. Contribuabilii care au obligaţia să depună decontul special de taxă pe valoarea adăugată. Secţiunea 1 «Achiziţii intracomunitare de bunuri taxabile - altele decât mijloacele de transport noi şi produsele accizabile» se completează numai de către persoanele înregistrate conform art. 317 din Legea nr. 227/2015 privind Codul fiscal, cu modificările şi completările ulterioare, denumită în continuare Codul fiscal, dar care nu sunt înregistrate şi nu trebuie să se înregistreze conform art. 316 din acelaşi cod."
— OPANAF 592/2016, Anexa 2, Instrucțiuni cap. I (sursă: anaf_surse/opanaf_592_2016_d301.txt)

„1.1. Declaraţia recapitulativă se depune lunar, în condiţiile prevăzute la art. 325 din Legea nr. 227/2015 privind Codul fiscal, cu modificările şi completările ulterioare (Codul fiscal), până la data de 25 inclusiv a lunii următoare unei luni calendaristice, de către persoanele impozabile înregistrate în scopuri de TVA conform art. 316 sau 317 din Codul fiscal."
— OPANAF 705/2020, Anexa 2, Instrucțiuni pct. 1.1 (sursă: anaf_surse/opanaf_705_2020_d390.txt)
:::

Diferența esențială stă chiar în cine are obligația de a le depune și ce anume declară fiecare:

- **D301 (Decont special de TVA)** — se depune, în principal, de persoane care **nu** sunt înregistrate normal în scopuri de TVA (nu conform art. 316), ci doar special, pentru operațiuni intracomunitare (art. 317) — de exemplu firme scutite de TVA sau la regimul de scutire pentru întreprinderi mici. E un decont care generează efectiv o **obligație de plată** a TVA pentru achiziția intracomunitară raportată.
- **D390 (declarație recapitulativă VIES)** — se depune de persoane înregistrate normal (art. 316) **sau** special (art. 317) în scopuri de TVA, pentru livrări, achiziții și prestări intracomunitare. E o declarație **informativă**, care nu generează ea însăși o plată — TVA-ul aferent operațiunilor raportate în D390 se reflectă, după caz, în decontul de TVA obișnuit (D300) sau chiar în D301, pentru cei înregistrați doar special.
- pentru achizițiile intracomunitare **de mijloace de transport noi**, D301 are o secțiune dedicată, separată de secțiunea generală de bunuri.

## Ce se greșește în practică

- Se tratează D301 ca pe o „variantă simplificată" a D390 pentru firme mici — de fapt cele două se adresează unor categorii diferite de înregistrare TVA și au funcții diferite (decont de plată versus declarație informativă).
- Se presupune că o firmă înregistrată normal în scopuri de TVA (art. 316) trebuie să depună și D301 — secțiunea generală a D301 e rezervată explicit celor **ne**înregistrați conform art. 316.
- Se omite depunerea D301 pentru achiziția unui mijloc de transport nou de către o persoană care nu are alte operațiuni intracomunitare — regimul special pentru mijloace de transport noi are reguli proprii, separate de restul declarației.

## Ce face iConta.eu

Aplicația generează separat, ca module distincte, atât D301 cât și D390. Cele două nu sunt izolate una de cealaltă: la generarea D390, motorul de clasificare a operațiunilor intracomunitare poate **prelua automat din ecranul D301** achizițiile introduse acolo (cu tip 1, 3 sau 5 — bunuri sau servicii intracomunitare), transformându-le în linii D390 pre-tipizate, dar numai dacă operațiunea din D301 are completată țara furnizorului. Achizițiile de mijloace de transport noi și cele cu taxare inversă generală (art. 307) sunt excluse explicit din această auto-derivare, cu motivul afișat, pentru că nu se declară pe același cod.

[iConta.eu](/)
