---
title: Cum se reconciliază decontul marketplace-ului când include vânzări, retururi, comisioane și penalități?
description: Decontul net al platformei se descompune în elementele lui brute, fiecare înregistrat separat, iar abia apoi se face compensarea (OMFP 1802/2014, pct. 56). Vânzările și retururile ajustează venitul și TVA colectată (Codul fiscal art. 287), comisionul este cheltuială cu TVA sau cu taxare inversă, iar penalitatea rămâne în afara TVA (art. 286 alin. (4) lit. b)).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se reconciliază decontul marketplace-ului când include vânzări, retururi, comisioane și penalități?

Suma virată de marketplace este un net: încasările de la clienți, minus retururile, comisioanele și penalitățile. Nu înregistrați netul ca venit. Descompuneți decontul pe elemente, înregistrați fiecare element brut, cu documentul lui, și abia apoi compensați. Reconcilierea este reușită când contul de decontare cu platforma ajunge la zero.

### De ce nu se înregistrează netul

OMFP nr. 1802/2014, pct. 56 alin. (1), interzice „orice compensare [...] între elementele de venituri și cheltuieli". Alin. (3) permite compensările legale între creanțe și datorii față de aceeași entitate numai după contabilizarea creanțelor și veniturilor, respectiv a datoriilor și cheltuielilor. Dacă înregistrați doar netul, vânzările sunt subevaluate, iar comisionul și TVA-ul aferent dispar din evidență.

### Cele patru elemente și tratamentul lor

- **Vânzări.** Sunt deja înregistrate din facturile sau bonurile emise de dumneavoastră, la valoarea plătită de client. În decont le verificați comandă cu comandă.
- **Retururi.** Pentru bunurile returnate și rambursate, baza de impozitare se reduce (Codul fiscal art. 287 lit. b)). Înregistrați stornarea venitului și a TVA-ului pe baza facturii de stornare, iar bunul revine în stoc.
- **Comisioane.** Sunt serviciu prestat de platformă, înregistrat în 622 „Cheltuieli privind comisioanele și onorariile", pe baza facturii platformei. O platformă din România facturează cu TVA. Pentru o platformă din alt stat membru, locul prestării este la sediul dumneavoastră (art. 278 alin. (2)), iar TVA se plătește prin taxare inversă (art. 307 alin. (2)).
- **Penalități.** Se înregistrează în 6581 și nu intră în baza TVA dacă sancționează neîndeplinirea contractului (art. 286 alin. (4) lit. b)). Verificați totuși să nu fie, de fapt, plata unui serviciu, de exemplu depozitare sau procesarea returului.

### Exemplu

Decontul pe august al unei platforme din România arată:

- vânzări: 50.000 lei, cu TVA 21% inclusă;
- retururi rambursate: 3.000 lei, cu TVA inclusă;
- comision: 5.000 lei + 1.050 lei TVA, conform facturii platformei;
- penalitate pentru expediere întârziată: 200 lei;
- sumă virată: 50.000 − 3.000 − 6.050 − 200 = **40.750 lei**.

Înregistrări, cu 4111 analitic pe platformă și 401 pentru platformă ca furnizor:

- vânzări, din facturile emise: 4111 = 707: 41.322,31 lei și 4111 = 4427: 8.677,69 lei;
- retururi, din facturile de stornare: 4111 = 707: −2.479,34 lei și 4111 = 4427: −520,66 lei;
- comision: 622 = 401: 5.000 lei și 4426 = 401: 1.050 lei;
- penalitate: 6581 = 401: 200 lei;
- compensare: 401 = 4111: 6.250 lei;
- încasare: 5121 = 4111: 40.750 lei.

Soldul 4111 pentru platformă: 50.000 − 3.000 − 6.250 − 40.750 = 0.

### Diferențele frecvente

- **Decalaj de perioadă.** Comenzile livrate la final de lună apar în decontul următor. Rămân sold în 4111, nu sunt erori.
- **Retur cerut, dar nerambursat.** Nu stornați până când returul nu este efectiv acceptat.
- **Comision fără factură.** Solicitați factura platformei. Decontul singur poate să nu fie suficient pentru deducerea TVA.
- **Sume neidentificate.** Țineți-le în 473 „Decontări din operațiuni în curs de clarificare" până la lămurire, nu pe venituri sau cheltuieli diverse.

### Pași practici

1. Exportați decontul pe linii: comandă, tip de sumă, valoare.
2. Potriviți fiecare vânzare cu factura sau bonul emis, iar fiecare retur cu stornarea.
3. Potriviți totalul comisioanelor cu factura platformei și totalul penalităților cu nota de debit.
4. Înregistrați elementele brute, apoi compensarea 401 = 4111.
5. Verificați că suma din extras este egală cu netul decontului și că 4111 pentru platformă s-a închis sau are sold explicabil.

### De reținut

- Netul virat nu este venit. Elementele se înregistrează brut, apoi se compensează (OMFP nr. 1802/2014, pct. 56).
- Retururile reduc baza TVA (Codul fiscal art. 287 lit. b)).
- Comisionul este cheltuială 622, cu TVA sau cu taxare inversă (art. 307 alin. (2)).
- Penalitățile contractuale nu intră în baza TVA (art. 286 alin. (4) lit. b)).
