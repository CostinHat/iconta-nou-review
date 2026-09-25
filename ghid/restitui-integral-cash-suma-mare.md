---
title: "Se poate restitui integral cash o sumă mai mare decât plafonul?"
description: "Excepția din Legea nr. 70/2015 care permite restituirea integrală în numerar către o persoană fizică fără cont bancar, peste plafonul obișnuit de 10.000 lei."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Se poate restitui integral cash o sumă mai mare decât plafonul?

Regula generală limitează restituirile în numerar către persoane fizice la 10.000 lei, dar legea prevede o excepție clară pentru situația în care persoana nu mai are cont bancar la data restituirii.

## Temeiul legal

::: ghid-temei
„În cazul returnării de bunuri de către persoanele fizice și, respectiv, neprestării de servicii către persoanele fizice, restituirea sumelor aferente poate fi efectuată în numerar în limita a 10.000 lei, sumele care depășesc acest plafon putând fi restituite numai prin instrumente de plată fără numerar. Prin excepție, în cazul în care, la data restituirii, persoanele fizice declară pe propria răspundere că nu mai dețin cont bancar, restituirea se poate face integral în numerar, indiferent de nivelul sumei care trebuie restituită."
— Legea nr. 70/2015, art. 9 alin. (2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Ce rezultă concret:

- Regula standard: restituirea către o persoană fizică (marfă returnată, serviciu neprestat) se face în numerar doar până la 10.000 lei; ce depășește acest prag trebuie plătit prin instrument fără numerar (transfer bancar, card etc.).
- Excepția: dacă la data restituirii persoana fizică **declară pe propria răspundere** că nu mai deține cont bancar, restituirea se poate face **integral** în numerar, oricât de mare ar fi suma — plafonul de 10.000 lei nu se mai aplică.
- Declarația pe propria răspundere e condiția obligatorie a excepției — fără ea, entitatea nu are temei să depășească plafonul, chiar dacă bănuiește sau știe informal că persoana nu are cont.
- Regula e diferită de cea aplicabilă între profesioniști (art. 9 alin. (1)), unde plafoanele sunt 5.000 lei, respectiv 10.000 lei pentru cash and carry, fără această excepție pentru lipsa contului bancar.

## Ce se greșește în practică

- Se restituie integral în numerar orice sumă mare, fără a cere și păstra declarația scrisă pe propria răspundere a persoanei fizice privind lipsa contului bancar — la un control, absența acestui document lasă restituirea fără temeiul excepției.
- Se aplică excepția și în relația cu alți profesioniști (firme, PFA-uri), deși art. 9 alin. (2) vizează explicit doar persoanele fizice, în calitate de cumpărători/beneficiari.
- Se confundă plafonul de restituire (art. 9) cu plafonul general de plăți către persoane fizice din altă parte a legii — sunt prevederi diferite, cu praguri și condiții proprii.

## Ce face iConta.eu

iConta.eu semnalează în modulul de casierie (`core/casa.py`, funcția `verifica_plafon`) depășirile plafoanelor de numerar ca avertismente, cu temeiul legal atașat fiecărei probleme — dar aplicația nu are, la data acestui ghid, un câmp dedicat pentru „declarație pe propria răspundere fără cont bancar" care să marcheze automat o restituire ca exceptată de la plafon. Excepția din art. 9 alin. (2) rămâne, deocamdată, o verificare manuală a contabilului, documentată în afara aplicației.

[iConta.eu](/)
