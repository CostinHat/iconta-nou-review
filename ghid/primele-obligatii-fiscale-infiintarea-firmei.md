---
title: Primele obligații fiscale după înființarea firmei
description: Ce declarații începe să urmărească semaforul de conformare fiscală de la prima lună de activitate a firmei — și de ce nicio restanță nu apare pentru perioada dinainte de înființare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Primele obligații fiscale după înființarea firmei

Imediat după înființare, obligațiile declarative ale unei firme depind în primul rând de regimul ei fiscal (microîntreprindere sau impozit pe profit) și de faptul dacă are sau nu angajați — nu toate declarațiile pornesc automat din prima lună.

## Temeiul legal

::: ghid-temei
„Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor..."

*(Codul fiscal — Legea nr. 227/2015, art. 42 alin. (1), formă aplicabilă din anul fiscal 2026, potrivit OUG nr. 8/2026 art. 6 pct. 12)*
:::

Pentru firmele pe regim de microîntreprindere, declarația echivalentă e D100, depusă trimestrial, nu anual — distincția dintre D100 și D101 ține strict de regimul fiscal ales de firmă la înființare (micro sau impozit pe profit).

## Ce urmărește semaforul de la prima lună

- **D100 sau D101, în funcție de regimul fiscal ales** — micro: D100, trimestrial; impozit pe profit: D101, anual, pentru anul fiscal încheiat.
- **D112, doar din luna în care firma are efectiv un angajat activ** — dacă firma nu are salariați, D112 nu apare deloc ca obligație.
- **D300/D394, doar dacă firma e înregistrată în scopuri de TVA** — o firmă neînregistrată nu are aceste obligații.
- **D406 (SAF-T)**, obligatorie tuturor firmelor din 2025 — inclusiv celor nou-înființate, cu periodicitate dependentă de statutul de TVA.

## Ce nu apare ca restanță

Semaforul nu marchează nicio declarație ca restantă pentru perioada dinainte ca firma să fi existat sau să fi avut activitate demonstrabilă — motorul verifică întâi existența/activitatea firmei în anul respectiv (din data înființării și din activitatea reală înregistrată), și doar apoi aplică termenele de declarare. O firmă înființată în cursul anului nu primește, deci, restanțe „retroactive" pentru lunile dinainte de înființare.

## Ce se greșește în practică

- Se presupune că toate cele 9 declarații urmărite de semafor pornesc automat din prima zi, inclusiv D112 fără angajați sau D300/D394 fără înregistrare de TVA.
- Nu se completează regimul fiscal (micro/profit) în profilul firmei la înființare — fără această informație, semaforul nu poate decide dacă firma datorează D100 sau D101 și marchează starea ca „nu se poate verifica", nu ca „la zi".
- Se așteaptă ca prima declarație D101 (pentru firmele pe profit) să apară în prima lună — de fapt D101 e anuală, pentru anul fiscal încheiat, cu termen mult mai târziu.

## Ce face iConta.eu

Motorul F022 (`core/control_fiscal_api.py`) construiește verdictul pentru fiecare firmă pornind de la profilul ei fiscal (regim, statut de TVA, existența de salariați) și de la data reală a existenței/activității — o firmă nou-înființată nu apare cu restanțe pentru perioada anterioară înființării. Pentru ca semaforul să poată evalua corect primele obligații, profilul firmei (regim fiscal, statut de TVA) trebuie completat încă din prima lună — necompletat, declarațiile care depind de el (D100/D101, D394) apar gri, nu verzi.

[iConta.eu](/)
