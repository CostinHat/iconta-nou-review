---
title: "Cum se raportează diferențele de inventar în D406?"
description: "De ce SAF-T (D406) nu tratează diferențele de inventariere ca o categorie separată, ci le absoarbe în soldurile de stoc raportate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se raportează diferențele de inventar în D406?

Răspunsul scurt, care corectează premisa întrebării: D406 **nu are** un câmp sau o secțiune dedicată „diferențe de inventar". Plusurile și minusurile constatate la inventariere intră în același flux ca orice altă mișcare de stoc și se pierd, ca eveniment identificabil, în soldurile cumulate raportate.

## Temeiul legal

::: ghid-temei
„PhysicalStock (Stocuri) — Conţine detalii cu privire la stocuri, precum ID-ul depozitului unde se găsesc bunurile, codul de identificare al produsului, detalii despre proprietarul stocurilor, codul de încadrare tarifară (codul NC), detalii privind cantitatea la început şi la final de perioadă de raportare, valoarea stocului la început şi la final de perioadă de raportare etc."
— OPANAF 1783/2021 (SAF-T D406), Anexa 1, descrierea secțiunii PhysicalStock (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Ce înseamnă practic:

- Diferențele constatate la o inventariere fizică (plus sau minus față de scriptic) se înregistrează contabil ca note pe conturile de stoc (de exemplu 371=607 la plus, 607=371 la minus) — exact ca orice altă intrare sau ieșire de stoc.
- SAF-T cumulează **toate** mișcările de stoc (intrări, ieșiri, indiferent de document) în soldurile de deschidere și închidere ale perioadei — nu izolează sau etichetează separat mișcările provenite dintr-o inventariere.
- Consecință: în D406, o diferență de inventar nu apare ca „linie de inventar" — ea dispare în soldul cumulat, alături de vânzări, achiziții și alte mișcări normale de stoc. Urma diferenței de inventar rămâne vizibilă doar în registrul-jurnal/balanța contabilă (pe contul de cheltuială/venit lovit de nota generată), nu ca rând distinct în structura SAF-T.

## Ce se greșește în practică

- Se caută în structura D406 un câmp sau o secțiune „inventar" — nu există; diferențele de inventar nu sunt o categorie separată în SAF-T.
- Se presupune că ANAF poate identifica automat, din D406, ce parte din variația de stoc a venit dintr-o inventariere — informația respectivă rămâne doar în contabilitatea internă a firmei (jurnal, note contabile), nu în fișierul SAF-T.
- Se omite completarea Registrului-inventar (cod 14-1-2), obligatoriu separat de orice raportare SAF-T, considerând că D406 acoperă și această obligație — nu o acoperă.

## Ce face iConta.eu

Aplicația are un mod de captură rapidă a inventarului faptic direct de pe telefonul mobil (scanare de cod de bare sau căutare după denumire, cu acumulare a cantităților numărate pe ecran și numărare „oarbă" — fără afișarea scripticului, ca să nu influențeze numărătorul). La finalizare, aplicația calculează automat diferența față de scriptic (citit live din fișa de magazie) și generează o notă contabilă pe articolele cu diferență, exact ca mecanismul descris mai sus — deci diferențele produse astfel intră, la fel ca oricare altă mișcare de stoc, în soldurile pe care le calculează secțiunea de stocuri a D406, fără o etichetă separată de „inventar" în fișierul SAF-T generat.

O limitare reală a acestui mod de inventariere pe mobil: dacă mai mulți angajați numără simultan, pe telefoane separate, aceeași gestiune, aplicația nu are azi un mecanism de coordonare între ei — fiecare numărătoare trăiește doar în memoria browserului până la finalizare, iar scripticul folosit la calculul diferenței se citește live, în momentul postării. Rezultatul poate depinde de ordinea în care fiecare finalizează, exact riscul pe care procedura legală de inventariere (comisie, zonă tampon, coordonare) e gândită să-l prevină. Pentru o firmă cu un singur numărător, care e cazul obișnuit, funcționalitatea calculează corect diferența și nota contabilă aferentă.

[iConta.eu](/)
