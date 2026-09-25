---
title: "Ce se întâmplă dacă ANAF modifică schema SAF-T?"
description: "Cum sunt reglementate modificările aduse structurii Declarației D406 (SAF-T) și ce înseamnă asta pentru firmele care generează fișierul de raportare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce se întâmplă dacă ANAF modifică schema SAF-T?

Structura fișierului standard de control fiscal (SAF-T), raportat prin Declarația informativă D406, nu este fixată o singură dată — ANAF a modificat-o deja de mai multe ori de la introducerea ei, prin ordine care înlocuiesc integral anexele actului normativ inițial. Pentru firme, asta înseamnă că același formular „D406" poate cere, la momente diferite, structuri XML diferite.

## Temeiul legal

::: ghid-temei
„Art. I - Anexa nr. 5 la Ordinul președintelui Agenției Naționale de Administrare Fiscală nr. 1.783/2021 privind natura informațiilor pe care contribuabilul/plătitorul trebuie să le declare prin fișierul standard de control fiscal, modelul de raportare, procedura și condițiile de transmitere, precum și termenele de transmitere și data/datele de la care categoriile de contribuabili/plătitori sunt obligate să transmită fișierul standard de control fiscal, publicat în Monitorul Oficial al României, Partea I, nr. 1073 din 9 noiembrie 2021, cu modificările ulterioare, se modifică și se înlocuiește cu anexa care face parte integrantă din prezentul ordin."
— OPANAF 407/2025, art. I, având în vedere art. 59^1 alin. (2), (4) și (5) din Legea 207/2015 (sursă: anaf_surse/opanaf_407_2025_saft_d406.txt)
:::

- Obligația de raportare SAF-T și structura ei sunt reglementate prin ordin al președintelui ANAF (inițial OPANAF 1783/2021), emis în temeiul Codului de procedură fiscală — ceea ce înseamnă că ANAF poate modifica anexele acestui ordin (inclusiv datele de la care diverse categorii de contribuabili devin obligate, sau structura tehnică a fișierului) printr-un ordin ulterior, fără să fie nevoie de o lege nouă.
- OPANAF 407/2025 este exact un astfel de exemplu: a înlocuit integral Anexa nr. 5 a OPANAF 1783/2021 (cea care stabilește datele de la care diferite categorii de contribuabili — mari, mijlocii, mici — au obligația de depunere).
- Practic, când ANAF modifică schema, contribuabilii și furnizorii de software trebuie să adapteze generarea fișierului XML la noua structură publicată oficial (fișierul XSD și nomenclatoarele aferente, disponibile pe site-ul ANAF) — vechea structură nu mai este validă de la data la care noul ordin intră în vigoare.
- Nu există, în textele analizate, o perioadă de grație generală garantată prin lege pentru trecerea la o schemă nouă — fiecare modificare de schemă vine, de regulă, cu propriile date de aplicare, stabilite explicit în ordinul respectiv.

## Ce se greșește în practică

- Se presupune că „D406" este o structură fixă, stabilită o dată pentru totdeauna prin OPANAF 1783/2021 din 2021 — de fapt anexele acestui ordin (inclusiv structura tehnică) pot fi și au fost modificate ulterior prin alte ordine.
- Se generează fișierul XML cu o versiune veche a schemei, fără verificarea prealabilă că structura folosită corespunde celei publicate curent de ANAF, ceea ce duce la respingere la validare.
- Se ignoră datele de aplicare specifice ale unei noi versiuni de schemă (care pot diferi pe categorii de contribuabili), presupunând că modificarea se aplică imediat tuturor, uniform.

## Ce face iConta.eu

Generatorul D406 din iConta.eu (`d406.py`) este construit direct din schema XSD oficială descărcată de la ANAF, cu referințe explicite, datate, la sursa folosită (de exemplu la nomenclatoare și structuri preluate din fișierul oficial `d406_schema_anaf.xlsx`, cu mențiunea versiunii aplicabile). Aceasta înseamnă că, atunci când ANAF publică o schemă nouă, codul generatorului trebuie actualizat manual pentru a reflecta noua structură — aplicația nu se „auto-actualizează" la o schemă nouă fără o intervenție de dezvoltare, dar urmărește explicit sursa oficială ca reper, exact pentru a evita generarea unor fișiere pe o structură depășită.

[iConta.eu](/)
