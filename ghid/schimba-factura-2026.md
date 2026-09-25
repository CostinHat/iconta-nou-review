---
title: "Ce se schimbă la e-Factura în 2026"
description: "Structura RO_CIUS și procedura RO e-Factura sunt reglementate prin ordin al ministrului finanțelor, iar orice schimbare pentru 2026 e ancorată tot într-un act publicat oficial, nu într-un anunț informal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce se schimbă la e-Factura în 2026

Sistemul RO e-Factura funcționează pe baza unui cadru legal care se poate modifica — procedura de utilizare, structura tehnică a facturii sau elementele obligatorii pot fi actualizate prin ordin al ministrului finanțelor. Ce contează, pentru orice firmă, e să știe unde anume trebuie căutată o schimbare oficială, nu să se bazeze pe zvonuri sau anunțuri neconfirmate.

## Temeiul legal

::: ghid-temei
„(4) Procedura de utilizare şi funcţionare a sistemului naţional privind factura electronică RO e-Factura se aprobă prin ordin al ministrului finanţelor în termen de 15 zile de la data publicării prezentei ordonanţe de urgenţă în Monitorul Oficial al României, Partea I.
[...]
(11) Prin ordin al ministrului finanţelor se reglementează specificaţiile tehnice şi de utilizare a elementelor de bază ale facturii electronice - RO_CIUS - şi regulile operaţionale specifice aplicabile la nivel naţional în termen de 15 zile de la data publicării prezentei ordonanţe de urgenţă în Monitorul Oficial al României, Partea I."
— OUG nr. 120/2021 privind Sistemul naţional privind factura electronică RO e-Factura, art. 3 alin. (4) și art. 4 alin. (11) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce se poate spune cert, pornind de la acest text, despre orice schimbare a sistemului în 2026:

- **Structura tehnică (RO_CIUS)** și **procedura de utilizare/funcționare** a sistemului RO e-Factura sunt reglementate exclusiv prin ordin al ministrului finanțelor — orice modificare reală trebuie să aibă un asemenea ordin publicat în Monitorul Oficial.
- Elementele obligatorii de bază ale unei facturi electronice (identificatori, date privind părțile, defalcarea TVA, totalul facturii) sunt enumerate explicit la art. 4 alin. (2) — o schimbare a acestei liste ar necesita, la rândul ei, o modificare a actului normativ care o stabilește.
- Verificarea "ce se schimbă" înseamnă, practic, urmărirea publicării de noi ordine ale ministrului finanțelor sau a unor acte care modifică OUG 120/2021, nu presupunerea unei schimbări pe baza unui anunț informal.

**Limitarea acestui ghid**: sursele verificate disponibile conțin forma OUG 120/2021 publicată inițial, iar un eventual ordin specific de modificare a schemei tehnice pentru anul 2026 nu se regăsește, ca atare, în corpusul consultat pentru acest ghid — recomandarea rămâne verificarea directă a ultimului ordin publicat de Ministerul Finanțelor/ANAF pentru versiunea curentă a schemei RO_CIUS.

## Ce se greșește în practică

- Se implementează o modificare de schemă pe baza unei discuții din comunitatea de contabili, fără confirmarea unui ordin oficial publicat.
- Se presupune că o schimbare de termene de raportare (de exemplu, la alte declarații conexe) înseamnă automat și o schimbare a structurii XML a facturii — cele două sunt reglementate, de regulă, prin acte separate.
- Se ignoră mesajele de eroare de validare la trimiterea facturilor, deși ele sunt primul semnal concret al unei schimbări de structură deja intrate în vigoare.

## Ce face iConta.eu

Generatorul de e-Factură din iConta.eu produce XML-ul pe structura curentă (UBL 2.1/CIUS-RO) și îl validează pe validatorul de structură ANAF înainte de trimitere — dacă schema s-a schimbat, factura respinsă la validare e primul semnal concret, verificat automat la fiecare trimitere. Actualizarea propriu-zisă a generatorului la o schemă nouă, atunci când ANAF publică o modificare, rămâne un proces intern al aplicației, declanșat la apariția noului ordin oficial, nu un mecanism de monitorizare proactivă a Monitorului Oficial.

[iConta.eu](/)
