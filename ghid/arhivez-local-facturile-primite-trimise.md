---
title: Cum arhivez local facturile primite și trimise prin e-Factura?
description: XML-ul original al fiecărei facturi rămâne stocat în baza de date și accesibil oricând, dar aplicația nu are, la acest moment, o funcție dedicată de export/arhivă locală în masă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum arhivez local facturile primite și trimise prin e-Factura?

Dacă te aștepți la un buton de „descarcă arhiva” cu toate XML-urile într-un ZIP, răspunsul onest e că nu există încă — dar asta nu înseamnă că XML-urile nu sunt păstrate.

## Temeiul legal

::: ghid-temei
„Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul naţional privind factura electronică RO e-Factura."

— OUG nr. 120/2021, art. 4 alin. (7)
:::

Exemplarul relevant din punct de vedere legal e XML-ul devenit disponibil în SPV — de aceea aplicația păstrează exact acest fișier, așa cum a fost descărcat, nu doar o interpretare a lui.

## Ce se păstrează, de fapt

Fiecare factură primită de la un furnizor prin SPV are XML-ul brut original păstrat integral, la nivel de bază de date, alături de o amprentă a conținutului (folosită doar ca informație, nu ca mecanism de control). După validare, XML-ul rămâne legat și de factura contabilizată propriu-zisă. Accesul se face individual, din ecranul fiecărei facturi — nu e afișat implicit pe listă, ci disponibil la cerere.

Ce nu există, verificat direct: un modul separat de arhivare sau o rută dedicată de export al mai multor XML-uri deodată (de exemplu într-o arhivă ZIP descărcabilă local, pe o perioadă aleasă). Persistența e cea din baza de date a aplicației, nu un mecanism de backup extern distinct.

## Ce se greșește în practică

- Se caută o funcție de „export arhivă” pe o perioadă, presupunând că există undeva în meniu — la acest moment, nu există o astfel de funcție dedicată.
- Se crede că, fără o arhivă locală explicită descărcată manual, XML-urile s-ar putea pierde — de fapt ele rămân stocate în aplicație atât timp cât facturile există, indiferent dacă au fost sau nu descărcate separat de contabil.
- Se confundă „arhivarea” cu simpla vizualizare a XML-ului — accesul la XML individual există deja, doar funcția de export în masă lipsește.

## Ce face iConta.eu

Fiecare XML — primit sau trimis prin RO e-Factura — rămâne stocat integral și accesibil oricând, factură cu factură, din ecranul respectiv. Nu există, la data acestei redactări, o funcție dedicată de arhivare/export local în masă a acestor XML-uri. Dacă ai nevoie de o copie locală organizată pentru o perioadă întreagă, singura variantă actuală e descărcarea individuală, factură cu factură.

[iConta.eu](/)
