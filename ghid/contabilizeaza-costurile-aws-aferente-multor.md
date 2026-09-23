---
title: Cum se contabilizează costurile AWS aferente mai multor proiecte?
description: Factura AWS se înregistrează ca orice altă cheltuială de clasa 6, iar repartizarea ei pe proiecte se face prin centrul de cost, atribuit pe linie — automat doar dacă nota e introdusă manual, altfel printr-o repartizare ulterioară.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se contabilizează costurile AWS aferente mai multor proiecte?

O factură lunară de la AWS care acoperă infrastructura mai multor proiecte ridică aceeași problemă ca orice cheltuială comună: contabilizarea propriu-zisă (înregistrarea facturii) este un pas, iar repartizarea costului pe proiecte este alt pas, separat.

## Temeiul legal

::: ghid-temei
„(6) Persoanele prevăzute la alin. (1)-(4) organizează și conduc, după caz, și contabilitatea de gestiune, potrivit reglementărilor elaborate în acest sens."

— Legea contabilității nr. 82/1991, art. 1 alin. (6)
:::

Repartizarea costurilor cloud pe proiecte este contabilitate de gestiune — nu există o cerință legală privind modul de alocare a unei facturi de servicii cloud pe centre interne de cost; e o decizie de management, motivată de nevoia de a cunoaște costul real al fiecărui proiect.

## Ce se greșește în practică

- Se înregistrează toată factura AWS pe o singură cheltuială generală, fără nicio repartizare — costul real al fiecărui proiect rămâne necunoscut.
- Se așteaptă ca repartizarea pe proiecte să se facă automat din factură — dacă factura intră prin fluxul automat de procesare a facturilor, nota rezultată nu primește centru de cost implicit; alocarea rămâne un pas manual.
- Se repartizează costul în mod egal între toate proiectele, indiferent de consumul real — dacă billing-ul AWS permite defalcarea pe proiect (tag-uri, conturi separate), o repartizare proporțională cu consumul reflectă mai corect realitatea decât o împărțire egală.

## Ce face iConta.eu

Cheltuiala cu factura AWS se înregistrează contabil ca orice altă cheltuială de servicii (clasa 6). Pentru repartizarea ei pe proiecte, contabilul stabilește — pe baza detalierii de consum din billing-ul AWS, calculată în afara aplicației — suma sau procentul cuvenit fiecărui proiect și înregistrează (sau editează) o notă manuală în Registrul jurnal, cu câte o linie pentru centrul de cost al fiecărui proiect implicat.

Raportul „realizat pe centru" arată apoi costul de infrastructură alocat fiecărui proiect, pentru orice interval de date ales, incluzând linia „nealocat" pentru partea nerepartizată. Dacă factura vine prin fluxul automat de procesare a facturilor, repartizarea pe centre rămâne un pas separat, ulterior — notele generate automat nu poartă centru de cost.

[iConta.eu](/)
