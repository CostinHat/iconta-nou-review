---
title: "Cum se acordă avansuri spre decontare 2026"
description: "Plafonul legal pentru avansurile de trezorerie date angajaților spre decontare și cum le înregistrează iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se acordă avansuri spre decontare 2026

Avansul spre decontare — banii dați unui angajat înainte de o deplasare sau o achiziție, pe care acesta îi justifică ulterior cu documente — e un avans de trezorerie (cont 542), diferit de avansul comercial dat unui furnizor sau încasat de la un client (conturile 409/419). Are propria regulă de plafon în numerar, pe zi și pe persoană.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile art. 1 alin. (1) se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: [...] e) plăți din avansuri spre decontare, în limita unui plafon zilnic de 5.000 lei, stabilit pentru fiecare persoană care a primit avansuri spre decontare."
— Legea 70/2015, art. 3 alin. (1) lit. e) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

- Plafonul de 5.000 lei/zi se aplică per persoană care a primit avansul, nu per firmă — dacă mai mulți angajați primesc avansuri în aceeași zi, plafonul se verifică separat, pentru fiecare în parte.
- „La data acordării avansurilor spre decontare, sumele aferente intră în calculul plafonului zilnic" al plăților în numerar către persoane fizice (art. 3 alin. 4 din aceeași lege) — avansul dat în numerar nu e o categorie complet separată de celelalte plăți cash către persoane fizice, ci se cumulează cu ele la verificarea plafonului zilnic.
- Contabil, avansul spre decontare e un avans de trezorerie: se acordă din casă sau din bancă (542 = 5311/5121), iar la decontul de cheltuieli (deplasare, achiziții mărunte) se închide prin cheltuiala efectiv justificată (625 = 542, plus TVA deductibil dacă există factură cu TVA pe cazare/transport), cu diferența restituită sau, dacă cheltuielile depășesc avansul, plătită suplimentar angajatului.
- Dacă avansul e legat de o deplasare, plafonul de diurnă neimpozabilă (art. 76 Cod fiscal, HG 714/2018) e o regulă separată, care privește doar componenta de diurnă a decontului, nu avansul în sine.

## Ce se greșește în practică

- Se confundă avansul spre decontare (cont 542, dat angajatului) cu avansul comercial către furnizor (cont 409) — sunt operațiuni contabile complet diferite, cu conturi și logică diferite.
- Se depășește plafonul de 5.000 lei/zi/persoană fără să se verifice cumulul cu alte plăți în numerar către aceeași persoană fizică din aceeași zi.
- Se emite avansul fără să se urmărească justificarea lui printr-un decont ulterior — suma rămasă în 542, nedecontată, distorsionează evidența trezoreriei.
- Se calculează TVA deductibilă pe cazare/transport din decont fără să existe o factură cu TVA pe numele firmei, sau invers, se omite TVA deductibilă când factura există.

## Ce face iConta.eu

Avansurile spre decontare fac parte din modulul „Deconturi de deplasare și diurnă" al iConta, nu din motorul de avansuri comerciale furnizori/clienți (409/419) — sunt două funcționalități distincte în aplicație, cu conturi și ecrane separate. Acordarea avansului generează nota **542 = 5311/5121** (din casă sau din bancă), iar decontul ulterior generează **625 = 542** pentru cheltuielile justificate (plus TVA deductibilă dacă există factură cu TVA pe cazare sau transport), cu restituirea sau plata diferenței față de avansul acordat.

Aplicația urmărește separat, în registrul de casă, plafonul zilnic de 5.000 lei pe fiecare persoană care a primit avansuri — dacă suma avansurilor date aceleiași persoane într-o zi depășește plafonul, apare un avertisment. Avertismentul e informativ, nu blocant: operațiunea rămâne legală de înregistrat, dar semnalează riscul la un eventual control. Cota de TVA pentru decont trebuie declarată explicit de contabil la fiecare decont cu documente justificative — aplicația nu presupune tacit nicio cotă implicită.

[iConta.eu](/)
