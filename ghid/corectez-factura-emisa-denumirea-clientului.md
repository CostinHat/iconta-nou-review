---
title: "Cum corectez o factură emisă cu denumirea clientului greșită?"
description: "Cele două căi legale de corectare a unei facturi cu date greșite despre client, în funcție de faptul că a fost sau nu transmisă deja beneficiarului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum corectez o factură emisă cu denumirea clientului greșită?

O factură emisă pe numele greșit — firmă confundată, denumire scrisă incorect, CIF-ul altui client — nu se editează pur și simplu în sistemul de facturare. Codul fiscal prevede exact două mecanisme de corectare, iar alegerea între ele depinde de un singur criteriu: dacă factura a ajuns deja la beneficiar.

## Temeiul legal

::: ghid-temei
„(1) Corectarea informațiilor înscrise în facturi sau în alte documente care țin loc de factură se efectuează astfel: a) în cazul în care factura nu a fost transmisă către beneficiar, aceasta se anulează și se emite o nouă factură; b) în cazul în care factura a fost transmisă beneficiarului, fie se emite o nouă factură care trebuie să cuprindă, pe de o parte, informațiile din factura inițială, numărul și data facturii corectate, valorile cu semnul minus sau, după caz, o mențiune din care să rezulte că valorile respective sunt negative, iar, pe de altă parte, informațiile și valorile corecte, fie se emite o nouă factură conținând informațiile și valorile corecte și concomitent se emite o factură cu valorile cu semnul minus sau, după caz, cu o mențiune din care să rezulte că valorile respective sunt negative, în care se înscriu numărul și data facturii corectate."
— Legea nr. 227/2015 (Codul fiscal), art. 330 alin. (1) lit. a), b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Concret, procedura corectă depinde de stadiul facturii:

- **Dacă factura nu a fost încă transmisă clientului** (a rămas doar în sistemul intern), se anulează pur și simplu și se emite alta, cu datele corecte — cea mai simplă situație.
- **Dacă factura a fost deja transmisă** (trimisă prin RO e-Factura, pe e-mail sau predată fizic), corectarea nu se poate face prin anulare simplă — trebuie emisă fie (i) o factură de stornare care conține datele facturii inițiale cu semnul minus, urmată de o factură nouă cu datele corecte, fie (ii) o factură nouă cu datele corecte, emisă concomitent cu o factură de stornare a celei greșite.
- Ambele variante de la lit. b) lasă o urmă clară în evidența contabilă — factura inițială greșită rămâne vizibilă, dar anulată prin stornare, nu ștearsă sau modificată direct.
- Simpla retipărire sau modificare a facturii deja transmise, fără emiterea unei stornări, nu respectă niciuna din cele două căi prevăzute de lege și lasă evidența contabilă a beneficiarului nealiniată cu cea a emitentului.

## Ce se greșește în practică

- Se „editează" factura direct în programul de facturare după ce a fost deja trimisă clientului, fără să se emită o stornare, lăsând două variante diferite ale aceleiași facturi în circulație.
- Se anulează o factură deja transmisă beneficiarului ca și cum n-ar fi ieșit niciodată din firmă, deși legea impune stornare, nu anulare simplă, odată ce factura a ajuns la client.
- Se corectează doar denumirea clientului în evidența internă, fără să se retrimită și noua factură (sau perechea stornare + factură corectă) către beneficiar, care rămâne astfel cu documentul greșit.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are o funcție dedicată de stornare a facturilor (`core/facturi_api.py`, funcția `storneaza`), care creează o factură de stornare — copie a originalului, cu cantități negative, cu numă nou din aceeași serie și referință la factura originală (`storno_din_id`) — exact mecanismul prevăzut la art. 330 alin. (1) lit. b). Aplicația impune ca orice corecție a unei facturi deja contabilizate să treacă prin acest flux de stornare, nu prin editare directă. Decizia dacă factura a fost deja transmisă beneficiarului (și, deci, dacă e nevoie de anulare simplă sau de stornare) rămâne o verificare pe care o face utilizatorul înainte de a alege calea corectă.

[iConta.eu](/)
