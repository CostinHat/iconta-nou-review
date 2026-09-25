---
title: "SAF-T pentru firmele din grup: consolidare"
description: "De ce fișierul SAF-T (D406) se depune per entitate fiscală și nu prevede o raportare consolidată la nivel de grup de firme."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# SAF-T pentru firmele din grup: consolidare

O întrebare frecventă la grupurile de firme: se poate depune un singur fișier SAF-T pentru tot grupul, consolidat? Răspunsul scurt e nu — structura oficială a declarației D406 e construită pe entitate fiscală (cod de identificare fiscală), fără un mecanism de consolidare la nivel de grup.

## Temeiul legal

::: ghid-temei
„Header (Antet) - Conţine informaţii generale despre fişier, inclusiv numele software-ului care l-a produs; compania în numele căreia este depus SAF-T."
— OPANAF 1783/2021, Anexa privind procedura de depunere a Declarației informative D406, secțiunea 1 Header din structura SAF-T (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

**Limitare asumată onest:** corpusul de surse verificate pentru acest ghid nu conține, în textele disponibile ale OPANAF 1783/2021 sau OPANAF 407/2025, o prevedere explicită care să interzică sau să permită o depunere consolidată la nivel de grup — dar structura fișierului, organizată pe secțiuni de „Header" cu un singur identificator fiscal (`RegistrationNumber`) și pe balanță/jurnale ale unei singure entități, arată clar că fișierul e conceput pentru o singură persoană juridică, nu pentru un grup.

Ce rezultă practic pentru un grup de firme:

- Fiecare firmă din grup, dacă intră în categoria contribuabililor obligați la SAF-T, depune propriul fișier D406, cu propriile solduri, jurnale și partenerii ei — nu există un fișier unic „de grup".
- Tranzacțiile intra-grup (facturi între firmele aceluiași grup) apar în fișierul SAF-T al fiecărei entități separat, ca operațiuni cu partenerul respectiv (identificat prin codul lui fiscal), nu eliminate ca la o consolidare contabilă de grup.
- O eventuală agregare a datelor din mai multe firme ale grupului, pentru raportare de management sau analiză, rămâne un proces separat, în afara declarației SAF-T oficiale.

## Ce se greșește în practică

- Se presupune că un grup de firme poate depune un singur SAF-T consolidat, ca la situațiile financiare consolidate — structura oficială a D406 nu prevede acest lucru.
- Se elimină manual, din fișierul unei firme, tranzacțiile cu firme afiliate din grup, ca la o consolidare contabilă — ceea ce ar denatura fișierul SAF-T al entității respective, care trebuie să reflecte contabilitatea ei proprie, neconsolidată.

## Ce face iConta.eu

Modulul SAF-T din iConta.eu (`core/d406.py`) generează fișierul D406 separat pentru fiecare firmă administrată în aplicație, pe baza contabilității proprii a acesteia. Aplicația nu oferă o funcție de consolidare a mai multor fișiere SAF-T la nivel de grup — fiecare entitate își generează și depune propria declarație.

[iConta.eu](/)
