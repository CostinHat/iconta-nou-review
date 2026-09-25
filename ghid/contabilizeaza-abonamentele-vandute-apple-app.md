---
title: "Cum se contabilizează abonamentele vândute prin Apple App Store?"
description: "Regimul TVA aplicabil vânzărilor de abonamente digitale distribuite printr-un magazin de aplicații și de ce contează cine este considerat prestatorul din punct de vedere fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează abonamentele vândute prin Apple App Store?

Un abonament vândut printr-un magazin de aplicații (App Store, Play Store etc.) este, fiscal, un serviciu furnizat pe cale electronică. Regimul TVA aplicabil acestor servicii este special: nu se aplică regulile generale de „loc al prestării" de la sediul prestatorului, ci regulile pentru serviciile electronice către persoane neimpozabile (consumatori finali).

## Temeiul legal

::: ghid-temei
„Serviciile furnizate pe cale electronică includ, în special, serviciile prevăzute în anexa II la Directiva 112 și la art. 7 alin. (1) din Regulamentul de punere în aplicare (UE) nr. 282/2011 al Consiliului din 15 martie 2011 de stabilire a măsurilor de punere în aplicare a Directivei 2006/112/CE privind sistemul comun al taxei pe valoarea adăugată[...]. În cazul în care prestatorul unui serviciu și clientul său comunică prin intermediul poștei electronice, acest lucru nu înseamnă, în sine, că serviciul furnizat este un serviciu furnizat pe cale electronică."
— Codul fiscal (Legea 227/2015), art. 266 alin. (1) pct. 28 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Pentru serviciile furnizate pe cale electronică către o persoană neimpozabilă (utilizatorul final, persoană fizică), **locul prestării este locul unde beneficiarul este stabilit sau își are domiciliul/reședința obișnuită** — nu locul unde este stabilit prestatorul (art. 278 alin. (5) lit. h) pct. 3 din același cod).
- În lanțul de distribuție prin App Store, contractual, Apple acționează adesea ca **agent care vinde în nume propriu** utilizatorului final, în timp ce dezvoltatorul facturează către Apple (relație B2B, între persoane impozabile). Această construcție comercială schimbă cine este, din punct de vedere TVA, prestatorul „vizibil" pentru client.
- Contravaloarea încasată de la Apple (de regulă comisionul reținut este dedus, iar suma netă este virată dezvoltatorului) se înregistrează ca venit din prestări de servicii, cu factura emisă către Apple, nu către fiecare utilizator final individual.

Precizare onestă: modul exact în care Apple este calificat contractual (agent în nume propriu vs. simplu intermediar de plată) rezultă din contractul de distribuție al Apple și din prevederile europene la care Codul fiscal trimite (Regulamentul UE nr. 282/2011), text care nu se regăsește integral, articol cu articol, în corpusul verificat. Temeiul de mai sus stabilește însă cu certitudine că abonamentul vândut este, fiscal, un „serviciu furnizat pe cale electronică", cu regim de loc al prestării distinct de serviciile obișnuite.

## Ce se greșește în practică

- Se contabilizează venitul brut încasat de la utilizatori, ignorând faptul că factura reală se emite către Apple, la valoarea netă de comision.
- Se aplică regulile generale de TVA (loc al prestării la sediul prestatorului) în loc de regulile speciale pentru servicii electronice.
- Se omite verificarea calității de persoană impozabilă a Apple (facturare B2B, posibil cu taxare inversă dacă Apple e stabilit în alt stat membru sau în afara UE) și se tratează greșit ca vânzare directă către consumatori din România.
- Se confundă momentul încasării de la Apple (adesea lunar, cumulat) cu momentul prestării efective a fiecărui abonament, ceea ce poate afecta exigibilitatea TVA și recunoașterea veniturilor.

## Ce face iConta.eu

La verificarea codului, iConta.eu **nu are o funcție dedicată** pentru vânzările prin marketplace-uri de aplicații (App Store, Play Store) — nu există în aplicație un flux specific de import sau contare automată a rapoartelor de vânzări Apple/Google. Facturarea către un astfel de intermediar se poate înregistra manual, ca orice altă factură de prestări servicii către o persoană impozabilă din UE sau din afara UE, folosind funcțiile generale de facturare și contare din aplicație, dar fără o automatizare specifică pentru acest tip de raportare.

[iConta.eu](/)
