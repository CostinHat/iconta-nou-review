---
title: "Ce se întâmplă dacă un SRL nou face prima achiziție intracomunitară?"
description: "Ce trebuie verificat înainte de prima achiziție intracomunitară de bunuri a unui SRL nou-înființat: cod de TVA, prag de 10.000 euro și înregistrarea specială."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce se întâmplă dacă un SRL nou face prima achiziție intracomunitară?

Un SRL nou-înființat care face prima achiziție de bunuri dintr-un alt stat membru UE trebuie, înainte de orice altceva, să clarifice propriul statut TVA — pentru că de el depinde cum se facturează achiziția.

## Temeiul legal

::: ghid-temei
CF art. 268 alin. (5)/(6) — plafon 10.000 €: „…valoarea totală a acestor achiziții intracomunitare nu depășește pe parcursul anului calendaristic curent sau nu a depășit pe parcursul anului calendaristic anterior plafonul de 10.000 euro, al cărui echivalent în lei este stabilit prin normele metodologice.” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L16639)

CF art. 317: „Înregistrare specială pentru neplătitori care fac AIC peste plafon sau servicii IC (alin. 1 lit. a-d).” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L21049-21160+)
:::

Dacă firma e deja înregistrată normal ca plătitoare de TVA (art. 316), prima achiziție intracomunitară de bunuri urmează regula obișnuită: furnizorul UE facturează fără TVA (dacă are cod de TVA valid al cumpărătorului), iar firma din România calculează TVA prin taxare inversă și declară operațiunea în D390.

Dacă firma **nu** e plătitoare de TVA (caz frecvent la un SRL nou, sub plafonul de scutire), regula depinde de plafonul de 10.000 euro pentru achiziții intracomunitare de bunuri: sub acest plafon, furnizorul poate factura cu TVA-ul propriei țări, iar firma din România nu are, doar din acest motiv, obligația înregistrării speciale. Peste plafon — sau dacă firma optează pentru regimul de taxare la destinație — devine necesară înregistrarea specială în scopuri de TVA (art. 317), înainte de a continua astfel de achiziții.

**Atenție:** pragul de 10.000 euro se calculează cumulat, pe an calendaristic — o singură achiziție mare poate depăși singură plafonul.

## Ce se greșește în practică

- Se presupune că, fiind neplătitoare de TVA, firma nu are nicio obligație legată de o achiziție din UE — de fapt tocmai acest statut poate declanșa nevoia înregistrării speciale, dacă plafonul e depășit.
- Se așteaptă apariția unei probleme (factură contestată, control) înainte de a verifica dacă înregistrarea specială era necesară.
- Se confundă înregistrarea specială art. 317 cu înregistrarea normală de plătitor de TVA (art. 316) — sunt regimuri diferite.

## Ce face iConta.eu

Profilul firmei conține câmpurile `operatiuni_ic` (Da/Nu — decide D390/VIES) și `inreg_art317` (Înregistrată art. 317), care influențează direct corectitudinea D390 și marcajul `pers_inreg` în D301.

**Important:** cercetarea care stă la baza acestui ghid nu a găsit, în codul citit, o urmărire automată, cumulativă pe an, a plafonului de 10.000 euro pentru achiziții intracomunitare de bunuri — câmpul `inreg_art317` e un flag manual, bifat de utilizator, nu rezultatul unui calcul automat al aplicației. Verificarea depășirii plafonului rămâne, pe baza acestei cercetări, în sarcina firmei/contabilului, la fiecare achiziție intracomunitară nouă.

[iConta.eu](/)
