---
title: "Retur de bunuri cu risc fiscal ridicat nerecepționate de client: trebuie cod UIT?"
description: "Da. Returul în țară al bunurilor cu risc fiscal ridicat nerecepționate, între firme diferite sau între o firmă și o persoană fizică, este un transport monitorizat și are nevoie de cod UIT."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Retur de bunuri cu risc fiscal ridicat nerecepționate de client: trebuie cod UIT?

Da. OUG 41/2022 enumeră expres, printre transporturile monitorizate pe teritoriul național, returul bunurilor cu risc fiscal ridicat care **nu au făcut obiectul recepției**. Regula se aplică atât între doi operatori economici diferiți, cât și între un operator economic și o persoană fizică. Drumul înapoi la furnizor are deci nevoie de un cod UIT propriu. Codul obținut pentru livrarea inițială nu acoperă returul.

Cazul e frecvent la distribuția de fructe și legume, băuturi sau materiale din oțel: clientul refuză marfa la descărcare, iar camionul se întoarce încărcat. Ce contează pentru ghid este un singur lucru: marfa se întoarce, pe drumuri publice din România, fără să fi fost recepționată.

## Temeiul legal

::: ghid-temei
„9. transport care face obiectul monitorizării pe teritoriul național:"
— OUG 41/2022, art. 2 pct. 9, partea introductivă (sursă: anaf_surse/oug_41_2022.txt)

„i) transportul pe teritoriul național al bunurilor cu risc fiscal ridicat returnate, care nu au făcut obiectul recepției, între operatori economici diferiți sau între un operator economic și o persoană fizică;"
— OUG 41/2022, art. 2 pct. 9 lit. i) (sursă: anaf_surse/oug_41_2022.txt)
:::

Ce rezultă concret:

- **Returul e un transport distinct.** Are propriul loc de încărcare (la client) și propriul loc de descărcare (la furnizor). Codul UIT al livrării inițiale nu acoperă returul, pentru că datele declarate, inclusiv traseul, nu mai corespund. După punerea în mișcare, datele nu se mai pot modifica (art. 11 alin. (3)).
- **Se aplică doar bunurilor cu risc fiscal ridicat**, adică bunurilor din lista stabilită prin ordin al președintelui ANAF (art. 2 pct. 2 și art. 15 alin. (2)).
- **Include returul de la persoane fizice.** Litera i) acoperă expres și returul dintre un operator economic și o persoană fizică, caz care altfel nu ar intra în tranzacțiile dintre firme.
- **Cine declară.** Art. 8 alin. (1) nu are o literă separată pentru retur. Procedura de aplicare se stabilește prin ordin comun ANAF și al Autorității Vamale Române (art. 15 alin. (1)). Declarantul și tipul de operațiune se stabilesc potrivit acestei proceduri, în forma în vigoare.

::: ghid-exemplu
SC Exemplu SRL livrează 2.000 kg de roșii (NC 0702) către SC Client SRL, pe o factură de 8.000 lei fără TVA, cu cod UIT obținut pentru livrare. La descărcare, clientul refuză marfa pentru că nu respectă calitatea din contract și nu o recepționează. Camionul se întoarce la depozitul SC Exemplu SRL.

- Livrarea: cod UIT pentru traseul depozit → client.
- Returul: un nou cod UIT pentru traseul client → depozit, obținut înainte ca vehiculul să plece de la client.
- În contabilitate, stocul rămâne la SC Exemplu SRL, iar livrarea se anulează sau se stornează conform documentelor.
:::

## Ce se greșește în practică

- **Se folosește la retur codul UIT al livrării.** Traseul declarat e altul, iar datele înregistrate nu se mai pot modifica după pornirea vehiculului.
- **Se omite returul pentru că „nu e o vânzare”.** Obligația ține de transportul bunurilor, nu de existența unei noi facturi.
- **Se ignoră returul de la persoane fizice.** Textul îl include expres.
- **Se confundă cu returul după recepție.** Dacă bunurile au fost recepționate și apoi trimise înapoi, situația nu mai intră la litera i). Ea se analizează ca transport între operatori economici diferiți (art. 2 pct. 9 lit. e)).

## Ce face iConta.eu

Pe cardul e-Transport, iConta.eu generează XML-ul unei notificări noi pentru obținerea codului UIT, cu locurile de pornire și sosire completate separat. Pentru un retur, se introduc ca traseu locația clientului și depozitul furnizorului. Aplicația nu leagă automat returul de notificarea livrării inițiale. Alegerea declarantului și a tipului de operațiune pentru retur rămâne decizia contabilului.

[iConta.eu](/)
