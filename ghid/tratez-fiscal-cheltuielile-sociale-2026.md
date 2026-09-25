---
title: "Cum tratez fiscal cheltuielile sociale în 2026?"
description: "Plafonul de 5% pentru cheltuielile sociale deductibile la impozitul pe profit și ce categorii intră sub această limită, potrivit Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum tratez fiscal cheltuielile sociale în 2026?

Cheltuielile sociale (ajutoare de înmormântare, cadouri pentru copiii salariaților, tichete de creșă, servicii de sănătate pentru boli profesionale ș.a.) nu sunt nici integral deductibile, nici nedeductibile — sunt cheltuieli cu deductibilitate limitată, plafonate global la un procent din fondul de salarii al firmei, indiferent câte categorii diferite de cheltuieli sociale sunt acordate în același an.

## Temeiul legal

::: ghid-temei
„Următoarele cheltuieli au deductibilitate limitată: [...] b) cheltuielile sociale, în limita unei cote de până la 5%, aplicată asupra valorii cheltuielilor cu salariile personalului, potrivit Codului muncii. Intră sub incidența acestei limite următoarele: 1. ajutoarele de înmormântare, ajutoarele pentru bolile grave și incurabile, ajutoarele pentru naștere, ajutoarele pentru proteze, ajutoarele pentru pierderi produse în gospodăriile proprii, ajutorarea copiilor din școli și centre de plasament; 2. cheltuielile pentru funcționarea corespunzătoare a unor unități aflate în administrarea contribuabililor, precum: creșe, grădinițe, școli, muzee, biblioteci, cantine, baze sportive, cluburi, cămine de nefamiliști și altele asemenea; 3. cheltuielile reprezentând: cadouri în bani sau în natură, inclusiv tichete cadou oferite salariaților și copiilor minori ai acestora, servicii de sănătate acordate în cazul bolilor profesionale și al accidentelor de muncă până la internarea într-o unitate sanitară, tichete culturale și tichete de creșă acordate de angajator [...]; 4. alte cheltuieli cu caracter social efectuate în baza contractului colectiv de muncă sau a unui regulament intern."
— Legea 227/2015, art. 25 alin. (3) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cum se aplică plafonul de 5% în 2026:

- **Baza de calcul** e valoarea cheltuielilor cu salariile personalului, potrivit Codului muncii — nu profitul contabil, ca la protocol, ci fondul de salarii al firmei pentru perioada respectivă.
- **Toate cele patru categorii se cumulează** sub același plafon de 5% — ajutoarele (pct. 1), cheltuielile pentru unități sociale proprii precum cantine sau creșe (pct. 2), cadourile și tichetele (pct. 3) și alte cheltuieli sociale din contractul colectiv sau regulamentul intern (pct. 4) nu au plafoane separate, ci un singur plafon comun.
- **Suplimentar există și un plafon specific** pentru sumele achitate de contribuabil pentru plasarea copiilor angajaților în unități de educație timpurie (creșe/grădinițe terțe) — maximum 1.500 lei/lună pentru fiecare copil, în condițiile de la art. 76 alin. (4^1) lit. i), sumă care intră tot sub plafonul general de 5%.
- **Partea care depășește 5%** din fondul de salarii devine, pentru anul fiscal respectiv, cheltuială nedeductibilă la calculul impozitului pe profit — cheltuiala rămâne înregistrată contabil integral, doar partea excedentară se adaugă înapoi la profitul impozabil.

## Ce se greșește în practică

- Se calculează separat câte un plafon de 5% pentru fiecare categorie (ajutoare, cadouri, unități sociale) în loc de un singur plafon comun aplicat la suma tuturor cheltuielilor sociale din categoriile 1-4.
- Se include, din eroare, în baza de calcul a plafonului (fondul de salarii) și alte cheltuieli cu personalul care nu sunt „salarii" în sensul Codului muncii (de exemplu contribuții datorate de angajator), umflând astfel artificial plafonul disponibil.
- Se depășește plafonul de 1.500 lei/lună/copil pentru sumele de educație timpurie, considerându-l independent de plafonul general de 5%, deși el rămâne cuprins în același calcul global.

## Ce face iConta.eu

iConta.eu are contul dedicat cheltuielilor sociale în planul de conturi și calculează cheltuielile cu salariile personalului prin modulul de salarizare (`core/salarizare.py`), date care ar constitui baza de calcul a plafonului de 5%. La data acestui ghid, aplicația **nu calculează automat, în cadrul declarației de impozit pe profit, încadrarea cumulată a cheltuielilor sociale în plafonul de 5%** din fondul de salarii — verificarea depășirii plafonului și ajustarea rezultatului fiscal rămân în sarcina contabilului, la momentul întocmirii declarației.

[iConta.eu](/)
