---
title: "Se declară facturile anulate în D394?"
description: "Ce înseamnă legal o factură anulată sau stornată și de ce D394 nu trebuie să le includă în bază și TVA, cu filtrul aplicat automat de iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se declară facturile anulate în D394?

Legea definește destul de precis ce înseamnă „factură anulată" și „factură stornată" — două noțiuni pe care contabilii le folosesc uneori interschimbabil, deși au tratament diferit. Niciuna dintre ele nu trebuie să umfle baza și TVA raportate în D394.

## Temeiul legal

::: ghid-temei
„2.2.1. seria şi numărul facturilor stornate; factura stornată reprezintă factura emisă de persoana impozabilă, a cărei valoare totală este negativă; 2.2.2. seria şi numărul facturilor anulate; factura anulată reprezintă factura emisă de persoana impozabilă, netransmisă beneficiarului, operaţiunile înscrise în aceasta nefiind înregistrate în contabilitatea persoanei impozabile."
— OPANAF 2194/2025, Anexa 2 (sursă: anaf_surse/opanaf_2194_2025_d394.txt:1030-1033)
:::

- **Factura anulată**, în sensul legii, e cea care nu a ajuns niciodată la beneficiar și nu are efect în contabilitate — nu se raportează cu bază și TVA, pentru că operațiunea, practic, nu a avut loc.
- **Factura stornată** nu e factura originală, ci documentul separat, cu valoare negativă, care o anulează pe cea dintâi. Ea are, la rândul ei, statutul unei facturi „reale" — se declară precum orice altă factură, cu semn negativ.
- Declarația trebuie să conțină, distinct, seria și numărul facturilor stornate și anulate din perioada de raportare — o informație suplimentară față de baza/TVA raportate la operațiunile normale.

## Ce se greșește în practică

- Se include o factură anulată în calculul bazei și al TVA-ului din D394, ca și cum ar fi o operațiune reală.
- Se confundă „stornarea" cu „anularea" — prima presupune un document nou, cu valoare negativă, care trebuie el însuși declarat; a doua presupune că documentul inițial nu a existat niciodată fiscal.
- Se raportează în D394 o valoare care nu mai corespunde cu decontul de TVA (D300), pentru că facturile anulate/stornate nu au fost excluse consecvent din ambele declarații.

## Ce face iConta.eu

Din 17.09.2026, generatorul D394 (`core/repo_d394.py`) filtrează facturile după status folosind același nomenclator ca decontul de TVA (D300): facturile aflate în starea ciornă, de_preluat, descărcată, anulată sau stornată sunt excluse din calculul bazei și al TVA-ului. Comentariul din cod e explicit despre problema reparată: „D394 filtra doar TIPUL (proformă/aviz), NU statusul: o factură anulată sau stornată intra în D394 cu bază/TVA — deși D300 le exclude", cu efect măsurat de supra-declarare a operațiunilor și a rezumatului față de decont.

O limită onestă: iConta.eu **nu completează** azi câmpurile de identificare a seriilor și numerelor facturilor stornate/anulate cerute distinct de instrucțiunile ANAF (secțiunea „seria şi numărul facturilor stornate/anulate") — generatorul construiește doar seriile facturilor emise și alocate (`<serieFacturi>`), nu și lista separată de storno/anulate. Dacă acest câmp e relevant pentru firma ta, verifică manual completarea lui înainte de depunere.

[iConta.eu](/)
