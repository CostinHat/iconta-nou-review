---
title: Cum emit o factură scutită de TVA în e-Factura?
description: Legea cere ca orice factură scutită să poarte mențiunea temeiului scutirii (art. 319 alin. 20 lit. l). În acest moment, generatorul XML al iConta.eu nu produce categoria de scutire și nici câmpul de motiv — o limitare v1, nu o funcționalitate ascunsă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum emit o factură scutită de TVA în e-Factura?

Răspunsul cinstit are două părți: ce spune legea despre o factură scutită, și ce poate genera în acest moment aplicația. Le tratăm separat, ca să nu-ți promitem un comportament pe care iConta.eu nu-l are încă.

## Temeiul legal

::: ghid-temei
**Art. 294 din Codul fiscal** — scutirile cu drept de deducere: exporturile, livrările intracomunitare de bunuri și alte operațiuni asimilate.

**Art. 319 alin. (20) lit. l) din Codul fiscal**: „în cazul în care este aplicabilă o scutire de taxă, trimiterea la dispozițiile aplicabile din prezentul titlu ori din Directiva 112 sau orice altă mențiune din care să rezulte că livrarea de bunuri ori prestarea de servicii face obiectul unei scutiri.”
:::

Legea nu cere doar cota 0% pe rândul facturii — cere o **mențiune explicită**, cu trimitere la textul de lege sau la Directiva 112, care să arate de ce operațiunea e scutită.

## Ce poți face azi în iConta.eu

Dacă operațiunea e scutită **cu cotă 0%** — de exemplu o livrare intracomunitară sau un export, unde cota facturii e efectiv 0 — poți introduce factura cu această cotă, iar generatorul XML o transmite normal, în categoria de cotă zero prevăzută de standardul UBL/CIUS-RO folosit de RO e-Factura.

Ce **nu** face aplicația, la acest moment: nu generează un câmp separat cu mențiunea legală a scutirii (trimiterea la art. 294 sau la alt temei, cerută de art. 319 alin. 20 lit. l) și nu are o categorie tehnică distinctă pentru operațiuni scutite fără drept de deducere. Generatorul XML actual (`v1`) lucrează doar cu două categorii — cotă standard și cotă zero — determinate strict din cota facturii, fără un câmp separat pentru motivul scutirii.

## Ce se greșește în practică

Se presupune că o factură cu cota 0% e, prin ea însăși, completă din punct de vedere legal pentru o operațiune scutită — nu e. Fără mențiunea explicită a temeiului scutirii (cerută separat de art. 319 alin. 20 lit. l), factura poate fi considerată incompletă la un control, chiar dacă baza de impozitare și cota sunt corecte.

## Ce face iConta.eu

De spus clar, ca să nu induci în eroare beneficiarul facturii sau propriul dosar de conformitate: generatorul de XML pentru e-Factura (`core/efactura_send.py`) produce în acest moment doar categoria „S" (standard) pentru cotă pozitivă și „Z" (cotă zero) pentru cotă 0%, fără un câmp de motiv al scutirii. Emiterea unei facturi cu cotă 0% și transmiterea ei prin e-Factura funcționează; adăugarea mențiunii legale a scutirii, cerută de art. 319 alin. (20) lit. l), nu e acoperită de aplicație la acest moment — nu există un câmp dedicat, iar generatorul XML nu-l poate produce. E o limitare cunoscută a versiunii curente, nu o funcționalitate ascunsă sau dezactivată; dacă mențiunea explicită îți e necesară pe acea factură, contactează suportul iConta.eu înainte de a te baza pe acest flux pentru operațiuni scutite care o cer.

[iConta.eu](/)
