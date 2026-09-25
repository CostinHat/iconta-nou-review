---
title: "Diferența dintre asociație și fundație la înființare"
description: "Ce separă legal o asociație de o fundație — numărul de fondatori, natura contribuției și capitalul minim cerut la înființare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Diferența dintre asociație și fundație la înființare

Asociațiile și fundațiile sunt ambele persoane juridice de drept privat fără scop patrimonial, dar structura lor de fondare e diferită din start — și diferența nu e formală, ci ține de natura juridică a contribuției fondatorilor.

## Temeiul legal

::: ghid-temei
„Asociația este subiectul de drept privat constituit de trei sau mai multe persoane care, pe baza unei înțelegeri, pun în comun și fără drept de restituire contribuția materială, cunoștințele sau aportul lor în muncă pentru realizarea unor activități în interes general, al unor colectivități sau, după caz, în interesul lor personal nepatrimonial."
— Ordonanța Guvernului nr. 26/2000 cu privire la asociații și fundații, art. 4 alin. (1) (sursă: anaf_surse/og_26_2000_asociatii_fundatii.txt)

„Fundația este subiectul de drept înființat de una sau mai multe persoane care, pe baza unui act juridic între vii ori pentru cauză de moarte, constituie un patrimoniu afectat, în mod permanent și irevocabil, realizării unui scop de interes general sau, după caz, al unor colectivități. Activul patrimonial inițial al fundației trebuie să includă bunuri în natură sau în numerar, a căror valoare totală să fie de cel puțin de 10 ori salariul de bază minim brut pe țară garantat în plată, la data constituirii fundației."
— Ordonanța Guvernului nr. 26/2000, art. 15 alin. (1)-(2) (sursă: anaf_surse/og_26_2000_asociatii_fundatii.txt)
:::

Diferențele principale rezultate direct din text:

- **Numărul minim de fondatori**: asociația cere **cel puțin trei persoane**; fundația poate fi înființată de **o singură persoană**.
- **Natura contribuției**: la asociație, membrii pun în comun contribuție materială, cunoștințe sau muncă, **fără drept de restituire** — accentul e pe activitatea desfășurată împreună. La fundație, fondatorul/fondatorii constituie un **patrimoniu afectat permanent și irevocabil** unui scop — accentul e pe patrimoniul alocat, nu pe participarea activă a mai multor membri.
- **Capital minim la înființare**: fundația are un prag legal explicit — activul patrimonial inițial trebuie să fie de **cel puțin 10 ori salariul de bază minim brut pe țară**, în bani sau în natură. Asociația nu are un asemenea prag minim de capital stabilit prin lege.
- **Personalitate juridică**: ambele dobândesc personalitate juridică prin înscrierea în Registrul asociațiilor și fundațiilor, aflat la grefa judecătoriei de la sediu.
- Ambele pot desfășura activități economice directe, dacă acestea au caracter accesoriu și legătură strânsă cu scopul principal, și pot înființa societăți comerciale ale căror dividende, dacă nu se reinvestesc, trebuie folosite obligatoriu pentru scopul asociației/fundației.

## Ce se greșește în practică

- Se alege forma de „asociație" cu un singur fondator, ignorând pragul minim de trei persoane cerut explicit de lege — o asociație cu mai puțin de trei fondatori nu poate fi înscrisă.
- Se subestimează capitalul minim cerut la fundație (10 salarii minime brute) și se încearcă înființarea cu un patrimoniu inițial mai mic.
- Se presupune că fundația poate fi „retrasă" de fondator ca un aport revocabil — patrimoniul afectat unei fundații e permanent și irevocabil, nu poate fi recuperat ulterior de fondator.
- Se confundă activitatea economică accesorie permisă (art. 47-48 OG 26/2000) cu scopul principal al entității — dacă activitatea economică devine principală, entitatea riscă să nu mai corespundă naturii ei fără scop patrimonial.

## Ce face iConta.eu

iConta.eu are un modul dedicat contabilității organizațiilor non-profit (`core/ong.py`, construit pe OMFP 3103/2017 și art. 15 alin. (2)-(3) din Codul fiscal), care separă evidența veniturilor fără scop patrimonial (cotizații, donații, sponsorizări) de cea a eventualelor activități economice, și calculează scutirea de impozit pe profit pentru veniturile economice sub pragul legal. Aplicația nu are însă un „asistent de înființare" care să ajute la alegerea între asociație și fundație — decizia rămâne una juridică, luată înainte de înregistrarea entității, iar iConta.eu intervine ulterior, în gestiunea contabilă curentă a organizației deja înființate.

[iConta.eu](/)
