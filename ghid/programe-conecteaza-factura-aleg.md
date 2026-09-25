---
title: "Programe care se conectează la e-Factura: cum aleg"
description: "Ce obligații legale trebuie să acopere un program conectat la sistemul RO e-Factura și pe ce criterii se alege un astfel de software."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Programe care se conectează la e-Factura: cum aleg

Transmiterea facturilor prin sistemul național RO e-Factura este obligatorie pentru majoritatea operatorilor economici din România, indiferent dacă lucrează cu un program de facturare, un ERP sau depun manual în Spațiul Privat Virtual. Alegerea unui program potrivit înseamnă, în primul rând, să te asiguri că acesta respectă termenele și formatul impuse de lege — restul (interfață, preț, integrări) e o chestiune secundară de confort.

## Temeiul legal

::: ghid-temei
„(1) În relația comercială B2B, între persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015 [...], pentru livrările de bunuri și prestările de servicii care au locul livrării/prestării în România [...], emitentul facturii electronice are obligația de transmitere a acesteia către destinatar utilizând sistemul național privind factura electronică RO e-Factura [...]."
— OUG 120/2021 privind sistemul național RO e-Factura, art. 10 alin. (1), astfel cum a fost modificat prin OUG 138/2024, art. I pct. 2 (sursă: anaf_surse/oug_138_2024.txt)
:::

Legea stabilește și termenul-limită pe care orice program folosit pentru emitere trebuie să-l respecte:

::: ghid-temei
„Termenul-limită pentru transmiterea facturilor în sistemul național privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită pentru emiterea facturii prevăzută la art. 319 alin. (16) din Legea nr. 227/2015 [...]."
— OUG 120/2021, art. 10 alin. (7), astfel cum a fost modificat prin OUG 89/2025, art. X pct. 2 (sursă: anaf_surse/oug_89_2025.txt)
:::

Din aceste texte rezultă criteriile legale minime pe care un program de facturare trebuie să le acopere, indiferent de furnizor:

- **Generarea facturii în formatul electronic standard** acceptat de sistem (structura UBL 2.1 / CIUS-RO), nu doar un PDF sau o factură tipărită.
- **Transmiterea propriu-zisă** către sistemul RO e-Factura, fie prin API direct, fie prin încărcare manuală asistată — cu respectarea termenului de 5 zile lucrătoare.
- **Confirmarea stării mesajului** (acceptat, respins, eroare de validare) — nerespectarea termenului sau transmiterea unei facturi invalide poate atrage amenzi (Legea nr. 296/2023, art. LIX alin. (7) prevede sancțiuni între 1.000 și 10.000 lei, în funcție de categoria contribuabilului).
- **Arhivarea facturilor transmise**, întrucât obligația de stocare a documentelor fiscale rămâne valabilă indiferent de canalul de transmitere.

## Ce se greșește în practică

- Se alege un program doar pe criterii de preț sau interfață, fără să se verifice dacă generează corect formatul UBL 2.1 cerut de sistem, ceea ce duce la respingeri repetate ale facturilor.
- Se ignoră termenul de 5 zile lucrătoare și se transmit facturile în lot, la sfârșit de lună — depășirea termenului pentru o singură factură poate atrage amendă, chiar dacă restul facturilor lunii au fost transmise corect.
- Se presupune că un program „conectat la e-Factura" transmite automat, fără intervenție — unele soluții doar generează XML-ul și lasă utilizatorul să îl încarce manual în SPV, ceea ce schimbă radical fluxul de lucru zilnic.
- Nu se verifică dacă programul păstrează un istoric interogabil al stărilor de transmitere (accept/respins), necesar în caz de control sau litigiu cu un partener despre primirea facturii.

## Ce face iConta.eu

iConta.eu are propriul modul de conectare la RO e-Factura: generează factura direct în formatul XML UBL 2.1/CIUS-RO cerut de ANAF, o validează structural, o încarcă în sistem prin API și verifică ulterior starea mesajului (acceptat/respins/eroare), toate din interiorul aplicației, fără a fi nevoie de încărcare manuală separată în SPV. Practic, iConta.eu este el însuși unul dintre programele descrise mai sus — utilizatorii care compară soluții pot verifica exact aceste criterii (format corect, transmitere automată, urmărire a stării) și pentru orice altă alternativă pe care o iau în calcul.

[iConta.eu](/)
