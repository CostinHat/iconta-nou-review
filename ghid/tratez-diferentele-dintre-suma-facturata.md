---
title: "Cum tratez diferențele dintre suma facturată și suma virată de procesator?"
description: "De ce venitul din vânzare și comisionul procesatorului de plăți se înregistrează separat, nu compensat, potrivit principiului necompensării din OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum tratez diferențele dintre suma facturată și suma virată de procesator?

Când un procesator de plăți (card, marketplace, platformă de încasare online) virează în cont o sumă mai mică decât valoarea facturată clientului — pentru că a reținut comisionul propriu — diferența nu se „pierde" contabil și nu se scade direct din venit. Legea cere ca venitul integral și cheltuiala cu comisionul să fie recunoscute separat.

## Temeiul legal

::: ghid-temei
„Principiul necompensării. Orice compensare între elementele de active și datorii sau între elementele de venituri și cheltuieli este interzisă. Toate creanțele și datoriile trebuie înregistrate distinct în contabilitate, pe bază de documente justificative."
— OMFP 1802/2014, reglementări contabile, pct. 56 alin. (1)-(2) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat la o diferență generată de un procesator de plăți:

- **Venitul din vânzare se înregistrează integral**, la valoarea facturată clientului — nu la suma netă primită efectiv în cont după reținerea comisionului.
- **Comisionul procesatorului se recunoaște separat**, ca o cheltuială distinctă (de regulă, cheltuieli cu serviciile bancare și asimilate), pe baza documentului justificativ emis de procesator (raport de decontare, factură de comision).
- Diferența dintre suma facturată și suma virată efectiv corespunde, contabil, unei **creanțe stinse parțial prin compensare cu o cheltuială** — dar acest lucru trebuie contabilizat explicit (încasare integrală urmată de plata comisionului, sau recunoașterea distinctă a celor două fluxuri), nu prin simpla înregistrare a sumei nete primite ca „venit".
- Situația e diferită de compensările legale între creanțe și datorii reciproce față de aceeași entitate, care pot fi înregistrate „numai după contabilizarea creanțelor și veniturilor, respectiv a datoriilor și cheltuielilor corespunzătoare" (pct. 56 alin. (3)) — deci chiar și o compensare permisă legal presupune, mai întâi, recunoașterea separată a ambelor elemente.

## Ce se greșește în practică

- Se înregistrează direct suma netă primită de la procesator ca venit din vânzare, „economisind" o notă contabilă — asta subraportează atât venitul, cât și cheltuiala cu comisionul, denaturând cifra de afaceri și baza de calcul a unor indicatori (de exemplu, plafonul de TVA sau cel de microîntreprindere).
- Se ignoră documentul justificativ al procesatorului (raportul de decontare) la reconcilierea încasărilor, tratând extrasul bancar ca singură sursă de adevăr, deși el arată doar suma netă, nu structura reală a operațiunii.
- Se confundă comisionul procesatorului cu o reducere comercială acordată clientului — cele două au tratamente fiscale și contabile diferite: reducerea comercială scade baza de impozitare a vânzării, comisionul procesatorului e o cheltuială a vânzătorului.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu reconciliază automat diferențele dintre suma facturată și suma virată de un procesator de plăți** — aplicația citește extrasele bancare (inclusiv formatele uzuale ING/Jasper) și le pune la dispoziția contabilului pentru asociere cu facturile emise, dar separarea corectă a venitului brut de comisionul reținut de procesator, conform principiului necompensării, rămâne o operațiune pe care contabilul o face pe baza raportului de decontare al procesatorului.

[iConta.eu](/)
