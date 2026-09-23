---
title: "Cum verific dacă factura a ajuns la destinatar în e-Factura"
description: "Explică ce înseamnă legal comunicarea unei facturi electronice și cum urmărește iConta.eu automat statusul la ANAF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific dacă factura a ajuns la destinatar în e-Factura

"A ajunge la destinatar" are, în sistemul RO e-Factura, un înțeles legal precis: nu ține de o confirmare de citire din partea clientului, ci de momentul în care factura devine disponibilă pentru descărcare în sistemul național.

## Temeiul legal

::: ghid-temei
"(4) În situaţia în care factura electronică transmisă respectă structura prevăzută la alin. (1), se aplică semnătura electronică a Ministerului Finanţelor şi se comunică de îndată destinatarului. Aplicarea semnăturii electronice a Ministerului Finanţelor atestă primirea acesteia în sistemul naţional privind factura electronică RO e-Factura." [...] "(7) Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul naţional privind factura electronică RO e-Factura. [...] Data comunicării este accesibilă în sistem şi emitentului facturii electronice."
— OUG 120/2021, art. 4 alin. (4) și alin. (7), `anaf_surse/oug_120_2021.txt:225-242`, dosar de cercetare F178.
:::

Odată ce factura trece validarea structurală și primește semnătura electronică a Ministerului Finanțelor, ea e considerată comunicată destinatarului — disponibilă pentru descărcare în sistemul național, indiferent dacă destinatarul a deschis-o efectiv sau nu. Data comunicării e vizibilă și emitentului, direct în sistem.

## Ce se greșește în practică

Greșeala frecventă e așteptarea unei confirmări explicite din partea clientului (telefon, email) ca dovadă a comunicării, deși legea consideră factura comunicată din momentul în care devine disponibilă în sistemul RO e-Factura, indiferent de acțiunea destinatarului. A doua greșeală e ignorarea statusului intermediar "în prelucrare" și presupunerea, prematur, că factura a fost deja acceptată.

## Ce face iConta.eu

După încărcarea facturii în SPV, iConta.eu interoghează automat, la fiecare 30 de minute (`core/spv_poll.py`, cron-ul spv-poll.timer, orele fixe `:07`/`:37`), starea trimiterii la ANAF. Când ANAF răspunde cu verdict terminal favorabil ("ok"), aplicația descarcă automat recipisa (arhivă ZIP), calculează amprenta SHA-256 a XML-ului semnat din interior și marchează factura ca finalizată — acesta e momentul confirmat tehnic al comunicării către destinatar, conform art. 4 alin. (4)-(7). Dacă starea rămâne "în prelucrare" peste un prag intern de 2 zile (un prag conservator de produs, nu un termen legal — ANAF nu documentează public durata procesării), aplicația marchează factura pentru verificare manuală, în loc să tacă situația.

De reținut: acest status confirmă acceptarea și disponibilitatea facturii în sistemul național, nu faptul că destinatarul a deschis-o efectiv — legea nu cere, și aplicația nu poate confirma, o "citire" din partea clientului.

[iConta.eu](/)
