---
title: "Cum se generează XML-ul D406?"
description: "Structura fișierului standard de control fiscal (SAF-T) și cadrul legal al Declarației informative D406, conform normelor ANAF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se generează XML-ul D406?

D406 nu este o declarație completată manual, câmp cu câmp — este un fișier XML generat din evidența contabilă a firmei, după o structură standard impusă de ANAF (SAF-T), verificat de un program de validare oficial înainte de depunere.

## Temeiul legal

::: ghid-temei
„Fişierul standard de control fiscal (SAF-T) se transmite de către contribuabili/plătitori prin intermediul unei declaraţii informative, denumită în continuare Declaraţia informativă D406 [...] SAF-T este un fişier în format electronic, de tip XML, conţinând date extrase [din evidența contabilă şi fiscală]."
— OPANAF nr. 1.783/2021 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Câteva elemente structurale, așa cum rezultă din procedura ANAF:

- SAF-T (fișierul XML propriu-zis) este anexat Declarației informative D406, care se poate genera și în format PDF cu XML atașat, cu semnătură electronică aplicată.
- Structura SAF-T este definită de ANAF pe baza standardului internațional OECD SAF-T 2.0, adaptat pentru România — conține secțiuni precum registrul jurnal general, facturile de vânzare și de cumpărare, plățile și mișcările de bunuri.
- Generarea corectă a XML-ului trebuie validată cu programul „Validator" pus la dispoziție de ANAF pentru fișierul SAF-T — un fișier care nu trece validarea nu poate fi transmis ca declarație validă.
- Declarația se depune electronic, iar frecvența de raportare (lunară sau trimestrială) urmează perioada fiscală aplicabilă pentru TVA a contribuabilului.

## Ce se greșește în practică

- Se generează un fișier XML pe baza unei interpretări proprii a structurii, fără validare pe programul oficial ANAF — orice discrepanță structurală (nume de element, cardinalitate) duce la respingerea declarației.
- Se ignoră faptul că o lună fără mișcări contabile tot trebuie raportată, ca declarație „pe zero", nu se omite depunerea doar pentru că nu au existat tranzacții.
- Se confundă structura anuală de referință (categoria de contribuabil, mare/mijlociu/mic) cu structura tehnică a fișierului — data de la care se depune D406 diferă pe categorii, dar formatul XML rămâne același pentru toți.

## Ce face iConta.eu

iConta.eu generează efectiv fișierul XML SAF-T pentru Declarația D406, în modulul `core/d406.py`, pe baza registrelor contabile din aplicație (jurnal general, facturi, plăți, active). Generatorul a fost verificat pe validatorul oficial ANAF (DUK), inclusiv pentru cazul unei luni fără mișcări, când se depune o declarație „pe zero", fără a inventa tranzacții. Aplicația mapează sursele interne (facturi, note contabile, jurnal de casă/bancă) pe structura de jurnale auxiliare cerută de normă, iar liniile de tranzacție poartă identificarea partenerului sau a codului propriu, conform regulilor XSD ale schemei SAF-T.

[iConta.eu](/)
