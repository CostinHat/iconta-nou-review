---
title: "Se calculează CMP după fiecare intrare sau lunar?"
description: "Ce spune legea despre cele două variante de calcul al costului mediu ponderat și care dintre ele o folosește efectiv iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se calculează CMP după fiecare intrare sau lunar?

Contabilii care lucrează cu evidența cantitativ-valorică a stocurilor se lovesc adesea de această întrebare, pentru că răspunsul corect nu este „doar una din variante" — legea permite ambele, dar sistemele de gestiune, de regulă, implementează efectiv doar una singură. Iată ce spune reglementarea și ce alege să facă iConta.eu.

## Temeiul legal

::: ghid-temei
„(2) Metoda «costului mediu ponderat» (CMP) presupune calcularea costului fiecărui element pe baza mediei ponderate a costurilor elementelor similare aflate în stoc la începutul perioadei și a costului elementelor similare produse sau cumpărate în timpul perioadei. Media poate fi calculată periodic sau după fiecare recepție. Perioada de calcul nu trebuie să depășească durata medie de stocare."
— OMFP 1802/2014, pct. 96 alin. (2) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- „Periodic" înseamnă, în practică, recalcul lunar sau la un alt interval fix ales de firmă — o singură medie ponderată valabilă pentru toate ieșirile din acea perioadă.
- „După fiecare recepție" înseamnă recalcul de fiecare dată când intră marfă la un preț nou — CMP-ul se schimbă imediat, iar ieșirile ulterioare din aceeași zi pot avea deja un cost diferit de cele dinaintea intrării.
- Limita comună celor două variante: perioada de calcul (dacă se alege varianta periodică) nu poate depăși durata medie de stocare a mărfii respective.
- Legea nu spune care variantă e „mai corectă" — ambele sunt metode acceptate, iar alegerea rămâne o decizie de politică contabilă a entității.

## Ce se greșește în practică

- Se crede greșit că OMFP 1802/2014 impune o singură metodă de recalcul — textul folosește explicit „sau", nu „doar".
- Se schimbă varianta de calcul în mijlocul unui exercițiu financiar, ceea ce face evidența greu de reconstituit și de verificat la un control.
- Se raportează CMP-ul recalculat după fiecare intrare ca fiind „media lunară", deși cele două valori pot diferi semnificativ când prețurile de achiziție variază des în cursul lunii.

## Ce face iConta.eu

iConta.eu implementează exclusiv varianta „**recalcul după fiecare intrare**" (recepție), niciodată varianta periodică/lunară, pentru modulul de stocuri cantitativ-valorice. Motorul de calcul (`core/stocuri_cv.py`) actualizează cantitatea și valoarea totală din stoc la fiecare mișcare de intrare, iar costul mediu ponderat curent se obține prin împărțirea valorii totale la cantitatea totală, imediat, fără să aștepte finalul lunii. Comportamentul e verificat printr-un test dedicat exact acestui scenariu (recalculul CMP-ului după o intrare intermediară).

Este important de spus onest: aceasta e **alegerea tehnică a iConta**, una dintre cele două variante permise expres de lege — nu singura variantă legală. Dacă firma preferă varianta cu recalcul periodic (lunar), aplicația nu oferă acest mod de lucru în cadrul modulului de stocuri cantitativ-valorice la CMP.

[iConta.eu](/)
