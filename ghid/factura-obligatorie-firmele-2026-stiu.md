---
title: "e-Factura obligatorie pentru toate firmele în 2026: ce trebuie să știu"
description: "Extinderile aduse sistemului RO e-Factura pentru 2026 și termenele de conformare pentru firme și persoane fizice care desfășoară activități economice."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# e-Factura obligatorie pentru toate firmele în 2026: ce trebuie să știu

Obligativitatea RO e-Factura în relația B2B nu e o noutate a lui 2026 — ea există din 2024 pentru toate persoanele impozabile stabilite în România. Ce se schimbă începând cu 2026 este extinderea sferei de aplicare (către persoane impozabile nestabilite, dar înregistrate în scopuri de TVA în România) și fixarea unor termene stricte de înscriere în Registrul RO e-Factura obligatoriu, inclusiv pentru persoanele fizice care desfășoară activități economice identificate prin CNP.

## Temeiul legal

::: ghid-temei
„(1) În relația comercială B2B, între persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015 [...], pentru livrările de bunuri și prestările de servicii care au locul livrării/prestării în România [...], emitentul facturii electronice are obligația de transmitere a acesteia către destinatar utilizând sistemul național privind factura electronică RO e-Factura [...]."
— OUG 120/2021, art. 10 alin. (1), astfel cum a fost modificat prin OUG 138/2024, art. I pct. 2 (sursă: anaf_surse/oug_138_2024.txt)
:::

::: ghid-temei
„Furnizorii/Prestatorii care au obligația să respecte prevederile art. 5, art. 9^1, art. 10 alin. (1) și art. 10^1 alin. (2) [...] și care se identifică fiscal prin codul numeric personal, care au început să desfășoare activități economice anterior datei de 15 ianuarie 2026, au obligația de a solicita înscrierea în Registrul RO e-Factura obligatoriu înainte de această dată."
— OUG 89/2025, art. XI alin. (1) — dispoziție tranzitorie proprie a OUG 89/2025, care face trimitere la obligațiile din OUG 120/2021 (sursă: anaf_surse/oug_89_2025.txt)
:::

- Obligația B2B generalizată există deja din 2024 (OUG 120/2021, modificată prin OUG 138/2024) — practic toate firmele stabilite în România trebuie să transmită facturile emise prin RO e-Factura.
- OUG 89/2025 a completat art. 10 din OUG 120/2021 cu un nou alineat (1^1): obligația de transmitere prin RO e-Factura se extinde și la livrările/prestările efectuate către persoane impozabile nestabilite, dar înregistrate în scopuri de TVA în România.
- Aceeași ordonanță a introdus art. 10^10: furnizorii care se identifică fiscal prin CNP (persoane fizice care desfășoară activități economice) trebuie să solicite înscrierea în Registrul RO e-Factura obligatoriu înainte de a începe activitatea; cei deja activi înainte de 15 ianuarie 2026 trebuie să se înscrie până la această dată.
- Termenul-limită de transmitere a facturilor în sistem a fost precizat la 5 zile lucrătoare de la data emiterii (sau de la data-limită legală de emitere), calculat conform Regulamentului CEE nr. 1182/71.

## Ce se greșește în practică

- Se crede că „obligativitatea din 2026" e un termen nou, complet diferit de cel din 2024 — de fapt majoritatea firmelor sunt deja obligate din 2024; 2026 aduce extinderi punctuale (nestabiliți înregistrați TVA, PFA cu CNP).
- Se ignoră termenul de 15 ianuarie 2026 pentru înscrierea în Registrul RO e-Factura obligatoriu a furnizorilor identificați prin CNP, care riscă blocaje la transmiterea facturilor după această dată.
- Se confundă termenul de emitere a facturii (conform art. 319 din Codul fiscal) cu termenul de transmitere în RO e-Factura (5 zile lucrătoare, calculate distinct).

## Ce face iConta.eu

iConta.eu are integrare reală cu RO e-Factura: modulul `efactura_send.py` generează XML-ul UBL 2.1 / CIUS-RO și face upload-ul prin API-ul ANAF, modulul `spv_receive.py` rulează periodic (cron) și descarcă din SPV facturile primite de la furnizori, iar `efactura_import.py` este parserul care interpretează XML-ul UBL descărcat (extrage numărul, datele, părțile, sumele, liniile). Extinderile din 2026 discutate mai sus (persoane nestabilite înregistrate TVA, termenul de 15 ianuarie pentru furnizorii cu CNP) țin de sfera de aplicare a legii, nu de un modul separat — la verificarea codului nu există un tratament special pentru identificarea prin CNP în `efactura_send.py`; aplicația folosește același flux de trimitere/validare pentru toate facturile eligibile, indiferent de tipul de contribuabil.

[iConta.eu](/)
