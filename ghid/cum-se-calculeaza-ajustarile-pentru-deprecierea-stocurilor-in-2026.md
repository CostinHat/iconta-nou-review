---
title: Cum se calculează ajustările pentru deprecierea stocurilor în 2026?
description: Ajustarea de depreciere a stocurilor se calculează ca diferență între valoarea contabilă și valoarea realizabilă netă (preț de vânzare estimat minus costuri de finalizare și de vânzare), dar rămâne nedeductibilă fiscal necondiționat — nu apare în lista limitativă a CF art. 26.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se calculează ajustările pentru deprecierea stocurilor în 2026?

La fiecare inventariere, stocurile se evaluează la cost, mai puțin ajustările pentru depreciere constatate. Când valoarea contabilă a unui stoc depășește valoarea pe care firma poate realmente să o obțină din vânzarea lui, diferența se recunoaște ca ajustare pentru depreciere — indiferent dacă stocul e cu mișcare sau fără mișcare.

## Temeiul legal

::: ghid-temei
"Activele de natura stocurilor se evaluează la cost, mai puțin ajustările pentru depreciere constatate.
Ajustări pentru depreciere se constată inclusiv pentru stocurile fără mișcare. În cazul în care
valoarea contabilă a stocurilor este mai mare decât valoarea de inventar, valoarea stocurilor se
diminuează până la valoarea realizabilă netă, prin constituirea unei ajustări pentru depreciere."

"În înțelesul prezentelor reglementări, prin valoare realizabilă netă a stocurilor se înțelege prețul
de vânzare estimat care ar putea fi obținut pe parcursul desfășurării normale a activității, minus
costurile estimate pentru finalizarea bunului, atunci când este cazul, și costurile estimate necesare
vânzării."
:::

## Formula de calcul

Ajustarea = valoarea contabilă a stocului − valoarea realizabilă netă, unde:

**Valoare realizabilă netă = preț de vânzare estimat − costuri estimate de finalizare − costuri estimate de vânzare**

::: ghid-exemplu
Un lot de marfă are valoarea contabilă (cost de achiziție) de 40.000 lei. La inventariere, se estimează că poate fi vândut cu 32.000 lei, iar costurile de vânzare (transport, comisioane) sunt estimate la 2.000 lei. Valoarea realizabilă netă = 32.000 − 2.000 = 30.000 lei. Ajustarea de constituit = 40.000 − 30.000 = 10.000 lei, înregistrată 6814 = 397.
:::

## Ce se greșește în practică

- Se compară valoarea contabilă direct cu prețul de vânzare estimat, fără să se scadă costurile de finalizare și de vânzare — asta supraestimează valoarea realizabilă netă și subevaluează ajustarea necesară.
- Se omit stocurile fără mișcare de la evaluare, deși reglementarea cere expres constatarea ajustării și pentru acestea.
- Se tratează ajustarea de stoc ca deductibilă fiscal, prin analogie cu ajustările de creanțe — CF art. 26 nu include ajustările pentru deprecierea stocurilor în lista limitativă de provizioane/ajustări deductibile, deci rămân nedeductibile necondiționat, oricât de bine documentat e calculul.
- Se reevaluează ajustarea o singură dată, la constituire, fără revizuire la fiecare bilanț ulterior, deși reglementările cer ajustarea la cea mai bună estimare curentă la fiecare dată de raportare.

## Ce face iConta.eu

Funcția `nota_ajustare_stoc(suma, cont_ajustare, actiune)` din `core/provizioane.py` generează nota contabilă de constituire (6814 = 39x) și de reluare (39x = 7814), validând doar că `cont_ajustare` începe cu prefixul "39" (grupa de conturi "Ajustări pentru deprecierea stocurilor și producției în curs de execuție"). Aplicația marchează necondiționat `deductibil: False` pentru orice ajustare de stoc, în acord cu lipsa unui temei de deducere la art. 26. Calculul propriu-zis al valorii realizabile nete (preț estimat minus costuri de finalizare și de vânzare) e o estimare de gestiune, făcută în afara motorului, pe baza datelor de inventariere.

[iConta.eu](/)
