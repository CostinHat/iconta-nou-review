---
title: Cum se contabilizează serviciile API cumpărate în funcție de consum?
description: Consumul de API facturat ulterior (pay-as-you-go) se înregistrează ca cheltuială în luna consumului, prin 408, dacă factura nu a sosit. Pentru furnizorii nestabiliți în România se aplică taxarea inversă (Codul fiscal art. 278 alin. (2), art. 307 alin. (2)), iar pentru serviciile continue faptul generator este data de plată din contract sau data facturii (art. 281 alin. (8)).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se contabilizează serviciile API cumpărate în funcție de consum?

Multe API-uri (modele de inteligență artificială, hărți, plăți, trimitere de SMS) se plătesc după consum. Furnizorul măsoară apelurile dintr-o lună și emite factura după închiderea lunii. Consumul este o cheltuială a lunii în care a avut loc, chiar dacă factura sosește mai târziu. TVA urmează însă regulile proprii ale faptului generator și, de cele mai multe ori, ale taxării inverse.

### Cheltuiala lunii: 408 când factura întârzie

OMFP 1802/2014 descrie contul 408 „Furnizori - facturi nesosite” ca evidența decontărilor cu furnizorii pentru serviciile prestate „pentru care nu s-au primit facturi”. La închiderea lunii, cheltuiala se estimează din consola sau raportul de utilizare al furnizorului:

- **628 = 408**, la valoarea consumului lunii;
- la sosirea facturii: **408 = 401**, iar diferența față de estimare se înregistrează pe 628.

Consumul plătit anticipat (credite preplătite) se tratează diferit: prin 471, cu trecere pe cheltuieli pe măsura consumului.

### TVA: locul prestării și taxarea inversă

API-urile cumpărate de o firmă sunt servicii furnizate unei persoane impozabile. Locul prestării este la sediul beneficiarului (Codul fiscal art. 278 alin. (2)). Dacă furnizorul nu este stabilit în România, taxa se datorează de beneficiar (art. 307 alin. (2)). Firma calculează TVA la cota de 21% și o înregistrează simultan ca taxă colectată și deductibilă: **4426 = 4427**.

### Când se înregistrează TVA

Faptul generator pentru servicii continue este stabilit de art. 281 alin. (8). Prestarea se consideră efectuată „la fiecare dată prevăzută în contract pentru plata” serviciilor sau, dacă contractul nu prevede, „la data emiterii unei facturi”, dar perioada de decontare nu poate depăși un an.

Consecințe practice:

- estimarea din 408 de la sfârșitul lunii este o înregistrare contabilă a cheltuielii. TVA prin taxare inversă se calculează când intervine faptul generator: data de plată din termenii furnizorului sau data facturii;
- pentru un serviciu continuu de peste un an fără nicio decontare, art. 281 alin. (10) îl consideră efectuat la expirarea fiecărui an calendaristic. La API-urile facturate lunar, situația aceasta nu apare de obicei.

### Impozitul pe profit

Cheltuiala cu API-ul este deductibilă ca cheltuială efectuată în scopul activității economice (Codul fiscal art. 25 alin. (1)). Păstrați factura, raportul de consum și termenii contractuali acceptați online. Împreună, ele arată ce s-a cumpărat și de ce suma diferă de la o lună la alta.

### Exemplu

O firmă folosește un API facturat în dolari de un furnizor din afara UE. Consumul din martie, citit din consolă pe 31 martie, este echivalentul a 4.200 lei. Factura, de 4.260 lei (cu ajustări de rotunjire ale furnizorului), sosește pe 3 aprilie și are data de 1 aprilie.

- 31 martie: 628 = 408, 4.200 lei
- 3 aprilie, la primirea facturii: 408 = 401, 4.200 lei, și 628 = 401, 60 lei
- TVA prin taxare inversă la data facturii (1 aprilie), 21% × 4.260 = 894,60 lei: 4426 = 4427, 894,60 lei, în decontul lunii aprilie
- Plata: 401 = 5124, cu diferențele de curs aferente

### Pași practici

1. Descărcați lunar raportul de utilizare din contul furnizorului și atașați-l la nota de estimare.
2. Verificați dacă entitatea care facturează este stabilită în România sau nu. De aici rezultă dacă aplicați taxarea inversă.
3. Închideți lunar diferențele dintre estimare și factură, ca să nu rămână solduri vechi în 408.

### De reținut

- Consumul lunii este cheltuială a lunii: 628 = 408, dacă factura întârzie (OMFP 1802/2014, contul 408).
- API cumpărat de la un furnizor nestabilit în România înseamnă taxare inversă, 4426 = 4427 (Codul fiscal art. 278 alin. (2), art. 307 alin. (2)).
- Pentru servicii continue, TVA urmează data de plată din contract sau data facturii (art. 281 alin. (8)).
- Păstrați raportul de consum ca justificare a sumei.
