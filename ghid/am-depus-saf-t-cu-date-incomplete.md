---
title: Am depus SAF-T cu date incomplete — ce fac?
description: Se depune o declarație rectificativă cu fișierul SAF-T corectat integral — D406 nu permite corecții parțiale, prin transmiterea selectivă a doar a înregistrărilor sau câmpurilor greșite.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Am depus SAF-T cu date incomplete — ce fac?

Descoperirea, după depunere, că declarația D406 conținea date incomplete sau greșite este o situație frecventă — de exemplu un partener fără CUI corect completat, sau o linie de factură lipsă. D406 tratează corectarea diferit față de alte declarații: nu există concept de "amendament parțial".

## Temeiul legal

::: ghid-temei
"6. În situaţia în care contribuabilul constată anumite erori în declaraţia depusă iniţial,
acesta poate depune declaraţii rectificative.
...
11. Pentru declaraţia informativă D406 transmisă cu erori identificate de Agenţia Naţională
de Administrare Fiscală şi pentru care a fost comunicată recipisa ce le semnalează,
contribuabilul retransmite integral Declaraţia informativă D406, care trebuie să cuprindă
fişierul SAF-T corectat.
12. Nu este admisă transmiterea unor corecţii parţiale prin transmiterea selectivă a
înregistrărilor sau câmpurilor corectate pentru Declaraţia informativă D406 anterior
transmisă şi pentru care au fost primite recipise ce semnalau erori."
(opanaf_1783_2021_saft_d406.txt, Anexa 4, pct. 6, 11, 12)
:::

## Regula: retransmitere integrală, nu corecție parțială

Fie că eroarea a fost descoperită de contribuabil singur, fie că a fost semnalată de ANAF prin recipisă, procedura este aceeași: se depune o declarație rectificativă care conține **integral** fișierul SAF-T corectat, nu doar înregistrările sau câmpurile care erau greșite.

::: ghid-exemplu
Într-un D406 depus pentru august 2026, un client a fost raportat cu un cod de identificare greșit (`00`+CUI în loc de `03`+CNP). Corectarea corectă nu înseamnă retransmiterea doar a acelui client — se generează din nou fișierul SAF-T complet pentru august 2026, cu toate secțiunile (Header, MasterFiles, GeneralLedgerEntries, SourceDocuments), de data aceasta cu identificatorul de client corectat, și se depune ca rectificativă.
:::

Această regulă are o implicație practică importantă pentru automatizare: motorul de generare trebuie rulat din nou, pe întreaga perioadă de raportare, nu doar pentru datele modificate — orice discrepanță reziduală în restul fișierului (conturi, facturi, plăți neschimbate) trebuie să rămână corectă și completă în noua versiune retransmisă.

## Ce se greșește în practică

- Se încearcă transmiterea doar a înregistrărilor corectate, considerând procesul similar unei declarații rectificative "pe diferență" — D406 nu permite acest lucru explicit.
- Se retransmite fișierul fără a regenera toate secțiunile din datele curente ale contabilității, riscând să se piardă alte corecturi intermediare deja operate în contabilitate.
- Se confundă corectarea unei erori proprii (descoperite de contribuabil) cu retransmiterea impusă de o recipisă ANAF — ambele urmează aceeași regulă de retransmitere integrală, dar termenele de reacție pot diferi.
- Nu se rulează din nou validarea oficială (DUKIntegrator) pe fișierul rectificat înainte de retransmitere, presupunând că singura corecție necesară era cea identificată.

## Ce face iConta.eu

Fluxul de generare al aplicației (`pull → construieste → valideaza → build_xml`) produce de fiecare dată fișierul SAF-T complet pentru perioada aleasă, pe baza datelor curente din contabilitate — ceea ce se potrivește exact cu cerința legală de retransmitere integrală: după corectarea datei greșite (ex. cod de partener, cont, linie de factură) direct în contabilitate, contabilul rulează din nou generarea pentru aceeași perioadă și obține fișierul complet, corectat, pregătit pentru retransmitere ca declarație rectificativă. Ca la orice generare, pasul de validare finală rămâne, în continuare, validatorul oficial ANAF (DUKIntegrator), care trebuie rulat din nou pe fișierul rectificat înainte de depunere — validarea structurală internă a aplicației nu îl înlocuiește.

[iConta.eu](/)
