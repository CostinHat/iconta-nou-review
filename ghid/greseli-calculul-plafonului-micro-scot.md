---
title: "Greșeli la calculul plafonului micro care te scot din regim"
description: Plafonul de 100.000 euro se verifică cumulat de la începutul anului, la cursul BNR fix de la închiderea exercițiului financiar precedent — nu la cursul zilnic — și, în anumite situații, trebuie însumat cu veniturile persoanelor afiliate care dețin peste 25% în alte microîntreprinderi.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Greșeli la calculul plafonului micro care te scot din regim

Depășirea plafonului de 100.000 euro venituri scoate firma din regimul micro începând cu trimestrul depășirii — dar calculul plafonului însuși are reguli specifice, diferite de cele folosite la TVA sau la alte praguri valutare, iar o greșeală în calcul poate duce fie la o ieșire nesesizată din regim, fie la o ieșire declarată greșit când, de fapt, plafonul nu era depășit.

## Temeiul legal

::: ghid-temei
„Limitele fiscale prevăzute la alin. (1) se verifică pe baza veniturilor înregistrate cumulat de la începutul anului fiscal. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar precedent." — Codul fiscal, art. 52 alin. (5).
:::

## Greșeala de curs valutar

Spre deosebire de TVA (curs zilnic, la exigibilitate) sau de reevaluarea contabilă lunară a soldurilor în valută, plafonul micro se verifică la un **curs fix, stabilit o singură dată pe an** — cel valabil la închiderea exercițiului financiar precedent (practic, cursul BNR de la 31 decembrie al anului anterior). Acest curs se aplică tuturor veniturilor cumulate ale anului curent, indiferent cum evoluează cursul BNR în cursul anului. Greșeala tipică: se recalculează plafonul cu cursul zilei fiecărui venit, ceea ce poate muta artificial momentul „depășirii" mai devreme sau mai târziu decât cel real.

## Greșeala de cumulare

Verificarea plafonului se face **cumulat de la începutul anului fiscal**, nu pe fiecare trimestru izolat — un trimestru cu venituri mici nu „resetează" suma cumulată din trimestrele anterioare.

## Greșeala veniturilor persoanelor afiliate

Într-o situație specifică (asociați/acționari care dețin, direct sau indirect, legături cu alte microîntreprinderi în condițiile art. 47 alin. (1^1)), verificarea plafonului de 100.000 euro trebuie să însumeze și veniturile persoanelor afiliate respective — omiterea acestei însumări poate duce la o concluzie greșită că plafonul nu a fost depășit, când de fapt a fost, la nivelul grupului de persoane legate.

## Ce se greșește în practică

- Se folosește cursul BNR al zilei fiecărei facturi pentru verificarea plafonului, în loc de cursul fix de la închiderea exercițiului financiar precedent.
- Se calculează plafonul doar pe trimestrul curent, ignorând cumulul de la începutul anului.
- Se omite verificarea veniturilor persoanelor afiliate, în situațiile în care legea o cere explicit.

## Ce face iConta.eu

Aplicația nu urmărește automat plafonul de ieșire din regimul micro — verificat direct în cod: nu există în `core/` nicio constantă sau logică de calcul/monitorizare a plafonului de 100.000 euro. Blocajul de schimbare a regimului fiscal se bazează strict pe câmpul `regim_fiscal` completat manual de contabil, nu pe un calcul intern al plafonului. Verificarea plafonului — inclusiv cursul fix corect și, dacă e cazul, cumularea cu veniturile persoanelor afiliate — rămâne o responsabilitate a contabilului, în afara aplicației.

[iConta.eu](/)
