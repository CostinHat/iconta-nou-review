---
title: Cum funcționează acreditivul în comerțul exterior (evidența contabilă)
description: Acreditivul este suma blocată la bancă în favoarea furnizorului extern. Se urmărește în contul 541 „Acreditive”: se deschide prin 581, se lichidează prin 401 sau 404, se reevaluează lunar la cursul BNR, iar diferențele merg la 665/765 (OMFP 1802/2014, pct. 304-305).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum funcționează acreditivul în comerțul exterior (evidența contabilă)

În comerțul exterior, acreditivul este un mecanism prin care cumpărătorul cere băncii să pună o sumă la dispoziția furnizorului extern. Furnizorul încasează suma când își îndeplinește obligațiile convenite. Pentru cumpărător, banii nu mai sunt disponibili în contul curent, dar nici nu au ajuns încă la furnizor. OMFP 1802/2014 prevede un cont separat pentru această etapă: contul 541 „Acreditive”, cu analiticele 5411 (în lei) și 5414 (în valută).

### Temeiul contabil

OMFP 1802/2014, pct. 305 alin. (1): „În vederea achitării unor obligații față de furnizori, entitățile pot solicita deschiderea de acreditive la bănci, în lei sau în valută, în favoarea acestora.”

Potrivit alin. (2) și (3) ale aceluiași punct, acreditivele în valută se lichidează la cursul BNR de la data lichidării. Diferența față de cursul de la constituire, sau față de cursul din evidență, se înregistrează la venituri sau cheltuieli din diferențe de curs valutar.

În planul de conturi, 541 este cont de activ. Se debitează cu acreditivele deschise (581) și cu diferențele favorabile de curs la finele lunii (765). Se creditează cu sumele plătite terților sau readuse în disponibil la încetarea valabilității acreditivului (401, 404, 581) și cu diferențele nefavorabile de curs (665).

### Circuitul pe un exemplu

O firmă importă un utilaj de 20.000 EUR și deschide un acreditiv în valută.

1. **Deschiderea acreditivului** (curs BNR 5,00):
   `581 = 5124` și apoi `5414 = 581` — 100.000 lei.
2. **Reevaluarea la finele lunii** (curs 5,02). OMFP 1802/2014, pct. 304 alin. (3) cere evaluarea lunară a acreditivelor în valută la cursul BNR din ultima zi bancară a lunii:
   `5414 = 765` — 400 lei.
3. **Lichidarea acreditivului** după livrare, când banca plătește furnizorul (curs 4,99). Datoria față de furnizor este înregistrată la cursul de la recepție. Acreditivul se descarcă la cursul zilei lichidării:
   `404 = 5414` — 99.800 lei.
   Diferența dintre soldul contului 5414 (100.400 lei) și valoarea la lichidare (99.800 lei), adică 600 lei, merge la `665 = 5414`. Se regularizează separat și diferența de curs pe datoria 404, față de cursul la care a fost înregistrată.
4. **Comisioanele băncii** pentru deschidere și confirmare sunt cheltuieli cu servicii bancare: `627 = 5124`.

Dacă acreditivul expiră neutilizat, suma revine în cont: `581 = 5414`, apoi `5124 = 581`.

### De ce contează contul separat

- **Bilanțul.** Acreditivele se prezintă distinct de disponibilități. OMFP 1802/2014, pct. 90 alin. (1) le enumeră printre valorile care se prezintă în bilanț conform prevederilor legale.
- **Reconcilierea.** Extrasul contului curent nu mai arată suma blocată. Fără 541, soldul contabil al băncii nu se mai potrivește cu extrasul.
- **Reevaluarea.** La închiderea exercițiului, OMFP 1802/2014, pct. 94 lit. a) tratează acreditivele ca elemente monetare, evaluate la cursul BNR de la data încheierii exercițiului.

### Pași practici pentru contabil

- Cere de la bancă confirmarea deschiderii acreditivului: sumă, valută, beneficiar și dată de expirare.
- Deschide un analitic 5414 pe fiecare acreditiv.
- Reevaluează soldul în ultima zi a fiecărei luni.
- La lichidare, folosește cursul BNR de la data operațiunii și închide analiticul la zero.
- Urmărește data de expirare, ca sumele neutilizate să revină în disponibil.

### De reținut

- Acreditivul se ține în contul 541, nu în 512 (OMFP 1802/2014, pct. 305).
- Acreditivele în valută se reevaluează lunar la cursul BNR (pct. 304 alin. (3)).
- La lichidare, diferențele de curs merg la 665/765.
- Comisioanele bancare se înregistrează în 627.
