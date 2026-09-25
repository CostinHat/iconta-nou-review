---
title: "Cum știu că nu mai am obligații după radiere"
description: "Ce înseamnă efectiv radierea înregistrării fiscale și de ce nu stinge automat obligațiile fiscale neachitate din perioada de activitate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum știu că nu mai am obligații după radiere

Radierea înregistrării fiscale retrage codul de identificare fiscală și certificatul de înregistrare — dar nu e, prin ea însăși, o confirmare că nu mai există obligații fiscale datorate. Legea leagă explicit codul retras de posibilitatea utilizării lui ulterioare, tocmai pentru situațiile în care rămân de îndeplinit obligații din perioada în care entitatea a existat ca subiect de drept fiscal.

## Temeiul legal

::: ghid-temei
„(1) Radierea înregistrării fiscale reprezintă activitatea de retragere a codului de identificare fiscală și a certificatului de înregistrare fiscală. [...]
(4) Codul de identificare fiscală retras ca urmare a radierii înregistrării fiscale poate fi utilizat ulterior radierii numai pentru îndeplinirea, de către succesorii persoanelor/entităților care și-au încetat existența, a obligațiilor fiscale aferente perioadelor în care persoana/entitatea a avut calitatea de subiect de drept fiscal."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 90 alin. (1) și (4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- **Radierea e o operațiune administrativă asupra codului fiscal**, nu o "curățare" automată a istoricului de obligații — ea nu șterge datoriile fiscale existente la momentul radierii.
- **Legea prevede explicit continuitatea obligațiilor**: codul retras poate fi reactivat ulterior, exclusiv pentru ca succesorii entității radiate să-și îndeplinească obligațiile fiscale aferente perioadei în care aceasta a funcționat.
- **Verificarea reală a lipsei de obligații restante se face prin certificatul de atestare fiscală**, nu prin simpla emitere a deciziei de radiere — acest certificat confirmă (sau infirmă) obligațiile fiscale restante la data solicitării.
- **Dacă firma e supusă unei inspecții fiscale în curs**, certificatul de atestare fiscală cerut în scopul radierii se emite abia după finalizarea inspecției, în termen de 5 zile lucrătoare de la decizia de impunere sau de nemodificare a bazei de impozitare (art. 158 alin. (6)) — deci radierea așteaptă, practic, closingul fiscal al perioadei verificate.

## Ce se greșește în practică

- Se presupune că, odată emisă decizia de radiere de la registrul comerțului, orice obligație fiscală anterioară dispare automat — legea nu susține această interpretare; obligațiile rămân urmăribile prin succesori.
- Se ignoră solicitarea certificatului de atestare fiscală înainte de finalizarea radierii, rămânând fără o confirmare oficială a stării obligațiilor la acel moment.
- Se arhivează documentele firmei imediat după radiere, deși eventualele obligații fiscale identificate ulterior (de exemplu în urma unui control) pot necesita documentele perioadei de activitate pentru apărare.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are un modul care să verifice sau să confirme absența obligațiilor fiscale restante ale unei firme în proces de radiere — există un modul de lichidare (`core/lichidare.py`) în cod, dar solicitarea și interpretarea certificatului de atestare fiscală de la ANAF, precum și confirmarea finală a stingerii tuturor obligațiilor, rămân un proces manual, în afara aplicației.

[iConta.eu](/)
