---
title: Cum se înregistrează o încasare în avans prin bancă?
description: O încasare în avans prin bancă generează TVA exigibilă imediat la data încasării, prin nota 4111 = 419 + 4427; dacă suma e în valută, cursul folosit e cel BNR din ultima zi bancară anterioară plății, iar suma trebuie deja convertită corect înainte de a fi introdusă în sistem.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se înregistrează o încasare în avans prin bancă?

Cel mai frecvent caz de avans e cel încasat prin transfer bancar de la un client, înainte de livrarea bunurilor sau prestarea serviciului. Mecanica e simplă, dar are câteva puncte unde apar greșeli — mai ales când suma e în valută.

## Temeiul legal

::: ghid-temei
"(2) Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine: ... b) la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine faptul generator. Avansurile reprezintă plata parțială sau integrală a contravalorii bunurilor și serviciilor, efectuată înainte de data livrării ori prestării acestora;"

"311^1. (1) Dacă un client plătește o sumă înainte ca entitatea să transfere acestuia un bun sau un serviciu, în momentul încasării entitatea înregistrează o datorie față de client. ... (2) Sumele încasate în condițiile alin. (1) se înregistrează ca o datorie față de client (contul 419 «Clienți - creditori»). Entitatea scoate din evidență acea datorie și recunoaște venituri atunci când transferă bunurile sau serviciile respective..."

"Contul 419 «Clienți ‐ creditori» — Cu ajutorul acestui cont se ține evidența clienților ‐ creditori, reprezentând avansurile încasate de la clienți. Contul 419 «Clienți ‐ creditori» este un cont de pasiv. În creditul contului 419 se înregistrează: ‐ sumele facturate clienților reprezentând avansuri pentru livrări de bunuri sau prestări de servicii (411); ..."

"304. ‐ (1) Operațiunile privind încasările şi plățile în valută se înregistrează în contabilitate la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii respective. ... prin curs de schimb de la data efectuării operațiunii se înțelege cursul de schimb al pieței valutare, comunicat de Banca Națională a României, din ultima zi bancară anterioară operațiunii, disponibil ca informație la momentul efectuării operațiunii (încasare, plată, emitere de documente)."
:::

## Mecanica notei contabile

La încasarea unei sume prin bancă, înainte de livrare, entitatea recunoaște o datorie față de client (nu venit) — pct. 311^1 din OMFP 1802/2014 e explicit pe acest punct: venitul se recunoaște abia la momentul transferului efectiv al bunurilor/serviciilor, nu la încasarea avansului. Contabil, avansul se reflectă prin creșterea creanței față de client (411) și a datoriei aferente avansului (419), împreună cu TVA colectată, dar neexigibilă la nivel de venit — deși exigibilă la nivel de TVA, conform art. 282 alin. (2) lit. b).

Dacă suma încasată e în valută, cursul de referință e cel BNR din **ultima zi bancară anterioară** datei încasării (pct. 304 alin. 1) — nu cursul din ziua exactă a încasării (care ar putea să nu fie încă disponibil) și nu cursul din data facturii finale.

## Ce se greșește în practică

- Se recunoaște venit la data încasării avansului, în loc de datorie față de client (419) — greșeală care denaturează atât rezultatul contabil, cât și, indirect, verificările fiscale ulterioare.
- Se emite factura de avans, dar TVA se înregistrează abia la factura finală, ignorând exigibilitatea imediată impusă de art. 282 alin. (2) lit. b).
- Pentru încasări în valută, se folosește cursul din ziua facturii finale sau cursul mediu lunar, în loc de cursul BNR din ultima zi bancară anterioară datei efective a încasării.
- Se omite verificarea extrasului bancar pentru data exactă a creditării contului — data relevantă pentru exigibilitate e data încasării efective, nu data emiterii facturii de avans sau data ordinului de plată al clientului.

## Ce face iConta.eu

Pentru încasarea unui avans prin bancă, motorul folosește `nota_avans_incasat(suma_fara_tva, cota)`, care generează exact mecanica din pct. 9 (OMFP 1802/2014): `4111 = 419 + 4427`. Rotunjirea sumelor se face cu `Decimal` și `ROUND_HALF_UP` la 2 zecimale, conform regulii de rotunjire aritmetică a proiectului. Cota de TVA e obligatorie la fiecare apel — nu există o valoare implicită în cod.

Dacă încasarea e în valută, este important de știut că `core/avansuri.py` **nu are niciun parametru de curs valutar sau monedă** — funcția primește direct `suma_fara_tva`, presupusă deja convertită în lei. Motorul nu contactează BNR și nu calculează singur cursul din ultima zi bancară anterioară încasării; conversia corectă (suma în valută × cursul BNR aplicabil) trebuie făcută de contabil înainte de a introduce suma în sistem.

[iConta.eu](/)
