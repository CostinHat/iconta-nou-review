---
title: "Ce documente trebuie predate contabilului după înființarea firmei"
description: "Ce spune legea despre documentele justificative pe care se sprijină evidența contabilă și de ce nu există o listă legală unică pentru startul unei firme."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce documente trebuie predate contabilului după înființarea firmei

Fondatorii unei firme noi caută adesea o „listă oficială" de documente pe care trebuie să le predea contabilului la start. O astfel de listă unică nu există în lege — dar principiul care stă la baza ei, da, și el explică de ce anumite documente sunt indispensabile, iar altele nu.

## Temeiul legal

::: ghid-temei
„(1) Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ. (2) Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea contabilității nr. 82/1991, art. 6 alin. (1)-(2) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

**Limitare declarată:** nu am găsit, în sursele verificate, un act normativ care să enumere exhaustiv „documentele de predat contabilului la înființare" ca listă formală — asta e mai degrabă o practică organizatorică, nu o obligație legală distinctă. Ce transează legea e principiul de fond: **orice operațiune economico-financiară trebuie să aibă un document justificativ** care să stea la baza înregistrării ei în contabilitate. De aici derivă, indirect, ce anume trebuie predat:

- Actele care dovedesc **existența legală a firmei** (certificat de înregistrare, act constitutiv) — fără ele, contabilul nu poate identifica firma și regimul ei fiscal (formă juridică, capital social, asociați, sediu, cod CAEN).
- Documentele care dovedesc **primele operațiuni economico-financiare** — extras de cont pentru capitalul social depus, facturi de achiziție inițiale, contracte de închiriere a sediului, dacă există.
- Orice document care **angajează răspunderea fiscală** a firmei de la început — contracte de muncă dacă există angajați, contracte cu furnizori/clienți semnate înainte de preluarea de către contabil.

## Ce se greșește în practică

- Se predau contabilului doar actele de la Registrul Comerțului, fără documentele operațiunilor economice deja efectuate (depunere capital, prime achiziții) — acestea rămân fără document justificativ în evidență.
- Se așteaptă o listă legală unică, universal valabilă pentru orice firmă — realitatea e că documentele necesare depind de operațiunile deja realizate, nu de un formular standard.
- Se ignoră principiul din art. 6: dacă o operațiune s-a produs, dar nu are document justificativ, ea nu poate fi înregistrată corect în contabilitate, indiferent cine „ar trebui" să aibă documentul.

## Ce face iConta.eu

Verificat în cod: nu am găsit în aplicație o funcționalitate de tip „checklist de onboarding" care să genereze automat lista de documente de predat la înființarea firmei. iConta.eu preia datele de identificare ale firmei direct din registrul ANAF (cod CAEN, adresă, stare) prin integrarea cu API-ul public al agenției, dar structurarea documentelor justificative interne ale primelor operațiuni economico-financiare rămâne, la acest moment, în sarcina contabilului.

[iConta.eu](/)
