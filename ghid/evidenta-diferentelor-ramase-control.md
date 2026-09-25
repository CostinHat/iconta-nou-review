---
title: "Evidența diferențelor rămase după control"
description: "Cum se înregistrează în contabilitate diferențele stabilite de organele de inspecție fiscală, aferente exercițiilor financiare anterioare: pe rezultatul reportat, nu pe cheltuieli/venituri curente."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Evidența diferențelor rămase după control

Când o inspecție fiscală stabilește diferențe de impozite, taxe sau contribuții pentru un exercițiu financiar deja închis, firma nu poate „repara" pur și simplu contul de profit și pierdere al anului curent — reglementările contabile tratează aceste diferențe ca erori aferente exercițiilor anterioare, cu un regim de înregistrare distinct.

## Temeiul legal

::: ghid-temei
„65. - (1) Erorile constatate în contabilitate se pot referi fie la exercițiul financiar curent, fie la exercițiile financiare precedente. (2) Corectarea erorilor se efectuează la data constatării lor. [...]
67. - (1) Corectarea erorilor aferente exercițiului financiar curent se efectuează pe seama contului de profit și pierdere. (2) Corectarea erorilor semnificative aferente exercițiilor financiare precedente se efectuează pe seama rezultatului reportat (contul 1174 «Rezultatul reportat provenit din corectarea erorilor contabile»). (3) Erorile nesemnificative aferente exercițiilor financiare precedente se corectează, de asemenea, pe seama rezultatului reportat. Totuși, potrivit politicilor contabile aprobate, erorile nesemnificative pot fi corectate pe seama contului de profit și pierdere. [...]
68. - (1) Corectarea erorilor aferente exercițiilor financiare precedente nu determină modificarea situațiilor financiare ale acelor exerciții. (2) [...] Informații comparative referitoare la poziția financiară și performanța financiară [...] sunt prezentate în notele explicative. (3) În notele explicative la situațiile financiare trebuie prezentate informații cu privire la natura erorilor constatate și perioadele afectate de acestea."
— OMFP 1802/2014, pct. 65, 67 și 68 (Reglementări contabile privind situațiile financiare anuale individuale) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat la o diferență stabilită printr-un act de control fiscal, mecanismul e:

- **Dacă exercițiul vizat de diferență e închis** (an financiar anterior), corectarea NU se face pe cheltuieli/venituri ale anului curent, ci pe rezultatul reportat — contul **1174**, dacă eroarea e semnificativă.
- **Situațiile financiare ale anului corectat nu se refac** — nu se depune din nou un bilanț pentru anul vizat de control; efectul se reflectă în anul curent, prin 1174, cu explicații în notele explicative.
- **Pragul de semnificație contează**: erorile nesemnificative pot fi corectate direct pe cheltuieli/venituri curente, dacă așa prevede politica contabilă a firmei — nu toate diferențele de control merg automat pe 1174.
- **Notele explicative sunt obligatorii**: natura erorii constatate și perioada afectată trebuie prezentate explicit, nu doar înregistrate contabil.

## Ce se greșește în practică

- Se înregistrează diferența stabilită de inspecția fiscală direct pe cheltuiala/venitul curent, deși privește un exercițiu financiar anterior deja închis — corect e prin 1174, dacă eroarea e semnificativă.
- Se încearcă „retratarea" bilanțului anului controlat, deși pct. 68 exclude explicit modificarea situațiilor financiare ale exercițiilor anterioare — corecția se vede doar în perioada curentă, cu comparative explicate în note.
- Se omite complet analiza pragului de semnificație — se tratează orice diferență de control ca fiind automat „semnificativă" (deci pe 1174) sau automat „nesemnificativă" (deci pe cheltuială curentă), fără o evaluare documentată în context.
- Se confundă corectarea erorii contabile cu obligația fiscală de plată: chiar dacă suma stabilită de control se plătește imediat, înregistrarea contabilă a diferenței urmează regulile de mai sus, nu se contabilizează doar ca o plată către buget.

## Ce face iConta.eu

La data acestui ghid, iConta.eu raportează diferențele stabilite de inspecția fiscală **doar în declarația de TVA** — modulul `core/d300.py` are rândurile dedicate R36 („diferențe stabilite de inspecție fiscală") și R39 („diferențe negative stabilite de inspecție fiscală"), care alimentează regularizarea din decont. Aplicația nu are însă un modul dedicat pentru **înregistrarea contabilă** a diferențelor de control pe contul 1174 și nu automatizează evaluarea pragului de semnificație din pct. 67 — nota contabilă pentru corectarea erorilor aferente exercițiilor anterioare se introduce, la acest moment, manual, conform politicii contabile a firmei.

[iConta.eu](/)
