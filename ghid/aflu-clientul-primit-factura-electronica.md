---
title: "Cum aflu dacă clientul a primit factura electronică"
description: "Explică diferența dintre comunicarea legală a facturii electronice și confirmarea de citire, plus cum urmărește iConta.eu statusul la ANAF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum aflu dacă clientul a primit factura electronică

În sistemul RO e-Factura, "primirea" de către client nu e o confirmare pe care o dă clientul, ci un fapt tehnic definit de lege: momentul în care factura devine disponibilă pentru descărcare, după ce trece validarea și primește semnătura Ministerului Finanțelor.

## Temeiul legal

::: ghid-temei
"(4) [...] se aplică semnătura electronică a Ministerului Finanţelor şi se comunică de îndată destinatarului. Aplicarea semnăturii electronice a Ministerului Finanţelor atestă primirea acesteia în sistemul naţional privind factura electronică RO e-Factura." [...] "(7) Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul naţional privind factura electronică RO e-Factura. [...] Data comunicării este accesibilă în sistem şi emitentului facturii electronice."
— OUG 120/2021, art. 4 alin. (4) și alin. (7), `anaf_surse/oug_120_2021.txt:225-242`, dosar de cercetare F178.
:::

Legea leagă "primirea" de disponibilitatea facturii în sistemul național, atestată prin semnătura electronică MF, nu de o acțiune explicită a clientului (deschidere, confirmare, descărcare efectivă). Data comunicării e accesibilă și emitentului, direct în sistemul RO e-Factura — de acolo se poate verifica, nu prin confirmare de la client.

## Ce se greșește în practică

Greșeala frecventă e solicitarea unei confirmări separate de la client (email, telefon) ca dovadă că a "primit" factura, deși legea consideră factura primită din momentul comunicării în sistem, indiferent dacă destinatarul a deschis-o. O altă greșeală e a considera statusul "în prelucrare" drept eșec, deși e o etapă normală, de așteptare, înainte de verdictul terminal.

## Ce face iConta.eu

iConta.eu interoghează automat starea trimiterii la ANAF la fiecare 30 de minute (`core/spv_poll.py`, cron-ul `spv-poll.timer`), pentru toate facturile aflate în așteptare. La verdict terminal favorabil ("ok"), aplicația descarcă automat recipisa (ZIP), calculează SHA-256 al XML-ului semnat și marchează data finalizării — acesta e semnalul tehnic, verificat de aplicație, că factura a fost comunicată conform legii. Dacă starea rămâne "în prelucrare" peste 2 zile (prag intern conservator, nu termen legal ANAF), aplicația marchează factura pentru verificare manuală în SPV, în loc să tacă. Exemplarul original opozabil rămâne XML-ul însoțit de semnătura electronică MF, nu recipisa în sine.

De reținut: nu există, în acest moment, un ecran dedicat listării facturilor respinse sau în așteptare la nivel de portofoliu în interfața aplicației — starea se verifică per factură; dacă un asemenea ecran a fost adăugat ulterior verificării acestui ghid, confirmați direct în aplicație.

[iConta.eu](/)
