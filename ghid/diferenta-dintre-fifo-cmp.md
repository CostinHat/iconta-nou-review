---
title: "Care este diferența dintre FIFO și CMP?"
description: "Diferența legală dintre metoda FIFO și metoda costului mediu ponderat (CMP) pentru evaluarea stocurilor, și de ce iConta.eu folosește doar CMP."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Care este diferența dintre FIFO și CMP?

FIFO și CMP sunt două dintre cele trei metode de evaluare a stocurilor recunoscute de legislația contabilă românească, iar diferența dintre ele nu ține doar de denumire — duc la valori diferite ale mărfii ieșite din gestiune și, implicit, la cheltuieli diferite recunoscute în contabilitate. Iată exact ce spune legea despre fiecare, și ce alege să implementeze iConta.eu.

## Temeiul legal

::: ghid-temei
„(2) Metoda «costului mediu ponderat» (CMP) presupune calcularea costului fiecărui element pe baza mediei ponderate a costurilor elementelor similare aflate în stoc la începutul perioadei și a costului elementelor similare produse sau cumpărate în timpul perioadei. Media poate fi calculată periodic sau după fiecare recepție. [...]
(3) Potrivit metodei «primul intrat-primul ieșit» (FIFO), bunurile ieșite din gestiune se evaluează la costul de achiziție sau de producție al primei intrări (lot). [...]"
— OMFP 1802/2014, pct. 96 alin. (2)-(3) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- **CMP** amestecă valoric toate loturile aflate în stoc într-un singur cost mediu, ponderat cu cantitățile fiecărui lot; costul se recalculează periodic sau după fiecare recepție (vezi alin. 2).
- **FIFO** nu amestecă loturile — fiecare ieșire „consumă" întâi cantitatea din lotul cel mai vechi rămas în stoc, la costul lui de achiziție, și trece la lotul următor abia după epuizarea celui curent.
- Diferența practică: în perioade cu prețuri de achiziție în creștere, FIFO tinde să lase în stoc valori mai apropiate de prețurile curente (loturile vechi, mai ieftine, ies primele), în timp ce CMP „netezește" variațiile de preț printr-o medie.
- Legea nu obligă o firmă la una dintre metode — art. 96 alin. (1) le prezintă pe toate trei (CMP, FIFO, LIFO) ca opțiuni egale de politică contabilă.

## Ce se greșește în practică

- Se crede că CMP și FIFO ar da mereu rezultate apropiate — în realitate, la volatilitate mare a prețurilor de achiziție, diferența de valoare a stocului final poate fi semnificativă.
- Se confundă FIFO ca metodă de evaluare contabilă a stocurilor cu principiul „primul intrat, primul ieșit" folosit uneori doar operațional (ex. rotația fizică a mărfii pe raft), fără nicio legătură cu evidența valorică.
- Se presupune că, odată aleasă o metodă, aceasta se poate schimba oricând fără nicio consecință în raportare — schimbarea unei politici contabile are propriile reguli, distincte de simpla alegere inițială.

## Ce face iConta.eu

Pentru gestiunea cantitativ-valorică, iConta.eu aplică **exclusiv metoda CMP** (`core/stocuri_cv.py`) — motorul de calcul actualizează costul mediu ponderat la fiecare intrare și evaluează toate ieșirile la acest cost curent. Metoda FIFO **nu este implementată nicăieri în modulul de stocuri** al aplicației; termenul „FIFO" apare în cod doar în alte module de alocare a plăților/documentelor în ordinea vechimii (de exemplu `core/reconciliere.py`, la potrivirea extraselor bancare cu facturile deschise, sau `core/dividende_curs.py`, la atribuirea plăților de dividende pe distribuirile deschise) — algoritmi complet diferiți, fără nicio legătură cu evaluarea stocurilor.

Așadar, dacă acest ghid explică diferența conceptuală dintre FIFO și CMP din perspectivă strict legală, precizarea onestă e că, în iConta.eu, alegerea nu există în practică: aplicația oferă doar evaluarea la CMP pentru stocurile cantitativ-valorice, nu ambele metode ca opțiuni configurabile.

[iConta.eu](/)
