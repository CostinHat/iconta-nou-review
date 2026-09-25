---
title: "Cum se calculează diferențele de curs la plata unei facturi?"
description: "Formula de calcul a diferenței de curs valutar la decontarea unei facturi în valută și cum o generează automat iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează diferențele de curs la plata unei facturi?

Când plătești o factură în valută la un curs diferit de cel la care ai înregistrat-o inițial, diferența dintre cele două valori în lei e o diferență de curs valutar — venit (765) dacă îți e favorabilă, cheltuială (665) dacă îți e nefavorabilă. Legea cere ca această diferență să fie recunoscută în luna în care are loc plata, nu reportată.

## Temeiul legal

::: ghid-temei
„322. - (1) Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate inițial pe parcursul lunii sau față de cele la care sunt înregistrate în contabilitate trebuie recunoscute în luna în care apar, ca venituri sau cheltuieli din diferențe de curs valutar."
— OMFP 1802/2014, pct. 322 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Formula de calcul: diferența = valoarea în valută × (cursul de la decontare − cursul de la înregistrare, sau ultimul curs de evidență, dacă factura a mai fost reevaluată între timp).
- Pentru o **datorie** (factură de la furnizor, cont 401/462): dacă în intervalul respectiv cursul a crescut, diferența e o pierdere (665); dacă a scăzut, e un câștig (765).
- Pentru o **creanță** (factură emisă de tine, cont 4111/461): regula e inversă — cursul crescut înseamnă câștig (765), cursul scăzut înseamnă pierdere (665).
- Cursul de referință pentru „cursul la decontare" e cursul BNR al zilei plății/încasării, comunicat de Banca Națională a României.

## Ce se greșește în practică

- Se calculează diferența față de cursul de la data facturii originale, chiar dacă între timp a existat deja o reevaluare lunară — corect e să se pornească de la ultimul curs de evidență (cel din urma reevaluare, nu neapărat cel inițial).
- Se inversează regula de semn — se tratează o datorie ca o creanță (sau invers), obținând o notă contabilă cu semnul greșit pe 665/765.
- Se amână recunoașterea diferenței pentru finalul lunii, deși pct. 322 cere recunoașterea „în luna în care apar" — la momentul plății, nu la închiderea perioadei.

## Ce face iConta.eu

Această operațiune corespunde exact rutei de decontare din iConta.eu: din ecranul **Operațiuni speciale → Decontare în valută**, completezi tipul (creanță sau datorie), valoarea în valută, moneda și cursul de evidență; aplicația ia automat cursul BNR al zilei din `core/curs_bnr.py` și, prin `core/diferente_curs.py`, calculează diferența cu regula de semn corectă pe tip (creanță/disponibil câștigă la curs în creștere, datorie pierde), generând o notă-ciornă cu linia principală și linia de diferență pe 665 sau 765. Motorul e testat unitar (`test_diferente_curs.py`, 11 teste). O limită de reținut: ecranul de decontare nu are câmp pentru contul de bancă/casierie — toate decontările se înregistrează implicit pe contul 5124, indiferent prin ce cont a avut loc efectiv plata.

[iConta.eu](/)
