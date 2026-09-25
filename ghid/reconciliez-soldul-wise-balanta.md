---
title: "Cum reconciliez soldul Wise cu balanța?"
description: "Obligația legală de a confrunta soldul din extrasul de cont (inclusiv Wise sau alte instituții de plată) cu soldul contabil, și cum se face practic."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum reconciliez soldul Wise cu balanța?

Multe firme românești folosesc, pe lângă banca tradițională, un cont Wise (sau alt instituție de plată) pentru încasări/plăți în valută. Contabil, aceste conturi se tratează la fel ca orice cont bancar de disponibilități — inclusiv obligația de reconciliere periodică a soldului.

## Temeiul legal

::: ghid-temei
„Disponibilitățile aflate în conturi la bănci sau la unitățile Trezoreriei Statului se inventariază prin confruntarea soldurilor din extrasele de cont emise de acestea cu cele din contabilitatea entității. În acest scop, extrasele de cont din ziua de 31 decembrie sau din ultima zi bancară [...] vor purta ștampila oficială a acestora."
— OMFP 2861/2009 (normele privind organizarea și efectuarea inventarierii), pct. 29 alin. (2) (sursă: anaf_surse/omfp_2861_2009.txt)
:::

Norma vorbește explicit despre conturi "la bănci" — iar o instituție de plată autorizată (cum e Wise, licențiată ca instituție de plată/monedă electronică într-un stat membru UE) intră în aceeași logică de disponibilități bănești ale entității, chiar dacă nu e o bancă tradițională licențiată în România. Practic, reconcilierea presupune:

- **Compararea soldului final din extrasul Wise** (la sfârșitul lunii sau, obligatoriu, la 31 decembrie) **cu soldul contului contabil corespunzător** (5124, pentru disponibilități în valută la instituții financiare, sau analitic dedicat).
- **Identificarea diferențelor** — de regulă cauzate de operațiuni în tranzit (sume trimise, dar neajunse încă la destinatar), comisioane Wise neînregistrate încă, sau diferențe de curs valutar nereevaluate.
- **Documentarea reconcilierii** — extrasul Wise descărcat și, cel puțin la închiderea anuală, păstrat ca document justificativ al soldului.

## Ce se greșește în practică

- Se tratează contul Wise ca pe o simplă "casă electronică" informală, fără reconciliere periodică, spre deosebire de conturile bancare tradiționale, unde reconcilierea e o rutină.
- Se omit din reconciliere sumele "în tranzit" (trimise, dar neajunse încă la beneficiar), ceea ce creează diferențe artificiale între soldul contabil și cel din extras.
- Se uită reevaluarea la cursul BNR de la sfârșitul lunii a soldurilor în valută din Wise, la fel ca la orice alt cont valutar.

## Ce face iConta.eu

La data acestui ghid, iConta.eu oferă evidența contabilă generală a conturilor de disponibilități, inclusiv conturi în valută, cu module dedicate de contabilizare a extraselor bancare și de calcul al diferențelor de curs valutar. Aplicația nu are un conector dedicat pentru importul automat al extraselor Wise — importul acestora, dacă e nevoie, se face prin fișierele generale de extras suportate de aplicație, iar reconcilierea propriu-zisă rămâne o verificare manuală a contabilului.

[iConta.eu](/)
