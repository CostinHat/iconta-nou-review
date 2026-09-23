---
title: "Cum se înregistrează contabil un mijloc fix primit prin proiect european?"
description: Mijlocul fix obținut printr-un proiect european se înregistrează la valoarea lui integrală, ca orice activ, iar finanțarea europeană se ține separat, ca subvenție pentru investiții.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se înregistrează contabil un mijloc fix primit prin proiect european?

Un mijloc fix obținut în cadrul unui proiect european — fie cumpărat direct de firmă cu finanțare rambursată ulterior, fie decontat prin proiect — se înregistrează la valoarea lui integrală, exact ca orice altă achiziție de mijloc fix. Finanțarea europeană se ține separat, ca subvenție pentru investiții.

## Temeiul legal

::: ghid-temei
„Subvențiile aferente activelor reprezintă subvenții pentru acordarea cărora principala condiție este ca entitatea beneficiară să cumpere, să construiască sau să achiziționeze active imobilizate."
— OMFP 1802/2014, pct. 394 alin. (1)
:::

::: ghid-temei
„Contabilitatea proiectelor finanțate din subvenții se ține distinct, pe fiecare proiect, sursă de finanțare, potrivit contractelor încheiate, fără a se întocmi situații financiare anuale distincte pentru fiecare asemenea proiect."
— OMFP 1802/2014, pct. 397 alin. (1)
:::

Practic:

1. Mijlocul fix intră în gestiune la valoarea integrală de achiziție, indiferent de sursa banilor.
2. Finanțarea europeană se înregistrează separat: dreptul de a o primi `445 = 4751`, încasarea `5121 = 445`.
3. Se reia la venituri treptat, `4751 = 7584`, proporțional cu amortizarea lunară a activului finanțat.

Contabilitatea proiectului se ține distinct, pe sursa de finanțare, dar asta nu înseamnă situații financiare separate — doar evidență analitică pe proiect, în paralel cu contabilitatea generală a firmei. Fiscal, la microîntreprindere, venitul din reluare (7584) se scade din baza impozabilă (art. 53 alin. (1) lit. d) din Codul fiscal); la impozitul pe profit rămâne impozabil.

## Ce se greșește în practică

- Se așteaptă decontarea integrală a proiectului înainte de a înregistra activul, deși activul trebuie recunoscut la intrarea lui efectivă în gestiune, indiferent de stadiul decontării.
- Se recunoaște finanțarea europeană integral ca venit la primire, nu eșalonat pe durata amortizării activului.
- Se ține evidența proiectului doar în afara contabilității (într-un tabel separat), fără analitică distinctă în conturile firmei, contrar pct. 397.

## Ce face iConta.eu

Mijlocul fix se înregistrează prin ecranul obișnuit de mijloace fixe, la valoarea integrală. Finanțarea europeană se reflectă separat, prin ecranul „Subvenții (445/741)", opțiunea „Investiții (475)" — dreptul și încasarea funcționează din acest ecran. Reluarea lunară proporțională cu amortizarea nu poate fi însă finalizată din același formular: la data acestei verificări, opțiunea „Reluare la venituri" apare în listă, dar ecranul nu are câmpurile `valoare_activ`, `subventie` și `amortizare_lunara` cerute de operație — reluarea trebuie introdusă pe altă cale (API direct sau notă manuală). Aplicația nu are un ecran dedicat de „proiect european" cu evidență analitică separată pe surse de finanțare — dacă contractul de finanțare îți cere raportare distinctă pe proiect, aceasta trebuie ținută separat, în completarea notelor generate aici.

[iConta.eu](/)
