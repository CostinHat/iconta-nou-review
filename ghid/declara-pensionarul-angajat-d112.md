---
title: "Cum se declară pensionarul angajat în D112?"
description: "Câmpul obligatoriu „Pensionar" din structura declarației 112, pentru salariații care au și calitatea de pensionar, conform documentației oficiale ANAF."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se declară pensionarul angajat în D112?

Un salariat care este și pensionar nu se declară altfel decât un salariat obișnuit în ce privește contribuțiile — dar structura declarației 112 cere marcarea explicită a acestei calități, printr-un câmp dedicat, la nivelul fiecărui raport de muncă din anexele nominale.

## Temeiul legal

::: ghid-temei
„15 A_2 Pensionar N(1) DA Valori : 1- pensionar sau 0 ERR : campul pensionar necompletat/incorect [...]
30 B1_2 2.Pensionar N(1) DA Valori : 1-pensionar sau 0"
— Structura oficială a Declarației 112, câmpurile A_2 (Anexa 1.1) și B1_2 (Anexa 1.2) (sursă: anaf_surse/d112_struct_anaf.txt)
:::

Ce rezultă din documentația tehnică oficială ANAF privind structura fișierului XML al D112:

- Pentru fiecare raport de muncă declarat în Anexa 1.1 (respectiv 1.2), există un câmp numeric **obligatoriu** ("DA" la coloana de obligativitate) numit „Pensionar", care acceptă doar valorile **1** (dacă persoana are calitatea de pensionar) sau **0** (dacă nu are).
- Completarea greșită sau lipsa acestui câmp generează o eroare de validare explicită („campul pensionar necompletat/incorect"), care blochează validarea declarației.
- Câmpul se completează la nivelul fiecărui raport de muncă, nu la nivelul întregii declarații — dacă o persoană are mai multe raporturi de muncă simultan (de exemplu, contract cu normă întreagă și un contract cu timp parțial la același angajator), calitatea de pensionar se marchează separat, pe fiecare raport declarat.

## Ce se greșește în practică

- Se lasă câmpul „Pensionar" necompletat sau se completează implicit cu 0, indiferent de situația reală a salariatului, ceea ce generează eroare de validare la depunere sau, mai grav, o declarație validă dar cu date incorecte.
- Se presupune că bifarea acestui câmp modifică automat regimul de contribuții al salariatului — câmpul este, în primul rând, o cerință de structură/raportare a datelor către sistemul de pensii și de sănătate, iar eventuale regimuri speciale legate de calitatea de pensionar se stabilesc prin alte prevederi legale, verificate separat de la caz la caz.
- Se omite actualizarea câmpului atunci când un salariat activ obține calitatea de pensionar în timpul anului (de exemplu, la pensionare pentru limită de vârstă, rămânând angajat) — informația trebuie reflectată în declarațiile lunare ulterioare acestui moment.

## Ce face iConta.eu

iConta.eu generează declarația 112 din datele de salarizare introduse în aplicație, inclusiv structura pe anexe nominale cerută de ANAF. Marcarea corectă a calității de pensionar pentru un angajat depinde de datele introduse în fișa salariatului — contabilul trebuie să seteze acest atribut în profilul angajatului pentru ca declarația generată să reflecte corect situația reală, conform structurii oficiale D112.

[iConta.eu](/)
