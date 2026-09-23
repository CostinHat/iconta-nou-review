---
title: "Cum fac prima factură în e-Factura"
description: Înainte de prima factură, cabinetul trebuie să autorizeze accesul la SPV și să aștepte fereastra de propagare de 24 de ore — apoi trimiterea trece prin patru verificări, în ordine, până la upload.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum fac prima factură în e-Factura

Prima factură are un pas în plus față de următoarele: autorizarea accesului la SPV, care se face o singură dată per certificat de cabinet. După acel pas, mecanismul de trimitere e identic pentru orice factură.

## Temeiul legal

::: ghid-temei
**OMFP nr. 660/2017** stabilește calitățile care dau acces la Spațiul Privat Virtual: „a) reprezentant legal ...; b) reprezentant desemnat ...", plus calitatea de împuternicit. Autorizarea acestor calități „se face prin intermediul aplicaţiilor informatice" puse la dispoziție de ANAF.

„În relaţia comercială B2B, între persoane impozabile stabilite în România ... emitentul facturii electronice are obligaţia de transmitere a acesteia către destinatar utilizând sistemul naţional privind factura electronică RO e-Factura." — OUG nr. 120/2021, art. 10 alin. (1), forma modificată prin Legea nr. 296/2023, art. LXV pct. 4.
:::

## Pasul 0: autorizarea accesului la SPV

Accesul la e-Factura se dă per certificat digital calificat al cabinetului, de către una din cele trei calități: reprezentant legal, reprezentant desemnat sau împuternicit. iConta nu deține propriul certificat — fiecare cabinet autorizează cu al lui, iar autorizarea acoperă toate CIF-urile pe care certificatul are drept declarat.

**Așteaptă circa 24 de ore** după înrolarea certificatului, înainte de prima trimitere reală — comportament observat constant al sistemului ANAF, nu o regulă scrisă într-un act normativ. O eroare de acces imediat după înrolare nu înseamnă neapărat că autorizarea a eșuat, poate fi doar fereastra de propagare.

## Pasul 1: generarea facturii

Factura se generează ca oricare altă factură din aplicație — cu datele complete ale clientului (CUI pentru persoană juridică) și, dacă firma sau clientul sunt în București, cu sectorul completat explicit (fără el, generarea e blocată, nu se trimit date presupuse).

## Pasul 2: trimiterea, cele patru verificări

**1. Conexiune activă la ANAF.** Fără un token valid pentru cabinet, trimiterea nu pornește.

**2. Validare de structură.** Factura e verificată la validatorul public ANAF înainte de orice upload. Dacă structura nu e conformă, nu se trimite nimic — primești mesajele exacte de eroare.

**3. Verificare că nu există deja o trimitere activă.** Protecție împotriva dublei trimiteri — upload-ul la ANAF nu e o operațiune sigură de repetat.

**4. Upload-ul propriu-zis.** Rezultatul — reușit sau eroare de încărcare — se scrie în evidență indiferent de cum a ieșit.

Semaforul de stare arată progresul: gri (netrimisă), galben (în curs de procesare la ANAF), verde (confirmată, cu recipisă), roșu (respinsă sau eroare).

## Termenul de transmitere

Din 1 ianuarie 2026, termenul e de 5 zile lucrătoare de la emitere, nu calendaristice — weekendurile și sărbătorile legale nu se numără.

## Ce se greșește în practică

- Se încearcă prima trimitere imediat după înrolarea certificatului, fără să se aștepte fereastra de propagare, și se interpretează eroarea ca „nu funcționează sistemul".
- Se confundă emiterea facturii (data de pe document) cu transmiterea ei prin sistem — termenul curge de la emitere.
- Se trimite o factură cu adresă incompletă pentru un client din București, fără să se știe că sistemul blochează trimiterea în loc să completeze un sector presupus.

## Ce face iConta.eu

Un singur ecran de conectare la ANAF, per cabinet — nu trebuie repetat pentru fiecare firmă administrată, doar verificat dreptul specific pentru fiecare CIF nou. La trimitere, nu lasă nimic să treacă nevalidat, nu permite o a doua trimitere peste una activă, și arată starea reală a fiecărei facturi cu semafor vizibil.

[iConta.eu](/)
