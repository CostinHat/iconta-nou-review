---
title: "Cum se depune D112 dacă firma nu mai are salariați?"
description: "Ce leagă obligația de depunere a D112 de calitatea de angajator (vectorul fiscal) și cum se comportă generatorul D112 din iConta.eu când tabelul de salariați al firmei e gol."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se depune D112 dacă firma nu mai are salariați?

Obligația de a depune lunar D112 nu ține de existența curentă a unor salariați, ci de calitatea de angajator (sau de plătitor asimilat) și de tipurile de obligații pentru care firma e înregistrată la organul fiscal — ceea ce Codul de procedură fiscală numește „vector fiscal". Practic, o firmă care a avut salariați și le-a încetat contractele nu scapă automat de obligația de raportare doar pentru că, într-o lună, numărul de persoane declarate e zero.

## Temeiul legal

::: ghid-temei
„39. vector fiscal - totalitatea tipurilor de obligații fiscale pentru care există obligații de declarare cu caracter permanent;"
— Legea 207/2015 (Codul de procedură fiscală), art. 1 pct. 39 (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Obligația de depunere a D112 propriu-zise e stabilită astfel:

::: ghid-temei
„Persoanele fizice şi juridice care au calitatea de angajatori sau sunt asimilate acestora, instituţiile şi persoanele fizice prevăzute la art. 68^1 alin. (2), art. 72 alin. (2), art. 84 alin. (8), art. 125 alin. (8) şi (9), art. 147 alin. (1), (1^1), (1^2) şi (1^3), art. 151 alin. (8), art. 169 alin. (1) şi (1^1), art. 174 alin. (5), art. 174^1 alin. (5), art. 220 alin. (1) şi (2) şi art. 220^7 din Legea nr. 227/2015 privind Codul fiscal, [...] au obligaţia depunerii declaraţiei [112] prin mijloace electronice de transmitere la distanţă."
— OPANAF 605/95/928/2314/2026, art. 3 (sursă: anaf_surse/opanaf_605_2026_d112.txt)
:::

Practic, câtă vreme firma și-a păstrat calitatea de angajator (vectorul fiscal e activ), obligația de declarare lunară persistă chiar și pentru o lună fără personal — abia scoaterea din evidență a acestei obligații (prin declarația de mențiuni corespunzătoare) oprește, formal, cerința de raportare recurentă.

## Ce se greșește în practică

- Se presupune că lipsa salariaților dintr-o lună anulează automat obligația de declarare — de fapt, obligația e legată de vectorul fiscal activ, nu de existența unor persoane cu contracte în luna respectivă.
- Se uită deregistrarea formală a vectorului „angajator" atunci când firma nu mai are, cu adevărat, intenția de a mai angaja — fără această mențiune, obligația recurentă de declarare rămâne deschisă în evidența ANAF.
- Se confundă „firmă fără salariați într-o lună" cu „firmă care nu a fost niciodată angajator" — a doua categorie nu are, de la bun început, obligația de a depune D112.

## Ce face iConta.eu

Registrul de salariați (F078, `core/salariati_api.py`) nu are o funcție specifică pentru situația „firmă fără salariați" — el gestionează operațiile obișnuite de creare, editare și încetare a contractelor înregistrate în aplicație. Ce contează pentru întrebarea din acest ghid e comportamentul generatorului D112 propriu-zis (`core/d112.py`), verificat direct în cod: funcția care citește datele salariaților (`pull`) interoghează tabelul pe cursor, nu pe rânduri, exact ca să prindă și cazul unui tabel gol — o firmă fără niciun salariat activ în luna respectivă generează în continuare o declarație D112, cu valorile aferente la zero, nu o eroare sau o declarație lipsă.

Decizia dacă, pentru acea lună, declarația trebuie totuși depusă la ANAF (pentru că vectorul fiscal e activ) rămâne una legală, în afara aplicației — iConta.eu nu verifică și nu semnalează starea vectorului fiscal al firmei la ANAF, nici nu recomandă automat deregistrarea calității de angajator atunci când ultimul salariat își încetează contractul.

[iConta.eu](/)
