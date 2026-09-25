---
title: "Cum se calculează media zilnică pentru concediul medical?"
description: "Formula legală a mediei zilnice folosite la calculul indemnizației de concediu medical — baza pe 6 luni, plafonul de 12 salarii minime — și cum o calculează efectiv iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează media zilnică pentru concediul medical?

Media zilnică e cifra de la care pornește tot calculul indemnizației de concediu medical: se determină o singură dată, din veniturile ultimelor 6 luni, iar peste ea se aplică ulterior procentul specific fiecărui tip de concediu. Legea nu ia însă în calcul orice venit — există un plafon lunar peste care sumele nu contează.

## Temeiul legal

::: ghid-temei
„Pentru persoanele prevăzute la art. 1 alin. (1) lit. A și B, baza de calcul al indemnizațiilor prevăzute la art. 2 se determină ca medie a veniturilor brute lunare din ultimele 6 luni din cele 12 luni din care se constituie stagiul de asigurare, până la limita a 12 salarii minime brute pe țară lunar, pe baza cărora se calculează contribuția asiguratorie pentru muncă."

„Din duratele de acordare a concediilor medicale, exprimate în zile calendaristice, se plătesc zilele lucrătoare."
— OUG 158/2005, art. 10 alin. (1) și alin. (8) (sursă: anaf_surse/oug_158_2005_consolidat.txt)
:::

Formula rezultă direct din text:

- Se adună veniturile brute lunare din **ultimele 6 luni** din cele 12 în care s-a constituit stagiul de asigurare — dar **fiecare lună**, plafonată individual la **12 salarii minime brute pe țară** (nu suma totală pe 6 luni, ci fiecare lună în parte, înainte de a fi adunată).
- Se adună și numărul de **zile lucrătoare** din aceleași 6 luni.
- **Media zilnică = suma veniturilor plafonate / suma zilelor lucrătoare.**
- Peste această medie zilnică se aplică ulterior procentul specific certificatului (55/65/75% pentru boală obișnuită, alte procente fixe pentru celelalte coduri) și numărul de zile plătite.

## Ce se greșește în practică

- Se calculează media din veniturile brute reale, fără plafonare, la salariații cu venituri peste 12 salarii minime brute pe lună — media rezultă mai mare decât permite legea.
- Se împarte suma veniturilor la 6 (numărul de luni) în loc de suma zilelor lucrătoare din cele 6 luni — cele două cifre coincid doar întâmplător.
- Se folosesc, pentru cele 6 luni, veniturile din statele de plată nedefinitive, fără să se recalculeze ulterior media dacă acele state se corectează.

## Ce face iConta.eu

Motorul de calcul (`core/salarizare.py`, funcția `calcul_cm`) aplică formula de mai sus — media zilnică din veniturile și zilele lucrătoare pe 6 luni — odată ce cele două cifre agregate sunt disponibile. Există și un modul (`core/baza_cm.py`) care adună automat veniturile și zilele lucrătoare din ultimele 6 luni pe baza statelor de plată emise (cu recalcul explicit pentru lunile încă neemise), dar el e conectat astăzi doar la un API intern (`/tenants/{tenant_id}/calcul-cm`), fără ecran propriu în aplicație.

O limitare reală, verificată în cod: ecranul real de introducere a certificatului (secțiunea Concedii din fișa salariatului) nu folosește deloc `core/baza_cm.py` — contabilul introduce el însuși suma veniturilor și numărul de zile lucrătoare pe cele 6 luni, ca sumă agregată, nu defalcate pe lună, iar aplicația nu recalculează sau confruntă acea sumă cu statele de plată deja emise. Din același motiv, plafonarea la 12 salarii minime brute **pe fiecare lună**, deși motorul o suportă tehnic printr-un parametru opțional, nu se activează în practică — nimic din ecranul folosit efectiv nu trimite veniturile defalcate pe lună. La un salariat cu venituri lunare peste plafonul legal, media zilnică (și, în consecință, indemnizația) calculată de iConta.eu poate ieși mai mare decât permite legea.

[iConta.eu](/)
