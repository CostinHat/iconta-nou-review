---
title: Cum se face plata impozitului pe profit la bugetul de stat?
description: Impozitul pe profit calculat prin D100 (cota 16%) se achită în contul bugetar unic 5503, identificat pe declarație prin numărul de evidență a plății (nr_evid).
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se face plata impozitului pe profit la bugetul de stat?

După ce D100 e generată corect, rămâne pasul plății efective — iar aici greșeala tipică nu ține de sumă, ci de contul bugetar folosit sau de identificarea corectă a plății.

## Temeiul legal

::: ghid-temei
**CF art. 17:**
> „Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.html`

**OPANAF 587/2016, Anexa 4, Cap. I, pct. 1.2 lit. c):**
> „Trimestrial, pentru obligațiile de plată reprezentând: ... c) impozitul pe profit datorat de persoane
> juridice române și persoanele juridice străine, altele decât cele prevăzute la lit. a) și b), precum și
> de către persoanele juridice cu sediul social în România, înființate potrivit legislației europene
> (trimestrele I-III);"
— sursă: `anaf_surse/opanaf_587_2016_aprobarea_modelului_continutului_formularelor_utilizate.txt:927-930`

**Structura tehnică D100 — cont bugetar unic:**
> „Atenție ! Se va inlocui peste tot contul bugetar 20470101 cu 5503 ! (data modificării 26.07.2018)"
— sursă: `anaf_surse/d100_struct_anaf.txt:562`
:::

## Contul corect și identificarea plății

Din 26 iulie 2018, contul bugetar vechi (20470101) a fost înlocuit oficial cu contul unic **5503XXXXXX**, valabil deopotrivă pentru impozitul pe profit (cod 103) și pentru impozitul micro (cod 121). Orice ordin de plată emis pe vechiul cont riscă să nu fie asociat corect cu obligația declarată.

Plata trebuie identificată corect prin numărul de evidență a plății (nr_evid) generat odată cu declarația — un cod de 23 de caractere care conține, printre altele, codul obligației (poz. 3-5), perioada de raportare (poz. 8-11, format LLAA) și data scadenței (poz. 12-17, format ZZLLAA). Acest cod leagă plata de exact obligația și perioada declarate, deci trebuie preluat din declarația generată, nu reconstruit manual.

## Ce se greșește în practică

- Se plătește în contul vechi 20470101, deși din 2018 contul valabil este 5503XXXXXX.
- Se face plata fără a atașa/menționa numărul de evidență a plății (nr_evid) generat de declarație, ceea ce poate întârzia asocierea corectă a plății cu obligația.
- Se confundă contul sau codul de identificare cu cel al altei obligații (de exemplu, TVA sau contribuții), deși contul bugetar 5503 e specific obligațiilor acoperite de D100.
- Se plătește o sumă rotunjită sau estimată, diferită de suma exactă rezultată din calculul cu cota de 16% aplicată bazei cumulate.

## Ce face iConta.eu

Nomenclatorul cod→cont bugetar din `core/d100.py` (`COD_BUGETAR`, liniile 54-63) conține exclusiv cele două obligații pe care aplicația le generează — cod 103 (profit) și cod 121 (micro) — ambele mapate la contul unic 5503XXXXXX. Orice alt cod de obligație transmis ridică explicit o eroare, nu se emite tăcut fără cont bugetar asociat. Numărul de evidență a plății (nr_evid, 23 de caractere) este derivat direct din aceeași dată de scadență calculată pentru declarație, nu recalculat independent — eliminând riscul ca cele două să diveargă atunci când scadența e determinată corect de generator.

[iConta.eu](/)
