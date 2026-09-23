---
title: Înființare firmă nouă și contractul de mandat pentru administrator
description: Administratorul unei firme noi e, implicit, remunerat printr-un contract de mandat, nu prin CIM — regimul fiscal e diferit de la prima indemnizație plătită.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Înființare firmă nouă și contractul de mandat pentru administrator

La înființarea unei firme, administratorul desemnat prin actul constitutiv e legat de societate printr-un contract de mandat, nu printr-un contract individual de muncă — chiar dacă e și asociat unic. Dacă societatea decide să-i plătească o indemnizație de administrare, aceasta intră de la prima plată în regimul fiscal specific mandatului, nu în cel de salarizare clasică.

## Temeiul legal

::: ghid-temei
„remunerația administratorilor societăților, companiilor/societăților naționale și regiilor autonome, desemnați/numiți în condițiile legii, precum și sumele primite de reprezentanții în adunarea generală a acționarilor și în consiliul de administrație"

*(Codul fiscal — Legea nr. 227/2015, art. 76 alin. (2) lit. o))*
:::

## Ce trebuie stabilit de la înființare

- **Nivelul indemnizației** — legea nu impune un nivel minim al remunerației de mandat, spre deosebire, de exemplu, de zilieri, unde există un prag orar minim legal explicit (Legea 52/2011). Remunerația administratorului se stabilește liber, prin actul constitutiv sau prin hotărârea adunării generale.
- **Taxele datorate, de la prima plată**: CAS 25% + CASS 10% + impozit pe venit 10% pe rest, fără contribuția asiguratorie pentru muncă (CAM) — pentru că mandatul nu e raport de muncă.
- **Contul contabil folosit** — indemnizația trece prin 621 (cheltuieli cu colaboratorii), nu prin 641.

## Ce se greșește în practică

- Se presupune, la o firmă nou-înființată, că administratorul unic (mai ales dacă e și asociat unic) „nu are voie" sau „nu trebuie" să fie remunerat, și se amână orice discuție despre taxe — decizia de remunerare rămâne opțională, dar dacă există plată, taxele de mai sus se aplică de la prima sumă.
- Se stabilește o indemnizație fixă „la nivelul salariului minim", din prudență, fără să existe de fapt o obligație legală în acest sens pentru contractul de mandat.
- Se tratează administratorul, din start, ca angajat cu CIM, pentru „simplitate" — ceea ce adaugă greșit CAM și schimbă temeiul legal aplicabil.

## Ce face iConta.eu

Modulul F021 (`core/contracte_speciale.py`) oferă, prin ecranul „Contracte speciale (zilieri, mandat, cenzori)", tipul „Mandat administrator" chiar din prima lună de activitate a firmei — cu calculul CAS 25% + CASS 10% + impozit 10% pe rest, fără CAM, și nota contabilă prin 621. O limitare de reținut de la înființare: generarea D112 din aplicație nu are, la acest moment, o legătură funcțională cu notele de mandat — declararea corectă a administratorului la D112 (categoria „tip asigurat" 6) rămâne un pas separat.

[iConta.eu](/)
