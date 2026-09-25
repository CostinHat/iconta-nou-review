---
title: "Cum declar dividendele impuse legal"
description: "Ce cotă se aplică dividendelor distribuite de o firmă românească, cine reține impozitul și care este termenul de declarare și plată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum declar dividendele impuse legal

Impozitul pe dividende nu e o declarație pe care o depune asociatul care le încasează — obligația de calcul, reținere și declarare aparține firmei care distribuie dividendele, iar cota aplicabilă depinde de data la care dividendele au fost efectiv distribuite.

## Temeiul legal

::: ghid-temei
„Veniturile sub formă de dividende, inclusiv câștigul obținut ca urmare a deținerii de titluri de participare definite de legislația în materie la organisme de plasament colectiv, se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor [...] Termenul de virare a impozitului este până la data de 25 inclusiv a lunii următoare celei în care se face plata."
— Legea 227/2015 (Codul fiscal), art. 97 alin. (7) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce trebuie știut la declararea dividendelor:

- Cota de 16% se aplică dividendelor **distribuite** începând cu 1 ianuarie 2026 (Legea 141/2025); dividendele interimare distribuite în 2025 rămân la cota de 10% chiar dacă se plătesc sau se regularizează în 2026, fără recalculare.
- Dacă dividendele distribuite nu sunt plătite până la sfârșitul anului în care s-a aprobat distribuirea, impozitul se declară și se plătește **până la 25 ianuarie a anului următor** (sau data echivalentă, pentru an fiscal modificat).
- Declararea impozitului reținut se face prin D205 (declarația informativă anuală, pe beneficiari de venit), cu termen până în ultima zi a lunii februarie a anului curent pentru anul expirat.

## Ce se greșește în practică

- Se aplică o singură cotă (16%) tuturor dividendelor distribuite în trecut, ignorând faptul că data distribuirii (nu data plății) decide cota aplicabilă — o distribuire din 2025 rămâne la 10%, chiar dacă plata are loc în 2026.
- Se confundă impozitul pe dividende (final, reținut la sursă de firmă) cu impozitul pe câștigul din lichidare — sunt regimuri și cote diferite (16%/10%, respectiv 10% fix, în articole distincte ale art. 97).
- Se omite declararea impozitului pentru dividendele aprobate, dar neplătite până la finalul anului — obligația de declarare/plată la 25 ianuarie există indiferent de plata efectivă către asociați.

## Ce face iConta.eu

iConta.eu are un modul funcțional pentru calculul impozitului pe dividende (`core/dividende_curs.py`), care urmărește mișcările contului 457 (distribuiri și plăți) și atribuie, prin metodă FIFO pe dată, cota corectă în funcție de momentul **distribuirii** — nu al plății — respectând astfel exact regula de tranziție 10%→16% din Legea 141/2025. Rezultatul alimentează generatorul D205 (`core/d205.py`), care produce declarația informativă anuală. Aplicația nu depune însă declarația la ANAF — generează documentul pregătit pentru depunere, pas care rămâne al contabilului.

[iConta.eu](/)
