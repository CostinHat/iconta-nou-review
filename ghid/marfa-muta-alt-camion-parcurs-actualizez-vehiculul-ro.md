---
title: "Marfa se mută pe alt camion pe parcurs: cum actualizez vehiculul în RO e-Transport?"
description: "Organizatorul transportului sau transportatorul actualizează numărul vehiculului pe același cod UIT, cât timp codul e valabil, înainte ca noul camion să plece."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Marfa se mută pe alt camion pe parcurs: cum actualizez vehiculul în RO e-Transport?

Pe același cod UIT se actualizează **doar datele de identificare ale vehiculului**. Actualizarea o face organizatorul transportului sau operatorul de transport, după caz. Ea se face în perioada de valabilitate a codului UIT și **înainte ca marfa să fie repusă în mișcare** pe noul camion. Nu se emite un cod nou și nu se modifică alte date ale notificării.

Este singura excepție de la regula care interzice modificarea datelor după pornirea vehiculului. Legea acceptă expres că o partidă de bunuri poate schimba mijlocul de transport pe traseu: la defecțiune, la transbordare într-un depozit intermediar sau la schimbarea tractorului.

## Temeiul legal

::: ghid-temei
„(1^1) Prin excepție de la prevederile art. 11 alin. (3) , organizatorul transportului sau operatorul de transport, după caz, are obligația să actualizeze, în perioada de valabilitate a codului UIT, informațiile privind identificarea vehiculului de transport rutier ori de câte ori acestea se modifică, înainte de repunerea în mișcare."
— OUG 41/2022, art. 8 alin. (1^1) (sursă: [OUG nr. 41/2022 pentru instituirea Sistemului național RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/253801))

„(3) Este interzisă modificarea datelor înregistrate în Sistemul RO e-Transport referitoare la transporturile de bunuri după prezentarea în punctul rutier de trecere a frontierei la intrarea în România sau la locul de import, respectiv după punerea efectivă în mișcare a vehiculului pe drumurile publice, după caz."
— OUG 41/2022, art. 11 alin. (3) (sursă: [OUG nr. 41/2022 pentru instituirea Sistemului național RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/253801))

„5. partida de bunuri - denumirea generică dată unui ansamblu indivizibil de bunuri, care are același loc de încărcare și de descărcare, un singur utilizator dintre cei prevăzuți la art. 8 alin. (1) și un singur destinatar final și este transportat cu un mijloc de transport ce poate fi schimbat pe parcursul deplasării de la locul de încărcare la locul de descărcare;"
— OUG 41/2022, art. 2 pct. 5 (sursă: [OUG nr. 41/2022 pentru instituirea Sistemului național RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/253801))
:::

Ce înseamnă concret:

- **Cine actualizează**: organizatorul transportului (de exemplu firma care a comandat transportul sau care transportă în nume propriu) ori operatorul de transport. Nu neapărat declarantul inițial.
- **Ce se actualizează**: numai identificarea vehiculului (numărul de înmatriculare al camionului sau al remorcii). Bunurile, cantitățile și traseul rămân cele declarate.
- **Când**: de fiecare dată când vehiculul se schimbă, înainte de repunerea în mișcare și numai cât timp codul UIT e valabil.
- **Dacă sistemul nu funcționează**: obligația se suspendă și se îndeplinește până la sfârșitul următoarei zile lucrătoare după repunerea în funcțiune (art. 8 alin. (1^2) și (1^3)).

Neactualizarea vehiculului e contravenție. Pentru persoanele juridice, amenda este de la 20.000 la 100.000 de lei (art. 13^1 alin. (1) lit. c) și alin. (3)).

::: ghid-exemplu
SC Exemplu SRL trimite din Constanța spre Cluj 24 t de fier-beton (NC 7214) cu un camion contractat. La Pitești, camionul se defectează, iar transportatorul trimite alt camion, în care marfa este transbordată integral.

- Transportatorul sau SC Exemplu SRL, ca organizator, introduce în RO e-Transport noul număr de înmatriculare pe codul UIT existent.
- Actualizarea se face înainte ca noul camion să plece din Pitești.
- Codul UIT, bunurile și destinația rămân aceleași.
:::

## Ce se greșește în practică

- **Se generează un cod UIT nou pentru același transport.** Legea cere actualizarea vehiculului pe codul existent. Un al doilea cod dublează declarația pentru aceeași partidă.
- **Se pleacă mai întâi și se actualizează la destinație.** Actualizarea se face înainte de repunerea în mișcare.
- **Se profită de actualizare pentru a schimba cantitatea sau destinația.** Aceste date nu mai pot fi modificate după pornire.
- **Actualizarea se face după expirarea codului.** Ea e posibilă doar în perioada de valabilitate.

## Ce face iConta.eu

Cardul e-Transport din iConta.eu generează XML-ul notificării inițiale pentru obținerea codului UIT, cu vehiculul și remorca. Actualizarea vehiculului pe un cod UIT existent **nu este o funcție disponibilă** în aplicație la data acestui ghid. Ea se face direct în sistemul ANAF, de către organizatorul transportului sau de transportator.

[iConta.eu](/)
