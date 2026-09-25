---
title: "Ce documente justifică deductibilitatea unei creanțe nerecuperabile?"
description: "Documentele care condiționează deductibilitatea 100% sau 30% a ajustării pentru deprecierea unei creanțe comerciale neîncasate, în funcție de situația juridică a debitorului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce documente justifică deductibilitatea unei creanțe nerecuperabile?

Deductibilitatea fiscală a unei creanțe neîncasate nu se stabilește pe baza convingerii contabilului că suma nu mai poate fi recuperată, ci strict pe baza documentelor care atestă situația juridică a debitorului. Fără documentul corect, ajustarea rămâne deductibilă doar parțial — sau deloc.

## Temeiul legal

::: ghid-temei
„ajustările pentru deprecierea creanțelor înregistrate potrivit reglementărilor contabile aplicabile, în limita unui procent de 100% din valoarea creanțelor, altele decât cele prevăzute la lit. d), e), f), h) și i), dacă creanțele îndeplinesc cumulativ următoarele condiții: 1. sunt deținute la o persoană juridică asupra căreia este declarată procedura de deschidere a falimentului, pe baza hotărârii judecătorești prin care se atestă această situație, sau la o persoană fizică asupra căreia este deschisă procedura de insolvență [...]"
— Legea nr. 227/2015 (Codul fiscal), art. 26 alin. (1) lit. j) pct. 1 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Documentele care fac diferența între deductibilitatea de 30% și cea de 100%:

- Pentru deducerea **integrală (100%)**, documentul obligatoriu este **hotărârea judecătorească** prin care se atestă deschiderea procedurii falimentului (pentru debitor persoană juridică) sau a insolvenței (pentru debitor persoană fizică) — fără acest act, creanța rămâne sub regimul general.
- Fără o astfel de hotărâre, ajustarea pentru deprecierea creanțelor comerciale (sume datorate de clienți pentru produse, mărfuri, lucrări sau servicii) rămâne deductibilă doar în **limita de 30%** din valoarea ajustării, potrivit regulii generale de la art. 26 alin. (1) lit. c).
- Alte cazuri reglementate separat, cu documente proprii, privesc pierderile din creanțele cesionate (deductibile în limita a 30% din diferența dintre prețul de cesiune și valoarea creanței) sau creanțele acoperite prin polițe de asigurare — fiecare cu regim și document justificativ distinct.

## Ce se greșește în practică

- Se deduce integral (100%) o creanță considerată „nerecuperabilă" pe baza unei simple notificări de neplată sau a unei corespondențe cu debitorul, fără hotărârea judecătorească de deschidere a falimentului/insolvenței.
- Se păstrează creanța nedepreciată în evidență, fără constituirea niciunei ajustări, deși documentele existente (chiar și fără hotărâre judecătorească) ar permite cel puțin deducerea de 30% aplicabilă regulii generale.
- Se scoate creanța direct din evidență ca pierdere definitivă, fără să se fi trecut întâi prin etapa de ajustare pentru depreciere, sărind astfel peste regimul fiscal aplicabil corect situației.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **calculează automat procentul de deductibilitate** al ajustării pentru deprecierea creanțelor (`core/provizioane.py`, funcția `deductibilitate_creanta`): pe baza numărului de zile de întârziere de la scadență și a răspunsurilor date de contabil — creanța e garantată, e la o persoană afiliată, există faliment/insolvență declarată — aplicația stabilește procentul corect (0%, 30% sau 100%, potrivit art. 26 lit. c)/j)) și generează nota contabilă de ajustare. Aplicația **nu verifică însă ea însăși existența sau conținutul hotărârii judecătorești** de deschidere a falimentului/insolvenței — confirmarea faptului că un astfel de document există și susține procentul de 100% rămâne o constatare a contabilului, introdusă ca atare în aplicație.

[iConta.eu](/)
