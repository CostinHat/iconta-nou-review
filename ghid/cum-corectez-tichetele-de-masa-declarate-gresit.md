---
title: Cum corectez tichetele de masă declarate greșit?
description: Corectarea unui număr greșit de tichete de masă se face diferit înainte și după depunerea declarației — înainte de depunere se reconfirmă pontajul și se recalculează, iar după depunere corecția se face exclusiv prin D112 rectificativă.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum corectez tichetele de masă declarate greșit?

O eroare la numărul sau valoarea tichetelor de masă dintr-o lună se corectează diferit în funcție de un singur criteriu: declarația D112 a fost deja depusă la ANAF sau nu.

## Temeiul legal

::: ghid-temei
HG nr. 1045/2018, Articolul 10 alin. (3), care stabilește baza corectă de calcul a tichetelor:

> „(3) Salariații beneficiază lunar de un număr de tichete de masă cel mult egal cu numărul de zile lucrate, iar acest număr nu poate depăși numărul de zile lucrătoare din luna pentru care se acordă tichetele."

Articolul 17 alin. (5), aplicabil când corecția presupune și un excedent necuvenit:

> „(5) În cazul tichetelor de masă, în situația în care salariatul utilizează într-o lună un număr de tichete de masă mai mare decât numărul de zile lucrate, stabilite potrivit art. 10, iar angajatorul nu a încasat de la salariat contravaloarea tichetelor utilizate și necuvenite, angajatorul acordă acestuia pentru luna următoare un număr de tichete de masă egal cu numărul de zile lucrătoare, diminuat cu numărul de tichete acordate pentru luna anterioară și necuvenite."
:::

## Înainte sau după depunerea D112 — criteriul care contează

Câtă vreme o lună nu a fost încă declarată la ANAF, corecția se face direct la sursă: se reconfirmă/deconfirmă pontajul, se corectează zilele lucrate sau valoarea configurată, apoi se recalculează statul de plată. După ce declarația D112 a fost depusă pentru luna respectivă, datele sunt considerate „fapt declarat" — nu se mai modifică retroactiv în stat de plată, iar corecția reală se face exclusiv prin depunerea unei D112 rectificative pentru acea lună.

## Ce se greșește în practică

- Se modifică retroactiv pontajul sau valoarea tichetului pentru o lună deja declarată, fără a depune o rectificativă — ceea ce lasă declarația la ANAF nealiniată cu evidența internă.
- Se așteaptă ca aplicația să „țină minte" valoarea tichetului dintr-o lună trecută, deși valoarea configurată pe salariat este una singură, curentă, fără istoric — orice schimbare afectează doar lunile calculate de acum înainte.
- Se ignoră excedentul de tichete acordate necuvenit, în loc să se aplice fie diminuarea lunii următoare (art. 17 alin. 5), fie o rectificativă, după caz.
- Se recorectează un pontaj deja confirmat fără a-l deconfirma întâi, ceea ce poate lăsa statul de plată nealiniat cu datele reale.

## Ce face iConta.eu

Modificarea datelor confirmate (fapt deja declarat la ANAF) este blocată în aplicație — corectarea se face prin declarație rectificativă, nu prin suprascrierea directă a datelor deja depuse. Pentru o lună nedeclarată încă, cu pontajul neconfirmat, corecția se face prin deconfirmarea perioadei, corectarea pontajului și recalcul. Valoarea tichetului de masă configurată per salariat (`tichet_masa_valoare`) este o singură valoare curentă, fără istoric de versiuni — spre deosebire de salariul brut, care are propriul istoric — deci o corecție a acestei valori afectează doar lunile calculate după modificare, nu retroactiv lunile deja procesate.

[iConta.eu](/)
