---
title: "Cum se întocmește NIR pentru o achiziție intracomunitară?"
description: "Cum se completează NIR-ul cu landed cost pentru o achiziție intracomunitară de bunuri și de ce nota de TVA generată automat trebuie corectată manual la taxare inversă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se întocmește NIR pentru o achiziție intracomunitară?

Un NIR pentru marfă cumpărată dintr-un stat membru UE se completează, tehnic, la fel ca oricare alt NIR: cantitate, preț de achiziție, plus eventualele cheltuieli accesorii (transport, taxe) de repartizat proporțional în costul mărfii. Diferența reală față de o achiziție internă nu e la nivelul costului, ci la nivelul TVA — o achiziție intracomunitară de bunuri se taxează invers, nu prin deducerea TVA-ului unei facturi de furnizor intern.

## Temeiul legal

::: ghid-temei
„6. cost de achiziție înseamnă prețul datorat şi eventualele cheltuieli conexe minus eventualele reduceri ale costului de achiziție. În acest sens, costul de achiziție al bunurilor cuprinde prețul de cumpărare, taxele de import şi alte taxe (cu excepția acelora pe care persoana juridică le poate recupera de la autoritățile fiscale), cheltuielile de transport, manipulare şi alte cheltuieli care pot fi atribuibile direct achiziției bunurilor respective. [...] Cheltuielile de transport sunt incluse în costul de achiziție şi atunci când funcția de aprovizionare este externalizată."
— OMFP 1802/2014, Reglementările contabile, Secțiunea 1.2 pct. 6 (sursă: anaf_surse/omfp_1802_2014.txt)
:::

Definiția costului de achiziție e generică — nu distinge intern, intracomunitar sau import — deci transportul unei achiziții IC intră în costul mărfii exact ca la o achiziție internă. Ce diferă e tratamentul TVA:

- O achiziție intracomunitară de bunuri se declară prin **taxare inversă**: `4426=4427`, fiindcă furnizorul din UE nu facturează TVA românesc.
- Repartizarea transportului pe articolele NIR-ului se face **proporțional cu costul de bază** al fiecărei linii, cu restul de rotunjire pe ultima linie, astfel încât suma repartizată să fie exact egală cu accesoriul introdus.
- **Valoarea capitalizată e netă de TVA** — TVA-ul aferent transportului (deductibil) și eventualele taxe vamale (tratate diferit, de regulă la import extracomunitar, nu la achiziția IC) se gestionează separat de capitalizarea costului.

## Ce se greșește în practică

- Se introduce achiziția IC direct în ecranul de NIR, cu transportul ca accesoriu, fără să se verifice ce notă de TVA generează automat aplicația — riscul e o notă de TVA de tip „deducere de la furnizor intern", incorectă pentru o achiziție IC.
- Se dublează TVA-ul: se lasă nota de taxare inversă generată separat pentru achiziția IC, ȘI se lasă și nota de TVA implicită a NIR-ului, care presupune deducere directă — rezultatul e un TVA deductibil înregistrat de două ori pentru aceeași marfă.
- Se omite repartizarea transportului pe articole atunci când o singură factură de transport acoperă mai multe SKU-uri cumpărate simultan din UE, lăsând costul de achiziție subevaluat pe fiecare linie.

## Ce face iConta.eu

Ecranul NIR cu **landed cost** (card Stocuri → NIR, motor `core/stocuri.py::nir_gv`) acceptă transportul și taxele ca parametri și le repartizează proporțional cu costul de bază pe fiecare linie, cu restul de rotunjire pe ultima linie — mecanismul e generic pe originea mărfii, deci funcționează identic pentru o achiziție IC. Testele aplicației confirmă repartizarea exactă (de exemplu 10 lei transport pe 3 linii egale → 3.33 + 3.33 + 3.34, sumă exact 10.00) și blocarea explicită a vânzării sub costul de achiziție cu accesoriu inclus.

**Limită de disponibilitate**: `nir_gv` e motorul gestiunii **global-valorice** (prețul cu amănuntul, cu adaos comercial și TVA neexigibilă) — cere pentru fiecare linie și prețul de vânzare cu TVA, nu doar costul de achiziție. Pentru firmele care țin gestiunea **cantitativ-valorică** (pe fișă de magazie, CMP), mecanismul de landed cost din acest ecran nu e disponibil; transportul trebuie adăugat manual la prețul unitar înainte de introducerea intrării.

**Limită reală, de cunoscut înainte de a folosi acest ecran pentru o achiziție IC**: nota de TVA generată automat de `nir_gv` e `4426=401` — adică TVA dedusă ca de la un furnizor intern care a facturat TVA. Pentru o achiziție intracomunitară de bunuri, acest tratament e **greșit**: furnizorul din UE nu facturează TVA românesc, iar tratamentul corect e taxarea inversă (`4426=4427`), disponibilă în aplicație printr-o funcționalitate separată, pentru operațiuni intracomunitare (achiziția IC ca sumă globală, legată de o singură factură). Motorul NIR-ului **nu are niciun parametru de „taxare inversă"** — cele două mecanisme nu sunt integrate.

Recomandarea practică, confirmată de comportamentul verificat al aplicației: dacă folosiți ecranul NIR pentru a capitaliza transportul pe articolele unei achiziții IC, tratați separat TVA-ul — fie introduceți NIR-ul fără TVA suplimentară pe marfă (doar capitalizarea costului), fie corectați manual nota de TVA generată automat, pentru a nu dubla deducerea alături de nota de taxare inversă introdusă separat.

[iConta.eu](/)
