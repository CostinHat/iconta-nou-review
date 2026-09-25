---
title: "Amortizarea costurilor de dezvoltare capitalizate"
description: "Durata legală de amortizare a cheltuielilor de dezvoltare recunoscute ca imobilizare necorporală și limita ei maximă atunci când depășește 5 ani."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Amortizarea costurilor de dezvoltare capitalizate

Când o firmă capitalizează costurile unui proiect de dezvoltare (de exemplu, dezvoltarea internă a unui produs software sau a unei tehnologii proprii, care îndeplinește criteriile contabile de recunoaștere ca activ), aceste costuri nu rămân cheltuială a perioadei, ci devin imobilizare necorporală — contul 203 „Cheltuieli de dezvoltare" — și se amortizează pe durata de utilizare sau pe perioada contractului aferent proiectului.

## Temeiul legal

::: ghid-temei
„182. - (1) Cheltuielile de dezvoltare se amortizează pe durata de utilizare sau pe perioada contractului, după caz. (2) În cazul în care durata contractului sau durata de utilizare depășește 5 ani, durata de amortizare a cheltuielilor de dezvoltare nu poate depăși 10 ani."
— OMFP nr. 1.802/2014, pct. 182 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Regula de bază este amortizarea pe durata de utilizare estimată sau pe durata contractului legat de proiectul de dezvoltare — nu există un plafon fix universal, ci un plafon condiționat.
- Dacă durata de utilizare estimată sau durata contractului **depășește 5 ani**, durata de amortizare este totuși **limitată la maximum 10 ani** — nu se poate amortiza, de exemplu, pe 20 sau 30 de ani, oricât de lungă ar fi durata reală de utilizare preconizată.
- Din perspectivă fiscală, aceleași cheltuieli de dezvoltare recunoscute contabil ca imobilizări necorporale „se recuperează prin intermediul deducerilor de amortizare liniară pe perioada contractului sau pe durata de utilizare, după caz" (Codul fiscal, art. 28 alin. (9)) — deci amortizarea fiscală urmează, ca metodă, amortizarea contabilă liniară.
- Atâta vreme cât cheltuielile de dezvoltare capitalizate nu sunt integral amortizate, legea restricționează distribuirea de profit, cu excepția cazului în care rezervele disponibile și profitul reportat acoperă cel puțin valoarea neamortizată (OMFP 1802/2014, pct. 184) — o regulă de protecție a capitalului adesea ignorată.

## Ce se greșește în practică

- Se amortizează cheltuielile de dezvoltare pe o durată arbitrară, fără legătură cu durata reală de utilizare estimată a proiectului sau cu durata contractului aferent.
- Se ignoră plafonul de 10 ani atunci când durata de utilizare estimată depășește 5 ani, extinzând amortizarea pe perioade nepermise de reglementările contabile.
- Se distribuie dividende fără să se verifice dacă rezervele disponibile acoperă partea neamortizată din cheltuielile de dezvoltare capitalizate — o restricție legală de multe ori trecută cu vederea.
- Se capitalizează cheltuieli care, de fapt, nu îndeplinesc criteriile stricte de recunoaștere ca imobilizare necorporală (proiect de cercetare, nu de dezvoltare propriu-zisă), trecându-le greșit la 203 în loc să rămână cheltuieli ale perioadei.

## Ce face iConta.eu

Din verificarea codului, iConta.eu recunoaște contul **203 „Cheltuieli de dezvoltare"** în planul de conturi (OMFP 1802/2014). La data acestui ghid, însă, aplicația **nu are un calculator dedicat de amortizare pentru imobilizările necorporale** (cum are, de exemplu, pentru pragul de încadrare a mijloacelor fixe corporale, prin modulul `obiecte_inventar.py`) — planul de amortizare pentru cheltuielile de dezvoltare capitalizate, inclusiv verificarea plafonului de 10 ani, se calculează și se introduce manual.

[iConta.eu](/)
