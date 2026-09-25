---
title: "Greșeli la credite: dobânzi tratate incorect"
description: "Cele mai frecvente greșeli de înregistrare a dobânzii la credite bancare — angajare vs. plată, termen lung vs. scurt, descoperit de cont — și limita fiscală de deductibilitate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Greșeli la credite: dobânzi tratate incorect

Dobânda la un credit bancar se înregistrează în două momente diferite — angajarea ei lunară, ca datorie, și plata ei efectivă — pe conturi diferite după cum creditul e pe termen lung sau scurt. Cea mai frecventă sursă de erori e amestecarea acestor doi pași, la care se adaugă un caz special, descoperitul de cont (overdraft), tratat diferit de restul creditelor și insuficient acoperit de norma contabilă.

## Temeiul legal

::: ghid-temei
„Cu ajutorul acestui cont [168] se ține evidența dobânzilor datorate, aferente împrumuturilor din emisiunea de obligațiuni, creditelor bancare pe termen lung [...] Contul 168 [...] este un cont de pasiv. În creditul contului 168 [...] se înregistrează: – valoarea dobânzilor datorate, aferente împrumuturilor și datoriilor asimilate (666); [...] În debitul contului 168 [...] se înregistrează: – suma dobânzilor plătite aferente împrumuturilor și datoriilor asimilate (512); [...] Soldul contului reprezintă dobânzile datorate și neplătite."
— OMFP 1802/2014, monografia contului 168 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Angajarea lunară a dobânzii neplătite încă se înregistrează **666 = 1682** (termen lung) sau **666 = 5198** (termen scurt) — cheltuiala se recunoaște în luna în care se datorează, nu în luna în care se plătește efectiv.
- La plată, dacă dobânda fusese deja angajată, se stinge datoria: **1682 = 5121** / **5198 = 5121**. Dacă nu fusese angajată în prealabil, plata se înregistrează direct pe cheltuială: **666 = 5121**.
- Pentru **descoperitul de cont (overdraft)**, textul legal nu folosește deloc acest termen — nu există, în OMFP 1802/2014, o prevedere explicită dedicată lui. Singura bază textuală e caracterul bifuncțional al contului 512 „Conturi curente la bănci": soldul creditor al acestui cont reprezintă, prin interpretare, credite primite — tratamentul practic uzual e înregistrarea directă a dobânzii pe cheltuială (666 = 5121), fără să se recunoască separat un principal pe 162/519.
- Deductibilitatea fiscală a dobânzii nu se judecă per tip de credit, ci global: Codul fiscal (art. 40^1 pct. 1) include în „costurile îndatorării" *„dobânda aferentă tuturor formelor de datorii"*, iar art. 40^2 limitează deducerea costurilor excedentare ale îndatorării la 30% din baza de calcul, în limita unui plafon de 1.000.000 euro.

## Ce se greșește în practică

- Se înregistrează dobânda o singură dată, la plată (666 = 5121), chiar și atunci când ea a fost deja angajată lunar pe 1682/5198 — rezultatul e o dublare a cheltuielii sau, dacă angajarea se omite complet, o subevaluare a datoriilor la închiderea lunii.
- Se tratează descoperitul de cont ca un credit obișnuit pe termen scurt, cu recunoașterea unui principal pe contul 519 — de fapt, la overdraft nu se înregistrează de regulă primirea unei sume distincte, pentru că nu există un transfer separat de bani, ci doar un sold creditor temporar al contului curent.
- Se presupune că dobânda la overdraft ar avea un regim fiscal diferit (nedeductibil sau plafonat separat) față de dobânda la un credit clasic — din perspectivă fiscală, Codul fiscal tratează unitar „toate formele de datorii", inclusiv descoperitul de cont; diferența dintre ele ține strict de contul contabil folosit, nu de deductibilitate.
- Se compensează greșit rata (principalul) cu dobânda într-o singură sumă nediferențiată, ceea ce denaturează atât soldul contului de credit, cât și cheltuiala cu dobânda din contul de profit și pierdere.

## Ce face iConta.eu

Verificat direct în cod: motorul `core/credite.py` generează notele contabile pentru credite bancare pe termen lung (conturile 1621/1682/1622) și pe termen scurt (5191/5198/5192), cu funcții separate pentru angajarea dobânzii (`nota_dobanda_angajata`), plata compusă rată+dobândă+comision (`nota_plata`) și reclasificarea la restanță (`nota_restanta`). Codul **nu acceptă un al treilea tip „overdraft"** — funcția internă de validare a tipului respinge explicit orice altă valoare în afară de „lung" sau „scurt". Tratamentul descoperitului de cont (666 = 5121, fără principal recunoscut) se poate obține doar ca efect secundar al aceleiași funcții de plată, apelată cu dobânda angajată dezactivată și rata/comisionul pe zero — nu există un buton sau o opțiune dedicată „overdraft" în aplicație, iar contabilul trebuie să știe să aleagă manual acest mod de lucru. Calculul plafonului fiscal de 30%/1.000.000 euro pentru costurile excedentare ale îndatorării (art. 40^2 CF) **nu e implementat** în acest motor — el produce doar notele contabile, nu și verificarea limitei de deductibilitate fiscală, care rămâne un calcul separat, în sarcina contabilului.

[iConta.eu](/)
