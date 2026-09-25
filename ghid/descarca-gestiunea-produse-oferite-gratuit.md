---
title: "Cum se descarcă gestiunea pentru produse oferite gratuit?"
description: "Documentul de descărcare din gestiune pentru bunurile cedate cu titlu gratuit și tratamentul TVA aferent, conform OMFP 2634/2015 și Codul fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se descarcă gestiunea pentru produse oferite gratuit?

Mostrele date clienților, produsele oferite ca stimulent de vânzare sau bunurile cedate în scop de protocol trebuie scoase din gestiune la fel de riguros ca o vânzare obișnuită — cu documentul potrivit și cu tratamentul corect de TVA, care nu e implicit "scutit" doar pentru că nu există plată.

## Temeiul legal

::: ghid-temei
„Dispoziția de livrare servește ca: - document pentru eliberarea din magazie a produselor, mărfurilor sau a altor valori materiale destinate vânzării, a bunurilor cedate cu titlu gratuit sau acordate pentru stimularea vânzării, după caz; [...] Avizul de însoțire a mărfii servește ca: [...] - document de descărcare din gestiune a bunurilor cedate cu titlu gratuit."
— OMFP 2634/2015, Anexa 2, Cod 14-3-5A și Cod 14-3-6A (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)

„Sunt asimilate livrărilor de bunuri efectuate cu plată următoarele operațiuni: [...] b) preluarea de către o persoană impozabilă a bunurilor mobile achiziționate sau produse de către aceasta pentru a fi puse la dispoziția altor persoane în mod gratuit, dacă taxa aferentă bunurilor respective sau părților lor componente a fost dedusă total sau parțial."
— Codul fiscal (Legea 227/2015), art. 270 alin. (4) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul complet:

- **Documentul de ieșire** e Dispoziția de livrare (Cod 14-3-5A), urmată de Avizul de însoțire a mărfii cu mențiunea „Fără factură" — nu se emite factură de vânzare, pentru că nu există contravaloare de facturat.
- **Descărcarea din gestiune** se face la costul de înregistrare al bunului, în corespondență, de regulă, cu un cont de cheltuială (6xx) sau cu contul de venituri din care s-a compensat inițial, după politica entității.
- **TVA nu dispare doar pentru că bunul e gratuit**: dacă taxa de la achiziția/producția bunului a fost dedusă, cedarea gratuită se asimilează unei livrări cu plată (art. 270 alin. (4) lit. b)) și se colectează TVA la valoarea bunului — cu excepția cazurilor expres scutite de art. 270 alin. (8): reclamă, stimularea vânzărilor, sau bunuri de mică valoare acordate ca protocol/sponsorizare, în condițiile din norme.

## Ce se greșește în practică

- Se scade marfa din gestiune fără niciun document, direct din stoc, "că oricum nu s-a facturat" — descărcarea trebuie susținută de dispoziție de livrare/aviz, la fel ca orice ieșire.
- Se presupune că, neexistând vânzare, nu se datorează TVA — dacă taxa a fost dedusă la intrare, cedarea gratuită e asimilată unei livrări cu plată, cu excepțiile expres prevăzute de lege.
- Se aplică automat excepția de la art. 270 alin. (8) (reclamă, mostre, protocol) fără verificarea condițiilor și plafoanelor din normele metodologice — excepția nu e generală, ci limitată la scop și, la protocol/sponsorizare, la bunuri de mică valoare.

## Ce face iConta.eu

La data acestui ghid, `core/stocuri_cv_api.py` oferă funcția generală `iesire()` pentru descărcarea din gestiune, folosibilă tehnic și pentru cedări gratuite. Aplicația nu are însă un flux dedicat „cedare cu titlu gratuit" care să calculeze automat TVA colectată conform art. 270 alin. (4) lit. b) sau să verifice dacă operațiunea se încadrează în vreuna dintre excepțiile de la art. 270 alin. (8) — încadrarea legală a fiecărei cedări rămâne, azi, o evaluare a contabilului.

[iConta.eu](/)
