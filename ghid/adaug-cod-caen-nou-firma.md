---
title: "Cum adaug un cod CAEN nou la firma existentă"
description: "Termenul de 15 zile pentru anunțarea la ANAF a modificărilor datelor de înregistrare fiscală, aplicabil și adăugării unui cod CAEN."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum adaug un cod CAEN nou la firma existentă

Adăugarea unui cod CAEN presupune două pași distincți: înregistrarea propriu-zisă la Oficiul Registrului Comerțului (act adițional la actul constitutiv) și, separat, anunțarea modificării la organul fiscal, într-un termen legal precis.

## Temeiul legal

::: ghid-temei
„Modificările ulterioare ale datelor din declarația de înregistrare fiscală trebuie aduse la cunoștință organului fiscal central, în termen de 15 zile de la data producerii acestora, prin completarea și depunerea declarației de mențiuni."
— Legea nr. 207/2015, art. 88 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă pentru adăugarea unui cod CAEN:

- Codul CAEN e o dată din declarația de înregistrare fiscală a firmei — orice modificare a acesteia (adăugarea unui cod secundar sau schimbarea codului principal) declanșează obligația de la art. 88 alin. (1): anunțarea organului fiscal, prin declarație de mențiuni, **în 15 zile** de la data producerii modificării.
- Data „producerii modificării" e, de regulă, data înregistrării mențiunii la Registrul Comerțului (unde se adaugă efectiv codul CAEN în obiectul de activitate), nu data deciziei interne a asociaților.
- Codul CAEN nu e doar o formalitate administrativă — el intră direct în validarea unor declarații fiscale: nomenclatorul CAEN e verificat, de exemplu, la generarea D101, D300 și D394, iar un cod în afara nomenclatorului acceptat de ANAF poate duce la respingerea declarației.
- Pentru firmele plătitoare de impozit pe veniturile microîntreprinderilor, anumite coduri CAEN pot influența și încadrarea în regimuri fiscale speciale (cote diferențiate, activități excluse de la micro) — motiv suplimentar pentru actualizarea promptă a datelor.

## Ce se greșește în practică

- Se adaugă codul CAEN la Registrul Comerțului, dar se omite depunerea declarației de mențiuni la ANAF în cele 15 zile prevăzute de art. 88 alin. (1) — modificarea rămâne „incompletă" din perspectivă fiscală.
- Se presupune că actualizarea automată a datelor firmei (preluată de ANAF de la Registrul Comerțului) scutește de obligația proprie de declarare — termenul de 15 zile e o obligație a contribuabilului, nu una condiționată de sincronizarea dintre instituții.
- Se folosește un cod CAEN nou, valid la Registrul Comerțului, dar care nu figurează încă în nomenclatorul acceptat de o anumită declarație fiscală (de exemplu D112) — declarația poate fi respinsă până la actualizarea nomenclatorului sau corectarea codului.

## Ce face iConta.eu

Câmpul de cod CAEN din profilul firmei în iConta.eu (`core/firma_profil_api.py`) e folosit direct la generarea declarațiilor D101, D300 și D394, iar aplicația verifică activ dacă valoarea introdusă se regăsește în nomenclatorul acceptat de D112, semnalând eroarea contabilului înainte de depunere dacă nu se regăsește. Aplicația gestionează însă un singur cod CAEN activ în profilul firmei, nu o listă completă de coduri secundare, iar depunerea declarației de mențiuni la ANAF pentru adăugarea codului rămâne un pas separat, în afara aplicației.

[iConta.eu](/)
