---
title: "Recuperarea TVA-ului la închiderea firmei"
description: "Obligația de a depune ultimul decont de TVA la anularea înregistrării, cu toate ajustările efectuate, conform art. 316 din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Recuperarea TVA-ului la închiderea firmei

Închiderea unei firme nu suspendă obligațiile de TVA — dimpotrivă, ultimul decont depus e cel mai încărcat, pentru că trebuie să reflecte toate ajustările impuse de încetarea calității de plătitor de TVA.

## Temeiul legal

::: ghid-temei
„(13) Persoanele impozabile aflate în situațiile prevăzute la alin. (11) au obligația să depună ultimul decont de taxă prevăzut la art. 323, indiferent de perioada fiscală aplicată conform art. 322, până la data de 25 a lunii următoare celei în care a fost comunicată decizia de anulare a înregistrării în scopuri de TVA."
— Legea 227/2015 (Codul fiscal), art. 316 alin. (13) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce trebuie să conțină acest ultim decont și ce rezultă pentru eventualul sold în favoarea firmei:

- **Termenul e fix**: 25 a lunii următoare celei în care a fost comunicată decizia de anulare a înregistrării în scopuri de TVA — indiferent de perioada fiscală obișnuită a firmei (lună sau trimestru), ultimul decont respectă acest termen unic.
- **Toate ajustările de TVA trebuie evidențiate** în acest decont — inclusiv ajustările pentru bunurile de capital rămase în patrimoniu (dacă nu mai sunt folosite în scopuri economice care dau drept de deducere), pentru stocurile nevândute și pentru orice altă situație care impune regularizarea taxei deduse anterior.
- **Dacă rezultă un sold negativ** (TVA de recuperat), acesta se solicită prin decontul respectiv, la fel ca orice altă cerere de rambursare — dar fiind ultimul decont al unei firme care își încetează activitatea, e un candidat firesc pentru verificare mai atentă din partea organului fiscal, tocmai pentru că nu mai există deconturile ulterioare prin care eventualele erori s-ar corecta automat.
- **Radierea firmei (art. 90 din Codul de procedură fiscală) și anularea codului de TVA** se leagă direct de acest ultim decont — o rambursare solicitată, dar nesoluționată la data radierii, rămâne un drept care se soluționează în beneficiul succesorilor legali (conform regulii generale de la art. 90 alin. 4 CPF), nu se pierde automat.

## Ce se greșește în practică

- Se depune ultimul decont fără a efectua toate ajustările impuse de încetarea calității de plătitor de TVA (bunuri de capital, stocuri) — un decont incomplet la închidere complică și întârzie soluționarea oricărei cereri de rambursare.
- Se așteaptă radierea efectivă a firmei înainte de a depune ultimul decont, deși termenul legal e legat de data comunicării deciziei de anulare a înregistrării în scopuri de TVA, nu de data radierii de la registrul comerțului.
- Se presupune că, o dată ce firma s-a radiat, dreptul la o rambursare de TVA solicitată anterior dispare automat — dreptul rămâne, dar exercitarea lui trece prin succesorii legali ai firmei.

## Ce face iConta.eu

Modulul de lichidare din iConta.eu (`core/lichidare.py`) tratează închiderea TVA/impozitelor curente ca parte a fluxului de lichidare, alături de calculul cotei de lichidare, notele de vânzare a activelor și partajul capitalului, conform OMFP 897/2015 și Legii 31/1990. La data acestui ghid, aplicația **nu depune automat ultimul decont de TVA** la anularea înregistrării — contabilul pregătește separat acest decont, cu toate ajustările de taxă impuse de art. 316 alin. (13), și îl depune respectând termenul legal de 25 a lunii următoare comunicării deciziei de anulare.

[iConta.eu](/)
