---
title: "Cum resetez parola în SPV"
description: "De ce firmele nu au propriu-zis o 'parolă' în SPV, ci se identifică prin certificat digital calificat, conform OMFP 660/2017."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum resetez parola în SPV

Întrebarea "cum resetez parola" ascunde adesea o confuzie de fond: pentru o firmă (persoană juridică), accesul la Spațiul Privat Virtual nu se face cu utilizator și parolă, ca la un cont obișnuit, ci prin certificat digital calificat. "Parola" în sensul clasic există doar pentru persoanele fizice care se autentifică prin sistemul NPOTP, pentru obligațiile lor personale.

## Temeiul legal

::: ghid-temei
„(1) Persoanele juridice sau alte entităţi fără personalitate juridică se identifică electronic cu certificate calificate. (2) Persoanele fizice care au calitatea de reprezentant sau de împuternicit al unei persoane fizice, persoane juridice sau al altei entităţi fără personalitate juridică se identifică electronic cu certificate calificate."
— OMFP 660/2017, art. 6 alin. (1)-(2) (sursă: anaf_surse/omfp_660_2017.txt)
:::

Ce rezultă de aici pentru o firmă:

- Accesul unei persoane juridice (sau al reprezentantului/împuternicitului ei) în SPV se face prin **certificat digital calificat**, nu prin combinație utilizator-parolă — "resetarea parolei", în sensul obișnuit, nu se aplică acestui tip de acces.
- Dacă certificatul digital a expirat, a fost pierdut sau compromis, soluția nu e o "resetare de parolă", ci obținerea unui certificat digital calificat nou, de la un furnizor acreditat, urmată de o nouă înregistrare/asociere a certificatului cu contul din SPV.
- Doar persoanele fizice care nu acționează pentru obligațiile fiscale ale unei persoane juridice (de exemplu un PFA pentru anumite obligații, sau o persoană fizică fără activitate economică) se pot identifica prin NPOTP (nume + parolă + cod OTP) — pentru acest tip de acces, resetarea se face prin procedura ANAF de recuperare a identității electronice, separată de certificatul digital.

## Ce se greșește în practică

- Se caută o funcție de "resetare parolă" în interfața SPV pentru contul firmei, deși accesul firmei nu funcționează niciodată cu parolă, ci exclusiv cu certificat calificat.
- Se confundă certificatul digital calificat folosit pentru autentificare (identitatea persoanei/entității) cu tokenul OAuth folosit de aplicațiile terțe pentru conectarea automată la API-urile ANAF (de exemplu pentru e-Factura) — sunt mecanisme diferite, cu proceduri diferite de reînnoire.
- Se așteaptă ca un contabil extern să poată "reseta" accesul firmei fără o împuternicire valabilă și fără propriul certificat digital — accesul e legat de identitatea electronică a persoanei autorizate, nu transferabil informal.

## Ce face iConta.eu

Conexiunea iConta.eu cu ANAF (pentru e-Factura, e-Transport și celelalte fluxuri automatizate) se face printr-un conector OAuth2 propriu, cu token stocat criptat și reînnoit automat prin rotație — un mecanism separat de contul SPV al firmei accesat direct de om, prin browser, cu certificat digital. iConta.eu nu resetează și nu gestionează certificatul digital calificat al firmei sau accesul uman în portalul SPV — acestea rămân în afara aplicației, gestionate direct cu ANAF și cu furnizorul certificatului.

[iConta.eu](/)
