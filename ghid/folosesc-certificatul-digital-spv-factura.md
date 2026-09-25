---
title: "Cum folosesc certificatul digital în SPV pentru e-Factura?"
description: "De ce persoanele juridice și PFA-urile nu se pot identifica în SPV decât cu certificat calificat, potrivit Codului de procedură fiscală."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum folosesc certificatul digital în SPV pentru e-Factura?

Certificatul digital calificat nu este o opțiune „mai sigură" pentru accesul la SPV — pentru firme și PFA-uri este singura metodă de identificare permisă de lege. Fără el, contul SPV nu poate fi folosit pentru RO e-Factura.

## Temeiul legal

::: ghid-temei
„(1) Contribuabilul/Plătitorul care depune cereri, înscrisuri sau documente la organul fiscal, prin mijloace electronice de transmitere la distanţă, se identifică în relaţia cu organul fiscal astfel:
a) persoanele juridice, asocierile şi alte entităţi fără personalitate juridică, precum şi persoanele fizice care desfăşoară activităţi economice în mod independent ori exercită profesii libere se identifică numai cu certificate calificate;
b) persoanele fizice, altele decât cele prevăzute la lit. a), se identifică prin intermediul furnizorilor de servicii publice de autentificare electronică autorizaţi potrivit legii sau prin diverse dispozitive, cum ar fi certificat calificat, credenţiale de tip utilizator/parolă însoţite de liste de coduri de autentificare de unică folosinţă, telefon mobil, digipass ori alte dispozitive [...]"
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 80 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Distincția din lege este clară și are consecințe practice directe:

- **Persoanele juridice, PFA-urile și profesiile liberale** (lit. a) nu au alternativă: identificarea se face „numai" cu certificate calificate. Nu există opțiune de utilizator/parolă pentru această categorie.
- **Persoanele fizice fără activitate economică** (lit. b) pot folosi și metode mai simple — certificat calificat, dar și credențiale utilizator/parolă cu coduri de unică folosință, telefon mobil sau alte dispozitive stabilite prin ordin ANAF.
- Practic, un administrator de SRL sau un titular de PFA are nevoie de un certificat calificat emis de un furnizor autorizat (pe token USB, de regulă), instalat pe calculatorul sau dispozitivul folosit pentru autentificare, atât pentru accesul manual în SPV, cât și pentru autorizarea aplicațiilor terțe care se conectează prin API.

## Ce se greșește în practică

- Se folosește un certificat digital simplu (necalificat), obținut pentru semnarea unor documente interne, crezând că este suficient și pentru identificarea la ANAF — legea cere explicit certificat calificat pentru persoanele juridice și PFA.
- Se instalează certificatul pe un singur calculator și apoi se blochează accesul din alte locații, fără să se înțeleagă că token-ul fizic sau fișierul certificatului este cel care contează, nu dispozitivul.
- Se confundă valabilitatea certificatului (de obicei 1-3 ani, stabilită de furnizorul de servicii de certificare) cu durata sesiunii sau a token-urilor tehnice generate ulterior prin OAuth — sunt lucruri diferite.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu emite și nu gestionează certificate digitale** — acestea se obțin de la furnizori autorizați de servicii de certificare, în afara aplicației. Ce face iConta.eu este să folosească, o singură dată, autorizarea obținută cu acest certificat (prin fluxul OAuth2 al ANAF, implementat în `core/spv_conector.py`) pentru a conecta contul SPV al firmei sau PFA-ului la aplicație; ulterior, aplicația reînnoiește automat accesul prin token-uri tehnice, fără să mai fie nevoie de certificatul fizic la fiecare operațiune. Certificatul rămâne, însă, obligatoriu la autorizarea inițială și la reautorizări.

[iConta.eu](/)
