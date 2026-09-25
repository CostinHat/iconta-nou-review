---
title: "Greșeala de a nu înregistra concediul medical corect"
description: "De ce indemnizația de concediu medical trebuie calculată pe baza veniturilor efectiv plătite în ultimele 6 luni, nu pe un recalcul retroactiv, potrivit OUG 158/2005."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Greșeala de a nu înregistra concediul medical corect

Cea mai frecventă greșeală la înregistrarea unui concediu medical nu e calculul propriu-zis al zilelor sau al cotei de indemnizație, ci baza de calcul: mulți contabili recalculează retroactiv veniturile ultimelor 6 luni cu parametrii de azi, în loc să folosească ce a fost efectiv plătit salariatului în acele luni.

## Temeiul legal

::: ghid-temei
„(1) Pentru persoanele prevăzute la art. 1 alin. (1) lit. A și B, baza de calcul al indemnizațiilor prevăzute la art. 2 se determină ca medie a veniturilor brute lunare din ultimele 6 luni din cele 12 luni din care se constituie stagiul de asigurare, până la limita a 12 salarii minime brute pe țară lunar, pe baza cărora se calculează contribuția asiguratorie pentru muncă."
— OUG 158/2005, art. 10 alin. (1) (sursă: anaf_surse/oug_158_2005_consolidat.txt)
:::

Ce înseamnă corect, pas cu pas:

- Baza se calculează ca **medie a veniturilor din ultimele 6 luni anterioare** lunii în care începe concediul medical, raportată la zilele lucrătoare din acele luni.
- Media se face pe **ce a primit efectiv salariatul** în acele 6 luni — sumele din statele de plată deja emise — nu pe o reconstituire cu cota sau salariul minim valabile azi.
- Dacă între timp s-a schimbat o cotă de contribuție sau salariul minim, un recalcul „la zi" al lunilor anterioare ar produce venituri care nu au existat niciodată efectiv, deci o bază de calcul greșită.
- Pentru lunile pentru care nu există încă un stat de plată emis (de exemplu la un salariat foarte nou), se folosește recalculul — dar aceste luni trebuie numărate separat de cele emise, ca să nu se amestece tacit două tipuri de cifre în aceeași medie.

## Ce se greșește în practică

- Se recalculează toate cele 6 luni anterioare cu parametrii fiscali curenți, în loc să se preia sumele deja plătite — greșeala tipică apare când s-a schimbat salariul minim brut sau o cotă de contribuție între timp.
- Se amestecă, fără să se marcheze separat, luni cu state de plată emise și luni recalculate, obținând o medie ambiguă, imposibil de reconstituit ulterior din ce anume a rezultat cifra finală.
- Se calculează baza pe **zile calendaristice**, nu pe **zile lucrătoare** — normele de aplicare a OUG 158/2005 cer raportarea la zilele lucrătoare din lunile respective, nu la numărul total de zile din lună.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează baza indemnizației de concediu medical exact pe principiul corect: preferă cifrele din statele de plată deja **emise** pentru fiecare din cele 6 luni anterioare, iar pentru lunile neemise folosește recalculul — dar le numără și le raportează **separat**, astfel încât contabilul să vadă din ce anume s-a compus media (`core/baza_cm.py`). Motivația din codul aplicației e explicită: „ce s-a plătit efectiv e un fapt" — un recalcul „la zi" ar produce o bază de calcul care nu corespunde niciunei realități efectiv plătite salariatului.

[iConta.eu](/)
