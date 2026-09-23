---
title: Ce este contul 4428 în gestiunea cu amănuntul?
description: Contul 4428 „Taxa pe valoarea adăugată neexigibilă” ține, în gestiunea la preț cu amănuntul, TVA-ul calculat pe prețul de vânzare al mărfii, dar care devine exigibil (de declarat) abia la vânzarea efectivă, nu la achiziție.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce este contul 4428 în gestiunea cu amănuntul?

Contul 4428 e un cont bifuncțional folosit, în gestiunea la preț cu amănuntul (metoda global-valorică), pentru TVA-ul care „așteaptă” vânzarea mărfii ca să devină declarabilă. Nu e o taxă suplimentară — e aceeași TVA aferentă mărfii, doar recunoscută mai devreme în stoc și transferată la vânzare.

## Temeiul legal

::: ghid-temei
„Contul 4428 «Taxa pe valoarea adăugată neexigibilă» (cont bifuncțional): «În acest cont se evidențiază, potrivit legii, taxa pe valoarea adăugată neexigibilă.»”

„Contul 371 «Mărfuri» ... în debit — «valoarea adaosului comercial și taxa pe valoarea adăugată neexigibilă, în situația în care evidența mărfurilor se ține la preț cu amănuntul (378, 4428)»; ...”

— *OMFP 1802/2014, Capitolul 16, funcțiunea conturilor 4428 și 371.*

„nota *2) la alin. (4): La calcularea procentului mediu de adaos comercial, soldul inițial al contului de mărfuri și valoarea intrărilor de mărfuri nu vor include TVA neexigibilă.”

— *OMFP 1802/2014, pct. 286 alin. (4), nota 2.*
:::

## Rolul contului 4428 în mecanismul global-valoric

- **La recepția mărfii**, TVA-ul calculat pe prețul de vânzare cu amănuntul (cost + adaos) se înregistrează `371 = 4428` — mărfurile intră în stoc „la preț cu amănuntul, cu TVA inclusă”, iar contul 4428 ține partea de TVA din acest preț.
- **Soldul contului 4428**, la un moment dat, reprezintă TVA-ul aferent mărfurilor încă nevândute — o taxă recunoscută în stoc, dar neexigibilă (nedatorată încă bugetului).
- **La vânzare**, TVA-ul aferent mărfii vândute devine exigibil și se descarcă: `4428 = 371`, iar suma respectivă intră în calculul TVA colectate de raportat prin decontul de TVA.
- **La calculul coeficientului de adaos** (K, folosit la descărcarea lunară), soldul contului 4428 se scade explicit din baza de calcul a stocurilor — legea cere ca „valoarea intrărilor de mărfuri" folosită pentru procentul de adaos să nu includă TVA neexigibilă.

## Ce se greșește în practică

- Se confundă 4428 cu 4426 (TVA deductibilă la achiziție) — sunt roluri complet diferite: 4426 se deduce imediat, la achiziție; 4428 rămâne „în așteptare”, legat de vânzarea efectivă a mărfii din gestiunea la preț cu amănuntul.
- Se raportează la ANAF soldul contului 4428 ca TVA de plată — 4428 nu e o taxă datorată în sine, ci o componentă a valorii stocului, exigibilă abia la vânzare.
- Se amestecă rulajul contului 4428 din gestiunea la preț cu amănuntul cu rulajul aceluiași cont folosit pentru regimul de TVA la încasare — sunt mecanisme fiscale diferite care, dacă firma le folosește pe amândouă, trebuie ținute separat, altfel calculul adaosului se denaturează.

## Ce face iConta.eu

`core/stocuri.py` folosește 4428 exact conform normei: la recepție (`nir_gv`), linia `371=4428` pentru TVA neexigibilă aferentă prețului de vânzare; la descărcarea lunară (`descarcare_gv`), linia `4428=371` pentru TVA aferentă vânzărilor lunii, calculată proporțional din stocul curent. Formula coeficientului K, implementată în `coeficient_k(si_378, rc_378, si_371, rd_371, si_4428, rc_4428)`, scade explicit soldul și rulajul contului 4428 din numitor — `numitor = (Si371 + Rd371) - (Si4428 + Rc4428)` — exact cum cere nota 2) de la pct. 286 alin. (4).

Risc tehnic de reținut: funcția `descarca_luna` citește rulajele 371/378/4428 **fără să filtreze pe sursa operațiunii** (spre deosebire de rulajul de vânzări, 707, care e filtrat explicit pe sursele de gestiune). Dacă firma combină gestiunea global-valorică cu ecranul manual de „TVA la încasare (art. 282)” — care produce note tot pe 4428 — rulajele celor două mecanisme se pot aduna, denaturând coeficientul K calculat automat.

[iConta.eu](/)
