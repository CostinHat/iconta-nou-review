---
title: "Cum se fac plăți inter-firme peste plafonul de numerar"
description: "Regulile Legii 70/2015 privind plafoanele de plată în numerar între firme și ce se întâmplă cu sumele care le depășesc."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se fac plăți inter-firme peste plafonul de numerar

Regula generală în România este că plățile între firme se fac prin instrumente de plată fără numerar (transfer bancar, card etc.). Legea permite totuși plăți în numerar, dar numai în limita unor plafoane zilnice stricte — orice sumă care le depășește trebuie achitată obligatoriu prin mijloace fără numerar, nu poate fi „completată" tot cash.

## Temeiul legal

::: ghid-temei
„(1) Operațiunile de încasări și plăți efectuate de persoane juridice, persoane fizice autorizate, întreprinderi individuale, întreprinderi familiale, liber profesioniști, persoane fizice care desfășoară activități în mod independent, asocieri și alte entități cu sau fără personalitate juridică de la/către oricare dintre aceste categorii de persoane se vor realiza numai prin instrumente de plată fără numerar, definite potrivit legii."
— Legea 70/2015, art. 1 alin. (1) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

::: ghid-temei
„Prin excepție de la prevederile art. 1 alin. (1) se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: [...] c) plăți către persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei/persoană, dar nu mai mult de un plafon total de 10.000 lei/zi [...]."
— Legea 70/2015, art. 3 alin. (1) lit. c) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

- Regula (art. 1) este că plățile între firme trebuie făcute prin instrumente fără numerar; plata cash e doar o excepție permisă în limite stricte.
- Plafonul pentru plăți în numerar către un singur partener (persoană juridică/PFA/ÎI etc.) este de 5.000 lei/zi, dar nu se pot depăși, oricum, 10.000 lei/zi în total plăți cash, indiferent câți parteneri diferiți sunt plătiți.
- Fragmentarea unei facturi mai mari de 5.000 lei în mai multe tranșe cash, pentru a „încăpea" sub plafon, este expres interzisă — atât fragmentarea plăților, cât și fragmentarea facturilor pentru aceeași livrare/prestare (art. 3 alin. (2)-(3)).
- Suma care depășește plafonul legal poate fi achitată **numai** prin instrument de plată fără numerar — de exemplu, dintr-o factură de 15.000 lei, maximum 5.000 lei se pot plăti cash, restul de 10.000 lei obligatoriu prin transfer bancar sau alt instrument fără numerar.
- Nerespectarea plafoanelor este contravenție, sancționată cu amendă de 10% din suma care depășește plafonul, dar nu mai puțin de 100 lei, pentru fiecare tip de operațiune.

## Ce se greșește în practică

- Se plătește integral cash o factură mare, considerând că plafonul de 10.000 lei/zi se aplică per factură, nu per partener și per zi — de fapt plafonul din numerar către un singur partener este de 5.000 lei/zi.
- Se fracționează plata unei facturi mari în mai multe zile consecutive, tot cash, pentru a „evita" plafonul — legea sancționează exact această practică de plată/încasare fragmentată.
- Se confundă plafonul pentru plăți către alte firme (5.000 lei/zi/partener, maximum 10.000 lei/zi total) cu plafonul pentru operațiunile cu magazinele de tip cash and carry (10.000 lei/zi) sau cu cel pentru avansuri spre decontare (5.000 lei/zi/persoană) — sunt plafoane distincte, reglementate separat.

## Ce face iConta.eu

iConta.eu are o funcție dedicată verificării plafoanelor de numerar: modulul de casierie (`casa.py`) implementează constantele legale din Legea 70/2015 (plafonul de 5.000 lei pentru încasări/plăți către o persoană juridică, plafonul total de 10.000 lei/zi, plafonul de 10.000 lei pentru cash and carry, plafonul de 5.000 lei pentru avansuri spre decontare) și funcția `verifica_plafon`, care semnalează depășirile ca avertisment la fiecare operațiune de casă — util pentru a preveni exact situațiile de mai sus înainte ca acestea să ajungă subiect de control.

[iConta.eu](/)
