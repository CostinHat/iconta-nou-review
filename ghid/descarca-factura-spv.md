---
title: De ce nu se descarcă factura din SPV
description: Verifică, în ordine, conexiunea SPV a cabinetului, CUI-ul firmei din profil și dacă factura a fost emisă efectiv către CIF-ul acestei firme — aplicația nu afișează încă o alertă dedicată pentru acest caz.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# De ce nu se descarcă factura din SPV

Când o factură pe care furnizorul spune că a trimis-o prin RO e-Factura nu apare în lista de validat, cauza e aproape întotdeauna una din câteva situații concrete, verificabile în ordine — nu un „bug” generic.

## Temeiul legal

::: ghid-temei
„Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul naţional privind factura electronică RO e-Factura. Destinatarul este notificat cu privire la facturile electronice primite (...) conform procedurii prevăzute la art. 3 alin. (4)."

— OUG nr. 120/2021, art. 4 alin. (7)
:::

Legea spune că factura e „primită” din momentul în care devine disponibilă pentru descărcare din SPV. Dacă acel moment încă nu s-a produs — sau dacă disponibilitatea ei nu ajunge la aplicație din alt motiv tehnic — factura pur și simplu nu apare, indiferent cât de sigur e furnizorul că a trimis-o corect.

## Ce verifici, în ordine

1. **Conexiunea SPV a cabinetului.** Procesul care descarcă facturile folosește autentificarea SPV la nivel de cabinet, nu de firmă. Dacă acea conexiune nu e activă sau tokenul a expirat, interogarea nici nu pornește pentru firmele cabinetului — fără să genereze o eroare vizibilă contabilului.
2. **CUI-ul firmei, în profil.** Dacă firma nu are CUI completat în profilul ei din aplicație, procesul nu are ce CIF să interogheze la ANAF pentru acea firmă și o sare, tot fără mesaj vizibil.
3. **CIF-ul real către care a fost emisă factura.** Dacă un cabinet gestionează mai multe firme, iar furnizorul a emis, din greșeală, factura către CIF-ul altei firme din același cabinet, aplicația **nu o importă** la firma ta — există un control explicit tocmai pentru a nu amesteca facturile firmelor din același cabinet. În acest caz, factura există în SPV, dar e legată de CIF-ul greșit.
4. **Conținutul arhivei descărcate.** Dacă arhiva primită de la ANAF pentru acel mesaj nu conține niciun fișier XML valid, descărcarea eșuează silențios pentru acea factură — se poate întâmpla, deși e rar.
5. **Eșecul HTTP la descărcare.** O eroare de rețea sau un răspuns gol la cererea de descărcare a unei facturi individuale nu oprește restul lotului — dar acea factură anume rămâne nedescărcată pentru rularea respectivă.

## Ce se greșește în practică

- Se presupune imediat că e o eroare a aplicației, fără să se verifice mai întâi conexiunea SPV a cabinetului — cea mai frecventă cauză reală.
- Se așteaptă o alertă automată (email sau notificare) când nu se descarcă nimic — nu există una dedicată pentru acest caz, spre deosebire de alte mecanisme SPV care alertează explicit la eșec de autentificare.
- Se ignoră posibilitatea ca factura să fi fost emisă către CIF-ul altei firme din același cabinet — o cauză frecventă când un cabinet gestionează mai multe firme.

## Ce face iConta.eu

Cronul de descărcare rulează la fiecare 30 de minute, cu o fereastră de interogare de 3 zile în urmă (suprapusă, nu doar „de la ultima rulare”), tocmai ca să tolereze eșecuri intermitente. Cauzele de mai sus sunt gestionate intern prin contorizare (nu opresc restul lotului), dar aplicația **nu afișează încă** aceste contoare într-un ecran dedicat contabilului și nu trimite o alertă automată când o firmă nu primește nicio factură nouă pentru o perioadă — la data acestei redactări, diagnosticarea se face manual, urmând pașii de mai sus.

[iConta.eu](/)
