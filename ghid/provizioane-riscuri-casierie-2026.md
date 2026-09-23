---
title: "Provizioane pentru riscuri de casierie 2026"
description: "Nici Codul fiscal, nici reglementările contabile (OMFP 1802/2014) nu prevăd o categorie distinctă de «provizion pentru risc de casierie» — categoriile de provizioane admise sunt altele, enumerate expres."
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Provizioane pentru riscuri de casierie 2026

Nu există, în reglementările contabile românești, o categorie de provizion numită „risc de casierie". Categoriile de provizioane pe care le recunosc reglementările sunt enumerate expres, iar riscul de casierie (eventuale plusuri/minusuri de casă) nu se numără printre ele — el se tratează prin alte mijloace, nu prin constituirea unui provizion.

## Temeiul legal

::: ghid-temei
„Provizioanele se constituie pentru elemente cum sunt: a) litigii, amenzi și penalități, despăgubiri, daune și alte datorii incerte; b) cheltuielile legate de activitatea de service în perioada de garanție și alte cheltuieli privind garanția acordată clienților; c) dezafectare imobilizări corporale și alte acțiuni similare legate de acestea; d) acțiunile de restructurare; e) pensii și obligații similare; f) impozite; g) terminarea contractului de muncă; h) prime ce urmează a se acorda personalului în funcție de profitul realizat [...]"

*(OMFP nr. 1802/2014 pentru aprobarea Reglementărilor contabile privind situațiile financiare anuale individuale și situațiile financiare anuale consolidate, pct. 377 alin. (1))*
:::

## De ce nu se potrivește „riscul de casierie"

Enumerarea de mai sus nu e strict închisă — textul o introduce cu „cum sunt", iar lista se termină cu o categorie generică, „k) alte provizioane". Dar orice provizion, inclusiv unul încadrat la „alte provizioane", trebuie mai întâi să treacă testul general de recunoaștere de la pct. 369-376: o obligație curentă a firmei, generată de un eveniment anterior, cu o ieșire de resurse probabilă și o estimare credibilă a valorii. Riscul de casierie — posibilitatea unui minus la numărarea casei — nu e o obligație a firmei față de un terț, ci un risc operațional intern; nu există un eveniment anterior care să genereze o datorie certă sau probabilă către altcineva. Diferențele de casă constatate efectiv (plusuri/minusuri) se tratează la momentul constatării, prin regularizare directă, nu prin constituirea anticipată a unui provizion.

## Ce se greșește în practică

- Se constituie un „provizion de risc de casierie" prin analogie cu alte provizioane, fără să existe o bază legală sau contabilă pentru el.
- Se confundă provizionul (o estimare pentru o obligație viitoare incertă) cu o simplă rezervă de prudență pentru gestiunea de casă — concepte diferite.
- Se tratează un minus de casă constatat ca fiind acoperit „din provizion", deși nu exista un provizion valid constituit pentru acest scop.

## Ce face iConta.eu

Modulul de provizioane (`core/provizioane.py`) generează note doar pentru categoriile recunoscute: litigii, garanții, dezafectare, restructurare, impozite și altele — dicționarul intern al aplicației nu conține o categorie „risc de casierie". Casieria (`core/casa.py`) e un modul separat, fără legătură cu motorul de provizioane; eventualele diferențe de casă se gestionează prin acel modul, nu prin F071.

[iConta.eu](/)
