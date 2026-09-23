---
title: "Cum se înregistrează un mijloc fix cumpărat din fonduri nerambursabile?"
description: Mijlocul fix se înregistrează la valoarea lui integrală, ca orice achiziție, iar fondurile nerambursabile care l-au finanțat se reflectă separat, ca subvenție pentru investiții.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se înregistrează un mijloc fix cumpărat din fonduri nerambursabile?

Fondurile nerambursabile primite pentru cumpărarea unui mijloc fix se tratează, contabil, ca o subvenție pentru investiții — indiferent dacă sursa e un program guvernamental sau unul european. Mijlocul fix și subvenția se înregistrează separat, cu propriile lor formule.

## Temeiul legal

::: ghid-temei
„Subvențiile aferente activelor reprezintă subvenții pentru acordarea cărora principala condiție este ca entitatea beneficiară să cumpere, să construiască sau să achiziționeze active imobilizate."
— OMFP 1802/2014, pct. 394 alin. (1)
:::

::: ghid-temei
„Subvențiile se recunosc, pe o bază sistematică, drept venituri ale perioadelor corespunzătoare cheltuielilor aferente pe care aceste subvenții urmează să le compenseze."
— OMFP 1802/2014, pct. 398 alin. (1)
:::

Pașii:

1. Mijlocul fix se înregistrează la valoarea integrală de achiziție (de exemplu `213 = 404`), indiferent cât din preț a fost acoperit din fonduri nerambursabile.
2. Dreptul de a primi fondurile: `445 = 4751`. Încasarea: `5121 = 445`.
3. Recunoașterea ca venit se face treptat, pe măsura amortizării mijlocului fix: `4751 = 7584`, proporțional cu partea finanțată din valoarea activului — nu integral, la încasare.

Fiscal, la microîntreprindere, venitul din reluare (7584) se scade din baza impozabilă (art. 53 alin. (1) lit. d) din Codul fiscal). La impozitul pe profit, veniturile din subvenții nu beneficiază de o scutire similară.

## Ce se greșește în practică

- Se înregistrează mijlocul fix „la valoarea netă" (preț minus fonduri nerambursabile), în loc de valoarea lui integrală de achiziție.
- Se recunoaște tot venitul din fonduri nerambursabile odată, la primirea banilor, nu eșalonat pe durata amortizării.
- Se confundă fondurile nerambursabile pentru un activ (subvenție de investiții, cont 4751/7584) cu o subvenție pentru cheltuieli curente (subvenție de exploatare, cont 741) — cele două au mecanisme diferite.

## Ce face iConta.eu

Mijlocul fix cumpărat din fonduri nerambursabile se înregistrează prin ecranul de mijloace fixe, la valoarea integrală. Fondurile primite se reflectă separat, prin ecranul „Subvenții (445/741)", opțiunea „Investiții (475)" — dreptul și încasarea funcționează din acest ecran. Reluarea lunară proporțională cu amortizarea nu poate fi însă finalizată din același formular: la data acestei verificări, deși „Reluare la venituri" apare ca opțiune de „Fel", ecranul nu expune câmpurile `valoare_activ`, `subventie` și `amortizare_lunara` cerute de operație — reluarea trebuie introdusă pe altă cale (API direct sau notă manuală). Aplicația nu are o rută unică care să lege automat cele două operațiuni; corelarea lor (procentul finanțat, folosit la calculul reluării) se face manual, la introducerea datelor.

[iConta.eu](/)
