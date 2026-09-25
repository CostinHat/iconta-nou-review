---
title: "Cum obțin CUI de la asociați pentru D205"
description: "Codul de identificare fiscală al beneficiarului de dividende este un câmp obligatoriu în structura D205, iar sursa lui rămâne datele deja deținute de firmă despre asociați."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum obțin CUI de la asociați pentru D205

Nu ANAF „trimite" codul de identificare al fiecărui asociat pentru completarea D205 — firma trebuie să îl aibă deja, din actele constitutive sau din registrul propriu de asociați, pentru că structura declarației îl cere ca element obligatoriu pe fiecare beneficiar.

## Temeiul legal

::: ghid-temei
„<benef> 1-n aparitii [...] 4. cifR 4.CNP/NIF din Romania N(13) DA Verificare cifR — cifR= CNP/NIF — ERR - campul '4.CNP/NIF din Romania' invalid / necompletat"
— OPANAF nr. 102/2025, structura declarației 205, câmpul `cifR` (codul de identificare fiscală — CNP/NIF din România — al beneficiarului) (sursă: anaf_surse/d205_struct_anaf.txt)
:::

Ce spune structura, practic:

- Fiecare beneficiar (`benef`) din secțiunea de dividende trebuie să poarte un cod de identificare fiscală (`cifR`, CNP/NIF din România) — pentru o persoană fizică, acesta este de regulă CNP-ul, iar din acest cod se derivă automat și rezidența (`Rezid`), în funcție de forma codului (CNP românesc valid de rezident versus alt tip de cod).
- Fără acest cod, declarația nu poate fi validă — validatorul oficial ANAF respinge o înregistrare de beneficiar fără identificator fiscal complet.
- Structura nu prevede un mecanism prin care ANAF „furnizează" acest cod firmei plătitoare de dividende — obligația de a-l deține corect revine plătitorului, ca parte a evidenței sale despre asociați.

## Ce se greșește în practică

- Se așteaptă ca declarația să poată fi generată fără codul de identificare al asociatului, urmând să fie completat „mai târziu" — declarația nu e validă fără acest câmp, iar termenul de depunere nu se amână pentru lipsa lui.
- Se folosește un CNP incorect sau incomplet (de exemplu, preluat verbal, netranscris corect), ceea ce produce erori de validare greu de diagnosticat ulterior.
- Se confundă codul de identificare al asociatului persoană fizică (CNP) cu CUI-ul unei eventuale firme deținute de acesta — pentru declararea dividendelor către o persoană fizică, structura cere CNP-ul persoanei, nu un CUI de firmă.

## Ce face iConta.eu

iConta.eu **nu obține automat** codul de identificare al asociaților de la ANAF sau de la alte registre publice — declarația D205 (`core/d205.py`) citește aceste date direct din modulul propriu de asociați al firmei (`select_asociati`), unde CNP-ul fiecărui asociat trebuie introdus și menținut de utilizator. Aplicația validează structural codul introdus (lungime, format numeric) pentru a deriva corect rezidența, dar corectitudinea și completitudinea datelor despre asociați rămân responsabilitatea contabilului sau a administratorului firmei.

[iConta.eu](/)
