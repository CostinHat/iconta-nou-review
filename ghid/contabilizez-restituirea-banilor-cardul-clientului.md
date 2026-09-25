---
title: "Cum contabilizez restituirea banilor pe cardul clientului?"
description: "Limitele legale pentru restituirea în numerar a sumelor către clienți persoane fizice, conform Legii 70/2015 privind disciplina financiară."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum contabilizez restituirea banilor pe cardul clientului?

Când un client returnează un produs sau renunță la un serviciu neprestat, întrebarea „îi dau banii cash sau pe card?" nu e doar o preferință operațională — legea limitează explicit restituirea în numerar peste un anumit plafon.

## Temeiul legal

::: ghid-temei
„(2) În cazul returnării de bunuri de către persoanele fizice și, respectiv, neprestării de servicii către persoanele fizice, restituirea sumelor aferente poate fi efectuată în numerar în limita a 10.000 lei, sumele care depășesc acest plafon putând fi restituite numai prin instrumente de plată fără numerar. Prin excepție, în cazul în care, la data restituirii, persoanele fizice declară pe propria răspundere că nu mai dețin cont bancar, restituirea se poate face integral în numerar, indiferent de nivelul sumei care trebuie restituită."
— Legea 70/2015, art. 9 alin. (2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Practic, regula e:

- Restituirea către o **persoană fizică**, pentru bunuri returnate sau servicii neprestate, se poate face **în numerar doar până la 10.000 lei**.
- Peste acest plafon, restituirea trebuie făcută **prin instrumente de plată fără numerar** — inclusiv prin rambursare pe cardul cu care s-a plătit inițial, ceea ce răspunde direct la întrebarea din titlu.
- Singura excepție care permite restituirea integrală în numerar, indiferent de sumă, e declarația pe propria răspundere a clientului că **nu mai deține cont bancar** la data restituirii.

Contabil, restituirea pe card se înregistrează ca o diminuare a creanței/încasării inițiale (stornare parțială sau totală a facturii/bonului), cu ieșire de disponibilități prin contul bancar, nu prin casierie.

## Ce se greșește în practică

- Se restituie în numerar sume care depășesc 10.000 lei către o persoană fizică, fără a verifica plafonul din Legea 70/2015, expunând firma la amendă contravențională (10% din suma care depășește plafonul, minimum 100 lei).
- Se cere clientului declarația pe propria răspundere „nu mai am cont bancar" ca formalitate de rutină, chiar și atunci când restituirea e oricum sub plafonul de 10.000 lei — excepția e relevantă doar peste acest prag.
- Se confundă restituirea către persoane fizice (plafon 10.000 lei, art. 9 alin. (2)) cu restituirea facturilor stornate către alte firme (plafon diferit, 5.000/10.000 lei, art. 9 alin. (1)) — regimul legal nu e identic pentru cele două categorii de beneficiari.

## Ce face iConta.eu

La data acestui ghid, iConta.eu oferă evidența generală a facturilor și a încasărilor/plăților asociate (casierie și bancă). Modulul de casierie (`core/casa.py`, funcția `verifica_plafon`) semnalează, ca avertisment, orice plată în numerar de peste 10.000 lei către aceeași persoană fizică într-o zi — inclusiv o restituire introdusă ca atare — dar nu distinge specific „restituire de bunuri/servicii neprestate" de o altă plată către persoana fizică, și nu verifică declarația pe propria răspundere privind lipsa contului bancar (excepția de la art. 9 alin. (2)). Încadrarea corectă a modalității de restituire rămâne o decizie a contabilului la momentul înregistrării.

[iConta.eu](/)
