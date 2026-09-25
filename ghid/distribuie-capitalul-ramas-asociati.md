---
title: "Cum se distribuie capitalul rămas între asociați"
description: "Partajul final la lichidarea unei societăți conform Legii 31/1990 și Codului fiscal: capitalul social se restituie neimpozabil, rezervele și profiturile se impozitează cu cota de lichidare de 10%."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se distribuie capitalul rămas între asociați

„Capitalul rămas" de distribuit între asociați apare la finalul lichidării unei societăți, după ce activele au fost valorificate și datoriile stinse — nu e o operațiune curentă de decontare cu asociații, ci ultimul pas al radierii firmei. Regimul fiscal al sumelor distribuite depinde de natura lor: capitalul social propriu-zis se restituie neimpozabil, dar rezervele și profiturile nedistribuite anterior sunt un câștig impozabil pentru asociat, cu o cotă distinctă de cea a dividendelor.

## Temeiul legal

::: ghid-temei
„Venitul impozabil obținut din lichidarea unei persoane juridice de către acționari/asociați persoane fizice sau din reducerea capitalului social, potrivit legii, care nu reprezintă distribuții în bani sau în natură ca urmare a restituirii cotei-părți din aporturi se impun cu o cotă de 10%, impozitul fiind final. Obligația calculării, reținerii și plății impozitului revine persoanei juridice."
— Legea 227/2015 (Codul fiscal), art. 97 alin. (5) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă practic pentru partajul final:

- **Restituirea cotei-părți din aporturi** (capitalul social propriu-zis, în limita a ce a fost vărsat de asociat) **nu e impozabilă** — nu e un câștig, e returnarea propriei contribuții.
- **Tot ce depășește aporturile** — rezerve, profituri nedistribuite acumulate în timp — reprezintă câștig impozabil la asociatul persoană fizică, cu **cota de 10%, impozit final**, distinctă de cota de 16% aplicată dividendelor curente (art. 97 alin. 7 Cod fiscal).
- Obligația de calcul, reținere și plată a impozitului de 10% revine **societății**, nu asociatului — se reține la sursă, din suma de distribuit.
- Termenul de plată a impozitului reținut e legat de momentul depunerii situației financiare finale de lichidare la registrul comerțului (întocmită de lichidatori) sau, pentru reducerea capitalului social, de data de 25 a lunii următoare distribuirii.

## Ce se greșește în practică

- Se aplică aceeași cotă de impozit ca la dividendele curente (16%) și pentru câștigul din lichidare, deși legea prevede explicit o cotă separată, de 10%, pentru acest caz.
- Se confundă restituirea capitalului social (neimpozabilă) cu distribuirea rezervelor/profiturilor acumulate (impozabilă) — tratamentul lor fiscal e complet diferit, deși ambele apar în același partaj final.
- Se omite reținerea la sursă de către societate, lăsând asociatul să declare singur venitul — legea pune obligația de calcul și reținere explicit pe firmă, nu pe asociat.

## Ce face iConta.eu

Această operațiune **nu ține de funcționalitatea Decontări asociați** (dividende curente, împrumuturi, regularizări interimare) — acolo se înregistrează decontările din timpul funcționării normale a firmei. Partajul final la lichidare e acoperit de o funcționalitate separată, **Lichidare/radiere societate** (`core/lichidare.py`), care conține exact acest calcul: funcția `partaj(capital_social, rezerve, profituri)` generează notele conform mecanismului de mai sus — `1012=456` pentru restituirea capitalului social (neimpozabilă), `1061=456`/`1171=456` pentru rezerve/profituri (câștig impozabil), `456=446` pentru impozitul de 10% calculat automat cu cota de lichidare valabilă la data operațiunii, și `456=5121` pentru plata netă către asociat.

Cota de impozit e citită dintr-un registru propriu de cote (nu e hardcodată în funcția de calcul), ceea ce înseamnă că aplicația aplică automat cota corectă valabilă la data lichidării, fără să ceară contabilului să o caute separat. Rămâne responsabilitatea contabilului să stabilească exact ce parte din sumă reprezintă restituire de aport (neimpozabilă) și ce parte reprezintă rezerve/profituri (impozabile) — distincția pe care o cere legea la introducerea sumelor în calculul de partaj.

[iConta.eu](/)
