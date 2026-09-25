---
title: "Penalizarea pentru nedepunerea raportului de beneficiar real"
description: "Amenzile prevăzute de lege pentru nedepunerea declarației privind beneficiarul real, confirmate din sursă pentru asociații și fundații, cu precizarea limitelor de verificare pentru societăți."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Penalizarea pentru nedepunerea raportului de beneficiar real

Obligația de a declara beneficiarul real (persoana fizică ce exercită efectiv controlul asupra unei entități) există atât pentru societăți, cât și pentru asociații și fundații, dar e reglementată prin acte diferite. Sursele fiscale disponibile permit confirmarea integrală a sancțiunilor doar pentru asociații și fundații, reglementate prin OG nr. 26/2000; pentru societăți (SRL, SA), regimul sancționator e stabilit de Legea nr. 129/2019, act care nu se regăsește, la data acestui ghid, în corpusul de surse (anaf_surse) folosit pentru redactare.

## Temeiul legal

```
::: ghid-temei
„(1) Nerespectarea de către o asociație sau fundație a obligației prevăzute la art. 34^4 constituie contravenție și se sancționează cu amendă de la 200 lei la 2.500 lei.
(6) Necomunicarea de către o asociație sau fundație a datelor de identificare ale beneficiarului real, în vederea înregistrării actualizării evidenței privind beneficiarii reali ai asociațiilor și fundațiilor, dacă aceasta a fost anterior sancționată pentru nerespectarea dispozițiilor prevăzute la art. 34^4, constituie contravenție și se sancționează cu amendă de la 500 lei la 5.000 lei."
— Ordonanța Guvernului nr. 26/2000 privind asociațiile și fundațiile, art. 34^5 alin. (1) și (6) (sursă: anaf_surse/og_26_2000_asociatii_fundatii.txt)
:::
```

Ce se poate confirma, punct cu punct, pentru asociații și fundații:

- **Prima abatere** (nedepunerea declarației privind beneficiarul real, cerută la constituire și la orice modificare a datelor de identificare) se sancționează cu **amendă de la 200 la 2.500 lei**, constatată de Oficiul Național de Prevenire și Combatere a Spălării Banilor.
- Contravenientul are, chiar și după amendă, **30 de zile** de la comunicarea procesului-verbal pentru a comunica totuși datele beneficiarului real.
- **Dacă nu le comunică nici atunci**, riscă o a doua sancțiune, mai mare — **amendă de la 500 la 5.000 lei** — și, mai grav, procesul-verbal menționează expres riscul **dizolvării** asociației sau fundației.
- Orice modificare ulterioară a datelor beneficiarului real trebuie declarată în 30 de zile de la producerea ei (art. 34^4 alin. (4) din același act).

**Pentru societăți comerciale (SRL, SA):** regimul declarativ și sancționator e stabilit de Legea nr. 129/2019, iar Legea nr. 31/1990 confirmă doar existența unui registru al beneficiarilor reali ținut de ONRC, fără să detalieze cuantumul amenzilor. Nu redăm aici o sumă pentru societăți, ca să nu prezentăm ca temei fiscal ceva neconfirmat direct din text; recomandăm verificarea directă a Legii nr. 129/2019 sau a informațiilor publicate de ONRC.

## Ce se greșește în practică

- Se aplică, din auzite, cifrele valabile pentru societăți și celor de la asociații/fundații (sau invers) — cele două regimuri au baze legale și cuantumuri diferite.
- Se crede că amenda „închide" complet obligația — de fapt, chiar și după sancționare, entitatea trebuie să comunice datele în 30 de zile, altfel urmează o a doua amendă, mai mare.
- Se ignoră obligația de actualizare la orice modificare a beneficiarului real, considerându-se — greșit — că declarația inițială, de la constituire, e suficientă pentru toată durata de existență a entității.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu gestionează** declarația sau evidența beneficiarului real pentru asociații, fundații sau societăți comerciale obișnuite (SRL, SA) — nu a fost găsită nicio funcționalitate cu acest scop în `core/`. Există, distinct, `core/d169.py` și `core/d169n.py`, module dedicate declarațiilor privind beneficiarul real **al fiduciei** (contract de fiducie sau construcție juridică similară, în temeiul Legii nr. 129/2019), dar acesta e un caz juridic îngust, separat de asociații/fundații și de societăți — nu acoperă situația din acest ghid. Aplicația oferă evidența contabilă generală a entității; obligația de declarare a beneficiarului real pentru o asociație, fundație sau societate și urmărirea termenelor aferente rămân, la acest moment, în sarcina administratorului sau a consultantului juridic al entității.

[iConta.eu](/)
