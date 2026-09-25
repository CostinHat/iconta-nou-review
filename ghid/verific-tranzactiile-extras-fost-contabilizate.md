---
title: Cum verific dacă toate tranzacțiile din extras au fost contabilizate?
description: Metoda de reconciliere bancă-contabilitate — de la obligația legală de a consemna fiecare operațiune printr-un document justificativ până la punctajul soldurilor.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific dacă toate tranzacțiile din extras au fost contabilizate?

Reconcilierea extrasului de cont cu rulajul contabil al contului 512 nu e un pas opțional de bună practică — pornește de la obligația legală ca fiecare operațiune economico-financiară să fie consemnată în contabilitate pe baza unui document justificativ.

### Temeiul obligației de înregistrare completă

Legea contabilității nr. 82/1991, art. 6 alin. (1): "Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ." Alin. (2): documentele justificative angajează răspunderea celor care le-au întocmit, vizat, aprobat, precum și a celor care le-au înregistrat în contabilitate.

Extrasul de cont emis de bancă este el însuși document justificativ pentru operațiunile bancare — deci principiul din art. 6 se traduce direct: fiecare linie din extras trebuie să aibă o înregistrare contabilă corespunzătoare (și, invers, fiecare înregistrare pe 512 trebuie să aibă o linie corespunzătoare în extras).

### Metoda de verificare (punctaj)

1. **Soldul de control**: soldul final din extrasul bancar la data de închidere trebuie să fie identic cu soldul contabil al contului 512 (analitic pe banca respectivă) la aceeași dată. Orice diferență semnalează fie o operațiune necontabilizată, fie una contabilizată dublu/greșit.
2. **Punctaj linie cu linie**: se bifează fiecare încasare și plată din extras față de rulajul debitor/creditor al contului 512, în ordine cronologică. Operațiunile care apar în extras dar nu au corespondent contabil sunt candidații pentru "tranzacții necontabilizate".
3. **Sume în curs de decontare**: potrivit pct. 302 alin. (2) din Reglementările contabile (OMFP 1802/2014), sumele virate/depuse la bănci, pe bază de documente prezentate entității dar neapărute încă în extrasul de cont, se înregistrează distinct, în contul 5125 "Sume în curs de decontare" — o diferență temporară de acest tip nu e o eroare, ci un decalaj de timp explicabil, care trebuie totuși urmărit până la stingere (apariția în extrasul lunii următoare).
4. **Comisioane și dobânzi bancare**: deseori omise pentru că nu au un document "extern" separat de extras — extrasul însuși e documentul justificativ pentru ele (622/627 = 5121 pentru comisioane; 5121 = 766 pentru dobânzi de încasat).

### Semnale tipice de omisiune

- Plăți card ale angajaților prin avansuri spre decontare (cont 542, potrivit pct. 302 alin. (3) OMFP 1802/2014) care apar în extras ca ieșire din 5121 dar nu au fost transferate corect în 542.
- Încasări de la clienți care nu corespund exact sumei facturate (compensări, discount-uri de plată) și rămân "suspendate" fără contabilizare.
- Taxe/comisioane reținute direct de bancă din suma transferată, pentru care se contabilizează doar suma netă, lăsând diferența nereconciliată.

Reconcilierea lunară, înainte de închiderea perioadei, este singura metodă care garantează că soldul contabil reflectă exact realitatea bancară — orice decalaj netratat se acumulează și devine tot mai greu de identificat pe măsură ce trec lunile.
