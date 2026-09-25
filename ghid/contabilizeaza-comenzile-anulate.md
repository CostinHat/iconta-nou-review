---
title: Cum se contabilizează comenzile anulate
description: Tratamentul diferă după momentul anulării — înainte sau după livrare — și după existența unei facturi în avans, cu ajustarea corespunzătoare a bazei de TVA acolo unde e cazul.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează comenzile anulate

O comandă anulată nu se tratează contabil la fel indiferent de moment. Contează dacă anularea are loc înainte de livrare/prestare, dacă există deja o factură emisă (eventual în avans) și dacă a existat sau nu o încasare.

### Anulare înainte de livrare, fără factură emisă

Dacă nu ai emis nicio factură, nu ai nimic de stornat — comanda se șterge din sistemul de gestiune al comenzilor, fără impact contabil. Dacă existase un avans încasat de la client, acesta rămâne o datorie (cont 419 "Clienți-creditori" sau 4198, după caz) până la restituire sau compensare cu altă comandă.

### Anulare cu factură emisă în avans

Situația e reglementată explicit de Codul fiscal (Legea nr. 227/2015). Art. 287 lit. a) prevede că baza de impozitare a TVA se reduce:

> "în cazul desființării totale sau parțiale a contractului pentru livrarea de bunuri sau prestarea de servicii, înainte de efectuarea acestora, dar pentru care au fost emise facturi în avans"

Practic, dacă ai emis factură de avans și comanda se anulează înainte de livrare, emiți o factură de stornare (cu semn negativ sau storno, după practica firmei) pentru a ajusta atât baza impozabilă, cât și TVA aferentă. Contabil, stornezi înregistrarea inițială:

```
4111 „Clienți” = 419 „Clienți-creditori” (stornare avans, dacă avansul rămâne la dispoziția clientului sub formă de creanță de restituit)
```

sau, dacă avansul se restituie direct:

```
419 „Clienți-creditori” = 512 „Conturi curente la bănci”
```

### Anulare după livrare (retur de marfă/refuz de serviciu)

Dacă produsul a fost deja livrat și clientul returnează marfa (sau refuză parțial/total serviciul prestat), se aplică art. 287 lit. b) din Codul fiscal — reducerea bazei de impozitare pentru "refuzurile totale sau parțiale privind cantitatea, calitatea ori prețurile bunurilor livrate sau ale serviciilor prestate". Se emite factură de stornare pentru valoarea returnată, marfa reintră în gestiune la costul de ieșire inițial (dacă e cazul și starea produsului o permite), iar TVA colectată aferentă se ajustează corespunzător prin decontul perioadei în care are loc stornarea.

### Ce nu se schimbă: momentul deductibilității cheltuielilor asociate

Cheltuielile deja angajate pentru onorarea comenzii (materii prime consumate, manoperă) și care nu mai pot fi recuperate din anulare rămân, de regulă, cheltuieli ale perioadei — nu se recapitalizează retroactiv doar pentru că respectiva comandă nu s-a mai finalizat, cu excepția cazului în care materialele neconsumate pot fi redirecționate spre altă comandă sau reintroduse în stoc.

### De reținut

- Ajustarea bazei de TVA la comenzi anulate cu factură deja emisă are temei explicit la art. 287 lit. a) (facturi în avans) și lit. b) (refuzuri/retururi) din Codul fiscal.
- Fără factură emisă, anularea nu are impact contabil — doar avansul încasat, dacă există, rămâne de gestionat ca datorie.
- Stornarea corectă a TVA se face prin decontul perioadei fiscale în care intervine anularea, nu retroactiv pe perioada facturării inițiale.
