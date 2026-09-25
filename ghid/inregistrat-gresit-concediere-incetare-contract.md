---
title: "Ce fac dacă am înregistrat greșit o concediere sau o încetare de contract?"
description: "Legea permite corectarea erorilor din registrul de evidență a salariaților la data la care angajatorul le observă — iar aplicația păstrează exact acest mecanism pentru data încetării unui contract."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă am înregistrat greșit o concediere sau o încetare de contract?

O dată de încetare a contractului introdusă greșit — prea devreme, la o persoană greșită sau pur și simplu dintr-o eroare de tastare — nu trebuie „ascunsă" prin ștergerea salariatului din evidență. Legea prevede explicit un mecanism de corecție a erorilor din registrul de evidență a salariaților, iar felul în care se face corecția contează pentru ce rămâne, de fapt, în istoricul firmei.

## Temeiul legal

::: ghid-temei
„Orice corecție a erorilor survenite în completarea Registrului se face la data la care angajatorul a luat cunoștință de acestea."
— HG 295/2025 privind Registrul general de evidență a salariaților (REGES-ONLINE), art. 5 alin. (8) (sursă: anaf_surse/hg_295_2025_reges_online_registru_salariati.txt)
:::

- Legea distinge clar: data reală a încetării contractului e diferită de data la care angajatorul **corectează** o eroare — corecția se raportează la momentul în care eroarea a fost observată, nu se rescrie retroactiv ca și cum nu ar fi existat.
- Transmiterea datei de încetare în Registru se face „cel târziu la data încetării contractului individual de muncă/la data luării la cunoștință a evenimentului ce a determinat [...] încetarea" (art. 5 alin. (1) lit. f) din același act) — deci și termenul inițial, și corecția lui, sunt legate de momentul constatării, nu de un termen fix, uniform.
- Răspunderea pentru corectitudinea datelor din Registru rămâne, prin lege, exclusiv a angajatorului, indiferent de aplicația folosită pentru evidența internă.

## Ce se greșește în practică

- Se șterge salariatul complet din evidență, în loc să se corecteze sau să se anuleze data încetării introdusă greșit — ștergerea pierde tot istoricul (salarii, pontaj), pe când corectarea datei păstrează totul intact.
- Se lasă câmpul „dată încetare" completat cu o valoare greșită, fără să se realizeze că trebuie golit explicit (nu doar lăsat necompletat la următoarea editare) pentru ca sistemul să recunoască din nou contractul ca activ.
- Se presupune că e suficient să corectezi data internă și că REGES-ONLINE „se aliniază" automat — corectarea trebuie dusă la capăt și acolo, separat.

## Ce face iConta.eu

Din ecranul **Stat de plată**, butonul **„Încetare"** al fiecărui salariat (afișat „Plecat <dată>" odată completată data) deschide câmpul „Data încetării contractului" și permite atât introducerea, cât și corectarea sau **anularea completă** a unei date de încetare greșite — un câmp gol la data încetării înseamnă, pentru aplicație, contract activ. Mecanismul din spate permite explicit golirea unei valori deja salvate (distinct de „nu am trimis câmpul"), exact pentru cazul unei încetări introduse greșit, care trebuie retrasă complet, nu doar suprascrisă. La ștergere, aplicația e restrictivă: refuză hard-delete-ul unui salariat dacă acesta are luni deja declarate (concedii medicale, o perioadă confirmată de pontaj/salarizare sau o declarație 112 depusă) — protecție rezervată greșelilor de introducere, nu plecării reale a unui angajat. De reținut, onest: butonul de ștergere nici nu e disponibil azi în interfață, deci în practică singura cale corectă din ecran e exact corectarea datei încetării. iConta.eu **nu retransmite** corecția către REGES-ONLINE. Transmiterea către REGES-ONLINE nu e nici automată la creare: se face manual, printr-un buton separat („Trimite în REGES"), și acoperă doar identitatea salariatului (CNP, nume, prenume) — nu există în aplicație niciun mecanism, manual sau automat, care să trimită spre REGES-ONLINE data încetării contractului. Actualizarea acestei date în Registru rămâne, integral, o obligație pe care utilizatorul o îndeplinește separat, direct pe platforma Inspecției Muncii.

[iConta.eu](/)
