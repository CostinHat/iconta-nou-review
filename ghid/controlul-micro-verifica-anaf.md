---
title: "Controlul pe micro: ce verifică ANAF"
description: "Plafonul de venituri pe care ANAF îl verifică prioritar la o microîntreprindere, coborât la echivalentul a 100.000 euro începând cu 1 ianuarie 2026, și celelalte condiții cumulative de eligibilitate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Controlul pe micro: ce verifică ANAF

La o microîntreprindere, prima linie de verificare a organului fiscal nu ține de deductibilitatea vreunei cheltuieli — pentru că impozitul micro se calculează pe venituri, nu pe cheltuieli — ci de îndeplinirea condițiilor cumulative de eligibilitate pentru acest regim, în frunte cu plafonul de venituri anuale.

## Temeiul legal

::: ghid-temei
„Pentru anul fiscal 2025/2026, limita veniturilor realizate, reprezentând echivalentul în lei a 250.000 euro, respectiv echivalentul în lei a 100.000 euro începând cu 1 ianuarie 2026, se verifică pe baza veniturilor realizate de către persoana juridică română la data de 31 decembrie 2024, respectiv la data de 31 decembrie 2025."
— Legea nr. 227/2015 (Codul fiscal), art. 54 alin. (3) (dispoziții tranzitorii privind plafonul micro) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce urmărește practic un control fiscal la o firmă micro:

- **Plafonul de venituri** — de la 1 ianuarie 2026, limita s-a redus la echivalentul a **100.000 euro**, față de 250.000 euro anterior; depășirea plafonului în cursul anului scoate firma din regimul micro începând din trimestrul depășirii, nu abia din anul următor.
- **Existența salariatului** — condiția de la art. 47 alin. (1) lit. d) (cel puțin un salariat, cu excepțiile de la art. 48 alin. (3)) e verificată separat de plafonul valoric.
- **Structura capitalului social și ponderea veniturilor din consultanță/management** — celelalte condiții cumulative din art. 47, a căror nerespectare, la fel ca depășirea plafonului, obligă la trecerea la impozitul pe profit.

## Ce se greșește în practică

- Se raportează la plafonul vechi de 250.000 euro și după 1 ianuarie 2026, deși limita s-a redus la 100.000 euro, expunând firma la riscul de a rămâne, fără să știe, sub obligația de impozit pe profit.
- Se verifică plafonul o singură dată, la începutul anului, în loc să se monitorizeze cumulat, trimestrial — depășirea în cursul anului scoate firma din micro imediat, nu de la 1 ianuarie următor.
- Se presupune că un control ANAF pe o firmă micro va verifica deductibilitatea cheltuielilor, similar unui control de impozit pe profit — la micro, miza controlului e alta: încadrarea corectă în regim, nu cheltuielile.

## Ce face iConta.eu

La data acestui ghid, iConta.eu urmărește obligațiile declarative datorate pentru regimul fiscal setat de firmă (`core/control_fiscal_api.py`, funcția `obligatii_datorate`), inclusiv D100 trimestrial pentru micro, dar **nu monitorizează automat** depășirea plafonului de venituri și nu alertează contabilul când firma trebuie să treacă la impozitul pe profit. Verificarea continuă a plafonului și a celorlalte condiții de eligibilitate rămâne responsabilitatea contabilului.

[iConta.eu](/)
