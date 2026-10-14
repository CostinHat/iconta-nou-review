---
title: "Cum verific calculul impozitului pe profit înainte de închiderea trimestrului?"
description: "Verificarea trimestrială a impozitului pe profit se face prin D100, nu prin D101, care rămâne exclusiv declarația anuală de definitivare."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Cum verific calculul impozitului pe profit înainte de închiderea trimestrului?

Un lucru trebuie clarificat de la început: D101 nu este instrumentul pentru verificarea trimestrială — aceasta se face prin D100.

## Temeiul legal

::: ghid-temei
„Calculul, declararea și plata impozitului pe profit, cu excepțiile prevăzute de prezentul articol, se efectuează trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III. Definitivarea și plata impozitului pe profit aferent anului fiscal respectiv se efectuează până la termenul de depunere a declarației privind impozitul pe profit prevăzut la art. 42.”
— Legea nr. 227/2015 privind Codul fiscal, art. 41 alin. (1) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Contribuabilii care aplică sistemul de declarare și plată a impozitului pe profit anual, cu plăți anticipate efectuate trimestrial, determină plățile anticipate trimestriale în sumă de o pătrime din impozitul pe profit datorat pentru anul precedent, actualizat cu indicele prețurilor de consum [...]”
— Legea nr. 227/2015 privind Codul fiscal, art. 41 alin. (8) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„(10^1) Prin excepție de la prevederile alin. (8) , plata anticipată pentru trimestrul I al fiecărui an fiscal/an fiscal modificat se calculează prin aplicarea cotei de impozit asupra profitului contabil al perioadei pentru care se efectuează plata anticipată. Aceasta se declară și se plătește până la data de 25 inclusiv a lunii următoare trimestrului I.”
— Legea nr. 227/2015 privind Codul fiscal, art. 41 alin. (10^1) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor [...]”
— Legea nr. 227/2015 privind Codul fiscal, art. 42 alin. (1) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Plățile trimestriale/anticipate de impozit pe profit (cod de obligație 103) se depun prin D100, nu prin D101 — confirmat de nomenclatorul „codul bugetar” din aplicație. D101 este, în toate cazurile, exclusiv declarația ANUALĂ de definitivare.

Dacă firma a optat pentru sistemul anual cu plăți anticipate trimestriale (art.41 alin.(2)), plățile anticipate reprezintă 1/4 din impozitul anului precedent, actualizat cu indicele prețurilor de consum (art.41 alin.(8)) — nu un calcul recalculat de la zero în fiecare trimestru. Excepție, începând cu anul fiscal 2026: plata anticipată pentru trimestrul I se calculează aplicând cota de impozit asupra profitului contabil al trimestrului I (art.41 alin.(10^1), introdus prin OUG 8/2026), nu ca o pătrime din impozitul anului precedent. Aplicația calculează în D100 impozitul pe profit în sistemul trimestrial (cumulat de la începutul anului); plățile anticipate din sistemul anual nu sunt calculate de aplicație.

## Ce se greșește în practică

Greșeala tipică e căutarea unei funcții de „verificare trimestrială" în motorul D101 — aceasta nu există, pentru că D101 nu operează la nivel trimestrial. Verificarea propriu-zisă a sumei datorate trimestrial ține de fluxul D100.

## Ce face iConta.eu

Pentru definitivarea anuală, D101 validează identitatea firmei („verificarea datelor înainte de generare (Declarații)”) și rulează reconciliere independentă a bazei contabile la generare. Pentru verificări trimestriale, fluxul relevant din aplicație este D100, cu codul de obligație 103.

[iConta.eu](/)
