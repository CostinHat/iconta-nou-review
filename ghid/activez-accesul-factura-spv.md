---
title: Cum activez accesul la e-Factura în SPV
description: Înscrierea în Registrul RO e-Factura se face prin opțiune exercitată de operatorul economic (sau prin obligație legală, pentru operațiunile B2B), iar efectul înscrierii nu e imediat — devine activ din prima zi a lunii următoare exercitării opțiunii, potrivit OUG 120/2021.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum activez accesul la e-Factura în SPV?

Accesul la sistemul RO e-Factura trece prin Spațiul Privat Virtual (SPV), dar activarea propriu-zisă înseamnă înscrierea în Registrul RO e-Factura, un pas cu efect întârziat de lege — nu instant.

### Pasul 0 — acces la SPV

Fără cont activ în Spațiul Privat Virtual, nu se poate exercita opțiunea pentru RO e-Factura. Dacă firma nu are deja SPV configurat, acesta e obligatoriu în prealabil — administratorul/reprezentantul legal se autentifică în SPV (cu certificat digital calificat sau alte mijloace de identificare acceptate de ANAF) și, pentru firme, poate delega acces și contabilului sau altei persoane împuternicite.

### Pasul 1 — exercitarea opțiunii pentru RO e-Factura

Pentru operatorii care nu au obligație legală de transmitere (deci vor să se înscrie opțional), sau pentru cei care intră oricum sub incidența obligației legale, înscrierea se face prin opțiune comunicată prin SPV. Potrivit art. 10 alin. (3) din OUG 120/2021, „operatorul economic care a optat pentru utilizarea sistemului național privind factura electronică RO e-Factura este înscris în Registrul RO e-Factura **începând cu data de 1 a lunii următoare exercitării opțiunii**."

Practic: dacă opțiunea e exercitată pe 15 martie, înscrierea efectivă în Registrul RO e-Factura devine activă pe 1 aprilie — nu în ziua exercitării opțiunii. Trebuie planificat din timp, nu în ultima clipă înainte de un termen de conformare.

### Pasul 2 — de la momentul înscrierii, obligațiile devin reciproce

Art. 10 alin. (3) mai precizează: „De la momentul înscrierii în Registrul RO e-Factura, emitentul dobândește și calitatea de destinatar", iar alin. (4) adaugă: „în vederea utilizării sistemului național privind factura electronică RO e-Factura, emitentul și destinatarul trebuie să fie înregistrați în Registrul RO e-Factura" — deci ambele părți trebuie înscrise pentru ca facturile respective să intre sub incidența regimului. Registrul RO e-Factura e public și afișat pe site-ul ANAF, deci oricine poate verifica dacă un partener comercial e deja înscris, înainte de a emite/aștepta o factură prin sistem.

### Pasul 3 — pentru cei cu obligație legală (B2B), verifică dacă mai e nevoie de "activare"

Pentru operațiunile B2B cu locul livrării/prestării în România, transmiterea prin RO e-Factura e obligatorie prin efectul legii (Legea 296/2023, care a completat regimul din OUG 120/2021), nu doar prin opțiune. În acest caz, accesul tehnic la platformă (autentificare în SPV, configurarea softului de facturare pentru transmitere XML/UBL către API-ul ANAF) e pasul practic relevant — obligația legală există independent de "activarea" formală, iar termenul de transmitere e de 5 zile lucrătoare de la data emiterii facturii.

### Checklist

1. Cont SPV activ și funcțional pentru firmă (certificat digital calificat sau alt mijloc de autentificare acceptat).
2. Verifică dacă firma se încadrează la obligație legală (B2B/B2G) sau doar la opțiune — obligația legală nu depinde de exercitarea unei opțiuni separate.
3. Dacă te înscrii opțional, ține cont că efectul e din prima zi a lunii următoare, nu imediat.
4. Verifică în Registrul RO e-Factura (public, pe site-ul ANAF) dacă partenerii comerciali relevanți sunt deja înscriși, înainte de a presupune că o factură trebuie transmisă prin sistem.
5. Configurează softul de facturare/contabilitate pentru transmiterea în formatul cerut, cu respectarea termenului de 5 zile lucrătoare de la emiterea facturii.
