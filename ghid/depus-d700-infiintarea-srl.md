---
title: "Trebuie depus D700 după înființarea unui SRL?"
description: "Când identificarea fiscală a unui SRL nou se obține automat la înmatriculare și când e nevoie, separat, de declarația 700 pentru vectorul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Trebuie depus D700 după înființarea unui SRL?

Confuzia vine din faptul că un SRL nou primește codul unic de înregistrare (CUI) chiar la înmatricularea la registrul comerțului, fără o cerere separată la ANAF — dar asta nu înseamnă automat că vectorul fiscal complet e stabilit din capul locului. D700 intervine separat, pentru înregistrarea sau modificarea categoriilor de obligații fiscale declarative.

## Temeiul legal

::: ghid-temei
„(1) Orice persoană sau entitate care este subiect într-un raport juridic fiscal se înregistrează fiscal primind un cod de identificare fiscală. Codul de identificare fiscală este: [...] b) pentru persoanele fizice și juridice, precum și pentru alte entități care se înregistrează potrivit legii speciale la registrul comerțului, codul unic de înregistrare atribuit potrivit legii speciale; [...]
(6) Declarația de înregistrare fiscală se depune în termen de 30 de zile de la: a) data înființării potrivit legii, în cazul persoanelor juridice, asocierilor și al altor entități fără personalitate juridică; [...]"
— Legea 207/2015 (Codul de procedură fiscală), art. 82 alin. (1) lit. b) și alin. (6) lit. a) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„ORDIN nr.2372/2017 pentru aprobarea modelului, conținutului, precum și a instrucțiunilor de completare a formularului (700) «Declarație pentru înregistrarea/modificarea categoriilor de obligații fiscale declarative înscrise în vectorul fiscal», cod 14.13.01.10.01"
— referință la art. 86, Legea 207/2015 (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă din aceste texte pentru un SRL nou-înființat:

- **Codul unic de înregistrare (CUI) se obține automat prin registrul comerțului**, la înmatriculare, potrivit legii speciale — firma nu depune o cerere separată la ANAF doar pentru a primi identitatea fiscală de bază.
- **Obligația de declarare fiscală în 30 de zile de la înființare rămâne**, separat de atribuirea CUI — ea privește stabilirea/completarea vectorului fiscal (ce declarații datorează firma: TVA, impozit pe profit sau micro, angajator etc.), nu identitatea fiscală în sine.
- **D700 e instrumentul concret pentru vectorul fiscal**: formularul „Declarație pentru înregistrarea/modificarea categoriilor de obligații fiscale declarative înscrise în vectorul fiscal" servește exact la înregistrarea inițială sau la orice modificare ulterioară a categoriilor de obligații declarative — de la opțiunea pentru TVA la trecerea de la micro la impozit pe profit.
- **Practic**, dacă la constituire firma nu a optat pentru toate elementele posibile ale vectorului fiscal prin procedura simplificată de la registrul comerțului, sau dacă apar schimbări ulterioare (ex. înregistrare TVA, angajarea primului salariat, schimbarea regimului de impozitare), D700 devine calea prin care se actualizează vectorul fiscal.

## Ce se greșește în practică

- Se presupune că, odată primit CUI-ul la înființare, firma nu mai are nicio obligație declarativă separată către ANAF — vectorul fiscal (ce declarații datorează efectiv) e o informație distinctă de simpla identificare fiscală.
- Se depune D700 pentru orice modificare administrativă a firmei (sediu, obiect de activitate), deși formularul privește strict categoriile de obligații fiscale declarative din vectorul fiscal, nu datele generale de identificare.
- Se omite actualizarea vectorului fiscal atunci când firma trece de la un regim la altul (ex. depășește plafonul de microîntreprindere, se înregistrează în scopuri de TVA), considerând că schimbarea se produce automat, fără nicio declarație.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu generează și nu depune declarația D700**. Din nota internă de dezvoltare a proiectului (`anaf_surse/d010_d020_d070_d700_status.md`) rezultă că structura declarației a fost recuperată din validatorul oficial DUK, dar acesta nu validează D700 ca XML de sine stătător (răspunde cu cod de eroare -5 pe toate versiunile testate) — D700 fiind, în fapt, o declarație de tip SmartPDF, nu XML standalone ca alte formulare (ex. D230). În absența unei căi de validare confirmate și a mapării complete operație → câmpuri din instrucțiunile oficiale ANAF, generarea D700 rămâne neconstruită în aplicație; înregistrarea sau modificarea vectorului fiscal se face, la acest moment, direct prin SPV sau la ghișeu.

[iConta.eu](/)
