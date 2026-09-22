---
title: Cum corectez soldul TVA preluat greșit în D300?
description: Soldul reportat din luna precedentă (rd.38 sau rd.41) e un câmp manual, nu se preia automat — dacă a fost introdus greșit, se corectează editând acel rând în perioada curentă, nu prin depunerea unui decont „rectificativ”, care nu există pentru D300.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum corectez soldul TVA preluat greșit în D300?

Soldul TVA de plată sau soldul sumei negative din luna anterioară nu se transferă automat în decontul lunii curente — contabilul îl introduce manual, la fiecare depunere. Dacă a fost introdus greșit, corectarea nu se face prin depunerea unei „rectificative” — D300 nu are acest mecanism. Se corectează în perioada în care greșeala a fost făcută sau, dacă termenul a trecut deja, prin rândul corect din perioada curentă.

## Temeiul legal

::: ghid-temei
„Rândul 38 - se preia suma prevăzută la rândul 44 din decontul perioadei precedente celei de
raportare, din care se scad sumele achitate până la data depunerii decontului.”

„Rândul 41 - se preia suma prevăzută la rândul 45 din decontul perioadei precedente celei de
raportare, pentru care nu s-a solicitat rambursarea, prin bifarea casetei corespunzătoare din
decontul anterior.”
— OPANAF 174/2026, instrucțiuni rd.38 și rd.41

„Nu se admit întocmirea şi depunerea de deconturi rectificative pentru corectarea datelor
din deconturile anterioare.”
— OPANAF 174/2026, instrucțiuni de completare
:::

## De ce apare greșeala și cum se corectează

Rândurile 38 (sold de plată reportat) și 41 (sold negativ reportat) sunt câmpuri manuale — aplicația nu le calculează automat din decontul lunii precedente, pentru că formularul cere explicit ca ele să fie transcrise, iar rd.38 se ajustează suplimentar cu sumele deja achitate până la data depunerii. Fiind manuale, sunt un punct predispus la erori de transcriere: o cifră greșită, un rând confundat cu altul, sau uitarea scăderii sumelor deja plătite la rd.38.

Pentru că formularul D300 nu are bifă de „declarație rectificativă” și instrucțiunile interzic explicit depunerea de deconturi rectificative, corectarea unei greșeli la soldul preluat se face astfel:

- dacă decontul greșit nu a fost încă depus la ANAF, se corectează direct rândul manual înainte de depunere;
- dacă a fost deja depus, corectarea se reflectă în decontul perioadei curente sau următoare, ajustând rândul manual corespunzător (rd.38 sau rd.41) cu suma corectă — nu prin refacerea decontului lunii greșite.

## Ce se greșește în practică

- Se transcrie soldul din rd.44/rd.45 al lunii precedente fără să se verifice mai întâi valoarea efectiv depusă la ANAF pentru luna respectivă.
- La rd.38 se uită scăderea sumelor deja achitate până la data depunerii curente — se raportează soldul brut, nu cel net de plăți.
- Se caută opțiunea de „decont rectificativ” pentru D300, care nu există — formularul nu are această bifă, spre deosebire de alte declarații ANAF.
- Se corectează greșeala editând decontul lunii în care a apărut eroarea, deși acel decont a fost deja depus și nu mai poate fi modificat retroactiv.

## Ce face iConta.eu

Câmpurile pentru soldul reportat (rd.38/rd.41, în cod R35/R38) fac parte din setul de rânduri manuale — nu se preiau automat din decontul generat anterior de aplicație, ci trebuie introduse de contabil la fiecare depunere. Aplicația nu are un parametru sau o funcție de „decont rectificativ” — corectarea unei sume greșite se face prin editarea rândului manual corespunzător pentru perioada curentă, exact ca la orice altă regularizare.

[iConta.eu](/)
