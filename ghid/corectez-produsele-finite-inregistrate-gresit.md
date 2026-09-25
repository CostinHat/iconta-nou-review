---
title: "Cum corectez produsele finite înregistrate greșit?"
description: "Ce se poate corecta direct și ce necesită notă de stornare la notele de producție și produse finite generate conform OMFP 1802/2014, în funcție de statusul lor: ciornă sau validată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez produsele finite înregistrate greșit?

Contabilitatea în partidă dublă nu permite ștergerea liberă a unei note validate — orice corecție ulterioară se face prin stornare, nu prin rescriere. Ce contează, practic, e statusul notei greșite: cât timp e ciornă, se poate edita sau șterge direct; odată validată, singura cale corectă e o notă manuală de corecție.

## Temeiul legal

::: ghid-temei
„Persoanele prevazute la art. 1 alin. (1)-(4) au obligatia sa conduca contabilitatea in partida dubla si sa intocmeasca situatii financiare anuale, potrivit reglementarilor contabile aplicabile."
— Legea contabilității 82/1991, art. 5 alin. (1) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Obligația de partidă dublă e temeiul pentru care o notă contabilă validată nu se poate pur și simplu șterge sau rescrie: fiecare înregistrare trebuie să rămână trasabilă, iar corectarea unei erori constatate ulterior se face printr-o **notă de stornare/corecție**, nu prin modificarea silențioasă a istoricului contabil. Pentru notele de producție/produse finite — obținere (345=711), producție în curs (331/711) și vânzare cu descărcare (711=345, eventual cu 348) — regulile OMFP 1802/2014 pentru conturile 331/345/348/711 (deja detaliate în ghidul dedicat notelor de producție) rămân valabile și după corectare: se aplică din nou, corect, în nota de stornare.

## Ce se greșește în practică

- Se încearcă modificarea directă a unei note deja validate, ca și cum ar fi încă o ciornă — practica trebuie să fie: se stornează nota greșită, apoi se introduce nota corectă.
- Se corectează doar cantitatea sau costul din nota greșită, fără să se recalculeze și diferențele de preț (348) sau producția în curs afectată de acea intrare/ieșire — o corecție parțială poate lăsa contul 348 sau soldul de producție în curs dezechilibrat.
- Se presupune că orice eroare de introducere (cost standard greșit, sumă greșită la producția în curs) se poate „repara" retroactiv fără urmă în contabilitate, ceea ce contravine principiului de trasabilitate al partidei duble.

## Ce face iConta.eu

Notele generate de funcționalitatea **Producție în curs și produse finite** (`core/productie.py`, prin ecranul Operațiuni speciale → Imobilizări) intră în contabilitate ca **note ciornă** (`facturi_ciorna` + linii), exact ca orice altă notă din aplicație — nu se validează automat.

Cât timp nota e încă **ciornă**, poate fi editată sau ștearsă direct, prin mecanismul general de jurnal al aplicației (`core/jurnal_api.py`, funcțiile `editeaza`/`sterge`), care operează generic pe orice notă din tabela de înregistrări, indiferent de funcționalitatea care a creat-o — inclusiv notele de producție. Aceste funcții **refuză explicit** orice notă care nu mai are statusul `ciorna` (mesajul din aplicație: „doar ciornele se pot edita" / „doar ciornele se pot șterge").

**Odată ce nota a fost validată, iConta.eu nu are o funcție dedicată de corecție** pentru notele de producție/produse finite — nu există un buton „corectează" sau „anulează" specific acestei funcționalități. Corectarea unei note validate greșit se face, ca în restul aplicației, printr-o **notă manuală de stornare/corecție**, introdusă de contabil în ecranul general de jurnal, nu printr-un mecanism automat al F069. Recomandarea practică: verificați cu atenție costul standard și cantitatea înainte de validare — după acel punct, corecția cere o intervenție manuală explicită.

[iConta.eu](/)
