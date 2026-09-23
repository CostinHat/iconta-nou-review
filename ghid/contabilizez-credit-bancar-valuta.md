---
title: Cum contabilizez un credit bancar în valută?
description: Nota de bază este identică cu a unui credit în lei (5121=1621 la primire, 1621=5121 la rată), doar că suma se convertește la cursul BNR din ziua primirii; lunar și la fiecare plată, soldul rămas se reevaluează, iar diferența de curs merge pe 665 (pierdere) sau 765 (câștig).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum contabilizez un credit bancar în valută?

Un credit bancar în valută (de regulă euro) se înregistrează la fel ca unul în lei — aceleași conturi, aceeași logică de rată/dobândă — cu o singură diferență structurală: suma în valută trebuie convertită în lei la cursul BNR din ziua operațiunii, iar soldul rămas se reevaluează periodic la cursul de la sfârșitul lunii. Diferența dintre cele două cursuri e cea care generează o notă contabilă suplimentară.

## Temeiul legal

::: ghid-temei
„319. - O tranzacție în valută trebuie înregistrată inițial la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii.”

„317. - (1) ... o tranzacție în valută este o tranzacție care este exprimată sau necesită decontarea într-o altă monedă decât moneda națională (leu), inclusiv tranzacțiile rezultate atunci când o entitate: ... b) împrumută sau oferă spre împrumut fonduri, iar sumele ce urmează să fie plătite sau încasate sunt exprimate în valută; ...”

— *OMFP 1802/2014, pct. 317 și pct. 319.*

„În creditul contului 162 [Credite bancare pe termen lung] ... se înregistrează: – suma creditelor pe termen lung primite (512); – diferențele nefavorabile de curs valutar ... (665). În debitul contului 162 ... se înregistrează: – suma creditelor pe termen lung rambursate (512); – diferențele favorabile de curs valutar ... (765).”

— *OMFP 1802/2014, Capitolul 16, funcțiunea contului 162.*
:::

## Pașii pentru înregistrarea corectă

1. **La primirea creditului**, convertiți suma în valută la cursul BNR din ziua în care banca a virat banii (pct. 319) și înregistrați nota obișnuită de primire — `5121 = 1621` pentru termen lung sau `5121 = 5191` pentru termen scurt — dar cu suma deja calculată în lei, la acel curs.
2. **La fiecare plată de rată/dobândă**, convertiți din nou la cursul BNR din ziua plății. Diferența dintre suma înregistrată inițial (sau la ultima reevaluare) și suma plătită efectiv la noul curs se recunoaște ca venit sau cheltuială din diferențe de curs.
3. **La sfârșitul fiecărei luni**, soldul rămas al creditului (partea nerambursată din 1621/5191, plus eventuala dobândă angajată neplătită din 1682/5198) se reevaluează la cursul BNR din ultima zi bancară a lunii — chiar dacă nu a avut loc nicio plată în luna respectivă.

::: ghid-exemplu
Un credit de 10.000 EUR e primit la curs BNR 5,00 lei/EUR → se înregistrează 50.000 lei (`5121=1621`, 50.000). La sfârșitul lunii, cursul BNR a urcat la 5,05 lei/EUR. Soldul de 10.000 EUR reevaluat ar valora acum 50.500 lei — diferența nefavorabilă de 500 lei se înregistrează `665 = 1621`, 500 lei (pierdere din curs, pentru că e o datorie, iar cursul a crescut).
:::

## Ce se greșește în practică

- Se înregistrează suma creditului direct în lei, la un curs aproximativ sau la cursul zilei curente, în loc de cursul BNR comunicat exact pentru ziua primirii banilor.
- Se omite reevaluarea lunară a soldului atunci când nu a existat nicio plată în luna respectivă — reevaluarea se face indiferent de mișcări, dacă soldul în valută e nenul.
- Se confundă sensul diferenței: pentru o **datorie** (creditul e o datorie a firmei), creșterea cursului generează pierdere (665), nu câștig — regula e inversă față de o creanță în valută.
- Se reevaluează doar suma principalului, uitând că și dobânda angajată, neplătită, aflată pe 1682/5198, e tot un sold în valută dacă a fost calculată în moneda creditului.

## Ce face iConta.eu

`core/credite.py` produce nota de bază (`nota_primire`, `nota_plata` etc.) exact ca pentru un credit în lei — motorul nu are un câmp dedicat de „monedă” în ecranul „Credite bancare” (`static/js/ecrane/operatiuni_ecran.js`, cheia `"credit"`), deci suma introdusă trebuie să fie deja convertită în lei, la cursul BNR din ziua operațiunii.

Reevaluarea periodică a soldurilor în valută (inclusiv pentru conturile de credit, 1621/1682/5191/5198) e tratată **separat**, printr-un motor dedicat: `core/diferente_curs.py`, funcția `reevaluare_sold(sold_valuta, curs_evidenta, curs_bnr_sfarsit_luna, tip, cont_sold)`, apelată din use-case-ul `reevaluare_valuta()` (`core/uc_tenants.py`) pe ruta `/tenants/{tenant_id}/reevaluare-valuta`. Pentru un credit (tip `"datorie"`), motorul generează automat linia `665=cont` sau `cont=765`, după caz. Practic: primirea și ratele creditului se introduc manual, convertite în lei, iar reevaluarea periodică a soldului se face separat, prin ecranul de reevaluare valută, nu prin ecranul „Credite bancare”.

[iConta.eu](/)
