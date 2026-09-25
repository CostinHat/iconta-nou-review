---
title: "Am depășit plafonul de numerar: consecințe"
description: "Ce plafoane zilnice de încasări și plăți în numerar se aplică firmelor în 2026 și ce amenzi riscă depășirea lor, conform Legii 70/2015."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Am depășit plafonul de numerar: consecințe

Disciplina financiară privind numerarul nu e o recomandare, ci o obligație legală cu plafoane zilnice fixe: depășirea lor, chiar și prin fracționarea artificială a unei sume, e contravenție sancționabilă.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile art. 1 alin. (1) se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: a) încasări de la persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei de la o persoană; [...] c) plăți către persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei/persoană, dar nu mai mult de un plafon total de 10.000 lei/zi.
(2) Sunt interzise încasările fragmentate în numerar de la beneficiari pentru facturile a căror valoare este mai mare de 5.000 lei [...], precum și fragmentarea facturilor pentru o livrare de bunuri sau o prestare de servicii a căror valoare este mai mare de 5.000 lei.
ART. 12 (2) Nerespectarea prevederilor art. 6 și art. 11 alin. (1)-(4) constituie contravenție și se sancționează cu amendă de la 3.000 lei la 4.500 lei."
— Legea 70/2015, art. 3 alin. (1) lit. a), c), art. 3 alin. (2) și art. 12 alin. (2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Plafoanele zilnice esențiale pentru operațiuni între persoane juridice/PFA/liber profesioniști:

- **5.000 lei/persoană/zi** — încasări sau plăți obișnuite între entitățile din art. 1 alin. (1) (persoane juridice, PFA, întreprinderi individuale/familiale, liber profesioniști).
- **10.000 lei/zi total** — plafonul agregat pentru plăți către aceeași persoană într-o zi, indiferent de câte tranzacții separate.
- **10.000 lei/persoană/zi** — plafonul pentru magazinele de tip cash and carry, respectiv pentru operațiunile cu persoane fizice (împrumuturi, cesiuni de creanțe, contravaloarea unor livrări/prestări).
- Fragmentarea unei sume sau a unei facturi în tranșe mai mici, special pentru a evita plafonul, e ea însăși interzisă și sancționabilă — legea o numește explicit „încasare fragmentată"/„plată fragmentată".

## Ce se greșește în practică

- Se calculează plafonul per tranzacție, nu per zi/persoană — două încasări de 4.000 lei în aceeași zi, de la același client, depășesc deja plafonul de 5.000 lei, chiar dacă fiecare încasare separată pare sub limită.
- Se ignoră plafonul total de 10.000 lei/zi la plăți, concentrându-se doar pe plafonul de 5.000 lei/persoană — cele două limite se aplică simultan.
- Se presupune că plata avansurilor spre decontare nu intră în calculul plafonului zilnic — de fapt, la data acordării avansului, suma intră direct în plafonul zilnic aplicabil.

## Ce face iConta.eu

iConta.eu implementează plafoanele de numerar din Legea 70/2015 (actualizată prin Legea 239/2025, în vigoare din 01.01.2026) direct în modulul de casierie: 5.000 lei pentru încasări de la persoane juridice (10.000 lei pentru cash and carry), 5.000 lei pentru plăți către persoane juridice cu plafon total de 10.000 lei/zi (tot 10.000 lei pentru cash and carry) și 10.000 lei pentru operațiuni cu persoane fizice — exact plafoanele discutate mai sus. Separat, aplicația urmărește și soldul de casă la sfârșitul zilei (50.000 lei, respectiv 500.000 lei pentru cash and carry), ca prag intern de avertizare, nu ca plafon de încasare/plată propriu-zis. Fiecare operațiune de casă generează o notă cu urmă care indică temeiul folosit, iar contabilul validează operațiunea — aplicația nu blochează încă automat, la nivel de interfață, o operațiune care ar depăși plafonul, ci semnalează plafonul aplicabil pentru validarea manuală.

[iConta.eu](/)
