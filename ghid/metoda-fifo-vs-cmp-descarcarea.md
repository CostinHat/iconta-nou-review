---
title: "Metoda FIFO vs CMP la descărcarea de gestiune"
description: "Cum evaluează legea marfa ieșită din gestiune prin FIFO față de CMP, și ce metodă folosește efectiv iConta.eu la descărcarea de gestiune."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Metoda FIFO vs CMP la descărcarea de gestiune

Descărcarea de gestiune — momentul în care o marfă sau materie primă iese din stoc și trece pe cheltuială sau pe costul vânzării — se face diferit după metoda de evaluare aleasă. FIFO și CMP dau, de regulă, valori diferite pentru aceeași ieșire, mai ales când prețurile de achiziție s-au schimbat între loturi.

## Temeiul legal

::: ghid-temei
„(2) Metoda «costului mediu ponderat» (CMP) presupune calcularea costului fiecărui element pe baza mediei ponderate a costurilor elementelor similare aflate în stoc la începutul perioadei și a costului elementelor similare produse sau cumpărate în timpul perioadei. [...]
(3) Potrivit metodei «primul intrat-primul ieșit» (FIFO), bunurile ieșite din gestiune se evaluează la costul de achiziție sau de producție al primei intrări (lot). [...]"
— OMFP 1802/2014, pct. 96 alin. (2)-(3) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- La descărcarea prin **CMP**, fiecare ieșire se evaluează la costul mediu ponderat curent al stocului, calculat din toate loturile amestecate valoric.
- La descărcarea prin **FIFO**, fiecare ieșire „consumă" întâi cantitatea din lotul cel mai vechi rămas, la costul lui real de achiziție, trecând la lotul următor doar după epuizarea celui curent.
- Nota contabilă de descărcare (de regulă 607=371 pentru mărfuri sau 601=301 pentru materii prime) reflectă, în ambele metode, valoarea calculată conform metodei alese — diferă doar cifra, nu formatul notei.
- Legea nu preferă una dintre metode pentru descărcarea de gestiune — alegerea rămâne o politică contabilă a firmei, stabilită dinainte, nu decisă ieșire cu ieșire.

## Ce se greșește în practică

- Se amestecă cele două metode în aceeași gestiune — unele ieșiri evaluate la CMP, altele „ca și cum ar fi FIFO" — ceea ce face fișa de magazie inconsistentă și greu de reconciliat cu balanța contabilă.
- Se crede că metoda de descărcare e o decizie tehnică fără impact fiscal — de fapt, ea influențează direct valoarea cheltuielii recunoscute și, implicit, rezultatul fiscal al perioadei.
- Se presupune că un sistem informatic de gestiune oferă automat ambele metode ca opțiuni interschimbabile — în realitate, multe aplicații implementează o singură metodă, hardcodată în motorul de calcul.

## Ce face iConta.eu

La descărcarea de gestiune, iConta.eu aplică **exclusiv metoda CMP**, niciodată FIFO. Funcția de ieșire din modulul de stocuri cantitativ-valorice (`core/stocuri_cv_api.py`) calculează valoarea ieșirii la costul mediu ponderat curent și generează automat nota contabilă de descărcare (607=371 pentru mărfuri, respectiv 601=301 pentru materii prime, în funcție de conturile atașate articolului). Nu există, nicăieri în motorul de calcul (`core/stocuri_cv.py`), o cale alternativă care să evalueze ieșirea la costul primului lot intrat — algoritmul lucrează mereu cu media ponderată a întregului stoc.

Prin urmare, un ghid „FIFO vs CMP la descărcarea de gestiune" în context iConta.eu nu descrie o alegere reală din aplicație: descărcarea se face întotdeauna la CMP, indiferent de preferința utilizatorului. Comparația FIFO/CMP rămâne utilă doar ca informație legală generală, pentru firmele care evaluează stocul manual sau în alt sistem înainte de a importa datele în iConta.

[iConta.eu](/)
