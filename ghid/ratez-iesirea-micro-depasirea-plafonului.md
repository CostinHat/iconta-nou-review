---
title: "Cum să nu ratez ieșirea din micro la depășirea plafonului"
description: "Plafonul de venituri care declanșează trecerea obligatorie de la impozitul pe veniturile microîntreprinderilor la impozitul pe profit, conform Codului fiscal actualizat prin OUG 8/2026."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum să nu ratez ieșirea din micro la depășirea plafonului

Ieșirea din sistemul de impozitare pe veniturile microîntreprinderilor nu e opțională și nu așteaptă finalul anului fiscal — se declanșează automat, din trimestrul în care plafonul e depășit, indiferent dacă firma a observat sau nu depășirea la timp.

## Temeiul legal

::: ghid-temei
„Articolul 52 Reguli de ieșire din sistemul de impunere pe veniturile microîntreprinderilor în cursul anului
(1) Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită.
[...]
(5) Limitele fiscale prevăzute la alin. (1) se verifică pe baza veniturilor înregistrate cumulat de la începutul anului fiscal. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar precedent."
— Codul fiscal (Legea 227/2015), art. 52 alin. (1) și (5), astfel cum a fost modificat de OUG 8/2026 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce trebuie urmărit, ca să nu se rateze momentul:

- **Plafonul e 100.000 euro**, coborât de la 250.000 euro (plafonul aplicabil pentru anul fiscal 2025) prin OUG 8/2026 (Monitorul Oficial nr. 147/25.02.2026), aplicabil pentru verificarea condițiilor de microîntreprindere **inclusiv pentru anul fiscal 2026**.
- **Verificarea e cumulativă, de la începutul anului fiscal**, la cursul de schimb valabil la închiderea exercițiului financiar precedent — nu se face pe fiecare trimestru izolat, ci prin însumarea veniturilor de la 1 ianuarie.
- **Trecerea la impozit pe profit e automată din trimestrul depășirii**, nu din trimestrul următor și nu din anul fiscal următor — o firmă care depășește plafonul în trimestrul II datorează deja impozit pe profit pentru acel trimestru.
- Alte cauze de ieșire obligatorie din micro (art. 52 alin. (2)-(4)): nedepunerea la timp a situațiilor financiare anuale, pierderea condiției de a avea cel puțin un salariat, sau începerea unor activități excluse expres (art. 47 alin. (3) lit. f)-i)) — nu doar depășirea plafonului de venituri.
- Practic, „a nu rata" ieșirea înseamnă urmărirea lunară a veniturilor cumulate față de echivalentul în lei al celor 100.000 euro, nu verificarea o singură dată, la final de an.

## Ce se greșește în practică

- Se verifică plafonul o singură dată, la 31 decembrie, în loc de urmărire cumulativă, lunară sau trimestrială, de la începutul anului.
- Se presupune că trecerea la impozit pe profit se aplică din anul fiscal următor, nu din trimestrul curent în care s-a produs depășirea — regula corectă e imediată, nu amânată.
- Se ignoră celelalte condiții de ieșire (nedepunerea situațiilor financiare, pierderea salariatului) tratând depășirea plafonului de venituri ca fiind singura cauză posibilă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu verifică și nu semnalează automat** depășirea plafonului de 100.000 euro — nu există, în cod, nicio constantă a plafonului micro. Modulul `core/test_a8_micro_baza.py` testează doar calculul bazei impozabile trimestriale (cota de 1%), nu verificarea eligibilității sau a plafonului. Aplicația **nu are, la data acestui ghid, o alertă proactivă** care să notifice utilizatorul, automat sau în timp real, la apropierea de plafon — momentul depășirii și trecerea la impozit pe profit rămân integral în sarcina contabilului, pe baza introducerii corecte și la timp a veniturilor cumulate.

[iConta.eu](/)
