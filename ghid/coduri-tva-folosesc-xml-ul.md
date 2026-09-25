---
title: "Ce coduri de TVA se folosesc în XML-ul e-Factura?"
description: "Baza legală a formatului RO_CIUS pentru factura electronică și ce coduri de categorie TVA sunt implementate în prezent în generatorul XML al iConta.eu."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce coduri de TVA se folosesc în XML-ul e-Factura?

Fiecare linie și fiecare subtotal de TVA dintr-o factură electronică RO e-Factura poartă un cod de categorie de TVA — nu doar cota procentuală. Codul e obligatoriu pentru că formatul e construit pe un standard european, nu pe o convenție internă.

## Temeiul legal

::: ghid-temei
„j) standard european privind factura electronică - standard european special pentru modelul de date semantice privind elementele esențiale ale unei facturi electronice, astfel cum este definit la art. 2 alin. (1) lit. b) din Regulamentul (UE) nr. 1.025/2012;
k) specificațiile naționale de utilizare a facturii electronice - RO_CIUS - specificații tehnice de utilizare a elementelor de bază ale facturii electronice așa cum sunt prevăzute în standardul european SR EN 16931-1, aplicabile la nivel național."
— OUG 120/2021, art. 2 alin. (1) lit. j) și k) (sursă: anaf_surse/oug_120_2021.txt)
:::

Legea trimite direct la standardul tehnic (SR EN 16931-1, în specificația națională RO_CIUS) pentru elementele obligatorii ale facturii, inclusiv codul de categorie de TVA aplicat fiecărei linii și fiecărui subtotal — codul nu e o interpretare internă, ci o clasificare standardizată european. Practic, semnificația codului depinde de regimul de TVA al operațiunii facturate: cotă standard sau redusă, cotă zero, scutire, taxare inversă sau operațiune în afara sferei TVA sunt tratate diferit, fiecare cu codul ei propriu în standard.

## Ce se greșește în practică

- Se presupune că un singur cod de categorie de TVA acoperă toate situațiile (orice cotă redusă tratată la fel ca cea standard), fără să se distingă între operațiunile taxabile, cele scutite și taxarea inversă.
- Se confundă cota procentuală de TVA (câmpul `Percent`) cu codul de categorie (câmpul `ID`) din structura XML — sunt informații complementare, nu interschimbabile.
- Se emit facturi cu taxare inversă sau către beneficiari neplătitori de TVA presupunând că sistemul le tratează automat corect, fără verificarea explicită a suportului tehnic pentru acel caz.

## Ce face iConta.eu

La data acestui ghid, generatorul de XML e-Factura al iConta.eu (`core/efactura_send.py`) implementează **doar codurile de categorie TVA „S" (cotă standard sau redusă, pentru orice linie cu cotă mai mare de zero) și „Z" (cotă zero)** — conform comentariului explicit din cod: „Doar factura standard cu TVA (categorii S/Z). taxare_inversa (AE), neplatitor TVA (O), storno/nota de credit (381) NU sunt tratate în v1 - se adaugă după confirmare pe TEST." Concret:

- Pentru o factură cu **taxare inversă**, aplicația **refuză explicit generarea** — codul aruncă o eroare (`NotImplementedError`) dacă factura e marcată cu taxare inversă, în loc să genereze un XML cu cod de categorie greșit.
- Pentru facturi către **beneficiari neplătitori de TVA** (cod „O") sau pentru **storno/notă de credit**, generatorul nu are încă suport dedicat.

Această limitare e asumată și documentată direct în cod, nu ascunsă — dacă emiteți facturi cu taxare inversă sau storno prin e-Factura, verificați cu atenție rezultatul generat, iar pentru aceste cazuri, la data acestui ghid, procesul rămâne parțial manual.

[iConta.eu](/)
