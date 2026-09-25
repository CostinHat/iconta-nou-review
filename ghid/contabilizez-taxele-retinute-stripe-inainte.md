---
title: "Cum contabilizez taxele reținute de Stripe înainte de virarea banilor?"
description: "De ce comisionul reținut de un procesator de plăți precum Stripe nu se scade direct din venit, ci se înregistrează separat, conform principiului necompensării din OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum contabilizez taxele reținute de Stripe înainte de virarea banilor?

Când un procesator de plăți precum Stripe reține comisionul înainte de a vira suma netă în cont, apare tentația de a înregistra direct doar suma încasată efectiv. Contabilitatea românească nu permite acest scurtcircuit — venitul se recunoaște la valoarea lui brută, iar comisionul se înregistrează separat, ca o cheltuială distinctă.

## Temeiul legal

::: ghid-temei
„56. - (1) Principiul necompensării. Orice compensare între elementele de active și datorii sau între elementele de venituri și cheltuieli este interzisă."
— OMFP 1802/2014, pct. 56 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat la un flux de tip Stripe/PayPal/alt procesator de plăți, principiul necompensării înseamnă:

- Se înregistrează **integral venitul din vânzare** (contul 707/704, după caz), la valoarea brută facturată clientului, indiferent de suma efectiv virată în cont de procesator.
- Se înregistrează **separat cheltuiala cu comisionul** reținut de procesator (de regulă la conturi de cheltuieli cu servicii bancare/comisioane, cont 627 sau analitic distinct), la valoarea comisionului dedus.
- Suma netă virată efectiv în contul bancar este doar rezultatul stingerii creanței (client/procesator) minus cheltuiala cu comisionul — nu poate înlocui înregistrarea celor două fluxuri separate.

Practic, dacă un client plătește 100 lei printr-un abonament procesat de Stripe, iar Stripe virează 97 lei după ce reține 3 lei comision, contabilitatea corectă înregistrează venit de 100 lei și cheltuială cu comisionul de 3 lei — nu venit net de 97 lei.

## Ce se greșește în practică

- Se înregistrează direct suma netă încasată în bancă drept venit, „compensând" implicit comisionul cu venitul — exact operațiunea interzisă de principiul necompensării.
- Se pierde astfel evidența reală a cheltuielilor cu comisioanele de procesare, ceea ce denaturează analiza costurilor și poate afecta corectitudinea unor calcule (de exemplu, deductibilitatea sau baza de calcul pentru anumite plafoane).
- Se omite reconcilierea între suma facturată clientului, suma raportată de procesator ca brută și suma efectiv virată — cele trei cifre trebuie să coincidă cu înregistrările contabile corespunzătoare.

## Ce face iConta.eu

iConta.eu oferă contabilitate generală, inclusiv importul extraselor bancare și înregistrarea manuală sau asistată a veniturilor și cheltuielilor. La data acestui ghid, aplicația nu are o integrare directă cu Stripe sau alți procesatori de plăți care să separe automat venitul brut de comisionul reținut — reconcilierea între suma facturată, comisionul dedus și suma netă încasată rămâne un pas manual, pe baza rapoartelor descărcate din contul de procesator.

[iConta.eu](/)
