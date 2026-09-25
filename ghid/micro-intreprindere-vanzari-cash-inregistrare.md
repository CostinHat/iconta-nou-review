---
title: "Micro întreprindere cu vânzări cash: înregistrare"
description: "Documentul justificativ pe baza căruia o microîntreprindere care încasează numerar își înregistrează veniturile, relevant pentru baza impozabilă a impozitului micro."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Micro întreprindere cu vânzări cash: înregistrare

O microîntreprindere plătește impozit pe veniturile realizate, nu pe profit — ceea ce face ca înregistrarea corectă și completă a fiecărei încasări în numerar să conteze direct pe baza de impozitare, nu doar pe corectitudinea evidenței contabile. Documentul care stă la baza acestei înregistrări diferă în funcție de dacă firma folosește sau nu casă de marcat electronică fiscală.

## Temeiul legal

::: ghid-temei
„CHITANȚA (Cod 14-4-1) [...] Chitanța și chitanța pentru operațiuni în valută sunt documente justificative de înregistrare în registrul de casă/registrul de casă în valută și în contabilitate a încasărilor și plăților efectuate în numerar (lei/valută), precum și a depunerilor de sume la casieria entității. [...] În condițiile utilizării aparatelor de marcat electronice fiscale, în conformitate cu prevederile legale, documentul în baza căruia se înregistrează în contabilitate veniturile aferente încasărilor zilnice este Raportul fiscal de închidere zilnică, respectiv Registrul special întocmit în condițiile defectării aparatelor de marcat electronice fiscale."
— OMFP nr. 2.634/2015 privind documentele financiar-contabile, anexa 2 (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Ce rezultă din text pentru o microîntreprindere cu vânzări în numerar:

- **Dacă firma folosește casă de marcat electronică fiscală (AMEF)**, documentul justificativ pentru veniturile din încasările zilnice nu e chitanța, ci **Raportul fiscal de închidere zilnică** — vânzarea cu amănuntul către persoane fizice, plătită cash, se recunoaște pe baza acestui raport, nu prin emiterea unei chitanțe pentru fiecare tranzacție.
- **Dacă AMEF e defectă**, legea prevede un substitut: **Registrul special** întocmit pe perioada defectării, care preia rolul de document justificativ până la repunerea în funcțiune a aparatului.
- **Chitanța rămâne documentul justificativ** pentru încasările în numerar care nu trec prin AMEF — de exemplu, încasări de la alte firme (B2B), unde nu există obligația casei de marcat.
- Toate aceste încasări, indiferent de documentul care le justifică, intră în **baza de calcul a impozitului micro**, care se aplică veniturilor realizate — o vânzare cash neînregistrată corect nu doar că expune firma la riscul unui control, dar subevaluează direct impozitul datorat.

## Ce se greșește în practică

- Se emit chitanțe pentru vânzări cu amănuntul care ar trebui să treacă prin casa de marcat, dublând sau confundând documentul justificativ corect (Raportul fiscal de închidere zilnică) cu unul care nu e cel prevăzut pentru acest tip de operațiune.
- Se omite folosirea Registrului special în perioadele de defectare a AMEF, ceea ce lasă încasările din acea perioadă fără document justificativ conform.
- Se înregistrează în contabilitate doar suma „raportată" de casa de marcat la sfârșitul zilei, fără reconcilierea cu soldul efectiv de numerar din registrul de casă — diferențele (lipsuri sau plusuri de casă) rămân astfel nedescoperite.

## Ce face iConta.eu

Modulul `core/amef_import.py` importă datele din aparatele de marcat electronice fiscale, confirmat direct din cod — funcționalitate relevantă exact pentru scenariul unei microîntreprinderi cu vânzări cash prin AMEF. Reconcilierea automată dintre raportul zilnic AMEF și soldul din registrul de casă (`core/casa.py`), pentru a semnala lipsuri sau plusuri de casă, nu a fost confirmată ca funcționalitate dedicată separat — dacă există, verificarea revine contabilului pe baza celor două surse de date oferite de aplicație.

[iConta.eu](/)
