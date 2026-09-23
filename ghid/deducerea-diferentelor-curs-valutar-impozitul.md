---
title: "Deducerea diferențelor de curs valutar la impozitul pe profit"
description: Ca regulă generală, veniturile și cheltuielile din diferențe de curs valutar (665/765) intră în calculul rezultatului fiscal ca orice alt venit sau cheltuială financiară — legea nu le exclude de la deducere. O excepție explicită există pentru diferențele de curs legate de leasingul auto, supuse plafonului de 50%.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Deducerea diferențelor de curs valutar la impozitul pe profit

Diferențele de curs valutar înregistrate în contabilitate (venituri pe 765, cheltuieli pe 665) intră, ca regulă, direct în calculul impozitului pe profit — nu apar printre categoriile de venituri neimpozabile, nici printre cheltuielile nedeductibile enumerate explicit în Codul fiscal. Există însă o excepție punctuală, legată de leasingul auto, unde diferențele de curs sunt supuse aceleiași limitări de 50% ca restul cheltuielilor vehiculului.

## Temeiul legal

::: ghid-temei
„În cazul cheltuielilor aferente vehiculelor rutiere motorizate reprezentând diferențe de curs valutar înregistrate ca urmare a derulării unui contract de leasing, limita de 50% se aplică asupra diferenței nefavorabile dintre veniturile din diferențe de curs valutar/veniturile financiare aferente creanțelor și datoriilor cu decontare în funcție de cursul unei valute, rezultate din evaluarea sau decontarea acestora și cheltuielile din diferențe de curs valutar/cheltuielile financiare aferente" — Codul fiscal, art. 25 alin. (3) lit. l), ultimul paragraf.
:::

## Regula generală

Rezultatul fiscal (baza de calcul a impozitului pe profit) pornește de la rezultatul contabil, ajustat cu veniturile neimpozabile și cheltuielile nedeductibile prevăzute explicit de lege. Diferențele de curs valutar din activitatea curentă — la decontarea facturilor în valută, la reevaluarea lunară a soldurilor și creanțelor/datoriilor în valută — nu se regăsesc printre categoriile enumerate ca nedeductibile la art. 25 alin. (4), nici printre veniturile neimpozabile de la art. 23. Practic, ele urmează regula generală: venitul din diferență favorabilă crește baza impozabilă, cheltuiala din diferență nefavorabilă o reduce, fără o limitare specifică.

## Excepția: leasingul auto

Pentru vehiculele rutiere motorizate supuse limitării de 50% (vehicule sub 3.500 kg, sub 9 locuri, care nu sunt utilizate exclusiv în scopul activității economice — art. 25 alin. (3) lit. l), diferențele de curs valutar apărute din derularea contractului de leasing auto **nu se tratează separat**: legea prevede explicit că plafonul de 50% se aplică asupra diferenței nefavorabile nete dintre veniturile și cheltuielile din diferențe de curs/financiare aferente acelui contract — nu asupra fiecărei diferențe individuale.

Vehiculele exceptate de la plafonul de 50% (folosite exclusiv pentru servicii de urgență, pază, curierat, vânzări, transport de persoane cu plată, instruire auto, mărfuri comerciale) rămân, prin extensie, cu diferențele de curs aferente leasingului integral deductibile, la fel ca restul cheltuielilor lor de funcționare.

## Ce se greșește în practică

- Se aplică plafonul de 50% pe toate diferențele de curs valutar din firmă, generalizând regula de la leasingul auto la orice diferență de curs — regula e specifică vehiculelor supuse acelui plafon, nu o limitare generală.
- Se tratează diferențele de curs ca venituri/cheltuieli „extraordinare", excluse din calculul impozitului pe profit — nu există un asemenea tratament special, ele intră în rezultatul fiscal ca orice alt element financiar.
- Se omite verificarea dacă vehiculul cu leasing în valută se încadrează la categoriile exceptate de la plafonul de 50% (curierat, vânzări, transport de persoane etc.) — pentru acestea, diferențele de curs aferente leasingului rămân integral deductibile.

## Ce face iConta.eu

Aplicația calculează și înregistrează diferențele de curs valutar (665/765) pe baza cursurilor introduse pentru fiecare operațiune, prin motorul de diferențe de curs (`core/diferente_curs.py`). Aceste sume ajung, ca orice altă cheltuială sau venit financiar, în balanța folosită la calculul impozitului pe profit — aplicația nu aplică, în prezent, o ajustare automată separată pentru plafonul de 50% specific diferențelor de curs din leasingul auto; verificarea acestei încadrări punctuale rămâne o decizie a contabilului, la calculul rezultatului fiscal.

[iConta.eu](/)
