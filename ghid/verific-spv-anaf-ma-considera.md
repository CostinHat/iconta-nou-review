---
title: "Cum verific în SPV că ANAF mă consideră micro"
description: "Încadrarea ca microîntreprindere se verifică direct în Spațiul Privat Virtual al ANAF, pe baza pragului de venituri din Codul fiscal — nu prin conectorul OAuth folosit de iConta.eu pentru e-Factura și e-Transport."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific în SPV că ANAF mă consideră micro

Dacă ești plătitor de impozit pe veniturile microîntreprinderilor sau de impozit pe profit, e o informație pe care ANAF o are înregistrată în „vectorul fiscal" al firmei, vizibil în Spațiul Privat Virtual (SPV) — nu ceva ce trebuie dedus singur. Condiția de fond care determină încadrarea, însă, e stabilită de Codul fiscal, iar verificarea ei nu ține de conectorul tehnic prin care o aplicație de contabilitate comunică cu SPV, ci de datele efective ale firmei.

## Temeiul legal

::: ghid-temei
„(1) În sensul prezentului titlu, o microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent: [...]
c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile;"
— Codul fiscal (Legea 227/2015), art. 47 alin. (1) lit. c), astfel cum a fost modificat de OUG 8/2026, cu aplicare inclusiv pentru încadrarea ca microîntreprindere în anul fiscal 2026 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Plafonul de venituri de 100.000 euro e doar una dintre condițiile cumulative de la art. 47 — se verifică alături de celelalte (structura capitalului social, absența dizolvării/lichidării etc.), nu izolat.
- Încadrarea se face „la data de 31 decembrie a anului fiscal precedent" — deci regimul aplicabil pe parcursul anului curent depinde de situația de la finalul anului anterior, nu de veniturile realizate până în prezent în anul curent.
- Confirmarea oficială a regimului fiscal (micro sau profit) aplicat efectiv de ANAF unei firme se citește din vectorul fiscal, disponibil în contul de SPV al firmei — nu se calculează separat de contribuabil, deși contribuabilul e cel care trebuie să verifice singur, din propriile date, dacă îndeplinește condițiile legale.

## Ce se greșește în practică

- Se confundă „categoria de mărime a entității" (micro/mică/mijlocie-mare, criteriu contabil din OMFP 1802/2014, folosit pentru a stabili ce fel de situații financiare trebuie depuse) cu „microîntreprindere" în sensul fiscal (art. 47 Cod fiscal, criteriu de venituri, care determină impozitul pe profit vs. impozitul pe veniturile microîntreprinderilor) — sunt două noțiuni diferite, cu praguri și scopuri diferite, care din întâmplare folosesc același cuvânt.
- Se presupune că regimul fiscal se schimbă automat de îndată ce veniturile depășesc pragul în cursul anului — de fapt condiția se verifică la 31 decembrie a anului precedent, iar trecerea la impozit pe profit are propriile reguli de moment (de la trimestrul în care se depășește plafonul, în cursul anului curent, conform regulilor specifice de trecere).
- Se caută încadrarea fiscală într-un ecran al aplicației de contabilitate, când sursa oficială și autoritară e chiar vectorul fiscal din SPV, gestionat de ANAF.

## Ce face iConta.eu

Verificat direct în cod: funcționalitatea **F176 — Conectorul OAuth SPV/ANAF** (`core/spv_conector.py`) gestionează strict autorizarea tehnică dintre iConta și SPV — autentificarea cu certificat calificat, obținerea și reînnoirea tokenului de acces, apelurile către serviciile e-Factura și e-Transport. Nu conține nicio funcție legată de afișarea sau verificarea regimului fiscal (micro vs. profit) al unei firme; căutarea directă în cod nu a găsit nicio referință la „vector fiscal" sau la încadrarea ca microîntreprindere în acest modul. iConta.eu are, separat, o funcționalitate care determină **categoria de mărime a entității** conform OMFP 1802/2014 (folosită pentru a stabili tipul situațiilor financiare datorate) — dar aceasta e un criteriu contabil distinct de plafonul de venituri din art. 47 Cod fiscal și nu răspunde la întrebarea „mă consideră ANAF micro din punct de vedere fiscal". Verificarea propriu-zisă a acestei încadrări, la acest moment, se face direct în SPV, pe portalul ANAF — nu prin conectorul F176 sau prin vreo altă funcționalitate a aplicației.

[iConta.eu](/)
