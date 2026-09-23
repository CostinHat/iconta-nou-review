---
title: Cum corectez o factură înregistrată pe clientul greșit?
description: O factură emisă, atribuită greșit altui client, nu se editează în iConta.eu. Fără notă contabilă, se șterge și se reintroduce pe clientul corect. Cu notă contabilă, corecția se face prin stornare — o factură nouă, cu liniile negate, urmată de factura corectă pe clientul real.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez o factură înregistrată pe clientul greșit?

O factură emisă pe clientul greșit poartă un venit real, dar atribuit unei alte firme decât cea căreia i-a fost livrat efectiv bunul sau serviciul. Ca la orice factură deja introdusă, nu există în iConta.eu o funcție de editare a câmpului „client" — corecția depinde de stadiul facturii.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ." — Legea contabilității nr. 82/1991, art. 6 alin. (1)

„În cazul stornărilor, pe documentul inițial se menționează numărul și data notei de contabilitate prin care s-a efectuat stornarea operațiunii, iar în nota de contabilitate de stornare se menționează documentul, data și numărul de ordine ale operațiunii care face obiectul stornării." — OMFP 2634/2015, pct. 20
:::

Regula de mai sus e temeiul direct al legăturii ținute de aplicație între factura originală și cea de stornare (`storno_din_id`) — nu e o simplă convenție internă, ci o cerință a documentelor financiar-contabile.

## Cum corectez în iConta.eu

- **Factura nu are încă notă contabilă** → se șterge și se reintroduce pe clientul corect.
- **Factura are notă contabilă** (deja contată) → ștergerea e refuzată explicit, cu mesajul: „Factura are notă contabilă și nu se mai șterge: o notă ștearsă lasă o gaură în evidență. Corecția unei facturi contabilizate se face prin STORNO." Corecția e prin `storneaza()`: funcția confirmată în cod pentru facturile **emise** — creează o factură nouă, cu liniile din original negate, număr nou din aceeași serie, legată de original prin `storno_din_id`, păstrând cursul valutar și clasificarea originalului (axă IC, taxare inversă etc.).
- După stornare, se introduce factura nouă, cu clientul corect — stornoul anulează operațiunea greșită, dar nu o înlocuiește automat cu cea reală.
- Dacă factura are deja statutul `anulata` sau `stornata`, aplicația refuză o nouă notă de contare pe ea, cu mesajul „o stornare se declară prin documentul ei nou" — nu se mai poate contabiliza a doua oară un document deja anulat.
- Perioada contabilă închisă blochează atât ștergerea, cât și stornarea sau contarea facturii noi, dacă luna e blocată administrativ.

## Ce se greșește în practică

- Se șterge sau se „anulează" manual factura din alte module, fără să treacă prin funcția de stornare — aplicația refuză ștergerea unei facturi cu notă de contare tocmai pentru asta.
- Se stornează factura, dar se uită introducerea celei corecte, pe clientul real — rezultă doar o anulare, fără evidența operațiunii economice reale.
- Se încearcă o a doua stornare sau contare pe o factură deja stornată — blocată explicit de poarta care verifică statutul `anulata`/`stornata`.

## Ce face iConta.eu

O factură emisă pe clientul greșit nu se editează. Fără notă contabilă, se șterge și se reintroduce corect. Cu notă contabilă, aplicația refuză ștergerea și oferă stornarea: o factură nouă, cu liniile negate și legată explicit de original, urmată de factura corectă pe clientul real. Corespondența dintre documentul original și cel de stornare e păstrată automat prin identificator, așa cum cer normele pentru documentele de stornare.

[iConta.eu](/)
