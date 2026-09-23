---
title: "Închiderea contului de impozit pe profit la final de an"
description: Contul 691 se închide lunar în 121, ca orice cheltuială — dar impozitul pe profit are propriul calendar de declarare și plată, distinct de închiderea contabilă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Închiderea contului de impozit pe profit la final de an

Contul 691 „Cheltuieli cu impozitul pe profit" se închide exact ca orice alt cont de cheltuieli, în contul 121, la sfârșitul fiecărei luni. Ce e specific impozitului pe profit este calendarul separat de declarare și plată către buget, care nu coincide automat cu momentul închiderii contabile a lunii sau a anului.

## Temeiul legal

::: ghid-temei
„În debitul contului 121 «Profit sau pierdere» se înregistrează: la sfârşitul perioadei, soldul debitor al conturilor de cheltuieli (601 la 698)."
— OMFP 1802/2014, funcțiunea contului 121
:::

::: ghid-temei
„Calculul, declararea și plata impozitului pe profit, cu excepțiile prevăzute de prezentul articol, se efectuează trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III. Definitivarea și plata impozitului pe profit aferent anului fiscal respectiv se efectuează până la termenul de depunere a declarației privind impozitul pe profit prevăzut la art. 42."
— Codul fiscal (Legea 227/2015), art. 41 alin. (1)
:::

::: ghid-temei
„Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor [...]."
— Codul fiscal (Legea 227/2015), art. 42 alin. (1)
:::

Mecanic, contabil, procesul e simplu: soldul debitor al contului 691, acumulat pe parcursul lunii sau anului, se transferă în 121 (**121 = 691**), alături de restul conturilor din clasa 6. Această închidere face parte din același proces de închidere lunară care descarcă toate conturile de venituri (7xx) și cheltuieli (6xx) în 121.

Ce nu se suprapune perfect cu închiderea contabilă este calendarul fiscal al impozitului pe profit propriu-zis: firmele care aplică sistemul trimestrial calculează și plătesc impozitul până la data de 25 a lunii următoare fiecărui trimestru (art. 41 alin. 1), dar definitivarea impozitului pentru întregul an se face abia la termenul declarației anuale, D101, depusă până la 25 iunie anul următor (art. 42 alin. 1). Practic, suma efectiv datorată pentru anul fiscal se confirmă și eventual se regularizează abia atunci — închiderea contabilă a lunii decembrie nu este, ea singură, momentul în care impozitul pe profit devine „definitiv".

## Ce se greșește în practică

O greșeală frecventă este să se aștepte ca închiderea contului 691 în 121 să reflecte automat impozitul corect al anului, fără a se ține cont că suma plătită trimestrial e o estimare, regularizată abia prin declarația anuală — dacă regularizarea aduce o diferență, ea trebuie înregistrată separat, în perioada corespunzătoare, nu retroactiv peste lunile deja închise. O a doua greșeală este confuzia dintre termenul de plată trimestrială (art. 41) și termenul de depunere a declarației anuale (art. 42) — cele două termene sunt distincte, iar depunerea declarației anuale nu amână obligația de plată trimestrială din cursul anului.

## Ce face iConta.eu

Motorul de calcul al închiderii lunare include soldul debitor al contului 691 (alături de toate celelalte conturi de cheltuieli) în transferul către contul 121 — calculul e disponibil ca funcție de închidere pe care contabilul o aplică la momentul potrivit, nu se postează de la sine. Calculul impozitului pe profit propriu-zis și generarea declarației D101 se fac separat, în modulul dedicat declarațiilor fiscale — inclusiv avertismentul pentru cheltuiala nedeductibilă cu impozitul pe profit, descris în ghidul dedicat contului 691. Verificați, la fiecare regularizare rezultată din declarația anuală, că suma corectă a fost și înregistrată contabil, nu doar declarată.

[iConta.eu](/)
