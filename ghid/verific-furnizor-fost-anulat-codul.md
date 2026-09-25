---
title: "Cum verific dacă unui furnizor i-a fost anulat codul de TVA?"
description: "Registrul public al ANAF unde se verifică dacă un furnizor are codul de înregistrare în scopuri de TVA activ sau anulat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific dacă unui furnizor i-a fost anulat codul de TVA?

Verificarea se face pe un registru public al ANAF, în afara oricărei aplicații de contabilitate — legea obligă fiscul să publice acest registru, tocmai pentru ca orice cumpărător să poată verifica statutul unui furnizor înainte de a-i deduce TVA-ul.

## Temeiul legal

::: ghid-temei
„A.N.A.F. organizează Registrul persoanelor impozabile înregistrate în scopuri de TVA conform art. 316 și Registrul persoanelor impozabile a căror înregistrare în scopuri de TVA conform art. 316 a fost anulată. Registrele sunt publice și se afișează pe site-ul A.N.A.F."
— Legea 227/2015 (Codul fiscal), art. 316 alin. (15) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din text:

- Legea obligă ANAF să țină **două registre publice**: unul cu persoanele înregistrate în scopuri de TVA și unul separat cu cele al căror cod a fost **anulat**.
- Ambele registre sunt **publice** și **afișate pe site-ul ANAF** — verificarea nu cere autentificare sau relație contractuală cu furnizorul, e disponibilă oricui.
- Verificarea în acest registru e utilă direct pentru problema deducerii TVA: dacă furnizorul apare în registrul persoanelor cu cod anulat, cumpărătorul trebuie să identifice și **motivul** anulării (unul din cele opt de la art. 316 alin. (11)), pentru că doar anumite motive (lit. c)-e) și h)) duc la pierderea dreptului de deducere a TVA aferente achizițiilor din acea perioadă.

## Ce se greșește în practică

- Se presupune că verificarea codului de TVA al unui partener se face doar prin VIES (registrul european pentru coduri de TVA valide comunitar) — pentru un furnizor din România, registrul relevant pentru anulare/reactivare e cel administrat direct de ANAF, distinct de VIES.
- Se verifică furnizorul o singură dată, la începutul relației comerciale, și nu se repetă verificarea periodic — codul poate fi anulat ulterior, iar riscul de nededucere privește fiecare achiziție făcută în perioada de anulare, nu doar momentul inițial.
- Se oprește verificarea la constatarea „cod anulat", fără să se identifice și motivul anulării — consecința asupra deducerii TVA depinde strict de acel motiv (vezi Codul fiscal art. 11 alin. (8)-(9)).

## Ce face iConta.eu

Verificarea statutului de TVA al unui furnizor în registrul public al ANAF e un proces **complet extern** aplicației — iConta.eu nu are azi o integrare cu acest registru și nu verifică automat, la introducerea unei facturi de achiziție, dacă furnizorul are codul de TVA activ sau anulat. Contabilul trebuie să facă această verificare direct pe site-ul ANAF, în afara aplicației, înainte de a decide dacă TVA-ul de pe o factură de la furnizorul respectiv poate fi dedus.

[iConta.eu](/)
