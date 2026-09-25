---
title: "Contabilitatea unei firme de evenimente: cum se recunosc veniturile"
description: "Momentul la care se recunoaște venitul dintr-un contract de organizare de evenimente, cu avansuri încasate înainte de prestarea efectivă a serviciului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Contabilitatea unei firme de evenimente: cum se recunosc veniturile

O firmă care organizează evenimente (nunți, conferințe, petreceri corporate) încasează de regulă unul sau mai multe avansuri înainte ca evenimentul să aibă loc. Momentul la care banii intră în cont nu e, contabil, momentul la care devin venit.

## Temeiul legal

::: ghid-temei
„Veniturile din prestări de servicii se înregistrează în contabilitate pe măsura efectuării acestora. Prestarea de servicii cuprinde inclusiv executarea de lucrări și orice alte operațiuni care nu pot fi considerate livrări de bunuri." — OMFP 1802/2014, Reglementările contabile, pct. 446 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)

„Dacă avansul încasat reprezintă o plată în avans efectuată de un client pentru servicii care urmează să fie prestate într-o perioadă viitoare, suma corespunzătoare se evidențiază în contul 472 «Venituri înregistrate în avans», urmând a fi recunoscută la venituri atunci când vor fi prestate serviciile respective." — OMFP 1802/2014, Reglementările contabile, pct. 351^1 alin. (2) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat la o firmă de evenimente: un avans încasat pentru un eveniment programat luna viitoare **nu e venit în luna încasării** — e o sumă înregistrată în contul 472, care devine venit abia atunci când evenimentul are loc și serviciul e efectiv prestat. Stadiul de realizare a serviciului se determină pe bază de situații de lucrări, procese-verbale de recepție sau alte documente care atestă prestarea (pct. 446 alin. (2)).

## Ce se greșește în practică

- Se recunoaște ca venit întreaga sumă a avansului în luna încasării, deși evenimentul are loc peste una sau mai multe luni — greșeala umflă artificial rezultatul lunii de încasare și îl subevaluează pe cel al lunii evenimentului.
- Se confundă avansul nerambursabil, perceput la începutul contractului (de exemplu un comision de rezervare), cu un venit definitiv câștigat imediat — regula cere să se stabilească întâi dacă acel avans se referă efectiv la un serviciu viitor; dacă da, se amână la venituri, nu se recunoaște pe loc.
- Se emite factura finală pe toată valoarea evenimentului, fără a regulariza mai întâi soldul avansurilor deja facturate — riscul e dublarea TVA colectate sau un sold fantomă de avans neregularizat în evidență.

## Ce face iConta.eu

Trebuie spus onest din capul locului: „evenimente" ca activitate economică (nunți, conferințe, petreceri) e un subiect complet diferit de „evenimente" ca termen tehnic folosit intern în aplicație — clopoțelul de notificări din iConta (mesaj de client nou, declarație respinsă/aprobată, alertă de control fiscal) declanșează notificări la evenimente de aplicație, nu are nicio legătură cu contabilitatea unei firme din industria evenimentelor.

Pentru facturarea propriu-zisă a unui eveniment cu avansuri, aplicația generează separat cele două tipuri de note: la încasarea fiecărui avans, 4111 = 419 + 4427 (TVA colectată devine exigibilă la încasare); la factura finală, avansul se regularizează prin nota inversă (419 = 4111, 4427 = 4111), iar diferența rămasă de încasat se facturează separat, prin motorul general de facturare. Momentul exact al recunoașterii venitului pe stadiul de execuție al serviciului — descris mai sus, conform pct. 446 — rămâne însă o decizie a contabilului, aplicată manual: aplicația nu ține o evidență automată a „gradului de finalizare" a unui eveniment care să deplaseze singură suma din 472 în cont de venit.

[iConta.eu](/)
