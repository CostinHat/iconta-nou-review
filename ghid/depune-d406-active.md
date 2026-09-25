---
title: "Când se depune D406 Active?"
description: "Termenul de depunere a secțiunii Active din declarația SAF-T (D406): o singură depunere anuală, la termenul situațiilor financiare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când se depune D406 Active?

Secțiunea Active a declarației SAF-T (D406) nu urmează calendarul lunar/trimestrial al restului declarației — are un regim propriu, anual, legat de un alt termen de referință: cel al situațiilor financiare.

## Temeiul legal

::: ghid-temei
„Declaraţia informativă D406 se transmite în format electronic, data-limită de transmitere fiind: - ultima zi calendaristică a lunii următoare perioadei de raportare, respectiv luna/trimestrul calendaristic, după caz, pentru alte informaţii decât cele privind secţiunile «Stocuri» şi «Active»; - la termenul de depunere a situaţiilor financiare aferente exerciţiului financiar, în cazul secţiunii «Active»; - la termenul stabilit de organul fiscal central, care nu poate fi mai mic de 30 de zile calendaristice de la data solicitării, în cazul secţiunii «Stocuri».
Informaţiile privind «Activele» din cadrul Declaraţiei informative D406 sunt întocmite la nivelul anului financiar aplicat de către contribuabili şi transmise printr-o singură depunere, respectiv o singură raportare a Declaraţiei informative D406, până la data depunerii situaţiilor financiare aferente exerciţiului financiar la care se referă.
Declaraţia informativă D406 pentru «Active» se poate transmite ca o declaraţie independentă, nefiind necesară introducerea tuturor secţiunilor/subsecţiunilor dintr-o Declaraţie informativă D406, ci doar a zonelor indicate ca fiind obligatorii pentru transmiterea acestui tip de informaţie."
— OPANAF 1783/2021 (SAF-T D406), Anexa 4, pct. 1 și pct. 7-8 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Trei lucruri rezultă direct din text:

- Secțiunea **Active** are termenul **situațiilor financiare anuale**, nu ultima zi a lunii următoare ca restul D406.
- E o **singură depunere pe an**, la nivelul întregului an financiar — nu se repetă lunar/trimestrial ca secțiunile de TVA/jurnal.
- Poate fi depusă ca **declarație independentă** — nu e nevoie să se completeze restul secțiunilor D406 (Header, GeneralLedgerEntries etc.) doar ca să se transmită Active; legea permite explicit un fișier de sine stătător, cu doar zonele obligatorii pentru Active.

## Ce se greșește în practică

- Se aplică termenul lunar al declarației principale D406 (ultima zi a lunii următoare) și secțiunii Active, deși legea îi dă un termen separat, legat de situațiile financiare.
- Se așteaptă ca secțiunea Active să se depună o dată cu fiecare D406 lunar/trimestrial, ceea ce ar produce depuneri redundante — legea cere o singură raportare anuală.
- Se presupune că Active trebuie completată în cadrul unui AuditFile complet, cu toate celelalte secțiuni populate — pct. 8 permite explicit depunerea ei separată.

## Ce face iConta.eu

Generatorul secțiunii Active (`core/d406_active.py`) calculează corect motorul de amortizare pe patru metode (liniară/degresivă/accelerată/superaccelerată, verificat câmp cu câmp cu structura oficială `Asset/Valuations`) și produce fragmentul XML `<Assets>` pornind din registrul de mijloace fixe al firmei. La data acestui ghid, ruta care expune acest calcul (`GET /tenants/{id}/d406-active`) există și funcționează, dar întoarce **doar fragmentul `<Assets>`**, nu un `<AuditFile>` complet, depunibil ca atare la ANAF — iar acest fragment nu are încă un ecran propriu în aplicație (comentariul din cod marchează explicit ruta ca „fără UI încă, păstrat deliberat"). Generatorul fișierului complet există la nivel de motor și a fost probat ca valid pe validatorul oficial DUK, dar nu e conectat la nicio rută accesibilă azi din interfață. Practic: calculul de amortizare pentru Active e corect și verificabil, dar depunerea propriu-zisă a declarației Active nu e încă disponibilă din ecranele aplicației.

[iConta.eu](/)
