---
title: Cum se completează D390 pentru prima operațiune intracomunitară?
description: La prima operațiune intracomunitară trebuie identificat tipul corect (L/T/A/P/S/R), verificat codul de TVA al partenerului și, dacă e vorba de servicii, marcată explicit factura ca atare — altfel aplicația o clasifică implicit ca bun (livrare sau achiziție).
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se completează D390 pentru prima operațiune intracomunitară?

Prima livrare sau achiziție intracomunitară dintr-o firmă ridică, de regulă, mai multe întrebări deodată: ce tip de operațiune e, până când trebuie depusă declarația și cum apare corect în aplicație. Ghidul de mai jos parcurge pașii esențiali.

## Temeiul legal

::: ghid-temei
**Art. 325 alin. (1)**: „(1) Orice persoană impozabilă înregistrată în scopuri de TVA conform art. 316 sau 317 trebuie să întocmească și să depună la organele fiscale competente o declarație recapitulativă în care menționează: a) livrările intracomunitare scutite de taxă [...]; b) livrările de bunuri efectuate în cadrul unei operațiuni triunghiulare [...] cu cod T [...]; c) prestările de servicii prevăzute la art. 278 alin. (2) efectuate în beneficiul unor persoane impozabile nestabilite în România, dar stabilite în Uniunea Europeană [...]; d) achizițiile intracomunitare de bunuri taxabile [...]; e) achizițiile de servicii prevăzute la art. 278 alin. (2), efectuate de persoane impozabile din România care au obligația plății taxei conform art. 307 alin. (2) [...] de la persoane impozabile nestabilite în România, dar stabilite în Uniunea Europeană. f) livrările intracomunitare de bunuri prevăzute la art. 315^1 alin. (8) lit. c) și d)."

**OPANAF 705/2020, anexa 2, pct. 1.1**: „Declarația recapitulativă se depune lunar, în condițiile prevăzute la art. 325 din Legea nr. 227/2015 privind Codul fiscal, cu modificările și completările ulterioare (Codul fiscal), până la data de 25 inclusiv a lunii următoare unei luni calendaristice, de către persoanele impozabile înregistrate în scopuri de TVA conform art. 316 sau 317 din Codul fiscal."
:::

## Pașii pentru prima operațiune

**1. Identifică tipul corect al operațiunii.** Nomenclatorul D390 are șase coduri: L (livrări de bunuri), T (livrări în operațiune triunghiulară), A (achiziții de bunuri), P (prestări de servicii), S (achiziții de servicii) și R (livrări de bunuri, regim special agricultori). Direcția facturii decide jumătatea din care poate face parte: o factură emisă poate deveni doar L, T, P sau R; o factură primită poate deveni doar A sau S — niciodată invers.

**2. Verifică dacă operațiunea e bun sau serviciu.** Implicit, orice factură e tratată ca bun: emisă → L, primită → A. Dacă operațiunea e de fapt un serviciu (consultanță, SaaS, licențe etc.), trebuie marcată explicit ca atare la introducere, altfel rămâne greșit clasificată ca bun.

**3. Verifică codul de TVA al partenerului.** Un cod invalid nu blochează raportarea, dar poate afecta scutirea de TVA a livrării, dacă e vorba de o livrare (vezi temeiul art. 294 alin. (2^1), tratat separat).

**4. Reține termenul.** Declarația pentru luna în care a avut loc prima operațiune se depune până pe 25 ale lunii următoare, indiferent de periodicitatea TVA a firmei (lunară sau trimestrială).

## Ce se greșește în practică

- Se presupune că D390 se depune doar dacă firma are deja experiență cu operațiuni intracomunitare frecvente — de fapt, obligația apare din prima lună cu o astfel de operațiune, oricât de mică.
- Se lasă factura fără marcaj de „servicii" atunci când operațiunea e de fapt o prestare/achiziție de servicii, iar aceasta apare implicit ca bun.
- Se introduc din greșeală operațiuni cu parteneri din Marea Britanie (cod GB) ca și cum ar fi operațiuni intracomunitare obișnuite — legal, operațiunile cu parteneri din Regatul Unit nu se raportează în D390, cu excepția transporturilor de bunuri în/din Irlanda de Nord (cod XI).
- Nu se verifică dacă partenerul e efectiv înregistrat în scopuri de TVA în UE, presupunând că orice firmă europeană se califică automat.
- Se așteaptă să acumuleze mai multe operațiuni înainte de a depune prima D390, depășind astfel termenul de 25 ale lunii următoare.

## Ce face iConta.eu

Aplicația verifică automat existența a cel puțin unei operațiuni intracomunitare (L/T/A/P/S/R) pentru luna selectată — dacă nu există nicio operațiune, generarea declarației e refuzată explicit, cu temei citat direct în mesaj (OPANAF 705/2020 pct. 1.2, art. 325 Cod fiscal). Clasificarea automată se face pe baza direcției documentului (emisă → L implicit, primită → A implicit); pentru servicii, factura trebuie marcată cu axa „servicii" la introducere, sau reclasificată manual în ecranul D390. Codul de țară al partenerului e validat împotriva listei de state UE folosite de validator, inclusiv codurile GB și XI — dar acceptarea structurală a codului GB de către validator nu înlocuiește verificarea legală: operațiunile cu Marea Britanie, cu excepția celor cu Irlanda de Nord, rămân excluse legal din D390.

[iConta.eu](/)
