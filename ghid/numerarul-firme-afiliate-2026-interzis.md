---
title: "Numerarul între firme afiliate 2026: ce este interzis"
description: "Regimul plăților și încasărilor în numerar între persoane juridice, aplicabil și firmelor afiliate, conform Legii 70/2015."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Numerarul între firme afiliate 2026: ce este interzis

Legea disciplinei financiare nu prevede un regim special, mai strict, pentru operațiunile în numerar dintre firme afiliate (aceiași asociați, grup de firme etc.) — le tratează exact ca pe orice altă operațiune între persoane juridice. De aceea, orice discuție despre „ce e interzis între firme afiliate" trebuie să pornească de la regula generală, nu de la o excepție care nu există în lege.

## Temeiul legal

::: ghid-temei
„ART. 1 (1) Operațiunile de încasări și plăți efectuate de persoane juridice, persoane fizice autorizate, întreprinderi individuale, întreprinderi familiale, liber profesioniști, persoane fizice care desfășoară activități în mod independent, asocieri și alte entități cu sau fără personalitate juridică de la/către oricare dintre aceste categorii de persoane se vor realiza numai prin instrumente de plată fără numerar, definite potrivit legii."
— Legea 70/2015 pentru întărirea disciplinei financiare privind operațiunile de încasări și plăți în numerar, art. 1 alin. (1) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Precizare importantă: am căutat explicit în Legea 70/2015 o prevedere specială pentru „firme afiliate" și nu există una — legea nu are un articol separat, mai restrictiv, pentru tranzacțiile dintre societăți controlate de aceiași asociați. Se aplică deci **regimul general**, exact ca între oricare două firme:

- Regula de bază este plata fără numerar. Numerarul este permis doar ca **excepție**, în limitele stabilite la art. 3-4.
- Încasările de la o altă persoană juridică sunt limitate la **5.000 lei/zi/persoană**; plățile către o altă persoană juridică, la **5.000 lei/zi/persoană, dar nu mai mult de 10.000 lei/zi în total**.
- Fragmentarea unei facturi sau a unei plăți pentru a evita aceste plafoane este expres interzisă (art. 3 alin. (2) și (3)).
- Nerespectarea plafoanelor se sancționează cu amendă de 10% din suma care depășește plafonul, dar nu mai puțin de 100 lei (art. 12 alin. (1)) — sancțiunea se aplică identic, indiferent dacă firmele sunt afiliate sau nu.

## Ce se greșește în practică

- Se presupune că între firme afiliate există o interdicție totală a numerarului sau, dimpotrivă, o îngăduință mai mare — niciuna dintre premise nu are temei în Legea 70/2015, care nu diferențiază după afiliere.
- Se folosesc plăți fragmentate „pe zile" între firme din același grup, tocmai pentru a evita plafonul de 5.000/10.000 lei — practică expres interzisă indiferent de relația dintre părți.
- Se confundă regulile pentru operațiuni cu persoane juridice (art. 3) cu cele pentru operațiuni cu persoane fizice (art. 4, plafon 10.000 lei/zi) sau cu regula generală dintre persoane fizice (art. 10, plafon 50.000 lei/tranzacție) — plafoane diferite, aplicabile unor categorii de parteneri diferite.

## Ce face iConta.eu

Am verificat în `core/casa.py`: aplicația **validează automat plafoanele din Legea 70/2015** (funcția `verifica_plafon`, cu constantele `PLAFON_INCASARE_PJ` și `PLAFON_PLATA_PJ`, ambele setate la 5.000 lei pentru operațiunile cu persoane juridice, respectiv 10.000 lei/zi cumulat la plăți) și semnalează un avertisment când o operațiune de casierie depășește pragul legal, indiferent dacă partenerul este sau nu o firmă afiliată — regula fiind, oricum, aceeași pentru toate persoanele juridice. Aplicația nu are o categorie separată „firmă afiliată" pentru că legea însăși nu face această distincție.

[iConta.eu](/)
