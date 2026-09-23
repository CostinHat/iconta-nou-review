---
title: Ce faci dacă ai calculat greșit coeficientul K?
description: Ce se poate corecta și ce nu, în iConta.eu, după ce o notă de descărcare de gestiune cu un coeficient K greșit a fost deja validată.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce faci dacă ai calculat greșit coeficientul K?

Legea (OMFP 1802/2014, pct. 286-291) descrie cum se calculează corect coeficientul K și cum se aplică metoda prețului cu amănuntul — nu descrie și o procedură pentru corectarea unei descărcări de gestiune deja înregistrate greșit. Corectarea unei erori contabile deja înregistrate ține de practica contabilă generală (stornare și notă de corecție), nu de o normă dedicată a OMFP 1802/2014.

## Temeiul legal

::: ghid-temei
„Repartizarea diferențelor de preț asupra valorii bunurilor ieșite și asupra stocurilor se efectuează cu ajutorul unui coeficient care se calculează astfel: Coeficient de repartizare = [Soldul inițial al diferențelor de preț + Diferențe de preț aferente intrărilor în cursul perioadei, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] / [Soldul inițial al stocurilor la preț de înregistrare + Valoarea intrărilor în cursul perioadei la preț de înregistrare, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] x 100."
— OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), pct. 286 alin. (4)
:::

Acest text spune cum trebuie calculat coeficientul corect. Nu există, în același act normativ, un text care să descrie explicit procedura de corectare a unei descărcări de gestiune deja înregistrate greșit — de aceea răspunsul de mai jos se bazează pe mecanismul verificat din aplicație și pe practica contabilă generală de stornare, nu pe o normă OMFP 1802/2014 dedicată corecției.

## Ce se întâmplă tehnic, în aplicație

Verificarea codului sursă arată explicit că:

- O notă contabilă poate fi editată sau ștearsă **doar cât timp are statutul de ciornă**. Odată validată, aplicația refuză explicit orice editare sau ștergere a ei.
- Nu există o a treia stare a notei (de tip „stornată" sau „anulată") și nicio funcție dedicată de stornare sau corecție a notelor de descărcare de gestiune sau a coeficientului K în motorul de calcul al gestiunii global-valorice. Singurul mecanism de stornare găsit în cod privește facturile, un flux complet separat, fără legătură cu notele de descărcare de gestiune.

## Ce se greșește în practică

- Se încearcă editarea directă a notei de descărcare deja validate, în speranța că aplicația permite o corecție rapidă — nu permite, indiferent de motiv.
- Se lasă nota greșită necorectată, sperând că luna următoare „compensează" automat eroarea — parțial adevărat, dar nu suficient: coeficientul K se calculează cumulat de la 1 ianuarie, deci o corecție a soldurilor prin notă manuală se va reflecta automat în K-ul lunilor următoare, însă **luna deja descărcată greșit rămâne cu nota ei greșită în jurnal** până când cineva o stornează explicit.

## Ce face iConta.eu

Pentru că nu există o funcție automată de „recalculează K" sau „corectează adaosul", corectarea unei descărcări greșite se face prin mecanismul disponibil deja în aplicație pentru corecții contabile generale: o notă manuală de stornare a notei greșite, urmată de o notă corectă, introduse de contabil prin ecranul de jurnal. Odată ce soldurile conturilor 371, 378 și 4428 sunt corectate prin această notă manuală, coeficientul K calculat pentru lunile următoare va porni automat de la soldurile corecte, pentru că formula folosește mereu rulajele reale, cumulate, ale conturilor — nu o valoare stocată separat.

[iConta.eu](/)
