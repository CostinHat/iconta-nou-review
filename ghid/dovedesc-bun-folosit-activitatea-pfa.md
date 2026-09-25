---
title: "Cum dovedesc că un bun este folosit în activitatea PFA"
description: "Condiția legală pentru deducerea cheltuielilor la PFA: justificarea prin documente că bunul este afectat activității independente, potrivit Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum dovedesc că un bun este folosit în activitatea PFA

Pentru un PFA care determină venitul net în sistem real (pe baza datelor din contabilitatea în partidă simplă), o cheltuială cu un bun (laptop, autoturism, mobilier, echipament) e deductibilă doar dacă poate fi legată, cu documente, de activitatea independentă. Legea nu cere un formular special, dar cere ca afectarea bunului activității să fie demonstrabilă, nu doar declarată.

## Temeiul legal

::: ghid-temei
„Condițiile generale pe care trebuie să le îndeplinească cheltuielile efectuate în scopul desfășurării activității independente, pentru a putea fi deduse, în funcție de natura acestora, sunt: a) să fie efectuate în cadrul activităților independente, justificate prin documente [...] i) cheltuielile efectuate pentru activitatea independentă, cât și în scopul personal al contribuabilului sau asociaților sunt deductibile numai pentru partea de cheltuială care este aferentă activității independente."
— Legea 227/2015, art. 68 alin. (4) lit. a) și alin. (5) lit. i) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă, în practică, „justificat prin documente":

- **Factura pe numele PFA** (cu CIF-ul/CNP-ul PFA-ului, nu al persoanei fizice) rămâne documentul de bază — fără ea, nici discuția despre afectare nu are unde să înceapă.
- **Declarația de afectare a bunului activității** — un document intern, semnat de titularul PFA, prin care bunul (mai ales dacă a fost cumpărat înainte de autorizare sau are și utilizare personală, cum e un autoturism) este menționat explicit ca fiind folosit în activitate; se păstrează alături de Registrul de evidență fiscală.
- **Documente de utilizare efectivă** — foaie de parcurs pentru autoturisme, contracte cu clienți care arată legătura dintre bun și activitatea desfășurată, fotografii/inventar pentru echipamente de lucru.
- Dacă bunul e folosit **și** personal **și** în activitate, doar partea aferentă activității e deductibilă (alin. (5) lit. i)) — proporția trebuie și ea documentată, nu estimată arbitrar.

## Ce se greșește în practică

- Se cumpără bunul pe numele persoanei fizice (nu al PFA) și se trece cheltuiala integral pe PFA, fără nicio declarație de afectare care să explice de ce un bun cumpărat „ca persoană fizică" servește activitatea independentă.
- Se deduce integral costul unui bun cu utilizare mixtă (laptop, telefon, autoturism) fără nicio documentare a proporției folosite în scop profesional.
- Se presupune că simpla evidențiere în Registrul-inventar e suficientă, fără păstrarea documentelor justificative care leagă efectiv bunul de activitatea desfășurată.

## Ce face iConta.eu

Pentru PFA, iConta.eu ține registrul de încasări și plăți (potrivit OMFP 170/2015) și permite clasificarea fiecărei plăți pe categorii — cheltuială deductibilă, cheltuială cu deductibilitate limitată sau cheltuială nedeductibilă (`core/rip_api.py`). La data acestui ghid, aplicația **nu verifică și nu generează documentele de afectare a bunului activității** — încadrarea unei cheltuieli ca deductibilă și păstrarea dovezilor (factură pe numele PFA, declarație de afectare, foaie de parcurs) rămân responsabilitatea titularului PFA sau a contabilului care operează în cont.

[iConta.eu](/)
