---
title: "Contează ordinul de plată cu cod bugetar eronat"
description: "Ce se întâmplă când o obligație fiscală e plătită cu un cod bugetar greșit și cum se corectează eroarea la ANAF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Contează ordinul de plată cu cod bugetar eronat

Un ordin de plată către bugetul de stat greșit completat — cont bugetar eronat, cod de identificare fiscală greșit — nu înseamnă că banii se pierd sau că plata nu e valabilă. Legea tratează explicit această situație: plata rămâne valabilă de la momentul efectuării ei, iar eroarea se corectează printr-o cerere la organul fiscal, nu prin refacerea plății.

## Temeiul legal

::: ghid-temei
„(1) Plata obligațiilor fiscale efectuată într-un cont bugetar eronat este valabilă, de la momentul efectuării acesteia, în condițiile prezentului articol. La cererea debitorului, organul fiscal competent efectuează îndreptarea erorilor din documentele de plată întocmite de debitor, în suma și din contul debitorului înscrise în documentul de plată, cu condiția debitării contului acestuia și a creditării unui cont bugetar.
(5) Cererea de îndreptare a erorilor din documentele de plată poate fi depusă în termen de 5 ani, sub sancțiunea decăderii. Termenul începe să curgă de la data de 1 ianuarie a anului următor celui în care s-a efectuat plata."
— Legea 207/2015 (Codul de procedură fiscală), art. 164 alin. (1) și (5) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă concret din text:

- Plata cu cod bugetar eronat rămâne **valabilă** — nu trebuie refăcută și nu se pierde data plății inițiale (relevantă pentru penalități de întârziere).
- Corectarea se face **la cererea debitorului**, depusă la organul fiscal competent.
- Aceleași reguli se aplică și când plata a ajuns în alt buget decât cel căruia îi aparține creanța (art. 164 alin. (2)) sau când a fost folosit un cod de identificare fiscală greșit (alin. (4)).
- Termenul de a cere corectarea e de **5 ani**, calculați de la 1 ianuarie a anului următor plății, sub sancțiunea decăderii — dacă se depășește, eroarea rămâne definitivă.
- Legea acoperă și situația în care eroarea a fost generată de operatorul bancar/de decontare, caz în care organul fiscal poate îndrepta eroarea și din oficiu (art. 164 alin. (8)).

## Ce se greșește în practică

- Se reface plata „ca să fie sigur", dublând suma virată la buget, în loc să se depună doar cererea de îndreptare a erorii.
- Se crede că plata cu cod bugetar greșit generează automat penalități de întârziere, ignorând că data plății inițiale rămâne valabilă odată corectată eroarea.
- Se lasă cererea de îndreptare nedepusă la timp, riscând să treacă termenul de 5 ani — după care corectarea nu mai e posibilă.
- Se confundă corectarea unui cod bugetar eronat (art. 164) cu o cerere de restituire a unei sume nedatorate (art. 168) — sunt proceduri diferite, pentru situații diferite.

## Ce face iConta.eu

iConta.eu nu automatizează depunerea cererii de îndreptare a erorilor de plată la ANAF — aceasta e o cerere separată, în afara declarațiilor generate din aplicație, și nu am găsit în cod nicio funcție care să genereze coduri bugetare pentru ordinele de plată. Ce face aplicația e să calculeze corect scadența fiecărei obligații fiscale (D100, D112, D300 etc.), mutată automat pe prima zi lucrătoare când pică în weekend sau sărbătoare legală — util pentru a evita alt tip de eroare (plata întârziată), dar fără legătură cu corectarea unui cod bugetar greșit pe ordinul de plată.

[iConta.eu](/)
