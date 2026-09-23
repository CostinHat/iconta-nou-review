---
title: Cum se indică motivul scutirii de TVA în XML-ul e-Factura?
description: Legea cere mențiunea temeiului scutirii pe orice factură scutită (art. 319 alin. 20 lit. l). Tehnic, standardul UBL/CIUS-RO are un câmp dedicat pentru motiv — dar generatorul XML al iConta.eu nu-l populează în acest moment.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se indică motivul scutirii de TVA în XML-ul e-Factura?

Răspuns direct: în acest moment, nu se indică — nu pentru că legea n-ar cere-o, ci pentru că generatorul XML al iConta.eu nu are, la acest moment, un câmp dedicat motivului scutirii. E o limitare pe care preferăm s-o spunem clar, în loc să lăsăm impresia unei funcționalități care nu există.

## Temeiul legal

::: ghid-temei
**Art. 319 alin. (20) lit. l) din Codul fiscal**: „în cazul în care este aplicabilă o scutire de taxă, trimiterea la dispozițiile aplicabile din prezentul titlu ori din Directiva 112 sau orice altă mențiune din care să rezulte că livrarea de bunuri ori prestarea de servicii face obiectul unei scutiri.”
:::

Legea nu cere un cod tehnic anume — cere doar ca mențiunea de pe factură să arate, într-un fel sau altul, temeiul scutirii (articolul din Codul fiscal sau din Directiva 112).

## Ce ceri tehnic, în XML

Standardul folosit de RO e-Factura (UBL 2.1 / CIUS-RO) are, pentru operațiunile scutite, o categorie de TVA distinctă (categoria „E" — exempt) și un câmp separat pentru motivul scutirii, care poate fi exprimat fie ca text liber, fie printr-un cod tehnic din lista europeană **VATEX**, parte din specificația EN16931 pe care se bazează CIUS-RO. Acest cod tehnic e o convenție a standardului european, nu un act normativ românesc — nu are, ca atare, un temei separat în legislația fiscală de la noi, dincolo de obligația generală de la art. 319 alin. (20) lit. l) ca mențiunea să existe.

## Ce se greșește în practică

Se presupune că simpla cotă 0% de pe rândul facturii înlocuiește mențiunea de scutire — nu o înlocuiește. Categoria de cotă zero (folosită, de exemplu, pentru livrări intracomunitare sau export) și categoria de scutire propriu-zisă sunt, tehnic, lucruri diferite în standardul UBL, chiar dacă efectul pe suma de plată e același (TVA 0).

## Ce face iConta.eu

De spus fără ocolișuri: generatorul de XML pentru e-Factura (`core/efactura_send.py`) determină categoria de TVA strict din cota liniei facturii — „S" pentru cotă pozitivă, „Z" pentru cotă zero — și nu produce categoria „E" (exempt), nici un câmp de motiv al scutirii sau cod VATEX. Nu există, în tot codul aplicației, vreo logică sau vreun câmp legat de motivul scutirii. Nu e o opțiune ascunsă sau dezactivabilă — pur și simplu generatorul actual (v1) nu tratează acest caz. Dacă operațiunea ta chiar necesită mențiunea de motiv al scutirii în XML, transmiterea prin iConta.eu nu o acoperă în acest moment.

[iConta.eu](/)
