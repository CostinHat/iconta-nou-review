---
title: "D205 pentru dividende către persoane fizice: date necesare"
description: "Structura declarației D205 pentru dividendele plătite unor persoane fizice rezidente și datele obligatorii pe fiecare beneficiar, conform structurii ANAF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# D205 pentru dividende către persoane fizice: date necesare

D205 nu este un simplu total de impozit reținut — este o declarație pe beneficiar, cu date individuale pentru fiecare asociat care a primit dividende, structurate strict conform schemei XML impuse de ANAF.

## Temeiul legal

::: ghid-temei
„<declaratie205 luna=\"12\" an=\"AAAA\" [...] cui=\"...\" nume_declar=\"...\" [...]>
<sect_II tip_venit=\"08\" nrben=\"N\" [...] Tbaza=\"...\" Timp=\"...\">
<benef tip_venit1=\"08\" den1=\"...\" Rezid=\"1\" cifR=\"...\" tip_plata=\"2\" divid_D=\"...\" divid_P=\"...\" baza1=\"...\" imp1=\"...\"/>
</sect_II>
</declaratie205>"
— OPANAF nr. 102/2025, structura declarației 205 (sursă: anaf_surse/d205_struct_anaf.txt) — notație reconstituită pe baza denumirilor exacte de câmpuri din documentul de structură (secțiunea I: `cui`, `nume_declar`; secțiunea II: `tip_venit`, `nrben`, `Tbaza`, `Timp`; secțiunea beneficiari: `tip_venit1`, `den1`, `Rezid`, `cifR`, `tip_plata`, `divid_D`, `divid_P`, `baza1`, `imp1`), documentul sursă fiind un tabel de câmpuri, nu un exemplu XML redat ca atare
:::

Pentru fiecare beneficiar de dividende trecut în D205, structura cere, în esență:

- **Identitatea beneficiarului** — nume (`den1`) și cod de identificare fiscală CNP/NIF din România (`cifR`), acesta din urmă determinând și rezidența (câmpul `Rezid`: un CNP românesc valid de rezident produce `Rezid=1`; dividendele către nerezidenți nu se declară pe D205, ci pe D207).
- **Codul tipului de venit** (`tip_venit1`) „08", corespunzător nomenclatorului ANAF pentru „venituri din dividende" (categoria 1.a).
- **Dividendul distribuit** (`divid_D`) și **dividendul plătit** (`divid_P`) — două valori distincte, pentru că un dividend poate fi distribuit într-un an și plătit în altul, iar impozitul se calculează pe baza plății, cu cota aplicabilă la data distribuirii.
- **Baza impozabilă** (`baza1`) și **impozitul reținut** (`imp1`) pe fiecare beneficiar, plus totalurile pe secțiune (`Tbaza`, `Timp`) și numărul de beneficiari (`nrben`).

## Ce se greșește în practică

- Se completează declarația cu suma dividendelor distribuite, nu a celor efectiv plătite în anul de raportare — cele două valori sunt distincte în structura oficială, iar impozitul se leagă de plată, nu de distribuire.
- Se omite corelarea corectă între rezidența beneficiarului (derivată din CNP) și secțiunea de declarare — un beneficiar identificat greșit ca rezident, deși are cod de nerezident, produce o declarație respinsă de validator.
- Se tratează codul de tip de venit ca fiind arbitrar sau opțional — „08" este codul specific din nomenclatorul ANAF pentru dividende și nu poate fi înlocuit cu alt cod de venit din investiții.

## Ce face iConta.eu

Generatorul D205 din iConta.eu (`core/d205.py`) construiește automat structura de mai sus din registrele proprii ale aplicației: citește mișcările contului 457 („Dividende de plată") pentru a distinge distribuirea (creditul contului) de plata efectivă (debitul contului), derivă rezidența fiecărui beneficiar din formatul codului de identificare introdus în modulul de asociați, și calculează baza și impozitul pe fiecare beneficiar, ponderat pe cota aplicabilă datei fiecărei distribuiri. Aplicația a fost verificată pe validatorul oficial ANAF (DUK), atât cu profiluri minime construite manual, cât și pe date reale.

[iConta.eu](/)
