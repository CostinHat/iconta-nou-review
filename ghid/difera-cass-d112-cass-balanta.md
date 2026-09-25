---
title: "De ce diferă CASS din D112 de CASS din balanță?"
description: "Cauze legale pentru care CASS-ul raportat prin D112 poate să nu coincidă cu suma calculată direct din brutul de pe statul de plată sau din balanță."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# De ce diferă CASS din D112 de CASS din balanță?

La fel ca la CAS, o diferență între CASS-ul din D112 și o sumă calculată rapid din balanța contabilă are, în general, o cauză legală precisă — nu o eroare de introducere a datelor.

## Temeiul legal

::: ghid-temei
„Calculul contribuției de asigurări sociale de sănătate se realizează prin aplicarea cotei prevăzute la art. 156 asupra bazelor lunare de calcul menționate la art. 157, 157^1 sau 157^4-157^9, după caz."
— Legea nr. 227/2015, art. 168 alin. (5) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Prevederile art. 146 alin. (5^6)-(5^9) se aplică în mod corespunzător."
— Legea nr. 227/2015, art. 168 alin. (6^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Explicația diferenței:

- Art. 168 alin. (6^1) **trimite direct** la regula bazei minime de la CAS (art. 146 alin. (5^6)-(5^9)) — deci și CASS are, pentru contracte cu normă întreagă sau part-time, un **prag minim** obligatoriu, calculat pe salariul minim pe economie, corespunzător zilelor lucrătoare active în lună.
- Dacă brutul contractual e sub acest prag, CASS din D112 nu e „brut × 10%", ci pragul minim × 10%, proporționat — de aici diferența față de un calcul rapid făcut în balanță pe brutul contabil.
- Tichetele de masă complică suplimentar tabloul: contravaloarea lor intră în baza CASS conform normelor de aplicare, dar nu și în baza CAS — o balanță care tratează cele două contribuții simetric va diverge de la valoarea reală a CASS.

## Ce se greșește în practică

- Se calculează CASS ca „brut × 10%" direct din balanță, fără verificarea bazei minime obligatorii de la art. 168 alin. (6^1), mai ales pentru salariile mici sau part-time.
- Se tratează CAS și CASS simetric în privința tichetelor de masă, deși acestea intră în baza CASS, dar nu în baza CAS — o eroare frecventă de generalizare între cele două contribuții.
- Se compară un total simplificat pe toată firma cu totalul real din D112, care aplică regulile (bază minimă, concediu medical, tichete) separat, pe fiecare angajat.

## Ce face iConta.eu

La data acestui ghid, iConta.eu recalculează independent CASS pentru fiecare salariat, printr-o a doua cale de verificare separată de generatorul principal, pentru cazul simplu (brut peste minim, lună întreagă, fără concediu medical, fără tichete de reconciliat) — și pentru cazul angajaților peste minim cu tichete de masă, unde reconciliază separat CAS-ul aferent. Diferențele identificate de acest gard sunt semnalate explicit, cu numele angajatului și ambele valori, nu corectate tacit.

[iConta.eu](/)
