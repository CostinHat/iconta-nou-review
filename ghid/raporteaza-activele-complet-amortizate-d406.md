---
title: "Cum se raportează activele complet amortizate în D406"
description: "Dacă un mijloc fix complet amortizat, dar încă în evidența contabilă, trebuie inclus în secțiunea Active a Declarației informative D406 (SAF-T)."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează activele complet amortizate în D406

Secțiunea "Active" a Declarației informative D406 (fișierul standard de control fiscal, SAF-T) reflectă inventarul contabil al mijloacelor fixe și imobilizărilor necorporale, nu doar pe cele cu valoare rămasă de amortizat. Un activ complet amortizat, dar care nu a fost scos din evidență, rămâne în continuare un element al patrimoniului și se raportează ca atare.

## Temeiul legal

::: ghid-temei
„Informaţiile privind «Activele» din cadrul Declaraţiei informative D406 sunt întocmite la nivelul anului financiar aplicat de către contribuabili şi transmise printr-o singură depunere, respectiv o singură raportare a Declaraţiei informative D406, până la data depunerii situaţiilor financiare aferente exerciţiului financiar la care se referă."
— OPANAF nr. 1.783/2021, Instrucțiunile de completare a Declarației informative D406 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Instrucțiunile ANAF stabilesc termenul și modul de transmitere a secțiunii "Active", dar nu tratează explicit cazul activelor complet amortizate — nu există o normă care să le excludă din raportare. Limitarea trebuie spusă clar: sursele disponibile nu conțin o prevedere dedicată acestei situații; ce se poate afirma cu temei e principiul general — secțiunea "Active" reflectă inventarul contabil existent, nu valoarea contabilă netă.

- **Un activ complet amortizat rămâne în evidența contabilă** până la scoaterea lui efectivă din gestiune (casare, vânzare, cedare) — amortizarea la zero nu echivalează cu ieșirea din patrimoniu.
- **Raportarea în D406 se face anual**, o singură dată pentru secțiunea Active, la termenul de depunere a situațiilor financiare anuale — nu lunar sau trimestrial, ca restul declarației.
- **Fiecare activ păstrat în evidență** trebuie să apară în fișier cu identificatorul lui de inventar, indiferent dacă valoarea contabilă netă a ajuns la zero.

## Ce se greșește în practică

- Se exclud din fișierul SAF-T activele complet amortizate, considerându-le "irelevante" pentru raportare, deși ele rămân în evidența contabilă a firmei.
- Se scot din gestiune contabil activele doar pentru că amortizarea s-a încheiat, fără o operațiune reală de casare sau cedare care să justifice ieșirea.
- Se confundă amortizarea completă cu ieșirea din patrimoniu, ceea ce poate crea discrepanțe între balanța de verificare și fișierul SAF-T transmis.

## Ce face iConta.eu

Motorul de amortizare al iConta.eu (`core/d406_active.py`) plafonează amortizarea calculată la valoarea amortizabilă a activului — odată atins acest plafon, amortizarea lunară se oprește, dar activul rămâne în evidență și e inclus în continuare în secțiunea Active a D406, cu valoare contabilă netă zero, până la o operațiune explicită de scoatere din gestiune.

[iConta.eu](/)
