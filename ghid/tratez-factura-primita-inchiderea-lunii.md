---
title: "Cum tratez o factură primită după închiderea lunii?"
description: "Ce se întâmplă tehnic când o factură de furnizor ajunge după ce luna a fost deja blocată, și cum se înregistrează fără să redeschizi perioada."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez o factură primită după închiderea lunii?

Când o factură de furnizor ajunge la tine după ce luna respectivă a fost deja blocată contabil, nu ai nevoie automat de redeschiderea lunii — aplicația are un mecanism dedicat pentru corectarea la data descoperirii.

## Temeiul legal

::: ghid-temei
„Erorile constatate după depunerea situaţiilor financiare anuale se corectează la data constatării lor, potrivit reglementărilor contabile emise de instituţiile prevăzute la art. 4 alin. (1) şi (3), după caz." — Legea nr. 82/1991 (Legea contabilității), art. 36^2
:::

Acesta e cel mai direct temei identificat pentru principiul „se corectează la data descoperirii", pe care se bazează mecanismul tehnic descris mai jos.

## Ce se greșește în practică

- Se încearcă înregistrarea facturii direct la data ei de emitere, într-o lună deja blocată — operațiunea e respinsă la nivel de bază de date, indiferent de sursă (interfață, import, cron, rețetar).
- Se cere redeschiderea lunii ca primă reacție, deși pentru o singură factură uitată există o cale mai simplă: contarea la data descoperirii, în luna curentă (deschisă).
- Se ignoră faptul că, dacă factura respectivă a venit prin e-Factura, ea ar fi trebuit în mod normal semnalată **înainte** de închiderea lunii — sistemul refuză să blocheze o lună dacă mai există e-Facturi primite neînregistrate. Dacă totuși ai ajuns în această situație, cel mai probabil factura a sosit pe alt canal (fizic, email) și nu a fost prinsă de verificarea automată de la închidere.

## Ce face iConta.eu

Orice încercare de a scrie o notă contabilă (înregistrare) cu data în luna blocată e respinsă la nivelul bazei de date, printr-un trigger care verifică tabelul de perioade blocate pentru firmă — indiferent de canalul prin care vine înregistrarea. Mesajul afișat este: „Perioada e blocată (luna închisă). Cere-i administratorului cabinetului să o redeschidă sau înregistrează în luna curentă."

Pentru exact acest scenariu — o factură cu data în luna închisă — motorul de contare acceptă o dată explicită de înregistrare (`data_nota`): dacă luna emiterii facturii e blocată, nota poate fi scrisă la data descoperirii, în luna curentă (deschisă), cu o mențiune care documentează legătura dintre data reală a facturii și data la care a fost efectiv înregistrată. Dacă nu se dă explicit o dată de înregistrare și data facturii cade într-o lună blocată, aplicația refuză operațiunea cu eroare explicită, nu o lasă să „dispară" tăcut.

Alternativa — redeschiderea lunii — rămâne disponibilă pentru administratorul firmei, dar cere obligatoriu un motiv consemnat (nu se poate redeschide „doar ca să șterg"), pe temeiul intern citat în cod: „OMFP 1802/2014 — o perioadă închisă se redeschide ca act, nu prin ștergere." Fiecare blocare și deblocare rămâne în istoricul firmei.

[iConta.eu](/)
