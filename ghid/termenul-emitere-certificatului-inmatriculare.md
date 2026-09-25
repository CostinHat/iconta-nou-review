---
title: "Termenul de emitere a certificatului de înmatriculare"
description: "Termenul legal în care organul fiscal eliberează certificatul de atestare fiscală solicitat de un contribuabil aflat sub inspecție fiscală, în vederea radierii din registrele în care a fost înregistrat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Termenul de emitere a certificatului de înmatriculare

Când o firmă supusă unei inspecții fiscale cere certificatul de atestare fiscală pentru a se radia (de exemplu din registrul comerțului, la dizolvare), Codul de procedură fiscală prevede un termen special, mai scurt decât termenul obișnuit de eliberare a certificatului — legat direct de finalizarea inspecției, nu de o cerere oarecare.

## Temeiul legal

::: ghid-temei
„(6) Prin excepție de la prevederile alin. (5), în situația contribuabilului/plătitorului supus unei inspecții fiscale și care solicită eliberarea unui certificat de atestare fiscală în scopul radierii din registrele în care a fost înregistrat, certificatul de atestare fiscală se emite în termen de 5 zile lucrătoare de la data emiterii deciziei de impunere sau a deciziei de nemodificare a bazei de impozitare, după caz."
— Legea 207/2015, art. 158 alin. (6) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Regula, aplicată la o firmă în inspecție care vrea să se radieze:

- Termenul de **5 zile lucrătoare** curge de la **data emiterii deciziei de impunere** (dacă inspecția a stabilit diferențe) sau de la **data deciziei de nemodificare a bazei de impozitare** (dacă inspecția nu a găsit diferențe) — nu de la data cererii de eliberare a certificatului.
- Acest termen e o **excepție** de la regula generală de eliberare a certificatului de atestare fiscală (termenul obișnuit, de la alin. (5)), aplicabilă exact scopului „radiere din registrele în care a fost înregistrat".
- Certificatul de atestare fiscală, în general, poate fi utilizat până la 30 de zile de la data eliberării (art. 158 alin. (5)) — termen extins la 90 de zile doar pentru persoanele fizice care nu desfășoară activități economice independente sau profesii libere, nu ca regulă generală. Dacă certificatul e cerut în scopul eșalonării la plată, eliberarea nu e supusă taxei extrajudiciare de timbru (art. 191 alin. (1)).

## Ce se greșește în practică

- Se calculează termenul de 5 zile de la **data depunerii cererii** de certificat, nu de la data deciziei de impunere/de nemodificare emise de organul de inspecție — cele două momente diferă, iar cererea poate fi depusă mai devreme sau mai târziu.
- Se presupune că orice cerere de certificat de atestare fiscală în timpul unei inspecții intră sub acest termen scurt de 5 zile — excepția se aplică strict scopului „radiere", nu oricărei cereri de certificat făcute în paralel cu un control.
- Se confundă certificatul de atestare fiscală (document fiscal, emis de ANAF pentru situația obligațiilor fiscale) cu certificate emise de alte instituții (de exemplu registrul comerțului) — sunt documente și proceduri diferite.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu depune și nu urmărește cereri de certificat de atestare fiscală** către ANAF — nu există în cod niciun modul care să genereze această cerere sau să calculeze termenul de 5 zile lucrătoare din art. 158 alin. (6). Aplicația are un modul real de conformare fiscală, `core/control_fiscal_api.py`, care urmărește declarațiile datorate versus cele depuse și semnalează neconformități, dar procedura de radiere și obținerea certificatului rămân în afara scopului actual al aplicației.

[iConta.eu](/)
