---
title: "Pot deduce TVA plătită prin D301 dacă am doar cod special de TVA?"
description: "De ce înregistrarea cu cod special de TVA (art. 317 CF) nu dă dreptul de a deduce taxa plătită prin decontul special 301, spre deosebire de înregistrarea normală conform art. 316."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Pot deduce TVA plătită prin D301 dacă am doar cod special de TVA?

O firmă neplătitoare de TVA în regim normal, dar înregistrată doar cu „cod special de TVA" (art. 317 CF) pentru că face achiziții intracomunitare, plătește taxa aferentă acelor achiziții prin decontul special 301. Întrebarea vine firesc: dacă a plătit deja taxa, poate să o deducă? Răspunsul scurt e nu, și motivul ține direct de cine are, prin lege, dreptul de deducere.

## Temeiul legal

::: ghid-temei
„Orice persoană impozabilă înregistrată în scopuri de TVA, conform art. 316, are dreptul să scadă din valoarea totală a taxei colectate, pentru o perioadă fiscală, valoarea totală a taxei pentru care, în aceeași perioadă, a luat naștere și poate fi exercitat dreptul de deducere, conform art. 297-300."
— Codul fiscal, art. 301 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Dreptul de deducere prin decont este condiționat explicit de înregistrarea „conform art. 316" — adică înregistrarea normală în scopuri de TVA, cu decontul de taxă (formularul 300), nu de simpla deținere a unui cod de TVA de orice fel.
- Înregistrarea conform art. 317 (codul special) vizează exact persoanele aflate în situația opusă. Codul fiscal o definește ca aplicându-se celor „neînregistrate și care nu au obligația să se înregistreze conform art. 316" — deci art. 317 și art. 316 sunt, prin construcție legală, două statuturi diferite, nu trepte ale aceleiași înregistrări.
- Instrucțiunile oficiale de completare a formularului 301 (OPANAF 592/2016) confirmă exact cine îl depune: „persoanele impozabile... care nu sunt înregistrate și nu trebuie să se înregistreze conform art. 316 din Codul fiscal, dar care sunt înregistrate conform art. 317 din același cod" — profilul tipic fiind cel al unei firme neplătitoare de TVA (inclusiv una aflată la regimul de scutire pentru întreprinderile mici, art. 310) care doar achiziționează intracomunitar.
- Formularul 301 e, prin natura lui, o declarație de plată a taxei datorate pentru operațiunea respectivă („titlu de creanță"), nu un decont cu secțiune de taxă deductibilă precum formularul 300 — nu are unde să înscrii o deducere, pentru că deducerea nu e un drept pe care îl ai în acest statut.

## Ce se greșește în practică

- Se confundă „am un cod de TVA" cu „sunt plătitor de TVA în regim normal" — codul special (art. 317) nu conferă niciuna dintre obligațiile sau drepturile regimului normal, în afara celei specifice (raportarea și plata TVA pe achizițiile intracomunitare sau operațiunile cu taxare inversă pentru care e obligatorie înregistrarea).
- Se așteaptă, din obișnuință, ca taxa plătită prin D301 să „iasă" undeva la o deducere ulterioară, ca la decontul 300 — nu există acest mecanism cât timp firma rămâne doar cu cod special.
- Se ignoră că trecerea la dreptul de deducere presupune înregistrarea normală conform art. 316, care aduce însă și obligația de a colecta TVA pentru toate operațiunile taxabile ale firmei, nu doar avantajul deducerii pe achizițiile intracomunitare.

## Ce face iConta.eu

Această întrebare privește o funcționalitate reală, dar separată, a aplicației: modulul `core/d301.py`, care generează efectiv declarația 301 (Decont special de TVA, conform OPANAF 592/2016) pentru achizițiile intracomunitare și operațiunile cu taxare inversă ale unei firme. Modulul urmărește explicit statutul de înregistrare art. 317 al firmei (câmpul `pers_inreg`, cu valorile „1 = neînregistrat" sau „2 = înregistrat doar conform art. 317") pentru completarea corectă a formularului — dar, consistent cu legea de mai sus, nu conține nicio logică de deducere a taxei raportate prin D301: modulul calculează și declară taxa datorată, nu o taxă deductibilă. Acest modul este distinct de funcționalitatea „Regim special agricultori" (compensația forfetară de 8%), cu care nu are legătură funcțională.

[iConta.eu](/)
