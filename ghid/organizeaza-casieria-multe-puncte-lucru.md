---
title: "Cum se organizează casieria la mai multe puncte de lucru"
description: "Regula contabilă potrivit căreia registrul de casă documentează operațiunile fiecărei casierii, cu implicații directe pentru firmele cu mai multe puncte de lucru."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se organizează casieria la mai multe puncte de lucru

O firmă cu mai multe puncte de lucru care încasează/plătește numerar la fiecare dintre ele are, de regulă, mai multe case fizice — și, din perspectiva reglementărilor contabile, fiecare casierie generează propriile documente de casă, pe baza cărora se stabilește separat soldul zilnic.

## Temeiul legal

```
::: ghid-temei
„REGISTRUL DE CASĂ (Cod 14-4-7A și Cod 14-4-7bA) [...] Registrul de casă servește ca: - document de înregistrare operativă a încasărilor și plăților în numerar (lei sau valută), efectuate prin casieria entității; - document de stabilire, la sfârșitul fiecărei zile, a soldului de casă; - document de înregistrare în contabilitate a operațiunilor de casă. Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți."
— OMFP nr. 2.634/2015 privind documentele financiar-contabile, anexa 2 (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::
```

Ce rezultă din text pentru firmele cu mai multe puncte de lucru:

- **Registrul de casă se ține pe casierie**, nu la nivelul întregii entități ca un singur document unic — dacă firma are casă fizică la fiecare punct de lucru, fiecare casierie își întocmește propriul registru zilnic, cu soldul ei propriu.
- **Soldul de casă se stabilește zilnic**, separat, pentru fiecare casierie în parte — nu se consolidează automat într-un sold unic pe firmă decât la nivelul situațiilor financiare, unde toate soldurile de casă se agregă în contul contabil 5311.
- Documentele justificative (chitanțe, dispoziții de plată/încasare către casierie) se emit **la nivelul fiecărei case**, cu numerotare proprie, pentru trasabilitate.
- Plafoanele legale pentru încasări/plăți în numerar (Legea nr. 70/2015) se verifică **pe zi și pe persoană/partener**, nu separat pe fiecare punct de lucru — dacă aceeași firmă are relații cu același partener prin mai multe puncte de lucru, sumele încasate/plătite prin toate casele se cumulează în verificarea plafonului zilnic.

## Ce se greșește în practică

- Se ține un singur registru de casă „centralizat" pentru toată firma, în care se amestecă operațiunile mai multor case fizice — practică ce face verificarea soldului de casă la fiecare punct de lucru imposibilă, deși norma cere stabilirea zilnică a soldului „de casă", nu a unui sold agregat pe firmă.
- Se verifică plafonul legal de numerar separat, pe fiecare punct de lucru, considerând că sunt „entități" distincte — plafonul se aplică la nivel de persoană juridică (firma), pe zi și pe partener, indiferent prin câte case a trecut suma.
- Se omite inventarierea periodică a numerarului la fiecare casă în parte, mulțumindu-se cu o verificare centralizată care nu surprinde eventualele diferențe locale.

## Ce face iConta.eu

Din verificarea codului, tabelul `casa_operatiuni` folosit de `core/casa_api.py` **nu are un câmp dedicat punctului de lucru** — registrul de casă din aplicație este, la data acestui ghid, **unic per firmă (schema tenant)**, nu structurat pe mai multe case fizice separate. Pentru o firmă cu mai multe puncte de lucru, funcția `verifica_plafon` din `core/casa.py` calculează corect plafonul agregat pe zi/partener la nivelul întregii firme (ceea ce corespunde regulii legale), dar ținerea unor registre de casă separate, cu solduri zilnice distincte pe fiecare punct de lucru, nu e susținută nativ — dacă acest lucru e necesar, evidența separată pe puncte de lucru trebuie ținută în afara aplicației sau folosind câmpul „document"/„partener" ca marcaj convențional.

[iConta.eu](/)
