---
title: "Amortizarea mijloacelor fixe în valută: cursul de schimb"
description: "Ce curs de schimb se folosește pentru un mijloc fix achiziționat în valută și cum se raportează el în situațiile financiare, potrivit reglementărilor contabile."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Amortizarea mijloacelor fixe în valută: cursul de schimb

Un mijloc fix cumpărat în valută (de exemplu, un utilaj importat, achitat în euro) se înregistrează în contabilitate la cursul de schimb valabil la data tranzacției și **rămâne la acel curs** pe toată durata sa de utilizare — spre deosebire de elementele monetare (disponibilități, creanțe, datorii în valută), care se reevaluează la fiecare închidere de exercițiu. Regula are efect direct și asupra bazei de calcul a amortizării.

## Temeiul legal

::: ghid-temei
„La fiecare dată a bilanțului: [...] c) Elementele nemonetare achiziționate cu plata în valută și înregistrate la cost istoric (imobilizări, stocuri) trebuie prezentate în situațiile financiare anuale utilizând cursul de schimb valutar de la data efectuării tranzacției."
— OMFP nr. 1.802/2014 pentru aprobarea reglementărilor contabile, pct. 94 lit. c) (sursă: anaf_surse/omfp_1802_2014.txt)
:::

Din acest text rezultă consecința practică pentru amortizare: dacă mijlocul fix nu este reevaluat (rămâne la cost istoric), valoarea lui în lei — deci și baza de amortizare — se stabilește o singură dată, la cursul BNR din ziua achiziției, și nu se recalculează ulterior în funcție de fluctuațiile cursului valutar.

Situația diferă doar dacă firma a optat pentru **reevaluarea** mijlocului fix (la valoare justă), caz reglementat separat:

::: ghid-temei
„d) Elementele nemonetare achiziționate cu plata în valută și înregistrate la valoarea justă (de exemplu, imobilizările corporale reevaluate) trebuie prezentate în situațiile financiare anuale la această valoare."
— OMFP nr. 1.802/2014 pentru aprobarea reglementărilor contabile, pct. 94 lit. d) (sursă: anaf_surse/omfp_1802_2014.txt)
:::

În acest caz, valoarea reevaluată (stabilită prin raport de evaluare, în lei) devine noua bază de amortizare, indiferent de moneda inițială de achiziție.

Din perspectivă fiscală, Codul fiscal (art. 28) stabilește regulile de amortizare fiscală (metoda liniară, degresivă, accelerată, cotele aplicabile), dar baza de pornire rămâne **valoarea fiscală de la data intrării în patrimoniu** — care, pentru un mijloc fix cumpărat în valută, se calculează exact conform principiului contabil de mai sus: la cursul din data tranzacției.

## Ce se greșește în practică

- Se recalculează greșit valoarea de amortizare a unui mijloc fix la cursul de schimb valabil la data bilanțului (31 decembrie), tratându-l ca pe un element monetar — regula se aplică doar creanțelor/datoriilor în valută, nu imobilizărilor la cost istoric.
- Se folosește cursul de la data facturii furnizorului extern, deși achiziția și plata pot avea date diferite — cursul relevant este cel de la data **efectuării tranzacției** (de regulă, data recepției/intrării în patrimoniu, conform politicii contabile a firmei).
- Se confundă diferențele de curs valutar generate de datoria față de furnizorul extern (care rămân monetare până la plată și se reevaluează) cu valoarea mijlocului fix în sine (nemonetară, fixată la cursul istoric).
- Se omite documentarea clară a cursului folosit la înregistrarea inițială, ceea ce complică verificarea ulterioară a bazei de amortizare la un control fiscal.

## Ce face iConta.eu

iConta.eu are un modul dedicat de amortizare fiscală a mijloacelor fixe (folosit și pentru registrul de active din declarația D406/SAF-T), care calculează automat amortizarea lunară și anuală după metodele liniară, degresivă și accelerată, conform regulilor din art. 28 din Codul fiscal. Modulul **nu tratează însă distinct conversia valutară** — valoarea de intrare a unui mijloc fix achiziționat în valută trebuie introdusă în aplicație deja convertită în lei, la cursul din data tranzacției, conform regulii descrise mai sus; aplicația nu recalculează și nu verifică independent acest curs istoric.

[iConta.eu](/)
