---
title: "Impozit pe profit la firmele cu activitate sezonieră"
description: "Codul fiscal nu prevede un regim special pentru firmele cu activitate sezonieră — se aplică regulile generale de calcul, declarare și plată a impozitului pe profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Impozit pe profit la firmele cu activitate sezonieră

Codul fiscal nu are un regim special pentru firmele cu activitate sezonieră (de exemplu, turism de vară, agrement de iarnă): anul fiscal, obligațiile de declarare și cota de impozit sunt aceleași ca pentru orice altă firmă plătitoare de impozit pe profit, indiferent cât de neuniform e distribuit profitul pe parcursul anului.

## Temeiul legal

::: ghid-temei
„Anul fiscal este anul calendaristic. Când un contribuabil se înființează sau încetează să mai existe în cursul unui an fiscal, perioada impozabilă este perioada din anul calendaristic pentru care contribuabilul a existat."
— Legea 227/2015, art. 16 alin. (1)-(2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Calculul, declararea și plata impozitului pe profit [...] se efectuează trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III. Definitivarea și plata impozitului pe profit aferent anului fiscal respectiv se efectuează până la termenul de depunere a declarației privind impozitul pe profit prevăzut la art. 42."
— Legea 227/2015, art. 41 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Consecința: o firmă cu activitate sezonieră (de exemplu, venituri concentrate în trimestrele II-III și activitate redusă restul anului) declară și, dacă e cazul, plătește impozit pe profit pentru fiecare trimestru, conform obligațiilor generale — dacă un trimestru „mort" nu generează profit impozabil, nu se datorează impozit pentru acel trimestru (declarația se depune totuși, dacă firma e obligată la sistemul trimestrial), iar impozitul se calculează cumulat de la începutul anului: pierderea unui trimestru diminuează impozitul datorat pentru trimestrele următoare cu profit, până la definitivarea anuală. Nu există un plafon special, o cotă redusă sau un termen extins doar pentru că activitatea e sezonieră.

## Ce se greșește în practică

- Se caută, fără temei, un „regim sezonier" separat în Codul fiscal — nu există; excepțiile de la sistemul trimestrial vizează categorii expres nominalizate (agricultura, art. 41 alin. 5 lit. b; instituțiile de credit, art. 41 alin. 4; firmele aflate în dizolvare cu lichidare, art. 41 alin. 1 coroborat cu art. 16 alin. 6), nu sezonalitatea activității în general.
- Se omite depunerea declarației trimestriale pentru perioadele fără activitate, presupunând greșit că absența profitului scutește și de obligația declarativă.
- Se confundă inactivitatea temporară înregistrată la registrul comerțului (care are reguli proprii, relevante mai ales pentru micro, art. 48 alin. 2^3) cu o simplă perioadă de activitate redusă specifică unui sezon, care nu declanșează niciun regim special.

## Ce face iConta.eu

iConta.eu calculează impozitul pe profit cumulat de la începutul anului fiscal, conform art. 41 — motorul D100 tratează corect cazul unui trimestru cu pierdere urmat de un trimestru cu profit, aplicând impozitul doar pe rezultatul cumulat, nu pe fiecare trimestru izolat. Această logică acoperă exact situația unei firme cu activitate sezonieră, indiferent dacă are un regim special declarat sau nu — pentru că, legal, nu există un regim special, iar calculul cumulat corect e suficient pentru orice distribuție neuniformă a profitului pe parcursul anului.

[iConta.eu](/)
