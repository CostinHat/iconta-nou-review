---
title: "Cum reconciliez rezultatul IFRS cu baza fiscală"
description: "Ce spune Codul fiscal despre contribuabilii care aplică Standardele Internaționale de Raportare Financiară — și diferența dintre rezultatul contabil IFRS și rezultatul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum reconciliez rezultatul IFRS cu baza fiscală

Codul fiscal nu conține un capitol unic „reconciliere IFRS–fiscal" — recunoaște însă explicit, în mai multe articole, situația contribuabililor care aplică reglementările contabile conforme cu Standardele Internaționale de Raportare Financiară (IFRS) și le tratează diferit de cei pe reglementările naționale (OMFP 1802/2014), acolo unde diferența contează efectiv pentru calculul impozitului.

## Temeiul legal

::: ghid-temei
„În cazul contribuabililor care aplică reglementările contabile conforme cu Standardele internaționale de raportare financiară, pentru activele imobilizate deținute pentru activitatea proprie, transferate în categoria activelor imobilizate deținute în vederea vânzării și reclasificate în categoria activelor imobilizate deținute pentru activitatea proprie, valoarea fiscală rămasă neamortizată este valoarea fiscală dinaintea reclasificării ca active imobilizate deținute în vederea vânzării. Durata de amortizare este durata normală de utilizare rămasă [...]."
— Legea nr. 227/2015, art. 28 alin. (26) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„În aplicarea prevederilor alin. (4) lit. e), pentru determinarea ponderii veniturilor neimpozabile în totalul veniturilor, contribuabilii care aplică reglementările contabile conforme cu Standardele internaționale de raportare financiară și care înregistrează evaluarea titlurilor de participare la valoare justă prin alte elemente ale rezultatului global [...] iau în calcul și sumele reprezentând diferențe din evaluare/reevaluare care se regăsesc în creditul conturilor de rezerve ca urmare a vânzării/cesionării titlurilor de participare."
— Legea nr. 227/2015, art. 25 alin. (12^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă, cu limita marcată explicit:

- Codul fiscal **nu tratează separat** rezultatul contabil obținut sub IFRS de rezultatul fiscal ca noțiuni globale — regula de bază rămâne aceeași pentru toți contribuabilii: rezultatul fiscal pornește de la rezultatul contabil (profitul/pierderea din situațiile financiare, întocmite fie potrivit OMFP 1802/2014, fie potrivit IFRS, după caz), ajustat cu veniturile neimpozabile, cheltuielile nedeductibile și elementele similare veniturilor/cheltuielilor, conform regulilor generale ale titlului II.
- Legea intervine punctual, doar acolo unde metodologia IFRS produce un rezultat structural diferit de reglementările naționale și care ar denatura calculul fiscal dacă nu ar fi corectat explicit: reclasificarea activelor deținute pentru vânzare (art. 28 alin. (26)) și evaluarea titlurilor de participare la valoare justă prin alte elemente ale rezultatului global (art. 25 alin. (12^1)) sunt exemplele identificate în sursele consultate.
- Nu am găsit, în sursele locale disponibile, un tabel sau o listă exhaustivă a tuturor ajustărilor IFRS-fiscal — pentru fiecare situație specifică (leasing IFRS 16, recunoașterea veniturilor IFRS 15 etc.), contribuabilul trebuie să identifice punctual dacă și unde Codul fiscal prevede o regulă distinctă pentru cei pe IFRS, altfel se aplică regula generală de calcul a rezultatului fiscal, comună tuturor contribuabililor.
- Recomandăm, pentru orice diferență semnificativă între tratamentul IFRS și cel din reglementările naționale, verificarea punctuală a articolului relevant din titlul II al Codului fiscal, nu presupunerea unei reguli generale de „ajustare IFRS".

## Ce se greșește în practică

- Se presupune că există un mecanism unic, generic, de „reconciliere IFRS" aplicabil oricărei diferențe de tratament contabil — Codul fiscal intervine doar punctual, în situațiile enumerate expres de lege.
- Se ignoră prevederile speciale pentru contribuabilii IFRS (de exemplu art. 28 alin. (26) sau art. 25 alin. (12^1)), aplicând regulile generale valabile pentru contabilitatea pe OMFP 1802/2014, deși legea prevede explicit un tratament diferit.
- Se tratează orice diferență temporară recunoscută sub IFRS (de exemplu din leasing) ca „automat deductibilă sau impozabilă", fără verificarea articolului specific din Codul fiscal care ar putea condiționa sau limita acel tratament.

## Ce face iConta.eu

iConta.eu identifică baza contabilă a firmei prin câmpul „TaxAccountingBasis" folosit la generarea SAF-T (valorile posibile includ explicit „IFRS", alături de „A" — reglementări naționale — și celelalte baze contabile recunoscute), vizibil în modulul de raportare D406 (`core/d406.py`). Aplicația nu automatizează însă, la data acestui ghid, ajustările fiscale specifice contribuabililor IFRS prevăzute punctual în Codul fiscal (de exemplu la art. 28 alin. (26) sau art. 25 alin. (12^1)) — acestea rămân calcule pe care contabilul le face separat, în funcție de situația concretă a firmei.

[iConta.eu](/)
