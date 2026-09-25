---
title: "Cum se calculează diferențele de curs la încasarea unei facturi?"
description: "La încasarea unei creanțe în valută, diferența de curs se calculează între cursul din evidență și cursul BNR de la data încasării: câștig (765) dacă cursul a crescut, pierdere (665) dacă a scăzut. Motor automat în iConta.eu, prin operațiunea Decontare în valută."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează diferențele de curs la încasarea unei facturi?

Diferența se calculează ca produs între valoarea în valută a facturii și diferența dintre cursul BNR de la data încasării și cursul la care creanța era înregistrată în evidență — cu semnul determinat de sensul mișcării cursului.

## Temeiul legal

::: ghid-temei
„Diferentele de curs valutar (665/765) - motor PUR. Sursa: OMFP 1802/2014 pct. 316-322: diferentele de curs la decontarea creantelor/datoriilor in valuta si la reevaluarea LUNARA a soldurilor (creante, datorii, disponibilitati) la cursul BNR din ultima zi bancara a lunii se recunosc in 665 (cheltuieli) / 765 (venituri). Reguli de semn: - CREANTA (4111, 461...) sau DISPONIBIL (5124): curs creste -> castig 765; - DATORIE (401, 462...): curs creste -> pierdere 665."
— core/diferente_curs.py (docstring)

„322. - (1) Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate inițial pe parcursul lunii sau față de cele la care sunt înregistrate în contabilitate trebuie recunoscute în luna în care apar, ca venituri sau cheltuieli din diferențe de curs valutar."
— OMFP 1802/2014, pct. 322 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Notă de verificare: docstring-ul din cod citează pct. 316-322 ca temei general, dar textul acestui interval conține și o dispoziție tranzitorie (pct. 316) fără legătură cu diferențele de curs — definiția tranzacției/cursului e la **pct. 317**, iar decontarea propriu-zisă la **pct. 322**, citat mai sus verbatim.

Formula de calcul, aplicată la o creanță (o factură de încasat de la un client în valută):

- `diferență = valoare_în_valută × (curs_la_încasare − curs_din_evidență)`
- Dacă diferența e **pozitivă** (cursul a crescut față de cel din evidență) → **câștig**, cont **765**.
- Dacă diferența e **negativă** (cursul a scăzut) → **pierdere**, cont **665**.
- Nota contabilă conține și linia principală — contravaloarea în lei a creanței, la cursul din evidență — pe lângă linia de diferență.

## Ce se greșește în practică

- Se calculează diferența față de cursul zilei facturii, nu față de cursul la care creanța e efectiv înregistrată în evidență la momentul încasării (care poate fi diferit, dacă a existat deja o reevaluare lunară între timp).
- Se inversează semnul: la o creanță, cursul în creștere înseamnă câștig (765), nu pierdere — regula e opusă față de o datorie, unde cursul în creștere înseamnă pierdere (665).
- Se omite recunoașterea diferenței în luna în care are loc încasarea, amânând-o pentru o perioadă ulterioară — legea cere recunoașterea „în luna în care apar".

## Ce face iConta.eu

Motorul pur `core/diferente_curs.py`, funcția `diferenta(valoare_valuta, curs_initial, curs_final, tip)`, calculează exact formula de mai sus pentru `tip="creanta"`, cu rotunjire aritmetică (Decimal + ROUND_HALF_UP). Operațiunea „Decontare în valută" din ecranul Operațiuni speciale (`decontare_valuta`) ia automat cursul BNR al zilei încasării (`core/curs_bnr.py`) și generează nota contabilă completă — linia principală plus linia de diferență pe 665/765 — direct în registrul jurnal, ca ciornă.

O limită de reținut: ecranul „Decontare în valută" nu are câmp pentru contul de bancă/casierie — orice încasare introdusă prin acest ecran se înregistrează implicit pe contul de bancă în valută (5124), chiar dacă încasarea a avut loc efectiv prin casierie în valută (5314) sau alt cont. Dacă încasarea ta a trecut prin alt cont decât 5124, verifică și corectează manual contul din nota generată.

[iConta.eu](/)
