---
title: "Cum verific D394 cu balanța contabilă?"
description: "De ce declarația informativă D394 trebuie să corespundă cu operațiunile înregistrate în contabilitate și cum se face, în principiu, această verificare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific D394 cu balanța contabilă?

D394 este declarația informativă prin care persoanele înregistrate în scopuri de TVA raportează livrările, prestările și achizițiile efectuate pe teritoriul național. Fiindcă se construiește din aceleași facturi care alimentează și contabilitatea, orice divergență între D394 și balanța de verificare (rulaje pe conturile de TVA și venituri/cheltuieli) e un semnal că undeva o factură a fost omisă, dublată sau clasificată greșit.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ."
— Legea contabilității nr. 82/1991, art. 6 alin. (1) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Notă onestă: acest text nu vorbește explicit despre D394, ci despre principiul general al înregistrării în contabilitate pe bază de document justificativ. Îl citez pentru că e exact fundamentul verificării: dacă D394 și balanța pornesc de la aceleași facturi (documente justificative), diferențele dintre ele nu pot fi decât erori de preluare sau de clasificare — nu diferențe „normale".

- D394 se depune conform modelului aprobat prin ORDIN nr. 3769/2015 — „declararea livrărilor/prestărilor și achizițiilor efectuate pe teritoriul național de persoanele înregistrate în scopuri de TVA" (Legea 207/2015, referință la formularul D394).
- În principiu, verificarea presupune confruntarea a două surse independente: totalul livrărilor/achizițiilor raportate în D394 pe cotă de TVA vs. rulajele conturilor de TVA colectată/deductibilă și de venituri/cheltuieli din balanță.
- Diferența nu trebuie să fie neapărat zero: D394 exclude anumite operațiuni (de exemplu cele intracomunitare, cota 0% sau scutite fără drept de deducere), deci o comparație brută, linie cu linie, poate da divergențe „false" dacă nu se ține cont de aceste excluderi.

## Ce se greșește în practică

- Se compară direct totalul din D394 cu rulajul brut de TVA din balanță, fără să se scadă operațiunile pe care D394 nu le raportează (intracomunitare, cotă 0, scutite).
- Se presupune că D394 și decontul de TVA (D300) trebuie să fie identice ca sumă — de fapt D300 e TVA totală, iar D394 e doar un subset raportabil.
- Nu se verifică periodic corespondența, ci doar la depunere, iar erorile acumulate pe mai multe luni devin greu de identificat.
- Se ignoră facturile sosite cu întârziere sau corectate, care pot apărea într-o perioadă în D394 și în alta în balanță.

## Ce face iConta.eu

iConta.eu **are un mecanism dedicat de verificare independentă a D394**, separat de motorul care generează declarația: modulul de reconciliere recalculează totalurile pe cotă de TVA (livrări și achiziții) direct din liniile brute de facturi, folosind interogări proprii, independente de codul generatorului declarației, apoi confruntă rezultatul cu ce a fost efectiv generat. Orice divergență blochează procesul cu o eroare explicită, care indică ambele valori — logica internă e explicit „a doua cale", ca să nu repete aceleași eventuale erori ale generatorului. Aceasta e o verificare automată, internă aplicației, distinctă de o comparație manuală D394-vs-balanță făcută de contabil.

[iConta.eu](/)
