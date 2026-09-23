---
title: Ce fac dacă am folosit contul contabil greșit?
description: Un cont contabil greșit pe o notă se corectează direct pe linie, cât timp nota e ciornă. Odată validată, singura cale e o notă nouă de stornare. iConta.eu reține contul corectat ca să propună mai bine data viitoare pe operațiuni similare.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce fac dacă am folosit contul contabil greșit?

Un cont greșit pe o notă contabilă (de exemplu un 4xx în loc de altul, sau un cont de cheltuială/venit nepotrivit) nu e o eroare specială în iConta.eu — e aceeași operațiune tehnică ca orice altă corecție de notă: se schimbă linia respectivă. Ce contează e doar în ce stare e nota.

## Temeiul legal

::: ghid-temei
„Persoanele prevăzute la art. 1 alin. (1)-(4) au obligația să conducă contabilitatea în partidă dublă și să întocmească situații financiare anuale, potrivit reglementărilor contabile aplicabile." — Legea contabilității nr. 82/1991, art. 5 alin. (1)

„În cazul completării documentelor prin utilizarea sistemelor informatice de prelucrare automată a datelor, corecturile sunt admise numai înainte de prelucrarea acestora." — OMFP 2634/2015, pct. 16
:::

Contul folosit pe fiecare linie de debit/credit e chiar mecanismul partidei duble — un cont greșit nu doar „arată prost", ci distorsionează balanța și situațiile financiare care se construiesc din ea.

## Cum corectez în iConta.eu

- **Nota e ciornă** → contul greșit se înlocuiește direct pe linia respectivă, cu condiția ca noul cont să existe în planul de conturi al firmei. Editarea acceptă schimbarea oricărui cont de pe orice linie a notei, cât timp nota nu a fost validată.
- Când editarea schimbă contul debitor de pe **prima linie** a notei, aplicația reține contul propus inițial și contul final ales — folosește această corecție pentru a propune mai bine contul pe operațiuni similare, viitoare.
- **Nota e validată** → contul nu se mai poate schimba direct; aplicația refuză editarea cu mesajul „doar ciornele se pot edita". Corecția se face printr-o notă nouă, care stornează contul greșit (sumă cu semn opus pe contul greșit) și înregistrează corect pe contul potrivit.
- Dacă nota e legată de o factură (e nota de contare a acesteia) și e deja validată, corecția contului trece prin stornarea facturii — nu prin editarea sau dezlegarea directă a notei.
- Luna închisă blochează atât editarea ciornei, cât și validarea sau introducerea notei de stornare.

## Ce se greșește în practică

- Se lasă contul greșit „pentru că suma e corectă" — dar contul afectează direct balanța analitică și rulajele conturilor implicate, indiferent de valoare.
- Se încearcă editarea unei note deja validate, deși codul o refuză explicit — corecția reală se face doar prin notă de stornare.
- Se creează manual o notă de corecție care nu menționează nota/documentul original — pierzându-se trasabilitatea între greșeală și corecție.

## Ce face iConta.eu

Contul greșit se corectează direct, pe linia respectivă, cât timp nota e ciornă. Odată validată, corecția se face exclusiv printr-o notă nouă de stornare. Când schimbarea privește contul debitor de pe prima linie, aplicația reține alegerea finală a contabilului față de propunerea inițială, ca să sugereze mai corect data viitoare — fără să schimbe însă regula de bază: contul unei note validate nu se editează.

[iConta.eu](/)
