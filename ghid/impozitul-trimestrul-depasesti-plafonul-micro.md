---
title: "Impozitul în trimestrul în care depășești plafonul micro"
description: "Cum se calculează impozitul pe profit din trimestrul în care o microîntreprindere depășește plafonul de 100.000 euro venituri."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Impozitul în trimestrul în care depășești plafonul micro

Când veniturile cumulate ale unei microîntreprinderi depășesc, în cursul anului, echivalentul a 100.000 euro, firma nu așteaptă anul fiscal următor pentru a trece la impozit pe profit — trecerea e imediată, chiar din trimestrul depășirii, iar impozitul pe profit se calculează doar pentru veniturile și cheltuielile din acel trimestru înainte, nu retroactiv pe tot anul.

## Temeiul legal

::: ghid-temei
„Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită."
— Legea nr. 227/2015 (Codul fiscal), art. 52 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- **Trecerea la impozit pe profit e obligatorie și imediată**, din trimestrul depășirii — nu e o opțiune și nu se poate amâna la finalul anului.
- **Limita se verifică pe baza veniturilor cumulate de la începutul anului fiscal**, potrivit art. 52 alin. (5), la cursul de schimb valabil la închiderea exercițiului financiar precedent.
- **Calculul impozitului pe profit se face separat, doar pentru trimestrul respectiv**: „Calculul și plata impozitului pe profit de către microîntreprinderile care se încadrează în prevederile alin. (1) [...] se efectuează luând în considerare veniturile și cheltuielile realizate începând cu trimestrul respectiv" — art. 52 alin. (6). Veniturile și cheltuielile din trimestrele anterioare rămân sub regimul micro, deja impozitate ca atare.

## Ce se greșește în practică

- Se așteaptă finalul anului fiscal pentru a comunica trecerea la impozit pe profit, deși obligația e din trimestrul depășirii, nu ulterior.
- Se recalculează retroactiv impozitul pentru întregul an ca impozit pe profit, deși legea prevede explicit că doar veniturile și cheltuielile "realizate începând cu trimestrul respectiv" intră în noul calcul.
- Se ignoră verificarea cumulată a plafonului atunci când firma face parte dintr-un grup de întreprinderi legate — art. 52 alin. (5^1) cere cumularea veniturilor persoanelor legate la verificarea plafonului, în situațiile prevăzute la art. 47 alin. (1^1).

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu verifică și nu semnalează automat** depășirea plafonului de 100.000 euro în cursul anului. Modulul `core/control_fiscal_api.py` tratează regimul fiscal (`regim_fiscal`) ca pe un câmp declarat manual de utilizator, la Date firmă, și confirmă explicit, în comentariile de cod, că nu există nicio constantă a plafonului micro în aplicație — deci nu poate detecta singură momentul depășirii și nici trimestrul din care ar trebui calculat impozitul pe profit. Comutarea efectivă a regimului de calcul, inclusiv separarea veniturilor și cheltuielilor pe trimestrul depășirii, rămâne integral responsabilitatea contabilului, care actualizează manual regimul fiscal declarat.

[iConta.eu](/)
