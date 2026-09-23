---
title: "e-Factura pentru livrări scutite: ce cod folosesc"
description: "Ce cere Codul fiscal pentru facturile cu operațiuni scutite de TVA și de ce, momentan, iConta nu generează un cod de motiv al scutirii în XML-ul e-Factura."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# e-Factura pentru livrări scutite: ce cod folosesc

Pentru o livrare scutită de TVA, factura trebuie să menționeze temeiul scutirii — dar în XML-ul e-Factura, standardul tehnic prevede și un cod distinct pentru motivul scutirii, separat de mențiunea din factura „pe hârtie".

## Temeiul legal

::: ghid-temei
„în cazul în care este aplicabilă o scutire de taxă, trimiterea la dispozițiile aplicabile din prezentul titlu ori din Directiva 112 sau orice altă mențiune din care să rezulte că livrarea de bunuri ori prestarea de servicii face obiectul unei scutiri;" — Codul fiscal, art. 319 alin. (20) lit. l), privind elementele obligatorii ale facturii
:::

Codul fiscal cere ca, pe orice factură pentru o operațiune scutită de TVA (art. 294 — scutiri cu drept de deducere, precum exportul sau livrările intracomunitare), să fie trecută trimiterea la dispoziția legală aplicabilă sau o altă mențiune din care să rezulte scutirea. Aceasta este cerința de conținut a facturii, indiferent de formatul ei.

## Ce se greșește în practică

Se presupune că, din moment ce factura circulă prin e-Factura, aplicația completează automat și codul tehnic de motiv al scutirii (codul „VATEX", din standardul european folosit de formatul XML al e-Facturii) — la fel cum completează cota de TVA sau tipul operațiunii.

## Ce face iConta.eu

La ora actuală, generatorul de XML pentru e-Factura din iConta produce doar **două** categorii de TVA în factura electronică: „S" (cotă standard) și „Z" (cotă zero). **Nu există o categorie dedicată de scutire („E") și nu există niciun câmp pentru codul de motiv al scutirii (VATEX)** în aplicație — această parte a standardului tehnic nu este încă implementată.

În practică, asta înseamnă că, pentru o livrare scutită (de exemplu export sau livrare intracomunitară), factura poate fi emisă și transmisă prin e-Factura, dar XML-ul generat nu poartă în acest moment codul tehnic de motiv al scutirii cerut de standardul UBL/CIUS-RO — doar clasificarea „standard"/„cotă zero". Mențiunea legală de pe factură (temeiul scutirii, conform art. 319 alin. 20) rămâne, desigur, obligatorie și trebuie verificată separat de contabil, indiferent de ce reține XML-ul.

Dacă aveți nevoie explicit de codul de motiv al scutirii în XML-ul transmis către SPV, această funcționalitate nu este disponibilă momentan în iConta — recomandăm verificarea directă cu echipa iConta pentru stadiul ei curent, înainte de a vă baza pe ea.

[iConta.eu](/)
