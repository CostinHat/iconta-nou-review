---
title: "Cum se înregistrează un mijloc fix primit cu titlu gratuit?"
description: "Evaluarea la valoare justă și contul de subvenții pentru investiții, conform OMFP 1802/2014, pentru un mijloc fix primit gratuit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează un mijloc fix primit cu titlu gratuit?

Un utilaj, un echipament sau orice altă imobilizare corporală poate ajunge în patrimoniul firmei fără plată — donație, sponsorizare primită în natură, transfer între entități afiliate. Regula de evaluare la intrare e diferită de cea aplicată bunurilor cumpărate, iar contrapartida contabilă nu e un cont de furnizor, ci unul de subvenții.

## Temeiul legal

::: ghid-temei
„75. - (1) La data intrării în entitate, bunurile se evaluează și se înregistrează în contabilitate la valoarea de intrare, care se stabilește astfel: a) la cost de achiziție - pentru bunurile procurate cu titlu oneros; ... b) la cost de producție - pentru bunurile produse în entitate; ... c) la valoarea de aport, stabilită în urma evaluării - pentru bunurile reprezentând aport la capitalul social; ... d) la valoarea justă - pentru bunurile obținute cu titlu gratuit sau constatate plus la inventariere."
— OMFP 1802/2014, pct. 75 alin. (1) lit. d) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Din normă rezultă mecanismul complet de înregistrare:

- **Valoarea de intrare** nu e prețul de achiziție (nu există), ci **valoarea justă** a bunului la data primirii — stabilită, de regulă, printr-o evaluare sau prin raportare la piață.
- **Contrapartida** nu e un cont de datorie (404/401), ci contul **475 "Subvenții pentru investiții"**: normele precizează, la funcțiunea conturilor de imobilizări (ex. 213 "Instalații tehnice și mijloace de transport"), că în debitul acestora se înregistrează „valoarea instalațiilor tehnice și a mijloacelor de transport primite prin subvenții pentru investiții, cu titlu gratuit sau constatate plus la inventar (475)".
- Subvenția înregistrată în contul 475 **nu se recunoaște integral ca venit la primire** — se trece treptat la venituri (contul 7584), pe măsura amortizării calculate pentru mijlocul fix respectiv, exact ca la orice altă subvenție pentru investiții.

## Ce se greșește în practică

- Se înregistrează mijlocul fix la o valoare arbitrară sau la zero, în loc de valoarea justă documentată (evaluare, preț de piață pentru bunuri similare, valoare din actul de donație).
- Se creditează contul 758 "Alte venituri din exploatare" integral, la data primirii, în loc de 475 — ceea ce supraevaluează profitul lunii de intrare și nu respectă corelarea cu amortizarea.
- Se omite complet trecerea ulterioară a subvenției din 475 la 7584, pe măsura amortizării — subvenția rămâne "înghețată" în bilanț la nesfârșit.

## Ce face iConta.eu

La data acestui ghid, `core/repo_mijloace_fixe.py` oferă funcții generale de gestiune a mijloacelor fixe — `adauga()` și `adauga_cu_reevaluare()` — cu parametri liberi pentru cont de imobilizare, cont de amortizare și valoare de intrare. Contabilul poate introduce manual valoarea justă și poate alege contul de contrapartidă potrivit (475), dar aplicația **nu are un flux dedicat „primire cu titlu gratuit"** care să completeze automat contrapartida 475 și să genereze, lună de lună, trecerea proporțională la 7584 corespunzător amortizării. Această corelare rămâne, azi, în sarcina contabilului.

[iConta.eu](/)
