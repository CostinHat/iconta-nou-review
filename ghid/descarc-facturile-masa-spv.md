---
title: "Cum descarc facturile în masă din SPV"
description: "De ce în iConta nu există un buton de descărcare în masă din SPV — și cum ajung totuși, automat, toate facturile primite de la furnizori."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum descarc facturile în masă din SPV

Nu există în iConta un buton „descarcă toate facturile din SPV" pe care contabilul să-l apese manual — descărcarea se întâmplă deja automat, în fundal, pentru toate facturile primite, fără nicio acțiune din partea contabilului.

## Temeiul legal

::: ghid-temei
„Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul naţional privind factura electronică RO e-Factura. Destinatarul este notificat cu privire la facturile electronice primite (...) conform procedurii prevăzute la art. 3 alin. (4)." — OUG 120/2021, art. 4 alin. (7)
:::

Legea prevede că factura electronică devine disponibilă destinatarului „pentru descărcare" din sistemul RO e-Factura, la data la care poate fi preluată din SPV. Modul tehnic prin care se face această preluare (interogarea listei de mesaje și descărcarea arhivei) ține de mecanismul pus la dispoziție de ANAF, nu de un articol separat din OUG 120/2021.

## Ce se greșește în practică

Contabilii obișnuiți cu SPV se așteaptă la un flux de tip „intru, aleg facturile, apăs descarcă" — un proces manual, punctual, pe care îl declanșează ei. În iConta procesul e inversat: nu contabilul inițiază descărcarea, ci aplicația o face singură, periodic, pentru toate facturile disponibile.

## Ce face iConta.eu

Un proces automat (rulează la fiecare 30 de minute) interoghează SPV pentru fiecare firmă conectată și preia **toate** mesajele de tip „factură primită" din ultimele 3 zile — o fereastră suprapusă, gândită tocmai ca nicio factură să nu se piardă dacă o rulare anterioară a eșuat. Fiecare factură nouă e descărcată și inserată ca ciornă, pregătită pentru validare de către contabil; facturile deja descărcate nu se reiau la rulările următoare.

Câteva limite de reținut, verificate direct în cod:
- **Nu există un buton sau un ecran din care contabilul să pornească manual o descărcare „în masă"** — frecvența și fereastra de interogare sunt fixate la nivel de server, nu configurabile din interfață.
- **Nu există o funcție de export/arhivare** a facturilor descărcate (de exemplu într-o arhivă ZIP) — XML-ul fiecărei facturi rămâne în baza de date și poate fi vizualizat individual, la cerere, din ecranul „Facturi primite".
- Descărcarea automată funcționează doar dacă firma are un cabinet conectat la SPV (autorizare ANAF activă) și un CUI valid înregistrat — altfel facturile respective nu ajung deloc în listă, fără o alertă vizibilă automat pentru contabil.

Dacă o factură așteptată nu apare, cauza cea mai probabilă e conexiunea SPV a cabinetului (token expirat) sau lipsa CUI-ului corect pe firmă, nu o problemă de „descărcare în masă" care ar trebui declanșată manual.

[iConta.eu](/)
