---
title: "Se declară facturile anulate în D394?"
description: "Ce înseamnă legal o factură anulată sau stornată, care dintre ele intră în D394 cu bază și TVA și cum le tratează automat iConta.eu."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Se declară facturile anulate în D394?

Legea definește destul de precis ce înseamnă „factură anulată" și „factură stornată" — două noțiuni pe care contabilii le folosesc uneori interschimbabil, deși au tratament diferit. Niciuna dintre ele nu trebuie să umfle baza și TVA raportate în D394.

## Temeiul legal

::: ghid-temei
„2.2.1. seria şi numărul facturilor stornate; factura stornată reprezintă factura emisă de persoana impozabilă, a cărei valoare totală este negativă; 2.2.2. seria şi numărul facturilor anulate; factura anulată reprezintă factura emisă de persoana impozabilă, netransmisă beneficiarului, operaţiunile înscrise în aceasta nefiind înregistrate în contabilitatea persoanei impozabile."
— OPANAF 2194/2025, Anexa 2 (sursă: [OPANAF nr. 2194/2025 pentru modificarea OPANAF nr. 3769/2015 (declarația informativă D394)](https://legislatie.just.ro/Public/DetaliiDocument/302310))
:::

- **Factura anulată**, în sensul legii, e cea care nu a ajuns niciodată la beneficiar și nu are efect în contabilitate — nu se raportează cu bază și TVA, pentru că operațiunea, practic, nu a avut loc.
- **Factura stornată** nu e factura originală, ci documentul separat, cu valoare negativă, care o anulează pe cea dintâi. Ea are, la rândul ei, statutul unei facturi „reale" — se declară precum orice altă factură, cu semn negativ.
- Declarația trebuie să conțină, distinct, seria și numărul facturilor stornate și anulate din perioada de raportare — o informație suplimentară față de baza/TVA raportate la operațiunile normale.

## Ce se greșește în practică

- Se include o factură anulată în calculul bazei și al TVA-ului din D394, ca și cum ar fi o operațiune reală.
- Se confundă „stornarea" cu „anularea" — prima presupune un document nou, cu valoare negativă, care trebuie el însuși declarat; a doua presupune că documentul inițial nu a existat niciodată fiscal.
- Se raportează în D394 o valoare care nu mai corespunde cu decontul de TVA (D300), pentru că facturile anulate nu au fost excluse, iar documentele de stornare nu au fost incluse, la fel în ambele declarații.

## Ce face iConta.eu

Din 17.09.2026, la întocmirea D394, iConta.eu exclude din calculul bazei și al TVA-ului facturile aflate în starea ciornă, descărcată, anulată sau stornată — după aceleași stări ca la decontul de TVA (D300). Înainte, D394 excludea doar proformele și avizele, nu și facturile anulate sau stornate: o factură anulată sau stornată intra în D394 cu bază și TVA, deși D300 o excludea, iar operațiunile și rezumatul ieșeau supradeclarate față de decont.

Atenție la sensul cuvântului: în aplicație, starea „stornată” marchează **factura inițială**, stornată printr-un document nou — nu documentul de stornare. Stornarea făcută din iConta.eu emite o factură nouă, cu număr nou din aceeași serie, cu liniile facturii inițiale la cantități negative și cu trimitere la ea; această factură de stornare intră în D394, ca și în D300, cu bază și TVA negative — adică „factura stornată” din definiția de mai sus, declarată cu semn negativ. Stornarea nu schimbă starea facturii inițiale: aceasta rămâne declarată, iar documentul de stornare o compensează.

O limită onestă: iConta.eu **nu completează** azi câmpurile de identificare a seriilor și numerelor facturilor stornate/anulate cerute distinct de instrucțiunile ANAF (secțiunea „seria şi numărul facturilor stornate/anulate") — aplicația completează doar seriile facturilor emise și alocate (`<serieFacturi>`), nu și lista separată de storno/anulate. Dacă acest câmp e relevant pentru firma ta, verifică manual completarea lui înainte de depunere.

[iConta.eu](/)
