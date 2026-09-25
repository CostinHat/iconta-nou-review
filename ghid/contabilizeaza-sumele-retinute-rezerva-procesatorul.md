---
title: Cum se contabilizează sumele reținute ca rezervă de procesatorul de plăți
description: Rezerva reținută de procesator din încasările clienților nu e cheltuială și nici venit diminuat — e o creanță a firmei asupra procesatorului, urmărită în contul 461 (sau 267, dacă reținerea depășește un an), potrivit funcțiunii conturilor din OMFP 1802/2014.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se contabilizează sumele reținute ca rezervă de procesatorul de plăți

Unii procesatori de plăți rețin temporar un procent din încasări (așa-numita rezervă sau „rolling reserve”) și îl eliberează după un număr de zile stabilit prin contract. Suma reținută rămâne a firmei: nu e comision, nu reduce venitul din vânzare și nu e încasată încă. Contabil, este o **creanță asupra procesatorului**, care se stinge la eliberarea rezervei.

### De ce nu e cheltuială și nici venit diminuat

Venitul se recunoaște la valoarea facturată clientului, indiferent cum decontează procesatorul. Diferența dintre suma brută și suma virată în bancă are două componente distincte:

- **comisionul** reținut definitiv, care este cheltuială (627 sau 622, după natura serviciului);
- **rezerva**, care va fi restituită, deci o sumă de primit.

A înregistra rezerva ca cheltuială ar subevalua rezultatul, iar la eliberare ar apărea un „venit” fără o vânzare în spate.

### Contul potrivit: 461 sau 267

Funcțiunea contului 461 „Debitori diverși” din OMFP 1802/2014 acoperă „alte creanțe”, altele decât cele față de entitățile afiliate, iar creditul său primește „valoarea debitelor încasate (512, 531)”. Rezerva reținută pentru câteva luni se încadrează aici; se recomandă un analitic distinct pe fiecare procesator.

Dacă reținerea contractuală depășește un an, contul 267 „Creanțe imobilizate” e cel indicat: funcțiunea lui include „depozite, garanții și cauțiuni depuse de entitate la terți”, deținute „pe o perioadă mai mare de un an”.

### Exemplu numeric

Vânzări online de 20.000 lei într-o lună, încasate prin procesator. Comision 2% = 400 lei, rezervă 10% = 2.000 lei, eliberată după 90 de zile. Virament net: 17.600 lei.

1. Facturarea vânzărilor: `4111 = 707/704 (+ 4427)` 20.000 lei, după caz cu TVA.
2. Decontarea procesatorului:
   - `5121 = 4111` 17.600 lei (suma intrată în bancă);
   - `627 = 4111` 400 lei (comisionul);
   - `461.procesator = 4111` 2.000 lei (rezerva reținută).
3. Eliberarea rezervei după 90 de zile: `5121 = 461.procesator` 2.000 lei.

Dacă procesatorul reține definitiv o parte din rezervă (de exemplu pentru o dispută pierdută), partea respectivă se analizează separat: e fie o restituire către client (care afectează venitul și, după caz, TVA), fie o penalitate contractuală, nu un comision.

### Rezerva în valută

Pentru procesatorii care decontează în euro, creanța din 461 e o creanță în valută. Funcțiunea contului 461 prevede explicit diferențele de curs la evaluarea de la finele lunii (765/665), așa că soldul rezervei se reevaluează lunar, ca orice creanță în valută.

### Pași practici pentru contabil

- Cere de la procesator raportul de decontare care arată separat brutul, comisionul și rezerva reținută și eliberată.
- Ține un analitic 461 pe fiecare procesator și reconciliază soldul cu soldul rezervei din contul de comerciant, la fiecare închidere de lună.
- Verifică în contract durata reținerii, ca să alegi între 461 și 267.
- La închiderea exercițiului, confirmă soldul cu procesatorul, ca pentru orice debitor.

### De reținut

- Rezerva reținută de procesator e o creanță (461, sau 267 peste un an), nu cheltuială și nici diminuare de venit.
- Doar comisionul reținut definitiv merge pe cheltuieli (627/622).
- Eliberarea rezervei stinge creanța: `5121 = 461`.
- Rezervele în valută se reevaluează lunar, ca orice creanță în valută.
