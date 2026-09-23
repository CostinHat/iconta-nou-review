---
title: "Voucherele de vacanță la HoReCa 2026"
description: Regulile de taxare a voucherelor de vacanță pentru 2026 nu depind de domeniul de activitate al angajatorului — se aplică identic firmelor din HoReCa și oricărei alte firme, inclusiv plafonul anual pe două praguri din 2026.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Voucherele de vacanță la HoReCa 2026

Nu există un regim fiscal special pentru voucherele de vacanță acordate de firmele din HoReCa — mecanismul de taxare și plafonul anual sunt aceleași ca pentru orice alt angajator, indiferent de domeniul de activitate.

## Temeiul legal

::: ghid-temei
OUG 8/2009 privind acordarea tichetelor de vacanță, art. 1 alin. (4): „Nivelul maxim al sumelor care pot fi acordate salariaților sub forma de tichete de vacanță este contravaloarea a 6 salarii de bază minime brute pe țară garantate în plată, pentru un salariat, în decursul unui an fiscal."
:::

Plafonul anual se calculează pe baza salariului minim brut pe țară valabil la data acordării, iar în 2026 acest salariu minim crește la jumătatea anului — ceea ce ridică plafonul în cursul aceluiași an fiscal:

- de la 1 ianuarie până la 30 iunie 2026: salariul minim e 4.050 lei/lună (HG 1506/2024, art. 1) → plafon anual = 6 × 4.050 = **24.300 lei**;
- de la 1 iulie 2026: salariul minim e 4.325 lei/lună (HG 146/2026, art. 1) → plafon anual = 6 × 4.325 = **25.950 lei**.

Indiferent de sector (inclusiv HoReCa), voucherele de vacanță sunt taxate cu CASS 10% și impozit 10% (calculat pe baza rămasă după CASS), fără CAS și fără CAM — inclusiv sub plafonul anual, care nu are rol de scutire, ci doar de limitare a sumei ce poate fi acordată sub această formă.

## Ce se greșește în practică

- Se presupune, greșit, că firmele din HoReCa au un plafon sau un regim de taxare diferit pentru voucherele de vacanță — nu există un astfel de temei legal.
- Se folosește un plafon anual fix (de exemplu 24.300 lei) pentru tot 2026, ignorând majorarea salariului minim de la 1 iulie, care ridică plafonul la 25.950 lei pentru voucherele acordate în a doua jumătate a anului.
- Se tratează voucherul de vacanță sub plafon ca sumă neimpozabilă, similar tichetelor cadou sub 300 de lei — de fapt e taxat integral cu CASS și impozit, indiferent de nivel.

## Ce face iConta.eu

Plafonul anual al voucherelor de vacanță se calculează dinamic pe baza salariului minim brut valabil la data fiecărei perioade (`core/stat_plata_api.py`), astfel încât cele două praguri din 2026 (24.300 lei / 25.950 lei) sunt aplicate automat, fără să depindă de domeniul de activitate al firmei. Taxarea propriu-zisă (CASS 10% + impozit 10%, fără CAS/CAM) se calculează la fel pentru orice firmă, inclusiv cele din HoReCa, iar excedentul peste plafon e adăugat automat la venitul salarial obișnuit.

[iConta.eu](/)
