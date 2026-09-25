---
title: "Contribuții pentru perioada de concediu medical: se datorează"
description: "Ce contribuții se rețin din indemnizația de concediu medical — CAS întotdeauna, CASS doar pentru anumite coduri — și cum le calculează iConta.eu la introducerea certificatului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Contribuții pentru perioada de concediu medical: se datorează

Indemnizația de concediu medical nu scapă de contribuții doar pentru că nu e „salariu propriu-zis". Legea o include explicit în baza de calcul a contribuției de asigurări sociale (CAS), dar, pentru contribuția de asigurări sociale de sănătate (CASS), regula e diferită: se reține doar pentru anumite coduri de indemnizație, nu pentru toate.

## Temeiul legal

::: ghid-temei
„Baza lunară de calcul a contribuției de asigurări sociale [...] o reprezintă câștigul brut realizat din salarii și venituri asimilate salariilor [...] care include: [...] o) indemnizațiile de asigurări sociale de sănătate suportate de angajator sau din Fondul național unic de asigurări sociale de sănătate, potrivit legii, primite pe perioada în care persoanele fizice care realizează venituri din salarii sau asimilate salariilor beneficiază de concedii medicale și de indemnizații de asigurări sociale de sănătate, conform prevederilor legale."

„[Categoriile de venituri supuse contribuției de asigurări sociale de sănătate includ] i) indemnizațiile de asigurări sociale de sănătate, acordate în baza art. 2 alin. (1) lit. a) și b) din [OUG 158/2005] [...] aferente concediilor medicale pentru codurile de indemnizație 01, 07 și 10 [...]."
— Codul fiscal, art. 139 alin. (1) lit. o) și art. 155 alin. (1) lit. i) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text rezultă o distincție importantă, ratată des:

- **CAS (25%) se datorează pentru toate indemnizațiile de concediu medical**, indiferent de cod — legea le include explicit în baza de calcul.
- **CASS (10%) se datorează doar pentru codurile 01 (boală obișnuită), 07 (carantină) și 10 (reducere timp de muncă)** — pentru celelalte coduri (maternitate, îngrijire copil, îngrijire pacient oncologic, risc maternal etc.), indemnizația **nu** intră în baza de calcul a CASS.
- Contribuțiile se rețin din indemnizație, indiferent dacă suma e suportată de angajator (primele zile) sau din bugetul FNUASS (restul perioadei) — regimul fiscal nu depinde de cine plătește, ci de codul indemnizației.

## Ce se greșește în practică

- Se reține CASS din orice indemnizație de concediu medical, indiferent de cod, deși legea o exceptează explicit pentru maternitate, îngrijire copil, risc maternal și îngrijire pacient oncologic.
- Se presupune că, dacă suma e suportată de FNUASS (nu de angajator), nu se mai datorează nicio contribuție — regula de mai sus nu face această distincție.
- Se omite complet CAS-ul pe indemnizația de concediu medical, pe motiv că „nu e salariu efectiv lucrat".

## Ce face iConta.eu

Motorul de calcul (`core/salarizare.py`, funcția `taxe_cm`) aplică exact distincția din lege: CAS 25% pe toate indemnizațiile de concediu medical, iar CASS 10% doar pentru codurile 01, 07 și 10 — potrivire exactă cu textul citat mai sus. Calculul rulează automat la introducerea unui certificat de concediu medical în fișa salariatului, iar rezultatul (CAS, CASS, impozit, net) se salvează odată cu certificatul.

[iConta.eu](/)
