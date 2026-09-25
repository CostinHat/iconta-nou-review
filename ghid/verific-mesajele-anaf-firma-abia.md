---
title: "Cum verific mesajele ANAF pentru o firmă abia înființată?"
description: "De ce o firmă nou-înființată trebuie să acceseze rapid Spațiul Privat Virtual, cu temeiul legal privind înregistrarea din oficiu și comunicarea prin publicitate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific mesajele ANAF pentru o firmă abia înființată?

O firmă abia înmatriculată presupune adesea că, până depune prima declarație, nu are de ce să verifice nimic la ANAF. De fapt, comunicarea electronică poate începe chiar din primele săptămâni, iar legea prevede o consecință dură pentru cine nu o verifică la timp.

## Temeiul legal

::: ghid-temei
„(16^1) În scopul comunicării actelor administrative prevăzute la alin. (16), organul fiscal central poate să înregistreze din oficiu contribuabilii/plătitorii în sistemul de comunicare electronică prin mijloace electronice de transmitere la distanță. Procedura de înregistrare din oficiu se aprobă prin ordin al președintelui A.N.A.F. (16^2) Comunicarea actelor administrative fiscale prevăzute la art. 46 alin. (6), pentru contribuabilii/plătitorii care au fost înregistrați din oficiu potrivit alin. (16^1) și nu au accesat sistemul de comunicare electronică în termen de 15 zile de la comunicarea datelor referitoare la înregistrare, se realizează doar prin publicitate potrivit alin. (5)-(7)."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 47 alin. (16^1) și (16^2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce înseamnă concret pentru o firmă nouă:

- ANAF poate înregistra **din oficiu** o firmă nou-înființată în sistemul de comunicare electronică (practic, în Spațiul Privat Virtual) — firma nu trebuie neapărat să inițieze ea acest proces pentru ca actele administrative fiscale să înceapă să-i fie adresate pe cale electronică.
- Dacă firma **nu accesează** sistemul în termen de **15 zile** de la comunicarea datelor de înregistrare, legea permite ca actele administrative fiscale să fie comunicate **doar prin publicitate** — adică printr-un anunț afișat la sediul organului fiscal și pe pagina de internet a ANAF, fără nicio altă notificare directă.
- Comunicarea prin publicitate se consideră efectuată la 15 zile de la afișarea anunțului (art. 47 alin. (7)) — indiferent dacă firma a văzut sau nu anunțul, actul produce efecte juridice, iar termenele curg de la acel moment.
- Practic, o firmă care nu verifică SPV în primele săptămâni de la înființare riscă să „piardă" comunicări oficiale (somații, decizii, cereri de clarificare) fără să știe, pentru că responsabilitatea de a verifica sistemul revine contribuabilului, nu invers.

## Ce se greșește în practică

- Se presupune că ANAF „nu are ce comunica" unei firme fără istoric, până la prima declarație depusă — înregistrarea din oficiu în sistemul electronic poate avea loc chiar de la înmatriculare.
- Se lasă contul SPV neaccesat luni de zile după înființare, considerându-l „pentru mai târziu" — termenul de 15 zile de la comunicarea datelor de înregistrare e scurt, iar depășirea lui deschide calea comunicării prin simplă publicitate.
- Se confundă „nu am primit nimic prin poștă" cu „nu am nimic de rezolvat" — pentru actele comunicate electronic sau prin publicitate, absența unei scrisori fizice nu înseamnă absența unei obligații legale în curs.

## Ce face iConta.eu

La data acestui ghid, iConta.eu preia și afișează mesajele primite prin conectorul propriu la Spațiul Privat Virtual, pentru fluxurile de e-Factura (`core/spv_receive.py`, `core/spv_poll.py`), dar nu monitorizează generic **toate** categoriile de acte administrative fiscale pe care ANAF le poate comunica unei firme — accesarea și verificarea periodică a secțiunii „Mesaje" din SPV rămân, în continuare, o responsabilitate directă a firmei sau a contabilului.

[iConta.eu](/)
