---
title: "Impozitul pe profit la firmele cu activitate sezonieră"
description: "Impozitul pe profit se calculează cumulat de la începutul anului, astfel încât pierderea dintr-un trimestru fără activitate se compensează automat cu profitul trimestrelor de sezon."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Impozitul pe profit la firmele cu activitate sezonieră

O firmă cu activitate sezonieră (de exemplu turism de vară sau de iarnă) are trimestre cu pierdere clară, alături de trimestre cu profit important. Codul fiscal nu tratează aceste firme diferit printr-un regim special — dar mecanismul de calcul al impozitului pe profit, aplicat corect, rezolvă exact această problemă, prin cumulare de la începutul anului fiscal.

## Temeiul legal

::: ghid-temei
„Calculul, declararea și plata impozitului pe profit, cu excepțiile prevăzute de prezentul articol, se efectuează trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III. Definitivarea și plata impozitului pe profit aferent anului fiscal respectiv se efectuează până la termenul de depunere a declarației privind impozitul pe profit prevăzut la art. 42."
— Legea nr. 227/2015 privind Codul fiscal, art. 41 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Impozitul pe profit nu se calculează separat, izolat, pentru fiecare trimestru — el se calculează **cumulat de la 1 ianuarie**, iar plata trimestrială reprezintă diferența față de ce a fost deja impozitat în trimestrele anterioare ale aceluiași an.
- O pierdere dintr-un trimestru fără activitate (de exemplu extrasezonul) reduce profitul cumulat al anului, compensând astfel profitul realizat în trimestrele de sezon — firma nu plătește impozit pe profitul „brut" al fiecărui trimestru de sezon, izolat.
- Regula se aplică identic tuturor firmelor plătitoare de impozit pe profit; nu există o derogare sau un regim special pentru activitatea sezonieră ca atare — mecanismul de cumulare e cel care „netezește" efectul sezonalității.

## Ce se greșește în practică

- Se calculează impozitul fiecărui trimestru izolat, pe baza profitului acelui trimestru, ignorând pierderea deja înregistrată în trimestrele anterioare — ceea ce duce la o supra-declarare a impozitului datorat în trimestrele de sezon.
- Se presupune că firmele sezoniere au un regim fiscal special la impozitul pe profit, deși legea nu prevede așa ceva — singura particularitate reală e cumularea rezultatului fiscal de la începutul anului.
- Nu se urmărește corect ce sumă a fost deja impozitată în trimestrele anterioare, ceea ce face dificilă calcularea corectă a „diferenței de plată" din trimestrul curent.

## Ce face iConta.eu

Verificarea codului sursă confirmă că iConta.eu calculează impozitul pe profit **cumulat de la 1 ianuarie**, conform art. 41 din Codul fiscal, exact mecanismul relevant pentru firmele sezoniere: un trimestru cu pierdere reduce cumulatul, iar impozitul datorat într-un trimestru ulterior cu profit se calculează ca diferență față de ce a fost deja impozitat, nu pe profitul izolat al acelui trimestru. Documentația internă a aplicației notează explicit acest caz ca fiind corect tratat, ca urmare a unei corecții aplicate calculului declarației D100/D101.

[iConta.eu](/)
