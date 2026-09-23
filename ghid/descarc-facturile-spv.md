---
title: Cum descarc facturile din SPV?
description: Nu există niciun buton de descărcat — facturile primite de la furnizori prin RO e-Factura ajung singure în aplicație, la fiecare jumătate de oră, cât timp cabinetul e conectat la SPV.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum descarc facturile din SPV?

Scurt: nu le descarci tu. Un proces programat interoghează periodic sistemul ANAF și aduce singur facturile noi primite de la furnizori — tu doar le găsești deja în aplicație, în lista de facturi de validat.

## Temeiul legal

::: ghid-temei
„Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul naţional privind factura electronică RO e-Factura. Destinatarul este notificat cu privire la facturile electronice primite (...) conform procedurii prevăzute la art. 3 alin. (4)."

— OUG nr. 120/2021, art. 4 alin. (7)
:::

Legea leagă momentul „primirii” facturii de momentul în care ea devine disponibilă pentru descărcare în SPV — nu de un moment ales de destinatar. Practic, e obligația legală a acestei disponibilități care justifică de ce descărcarea propriu-zisă e automatizată, nu lăsată pe seama unui click manual.

## Cum ajunge efectiv factura la tine

Un proces rulează în fundal la fiecare 30 de minute și interoghează ANAF pentru firma ta, cerând mesajele noi marcate „factură primită”. Pentru fiecare mesaj găsit, verifică întâi că factura chiar aparține firmei tale (nu alteia din același cabinet), apoi verifică dacă nu a mai fost adusă și o descarcă, dacă e nouă.

Rezultatul apare direct în lista de facturi primite, ca ciornă gata de validat — cu furnizorul, numărul, data și sumele deja extrase din XML, plus un cont de cheltuială sugerat, dacă mai ai facturi anterioare de la același furnizor.

Ca să funcționeze deloc, e nevoie ca cel puțin: cabinetul tău să aibă o conexiune SPV activă (autentificare la ANAF) și firma să aibă CUI-ul completat în profil. Fără aceste două condiții, procesul nu are ce interoga.

## Ce se greșește în practică

- Se caută un buton „Descarcă din SPV” în interfață — nu există, pentru că descărcarea nu e o acțiune a contabilului, ci un proces care rulează deja, indiferent dacă ești logat sau nu.
- Se crede că factura „nu s-a descărcat” pentru că nu apare încă printre cheltuieli — de fapt ea poate fi deja adusă ca ciornă, doar că nu a fost încă validată de contabil.
- Se așteaptă o descărcare instantanee — pot trece până la 30 de minute, pentru că procesul rulează la intervale fixe, nu la fiecare secundă.

## Ce face iConta.eu

Descărcarea din SPV e complet automată: un proces programat rulează la fiecare 30 de minute, folosind conexiunea SPV a cabinetului, și aduce facturile noi ca ciorne în lista „facturi de validat”. Nu creează nicio cheltuială automat — contul contabil rămâne o decizie a ta, la validare. Dacă nu apare nicio factură nouă, primul lucru de verificat e conexiunea SPV a cabinetului și CUI-ul firmei din profil — aplicația nu afișează încă un contor sau o alertă dedicată pentru acest caz.

[iConta.eu](/)
