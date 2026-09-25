---
title: Cum se descarcă gestiunea pentru semifabricate?
description: Semifabricatele se descarcă din contul 341 pe două căi. Cele vândute se descarcă prin 711 = 341, cu venitul pe 702. Cele consumate în aceeași unitate se transferă prin 301/302 = 341. Temeiul este funcțiunea conturilor din OMFP 1802/2014.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se descarcă gestiunea pentru semifabricate?

Semifabricatele au cont propriu, 341 „Semifabricate”, și două destinații posibile: vânzarea către terți sau consumul intern în faza următoare de fabricație. Descărcarea gestiunii diferă după destinație. Semifabricatele vândute ies prin contul 711. Cele consumate intern trec mai întâi în conturile de materii prime sau materiale consumabile și ajung pe cheltuieli la consum.

### Ce sunt semifabricatele

OMFP 1802/2014, pct. 276 alin. (1) lit. e), definește semifabricatele ca produse „al căror proces tehnologic a fost terminat într-o secție (fază de fabricație) și care trec în continuare în procesul tehnologic al altei secții (faze de fabricație) sau se livrează terților”. Nu sunt produse finite, pentru care există contul 345, și nici producție în curs, pentru care există contul 331. Au un stoc propriu, recepționat în gestiune.

### Intrarea în gestiune

Potrivit funcțiunii contului 341 din OMFP 1802/2014, semifabricatele obținute din activitatea proprie intră la preț de înregistrare sau la preț de producție:

- `341 = 711` pentru semifabricatele obținute;
- dacă firma folosește prețuri prestabilite, diferențele de preț nefavorabile aferente produselor intrate se înregistrează `348 = 711`, conform funcțiunii contului 711.

### Descărcarea la vânzare

Vânzarea presupune două înregistrări:

1. Factura: `4111 = 702 + 4427`. Contul 702 „Venituri din vânzarea semifabricatelor” se creditează cu prețul de vânzare. TVA se aplică la cota standard de 21%, prevăzută de Codul fiscal art. 291 alin. (1).
2. Descărcarea gestiunii: `711 = 341`, la preț de înregistrare. Funcțiunea contului 341 prevede creditarea lui cu „valoarea la preț de înregistrare a semifabricatelor vândute” prin 711.

### Descărcarea la consum intern

Semifabricatele păstrate și folosite în faza următoare de producție nu se descarcă direct pe cheltuieli. Planul de conturi le trece întâi în contul materiei în care se transformă:

- `301 = 341` dacă sunt consumate ca materie primă. Contul 301 se debitează cu „semifabricatele și produsele reținute și consumate ca materie primă în aceeași unitate”;
- `302 = 341` dacă sunt consumate ca materiale consumabile;
- apoi, la consum efectiv, `601 = 301` sau `602 = 302`.

Transferurile către subunități se fac prin 481/482, iar trimiterea la terți pentru prelucrare se face prin 354.

### Cu ce valoare se descarcă

Ieșirile se evaluează după metoda aleasă în politica contabilă. OMFP 1802/2014 pct. 96 alin. (1) enumeră, printre altele, metoda costului mediu ponderat (CMP) și metoda FIFO. Dacă firma ține semifabricatele la preț prestabilit, diferențele de preț aferente ieșirilor se repartizează prin 348, la fel ca la produsele finite.

### Exemplu

O fabrică de mobilă obține 100 de blaturi debitate, la un cost de producție de 80 lei/buc. Nota de intrare este `341 = 711` cu 8.000 lei. Firma vinde 30 de blaturi cu 120 lei/buc: `4111 = 702 + 4427` cu 3.600 + 756 lei și `711 = 341` cu 2.400 lei. Restul de 70 de blaturi intră în asamblare: `301 = 341` cu 5.600 lei, apoi `601 = 301` pe măsura consumului.

### Pași practici

1. Stabilește în politica contabilă metoda de evaluare a ieșirilor (CMP sau FIFO) și dacă folosești prețuri prestabilite.
2. Documentează fiecare ieșire: factura și avizul pentru vânzare, bonul de consum sau de transfer pentru consumul intern.
3. Verifică lunar ca soldul contului 341 să corespundă stocului faptic.

### De reținut
- Pentru vânzare, venitul se înregistrează pe 702, iar descărcarea se face prin `711 = 341`.
- Pentru consumul intern, semifabricatele trec prin `301/302 = 341`, apoi pe cheltuieli (OMFP 1802/2014, funcțiunea conturilor 301, 302 și 341).
- Evaluarea ieșirilor urmează metoda din politica contabilă (OMFP 1802/2014 pct. 96).
