---
title: "Ce amendă riscă firma pentru depășirea plafonului de numerar"
description: "Sancțiunile contravenționale prevăzute de lege pentru nerespectarea plafoanelor de încasări și plăți în numerar."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce amendă riscă firma pentru depășirea plafonului de numerar

Legea disciplinei financiare privind operațiunile în numerar nu se mulțumește să fixeze plafoane — prevede și sancțiuni concrete pentru nerespectarea lor, calculate diferit după tipul de încălcare.

## Temeiul legal

::: ghid-temei
„(1) [...] constituie contravenții, dacă nu au fost săvârșite în astfel de condiții încât, potrivit legii penale, să constituie infracțiuni, și se sancționează, prin derogare de la prevederile art. 8 din Ordonanța Guvernului nr. 2/2001 privind regimul juridic al contravențiilor [...], cu amendă de 10% din suma încasată/plătită care depășește plafonul stabilit de prezentul capitol pentru fiecare tip de operațiune, dar nu mai puțin de 100 lei.
(2) Nerespectarea prevederilor art. 6 și art. 11 alin. (1)-(4) constituie contravenție și se sancționează cu amendă de la 3.000 lei la 4.500 lei."
— Legea nr. 70/2015, art. 12 alin. (1)-(2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Sunt, de fapt, **două regimuri sancționatorii distincte**, în funcție de tipul încălcării:

- **Depășirea unui plafon** (de exemplu plata de 15.000 lei către un furnizor, când plafonul e 5.000/10.000 lei, sau depășirea plafonului avansurilor spre decontare) se sancționează cu **amendă proporțională**: 10% din suma care depășește plafonul, dar minimum 100 lei — deci amenda crește odată cu mărimea depășirii.
- **Alte încălcări structurale** (de exemplu nerespectarea obligațiilor de la art. 6 — legate de evidența operațiunilor — sau a celor de la art. 11 alin. (1)-(4)) se sancționează cu **amendă fixă între 3.000 și 4.500 lei**, indiferent de sumele implicate.
- Ambele categorii de contravenții se constată și se sancționează conform Ordonanței Guvernului nr. 2/2001, cu derogările specifice prevăzute de Legea nr. 70/2015 (de exemplu, prin excluderea posibilității de plată a jumătate din amendă în anumite termene, prevăzută de regimul general al contravențiilor).

## Ce se greșește în practică

- Se estimează amenda ca fiind fixă, indiferent de sumă — pentru depășirile de plafon, amenda e proporțională (10% din depășire), nu o sumă fixă predeterminată.
- Se confundă cele două tipuri de contravenții — o depășire de plafon de încasare/plată nu se sancționează la fel ca nerespectarea obligațiilor de evidență de la art. 6, chiar dacă ambele apar în același control.
- Se presupune că amenda minimă de 100 lei se aplică oricărei depășiri mici, fără să se verifice dacă suma calculată la 10% din depășire ar fi, de fapt, mai mare.

## Ce face iConta.eu

Verificat în cod: modulul `core/casa.py` semnalează depășirile plafoanelor legate de operațiunile în numerar (sold casă, încasări de la persoane juridice, avansuri spre decontare) ca **avertismente cu temei citat**, prin funcția `verifica_plafon` — util pentru a preveni o depășire înainte să devină o problemă de control. Aplicația **nu calculează automat cuantumul amenzii potențiale** (10% din depășire, minimum 100 lei, sau amenda fixă de 3.000-4.500 lei, după caz) — avertismentele arată doar că un prag legal a fost depășit, nu și expunerea financiară concretă la sancțiune, care rămâne o evaluare separată.

[iConta.eu](/)
