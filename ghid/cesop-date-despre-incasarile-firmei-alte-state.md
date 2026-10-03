---
title: "CESOP: ce date despre încasările firmei din alte state păstrează și transmit băncile?"
description: "Banca păstrează, pe trimestre, numele firmei beneficiare, codul ei de TVA, IBAN-ul, adresa și detaliile fiecărei plăți transfrontaliere: data, suma, moneda și statul de origine. Le ține trei ani și le transmite fiscului."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# CESOP: ce date despre încasările firmei din alte state păstrează și transmit băncile?

Prestatorii de servicii de plată, cum sunt băncile, păstrează pentru fiecare trimestru **evidențe despre beneficiarii plăților transfrontaliere și despre fiecare plată**. Pentru firma care încasează din alte state, evidența cuprinde **identitatea ei** (nume, cod de TVA, dacă e disponibil, IBAN și adresă) și **detaliile fiecărei încasări**: data și ora, valoarea, moneda, statul de origine și referința plății. Datele se păstrează electronic **trei ani** și se pun la dispoziția fiscului printr-un formular electronic standard.

Pentru firmă, consecința practică e că încasările transfrontaliere ajung la autoritățile fiscale independent de ce declară ea. Diferențele dintre aceste date și declarațiile de TVA pot fi identificate la control.

## Temeiul legal

::: ghid-temei
„(2) Prestatorii de servicii de plată sunt obligați să păstreze evidențe ale beneficiarilor plăților și ale plăților în legătură cu serviciile de plată pe care le prestează pentru fiecare trimestru calendaristic, pentru a permite organelor fiscale competente să efectueze controale privind livrările de bunuri și prestările de servicii care, în conformitate cu prevederile capitolului V din prezentul titlu, se consideră că au loc în România, în vederea atingerii obiectivului de combatere a fraudei în domeniul TVA."
— Codul fiscal (Legea 227/2015), art. 321^2 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„b) numele sau denumirea comercială a beneficiarului plății, astfel cum figurează în evidențele prestatorului de servicii de plată; ... c) dacă este disponibil, orice cod de înregistrare în scopuri de TVA sau alt cod fiscal național al beneficiarului plății; ... d) codul IBAN sau, în absența codului IBAN, orice alt identificator care identifică fără echivoc și furnizează locația beneficiarului plății;"
— Codul fiscal (Legea 227/2015), art. 321^2 alin. (11) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„a) data și ora efectuării plății sau a restituirii plății; ... b) valoarea și moneda plății sau a restituirii plății; ... c) statul membru de origine al plății primite de sau în numele beneficiarului plății"
— Codul fiscal (Legea 227/2015), art. 321^2 alin. (12) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce conține evidența (art. 321^2 alin. (11)):

- **Despre banca beneficiarului:** codul BIC sau alt cod care o identifică.
- **Despre firmă:** numele sau denumirea; codul de TVA ori alt cod fiscal, dacă e disponibil; IBAN-ul sau alt identificator al locației; adresa, dacă e disponibilă.
- **Fără cont de plăți:** dacă firma primește fonduri fără să aibă un cont de plăți, se înregistrează BIC-ul prestatorului care acționează în numele ei.
- **Despre plăți și restituiri:** detaliile oricărei plăți transfrontaliere și ale oricărei restituiri legate de acestea.

Detaliile fiecărei plăți (art. 321^2 alin. (12)): data și ora; valoarea și moneda; statul de origine sau, la restituiri, statul de destinație, împreună cu informațiile din care rezultă; referința unică a plății; mențiunea că plata a fost inițiată la sediul fizic al comerciantului, dacă e cazul.

Păstrare și transmitere (art. 321^2 alin. (7)):

- evidențele se păstrează electronic **trei ani calendaristici** de la sfârșitul anului plății;
- se pun la dispoziția organului fiscal, potrivit art. 24b din Regulamentul (UE) nr. 904/2010, prin formular electronic standard;
- termenul este sfârșitul lunii care urmează trimestrului, chiar dacă ultima zi este nelucrătoare.

Obligația privește doar plățile transfrontaliere (alin. (3)) și se aplică numai peste un anumit număr de plăți pe trimestru către același beneficiar (alin. (4)). Ea aparține prestatorului de servicii de plată. Articolul nu impune firmei beneficiare o declarație proprie.

::: ghid-exemplu
SC Exemplu SRL vinde online produse cosmetice și încasează, în trimestrul II 2026, 140 de plăți cu cardul de la clienți din Austria, prin procesatorul ei de plăți. Pentru fiecare plată, evidența procesatorului conține: denumirea SC Exemplu SRL, codul ei de TVA, IBAN-ul, data și ora, suma și moneda, Austria ca stat de origine și referința tranzacției. Evidența pe trimestrul II se pune la dispoziția organului fiscal până pe 31 iulie 2026 și se păstrează până la 31 decembrie 2029.
:::

## Ce se greșește în practică

- Se crede că încasările mici, prin card sau prin procesatori de plăți, nu sunt vizibile fiscului.
- Vânzările la distanță către consumatori din alte state nu se declară, deși încasările lor sunt raportate de prestatorul de plăți.
- Se presupune că firma trebuie să depună ea o declarație privind plățile primite.
- Restituirile către clienți se ignoră în evidența proprie, deși apar și ele în evidența prestatorului.

## Ce face iConta.eu

iConta.eu importă extrasele bancare, inclusiv în formatul standard MT940, și propune note contabile pentru încasările de la parteneri, cu identificarea partenerului din descrierea operațiunii. Aplicația nu are acces la evidențele pe care băncile le transmit fiscului și nu face reconcilieri cu acestea. Concordanța dintre încasările transfrontaliere și facturile sau declarațiile de TVA ale firmei o verifică contabilul.

[iConta.eu](/)
