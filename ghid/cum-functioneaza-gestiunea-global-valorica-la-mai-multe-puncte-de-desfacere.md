---
title: Cum funcționează gestiunea global-valorică la mai multe puncte de desfacere?
description: Coeficientul de repartizare se poate calcula la nivelul conturilor sintetice sau pe grupe/categorii de stocuri, ceea ce permite urmărirea separată a fiecărui punct de desfacere, dar cere rulaje distincte pe fiecare gestiune.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum funcționează gestiunea global-valorică la mai multe puncte de desfacere?

Un comerciant cu mai multe magazine sau puncte de desfacere care aplică metoda prețului cu amănuntul nu e obligat să calculeze un singur coeficient de repartizare „la nivel de companie”. Legea permite defalcarea pe conturi sintetice, pe grupe sau pe categorii de stocuri — ceea ce, în practică, înseamnă că fiecare punct de desfacere (sau categorie omogenă de marfă) poate avea propriul coeficient K, calculat din propriile rulaje.

## Temeiul legal

::: ghid-temei
> "(4) Repartizarea diferențelor de preț asupra valorii bunurilor ieșite și asupra stocurilor se
> efectuează cu ajutorul unui coeficient care se calculează astfel:
>
> Coeficient de repartizare = [Soldul inițial al diferențelor de preț + Diferențe de preț aferente
> intrărilor în cursul perioadei, cumulat de la începutul exercițiului financiar până la finele
> perioadei de referință] / [Soldul inițial al stocurilor de preț de înregistrare + Valoarea
> intrărilor în cursul perioadei la preț de înregistrare, cumulat de la începutul exercițiului
> financiar până la finele perioadei de referință] × 100
>
> *2) **La calcularea procentului mediu de adaos comercial, soldul inițial al contului de mărfuri
> și valoarea intrărilor de mărfuri nu vor include TVA neexigibilă.** Acest coeficient se înmulțește
> cu valoarea bunurilor ieșite din gestiune la preț de înregistrare, iar suma rezultată se
> înregistrează în conturile corespunzătoare în care au fost înregistrate bunurile ieșite.
>
> (5) Coeficienții de repartizare a diferențelor de preț pot fi calculați la nivelul conturilor
> sintetice de gradul I și II, [...] pe grupe sau categorii de stocuri.
>
> (6) La sfârșitul perioadei, soldurile conturilor de diferențe se cumulează cu soldurile conturilor
> de stocuri, la preț de înregistrare, astfel încât aceste conturi să reflecte valoarea stocurilor
> la costul de achiziție sau costul de producție, după caz.
>
> (7) Diferențele de preț se repartizează proporțional atât asupra valorii bunurilor ieșite, cât și
> asupra bunurilor rămase în stoc."
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, pct. 286 alin. (4)-(7) și
> nota *2).
:::

## Ce înseamnă „pe grupe sau categorii” în practică

Alin. (5) dă libertate de organizare, dar cere consecvență: odată aleasă granularitatea (un coeficient pe toată firma, sau câte unul pe fiecare punct de desfacere / grupă de marfă), rulajele care alimentează formula (soldul și intrările în 371, 378, 4428) trebuie ținute separat, pe aceeași granularitate, altfel coeficientul rezultat amestecă marje și structuri de cote care nu au legătură între ele.

::: ghid-exemplu
Un comerciant cu două magazine — unul cu marfă alimentară (adaos mediu 15%) și unul cu produse electronice (adaos mediu 40%) — care ar calcula un singur K la nivel de firmă ar obține un coeficient „mediu” nereprezentativ pentru niciunul dintre cele două puncte. Ținând gestiuni (și rulaje 371/378/4428) separate pe fiecare punct de desfacere, fiecare magazin își descarcă lunar propriul cost al mărfii vândute cu propriul coeficient, reflectând corect marja reală practicată acolo.
:::

## Ce se greșește în practică

- Se amestecă rulajele mai multor puncte de desfacere într-un singur calcul de K, deși magazinele au structuri de marjă complet diferite.
- Se schimbă granularitatea de calcul (de la „pe firmă” la „pe magazin”) în cursul exercițiului financiar, ceea ce rupe continuitatea cumulului „de la 1 ianuarie” cerut de alin. (4).
- Se uită să se aloce corect stocul inițial de exercițiu (Si371, Si378, Si4428) pe fiecare gestiune/punct de desfacere atunci când se trece de la o evidență centralizată la una descentralizată.
- Se presupune că defalcarea pe puncte de desfacere rezolvă automat problema cotelor multiple de TVA în interiorul aceluiași magazin — de fapt, cele două probleme (granularitate pe gestiune vs. granularitate pe cotă de TVA) sunt independente.

## Ce face iConta.eu

Coeficientul de repartizare K este calculat de `coeficient_k` din soldurile și rulajele conturilor 371, 378 și 4428 transmise de apelant: `K = (Si378 + Rc378) / [(Si371 + Rd371) - (Si4428 + Rc4428)]`, exact formula din pct. 286 alin. (4), cu excluderea TVA neexigibile din numitor conform notei *2). Funcția ridică eroare dacă numitorul e zero sau negativ, semnalând contabilului să verifice soldurile/rulajele. Pentru că funcția primește soldurile și rulajele ca parametri, aceeași logică poate fi rulată separat pe fiecare gestiune sau punct de desfacere, atât timp cât rulajele transmise sunt filtrate corect pe gestiunea respectivă — granularitatea e o decizie de organizare a datelor, nu o limitare a motorului de calcul.

La descărcarea lunară (`descarca_luna`), TVA-ul din 4428 se aproximează dintr-o cotă medie ponderată a stocului cumulat, nu din structura reală vândută în lună — un aspect valabil identic pentru fiecare punct de desfacere calculat separat, care merită verificat gestiune cu gestiune, nu doar la nivel centralizat.

[iConta.eu](/)
