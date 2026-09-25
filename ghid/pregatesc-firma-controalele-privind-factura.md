---
title: "Cum pregătesc firma pentru controalele privind e-Factura"
description: "Termenul legal de transmitere a facturilor în RO e-Factura și amenzile pentru nerespectarea lui — ce trebuie să poată dovedi firma la un control."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum pregătesc firma pentru controalele privind e-Factura

Pregătirea pentru un control privind RO e-Factura nu înseamnă doar „am transmis facturile" — ANAF verifică punctual, pentru fiecare factură, dacă transmiterea s-a făcut în termenul legal. O firmă care vrea să fie pregătită trebuie să poată reconstitui, pentru orice lună, care facturi au fost transmise la timp și care nu.

## Temeiul legal

::: ghid-temei
„(6) Termenul-limită pentru transmiterea facturilor prevăzute la alin. (1)-(3) în sistemul național privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită prevăzută pentru emiterea facturii la art. 319 alin. (16) din Legea nr. 227/2015, cu modificările și completările ulterioare.
(7) Nerespectarea prevederilor alin. (6) pentru una sau mai multe facturi al căror termen-limită de transmitere în sistemul național privind factura electronică RO e-Factura intervine în cursul unei luni calendaristice constituie contravenție și se sancționează cu amendă de la 5.000 lei la 10.000 lei, pentru persoanele juridice încadrate în categoria contribuabililor mari, [...] cu amendă de la 2.500 lei la 5.000 lei, pentru persoanele juridice încadrate în categoria contribuabililor mijlocii, [...] și cu amendă de la 1.000 lei la 2.500 lei, pentru celelalte persoane juridice, precum și pentru persoanele fizice."
— Legea 296/2023, art. LIX alin. (6) și (7) (Secțiunea a 2-a, Capitolul IV) (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

Ce rezultă din text pentru pregătirea unui control:

- **Termenul curge de la două repere, nu unul singur**: 5 zile lucrătoare de la data emiterii facturii, dar niciodată mai târziu de 5 zile lucrătoare de la data-limită legală de emitere a facturii (art. 319 alin. (16) din Codul fiscal) — dacă factura a fost emisă cu întârziere, termenul de transmitere tot se calculează raportat la data-limită legală, nu la data reală de emitere.
- **Sancțiunea se aplică pe lună calendaristică, cumulat**: nu pe fiecare factură separat, ci pentru toate facturile a căror scadență de transmitere cade în aceeași lună — deci o singură amendă poate acoperi mai multe facturi întârziate din aceeași lună.
- **Amenda depinde de categoria contribuabilului**: 5.000-10.000 lei pentru contribuabili mari, 2.500-5.000 lei pentru mijlocii, 1.000-2.500 lei pentru restul persoanelor juridice și pentru persoanele fizice — pregătirea pentru control trebuie să țină cont de propria categorie.
- **Dovada la control e data reală de transmitere în sistem**, nu data emiterii facturii în evidența internă — firma trebuie să poată extrage, pentru fiecare factură, momentul confirmat de încărcare în RO e-Factura.

## Ce se greșește în practică

- Se urmărește doar dacă factura a fost „trimisă", fără să se verifice data exactă de încărcare față de termenul de 5 zile lucrătoare de la data-limită de emitere.
- Se calculează termenul de la data facturării interne, ignorând că, pentru facturile emise cu întârziere față de art. 319 alin. (16), termenul de transmitere curge oricum de la data-limită legală, nu de la data reală (mai târzie) a emiterii.
- Se presupune că sancțiunea se aplică per factură, ceea ce duce la subestimarea riscului — amenda cumulează toate întârzierile dintr-o lună calendaristică într-o singură contravenție.
- Se ignoră diferența de amendă pe categorie de contribuabil, iar firma nu-și verifică din timp încadrarea (mare/mijlociu/altele) la data controlului.

## Ce face iConta.eu

La data acestui ghid, iConta.eu automatizează transmiterea efectivă în RO e-Factura prin `core/efactura_send.py` — generarea XML-ului UBL (`genereaza_xml()`), validarea față de schema FACT1 (`valideaza()`), încărcarea (`upload_ubl()`) și interogarea stării mesajului (`stare_mesaj()`, `lista_mesaje()`). Aplicația nu are însă, la acest moment, o verificare automată explicită a încadrării în termenul de 5 zile lucrătoare din art. LIX alin. (6) — nu există o funcție dedicată care să semnaleze facturile aflate în risc de depășire a termenului sau să genereze un raport lunar de conformitate pentru pregătirea unui control. Reconstituirea istoricului de transmitere pe fiecare factură, pentru dovada la control, se face din stările interogate individual (`stare_mesaj`), nu dintr-un tablou de bord dedicat conformității.

[iConta.eu](/)
