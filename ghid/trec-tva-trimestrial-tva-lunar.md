---
title: "Când trec de la TVA trimestrial la TVA lunar?"
description: "Momentul legal în care o firmă cu perioadă fiscală trimestrială pentru TVA trece obligatoriu la perioadă lunară, potrivit art. 322 din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Când trec de la TVA trimestrial la TVA lunar?

Perioada fiscală a TVA nu e o alegere liberă a firmei, ci rezultatul direct al unei condiții din Codul fiscal: cifra de afaceri din anul precedent și, separat, existența achizițiilor intracomunitare. Depășirea plafonului sau efectuarea unei achiziții intracomunitare scoate firma din regimul trimestrial, indiferent de preferința ei.

## Temeiul legal

::: ghid-temei
„Perioada fiscală este luna calendaristică.
Prin excepție de la prevederile alin. (1), perioada fiscală este trimestrul calendaristic pentru persoana impozabilă care în cursul anului calendaristic precedent a realizat o cifră de afaceri din operațiuni taxabile și/sau scutite cu drept de deducere și/sau neimpozabile în România conform art. 275 și 278, dar care dau drept de deducere conform art. 297 alin. (4) lit. b), care nu a depășit plafonul de 100.000 euro al cărui echivalent în lei se calculează conform normelor metodologice, cu excepția situației în care persoana impozabilă a efectuat în cursul anului calendaristic precedent una sau mai multe achiziții intracomunitare de bunuri."
— Legea 227/2015, art. 322 alin. (1) și (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Regula, tradusă în momentul concret de trecere:

- **Regula generală**: perioada fiscală a TVA e **luna calendaristică**.
- **Excepția trimestrială** se aplică doar dacă, în anul calendaristic **precedent**, firma nu a depășit plafonul de **100.000 euro** cifră de afaceri din operațiuni taxabile/scutite cu drept de deducere/neimpozabile, **și** nu a efectuat nicio achiziție intracomunitară de bunuri în acel an.
- Firma trece **obligatoriu la lunar** dacă, în anul precedent, fie a depășit plafonul de 100.000 euro, fie a efectuat **măcar o singură** achiziție intracomunitară de bunuri — cele două condiții funcționează independent, oricare dintre ele scoate firma din regimul trimestrial.
- Trecerea afectează periodicitatea declarațiilor legate de TVA — D300, D394, D406 — care urmează perioada fiscală efectivă a firmei, nu un calendar fix ales de contabil.

## Ce se greșește în practică

- Se verifică doar plafonul de 100.000 euro și se ignoră achizițiile intracomunitare — o singură achiziție intracomunitară de bunuri în anul precedent scoate firma din regimul trimestrial, chiar dacă cifra de afaceri e mult sub plafon.
- Se calculează plafonul pe anul **curent**, nu pe anul **calendaristic precedent** — verificarea condiției se face retrospectiv, la finalul anului anterior, nu în timp real, pe măsură ce se apropie plafonul în anul curent.
- Se presupune că trecerea la lunar e o opțiune pe care firma o poate amâna „până la momentul potrivit" — de fapt e o consecință automată a depășirii condițiilor, cu efect asupra periodicității declarațiilor din anul următor.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu numără automat plafonul de 100.000 euro** al anului precedent și nu decide singură trecerea firmei de la trimestrial la lunar — aceasta e o verificare pe care contabilul o face și o reflectă în profilul firmei (`tip_decont`). Aplicația are însă un modul dedicat care leagă corect regula legală de periodicitatea afișată: pentru declarațiile a căror perioadă fiscală urmează TVA (D300, D394, D406), aplică art. 322 alin. (1)/(2) exact ca temei, fără să inventeze o regulă proprie și fără să confunde acest temei cu periodicitatea altor declarații (`core/perioada_fiscala_tva.py`).

[iConta.eu](/)
