---
title: "Noutăți 2026 la digitalizarea ANAF: e-Factura, e-TVA, e-Transport"
description: "Termenul de transmitere pentru RO e-Factura, calendarul suspendării RO e-TVA și mecanismul codului UIT la RO e-Transport, valabile în 2026."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Noutăți 2026 la digitalizarea ANAF: e-Factura, e-TVA, e-Transport

Trei dintre sistemele digitale ale ANAF au reguli care s-au schimbat sau au ajuns la un moment de tranziție în 2026: termenul de transmitere pentru RO e-Factura a rămas la 5 zile lucrătoare, dar cu un calcul precizat legal; suspendarea unor obligații RO e-TVA a încetat pentru majoritatea contribuabililor la 1 ianuarie 2026, dar a fost prelungită separat pentru plătitorii de TVA la încasare; iar RO e-Transport continuă să funcționeze pe codul UIT, valabil 5 zile calendaristice de la generare.

## Temeiul legal

::: ghid-temei
„Termenul-limită pentru transmiterea facturilor în sistemul național privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită pentru emiterea facturii prevăzută la art. 319 alin. (16) din Legea nr. 227/2015 [...]. Calculul termenului-limită se efectuează conform Regulamentului (CEE, Euratom) nr. 1182/71 al Consiliului din 3 iunie 1971 privind stabilirea regulilor care se aplică termenelor, datelor și expirării termenelor."
— OUG 89/2025, art. X pct. 2 (modifică art. 10 alin. (7) din OUG 120/2021) (sursă: anaf_surse/oug_89_2025.txt)
:::

Pentru RO e-TVA, textul distinge două situații:

- **Regula generală**: „suspendarea prevederilor din Ordonanța de urgență a Guvernului nr. 70/2024 [...] care reglementează transmiterea răspunsurilor de către contribuabili la «Notificarea de conformare RO e-TVA», precum și a celor referitoare la transmiterea acestei notificări către persoanele impozabile care aplică sistemul TVA la încasare încetează la data de 1 ianuarie 2026" (OUG 89/2025).
- **Excepția TVA la încasare**: „În cazul persoanelor impozabile care aplică sistemul TVA la încasare conform art. 282 alin. (3)-(8) din Legea nr. 227/2015, aplicarea dispozițiilor art. 5 și 8 din Ordonanța de urgență a Guvernului nr. 70/2024 [...] se suspendă până la data de 30 septembrie 2026" (OUG 89/2025) — pentru acest grup, obligația de a răspunde la notificarea de conformare rămâne suspendată câteva luni în plus față de restul contribuabililor.

Pentru RO e-Transport, mecanismul de bază (necontestat, în vigoare) e codul UIT:

::: ghid-temei
„11. cod UIT - codul unic generat de Sistemul RO e-Transport prin intermediul căruia se identifică bunurile aferente fiecărei relații comerciale care face obiectul transportului de bunuri cu risc fiscal ridicat; [...]
(2) Termenul de valabilitate a codului UIT este de 5 zile calendaristice, începând cu data declarată pentru începerea transportului [...]"
— OUG 41/2022, art. 2 pct. 11 și art. 11 alin. (2) (sursă: anaf_surse/oug_41_2022.txt)
:::

## Ce se greșește în practică

- Se calculează termenul de 5 zile lucrătoare de la data emiterii facturii fără să se verifice și limita a doua din text — „nu mai târziu de 5 zile lucrătoare de la data-limită pentru emiterea facturii" — care poate scurta termenul efectiv dacă factura a fost emisă cu întârziere față de operațiune.
- Se presupune că, de la 1 ianuarie 2026, toți contribuabilii răspund la notificările de conformare RO e-TVA — pentru plătitorii de TVA la încasare, obligația respectivă rămâne suspendată până la 30 septembrie 2026.
- Se lasă un cod UIT „deschis" mai mult de 5 zile calendaristice, presupunând că rămâne valabil pe toată durata efectivă a transportului — valabilitatea legală expiră strict la 5 zile de la data declarată de start.

## Ce face iConta.eu

**e-Factura SPV complet (F126)**: aplicația trimite automat facturile emise în SPV, cu reîncercare la indisponibilitate ANAF, și urmărește starea trimiterii (recipisă/erori); primește și facturile de la furnizori din SPV, transformându-le automat în ciornă de NIR/cheltuială, validată însă de om (mecanism „four-eyes": mașina propune, contabilul confirmă contul și validează).

**e-Transport (F121)**: iConta.eu generează și trimite codul UIT prin API SPV, cu o „gardă de timp" proprie — cererea e blocată în afara ferestrei legale (UIT declarat cu maximum 3 zile înainte, valabil 5 zile pentru transport național / 15 zile pentru cel intracomunitar), iar după expirare declanșarea trimiterii e blocată explicit, cu motivul afișat.

**e-TVA**: nu am identificat, în cercetarea pentru acest ghid, un modul dedicat de generare sau răspuns automat la notificarea de conformare RO e-TVA în iConta.eu — regulile de mai sus rămân, pentru moment, informație de conformitate pe care contabilul o gestionează prin canalele oficiale ANAF.

Notă: funcționalitatea din spatele acestui ghid, F060 (Monitor fiscal), e un mecanism intern — un cron săptămânal care citește noutățile ANAF/MF și trimite un rezumat filtrat prin email către administratorul aplicației. Nu e un modul orientat spre contabil și nu generează automat conținut vizibil în aplicație; rezumatul de mai sus e redactat manual, pe bază de surse legale verificate, nu produs de acel cron.

[iConta.eu](/)
