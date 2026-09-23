---
title: Cum se repartizează cheltuielile indirecte între mai multe șantiere?
description: iConta.eu nu calculează automat cheia de repartizare a cheltuielilor indirecte — contabilul o stabilește și înregistrează rezultatul printr-o notă manuală, cu linii separate pe centrul de cost al fiecărui șantier.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se repartizează cheltuielile indirecte între mai multe șantiere?

Cheltuielile indirecte (de exemplu chiria unui depozit comun, combustibilul unui utilaj partajat, costuri administrative de șantier) nu aparțin în întregime unui singur șantier, ci trebuie împărțite după o cheie stabilită de contabil — proporțional cu manopera, cu valoarea lucrării, cu suprafața sau orice alt criteriu relevant pentru firmă.

## Temeiul legal

::: ghid-temei
„(6) Persoanele prevăzute la alin. (1)-(4) organizează și conduc, după caz, și contabilitatea de gestiune, potrivit reglementărilor elaborate în acest sens."

— Legea contabilității nr. 82/1991, art. 1 alin. (6)
:::

Repartizarea cheltuielilor indirecte pe centre de cost este contabilitate de gestiune, fără o formă sau o cheie de repartizare impusă de lege. Alegerea criteriului de repartizare (manoperă, suprafață, valoare etc.) este o decizie de management, nu una de conformare fiscală.

## Ce se greșește în practică

- Se așteaptă ca aplicația să calculeze singură procentele de repartizare — iConta.eu nu are un motor automat de repartizare a cheltuielilor indirecte; nu există o funcționalitate de acest tip.
- Se lasă cheltuielile indirecte „nealocate" din comoditate — raportul „realizat pe centru" arată separat suma nealocată, deci lipsa repartizării se vede, nu dispare.
- Se repartizează cheltuiala direct pe conturile de cheltuială, fără să fie legată de niciun centru de cost — rezultatul e că centrele de cost nu reflectă costul real al fiecărui șantier.

## Ce face iConta.eu

iConta.eu nu calculează cheia de repartizare — asta rămâne decizia contabilului, făcută în afara aplicației (de exemplu într-un calcul separat, pe baza criteriului ales). Ce oferă aplicația este mecanismul de a înregistra rezultatul: o notă manuală în Registrul jurnal, în care fiecare linie poartă centrul de cost al șantierului căruia îi este alocată o parte din cheltuiala indirectă, cu suma corespunzătoare procentului stabilit. O singură notă poate distribui aceeași cheltuială pe mai multe șantiere, câte o linie pentru fiecare.

După înregistrare, raportul „realizat pe centru" arată suma alocată fiecărui șantier (din liniile clasei 6, pe note validate), iar linia „nealocat" arată tot ce nu a fost încă repartizat — util ca semnal că repartizarea nu e completă, nu ca defect al aplicației.

[iConta.eu](/)
