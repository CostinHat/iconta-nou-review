---
title: "Cum se înregistrează mesele oferite gratuit influencerilor de către un restaurant?"
description: "Diferența de tratament fiscal, la TVA și la impozit pe profit, între o masă gratuită oferită unui influencer în scop de reclamă și un cadou de protocol clasic."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează mesele oferite gratuit influencerilor de către un restaurant?

Tratamentul fiscal corect depinde de scopul documentat al gratuității: dacă masa este oferită în cadrul unei înțelegeri de promovare (reclamă/publicitate, cu conținut postat de influencer), Codul fiscal o scoate din sfera TVA-ului ca „livrare către sine" și poate fi tratată drept cheltuială de reclamă, deductibilă integral; dacă e oferită fără o asemenea legătură documentată cu activitatea economică, riscă să fie încadrată drept cheltuială de protocol, cu deductibilitate limitată și, peste un anumit prag valoric, cu TVA de colectat.

## Temeiul legal

::: ghid-temei
„(8) Nu constituie livrare de bunuri, în sensul alin. (1): [...]
b) acordarea în mod gratuit de bunuri în scop de reclamă sau în scopul stimulării vânzărilor sau, mai general, în scopuri legate de desfășurarea activității economice, în condițiile stabilite prin normele metodologice;
c) acordarea de bunuri de mică valoare, în mod gratuit, în cadrul acțiunilor de sponsorizare, de mecenat, de protocol/reprezentare, în condițiile stabilite prin normele metodologice."
— Legea nr. 227/2015 (Codul fiscal), art. 270 alin. (8) lit. b), c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cele două căi posibile de tratament, cu consecințele lor:

- **Ca reclamă/publicitate** (art. 270 alin. (8) lit. b), respectiv art. 271 alin. (5) lit. b) pentru servicii): dacă restaurantul poate documenta legătura dintre masa oferită gratuit și o acțiune de promovare a activității sale (de exemplu, contract sau înțelegere cu influencerul privind conținutul postat, vizibilitatea obținută), acordarea gratuită **nu este considerată livrare de bunuri cu titlu oneros** pentru TVA — nu se colectează TVA la „autoconsum". La impozitul pe profit, cheltuiala se poate încadra la cheltuieli de reclamă și publicitate (cont 623), fără limita de 2% aplicabilă protocolului, dacă natura de reclamă e susținută de documente.
- **Ca protocol/reprezentare** (art. 270 alin. (8) lit. c), respectiv art. 25 alin. (3) lit. a) din Codul fiscal, pentru profit): dacă masa e oferită fără o legătură documentată de reclamă, ci pur și simplu ca gest de curtoazie față de un client/partener, ea intră la cheltuieli de protocol — deductibile la impozitul pe profit doar în limita a 2% din profitul contabil ajustat, iar la TVA, gratuitatea nu constituie livrare doar dacă bunul are „mică valoare", condiții stabilite prin normele metodologice; peste acest prag, TVA-ul aferent trebuie colectat ca la o livrare cu titlu oneros.
- Documentele care susțin calificarea aleasă (contract/înțelegere cu influencerul, dovada postării, obiectivul de marketing) sunt esențiale — fără ele, un control fiscal poate reîncadra operațiunea ca protocol, cu consecințele fiscale mai restrictive descrise mai sus.

## Ce se greșește în practică

- Se înregistrează mesele oferite influencerilor direct ca „protocol", fără a analiza dacă există, de fapt, o relație de promovare contractuală care ar permite încadrarea mai favorabilă la reclamă/publicitate.
- Se omite orice document care să ateste scopul de reclamă al gratuității (contract, corespondență, dovada postării), ceea ce face imposibilă susținerea calificării de „reclamă" în fața unui control.
- Se ignoră complet colectarea TVA la autoconsum atunci când valoarea meselor oferite depășește pragul de „mică valoare" stabilit prin normele metodologice pentru protocol, considerând orice gratuitate automat scutită de TVA.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are, în planul de conturi, contul 623 „Cheltuieli de protocol, reclamă și publicitate" (`core/plan_omfp.py`), pe care contabilul îl poate folosi pentru înregistrarea unor astfel de cheltuieli. Aplicația nu clasifică automat o cheltuială ca fiind „protocol" sau „reclamă/publicitate" în sensul art. 25 și art. 270 din Codul fiscal și nu calculează limita de deductibilitate de 2% pentru protocol — încadrarea corectă, pe baza documentelor justificative disponibile, rămâne o decizie a contabilului.

[iConta.eu](/)
