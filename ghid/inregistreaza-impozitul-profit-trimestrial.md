---
title: Cum se înregistrează impozitul pe profit trimestrial?
description: Sistemul implicit e calcul, declarare și plată trimestrială, cu termen 25 ale lunii următoare fiecărui trimestru I-III, declarat prin D100 (nu D101). Firma poate opta pentru plăți anticipate anuale, dar unele categorii sunt obligate la trimestrial.
published: 2026-09-25
modified: 2026-10-13
poarta: v1
---

# Cum se înregistrează impozitul pe profit trimestrial?

Regula implicită din Codul fiscal e calcul, declarare și plată trimestrială a impozitului pe profit, pentru fiecare din trimestrele I–III, cu definitivare anuală separată.

## Temeiul legal

::: ghid-temei
**Art. 41 alin. (1) din Codul fiscal** (fragment): calculul, declararea și plata impozitului pe profit se fac trimestrial, „până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III".
„(10^1) Prin excepție de la prevederile alin. (8) , plata anticipată pentru trimestrul I al fiecărui an fiscal/an fiscal modificat se calculează prin aplicarea cotei de impozit asupra profitului contabil al perioadei pentru care se efectuează plata anticipată. Aceasta se declară și se plătește până la data de 25 inclusiv a lunii următoare trimestrului I.”
— Legea nr. 227/2015 privind Codul fiscal, art. 41 alin. (10^1) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

## Mecanismul

Pentru fiecare trimestru (I, II, III): se calculează impozitul aferent, se înregistrează contabil (691 = 441) și se declară/plătește până la 25 ale lunii următoare, prin **D100**, la obligația bugetară cu cod 103 — D101 nu intervine în acest ciclu, fiind exclusiv declarația anuală de definitivare.

Există și o opțiune (art. 41 alin. 2) pentru sistemul anual, cu plăți anticipate trimestriale egale cu un sfert din impozitul anului precedent, actualizat cu indicele prețurilor de consum (art. 41 alin. 8). De la anul fiscal 2026 există o excepție pentru trimestrul I: plata anticipată pentru trimestrul I nu mai este un sfert din impozitul anului precedent, ci se calculează aplicând cota de impozit asupra profitului contabil al trimestrului I (art. 41 alin. 10^1, introdus prin OUG nr. 8/2026). Opțiunea se exercită la începutul anului fiscal, e obligatorie minimum doi ani fiscali consecutivi și se comunică organului fiscal până la 31 ianuarie inclusiv (art. 41 alin. 3).

Unele categorii de contribuabili nu pot opta pentru anual și rămân obligate la sistemul trimestrial: firmele nou-înființate, cele cu pierdere fiscală în anul precedent, cele în inactivitate temporară sau cele foste plătitoare de impozit pe veniturile microîntreprinderilor, în anul imediat următor schimbării de regim (art. 41 alin. 5 lit. c și alin. 6).

## Ce se greșește în practică

Se calculează plata trimestrială, dar se declară prin D101 în loc de D100 — D101 nu are rol în raportarea trimestrială, e exclusiv declarația de definitivare anuală. A doua greșeală: se optează pentru sistemul anual fără verificarea prealabilă a categoriei firmei (firmă nouă, fostă micro, cu pierdere fiscală anterioară) — categoriile enumerate mai sus nu pot opta, indiferent de cerere.

## Ce face iConta.eu

D100 gestionează plățile trimestriale de impozit pe profit (sistemul trimestrial, cu impozitul calculat cumulat de la începutul anului) prin obligația cu cod bugetar 103, separat de impozitul micro (cod 121). Aplicația nu calculează plățile anticipate din sistemul anual (nici sfertul din impozitul anului precedent, nici plata pentru trimestrul I pe profitul contabil) — pentru o firmă care a optat pentru sistemul anual, suma lor rămâne în sarcina contabilului. Dacă apare o eroare într-o declarație trimestrială deja depusă, aceasta se poate corecta prin D710, motor dedicat de rectificativă pentru obligațiile declarate prin D100 — spre deosebire de D101, care nu are în prezent un mecanism echivalent de rectificativă în aplicație.

[iConta.eu](/)
