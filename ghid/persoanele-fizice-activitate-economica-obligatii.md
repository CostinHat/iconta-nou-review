---
title: "Persoanele fizice cu activitate economică: obligații"
description: "Când o persoană fizică autorizată sau cu venituri din activități independente datorează contribuția de asigurări sociale (CAS) și de sănătate (CASS), în funcție de pragurile din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Persoanele fizice cu activitate economică: obligații

Pentru o persoană fizică autorizată, întrebarea centrală în fiecare an nu este „cât impozit plătesc", ci „am depășit pragul de venit care mă obligă la CAS și CASS". Legea leagă totul de multipli ai salariului minim brut pe țară, nu de o sumă fixă.

## Temeiul legal

::: ghid-temei
„[Persoana fizică care realizează venituri], din una sau mai multe surse și/sau categorii de venituri, a căror valoare anuală cumulată este cel puțin egală cu 12 salarii minime brute pe țară, datorează contribuția de asigurări sociale la o bază de calcul stabilită potrivit alin. (2). [...] Încadrarea în plafonul anual de cel puțin 12 salarii minime brute pe țară [...] se efectuează prin cumularea veniturilor nete și/sau a normelor anuale de venit din activități independente determinate potrivit art. 68."
— Legea nr. 227/2015 (Codul fiscal), art. 148 alin. (1) și (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul de bază, pentru o PFA sau altă persoană cu activitate independentă:

- **CAS** (pensii) devine datorată doar dacă venitul net anual cumulat, din una sau mai multe surse, atinge sau depășește **12 salarii minime brute pe țară**. Sub acest prag, contribuția e opțională.
- **CASS** (sănătate) are un prag mai jos — venitul anual cumulat trebuie să atingă **6 salarii minime brute pe țară** pentru a deveni obligatorie plata contribuției.
- Verificarea încadrării se face prin **cumularea veniturilor din toate sursele** de activitate independentă din acel an, inclusiv normele anuale de venit, nu doar din activitatea principală declarată.

## Ce se greșește în practică

- Se verifică pragul de CAS/CASS doar pentru activitatea principală declarată, ignorând cumulul cu alte venituri independente realizate în același an fiscal (drepturi de autor, activități economice suplimentare).
- Se confundă pragul de CAS (12 salarii minime) cu cel de CASS (6 salarii minime) — sunt praguri diferite, verificate separat, iar depășirea unuia nu înseamnă automat depășirea celuilalt.
- Se omite depunerea Declarației unice la termen atunci când venitul estimat depășește pragul abia în cursul anului, deși legea prevede obligații de regularizare și declarare pentru astfel de situații.

## Ce face iConta.eu

La data acestui ghid, iConta.eu oferă un registru-jurnal de încasări și plăți pentru persoane fizice autorizate care conduc contabilitate în partidă simplă, în regim de venit net real (`core/rip_api.py`, conform OMFP 170/2015), din care se pot calcula veniturile realizate. Aplicația **nu verifică automat** încadrarea în pragurile de 12, respectiv 6 salarii minime brute pentru CAS și CASS și nu depune Declarația unică — cumularea veniturilor din toate sursele și evaluarea obligației de contribuție rămân responsabilitatea contabilului sau a persoanei fizice autorizate.

[iConta.eu](/)
