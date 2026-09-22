---
title: Cum se depune declarația 100 pentru impozitul pe profit trimestrial?
description: D100 pentru impozitul pe profit se depune trimestrial (trimestrele I-III), până pe 25 ale lunii următoare, dar pentru firmele pe regim de profit trebuie generată manual — semaforul de obligații nu o reamintește automat.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se depune declarația 100 pentru impozitul pe profit trimestrial?

Depunerea D100 pentru impozitul pe profit ridică o capcană specifică în iConta.eu: spre deosebire de impozitul micro, unde obligația apare automat în lista de urmărire, pentru firmele pe regim de profit generarea D100 trebuie inițiată manual, trimestru de trimestru.

## Temeiul legal

::: ghid-temei
**CF art. 41 alin. (1):**
> „Calculul, declararea și plata impozitului pe profit, cu excepțiile prevăzute de prezentul articol, se
> efectuează trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III.
> Definitivarea și plata impozitului pe profit aferent anului fiscal respectiv se efectuează până la
> termenul de depunere a declarației privind impozitul pe profit prevăzut la art. 42."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt:4532-4534`

**OPANAF 587/2016, Anexa 4, Cap. I, pct. 1.2 lit. c):**
> „Trimestrial, pentru obligațiile de plată reprezentând: ... c) impozitul pe profit datorat de persoane
> juridice române și persoanele juridice străine, altele decât cele prevăzute la lit. a) și b), precum și
> de către persoanele juridice cu sediul social în România, înființate potrivit legislației europene
> (trimestrele I-III);"
— sursă: `anaf_surse/opanaf_587_2016_aprobarea_modelului_continutului_formularelor_utilizate.txt:927-930`

**Structura tehnică D100, nomenclator poz. 2, cod 103:**
> „2. 103 (poz.2) Impozit pe profit/plăți anticipate în contul impozitului pe profit anual datorat
> /datorate de persoane juridice române, altele decât cele de la pct.1, precum și de persoanele juridice
> cu sediul social în România, înființate potrivit legislației europene — art.13 și 41 din Legea
> nr.227/2015 privind Codul fiscal — 5503 — T ... a) pt. plăți anticipate trim.I,II,III: 25 a lunii
> următoare per. de raportare — 25LU; b) pt. plăți anticipate trim.IV: 25 a lunii de sfârșit (LS) din
> anul de raportare — 25LS"
— sursă: `anaf_surse/d100_struct_anaf.txt:634-684`
:::

## Pașii de depunere pentru trimestrele I-III

Pentru trimestrele I-III, termenul legal e ferm: 25 a lunii următoare încheierii trimestrului (25 aprilie, 25 iulie, 25 octombrie). Suma se calculează pe baza profitului cumulat de la 1 ianuarie minus ce s-a impozitat deja în trimestrele anterioare, cu cota de 16%.

**Atenție critică:** pentru firmele pe regim „profit", semaforul de obligații/restanțe al aplicației **nu adaugă niciodată D100 la lista de urmărit** — doar D101 (declarația anuală) apare automat. Asta înseamnă că trebuie să generați manual D100, din ecranul de declarații, la fiecare din trimestrele I-III, fără să vă bazați pe o alertă a aplicației. Dacă regimul fiscal al firmei nu e completat în vectorul fiscal, nici D100, nici D101 nu pot fi determinate corect — completați regimul fiscal înainte de a genera declarații.

Pentru trimestrul IV, situația e mai puțin clară: legea (art. 41 alin. 1) și normele ANAF rezervă în mod explicit D100 trimestrial doar trimestrelor I-III, urmând ca definitivarea anuală să se facă prin D101. Structura tehnică D100 permite totuși generarea unei obligații cod 103 și pentru luna 12 (cu scadență 25 decembrie), dar acest caz aparține de regulă regimului opțional cu plăți anticipate (o formulă de calcul diferită de cea standard). Dacă firma dvs. nu a optat explicit pentru regimul cu plăți anticipate trimestriale, tratați cu prudență orice D100 generat pentru trimestrul IV și verificați cu un consultant fiscal dacă nu cumva situația dvs. se rezolvă exclusiv prin D101.

## Ce se greșește în practică

- Se așteaptă ca aplicația să semnaleze D100 restant pentru firmele pe profit, la fel ca la micro — nu se întâmplă, trebuie generat manual.
- Se ignoră termenul pentru că „nu apare nicio alertă", ceea ce duce direct la penalități de întârziere.
- Se calculează scadența trimestrului IV după regula generică „25 a lunii următoare" (adică 25 ianuarie anul următor) — regula corectă de scadență pentru micro trim. IV e 25 iunie anul următor, iar pentru profit cod 103 la luna 12 e 25 decembrie anul curent; niciuna din ele nu e 25 ianuarie.
- Se depune D100 cu bază de calcul zero sau negativă (pierdere cumulată) — structural, declarația nu poate fi generată fără cel puțin o obligație pozitivă.

## Ce face iConta.eu

`core/d100.py` calculează corect obligația cod 103, cu bază cumulată de la 1 ianuarie și scadență 25 a lunii următoare pentru trimestrele I-III. Totuși, `core/control_fiscal_api.py` adaugă D100 la lista de obligații urmărite doar pe ramura `regim == "micro"` (funcția `_adauga_d100_micro`); pe ramura `regim == "profit"` se adaugă automat numai D101 — D100 nu apare niciodată în „obligații"/„restanțe" pentru o firmă pe profit, deși motorul de calcul o suportă complet. Aceasta e o neconformitate deschisă (R95) în registrul intern al proiectului: generarea D100 pentru o firmă pe profit rămâne, pentru moment, un pas manual.

În plus, modulul de scadențar folosit de semafor (`core/scadente.py`) nu are o ramură specială pentru tipul „d100" și cade pe regula generică pentru trimestrul IV, care calculează 25 ianuarie anul următor — dată diferită de cea generată efectiv în XML-ul D100 (25 iunie pentru micro, 25 decembrie pentru profit). Dacă folosiți lista de termene/scadențe din aplicație pentru trimestrul IV, verificați suplimentar data reală din declarația generată, nu doar afișajul din semafor.

[iConta.eu](/)
