---
title: "Cum se înregistrează lucrările în curs pe șantiere"
description: "Lucrările neterminate la sfârșitul lunii pe un șantier intră la producția în curs de execuție — contul 331 — și se reiau la începutul lunii următoare, potrivit reglementărilor contabile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează lucrările în curs pe șantiere

O firmă de construcții care lucrează pe un șantier la finalul lunii, fără să fi predat lucrarea beneficiarului, are o problemă de contabilizare: valoarea muncii deja depuse trebuie reflectată în situațiile financiare ale lunii, deși încă nu există o factură de vânzare. Reglementările contabile tratează exact această situație prin categoria producției în curs de execuție.

## Temeiul legal

::: ghid-temei
„h) producția în curs de execuție, reprezentând producția care nu a trecut prin toate fazele (stadiile) de prelucrare, prevăzute în procesul tehnologic, precum și produsele nesupuse probelor și recepției tehnice sau necompletate în întregime. În cadrul producției în curs de execuție se cuprind, de asemenea, serviciile și studiile în curs de execuție sau neterminate."
— OMFP 1802/2014, pct. 276 alin. (1) lit. h) (Reglementări contabile privind situațiile financiare anuale individuale) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Ce rezultă din text pentru lucrările pe șantier:

- **Norma include explicit serviciile și studiile în curs de execuție sau neterminate** în categoria producției în curs — nu doar bunurile fizice nefinalizate dintr-o fabrică. Lucrările de construcții-montaj neterminate la finalul lunii, deși sunt o prestare de serviciu, intră în această categorie.
- **Criteriul e stadiul de finalizare, nu existența unei facturi** — dacă lucrarea nu a trecut prin toate fazele prevăzute (nu a fost recepționată/predată integral beneficiarului), valoarea ei se recunoaște ca producție în curs, indiferent dacă s-a emis sau nu o factură parțială.
- **Recunoașterea se face la închiderea lunii, pe baza stadiului real al lucrării** — evaluat, de regulă, prin situații de lucrări interne, procente de execuție sau devize actualizate, nu prin estimări arbitrare.
- **La începutul lunii următoare, producția în curs constatată se reia** — soldul recunoscut anterior se anulează, urmând ca noul stadiu al lucrării, la finalul lunii curente, să fie din nou evaluat și înregistrat.

## Ce se greșește în practică

- Se așteaptă factura finală sau procesul-verbal de recepție pentru a înregistra orice valoare legată de șantier, ignorând că norma cere recunoașterea stadiului lucrării la fiecare închidere de lună, indiferent de facturare.
- Se confundă producția în curs de execuție cu o creanță asupra clientului — nu e o creanță (nu există încă o factură emisă și acceptată), ci o evaluare internă a stadiului lucrării, reflectată la stocuri.
- Se omite reluarea la începutul lunii următoare a sumei constatate anterior, ceea ce duce la dublarea valorii producției în curs de la o lună la alta, dacă lucrarea continuă.
- Se estimează stadiul lucrării fără un document de susținere (situație de lucrări, deviz, proces-verbal intern) — o evaluare nedocumentată e greu de justificat la un control ulterior.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un motor dedicat producției în curs de execuție, în `core/productie.py`: funcția `nota_productie_in_curs(suma, moment)` generează nota contabilă de constatare la sfârșitul lunii (331 = 711, pentru suma introdusă) și, simetric, nota de reluare la începutul lunii următoare (711 = 331), pe baza aceleiași sume. Motorul nu evaluează el însuși stadiul lucrării pe șantier și nu declanșează automat reluarea din luna următoare — suma constatată se introduce de contabil, pe baza situației de lucrări sau a devizului actualizat, iar generarea notei de reluare rămâne o acțiune separată, la momentul potrivit.

[iConta.eu](/)
