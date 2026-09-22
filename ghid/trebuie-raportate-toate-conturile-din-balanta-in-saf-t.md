---
title: Trebuie raportate toate conturile din balanță în SAF-T?
description: Nu — se raportează doar conturile care există în nomenclatorul oficial al normei contabile declarate de firmă; conturile "străine" acelui nomenclator sunt excluse automat din fișierul XML.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Trebuie raportate toate conturile din balanță în SAF-T?

Un contabil care se uită prima dată la o declarație D406 generată se poate întreba de ce nu regăsește în `GeneralLedgerAccounts` absolut toate conturile din balanța de verificare a firmei. Răspunsul: nu, iar acest lucru e corect din punct de vedere legal — nu orice cont din balanță aparține automat nomenclatorului oficial al normei contabile a firmei.

## Temeiul legal

::: ghid-temei
"|Customers (Clienţi) | Conţine informaţii despre clienţi, precum detaliile de identificare
(denumire, adresa, cod de înregistrare fiscală), contul analitic în care este înregistrat
soldul clientului respectiv, soldul iniţial debitor/creditor, sold final debitor/creditor
etc."
(opanaf_1783_2021_saft_d406.txt, Anexa 1, pct. 5, tabelul cu structura AuditFile)

"NOTĂ: Secţiunea "Taxonomies" (Taxonomii) nu va trebui raportată în D406."
(opanaf_1783_2021_saft_d406.txt, Anexa 1, pct. 5, nota de sub tabel)
:::

## De ce lipsesc unele conturi

Nomenclatorul oficial ANAF pentru fiecare normă contabilă (societăți comerciale, IFRS, bancar, ONG etc.) definește explicit ce conturi sunt acceptate în validarea SAF-T. Dacă firma are, în balanța ei, conturi care nu aparțin nomenclatorului normei declarate — de exemplu conturi specifice altui tip de entitate — acele conturi sunt excluse din `GeneralLedgerAccounts`, altfel validatorul oficial le-ar respinge direct.

::: ghid-exemplu
Conturile 731-738 (venituri specifice contabilității ONG, OMFP 3103/2017) apar uneori implicit în balanța unei firme, deși aceasta funcționează sub norma "societăți comerciale" (OMFP 1802/2014). Aceste conturi nu există în nomenclatorul acelei norme, deci sunt filtrate din SAF-T — validatorul oficial ar respinge fișierul cu mesajul "ID-ul contului [731] trebuie să se găsească în planul de conturi" dacă ar fi incluse.
:::

Deci regula corectă este: se raportează conturile din balanță care se regăsesc în nomenclatorul oficial al normei contabile a firmei — nu absolut toate conturile care apar în balanța internă.

## Ce se greșește în practică

- Se așteaptă ca toate conturile din balanța de verificare să apară automat în declarație, fără a ține cont de nomenclatorul normei contabile aplicabile.
- Se introduc manual conturi specifice altei norme contabile (ex. conturi ONG pe o firmă comercială), fără să se observe că acestea nu vor fi raportate.
- Nu se verifică dacă lista conturilor excluse ("străine" de normă) este afișată vizibil contabilului înainte de depunere — dacă un cont e exclus tacit, o eroare de mapare a normei poate trece neobservată.
- Se raportează secțiunea "Taxonomies", care norma spune explicit că nu trebuie inclusă în D406.

## Ce face iConta.eu

Filtrarea este automată: la construirea declarației, conturile din balanța firmei care nu se regăsesc în nomenclatorul oficial al normei contabile declarate sunt excluse din `GeneralLedgerAccounts` și colectate separat, într-o listă distinctă de conturi "străine" normei. Nu s-a putut confirma, în verificarea efectuată, dacă această listă de conturi excluse ajunge integral în avertismentele afișate contabilului la generare — recomandarea este ca, în cazul unei firme cu conturi neobișnuite pentru norma ei contabilă, contabilul să verifice manual, înainte de depunere, dacă toate conturile relevante cu mișcări apar în XML-ul generat.

[iConta.eu](/)
