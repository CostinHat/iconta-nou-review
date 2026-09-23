---
title: "Cum se repartizează transportul internațional asupra costului mărfurilor importate?"
description: "Transportul internațional intră în costul de achiziție al mărfurilor și se repartizează proporțional cu valoarea fiecărui articol din NIR, cu rotunjire exactă pe ultima linie."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se repartizează transportul internațional asupra costului mărfurilor importate?

Transportul plătit pentru aducerea mărfii din import nu este o cheltuială de exploatare separată — este parte din costul de achiziție al mărfii și trebuie „împărțit" pe articolele efectiv cumpărate.

## Temeiul legal

::: ghid-temei
„6. cost de achiziție înseamnă prețul datorat şi eventualele cheltuieli conexe minus eventualele reduceri ale costului de achiziție. În acest sens, costul de achiziție al bunurilor cuprinde prețul de cumpărare, taxele de import şi alte taxe (...), cheltuielile de transport, manipulare şi alte cheltuieli care pot fi atribuibile direct achiziției bunurilor respective. (...) Cheltuielile de transport sunt incluse în costul de achiziție şi atunci când funcția de aprovizionare este externalizată." — OMFP 1802/2014, Secțiunea 1.2, pct. 6
:::

Legea cere ca transportul să fie inclus în costul de achiziție, dar nu impune o formulă anume pentru cazul în care un singur transport aduce mai multe articole diferite. Regula pe care o folosește aplicația este **repartizarea proporțională cu costul de bază** al fiecărei linii din NIR (nu cu greutatea sau cu cantitatea): fiecare articol primește din transport o cotă egală cu ponderea lui în valoarea totală a mărfii de pe acel NIR.

## Ce se greșește în practică

- Se înregistrează transportul internațional direct pe o cheltuială de exploatare (ex. 624 „cheltuieli cu transportul de bunuri"), în loc să fie capitalizat în costul mărfii — asta subevaluează stocul și denaturează adaosul comercial calculat ulterior.
- Se presupune că repartizarea „corectă" din punct de vedere vamal ar trebui făcută pe greutate, mai ales la mărfuri cu greutăți foarte diferite — legea nu cere o cheie anume, iar aplicația folosește valoarea, nu greutatea (aceasta e o alegere de produs, nu o eroare).
- Se stabilește un preț de vânzare pornind doar de la costul de bază al mărfii, fără să se țină cont că, odată capitalizat transportul, costul real (și deci adaosul) e mai mare decât prețul de listă al furnizorului.
- Se uită că TVA-ul aferent transportului nu se capitalizează — doar valoarea netă intră în costul mărfii; TVA-ul se tratează separat.

## Ce face iConta.eu

La introducerea unui NIR cu costuri accesorii, câmpul de transport se repartizează **automat, proporțional cu costul de bază** al fiecărei linii din NIR, iar restul de rotunjire se pune pe ultima linie, astfel încât suma repartizată să fie exact egală cu transportul introdus (de exemplu, 10 lei transport pe 3 linii egale se împart 3,33 + 3,33 + 3,34 lei, nu 3,33 + 3,33 + 3,33). Contul de credit al transportului este implicit 401, dar poate fi schimbat și confirmat de contabil, nu e fix în cod.

Aplicația verifică apoi ca prețul de vânzare introdus pentru fiecare articol să acopere costul de achiziție **cu transportul inclus**, nu doar costul de bază — dacă prețul de vânzare e sub acest cost majorat, înregistrarea este blocată.

Două limitări de care trebuie să ții cont: repartizarea se face doar pe **gestiunea global-valorică**, nu și pe gestiunea cantitativ-valorică (CMP) — pentru firmele care țin gestiunea CMP, capitalizarea transportului pe articole nu e automată în aplicație, se calculează manual de contabil. În plus, pentru mărfurile aduse dintr-un import cu declarație vamală, taxa vamală în sine se calculează separat (ecranul de import extracomunitar), iar suma rezultată se introduce apoi manual, ca parametru, în ecranul NIR — cele două calcule nu sunt legate automat.

[iConta.eu](/)
