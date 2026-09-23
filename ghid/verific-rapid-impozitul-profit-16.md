---
title: "Cum verific rapid dacă impozitul pe profit de 16% a fost calculat corect înainte de depunerea D101?"
description: Verificarea rapidă e o singură înmulțire — profitul impozabil (rd. 40) × 16% trebuie să dea impozitul de la rd. 41 — cu o singură excepție de regim (IMCA), pentru cifre de afaceri peste 50 de milioane de euro.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific rapid dacă impozitul pe profit de 16% a fost calculat corect înainte de depunerea D101?

Pentru marea majoritate a firmelor, verificarea rapidă e o singură formulă. Pentru cele mari, mai există o al doilea regim de calculat, dar la fel de precis.

## Temeiul legal

::: ghid-temei
„Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%." — Legea nr. 227/2015 (Codul fiscal), art. 17.
:::

## Formula de verificat

Impozitul pe profit (rândul 41 al declarației) se calculează, în regimul standard, ca profitul impozabil (rândul 40) înmulțit cu 16%. Verificarea rapidă e exact atât: ia profitul impozabil din declarație, înmulțește-l cu 0,16 și compară rezultatul, rotunjit, cu ce apare pe rândul 41.

Dacă suma nu se potrivește, cauzele cele mai probabile sunt: o rotunjire greșită (rotunjirea corectă e aritmetică — la 0,5 se rotunjește în sus —, nu bancară), un profit impozabil calculat greșit în etapele anterioare, sau o eroare de transcriere.

## Excepția: regimul IMCA

Firmele cu cifra de afaceri a anului precedent peste **50.000.000 euro** (la cursul de la închiderea exercitiului financiar precedent) pot datora impozitul minim pe cifra de afaceri (IMCA), calculat după o formulă proprie (bazată pe cifra de afaceri și investiții, nu pe profitul impozabil), nu simpla înmulțire cu 16%. Declarația compară cele două variante de calcul și o alege pe cea aplicabilă — dacă firma ta se apropie de acest prag, verificarea rapidă de mai sus nu mai e suficientă, fiindcă baza de calcul se schimbă complet.

## Ce se greșește în practică

- Se verifică formula pe profitul **contabil**, nu pe cel **impozabil** — cele două diferă exact prin ajustările fiscale (deduceri, venituri neimpozabile, cheltuieli nedeductibile), iar cota de 16% se aplică doar pe al doilea.
- Se aplică rotunjirea Python standard (half-to-even) în loc de rotunjirea aritmetică cerută pentru sumele fiscale — la valori exact pe „,50" cele două metode pot da rezultate diferite.
- Se ignoră pragul IMCA la firmele care se apropie de el de la un an la altul — verificarea „profit impozabil × 16%" nu se mai aplică odată depășit pragul.

## Ce face iConta.eu

Calculează rândul 41 direct din profitul impozabil × 16%, cu rotunjire aritmetică (nu bancară) pentru sumele fiscale. Când cifra de afaceri a anului precedent depășește pragul de 50.000.000 euro, cere explicit componentele regimului IMCA și calculează varianta corespunzătoare, comparând-o cu cea standard — nu aplică tacit un implicit care ar putea subevalua impozitul unei firme mari.

[iConta.eu](/)
