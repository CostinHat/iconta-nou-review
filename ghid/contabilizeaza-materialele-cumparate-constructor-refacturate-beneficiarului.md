---
title: Cum se contabilizează materialele cumpărate de constructor și refacturate beneficiarului?
description: Tratamentul TVA și contabil al materialelor de construcție achiziționate de antreprenor și incluse în valoarea lucrării facturate beneficiarului — bază impozabilă unică, nu livrare separată.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează materialele cumpărate de constructor și refacturate beneficiarului?

Un constructor care cumpără materiale pe care le încorporează într-o lucrare executată pentru un beneficiar nu "refacturează" materialele ca pe o livrare distinctă — le include în baza de impozitare a prestării de servicii de construcții-montaj. Distincția contează atât pentru TVA, cât și pentru înregistrarea contabilă.

### Baza de impozitare TVA include costul materialelor

Codul fiscal, art. 286 alin. (1) lit. a), stabilește regula generală: baza de impozitare a TVA pentru livrări de bunuri și prestări de servicii este "tot ceea ce constituie contrapartida obținută sau care urmează a fi obținută de furnizor ori prestator din partea cumpărătorului, beneficiarului sau a unui terț". Materialele încorporate în lucrare nu se facturează separat cu regim de TVA distinct de restul lucrării — ele sunt parte a prestației unice de construcții-montaj, iar TVA-ul se aplică o singură dată, la valoarea totală facturată beneficiarului (manoperă + materiale + alte cheltuieli aferente).

### Circuitul contabil la constructor

**La achiziția materialelor:**
```
301/302 „Materii prime/Materiale consumabile"  =  401 „Furnizori"
4426 „TVA deductibilă"                          =  401 „Furnizori"
```

**La darea în consum pe șantier (consumul materialelor în lucrare):**
```
601/602 „Cheltuieli cu materiile prime/materialele"  =  301/302
```

**La recunoașterea veniturilor din lucrare** (pe măsura executării, potrivit gradului de avansare, sau la finalizare/recepție, în funcție de politica contabilă a entității pentru contractele de construcție):
```
418/411 „Clienți"  =  704/705/722 „Venituri din lucrări executate/producția în curs"
4427 „TVA colectată"  =  (aplicată asupra valorii totale facturate, inclusiv materiale)
```

### Ce NU se face

Nu se înregistrează o "vânzare" separată a materialelor către beneficiar (cu ieșire din 301/302 direct în 371/707 sau prin refacturare 401→411 cu marjă zero) urmată de o "prestare de manoperă" distinctă — decât dacă acesta e chiar obiectul contractual (beneficiarul cumpără materialele separat, pe factură proprie, iar constructorul facturează doar manopera). Dacă materialele sunt parte a angajamentului de execuție a lucrării (situație tipică pentru contractele de antrepriză), ele intră în costul lucrării, se consumă pe 601/602 și se recuperează prin prețul de vânzare al lucrării, nu printr-o refacturare cu TVA aplicat separat pe fiecare material.

### De ce contează distincția

Dacă entitatea tratează greșit materialele ca "refacturare" 1:1 (cumpărare-revânzare la același preț), riscă neconcordanțe între jurnalul de cumpărări/vânzări și declarația 394 (unde operațiunea corectă e o singură livrare de servicii de construcții către beneficiar, nu o pereche cumpărare-revânzare de bunuri), plus o denaturare a costului lucrării raportat la contractul de execuție.
