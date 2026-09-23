---
title: Ce fac dacă primesc aceeași factură de două ori cu XML-uri diferite?
description: Dacă ANAF a trimis două mesaje diferite pentru practic aceeași operațiune, ambele pot ajunge ca ciorne separate — dar validarea celei de-a doua nu creează o cheltuială nouă, se leagă automat de prima.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce fac dacă primesc aceeași factură de două ori cu XML-uri diferite?

Situația e reală și are o explicație tehnică simplă: ANAF poate genera două mesaje distincte pentru practic aceeași operațiune (de exemplu o retransmitere sau o corecție), iar aplicația le tratează inițial ca fiind două lucruri diferite, pentru că, la nivelul mesajului, chiar sunt diferite.

## Temeiul legal

::: ghid-temei
„Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul naţional privind factura electronică RO e-Factura."

— OUG nr. 120/2021, art. 4 alin. (7)
:::

Fiecare mesaj ANAF nou devine, de sine stătător, „disponibil pentru descărcare” — legea nu cere ca sistemul destinatarului să recunoască retransmiterile drept aceeași factură inițială. Corecția facturii electronice deja comunicate urmează, separat, procedura de la art. 330 din Codul fiscal și se retransmite prin același sistem RO e-Factura (art. 4 alin. (10) OUG 120/2021) — ceea ce explică de ce poate exista, legitim, un al doilea XML pentru aceeași operațiune economică.

## De ce apar două rânduri

La descărcare, aplicația ține minte identificatorul unic al fiecărui mesaj ANAF, nu conținutul facturii. Dacă cele două XML-uri au ajuns prin mesaje ANAF cu identificatori diferiți, aplicația nu are cum să știe, doar din identificator, că se referă la aceeași factură — le descarcă pe amândouă, ca ciorne separate în lista de validat.

## Ce se întâmplă dacă le validezi pe amândouă

Aici intervine controlul real: la validare, aplicația verifică dacă există deja o factură înregistrată cu același număr, același furnizor (CUI) și aceeași dată de emitere. Dacă da, **nu creează o a doua cheltuială** — leagă a doua ciornă de factura deja existentă. Practic, chiar dacă validezi ambele rânduri, nu rezultă două cheltuieli duble în contabilitate.

Ce rămâne totuși de curățat manual: al doilea rând, chiar dacă nu produce o cheltuială nouă la validare, poate rămâne vizibil ca duplicat în lista de validat până e tratat — cel mai curat e să-l respingi, cu un motiv scurt, dacă observi din timp că e un al doilea mesaj pentru aceeași factură.

## Ce se greșește în practică

- Se presupune că al doilea XML e obligatoriu o greșeală și se ignoră complet, fără a verifica dacă e o corecție legitimă a facturii inițiale (de exemplu cu sume diferite, corectate).
- Se validează ambele rânduri fără să se compare mai întâi sumele — dacă al doilea XML e o corecție reală (nu doar o retransmitere identică), sumele pot fi diferite de primul, iar mecanismul de dedup pe număr+furnizor+dată tot le leagă de aceeași factură, ceea ce poate cere atenție suplimentară.
- Se șterge manual unul dintre rânduri (dacă interfața ar permite ceva similar) în loc de a-l respinge cu motiv, pierzând astfel trasabilitatea situației.

## Ce face iConta.eu

Deduplicarea la descărcare funcționează pe identificatorul mesajului ANAF, nu pe conținutul XML — de aceea două mesaje diferite pentru aceeași factură pot ajunge ambele ca ciorne. Deduplicarea la validare, pe număr + furnizor + dată de emitere, garantează însă că nu rezultă niciodată o cheltuială dublă în contabilitate, indiferent câte XML-uri diferite au fost descărcate pentru aceeași operațiune reală.

[iConta.eu](/)
