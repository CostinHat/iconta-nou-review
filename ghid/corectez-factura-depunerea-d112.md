---
title: Cum corectez o factură după depunerea D112
description: Depunerea D112 nu blochează facturile în iConta.eu — blochează doar editarea pontajului lunii respective. Corectarea unei facturi urmează un mecanism complet diferit, independent de D112.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez o factură după depunerea D112

Întrebarea asta pornește, de obicei, de la o presupunere greșită: că depunerea D112 „închide" cumva luna pentru toată evidența, facturi incluse. Nu e cazul — verificat direct în cod, depunerea D112 nu blochează nimic legat de facturi sau de notele contabile.

## Ce blochează, de fapt, D112

Singurul lucru pe care depunerea D112 îl blochează în iConta.eu e editarea **pontajului** lunii respective (evidența zilelor lucrate/concediu/absențe folosită la calculul salarial). Verificarea se face pe o evidență separată a depunerilor (`declaratii_depuse`, tip `d112`) și afectează exclusiv tabelul de pontaj — nu tabelul de perioade blocate folosit de facturi și note contabile, și nu are nicio verificare echivalentă pe `facturi`.

Cu alte cuvinte: **D112 depusă ≠ lună blocată contabil.** Sunt evenimente diferite, pe tabele diferite, fără nicio legătură cablată între ele.

## Cum se corectează, de fapt, o factură

Corectarea unei facturi în iConta.eu depinde exclusiv de starea funcției **Blocare perioade** (Registru jurnal), nu de D112:

- Dacă luna **nu** e blocată prin „Blocare perioade", factura emisă greșit se corectează prin stornare (o factură nouă, cu cantități negative, cu propriul număr), la fel ca orice altă corecție de factură.
- Dacă luna **este** blocată prin „Blocare perioade", corectarea urmează exact același drum — stornarea se face oricum cu data de azi, în luna curentă deschisă, deci nu are nevoie de starea D112 și nici de deblocarea lunii vechi.

## Temeiul legal

::: ghid-temei
„Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (stornare în roșu), fie prin înregistrarea inversă a acesteia (stornare în negru), în funcție de politica contabilă și programele informatice utilizate." — OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), pct. 69
:::

Nicio prevedere legală nu leagă corectarea unei facturi de existența unei declarații D112 depuse — cele două aparțin unor zone diferite ale evidenței (salarii vs. facturi/TVA), fiecare cu regimul ei de corecție.

## Ce se greșește în practică

- Se amână corectarea unei facturi, crezând că D112 depusă „blochează" și facturile — nu e cazul; blocajul real, dacă există, vine de la „Blocare perioade", nu de la D112.
- Se caută în mesajele de eroare legate de facturi o referire la D112 — mesajul relevant pentru D112 apare exclusiv la editarea pontajului, nu la facturi.
- Se confundă „lună blocată" (tabelul `perioade_blocate`, valabil pentru facturi/note) cu „D112 depusă" (evidența `declaratii_depuse`, valabilă pentru pontaj) — sunt verificări separate, cu mesaje separate.

## Ce face iConta.eu

Depunerea D112 nu afectează corectarea facturilor — verificarea ei se aplică strict pontajului. O factură se corectează prin storno indiferent de starea D112: o factură nouă, cu liniile negate, datată la momentul corecției, în luna curentă deschisă. Nu există editare directă a unei facturi emise, iar existența unei D112 depuse pe luna respectivă nu schimbă acest mecanism.

[iConta.eu](/)
