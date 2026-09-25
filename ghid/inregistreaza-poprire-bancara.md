---
title: "Cum se înregistrează o poprire bancară?"
description: "Mecanismul legal al popririi bancare pentru datorii fiscale și cum tratează iConta.eu linia din extras rezultată dintr-o poprire."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează o poprire bancară?

Poprirea bancară nu e o plată pe care firma o inițiază — e banca ta care, la ordinul organului fiscal, blochează și virează o sumă din cont, indiferent de voința firmei. Din punct de vedere contabil, ea apare pur și simplu ca o ieșire de bani din extrasul de cont, pentru care trebuie identificată corect datoria pe care o stinge.

## Temeiul legal

::: ghid-temei
„(12) Pentru stingerea creanțelor fiscale, debitorii titulari de conturi bancare pot fi urmăriți prin poprire asupra sumelor din conturile bancare, prevederile alin. (5) aplicându-se în mod corespunzător. (13) [...] sumele existente, precum și cele viitoare provenite din încasările zilnice în conturile în lei și în valută sunt indisponibilizate în limita sumei necesare pentru realizarea obligației ce se execută silit [...]. Instituțiile de credit au obligația să plătească sumele indisponibilizate în contul indicat de organul de executare silită în termen de 3 zile lucrătoare de la indisponibilizare."
— Legea 207/2015 (Codul de procedură fiscală), art. 236 alin. (12)-(13) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Poprirea se înființează printr-o adresă a organului fiscal trimisă direct băncii (terțul poprit), nu firmei — poprirea „se consideră înființată" din momentul în care banca primește adresa, nu din momentul în care contabilul află de ea (art. 236 alin. 5, 8).
- Poprirea nu e supusă vreunei validări prealabile din partea debitorului (alin. 6) — banca e obligată să blocheze sumele imediat, iar contestația privind temeinicia ei se face pe altă cale, nu prin refuzul băncii de a executa.
- Banca are 3 zile lucrătoare de la indisponibilizarea sumelor pentru a le vira către contul indicat de organul de executare silită (alin. 13) — ceea ce apare în extrasul de cont e, de regulă, deja transferul efectiv către buget, nu doar un blocaj temporar vizibil separat.
- Cât timp poprirea e activă, banca nu mai decontează alte plăți din cont până la stingerea integrală a sumei din adresa de înființare, cu câteva excepții limitate (salarii nete, accize, obligații legate de o înlesnire la plată) (alin. 14).

## Ce se greșește în practică

- Se tratează linia de poprire din extras ca pe o plată voluntară obișnuită și se caută (greșit) un furnizor sau o factură căreia să i se aloce suma.
- Se așteaptă o „notificare separată" de poprire înainte de a acționa contabil, deși suma poate apărea direct debitată din cont — legea nu obligă banca să aștepte confirmarea firmei înainte de a executa.
- Se ignoră identificarea exactă a datoriei fiscale stinse prin poprire (TVA, impozit pe profit, contribuții etc.) — fără ea, nota contabilă nu poate închide corect obligația respectivă în evidență.

## Ce face iConta.eu

Reconcilierea bancară din iConta (motorul de potrivire a liniilor din extras cu facturile deschise) caută în descrierea fiecărei linii un CUI de partener și o potrivește cu facturi emise sau primite — mecanism gândit pentru încasări de la clienți și plăți către furnizori. O linie de poprire bancară nu are un CUI de factură în descriere și nu corespunde niciunei facturi deschise, așa că motorul de matching o clasifică drept **roșu** (nepotrivită), la fel ca orice altă linie fără corespondent de factură.

Nu există în aplicație o clasificare automată dedicată pentru „poprire" — spre deosebire de comision, dobândă sau rambursare de credit, care sunt recunoscute din cuvinte-cheie în descrierea liniei și primesc o notă propusă automat, „poprire" nu e printre cuvintele-cheie recunoscute. Contabilul trebuie să identifice manual linia din extras, să stabilească din adresa de înființare a popririi (sau din corespondența cu organul fiscal) ce datorie stinge suma, și să înregistreze nota contabilă corespunzătoare direct din jurnal, nu prin fluxul automat de „Contează" al reconcilierii.

[iConta.eu](/)
