---
title: "Reacția pieței la noile restricții de numerar 2026"
description: "Plafoanele actuale pentru încasări și plăți în numerar între firme, între firme și persoane fizice, și de ce comercianții își adaptează practicile de casierie."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Reacția pieței la noile restricții de numerar 2026

Plafoanele legale pentru operațiunile cu numerar există de mai mulți ani, dar rămân o sursă constantă de fricțiune pentru comercianți: praguri diferite după tipul de operațiune, interdicția fragmentării plăților și distincția între relațiile firmă-firmă și firmă-persoană fizică fac ca „reacția firească" a pieței să fie multiplicarea metodelor de plată electronică acolo unde plafonul de numerar riscă să fie depășit.

## Temeiul legal

```
::: ghid-temei
„(1) Prin excepție de la prevederile art. 1 alin. (1) se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții:
a) încasări de la persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei de la o persoană;
...
c) plăți către persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei/persoană, dar nu mai mult de un plafon total de 10.000 lei/zi."
— Legea nr. 70/2015 pentru întărirea disciplinei financiare privind operațiunile de încasări și plăți în numerar, art. 3 alin. (1) lit. a) și c) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::
```

Structura actuală a plafoanelor, așa cum rezultă din lege:

- **Între firme (persoane juridice/entități din art. 1 alin. (1)):** 5.000 lei/zi/persoană la încasări, respectiv 5.000 lei/zi/persoană la plăți, dar cu un plafon total de 10.000 lei/zi pentru toate plățile în numerar ale unei zile.
- **Magazinele de tip cash and carry** au un plafon distinct, mai mare: 10.000 lei/zi/persoană, atât la încasări cât și la plăți.
- **Avansurile spre decontare** (banii dați angajaților/administratorilor pentru cheltuieli) au propriul plafon zilnic: 5.000 lei, per persoană care a primit avansul.
- **Firmă către persoană fizică** (achiziții de bunuri, servicii, dividende, restituiri de împrumuturi): plafon zilnic de 10.000 lei către o persoană (art. 4).
- **Între persoane fizice**, operațiunile de acest tip (transfer de proprietate, prestări servicii, împrumuturi) au un plafon mai mare: 50.000 lei/tranzacție.
- **Fragmentarea este expres interzisă:** legea nu permite împărțirea unei facturi sau a unei tranzacții în tranșe mai mici, doar ca să încapă sub plafon.

## Ce se greșește în practică

- Se aplică plafonul de 10.000 lei (specific cash and carry sau plăților firmă-persoană fizică) și tranzacțiilor obișnuite firmă-firmă, unde plafonul e de fapt 5.000 lei/persoană.
- Se împarte o factură mare în mai multe încasări succesive în numerar, în aceeași zi sau în zile diferite, crezând că fiecare tranșă „sub plafon" e legală — legea sancționează explicit fragmentarea.
- Se ignoră faptul că avansurile spre decontare au propriul plafon de 5.000 lei/zi/persoană, distinct de plafonul general al plăților firmă-firmă.

## Ce face iConta.eu

Modulul `core/casa.py` conține funcția `verifica_plafon`, care calculează, pe baza operațiunilor de casă înregistrate, dacă plafonul legal a fost depășit — inclusiv distincția pentru cash and carry și pentru avansurile spre decontare, confirmat direct din cod (`plafon_avans_decontare` ca parametru distinct al cotei aplicate). Verificarea acoperă operațiunile trecute prin registrul de casă din aplicație; tranzacțiile în numerar care nu sunt înregistrate prin acest modul nu pot fi, evident, verificate automat.

[iConta.eu](/)
