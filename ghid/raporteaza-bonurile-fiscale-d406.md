---
title: "Cum se raportează bonurile fiscale în D406?"
description: "Ce spune ordinul ANAF privind fișierul standard de control fiscal (SAF-T) despre obligația de raportare și unde se încadrează bonurile fiscale emise prin case de marcat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează bonurile fiscale în D406?

Fișierul standard de control fiscal (SAF-T), depus prin declarația informativă D406, cere o evidență electronică a operațiunilor economice ale contribuabilului. Pentru firmele cu vânzare cu amănuntul, întrebarea e inevitabilă: intră și bonurile fiscale emise prin casa de marcat electronică fiscală (AMEF) în acest fișier, și dacă da, cum?

## Temeiul legal

::: ghid-temei
„1. Fişierul standard de control fiscal (SAF-T), prevăzut la art. 59^1 alin. (1) din Legea nr. 207/2015 privind Codul de procedură fiscală, cu modificările şi completările ulterioare, reprezintă un standard internaţional utilizat pentru transferul electronic de date din evidenţa contabilă şi fiscală, de la contribuabili/plătitori către autorităţile fiscale şi auditori."
— OPANAF 1783/2021, anexa 1, pct. 1 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Ordinul stabilește obligația generală de raportare a evidenței contabile și fiscale prin D406, dar structura tehnică exactă a fișierului (ce secțiune XML primește bonurile fiscale — de regulă agregate pe zi, prin raportul Z, nu bon cu bon) este dată de schema XSD oficială a SAF-T, un document tehnic separat de textul ordinului, la care nu am acces într-o formă verbatim în sursele disponibile aici. Ce se poate confirma din text:

- Obligația de transmitere D406 și termenele ei sunt fixate prin OPANAF 1783/2021 (înlocuit ulterior, pentru unele categorii, de OPANAF 407/2025), în funcție de categoria de contribuabil.
- Baza legală a fișierului însuși e art. 59^1 din Codul de procedură fiscală (Legea 207/2015).
- Bonurile fiscale, ca atare, provin din aparatul de marcat electronic fiscal (AMEF), reglementat separat prin OPANAF 146/2018 (structura raportului Z), nu prin ordinul SAF-T.

**Limitare onestă:** nu am găsit, în sursele disponibile, o prevedere care să detalieze explicit secțiunea SAF-T în care se încadrează bonurile fiscale (spre deosebire de facturi, unde structura e clară). Pentru mapare tehnică exactă, temeiul corect e schema XSD oficială ANAF pentru D406, nu un text de lege — o distincție importantă, pentru că regulile de validator nu sunt normă fiscală.

## Ce se greșește în practică

- Se presupune că fiecare bon fiscal trebuie raportat individual în D406, ca o factură — de regulă, vânzările cu amănuntul se agregă pe zi/casă de marcat, prin raportul Z, nu bon cu bon.
- Se confundă obligația SAF-T cu obligația de arhivare a jurnalului electronic al casei de marcat — sunt doua fluxuri distincte, cu temeiuri diferite.
- Se ignoră faptul că termenul de transmitere D406 diferă pe categorii de contribuabili (mari, mijlocii, mici), stabilit prin anexele ordinului, nu printr-un termen unic.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **importă raportul Z** din fișierul exportat de casa de marcat electronică fiscală (format AMEF, conform OPANAF 146/2018, anexa 2, secțiunea II.7), prin modulul de import AMEF. În schimb, generatorul de D406/SAF-T **nu include încă datele din bonurile fiscale/rapoartele Z** — la fel ca la declarația D394, unde codul menționează explicit că secțiunile pentru facturi simplificate și AMEF „rămân 0 până se construiesc". Această limitare e reală și asumată, nu ascunsă în spatele unei generări „complete" a declarației.

[iConta.eu](/)
