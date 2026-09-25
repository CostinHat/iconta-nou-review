---
title: "La ce marjă de profit devine mai avantajos matematic impozitul micro față de profit?"
description: "Cotele de 1% (micro) și 16% (impozit pe profit) comparate aritmetic — și de ce pragul rezultat e un reper orientativ, nu o regulă legală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# La ce marjă de profit devine mai avantajos matematic impozitul micro față de profit?

Întrebarea revine des la alegerea regimului fiscal: dacă firma poate opta între impozitul pe veniturile microîntreprinderilor (aplicat pe venit) și impozitul pe profit (aplicat pe profit), la ce marjă de profit unul devine matematic mai avantajos decât celălalt? Răspunsul e o simplă comparație aritmetică între cele două cote — nu o regulă fixată de lege.

## Temeiul legal

::: ghid-temei
„Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— Cod fiscal (Legea 227/2015), art. 51 alin. (1), astfel cum a fost modificat prin OUG 89/2025 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
— Cod fiscal (Legea 227/2015), art. 17 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Comparația matematică, pas cu pas:

- Impozitul micro se aplică pe **venit** (V), cel pe profit se aplică pe **profit** (P = V × marjă). Egalând cele două sarcini fiscale: 1% × V = 16% × marjă × V, rezultă marjă = 1%/16% ≈ **6,25%**.
- Sub o marjă de profit de aproximativ 6,25%, impozitul micro (1% din venit) e matematic mai mic decât 16% din profit; peste acest prag, impozitul pe profit devine mai avantajos.
- Acesta e un calcul pur aritmetic pe cele două cote — nu ține cont de alte diferențe reale între regimuri: la micro nu se deduc cheltuielile (deci sarcina fiscală nu variază cu profitabilitatea reală sub prag), la impozitul pe profit baza se determină după deduceri, amortizări, rezerve legale, credite fiscale (sponsorizare, cercetare-dezvoltare) care pot coborî semnificativ impozitul efectiv sub 16% din profitul contabil.
- Condiția de eligibilitate pentru regimul micro (Cod fiscal art. 47) — venituri anuale care nu depășesc echivalentul în lei a 100.000 euro — rămâne o condiție separată de acest calcul: o firmă poate avea o marjă de profit foarte mare și tot să nu poată opta pentru micro dacă depășește plafonul de venituri.

## Ce se greșește în practică

- Se tratează pragul de 6,25% ca pe o regulă legală („legea spune că sub X% ești micro") — nu există; e strict rezultatul împărțirii celor două cote și ignoră deducerile fiscale reale.
- Se compară impozitul micro cu impozitul pe profit calculat pe profitul contabil brut, fără să se scadă cheltuielile nedeductibile/deductibile suplimentar, care pot modifica semnificativ baza reală de impozitare la profit.
- Se ignoră plafonul de venituri de 100.000 euro (art. 47 CF) — o firmă cu marjă mică de profit, dar venituri peste plafon, nu poate opta pentru micro indiferent de calculul de mai sus.
- Se presupune că trecerea de la un regim la altul se poate face oricând în cursul anului, fără să se verifice regulile de ieșire/intrare din regimul micro (art. 52 CF).

## Ce face iConta.eu

Subiectul nu are nicio legătură cu funcționalitatea **Jurnal regim marjă** (raportul care grupează vânzările în regimul special de marjă TVA pentru bunuri second-hand și agenții de turism, conform art. 312/311 Cod fiscal) — „marjă" înseamnă aici altceva: marja de profit a firmei, un concept de impozit pe profit/impozit micro, nu de TVA. E o capcană de omonim: „regim de marjă" (TVA) și „marjă de profit" (impozit pe profit vs. micro) nu au nimic în comun în lege sau în cod.

Verificat direct în aplicație: nu există niciun modul care să calculeze sau să compare automat impozitul micro cu impozitul pe profit pentru a recomanda un regim — căutarea explicită a arătat că aplicația **nu urmărește** plafonul de ieșire din regimul micro (nicio constantă de plafon în cod) și tratează regimul fiscal (`regim_fiscal`) strict ca pe un câmp completat manual de contabil, nu ca pe un rezultat al unui calcul intern. Comparația de mai sus e, deci, un instrument didactic de folosit înainte de a alege regimul, nu o funcție a aplicației.

[iConta.eu](/)
