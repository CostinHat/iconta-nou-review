---
title: "Cum se calculează pro-rata definitivă la sfârșitul anului?"
description: "Regula de calcul a pro-ratei definitive de TVA la închiderea anului și diferența ei față de pro-rata provizorie aplicată în cursul anului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează pro-rata definitivă la sfârșitul anului?

O persoană impozabilă cu regim mixt (operațiuni cu și fără drept de deducere) aplică în cursul anului o pro-rata provizorie, dar la sfârșitul anului trebuie să o recalculeze pe baza operațiunilor efectiv realizate — pro-rata definitivă — și să regularizeze deducerile din tot anul pe baza ei.

## Temeiul legal

::: ghid-temei
„Pro rata definitivă se determină anual, iar calculul acesteia include toate operațiunile prevăzute la alin. (6) [...]. Pro rata definitivă se determină procentual și se rotunjește până la cifra unităților imediat următoare. [...]
Pro rata aplicabilă provizoriu pentru un an este pro rata definitivă, prevăzută la alin. (8), determinată pentru anul precedent, sau pro rata estimată pe baza operațiunilor prevăzute a fi realizate în anul calendaristic curent [...]"
— Legea 227/2015 (Codul fiscal), art. 300 alin. (8)-(9) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul complet, din text:

- Pro-rata folosită lună de lună (sau trimestru de trimestru) e una provizorie — de regulă pro-rata definitivă a anului precedent sau o estimare comunicată organului fiscal până la 25 ianuarie.
- La sfârșitul anului, pro-rata definitivă se recalculează pe baza operațiunilor efectiv realizate în tot anul (art. 300 alin. (6)-(7)), rotunjită la cifra unităților imediat următoare (adică întotdeauna în sus).
- Diferența dintre TVA dedusă pe parcursul anului (pe pro-rata provizorie) și TVA care ar fi trebuit dedusă pe pro-rata definitivă se regularizează prin decontul de taxă aferent ultimei perioade fiscale a anului.

## Ce se greșește în practică

- Se aplică toată anul aceeași pro-rata provizorie, fără a o recalcula și regulariza la final de an cu pro-rata definitivă.
- Se rotunjește pro-rata definitivă matematic standard, în loc de „la cifra unităților imediat următoare" (rotunjire întotdeauna în sus, conform legii).
- Se aplică pro-rata pe toate achizițiile, în loc de a o aplica strict pe achizițiile cu destinație mixtă sau necunoscută (art. 300 alin. (5)).

## Ce face iConta.eu

Modulul D300 din iConta.eu (`core/d300.py`) aplică pro-rata exclusiv pe baza achizițiilor cu destinație mixtă, conform art. 300 alin. (5), și calculează ajustarea aferentă (rândul de ajustări din decont) atunci când pro-rata din profilul firmei e sub 100%. Procentul de pro-rata (provizorie sau definitivă) se introduce însă de către contabil în profilul firmei — aplicația nu calculează automat, la finalul anului, pro-rata definitivă din operațiunile anuale.

[iConta.eu](/)
