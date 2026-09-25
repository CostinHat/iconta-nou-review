---
title: "Norme de consum în bucătărie: cum se aprobă"
description: "Cine stabilește norma de consum proprie pentru pierderile tehnologice la prepararea produselor și ce document o susține fiscal, potrivit Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Norme de consum în bucătărie: cum se aprobă

Pentru firmele din alimentație publică (restaurante, cofetării, cantine), o parte din materiile prime se pierde inevitabil în procesul de preparare — curățare de legume, evaporare la gătit, tăiere de carne. Fiscal, aceste pierderi sunt deductibile doar dacă se încadrează într-o normă de consum proprie, documentată — nu sunt deductibile „la liber", pe simpla afirmație că au existat pierderi.

## Temeiul legal

::: ghid-temei
„Următoarele cheltuieli au deductibilitate limitată: [...] pierderile tehnologice care sunt cuprinse în norma de consum proprie necesară pentru fabricarea unui produs sau prestarea unui serviciu."
— Legea 227/2015, art. 25 alin. (3) lit. e) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă practic „normă de consum proprie":

- **Norma de consum e stabilită de firmă însăși**, nu de o autoritate externă — legea nu impune o procedură de aprobare de la ANAF sau de la un alt organism, ci cere ca pierderea tehnologică să fie „cuprinsă în norma de consum proprie", deci documentată intern, consecvent aplicată și fundamentată tehnic (de exemplu, prin rețetare, fișe tehnologice de preparare, teste de gramaj).
- **Documentul intern** care stabilește norma (decizie a administratorului, fișă tehnologică aprobată, rețetar standardizat) trebuie păstrat ca justificare — la un control, ANAF verifică dacă pierderea înregistrată efectiv se încadrează rezonabil în norma declarată de firmă, nu dacă norma a fost „autorizată" cumva extern.
- **Fișele tehnologice de preparare** (cantitate de materie primă la intrare, cantitate de produs finit rezultat, pierdere procentuală) sunt documentul practic prin care se susține atât norma de consum, cât și descărcarea de gestiune a materiilor prime folosite.
- Pierderea care depășește norma proprie stabilită devine, pentru partea excedentară, o cheltuială care trebuie justificată suplimentar (de exemplu, ca lipsă în gestiune, cu procedura de inventariere aferentă) — nu se mai încadrează automat la deductibilitatea prevăzută pentru pierderile tehnologice normale.

## Ce se greșește în practică

- Se presupune că normele de consum trebuie „aprobate" printr-o procedură oficială la ANAF sau la o altă instituție — legea cere doar ca ele să existe, documentat, ca politică internă a firmei, nu o aprobare externă.
- Se înregistrează pierderi de gestiune la bucătărie fără nicio fișă tehnologică sau rețetar care să justifice procentul, ceea ce face imposibilă distincția, la un control, între o pierdere tehnologică normală și o lipsă nejustificată în gestiune.
- Se folosește aceeași normă de consum ani la rând, fără recalculare, deși rețetarul sau furnizorii de materii prime s-au schimbat, ceea ce poate duce la o normă nerealistă față de practica efectivă din bucătărie.

## Ce face iConta.eu

Modulul de stocuri din iConta.eu (`core/stocuri.py`, `core/obiecte_inventar.py`) ține evidența cantitativ-valorică a materiilor prime și produselor, cu note contabile pentru plusuri și minusuri de inventar. La data acestui ghid, aplicația **nu are un modul dedicat de fișe tehnologice sau rețetare** care să calculeze automat norma de consum proprie pentru prepararea produselor din bucătărie — stabilirea și documentarea normei de consum, precum și verificarea încadrării pierderilor efective în această normă, rămân un proces intern al firmei, în afara aplicației.

[iConta.eu](/)
