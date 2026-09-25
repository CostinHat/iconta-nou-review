---
title: "Data comunicării prin e-Factura schimbă dreptul de deducere a TVA?"
description: "Diferența dintre momentul în care factura electronică e considerată acceptată și momentul în care ia naștere dreptul de deducere a TVA."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Data comunicării prin e-Factura schimbă dreptul de deducere a TVA?

Nu. Legea RO e-Factura fixează o dată de „acceptare" a facturii electronice între emitent și destinatar — utilă pentru raporturile lor comerciale — dar dreptul de deducere a TVA rămâne guvernat exclusiv de Codul fiscal, care îl leagă de exigibilitatea taxei, nu de data comunicării în sistemul e-Factura.

## Temeiul legal

::: ghid-temei
„Dreptul de deducere ia naștere la momentul exigibilității taxei."
— Legea 227/2015 (Codul fiscal), art. 297 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

Cele două reguli, din surse diferite, nu trebuie confundate:

- **OUG 120/2021, art. 11**: „În cazul în care emitentul și destinatarul facturii electronice sunt înregistrați în Registrul RO e-Factura [...], utilizarea facturii electronice este considerată acceptată la data comunicării în sistemul național privind factura electronică RO e-Factura." Această regulă privește doar acceptarea facturii ca document electronic valabil, nu momentul dreptului de deducere.
- **CF art. 299 alin. (1) lit. a)**: pentru exercitarea dreptului de deducere, persoana impozabilă trebuie „să dețină o factură emisă în conformitate cu prevederile art. 319" — condiția e deținerea unei facturi valabile, nu data la care sistemul RO e-Factura o „comunică" drept acceptată.
- **Concluzia**: dreptul de deducere se raportează la exigibilitatea taxei (de regulă, data emiterii/livrării, conform regulilor generale de exigibilitate), iar deținerea facturii e o condiție de formă pentru exercitarea acestui drept, nu momentul care îl declanșează.

## Ce se greșește în practică

- Se amână deducerea TVA până la data comunicării facturii în sistemul RO e-Factura, tratând-o greșit ca moment al nașterii dreptului de deducere.
- Se confundă „acceptarea" facturii electronice (efect al art. 11 din OUG 120/2021, relevant pentru relația comercială emitent-destinatar) cu condițiile de deducere a TVA, guvernate separat de art. 297 și art. 299 din Codul fiscal.
- Se ignoră regimul special al TVA la încasare (art. 297 alin. 2-3), unde dreptul de deducere e într-adevăr amânat — dar până la plata efectivă către furnizor, nu până la data comunicării electronice a facturii.

## Ce face iConta.eu

iConta.eu trimite și primește facturi prin sistemul RO e-Factura (`core/efactura_send.py`), fără să facă distincție de tratament fiscal în funcție de forma juridică a firmei. Aplicația nu am identificat-o legând momentul deducerii TVA de data comunicării facturii în sistemul e-Factura — deducerea rămâne calculată după regulile generale de exigibilitate din decontul de TVA (D300), conform art. 297 și 299 din Codul fiscal.

[iConta.eu](/)
