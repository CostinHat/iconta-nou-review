---
title: "Cum se declară dividendele unui asociat cu rezidență fiscală în alt stat?"
description: "Impozitul pe dividendele plătite unui asociat nerezident, cota implicită de 16% și rolul convențiilor de evitare a dublei impuneri, conform Codului fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se declară dividendele unui asociat cu rezidență fiscală în alt stat?

Pentru un asociat nerezident, cota de impozit pe dividende nu este automat cea din dreptul intern — poate fi redusă printr-o convenție de evitare a dublei impuneri, dar numai dacă beneficiarul face dovada rezidenței sale fiscale.

## Temeiul legal

::: ghid-temei
„(4) Impozitul datorat de nerezidenţi pentru veniturile impozabile obţinute din România se calculează, se reţine, se declară şi se plăteşte la bugetul de stat de către plătitorii de venituri, astfel: [...]
b) 16% pentru veniturile din dividende prevăzute la art. 223 alin. (1) lit. a)."
— Legea nr. 227/2015 (Codul fiscal), art. 224 alin. (4) lit. b), astfel cum a fost modificat prin Legea nr. 141/2025 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cota de 16% este cea de drept intern, dar nu este obligatoriu ultimul cuvânt:

- Legea prevede și cote reduse pentru anumite categorii de nerezidenți — de exemplu, 10% pentru veniturile obținute din România de persoane fizice rezidente într-un stat membru al UE sau într-un stat cu convenție de evitare a dublei impuneri (art. 224 alin. (4) lit. c^1)) — dar aplicarea unei cote reduse ține de coroborarea corectă a categoriilor de venit, nu se aplică automat oricărui nerezident.
- Aplicarea unei convenții de evitare a dublei impuneri (care poate stabili o cotă și mai mică) este condiționată, la nivel general în Codul fiscal, de prezentarea de către beneficiar a unui **certificat de rezidență fiscală** valabil — fără acest document, plătitorul aplică cota din legea română.
- Impozitul se calculează, reține, declară și plătește de firma plătitoare, până la data de 25 a lunii următoare celei în care s-a plătit venitul, similar regulii pentru dividendele către rezidenți.
- Declararea nominală, pe beneficiar nerezident, se face prin Declarația informativă **D207**, nu prin D205 — D205 este rezervată explicit beneficiarilor rezidenți.

## Ce se greșește în practică

- Se aplică automat cota de 16% oricărui asociat nerezident, fără să se verifice dacă există o convenție de evitare a dublei impuneri aplicabilă și dacă beneficiarul a prezentat certificatul de rezidență fiscală care ar permite o cotă redusă.
- Se declară dividendele către un asociat nerezident prin D205, alături de cele către asociați rezidenți — D205 este destinată exclusiv beneficiarilor rezidenți; nerezidenții se raportează separat, prin D207.
- Se acceptă un certificat de rezidență fiscală expirat sau necorespunzător formal, fără verificarea condițiilor cerute pentru aplicarea convenției.

## Ce face iConta.eu

Generatorul D205 din iConta.eu (`core/d205.py`) **respinge explicit** înregistrarea unui beneficiar nerezident: rezidența este derivată automat din tipul codului de identificare (CNP românesc de rezident versus NIF străin, pașaport sau cod invalid), iar un asociat identificat ca nerezident nu poate fi inclus într-o declarație D205 — potrivit regulilor validatorului oficial ANAF, dividendele către nerezidenți se declară pe D207. Declarația D207 (`core/d207.py`) este implementată în aplicație, dar la acest moment este o declarație **manuală**: lista beneficiarilor nerezidenți și sumele plătite se introduc de contabil, aplicația neavând încă un registru propriu al plăților către nerezidenți din care să genereze automat aceste date.

[iConta.eu](/)
