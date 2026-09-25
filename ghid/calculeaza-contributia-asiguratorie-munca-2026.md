---
title: "Cum se calculează contribuția asiguratorie pentru muncă în 2026?"
description: "Cine datorează CAM, formula de calcul și situațiile în care legea exceptează angajatorul de la plata acestei contribuții."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează contribuția asiguratorie pentru muncă în 2026?

CAM se calculează simplu — o cotă unică aplicată pe baza salarială — dar întrebările frecvente apar la marginile ei: cine o datorează și pentru ce sume nu se calculează deloc.

## Temeiul legal

::: ghid-temei
„Contribuabilii obligați la plata contribuției asiguratorii pentru muncă sunt, după caz: a) persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora, pentru cetățenii români, cetățeni ai altor state sau apatrizii, pe perioada în care au, conform legii, domiciliul sau reședința în România [...]"
— Legea nr. 227/2015, art. 220^1 lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Contribuția asiguratorie pentru muncă nu se datorează pentru prestațiile suportate din bugetul asigurărilor sociale de stat, bugetul asigurărilor pentru șomaj, precum și din Fondul național unic de asigurări sociale de sănătate."
— Legea nr. 227/2015, art. 220^5 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă:

- Debitorul CAM e **angajatorul** (sau entitatea asimilată), nu salariatul — contribuția se calculează prin aplicarea cotei de 2,25% pe baza salarială de la art. 220^4, integral pe cheltuiala angajatorului.
- CAM **nu se datorează** pentru sumele suportate din bugetele publice de asigurări — de exemplu, indemnizațiile de concediu medical plătite din Fondul național unic de asigurări sociale de sănătate nu intră în baza CAM, pentru că nu sunt „câștig brut" plătit de angajator, ci prestație socială.
- Excepția de la art. 220^5 se aplică indiferent de motivul concret al prestației — șomaj, concediu medical sau alte plăți din bugetele de asigurări sociale — cât timp sumele sunt suportate din aceste bugete, nu din costul salarial al angajatorului.

## Ce se greșește în practică

- Se calculează CAM pe indemnizațiile de asigurări sociale de sănătate (concedii medicale) suportate din FNUASS, deși art. 220^5 exclude expres aceste sume din baza de calcul.
- Se presupune că CAM se datorează doar pentru salariile din contracte de muncă „clasice", ignorând că baza include și remunerațiile administratorilor cu contract de mandat sau indemnizațiile de conducere.
- Se tratează CAM ca pe o contribuție a salariatului, similar CAS/CASS, deși legea o stabilește integral în sarcina angajatorului.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează CAM la cota de 2,25% pentru fiecare salariat, pe baza salarială introdusă în modulul de salarizare, și exclude automat din calcul zilele de concediu medical suportate din bugetul asigurărilor sociale de sănătate, conform regulilor aplicate la generarea **D112**. Componentele mai puțin uzuale ale bazei (remunerații de mandat, indemnizații de conducere) se introduc manual de utilizator.

[iConta.eu](/)
