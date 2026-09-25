---
title: Cum obțin un certificat calificat pentru e-Factura
description: RO e-Factura nu necesită un certificat digital al firmei pentru semnarea facturilor — Ministerul Finanțelor aplică propria semnătură electronică la validare; certificatul calificat este necesar pentru identificarea electronică și accesul la Spațiul Privat Virtual (SPV), obținut de la un furnizor de servicii de certificare acreditat conform legislației privind semnătura electronică.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum obțin un certificat calificat pentru e-Factura

O confuzie frecventă: firmele cred că au nevoie de un certificat digital calificat pentru a „semna" facturile electronice transmise prin RO e-Factura. Nu este corect — semnătura care validează factura electronică aparține Ministerului Finanțelor, nu emitentului. Certificatul calificat este necesar, de fapt, pentru accesul și identificarea electronică în Spațiul Privat Virtual (SPV), platforma prin care se interacționează cu ANAF, inclusiv pentru RO e-Factura.

### De ce nu aveți nevoie de certificat propriu pentru semnarea facturii

Potrivit art. 4 alin. (4) din OUG nr. 120/2021 privind sistemul național RO e-Factura, „în situația în care factura electronică transmisă respectă structura prevăzută [...], se aplică semnătura electronică a Ministerului Finanțelor și se comunică de îndată destinatarului." Exemplarul original al facturii electronice este fișierul XML însoțit de semnătura electronică a Ministerului Finanțelor (art. 4 alin. (6)) — deci nu factura dumneavoastră semnată digital, ci factura validată și semnată de sistemul ANAF.

### Pentru ce aveți nevoie de certificat calificat

Certificatul calificat este mijlocul de **identificare electronică** în relația cu Ministerul Finanțelor/ANAF, necesar pentru accesul la Spațiul Privat Virtual (SPV) — prin care se depun declarații, se accesează Registrul RO e-Factura și se comunică electronic cu autoritatea fiscală. Procedura este reglementată de OMFP nr. 660/2017.

Potrivit art. 6 din OMFP nr. 660/2017:

- persoanele juridice sau alte entități fără personalitate juridică **se identifică electronic obligatoriu cu certificate calificate** (alin. (1));
- persoanele fizice care au calitatea de reprezentant/împuternicit al unei persoane juridice se identifică electronic tot cu certificat calificat (alin. (2));
- alte persoane fizice pot alege între certificat calificat și NPOTP (nume + parolă + cod de autentificare unică) (alin. (4)).

### Ce este certificatul calificat

Definit la art. 5 lit. b) din OMFP nr. 660/2017: certificat eliberat de furnizori de servicii de certificare **acreditați** în condițiile legislației privind semnătura electronică și ale Regulamentului (UE) nr. 910/2014 (eIDAS). Se obține de la un furnizor de servicii de certificare acreditat, nu de la ANAF — ANAF doar înregistrează și verifică certificatul deja emis.

### Pașii de înregistrare a certificatului la ANAF (procedura SPV)

Potrivit art. 9 din OMFP nr. 660/2017:

1. Achiziționați certificatul calificat de la un furnizor de servicii de certificare acreditat.
2. Depuneți cererea de utilizare a certificatului calificat prin aplicațiile informatice dedicate, pe platforma ANAF.
3. Completați numele, prenumele, codul de identificare fiscală, elementele de identificare a certificatului și ale documentului de identitate, plus o adresă de e-mail.
4. ANAF verifică veridicitatea datelor cu emitentul certificatului și cu emitenții documentelor de identitate (art. 9 alin. (4)).
5. Primiți confirmarea înregistrării certificatului la adresa de e-mail indicată (sau respingerea cererii, motivată).

Modificarea datelor sau reînnoirea certificatului se face tot prin aplicațiile informatice de pe platforma dedicată (art. 10), iar renunțarea la identificarea prin certificat calificat urmează o procedură similară (art. 11).

### Tabel-sinteză

| Aspect | Cine îl face | Temei |
|---|---|---|
| Semnarea/validarea facturii electronice | Ministerul Finanțelor, automat | Art. 4 alin. (4), (6) OUG 120/2021 |
| Emiterea certificatului calificat | Furnizor de servicii de certificare acreditat | Legislația privind semnătura electronică, Regulamentul (UE) 910/2014 |
| Înregistrarea certificatului la ANAF (SPV) | Firma/reprezentantul legal | OMFP nr. 660/2017, art. 9 |
| Obligativitate certificat pentru persoane juridice | Da, întotdeauna | Art. 6 alin. (1) OMFP 660/2017 |

### De reținut

- Certificatul calificat vă dă acces la SPV, nu „semnează" facturile RO e-Factura — acelea sunt validate automat de sistemul Ministerului Finanțelor.
- Verificați ca furnizorul de la care cumpărați certificatul să fie acreditat conform legislației privind semnătura electronică — altfel identificarea la ANAF nu va fi acceptată.
