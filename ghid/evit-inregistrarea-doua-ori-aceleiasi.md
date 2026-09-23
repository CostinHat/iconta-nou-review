---
title: Cum evit înregistrarea de două ori a aceleiași facturi din e-Factura?
description: Descărcarea din SPV nu creează niciodată cheltuială dublă, chiar dacă aceeași factură ajunge de două ori ca ciornă — controlul real se aplică la momentul validării, pe numărul facturii, furnizor și dată.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum evit înregistrarea de două ori a aceleiași facturi din e-Factura?

Vestea bună: nu poți, practic, să înregistrezi de două ori aceeași cheltuială din e-Factura, chiar dacă vezi două rânduri asemănătoare în lista de validat. Controlul care contează nu e la descărcare, ci la validare.

## Temeiul legal

::: ghid-temei
„Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul naţional privind factura electronică RO e-Factura."

— OUG nr. 120/2021, art. 4 alin. (7)
:::

Fiindcă legea leagă „primirea” facturii de disponibilitatea ei pentru descărcare, iar sistemul ANAF poate genera mai multe mesaje de notificare pentru aceeași operațiune (de exemplu la o retransmitere), e firesc ca aplicația să întâlnească uneori mai multe „anunțuri” pentru practic aceeași factură — problema tehnică reală e cum tratează asta, nu dacă se poate întâmpla.

## Cum funcționează, în doi pași

**La descărcare**, aplicația ține minte identificatorul unic al fiecărui mesaj ANAF descărcat deja și nu îl reimportă. Fereastra de interogare se suprapune intenționat (aceleași zile sunt verificate la mai multe rulări succesive, ca tolerantă la eșecuri), deci același mesaj poate fi „văzut” de mai multe ori de proces — dar e recunoscut și sărit după prima descărcare.

**La validare** intervine controlul real anti-duplicat: când confirmi o factură, aplicația verifică dacă mai există deja o factură înregistrată cu același număr, același furnizor și aceeași dată de emitere. Dacă da, nu creează o cheltuială nouă — leagă factura curentă de cea deja existentă. Practic, chiar dacă ai valida din greșeală același conținut de două ori, a doua oară nu apare o cheltuială în plus.

Ce **poate** totuși să se întâmple: dacă ANAF trimite două mesaje diferite (id-uri diferite) pentru aceeași factură — de exemplu o retransmitere — ambele pot ajunge ca ciorne separate în lista de validat, până când una dintre ele e validată sau respinsă.

## Ce se greșește în practică

- Se validează, din grabă, ambele rânduri „gemene” din lista de facturi de validat, presupunând că fiecare e o factură diferită — de obicei a doua validare nu creează cheltuială nouă, dar rândul rămâne confuz în listă dacă nu e curățat.
- Se ignoră rândul duplicat rămas ca ciornă, lăsându-l la nesfârșit în lista de validat, în loc de a-l respinge cu un motiv explicit odată ce cealaltă a fost validată.
- Se presupune că verificarea de duplicat se face pe conținutul XML-ului — de fapt se face pe numărul facturii, furnizor și dată, nu pe amprenta fișierului.

## Ce face iConta.eu

Aplicația aplică două controale distincte: dedup la descărcare, pe identificatorul de mesaj ANAF (ca să nu reimporte de la zero același mesaj la rulări succesive), și dedup la validare, pe combinația număr factură + furnizor + dată de emitere (ca să nu creeze niciodată două cheltuieli pentru aceeași factură reală). Amprenta XML-ului e stocată pentru fiecare rând descărcat, dar nu participă la nicio verificare de duplicat — e doar o informație suplimentară.

[iConta.eu](/)
