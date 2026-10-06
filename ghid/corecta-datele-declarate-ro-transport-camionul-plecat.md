---
title: "Se pot corecta datele declarate în RO e-Transport după ce camionul a plecat?"
description: "Nu, cu o singură excepție: după punerea în mișcare a vehiculului datele nu mai pot fi modificate, dar datele de identificare a vehiculului se actualizează ori de câte ori se schimbă."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Se pot corecta datele declarate în RO e-Transport după ce camionul a plecat?

Ca regulă, nu. Datele declarate în RO e-Transport pot fi modificate doar până la momentul-cheie al transportului: prezentarea la punctul de trecere a frontierei la intrarea în țară, la locul de import sau punerea efectivă în mișcare a vehiculului pe drumurile publice. După acest moment, modificarea este interzisă.

Singura excepție privește vehiculul: dacă marfa e mutată pe alt camion sau se schimbă numărul de înmatriculare, organizatorul transportului sau transportatorul trebuie să actualizeze informațiile de identificare a vehiculului, în perioada de valabilitate a codului UIT și înainte de repunerea în mișcare. Pentru cabinet asta înseamnă că verificarea datelor (cantități, valori, adrese) trebuie făcută înainte de plecare, nu după.

## Temeiul legal

::: ghid-temei
„(3) Este interzisă modificarea datelor înregistrate în Sistemul RO e-Transport referitoare la transporturile de bunuri după prezentarea în punctul rutier de trecere a frontierei la intrarea în România sau la locul de import, respectiv după punerea efectivă în mișcare a vehiculului pe drumurile publice, după caz."
— OUG 41/2022, art. 11 alin. (3) (sursă: [OUG nr. 41/2022 pentru instituirea Sistemului național RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/253801))

„(1^1) Prin excepție de la prevederile art. 11 alin. (3) , organizatorul transportului sau operatorul de transport, după caz, are obligația să actualizeze, în perioada de valabilitate a codului UIT, informațiile privind identificarea vehiculului de transport rutier ori de câte ori acestea se modifică, înainte de repunerea în mișcare."
— OUG 41/2022, art. 8 alin. (1^1) (sursă: [OUG nr. 41/2022 pentru instituirea Sistemului național RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/253801))
:::

Ce se poate și ce nu:

- **Înainte de plecare** (sau înainte de intrarea în țară, la achiziții intracomunitare și importuri): datele pot fi corectate.
- **După plecare**: nicio modificare a datelor despre bunuri, cantități, parteneri sau locuri de încărcare și descărcare.
- **Excepția vehiculului**: schimbarea vehiculului se actualizează obligatoriu, în valabilitatea codului UIT, înainte de repunerea în mișcare. Obligația e a organizatorului transportului sau a transportatorului, după caz.
- **Sistem nefuncțional**: dacă RO e-Transport nu funcționează, obligația de declarare și de actualizare se suspendă și se îndeplinește până la sfârșitul următoarei zile lucrătoare după repunerea în funcțiune (art. 8 alin. (1^2) și (1^3)).

Nerespectarea art. 11 alin. (3) sau a art. 8 alin. (1^1) se sancționează cu amendă de la 10.000 la 50.000 lei pentru persoane fizice și de la 20.000 la 100.000 lei pentru persoane juridice (art. 13^1 alin. (1) lit. c) și alin. (3)). Dacă datele greșite privesc cantitățile, riscul e mai mare: declararea unor cantități diferite de cele transportate se sancționează separat, cu amendă și cu confiscarea contravalorii bunurilor nedeclarate (art. 13^1 alin. (1) lit. b) și alin. (2)).

## Ce se greșește în practică

- Se descoperă o eroare de cantitate după plecarea camionului și se încearcă „corectarea" declarației; legea nu mai permite modificarea.
- Se schimbă camionul pe traseu (transbordare, defecțiune) și nu se actualizează vehiculul în sistem.
- Se declară cu date estimative („cantitatea se confirmă la încărcare") și nu se revine înainte de plecare.
- Se confundă actualizarea vehiculului, permisă și obligatorie, cu modificarea celorlalte date, interzisă după plecare.

## Ce face iConta.eu

Cardul e-Transport din iConta.eu generează XML-ul notificării în structura oficială v2, cu bunurile, cantitățile, greutățile, valorile, partenerul, locurile de încărcare și descărcare și vehiculul, și verifică câmpurile obligatorii lipsă înainte de generare. Aplicația nu are o funcție dedicată de actualizare a vehiculului după plecare; aceasta rămâne o operațiune a organizatorului transportului sau a transportatorului.

[iConta.eu](/)
