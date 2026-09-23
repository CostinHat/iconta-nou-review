---
title: "Greșeala de a nu depune D205 la timp"
description: "Termenul de depunere a declarației D205 este diferit de termenul de virare a impozitului pe dividende, iar confuzia dintre ele este o greșeală frecventă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Greșeala de a nu depune D205 la timp

D205 este o declarație informativă anuală, cu un termen propriu de depunere — distinct de termenul lunar de virare a impozitului pe dividende. Confundarea celor două date este una dintre cele mai frecvente cauze de depunere întârziată.

## Temeiul legal

::: ghid-temei
"5. Termenul de depunere a declarației [...] a) până în ultima zi a lunii februarie inclusiv a anului curent pentru anul expirat."
— OPANAF 179/2022 (baza legală pentru formularele D205 și D207)
:::

Acesta este termenul de depunere a declarației informative D205 — diferit de termenul de virare a impozitului (25 a lunii următoare plății, respectiv 25 ianuarie pentru dividendele distribuite dar neplătite până la sfârșitul anului, conform art. 97 alin. (7) din Codul fiscal). Cele două date nu trebuie confundate.

## Ce se greșește în practică

Greșeala tipică este tratarea termenului de virare a impozitului (lunar, 25 a lunii următoare plății) ca fiind și termenul de depunere a declarației D205, ceea ce duce fie la depunerea prematură, cu date incomplete pentru tot anul, fie — mai grav — la omiterea depunerii D205 până la finalul lunii februarie, pentru că firma consideră eronat că obligația a fost deja "rezolvată" prin virările lunare de impozit.

O a doua sursă de întârziere, mai gravă, ține de un gol identificat în modul de generare: un dividend distribuit (aprobat) dar neplătit până la 31 decembrie nu apare automat printre beneficiarii calculați pentru declarația anului respectiv, deși instrucțiunile oficiale de completare prevăd explicit că impozitul aferent unui astfel de dividend "se cuprinde în declarația aferentă perioadei în care s-a aprobat distribuirea dividendelor". Dacă acest beneficiar nu este adăugat manual, D205 se depune la timp, dar incomplet.

## Ce face iConta.eu

Declarația D205 se generează automat din asociați (cotă și CNP) și din notele contabile validate pe contul 457, cu XML validat conform structurii oficiale. Pentru cazul dividendelor distribuite într-un an anterior și plătite ulterior, aplicația calculează corect impozitul la cota de la data distribuirii.

Pentru cazul distribuit-dar-neplătit la 31 decembrie: la data acestei verificări, generatorul de D205 filtrează beneficiarii după suma efectiv plătită, astfel încât un dividend doar distribuit (fără nicio plată) nu produce automat un beneficiar în declarație. Dacă acest caz apare, contabilul trebuie să introducă manual beneficiarul respectiv (opțiunea de beneficiari introduși manual la generare), altfel riscă să depună D205 la termen, dar fără acea obligație inclusă.

[iConta.eu](/)
