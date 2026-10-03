---
title: "Ce date ale unui PFA sau ale unei persoane fizice raportează platforma online la ANAF?"
description: "Pentru o persoană fizică, platforma raportează numele, adresa principală, NIF-ul, codul de TVA, data nașterii, contul bancar, statele de rezidență și, pe trimestre, sumele încasate și comisioanele."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Ce date ale unui PFA sau ale unei persoane fizice raportează platforma online la ANAF?

Pentru un vânzător persoană fizică, platforma colectează și raportează cinci date de identificare: prenumele și numele, adresa principală, NIF-ul (sau locul nașterii, dacă nu există NIF), numărul de TVA, dacă există, și data nașterii. La ele se adaugă datele financiare: contul în care primește banii, statele de rezidență, contraprestația totală și numărul de activități pe fiecare trimestru, plus comisioanele reținute.

Pentru contabil, setul arată exact ce vede ANAF: identificarea leagă raportarea de client, iar sumele trimestriale se pot compara cu ce declară acesta.

## Temeiul legal

::: ghid-temei
„1. Operatorul de platformă care are obligația de raportare colectează toate informațiile următoare pentru fiecare Vânzător care este o persoană fizică și care nu este Vânzător Exclus: a)prenumele și numele; b)Adresa Principală; c)orice NIF emis Vânzătorului respectiv, inclusiv fiecare stat membru emitent, și, în absența unui NIF, locul nașterii Vânzătorului respectiv; d)numărul TVA al Vânzătorului respectiv, dacă există; e)data nașterii."
— Codul de procedură fiscală (Legea 207/2015), Anexa nr. 5, secț. II lit. B pct. 1 (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„e)Contraprestația totală plătită sau creditată în fiecare trimestru al Perioadei de Raportare și numărul de Activități Relevante pentru care aceasta a fost plătită sau creditată; f)orice onorarii, comisioane sau taxe reținute sau percepute de Operatorul de platformă care are obligația de raportare în fiecare trimestru al Perioadei de Raportare."
— Codul de procedură fiscală (Legea 207/2015), Anexa nr. 5, secț. III lit. B pct. 2 lit. e) și f) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„b) pentru persoanele fizice și juridice, precum și pentru alte entități care se înregistrează potrivit legii speciale la registrul comerțului, codul unic de înregistrare atribuit potrivit legii speciale; [...] d) pentru persoanele fizice, altele decât cele prevăzute la lit. c), codul numeric personal atribuit potrivit legii speciale;"
— Codul de procedură fiscală (Legea 207/2015), art. 82 alin. (1) lit. b) și d) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Setul complet, pe categorii:

- **Identificare (secț. II lit. B pct. 1).** Prenume și nume, adresa principală, NIF cu statul emitent, cod de TVA dacă există, data nașterii. În România, codul de identificare fiscală al unei persoane fizice fără activitate economică este CNP-ul, iar al unui PFA înregistrat la registrul comerțului este codul unic de înregistrare (art. 82 alin. (1) lit. b) și d)). Pentru că legea cere „orice NIF”, pot apărea amândouă. Adresa principală e cea a reședinței principale (secț. I lit. C pct. 5).
- **Contul financiar.** Platforma raportează numărul contului în care plătește contraprestația, dacă îl are și dacă statul de rezidență nu a anunțat public că nu îl folosește (secț. III lit. B pct. 2 lit. b)). Dacă titularul contului e altă persoană decât vânzătorul, se raportează și numele titularului (lit. c)).
- **Statele de rezidență** stabilite prin regulile de diligență (lit. d)).
- **Sumele.** Contraprestația totală și numărul de activități, defalcate pe trimestre, plus comisioanele reținute în fiecare trimestru (lit. e) și f)).
- **La închirieri de imobile** se adaugă adresa fiecărui bun listat, numărul de carte funciară dacă e disponibil, sumele pe fiecare bun și, dacă e disponibil, numărul de zile de închiriere (secț. III lit. B pct. 3).

Există și câteva excepții:

- **Fără NIF.** Platforma nu e obligată să colecteze NIF-ul dacă statul de rezidență nu îl emite sau nu impune colectarea lui (secț. II lit. B pct. 4).
- **Serviciu de identificare.** Dacă identitatea e confirmată printr-un serviciu de identificare al unui stat membru sau al UE, se raportează numele, identificatorul serviciului și statul emitent (secț. III lit. B pct. 4).

Calitatea de PFA nu schimbă, în lectura noastră, setul de date: PFA-ul nu are personalitate juridică, deci nu pare a fi „Entitate” (persoană juridică sau construcție juridică, secț. I lit. C pct. 1). Codul de TVA apare numai dacă PFA-ul e înregistrat în scopuri de TVA.

::: ghid-exemplu
Ion Popescu PFA vinde ceramică lucrată manual pe un marketplace. În 2026 a avut 64 de vânzări. Raportul platformei pentru 2026 conține:
- Ion Popescu, adresa din Cluj-Napoca, NIF-urile declarate pe platformă (codul PFA-ului și CNP-ul), emise de România, fără cod de TVA, data nașterii;
- IBAN-ul contului PFA în care a încasat;
- România ca stat de rezidență;
- pe trimestre, de exemplu în trimestrul II: 21 de vânzări, contraprestație de 4.250 lei, comisioane reținute de 750 lei.
Contabilul compară 4.250 + 750 = 5.000 lei cu vânzările din trimestrul II din registrul de încasări și plăți.
:::

## Ce se greșește în practică

- Clientul dă platformei o adresă veche sau incompletă, iar raportarea nu se mai potrivește cu domiciliul fiscal.
- PFA-ul își trece pe platformă contul personal, nu pe al PFA-ului. Încasările apar raportate pe un cont pe care contabilul nu îl vede în evidență.
- Se uită că platforma raportează separat comisioanele. Suma netă primită nu e tot ce a plătit cumpărătorul.

## Ce face iConta.eu

iConta.eu nu primește raportările platformelor. Pentru PFA, aplicația ține registrul de încasări și plăți pe lună, cu categorie și deductibilitate pe fiecare operațiune, și poate prelua ciorne din extrasul bancar. Comisionul reținut direct de platformă, care nu apare ca linie separată în extras, se introduce manual de contabil pe baza documentului platformei. Comparația pe trimestre cu datele raportate rămâne în sarcina contabilului.

[iConta.eu](/)
