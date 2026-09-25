---
title: "Ce informații trebuie să conțină SAF-T Active?"
description: "Datele obligatorii din secțiunea 'Active' a fișierului standard de control fiscal D406 și termenul specific de transmitere, potrivit OPANAF 1783/2021."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce informații trebuie să conțină SAF-T Active?

Secțiunea „Active" din SAF-T (D406) e cea mai apropiată de un registru de mijloace fixe transmis electronic către ANAF — și, la fel ca secțiunea „Stocuri", are propriul termen de depunere, diferit de restul declarației.

## Temeiul legal

::: ghid-temei
„Assets (Active): Conține detalii cu privire la active, precum ID-ul unic de inventar al activului, contul analitic în care este înregistrat activul, descrierea activului, furnizorul activului, data achiziției și data punerii în funcțiune, precum și informații contabile cu privire la evaluarea activului (de exemplu, costurile totale de achiziție/producție la începutul și finalul perioadei selectate pentru raportare, valoarea costului cu capitalizările, perioada de viață a activului în ani/luni, valori contabile asociate transferurilor de active/ieșirilor de active, metoda de amortizare, valoarea amortizării din perioada selectată, reevaluări etc.)."
— Ordinul președintelui A.N.A.F. nr. 1.783/2021, Instrucțiuni de completare D406, secțiunea Assets (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

- Fișierul trebuie să identifice fiecare mijloc fix printr-un **ID unic de inventar** și contul analitic în care e înregistrat, plus o descriere clară a activului și furnizorul de la care a fost achiziționat.
- Se raportează atât **data achiziției**, cât și **data punerii în funcțiune** — două momente distincte, relevante pentru calculul corect al amortizării.
- Partea contabilă e detaliată: cost de achiziție/producție la început și sfârșit de perioadă, capitalizări ulterioare, durata de viață utilă (în ani/luni), **metoda de amortizare** folosită, valoarea amortizării din perioada raportată, reevaluări și ieșiri/transferuri de active.
- Termenul de depunere e special: „la termenul de depunere a situațiilor financiare aferente exercițiului financiar, în cazul secțiunii «Active»" — deci o singură transmitere pe an, corelată cu bilanțul, nu lunar/trimestrial ca restul D406 (aceeași sursă, pct. termene).
- Secțiunea „Active" se poate transmite ca declarație independentă, fără a mai completa toate celelalte secțiuni ale D406 (pct. 8 din aceleași instrucțiuni).

## Ce se greșește în practică

- Se transmite secțiunea „Active" lunar sau trimestrial, din obișnuință, deși termenul legal e anual, corelat cu depunerea situațiilor financiare.
- Se omite data punerii în funcțiune (distinctă de data achiziției), deși amortizarea fiscală pornește de la aceasta, nu de la data facturii de achiziție.
- Se raportează costul de achiziție inițial fără actualizare pentru capitalizări ulterioare (modernizări, investiții adiționale asupra aceluiași activ).
- Nu se corelează metoda de amortizare raportată în SAF-T cu cea folosită efectiv în calculul fiscal din registrul de amortizare, generând o discrepanță ușor de detectat la o verificare încrucișată.

## Ce face iConta.eu

iConta.eu are un modul dedicat exact pentru această secțiune (`d406_active.py`), care calculează amortizarea pe metode (liniară, degresivă, neliniară), urmărește categoria activului și metodele permise pentru ea, ține evidența reevaluărilor și generează direct structura XML cerută de ANAF (`xml_asset`, `xml_assets`, `xml_d406_anual_active`). Datele de amortizare folosite pentru SAF-T Active sunt aceleași cu cele din registrul intern de mijloace fixe al aplicației, deci nu există un calcul „paralel" doar pentru declarație.

[iConta.eu](/)
