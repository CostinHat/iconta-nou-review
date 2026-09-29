---
title: "Se confiscă marfa nedeclarată în RO e-Transport dacă e înregistrată în contabilitate la timp?"
description: "Nu, dacă nedeclararea e constatată la o verificare ulterioară încheierii transportului, iar operațiunea e înregistrată la timp în documente și în contabilitate. Amenda rămâne."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Se confiscă marfa nedeclarată în RO e-Transport dacă e înregistrată în contabilitate la timp?

Nu se aplică confiscarea, dacă sunt îndeplinite simultan condițiile legii: fapta este nedeclararea transportului, este constatată la o verificare ulterioară încheierii transportului, iar operațiunea a fost înregistrată în documentele justificative și în contabilitate, în perioada la care se referă. Amenda pentru nedeclarare rămâne însă aplicabilă.

Pentru cabinet, regula are o consecință directă: o contabilitate ținută la zi, cu facturi, avize și NIR-uri înregistrate în luna operațiunii, este chiar condiția care scutește clientul de confiscare la un control ulterior. O înregistrare întârziată sau lipsa documentelor pierde această protecție.

## Temeiul legal

::: ghid-temei
„(2^1) Prin excepție de la prevederile alin. (2) , pentru contravenția prevăzută la alin. (1) lit. a) , în ceea ce privește nerespectarea prevederilor art. 9 alin. (2) și (3) , sancțiunea complementară a confiscării nu se aplică în cazul constatărilor rezultate din verificări ulterioare încheierii transportului rutier de bunuri, când acestea au fost înregistrate în documentele justificative care stau la baza înregistrărilor contabile, precum și în contabilitatea utilizatorilor, după caz, în perioada la care se referă operațiunile respective."
— OUG 41/2022, art. 13^1 alin. (2^1) (sursă: anaf_surse/oug_41_2022.txt)

„(2) Contravențiile prevăzute la alin. (1) lit. a) și b) se sancționează cu amendă de la 10.000 de lei la 50.000 de lei în cazul persoanelor fizice sau cu amendă de la 20.000 de lei la 100.000 de lei în cazul persoanelor juridice, precum și confiscarea contravalorii bunurilor nedeclarate."
— OUG 41/2022, art. 13^1 alin. (2) (sursă: anaf_surse/oug_41_2022.txt)
:::

Condițiile, toate obligatorii:

- **Fapta e nedeclararea** transportului de bunuri cu risc fiscal ridicat (art. 9 alin. (2)) sau a transportului internațional (art. 9 alin. (3)). Excepția nu acoperă codul UIT expirat, descărcarea interzisă în tranzit (tot din lit. a), dar pe art. 11) și nici declararea unor cantități diferite (lit. b)).
- **Constatarea e ulterioară**, adică dintr-o verificare făcută după încheierea transportului. La un control în trafic, în timpul transportului, excepția nu se aplică.
- **Operațiunea e înregistrată** în documentele justificative și în contabilitatea utilizatorului.
- **Înregistrarea e la timp**, „în perioada la care se referă operațiunile respective", nu după începerea controlului.

Chiar și cu excepția aplicată, amenda rămâne: de la 20.000 la 100.000 lei pentru persoane juridice (10.000–50.000 lei pentru persoane fizice), fără posibilitatea plății a jumătate din minim în 15 zile (Legea 296/2023, art. LVIII).

::: ghid-exemplu
La o inspecție fiscală din iunie, ANAF constată că SC Exemplu SRL a livrat în martie, pe teritoriul național, bunuri cu risc fiscal ridicat în valoare de 80.000 lei fără cod UIT. Factura și avizul sunt din martie și sunt înregistrate în contabilitatea lunii martie. Se aplică amenda (minimum 20.000 lei), dar nu și confiscarea celor 80.000 lei. Dacă factura ar fi fost înregistrată abia în iunie, după începerea inspecției, excepția nu s-ar mai aplica.
:::

## Ce se greșește în practică

- Se crede că înregistrarea în contabilitate scutește și de amendă; scutește doar de confiscare.
- Se invocă excepția la un control în trafic; ea privește doar verificările ulterioare încheierii transportului.
- Se înregistrează documentele „recuperate" după anunțarea controlului; legea cere înregistrarea în perioada operațiunii.
- Se aplică excepția și la declararea unor cantități diferite; textul o limitează la nedeclararea din art. 9 alin. (2) și (3).

## Ce face iConta.eu

iConta.eu ține contabilitatea generală a firmei-client, în care facturile și notele contabile se înregistrează pe perioada operațiunii; ținerea ei la zi e în sarcina contabilului. Separat, cardul e-Transport generează XML-ul notificării în structura oficială v2. Aplicația nu corelează automat facturile cu codurile UIT; verificarea că fiecare transport monitorizat are cod UIT rămâne a contabilului.

[iConta.eu](/)
