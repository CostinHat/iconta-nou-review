---
title: "Ce coduri de unități de măsură se folosesc în e-Factura?"
description: De ce unitatea de măsură dintr-o factură RO e-Factura trebuie să respecte un cod standardizat, nu textul liber obișnuit de pe factura pe hârtie, și unde e ancorat legal acest standard tehnic.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce coduri de unități de măsură se folosesc în e-Factura?

Pe o factură pe hârtie poți scrie „buc", „bucată" sau „buc." fără nicio problemă. În sistemul RO e-Factura, unitatea de măsură nu e text liber — e un cod dintr-o listă standardizată, iar structura care impune asta e stabilită prin lege, nu doar prin convenție tehnică.

### Temeiul legal al structurii facturii electronice

::: ghid-temei
„Structura facturii electronice respectă: a) specificaţiile tehnice şi de utilizare a elementelor de bază ale facturii electronice aşa cum sunt prevăzute în standardul european SR EN 16931-1, care sunt aplicabile la nivel naţional; b) specificaţiile tehnice şi de utilizare a elementelor de bază ale facturii electronice - RO_CIUS - şi regulile operaţionale specifice aplicabile la nivel naţional; [...]"
— OUG 120/2021 (RO e-Factura), art. 4 alin. (1) (sursă: anaf_surse/oug_120_2021.txt)
:::

Legea nu enumeră ea însăși codurile de unități de măsură — le trimite la un standard tehnic european (SR EN 16931-1) și la specificațiile naționale de utilizare (RO_CIUS), care detaliază exact ce coduri sunt acceptate pentru fiecare tip de poziție de pe factură. Practic, RO_CIUS preia, pentru unitatea de măsură, lista de coduri standard UN/ECE Recomandarea 20 (aceleași coduri folosite în comerțul electronic european în general: de exemplu „H87" pentru bucată, „KGM" pentru kilogram, „MTR" pentru metru, „LTR" pentru litru) — nu abrevierile uzuale românești.

### De ce contează structura, nu doar conținutul

::: ghid-temei
„În situaţia în care factura electronică transmisă nu respectă structura prevăzută la alin. (1), emitentul primeşte mesaj cu erorile identificate."
— OUG 120/2021 (RO e-Factura), art. 4 alin. (5) (sursă: anaf_surse/oug_120_2021.txt)
:::

O unitate de măsură scrisă greșit (cod inexistent în lista standard, sau text liber în loc de cod) nu trece de validarea automată a sistemului — factura e respinsă cu eroare de structură, nu e doar o „imperfecțiune" tolerată.

### Poziția pe factură, ca element obligatoriu

Legea enumeră, printre elementele principale ale facturii electronice, „informațiile privind pozițiile de pe factură" — categoria în care intră, pentru fiecare linie, cantitatea și unitatea de măsură aferentă, alături de descrierea bunului/serviciului, preț unitar și cota de TVA aplicabilă.

### Ce se greșește în practică

- Se preia direct textul de pe factura veche pe hârtie („buc", „set", „pachet") fără să se mapeze la codul standard corespunzător din lista RO_CIUS — softul de facturare trebuie să facă exact această conversie, nu utilizatorul manual.
- Se presupune că unitatea de măsură e un câmp opțional sau descriptiv, când de fapt structura standardizată a facturii electronice o tratează ca element obligatoriu de validare.
- Se inventează coduri „logice" (de exemplu „BUC" în loc de codul standard corect) — validarea automată nu acceptă coduri în afara listei standardizate.
