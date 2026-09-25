---
title: "Cum se tratează diferențele de curs la plățile în valută"
description: "Tratamentul contabil complet al plăților (și încasărilor) în valută: regula de semn pe tip de sold și recunoașterea diferenței în luna decontării."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se tratează diferențele de curs la plățile în valută

Orice plată sau încasare în valută făcută la un curs diferit de cel din evidența contabilă produce o diferență de curs valutar, care se recunoaște imediat, în luna decontării, ca venit sau cheltuială financiară — nu se reportă și nu se ignoră dacă suma e mică.

## Temeiul legal

::: ghid-temei
„322. - (1) Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate inițial pe parcursul lunii sau față de cele la care sunt înregistrate în contabilitate trebuie recunoscute în luna în care apar, ca venituri sau cheltuieli din diferențe de curs valutar."
— OMFP 1802/2014, pct. 322 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Tratamentul depinde de tipul soldului decontat: **datorie** plătită (401, 462...) — curs în creștere înseamnă pierdere (665), curs în scădere înseamnă câștig (765).
- **Creanță** încasată (4111, 461...) sau mișcare de **disponibil** (5124) — regula e inversă: curs în creștere înseamnă câștig (765), curs în scădere înseamnă pierdere (665).
- Nota contabilă are întotdeauna două componente: linia principală, la contravaloarea în lei calculată la cursul din evidență, și linia de diferență, pe 665 sau 765, după caz.
- Diferența se calculează pentru „cursuri diferite față de cele la care au fost înregistrate inițial [...] sau față de cele la care sunt înregistrate în contabilitate" — adică față de ultimul curs de evidență, nu neapărat cursul de la emiterea facturii.

## Ce se greșește în practică

- Se tratează o încasare de creanță cu regula de semn a unei datorii (sau invers), obținând o notă contabilă cu 665/765 inversate.
- Se omite complet nota de diferență de curs atunci când suma e mică, considerând-o „nesemnificativă" — legea nu prevede un prag de minimis pentru recunoașterea diferenței.
- Se calculează diferența pe baza cursului valabil la data facturii inițiale, ignorând o eventuală reevaluare lunară intermediară care a modificat deja cursul de evidență al soldului.

## Ce face iConta.eu

Ecranul **Operațiuni speciale → Decontare în valută** din iConta.eu acoperă exact acest scenariu, pentru încasarea unei creanțe sau plata unei datorii. Motorul (`core/diferente_curs.py`, funcția `nota_decontare`) primește tipul soldului, valoarea în valută și cursul de evidență, ia automat cursul BNR al zilei (`core/curs_bnr.py`) și aplică regula de semn corectă pe tip, generând nota-ciornă cu linia principală și diferența pe 665/765. Ruta cere ca luna să fie deschisă (`_cere_luna_deschisa`) — dacă e închisă, aplicația refuză nota și returnează o eroare clară, nu un mesaj tehnic. Limita cunoscută: contul de bancă folosit la decontare e mereu 5124 (implicit hardcodat), fiindcă ecranul nu are câmp pentru contul efectiv — dacă plata/încasarea a avut loc prin casieria în valută (5314) sau alt cont bancar în valută, contabilul trebuie să corecteze manual nota generată.

[iConta.eu](/)
