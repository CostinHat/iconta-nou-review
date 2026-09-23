---
title: Cum fac un control fiscal intern înainte să vină ANAF?
description: Un control intern complet nu se rezumă la un singur indicator — dar verificarea automată a regimului de TVA față de datele oficiale ANAF e o piesă concretă, verificată, pe care o poți folosi ca punct de plecare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum fac un control fiscal intern înainte să vină ANAF?

Un control fiscal intern serios se bazează pe documente justificative solide și pe corelarea datelor firmei cu ce are ANAF înregistrat — pentru că, la un control real, sarcina de a dovedi actele și faptele care au stat la baza declarațiilor revine contribuabilului, nu inspectorului. O piesă concretă a acestui control, verificată aici, e compararea automată dintre regimul de TVA setat în firmă și cel pe care îl are efectiv ANAF.

## Temeiul legal

::: ghid-temei
"Documentele justificative și evidențele contabile ale contribuabilului/plătitorului constituie probe la stabilirea bazei de impozitare."
— Codul de procedură fiscală (Legea 207/2015), art. 72

"Contribuabilul/Plătitorul are sarcina de a dovedi actele și faptele care au stat la baza declarațiilor sale și a oricăror cereri adresate organului fiscal."
— Codul de procedură fiscală, art. 73 alin. (1)
:::

## Ce verifică automat aplicația

La fiecare salvare a regimului de TVA (Vector fiscal sau Configurare emitere), aplicația interoghează live serviciul oficial ANAF (`PlatitorTvaRest`) și compară statutul de plătitor TVA setat local cu cel din răspunsul ANAF: dacă cele două coincid, situația e „verde"; dacă diferă, „roșu"; dacă ANAF nu poate fi interogat sau nu întoarce o valoare, „gri" — niciodată un avertisment pe date necunoscute. O divergență identificată aici poate face „roșie" evaluarea generală a firmei, chiar dacă toate declarațiile sunt depuse la timp.

De onestitate: comparația se face doar la salvarea manuală a regimului de TVA, nu periodic — dacă statutul de plătitor TVA se schimbă la ANAF fără ca tu să mai atingi acel ecran, firma poate rămâne cu o comparație veche până la următoarea editare.

## Ce se greșește în practică

- Se presupune că un control intern se rezumă la verificarea regimului de TVA — el e doar o piesă; documentele justificative pentru fiecare operațiune rămân baza reală de apărare la un control.
- Se salvează regimul de TVA o singură dată, la înființare, și nu se mai revine niciodată la acel ecran — situația poate rămâne „verde" fals, dacă ANAF a înregistrat între timp o schimbare.
- Se ignoră starea gri, presupunând că e echivalentă cu verde — gri înseamnă doar că ANAF nu a putut fi interogat sau nu a răspuns, nu că situația e confirmată corectă.

## Ce face iConta.eu

Aplicația compară automat, la fiecare salvare a regimului de TVA, statutul local cu cel raportat live de ANAF, și marchează divergențele ca element al evaluării generale a firmei. Comparația se limitează strict la statutul de plătitor TVA (nu acoperă TVA la încasare sau alte regimuri) și se reîmprospătează doar la editare manuală, nu automat — pentru un control intern complet, aceasta rămâne o piesă printre mai multe, alături de documentele justificative pentru fiecare operațiune înregistrată.

[iConta.eu](/)
