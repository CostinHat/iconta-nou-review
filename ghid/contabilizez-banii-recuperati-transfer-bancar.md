---
title: Cum contabilizez banii recuperați după un transfer bancar greșit?
description: Plata trimisă greșit nu e cheltuială. Rămâne o sumă de recuperat, urmărită în contul 461 sau, dacă destinația e încă neclară, în 473, iar la recuperare se închide cu 5121. Doar partea nerecuperabilă ajunge pe cheltuieli, conform funcțiunii conturilor din OMFP 1802/2014.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum contabilizez banii recuperați după un transfer bancar greșit?

Un transfer trimis greșit (alt beneficiar, sumă dublă, IBAN eronat) nu stinge nicio datorie a firmei și nu este cheltuială. Din momentul constatării, banii sunt o **sumă de recuperat**. Recuperarea ulterioară doar închide această creanță, fără să genereze venit.

### Pasul 1: înregistrarea plății greșite

Ce cont folosești depinde de cât de clară este situația în momentul constatării.

- **Știi cine a primit banii și că trebuie să-i returneze.** Folosește contul 461 „Debitori diverși”. Potrivit OMFP 1802/2014, acesta ține evidența „altor creanțe”, iar creditul lui primește „valoarea debitelor încasate (512, 531)”.
- **Situația încă se clarifică.** De exemplu, banca investighează unde au ajuns fondurile. Folosește contul 473 „Decontări din operațiuni în curs de clarificare”. Funcțiunea lui prevede explicit în debit „plățile pentru care în momentul efectuării sau constatării acestora nu se pot lua măsuri de înregistrare definitivă într-un cont, necesitând clarificări suplimentare (512)”.

Nu lăsa plata pe contul furnizorului (401). Dacă furnizorul corect nu a primit banii, datoria față de el rămâne deschisă. Un avans fictiv pe 401 ar denatura soldul.

### Pasul 2: recuperarea

Când banii revin în cont:

- `5121 = 461` (sau `5121 = 473`), cu suma recuperată.

Dacă la plată ai folosit 473 și ulterior ai lămurit cine datorează suma, mută întâi creanța: `461 = 473`.

### Pasul 3: partea nerecuperată

Dacă, după demersurile făcute, o parte nu mai poate fi recuperată:

- din 473, funcțiunea contului permite trecerea „sumelor clarificate” pe cheltuieli (601 la 658);
- din 461, creditul contului include „sumele trecute pe pierderi cu prilejul scăderii din evidență a debitorilor (654)”.

Deductibilitatea fiscală a pierderii depinde de documentele care o susțin (hotărâre, confirmare bancară, dovada demersurilor). Păstrează-le în dosarul operațiunii.

### Exemplu numeric

Pe 10 martie, firma plătește furnizorului X o factură de 8.000 lei, dar din greșeală de două ori. Furnizorul confirmă și returnează suma pe 25 martie.

- 10 martie: `401.X = 5121` 8.000 (plata corectă) și `461.X = 5121` 8.000 (plata dublă).
- 25 martie: `5121 = 461.X` 8.000.

Alt caz: 3.000 lei sunt trimiși la un IBAN greșit, necunoscut. Banca deschide o cerere de recuperare și obține 2.500 lei. Restul se pierde definitiv.

- La constatare: `473 = 5121` 3.000.
- La recuperare: `5121 = 473` 2.500.
- Diferența de 500 lei, după clarificare: `658 = 473` 500.

### Dacă plata greșită era în valută

Creanța din 461 este o creanță în valută. La finele lunii se reevaluează cu diferențe de curs 765/665, conform funcțiunii contului 461. La recuperare, diferența dintre cursul istoric și cel de la încasare se înregistrează tot pe 765/665.

### Pași practici pentru contabil

- Documentează imediat eroarea: extras, ordin de plată, notă explicativă.
- Alege 461 sau 473 după cât de clară e situația și închide soldul 473 cât mai repede.
- Urmărește soldurile 461/473 la fiecare închidere de lună. Un sold vechi pe 473 e un semnal de alarmă la control.

### De reținut

- O plată greșită nu e cheltuială, ci o sumă de recuperat.
- Folosește 461 când debitorul e cunoscut și 473 când situația e în curs de clarificare.
- Recuperarea se înregistrează `5121 = 461/473`, fără venit.
- Doar partea definitiv nerecuperabilă trece pe cheltuieli (654/658), cu documente justificative.
