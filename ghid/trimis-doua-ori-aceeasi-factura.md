---
title: Ce fac dacă am trimis de două ori aceeași factură în e-Factura?
description: Dacă ambele transmiteri au primit sigiliul Ministerului Finanțelor, clientul a primit de două ori aceeași factură, iar a doua nu se mai poate retrage (OUG 120/2021, art. 4 alin. (8)). Se anulează efectul ei printr-o factură cu valori negative, transmisă tot în RO e-Factura (art. 4 alin. (10) și Codul fiscal art. 330 alin. (1) lit. b)). În contabilitate și în D300, factura se înregistrează o singură dată.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă am trimis de două ori aceeași factură în e-Factura?

Mai întâi verifică în SPV starea celei de-a doua transmiteri. Dacă a fost respinsă, nu ai nimic de corectat: un XML respins nu primește sigiliu și nu ajunge la client. Dacă a fost acceptată, clientul are în sistem două facturi electronice identice. Pe cea în plus nu o poți șterge și nici retrage, deci îi anulezi efectul printr-o factură cu valori negative, transmisă tot prin RO e-Factura.

### De ce nu se poate „șterge" dublura

OUG 120/2021, art. 4:
- **alin. (4)**: factura care respectă structura primește sigiliul electronic al Ministerului Finanțelor și se comunică de îndată destinatarului;
- **alin. (8)**: factura electronică comunicată destinatarului „nu se poate returna" în sistem;
- **alin. (10)**: corecția unei facturi comunicate se face conform art. 330 din Codul fiscal, iar factura corectată se transmite în același sistem.

Odată acceptată, a doua transmitere este, pentru client, un document distinct pe care îl poate descărca și înregistra.

### Cum se face corecția

Codul fiscal art. 330 alin. (1) lit. b) prevede, pentru o factură transmisă beneficiarului, emiterea unei facturi cu valorile cu semnul minus, în care se înscriu numărul și data facturii corectate. Pentru dublură:
1. Emiți o factură nouă, cu număr nou din serie, cu aceleași linii ca dublura, dar cu cantități sau valori negative.
2. Faci referire la numărul și data facturii duplicate. Precizează în text că stornezi a doua transmitere, ca să nu fie confundată cu originalul.
3. O transmiți în RO e-Factura în termenul de 5 zile lucrătoare de la emitere (OUG 120/2021, art. 10 alin. (7), în forma dată de OUG 89/2025).
4. Anunți clientul, ca să nu deducă TVA de două ori.

### Efectul în evidența ta

Dacă ai înregistrat factura o singură dată în contabilitate, adică doar XML-ul a plecat de două ori, factura de stornare nu modifică nimic în TVA colectată. Ea compensează doar dublura din sistem. Înregistrezi atunci în jurnalul de vânzări perechea dublură și stornare, cu sold zero, ca evidența să corespundă cu ce vede ANAF în RO e-Factura.

Dacă ai înregistrat de două ori și în contabilitate, stornarea reduce TVA colectată cu suma înregistrată în plus. Exemplu: factură de 10.000 lei plus TVA 2.100 lei, înregistrată de două ori. Stornarea duce TVA colectată la 2.100 lei, nu 4.200 lei.

### Ce face clientul

Clientul nu are voie să deducă de două ori taxa aferentă aceleiași operațiuni. Dacă a înregistrat ambele facturi, stornarea primită în SPV îi dă documentul pe baza căruia își corectează deducerea. Destinatarul poate semnala oricând obiecții printr-un mesaj în sistem (art. 4 alin. (9)).

### De reținut
- Verifică întâi dacă a doua transmitere a fost acceptată sau respinsă.
- O factură acceptată nu se poate retrage (art. 4 alin. (8)).
- Dublura se neutralizează cu o factură cu minus, transmisă în RO e-Factura (art. 4 alin. (10), Codul fiscal art. 330).
- TVA colectată se corectează doar dacă și în contabilitate factura a fost înregistrată de două ori.
