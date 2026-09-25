---
title: "Cum se generează XML-ul pentru D112?"
description: "Obligația de depunere electronică a declarației 112 și structura de bază a fișierului XML cerut de ANAF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se generează XML-ul pentru D112?

Declarația 112 — cea prin care se raportează lunar contribuțiile sociale, impozitul pe venitul din salarii și evidența nominală a asiguraților — nu se poate depune pe hârtie de către majoritatea angajatorilor. Legea impune transmiterea ei electronică, printr-un fișier XML structurat conform modelului aprobat oficial de ANAF, CNPP, CNAS și ANOFM.

## Temeiul legal

::: ghid-temei
„Art. 1 - (1) Se aprobă modelul şi conţinutul formularului 112 «Declaraţie privind obligaţiile de plată a contribuţiilor sociale, impozitului pe venit şi evidenţa nominală a persoanelor asigurate», precum şi anexele nr. 1.1 «Anexa angajator» şi nr. 1.2 «Anexa asigurat» la acesta [...] (4) Declaraţia prevăzută la alin. (1) este o declaraţie de impunere în sensul art. 1 pct. 18 din Legea nr. 207/2015 privind Codul de procedură fiscală [...]
Art. 3 - Persoanele fizice şi juridice care au calitatea de angajatori sau sunt asimilate acestora [...] au obligaţia depunerii declaraţiei prevăzute la art. 1 prin mijloace electronice de transmitere la distanţă."
— Ordinul comun ANAF/CNPP/CNAS/ANOFM nr. 605/95/928/2.314/2026 pentru aprobarea formularului 112, art. 1 alin. (1), (4) și art. 3 (sursă: anaf_surse/opanaf_605_2026_d112.txt)
:::

- D112 este, prin lege, o declarație de impunere — depunerea ei greșită sau cu întârziere are aceleași consecințe procedurale ca orice altă declarație fiscală (posibilă stabilire din oficiu, sancțiuni pentru nedepunere).
- Formularul are o structură fixă, cu formularul propriu-zis plus două anexe obligatorii: „Anexa angajator" (date la nivel de firmă) și „Anexa asigurat" (date per salariat/asigurat) — XML-ul trebuie să respecte exact schema publicată pentru fiecare perioadă de raportare, inclusiv nomenclatoarele anexate ordinului.
- Depunerea electronică e obligatorie pentru angajatori și persoanele asimilate acestora — nu e o opțiune, ci o cerință legală explicită.
- Structura XML se schimbă periodic (ordinul care o aprobă e reemis când se modifică formularul sau regulile de completare), astfel încât un fișier generat cu o schemă veche poate fi respins de sistemul ANAF pentru o perioadă de raportare ulterioară modificării.

## Ce se greșește în practică

- Se generează sau se reutilizează un XML pe o structură veche a formularului, fără să se verifice dacă ordinul care o aprobă a fost înlocuit pentru perioada de raportare curentă.
- Se depune declarația fără anexele obligatorii (angajator/asigurat) complete pentru fiecare salariat, ceea ce duce la respingerea sau la o declarație incompletă.
- Se confundă validarea locală a fișierului XML (structura corectă) cu validarea de fond a datelor (corectitudinea sumelor, coerența cu statul de plată) — un XML valid structural poate conține totuși date greșite.
- Se ignoră faptul că D112 e o declarație de impunere în sensul Codului de procedură fiscală, cu toate consecințele care decurg din asta (posibilitatea corectării prin declarație rectificativă, termene de prescripție etc.).

## Ce face iConta.eu

iConta.eu are o funcție dedicată de generare a XML-ului pentru D112, care produce fișierul pe baza datelor din statul de plată al fiecărei firme, pentru luna și anul selectate. Această funcție face parte din motorul intern de salarizare al aplicației și corelează sumele declarate cu notele contabile generate automat pentru contribuțiile sociale și impozitul pe salarii, pentru a reduce riscul de discrepanțe între contabilitate și declarație.

[iConta.eu](/)
