---
title: "Anularea unei chitanțe emise din greșeală"
description: "Ce prevede legea pentru o chitanță întocmită greșit — anulare, nu corectare prin ștersătură — și de ce iConta.eu nu automatizează azi acest pas."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Anularea unei chitanțe emise din greșeală

Cui nu i s-a întâmplat să scrie o sumă greșită pe o chitanță, sau să o emită pe numele clientului nepotrivit? Regula contabilă pentru acest caz nu e „se taie cu o linie și se scrie deasupra", ca la majoritatea documentelor — chitanța face parte dintr-o categorie specială, cu propria ei procedură.

## Temeiul legal

::: ghid-temei
„În cazul documentelor financiar-contabile la care nu se admit corecturi, cum sunt cele pe baza cărora se primește, se eliberează sau se justifică numerarul [...] documentul întocmit greșit se anulează și se păstrează sau rămâne în carnetul respectiv."
— OMFP 2634/2015, Anexa 1 „Norme generale", pct. 15 (sursă: anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt)
:::

- Chitanța e un document „pe baza căruia se primește, se eliberează sau se justifică numerarul" — deci intră expres în categoria documentelor **la care nu se admit corecturi** prin tăiere și rescriere (regula generală de la pct. 14 din aceleași norme).
- Soluția legală e alta: chitanța greșită **se anulează** (de regulă cu mențiunea „ANULAT" pe exemplar) și **se păstrează** — fie în carnetul din care a fost ruptă, fie în arhiva documentelor emise electronic, dacă seria e ținută pe calculator.
- Chitanța corectă se întocmește separat, cu următorul număr disponibil din serie — numerotarea secvențială, odată alocată unui număr, nu se „reutilizează" pentru documentul anulat.

## Ce se greșește în practică

- Se încearcă „repararea" chitanței greșite prin tăierea sumei și rescrierea alteia deasupra, ca la o factură sau la o notă obișnuită — exact procedeul pe care norma îl exclude pentru documentele de numerar.
- Chitanța anulată e aruncată, în loc să fie păstrată alături de celelalte documente ale seriei — la un control, un „gol" în numerotare fără document anulat justificativ ridică întrebări.
- Se emite o chitanță nouă fără să se anuleze explicit cea greșită, lăsând două documente valabile în aparență pentru aceeași operațiune.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are o funcție de anulare** pentru chitanțele deja emise. Emiterea (`chitanta_emite`) alocă un număr secvențial nou pe seria firmei, generează PDF-ul cu suma în litere și înregistrează operațiunea în Registrul de casă (5311=4111); verificat în cod, nu există nicio rută sau funcție care să marcheze o chitanță drept anulată sau să șteargă rândul creat. Practic, o chitanță emisă greșit din aplicație rămâne activă în listă și în Registrul de casă — corectarea ei, conform normei de mai sus, trebuie gestionată azi manual, în afara aplicației (de exemplu printr-o notă către contabil și, dacă e cazul, o operațiune de stornare a înregistrării de casă generate).

[iConta.eu](/)
