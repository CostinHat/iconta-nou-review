---
title: Cum se scot din evidență bunurile amortizate complet?
description: Ce se întâmplă fiscal și contabil cu un mijloc fix care și-a atins valoarea fiscală integral amortizată, și cum se face casarea lui în iConta.eu.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se scot din evidență bunurile amortizate complet?

Un mijloc fix ajuns la finalul duratei normale de utilizare, cu valoarea rămasă (net book
value) zero, nu dispare automat din evidență — trebuie scos formal, printr-o operațiune de
casare, pe baza amortizării calculate la zi.

## Temeiul legal

::: ghid-temei
Pentru mijloacele fixe amortizabile, deducerile de amortizare se determină fără a lua în
calcul amortizarea contabilă. Câștigurile sau pierderile rezultate din vânzarea ori din
scoaterea din funcțiune a acestor mijloace fixe se calculează pe baza valorii fiscale a
acestora, diminuată cu amortizarea fiscală, cu excepția celor prevăzute la alin. (14).

— Codul fiscal (Legea 227/2015), art.28 alin.(17)
:::

La scoaterea din funcțiune (casare) sau la vânzare, rezultatul fiscal (câștig sau pierdere) se
calculează pe **valoarea fiscală diminuată cu amortizarea fiscală** — adică exact valoarea
rămasă (net book value) din registrul de mijloace fixe, calculată pe metoda reală a activului,
nu pe o amortizare contabilă paralelă. Pentru un bun complet amortizat, valoarea rămasă e zero,
deci scoaterea lui din evidență nu mai generează, în mod normal, niciun rezultat fiscal
suplimentar legat de amortizare.

## Ce se greșește în practică

- Se scoate manual bunul din evidență fără să se calculeze mai întâi amortizarea cumulată la
  zi pe metoda lui reală (mai ales la active pe metodă degresivă sau accelerată, unde ritmul
  amortizării nu e liniar și o estimare "din cap" poate fi greșită).
- Se lasă activul "activ" în registru mult timp după ce fizic a fost casat, ceea ce distorsionează
  raportările (ex. D406/SAF-T) și evidența patrimonială.
- Se confundă casarea cu o simplă ștergere a rândului din evidență, fără nota contabilă aferentă
  (contul de "PV comisie" pentru rezultatul casării).

## Ce face iConta.eu

Din ecranul `Firma > Mijloace fixe`, un mijloc fix activ are acțiunea **Casează**. Aceasta
calculează automat amortizarea la data casării, pe metoda reală a activului (același motor unic
de calcul folosit de registru, nota lunară de amortizare, D406 și reevaluare), și generează o
notă contabilă **ciornă** (cont de rezultat al casării), care se validează separat din Registrul
jurnal — nu se aplică direct pe registrul de mijloace fixe. După validare, activul e marcat ca
inactiv (`activ=false`) și iese din calculul amortizărilor viitoare, rămânând vizibil în istoric.
De reținut: pragul minim al mijlocului fix (5.000 lei) nu mai e reverificat la casarea unui
activ deja existent în registru — pragul contează doar la momentul intrării, nu și la ieșire.

[iConta.eu](/)
