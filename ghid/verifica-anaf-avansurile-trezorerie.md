---
title: "Ce verifică ANAF la avansurile de trezorerie"
description: "Plafonul zilnic legal pentru plățile din avansuri spre decontare și de ce e unul dintre primele lucruri urmărite la un control de casierie."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce verifică ANAF la avansurile de trezorerie

Avansurile spre decontare — sumele date angajaților pentru cheltuieli mărunte, deplasări sau achiziții urgente — sunt un punct clasic de verificare la controlul de casierie, pentru că plafonul lor legal e ușor de depășit din neatenție și greu de justificat retroactiv.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile art. 1 alin. (1) se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: [...] e) plăți din avansuri spre decontare, în limita unui plafon zilnic de 5.000 lei, stabilit pentru fiecare persoană care a primit avansuri spre decontare.
[...] (4) La data acordării avansurilor spre decontare, sumele aferente intră în calculul plafonului zilnic prevăzut la alin. (1) lit. c) sau d), după caz."
— Legea nr. 70/2015, art. 3 alin. (1) lit. e) și alin. (4) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Ce urmărește efectiv un control pe avansurile de trezorerie:

- **Plafonul de 5.000 lei/zi se verifică pe fiecare persoană** care a primit avans, nu la nivel agregat pe firmă — un angajat care justifică cheltuieli de peste 5.000 lei într-o singură zi din avansul primit depășește plafonul, chiar dacă suma totală a firmei pare rezonabilă.
- **Momentul acordării avansului intră în calculul plafonului zilnic** al plăților către persoana respectivă — deci acordarea avansului și cheltuielile justificate din el, în aceeași zi, se cumulează la același plafon.
- Fragmentarea artificială a unei plăți mai mari, prin decontări succesive în aceeași zi, pentru a rămâne „tehnic" sub plafon, e exact tipul de practică pe care organul de control o caută.

## Ce se greșește în practică

- Se acordă avansuri mari, „pentru siguranță", fără să se verifice dacă justificarea din acea zi va depăși plafonul de 5.000 lei — plafonul se aplică plăților efective din avans, nu doar sumei acordate inițial.
- Se decontează cheltuieli din avans în tranșe mici, în aceeași zi, pentru a evita depășirea aparentă a plafonului — fragmentarea e explicit interzisă de lege, indiferent de intenție.
- Se ignoră cumularea dintre suma acordată ca avans și cheltuielile plătite din acesta, în aceeași zi calendaristică — ambele intră în același calcul de plafon.

## Ce face iConta.eu

Verificat în cod: modulul `core/casa.py` conține funcția `verifica_plafon`, care calculează soldul zilnic al casei și verifică explicit plafonul avansurilor spre decontare (`plafon_avans_decontare`), pe baza cotei/temeiului legal ținut în registrul intern al aplicației. Depășirile sunt semnalate ca avertismente cu temei citat (nu blochează operațiunea, dar marchează riscul de control), pentru fiecare zi în care apar. Funcția `avans_deconteaza` din același modul gestionează decontarea efectivă a avansurilor acordate angajaților, cu urmărirea sumei rămase nedecontate.

[iConta.eu](/)
