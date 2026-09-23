---
title: Cum se înregistrează activele achiziționate cu granturi
description: Activul cumpărat cu ajutorul unui grant se înregistrează normal, la valoarea de intrare, iar grantul se reflectă separat, ca subvenție pentru investiții, reluată treptat pe măsura amortizării.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se înregistrează activele achiziționate cu granturi

Un activ cumpărat cu ajutorul unui grant nu are o formulă contabilă specială pentru intrarea în gestiune — se înregistrează la fel ca orice mijloc fix, la valoarea de intrare. Grantul se ține separat, ca subvenție pentru investiții, cu propriul lui traseu de recunoaștere.

## Temeiul legal

::: ghid-temei
„Subvențiile aferente activelor reprezintă subvenții pentru acordarea cărora principala condiție este ca entitatea beneficiară să cumpere, să construiască sau să achiziționeze active imobilizate."
— OMFP 1802/2014, pct. 394 alin. (1)
:::

::: ghid-temei
„Subvențiile nu trebuie înregistrate direct în conturile de capital și rezerve deoarece acestea reprezintă sume acordate sub rezerva îndeplinirii anumitor condiții de către societate."
— OMFP 1802/2014, pct. 402 alin. (1)
:::

Practic, sunt două înregistrări distincte, care nu se amestecă:

1. **Activul**: intră în gestiune la valoarea lui de achiziție (de exemplu, `213 = 404` sau `213 = 512`, după cum a fost plătit), indiferent că finanțarea vine parțial sau integral dintr-un grant. Se amortizează normal, pe durata lui de utilizare.
2. **Grantul**: dreptul de a-l primi se înregistrează `445 = 4751`, încasarea `5121 = 445`, iar recunoașterea lui ca venit se face treptat, `4751 = 7584`, proporțional cu amortizarea activului finanțat — nu integral, la primirea banilor, și nu direct în capitaluri proprii.

Fiscal, la microîntreprindere, venitul din reluarea grantului (7584) se scade din baza impozabilă (art. 53 alin. (1) lit. d) din Codul fiscal); la impozitul pe profit nu există o scutire echivalentă.

## Ce se greșește în practică

- Se scade valoarea grantului din costul de intrare al activului, înregistrându-l „la net" — activul trebuie ținut la valoarea lui integrală de achiziție, iar grantul reflectat separat.
- Se recunoaște grantul integral ca venit la încasare, în loc să fie reluat treptat, pe măsura amortizării.
- Se înregistrează grantul direct într-un cont de rezerve/capital propriu, contrar OMFP 1802 pct. 402.

## Ce face iConta.eu

Operațiunile de mijloace fixe și cele de subvenții sunt separate în iConta.eu, exact ca în mecanismul de mai sus: activul se înregistrează prin ecranul dedicat de mijloace fixe, la valoarea lui integrală, iar grantul primit se reflectă prin ecranul „Subvenții (445/741)", cu opțiunea „Investiții (475)" — dreptul și încasarea funcționează normal din acest ecran. **Reluarea lunară proporțională cu amortizarea nu poate fi însă finalizată din același formular**: deși „Reluare la venituri" apare ca opțiune de „Fel", ecranul nu are câmpurile `valoare_activ`, `subventie` și `amortizare_lunara` pe care ruta le cere; la data acestei verificări, reluarea trebuie introdusă pe altă cale (API direct sau notă manuală calculată după formula `amortizare_lunară × subvenție / valoare_activ`). Aplicația nu leagă automat valoarea grantului de valoarea activului la intrare — corelarea celor două (procentul subvenționat, folosit la calculul reluării) trebuie făcută manual.

[iConta.eu](/)
