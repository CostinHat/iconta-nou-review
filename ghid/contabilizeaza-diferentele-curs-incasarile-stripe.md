---
title: "Cum se contabilizează diferențele de curs la încasările Stripe?"
description: "O încasare prin Stripe la un curs diferit de cel al facturii e o decontare de creanță în valută, ca oricare alta — dar iConta.eu nu are o integrare automată cu Stripe."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează diferențele de curs la încasările Stripe?

Din punct de vedere contabil, o încasare printr-un procesator de plăți online precum Stripe nu e diferită de orice altă încasare a unei facturi în valută: dacă factura a fost emisă la un curs BNR, iar banii ajung efectiv în cont (după decontarea Stripe) la un curs diferit al zilei, diferența dintre cele două se recunoaște ca venit sau cheltuială din diferențe de curs. Ce diferă e doar circuitul tehnic prin care ajung banii — nu regula contabilă de recunoaștere a diferenței.

## Temeiul legal

::: ghid-temei
„322. - (1) Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate inițial pe parcursul lunii sau față de cele la care sunt înregistrate în contabilitate trebuie recunoscute în luna în care apar, ca venituri sau cheltuieli din diferențe de curs valutar."
— OMFP 1802/2014, Reglementările contabile, pct. 322 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat la o încasare Stripe: creanța față de client (factura emisă, în valută) se stinge la momentul în care banii ajung efectiv la firmă, la cursul BNR al zilei decontării. Dacă acel curs diferă de cursul din evidență (cel de la emiterea facturii), diferența — favorabilă (765) sau nefavorabilă (665) — se recunoaște în luna în care are loc încasarea, exact ca la orice altă decontare de creanță în valută.

## Ce se greșește în practică

- Se recunoaște venitul din diferența de curs la data facturării, nu la data efectivă a încasării — greșeală comună și la orice altă valută, nu specifică Stripe.
- Se ignoră comisionul reținut de procesatorul de plăți (Stripe) ca element separat de diferența de curs — comisionul e o cheltuială de operare, nu o diferență de curs valutar, chiar dacă amândouă reduc suma netă primită.
- Se înregistrează încasarea direct pe contul de bancă principal, fără să se distingă contul/circuitul real prin care banii au tranzitat (cont Stripe, apoi transfer către bancă), ceea ce poate complica ulterior reconcilierea bancară.

## Ce face iConta.eu

Aici trebuie spus direct: iConta.eu **nu are o integrare cu Stripe sau cu alt procesator de plăți online** — decizia de produs a fost explicit să nu se automatizeze această cale, fluxul real fiind transferul bancar, confirmat din extrasul de cont, la reconciliere. Deci nu există un circuit automat care să detecteze o încasare Stripe și să calculeze diferența de curs.

Ce se poate folosi, manual: dacă o creanță în valută a fost încasată (indiferent prin ce mijloc — inclusiv printr-un procesator de plăți) la un curs diferit de cel din evidență, contabilul poate introduce decontarea prin funcționalitatea de decontare în valută din iConta.eu, care calculează automat diferența 665/765. De reținut: ecranul de decontare nu are un câmp pentru contul de bancă/casierie folosit efectiv — orice decontare introdusă acolo se înregistrează implicit pe contul de bancă în valută standard, indiferent dacă banii au tranzitat printr-un cont intermediar de tip Stripe.

[iConta.eu](/)
