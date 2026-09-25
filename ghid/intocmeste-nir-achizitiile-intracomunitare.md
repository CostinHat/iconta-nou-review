---
title: "Cum se întocmește NIR la achizițiile intracomunitare"
description: "Regulile de întocmire a notei de recepție și constatare de diferențe (NIR) la o achiziție intracomunitară de bunuri, potrivit OMFP 2634/2015, și particularitățile de TVA prin taxare inversă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se întocmește NIR la achizițiile intracomunitare

Nota de recepție și constatare de diferențe (NIR) rămâne documentul de bază la orice intrare de marfă în gestiune — inclusiv la o achiziție intracomunitară de bunuri, de la un furnizor înregistrat în scopuri de TVA în alt stat membru. Ce diferă față de o achiziție internă e regimul de TVA: nu se plătește TVA furnizorului, ci se aplică taxarea inversă, cu autolichidarea taxei de către cumpărător.

## Temeiul legal

::: ghid-temei
„NOTĂ DE RECEPȚIE ȘI CONSTATARE DE DIFERENȚE (Cod 14-3-1A) [...] Servește ca: document pentru recepția bunurilor aprovizionate; document justificativ pentru încărcare în gestiune; document justificativ de înregistrare în contabilitate."
— OMFP 2634/2015, anexa 2 (Norme specifice de întocmire și utilizare a documentelor financiar-contabile) (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Ce presupune, concret, NIR-ul la o achiziție intracomunitară:

- costul de achiziție înregistrat în NIR include prețul de cumpărare **plus** taxele nerecuperabile de import (dacă e cazul) și cheltuielile de transport direct atribuibile, capitalizate potrivit regulilor generale din OMFP 1802/2014;
- suma de pe factura furnizorului intracomunitar, emisă de regulă în valută (EUR sau altă monedă), trebuie convertită în lei la cursul de schimb valabil la data operațiunii, înainte de a fi introdusă în NIR;
- spre deosebire de o achiziție de la un furnizor intern, TVA-ul **nu se plătește furnizorului** — cumpărătorul înregistrat în scopuri de TVA autolichidează taxa, înregistrând-o simultan ca TVA deductibilă și ca TVA colectată (taxare inversă), fără impact de trezorerie pe operațiune;
- fiscal, achiziția trebuie raportată corect prin declarațiile specifice — codul de partener trebuie verificat prin sistemul VIES înainte de aplicarea regimului de scutire/taxare inversă, iar operațiunea intră în evidența pentru declarația recapitulativă (D390) privind livrările/achizițiile intracomunitare.

## Ce se greșește în practică

- Se aplică regimul obișnuit de TVA deductibilă direct pe factura furnizorului (ca la o achiziție internă), în loc de taxare inversă — eroare care fie dublează, fie omite TVA-ul aferent, în funcție de sensul greșelii.
- Se introduce în NIR valoarea în valută de pe factura furnizorului, fără conversia la cursul de schimb corect de la data operațiunii — sau se folosește cursul zilei de plată în loc de cursul de la data recepției/facturii, potrivit regulilor contabile aplicabile.
- Se omite verificarea codului de TVA al furnizorului în sistemul VIES înainte de tratarea operațiunii ca achiziție intracomunitară scutită/cu taxare inversă — dacă furnizorul nu e valid înregistrat, operațiunea riscă să fie recalificată.

## Ce face iConta.eu

iConta.eu are un modul de NIR global-valoric care calculează costul de achiziție (inclusiv transportul și taxele accesorii capitalizate proporțional pe articole), TVA-ul aferent și valoarea de vânzare, generând notele contabile ciornă corespunzătoare, pe baza sumelor și cotei de TVA introduse pe fiecare linie de articol. La acest moment, motorul NIR **nu tratează distinct** regimul de taxare inversă specific achizițiilor intracomunitare — TVA-ul dedus e înregistrat direct pe baza cotei introduse de contabil, iar aplicarea corectă a mecanismului de autolichidare (inclusiv corespondența TVA deductibilă/colectată) rămâne, deocamdată, o verificare manuală a contabilului, la fel ca și conversia valutară la cursul corect de la data operațiunii. Raportarea acestor achiziții în declarația recapitulativă D390 e tratată separat, în modulul dedicat acesteia.

[iConta.eu](/)
