---
title: "Cum verific D101 cu declarațiile depuse în cursul anului?"
description: "Firmele care au optat pentru sistemul anual cu plăți anticipate trimestriale trebuie să verifice D101 față de plățile anticipate declarate în cursul anului prin D100 — un pas ușor de omis la definitivare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific D101 cu declarațiile depuse în cursul anului?

Firmele care au ales sistemul anual de declarare a impozitului pe profit, cu plăți anticipate trimestriale, ajung la sfârșitul anului cu o declarație anuală (D101) care trebuie să se lege corect de sumele deja declarate trimestrial — nu recalculate de la zero, izolat.

## Temeiul legal

::: ghid-temei
„Contribuabilii, alții decât cei prevăzuți la alin. (4) și (5), pot opta pentru calculul, declararea și plata impozitului pe profit anual, cu plăți anticipate, efectuate trimestrial. Termenul până la care se efectuează plata impozitului anual este termenul de depunere a declarației privind impozitul pe profit, prevăzut la art. 42."
— Codul fiscal (Legea 227/2015), art. 41 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce presupune, în practică, verificarea:

- Firma care a optat pentru sistemul anual plătește trimestrial doar **plăți anticipate** (nu impozit definitiv calculat pe trimestru) — abia la definitivarea anuală, prin D101, se stabilește impozitul real datorat pe tot anul.
- Diferența dintre impozitul anual definitivat (din D101) și totalul plăților anticipate deja declarate în cursul anului determină suma rămasă de plată sau, dacă plățile anticipate au fost mai mari, suma de recuperat.
- Opțiunea pentru sistemul anual e obligatorie pentru cel puțin 2 ani fiscali consecutivi (art. 41 alin. (3)) — deci verificarea nu e una izolată, ci trebuie să țină cont de continuitatea regimului ales de la an la an.

## Ce se greșește în practică

- Se calculează D101 exclusiv din balanța anului curent, fără a confrunta rezultatul cu totalul plăților anticipate deja declarate trimestrial, riscând fie o dublă plată, fie omiterea unei diferențe de achitat.
- Se schimbă sistemul de declarare (din anual în trimestrial sau invers) fără să se respecte perioada minimă obligatorie de 2 ani fiscali consecutivi prevăzută de lege.
- Se confundă termenul de plată a impozitului anual definitivat (termenul de depunere a D101) cu termenele trimestriale ale plăților anticipate, generând întârzieri la plată.

## Ce face iConta.eu

D101 este funcționalitate live în iConta.eu: aplicația calculează impozitul pe profit anual din balanță, aplică pierderea reportată, calculează IMCA (impozitul minim pe cifra de afaceri) și compară cele două sume, generând XML-ul validat pentru depunere. La data acestui ghid, nu am găsit în cod o verificare automată dedicată care să confrunte suma rezultată în D101 cu totalul plăților anticipate deja declarate trimestrial în cursul anului pentru firmele aflate în sistemul anual — această corelare rămâne o verificare manuală a contabilului înainte de definitivare.

[iConta.eu](/)
