---
title: "Cum se recunoaște venitul din subvenție aferent amortizării?"
description: Venitul din subvenția pentru investiții se recunoaște lunar, prin reluarea din 4751 în 7584, proporțional cu amortizarea activului finanțat — nu ca sumă fixă și nu integral, la încasare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se recunoaște venitul din subvenție aferent amortizării?

Venitul dintr-o subvenție pentru investiții nu apare o singură dată, la încasare. El se recunoaște lunar, pe măsură ce activul finanțat se amortizează, printr-o formulă legată direct de amortizarea acelui activ.

## Temeiul legal

::: ghid-temei
„Subvențiile se recunosc, pe o bază sistematică, drept venituri ale perioadelor corespunzătoare cheltuielilor aferente pe care aceste subvenții urmează să le compenseze."
— OMFP 1802/2014, pct. 398 alin. (1)
:::

::: ghid-temei
„Subvențiile legate de activele amortizabile sunt recunoscute, de regulă, în contul de profit și pierdere pe parcursul perioadelor și în proporția în care amortizarea acelor active este recunoscută."
— OMFP 1802/2014, pct. 399 alin. (1)
:::

Formula contabilă e `4751 = 7584` (Subvenții guvernamentale pentru investiții → Venituri din subvenții pentru investiții), iar suma lunară se calculează astfel:

`venit_lunar = amortizare_lunară × (valoare_subvenționată / valoare_activ)`

Adică amortizarea lunară a activului, înmulțită cu procentul din valoarea lui acoperit de subvenție. Dacă activul e cedat înainte de amortizarea integrală, soldul rămas în 4751 se reia integral la venituri în acel moment, nu se pierde și nu rămâne suspendat.

Fiscal, acest venit (contul 7584) se scade din baza impozabilă a impozitului pe veniturile microîntreprinderilor (art. 53 alin. (1) lit. d) din Codul fiscal), dar rămâne impozabil la calculul impozitului pe profit, unde nu există o scutire echivalentă pentru veniturile din subvenții.

## Ce se greșește în practică

- Se recunoaște întreaga subvenție ca venit la data încasării banilor, nu treptat, pe durata amortizării.
- Se folosește o sumă lunară fixă, aleasă arbitrar, în loc de calculul proporțional cu amortizarea efectivă și cu procentul subvenționat.
- Se scade venitul din reluare (7584) din baza impozabilă și la impozitul pe profit, unde legea nu prevede o asemenea scutire.

## Ce face iConta.eu

Motorul din spatele acestei operații (`reluare_lunara_investitii(valoare_activ, subventie, amortizare_lunara)`) calculează exact formula de mai sus. **Dar, la data acestei verificări, ecranul „Subvenții (445/741)" nu expune câmpurile pentru valoarea activului, subvenție și amortizarea lunară** — opțiunea „Reluare la venituri" există în lista de „Fel", însă formularul standard cere doar dată, sumă, moment și descriere, fără cele trei valori necesare calculului, deci operația nu poate fi dusă la capăt din ecran. Până la o corectare, reluarea lunară trebuie introdusă manual, prin altă cale (API direct sau notă de jurnal calculată separat cu formula de mai sus). La declarația unificată (regimul microîntreprindere), verifică manual, conform art. 53 alin. (1) lit. d), că suma reluată în perioada raportată a fost scăzută din baza impozabilă înainte de depunere.

[iConta.eu](/)
