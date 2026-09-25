---
title: "Cum se aplică plafonul cash pentru un punct de lucru cu casierie proprie?"
description: "Ce spune Legea 70/2015 despre plafoanele zilnice de încasări și plăți în numerar și la ce nivel se calculează — la firmă, nu la punct de lucru."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se aplică plafonul cash pentru un punct de lucru cu casierie proprie?

O firmă cu mai multe puncte de lucru, fiecare cu casă de marcat sau casierie proprie, se întreabă frecvent dacă plafonul zilnic de numerar se aplică separat, pe fiecare punct de lucru, sau global, la nivel de firmă. Legea 70/2015 nu menționează „punctul de lucru" ca unitate de calcul al plafonului — plafonul e legat de persoană, nu de locație.

## Temeiul legal

::: ghid-temei
„Articolul 1 (1) Operațiunile de încasări și plăți efectuate de persoane juridice, persoane fizice autorizate, întreprinderi individuale, întreprinderi familiale, liber profesioniști, persoane fizice care desfășoară activități în mod independent, asocieri și alte entități cu sau fără personalitate juridică de la/către oricare dintre aceste categorii de persoane se vor realiza numai prin instrumente de plată fără numerar, definite potrivit legii.
Articolul 3 (1) [...] a) încasări de la persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei de la o persoană; [...] c) plăți către persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei/persoană, dar nu mai mult de un plafon total de 10.000 lei/zi."
— Legea 70/2015, art. 1 alin. (1) și art. 3 alin. (1) lit. a) și c) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Ce rezultă din text:

- Plafonul zilnic (5.000 lei/persoană pentru încasări, respectiv 5.000 lei/persoană pentru plăți, cu plafon total de 10.000 lei/zi la plăți) se calculează **pe relația dintre două entități** dintre cele prevăzute la art. 1 alin. (1), nu pe locație fizică — legea nu face o distincție de plafon după cum partenerul e persoană fizică sau juridică, ci după tipul operațiunii (încasare/plată, respectiv magazin cash and carry sau nu). Legea nu menționează nicăieri „punct de lucru" ca unitate separată de calcul.
- Dacă o firmă are mai multe puncte de lucru, fiecare cu casă de marcat proprie, dar toate încasările/plățile de la aceeași persoană (client/furnizor) în aceeași zi se cumulează — plafonul e la nivelul persoanei juridice care încasează sau plătește, nu la nivelul fiecărei case de marcat.
- Art. 3 alin. (2)-(3) interzic explicit **fragmentarea** încasărilor sau facturilor pentru a evita plafonul — o practică des întâlnită tocmai în firmele cu mai multe puncte de lucru, care încearcă să „împartă" o încasare mare pe mai multe case de marcat.

## Ce se greșește în practică

- Se calculează plafonul separat, pe fiecare punct de lucru/casă de marcat, presupunând că fiecare are propriul plafon zilnic — legea nu susține această interpretare, plafonul fiind legat de relația dintre persoane, nu de locație.
- Se încasează aceeași factură mare fragmentat, la case de marcat diferite ale aceleiași firme, pentru a rămâne sub plafon — interzis explicit ca „încasare fragmentată" (art. 3 alin. (2)).
- Se ignoră faptul că plafonul pentru magazinele de tip cash and carry e diferit (10.000 lei/zi de la o persoană), aplicând din eroare plafonul general de 5.000 lei.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **aplică plafoanele de numerar din Legea 70/2015 (actualizată prin Legea 239/2025, în vigoare din 01.01.2026)** direct în modulul de casierie (`core/casa.py`), cu constante distincte pentru partenerii de tip persoană juridică (5.000 lei/încasare, 5.000 lei/plată cu plafon total de 10.000 lei/zi) și, separat, pentru partenerii marcați ca persoană fizică (constanta `PLAFON_PF`, 10.000 lei) — o distincție de organizare internă a aplicației, nu una explicit textuală în art. 1 sau art. 3 din lege, care condiționează plafoanele de tipul operațiunii, nu de calitatea partenerului. Aplicația **nu segmentează plafonul pe puncte de lucru** — calculul urmează structura legii, la nivelul relației cu partenerul, nu al locației fizice.

[iConta.eu](/)
