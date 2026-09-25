---
title: "Ce fac dacă salariile plătite nu corespund cu statul de plată?"
description: "Ce prevede legea despre dovada plății salariului și cum se investighează o neconcordanță între suma efectiv plătită și statul de plată al lunii."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă salariile plătite nu corespund cu statul de plată?

Statul de plată arată cât se datorează fiecărui salariat. Ce a ieșit efectiv din contul firmei sau din casierie e altă informație — și, atunci când cele două nu coincid, cauza cea mai frecventă nu e o greșeală de calcul în stat, ci ceva petrecut la nivelul plății propriu-zise: un IBAN greșit, o plată parțială, un salariat omis dintr-un ordin de plată colectiv.

## Temeiul legal

::: ghid-temei
„(1) Plata salariului se dovedeşte prin semnarea statelor de plată, precum şi prin orice alte documente justificative care demonstreaza efectuarea plăţii către salariatul îndreptăţit.
(2) Statele de plată, precum şi celelalte documente justificative se păstrează şi se arhiveaza de către angajator în aceleaşi condiţii şi termene ca în cazul actelor contabile, conform legii."
— Legea 53/2003 (Codul muncii), art. 163 alin. (1)-(2) (sursă: anaf_surse/legea_53_2003_codul_muncii.txt)
:::

- Legea cere DOUĂ lucruri distincte pentru a dovedi plata: statul de plată (ce se datorează) și „orice alte documente justificative" (ordinul de plată, extrasul de cont, chitanța) care arată ce s-a plătit efectiv — o neconcordanță se investighează comparând cele două, nu presupunând că unul dintre ele e automat corect.
- Ambele categorii de documente trebuie păstrate și arhivate în aceleași condiții ca actele contabile — deci, la o neconcordanță descoperită ulterior, trebuie să existe încă acces la dovada plății, nu doar la statul de plată.
- Termenul de prescripție pentru drepturi salariale neexecutate integral e de 3 ani (art. 166 alin. (1), Codul muncii) — o neconcordanță găsită la câteva luni distanță e, de regulă, încă recuperabilă.

## Ce se greșește în practică

- Se confundă statul de plată cu dovada plății efective — sunt documente diferite prin natura lor, iar unul nu înlocuiește legal pe celălalt.
- Se descoperă abia la reconcilierea bancară de sfârșit de lună că un salariat n-a fost plătit deloc, pentru că IBAN-ul lui era greșit sau lipsă în firmă, iar plata s-a făcut doar pentru restul angajaților.
- Se presupune că o plată parțială sau întârziată „se rezolvă de la sine" — legea prevede explicit că întârzierea nejustificată sau neplata poate obliga angajatorul la daune-interese (art. 161 alin. (4), Codul muncii).

## Ce face iConta.eu

Statul de plată (F087) e sursa cifrei pe care se bazează plata, dar nu verifică el însuși dacă suma respectivă a ajuns efectiv la salariat — asta e domeniul unei funcționalități separate din aplicație, cea de plată a salariilor pe card printr-un fișier bancar. Acolo, netul calculat de statul de plată alimentează fișierul de plată, dar cu o regulă explicită de siguranță: fișierul se generează DOAR pentru salariații cu IBAN valid; cei fără IBAN valid sunt excluși din plată și raportați ca atare, nu plătiți tacit sau ignorați silențios.

Deci, dacă suma efectiv plătită nu corespunde cu statul de plată, cauza cea mai probabilă de verificat întâi e exact acolo — un IBAN greșit sau lipsă, un salariat exclus dintr-o rulare de plată colectivă, sau o plată efectuată prin alt canal decât cel evidențiat în aplicație. Statul de plată din F087 rămâne, prin construcție, documentul „cât se datorează", nu un instrument de reconciliere cu extrasul bancar.

[iConta.eu](/)
