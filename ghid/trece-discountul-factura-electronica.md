---
title: Cum se trece discountul pe factura electronică?
description: Discountul acordat pe loc se scade din baza de impozitare. Pe factură apare fie inclus în prețul unitar, fie separat, pe cota de TVA corespunzătoare (Codul fiscal art. 286 alin. (4) lit. a) și art. 319 alin. (20) lit. i)). Discountul acordat ulterior se face printr-o factură cu minus transmisă tot în RO e-Factura (art. 287 lit. c), art. 330 alin. (2) și OUG 120/2021, art. 4 alin. (10)).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se trece discountul pe factura electronică?

Pentru e-Factura nu există reguli speciale de discount. Se aplică regulile din Codul fiscal, iar XML-ul trebuie doar să le reflecte corect. Contează momentul acordării: un discount dat chiar pe factura de livrare scade baza de impozitare încă de la început, iar un discount acordat după livrare se face printr-o factură separată, cu valori negative, transmisă tot prin RO e-Factura.

### Discountul acordat pe loc

Codul fiscal art. 286 alin. (4) lit. a) exclude din baza de impozitare „rabaturile, remizele, risturnele, sconturile și alte reduceri de preț, acordate de furnizori direct clienților la data exigibilității taxei". TVA se calculează deci la valoarea după discount.

Art. 319 alin. (20) lit. i) cere ca factura să cuprindă baza de impozitare pentru fiecare cotă, prețul unitar fără taxă și reducerile de preț, „în cazul în care acestea nu sunt incluse în prețul unitar". Rezultă două variante corecte:
1. **Discount inclus în prețul unitar.** Pe linie apare direct prețul redus și nu mai trebuie arătată separat reducerea.
2. **Discount separat.** Apare prețul întreg, iar reducerea se înscrie distinct, pe linie sau la nivelul facturii.

În e-Factura, structura trebuie să respecte specificațiile RO_CIUS și standardul european la care trimite OUG 120/2021, art. 4 alin. (1). O reducere arătată separat trebuie legată de cota de TVA a bazei pe care o micșorează. Altfel, defalcarea pe cote cerută de lit. i) iese greșită.

### Mai multe cote pe aceeași factură

Baza se raportează „pentru fiecare cotă" (art. 319 alin. (20) lit. i)). Un discount global trebuie repartizat pe cote. Exemplu: factura are produse de 1.000 lei la cota de 21% și de 500 lei la 11%, iar discountul este de 10% pe tot:
- baza 21%: 900 lei, TVA 189 lei;
- baza 11%: 450 lei, TVA 49,50 lei;
- total factură: 1.588,50 lei.

Un discount de 150 lei scăzut doar din baza de 21% ar duce la un TVA colectat greșit, chiar dacă totalul de plată ar ieși la fel.

### Discountul acordat după livrare

Art. 287 lit. c) reduce baza de impozitare când se acordă reduceri de preț după livrare. Art. 330 alin. (2) cere pentru aceasta o factură cu valorile cu semnul minus, transmisă și beneficiarului. Dacă reducerile nu sunt acordate direct clientului, art. 330 alin. (2^1) cere un document centralizator pentru fiecare perioadă fiscală.

Factura electronică deja comunicată nu se poate returna în sistem (OUG 120/2021, art. 4 alin. (8)). Corecția se face potrivit art. 330 din Codul fiscal și se transmite în același sistem (art. 4 alin. (10)). Termenul de transmitere este de 5 zile lucrătoare de la emitere (art. 10 alin. (7), în forma dată de OUG 89/2025).

### Verificări înainte de trimitere

1. Baza pe fiecare cotă este calculată după discount.
2. Reducerea separată are atașată cota de TVA corectă.
3. Suma dintre baze și TVA este egală cu totalul de plată.
4. Discountul ulterior are factură proprie cu minus, cu trimitere la factura inițială.

### De reținut
- Discountul acordat pe loc nu intră în baza de impozitare (art. 286 alin. (4) lit. a)).
- Poate fi inclus în preț sau arătat separat (art. 319 alin. (20) lit. i)).
- Un discount global se repartizează pe cote.
- Discountul ulterior se face prin factură cu minus, transmisă tot în RO e-Factura.
