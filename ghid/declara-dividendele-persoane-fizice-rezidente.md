---
title: "Cum se declară dividendele unei persoane fizice rezidente?"
description: "Cota de impozit pe dividende, termenul de plată și declararea prin D205 pentru dividendele distribuite unei persoane fizice rezidente în România."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se declară dividendele unei persoane fizice rezidente?

Impozitul pe dividende plătite unei persoane fizice rezidente este final, se reține la sursă de către firma plătitoare, iar din 2026 cota a revenit la 16% — nivelul cel mai ridicat din ultimul deceniu.

## Temeiul legal

::: ghid-temei
„Veniturile sub formă de dividende, inclusiv câştigul obţinut ca urmare a deţinerii de titluri de participare definite de legislaţia în materie la organisme de plasament colectiv, se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligaţia calculării şi reţinerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor/sumelor reprezentând câştigul obţinut ca urmare a deţinerii de titluri de participare de către acţionari/asociaţi/investitori. Termenul de virare a impozitului este până la data de 25 inclusiv a lunii următoare celei în care se face plata."
— Legea nr. 227/2015 (Codul fiscal), art. 97 alin. (7), astfel cum a fost modificat prin Legea nr. 141/2025, aplicabil dividendelor distribuite începând cu 1 ianuarie 2026 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Pentru o distribuire către o persoană fizică rezidentă, pașii legali sunt:

- **Calculul și reținerea** impozitului revin firmei plătitoare, nu asociatului — obligația se naște „odată cu plata dividendelor", deci momentul relevant este plata efectivă, nu doar aprobarea distribuirii.
- **Cota este de 16%**, aplicabilă dividendelor distribuite începând cu 1 ianuarie 2026 (cota a fost 5% în perioada 2016-2022, apoi 8% în 2023-2024, 10% în 2025).
- **Termenul de virare** este până la data de 25 inclusiv a lunii următoare celei în care s-a făcut plata; dacă dividendele au fost distribuite dar nu au fost plătite până la sfârșitul anului aprobării, impozitul se plătește până la 25 ianuarie a anului următor.
- Impozitul este **final** — asociatul nu mai raportează separat acest venit, iar firma îl declară nominal, pe beneficiar, prin Declarația informativă D205.

## Ce se greșește în practică

- Se calculează impozitul la data aprobării distribuirii dividendelor, nu la data plății efective — momentul relevant pentru cotă și pentru termenul de virare este plata, nu aprobarea în AGA.
- Se aplică o cotă veche (5%, 8% sau 10%), reținută din experiența anilor anteriori, pentru dividende distribuite după 1 ianuarie 2026, când cota corectă este 16%.
- Se omite declararea nominală prin D205 a fiecărui beneficiar persoană fizică, deși impozitul a fost reținut și virat corect — declararea informativă este un pas separat, obligatoriu.

## Ce face iConta.eu

Generatorul D205 din iConta.eu (`core/d205.py`) calculează impozitul pe dividende plătit pe fiecare asociat, aplicând cota corespunzătoare **datei distribuirii** dividendului (nu datei plății), potrivit regulii tranzitorii din Legea 141/2025 pentru dividendele interimare distribuite în 2025 dar plătite ulterior. Aplicația distinge explicit între dividendul distribuit (creditul contului 457) și dividendul efectiv plătit (debitul contului 457), atribuind plățile pe distribuiri în ordine cronologică (FIFO), pentru a calcula corect impozitul atunci când cota s-a schimbat între cele două momente. Declarația D205 este generată direct din aceste înregistrări, fără reintroducere manuală a datelor.

[iConta.eu](/)
