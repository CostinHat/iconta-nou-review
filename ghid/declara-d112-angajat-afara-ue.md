---
title: "Cum se declară în D112 un angajat din afara UE?"
description: "Regimul contribuțiilor sociale pentru un salariat cetățean al unui stat din afara UE, condiționat de existența unui acord de securitate socială, și codificarea CNP/NIF în D112."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se declară în D112 un angajat din afara UE?

Un salariat cetățean al unui stat din afara Uniunii Europene nu se declară automat la fel ca un angajat român sau dintr-un stat membru UE — regimul contribuțiilor sociale depinde de existența (sau absența) unui acord de securitate socială între România și statul de cetățenie al salariatului.

## Temeiul legal

::: ghid-temei
„Următoarele persoane au calitatea de contribuabili/plătitori de venit la sistemul public de pensii, cu respectarea legislației europene aplicabile în domeniul securității sociale, precum și a acordurilor privind sistemele de securitate socială la care România este parte, după caz: a) cetățenii români, cetățenii altor state sau apatrizii, pe perioada în care au, conform legii, domiciliul ori reședința în România."
— Legea 227/2015 (Codul fiscal), art. 136 alin. (1) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Regula de fond, pentru contribuțiile sociale: se aplică legislația română, **cu respectarea** legislației europene de coordonare (irelevantă pentru un cetățean din afara UE) **și a acordurilor bilaterale de securitate socială** pe care România le are cu alte state. Practic:

- Dacă România are un **acord de securitate socială** cu statul de cetățenie al angajatului, acordul poate scuti salariatul de contribuțiile sociale românești pentru o perioadă determinată (de regulă pe baza unui certificat de detașare/atestare emis de statul de origine), sau poate stabili reguli speciale de cumul.
- Dacă **nu există un astfel de acord**, salariatul din afara UE angajat cu contract de muncă în România datorează, în principiu, contribuțiile sociale românești ca orice alt salariat cu reședința în țară.
- Din punct de vedere tehnic, structura D112 acceptă identificarea salariatului fie prin **CNP**, fie prin **NIF** (numărul de identificare fiscală atribuit străinilor fără CNP) — câmpul „cnpAsig" din declarație e definit expres ca „CNP/NIF".

## Ce se greșește în practică

- Se aplică automat scutirea de contribuții sociale doar pentru că angajatul e cetățean străin, fără a verifica dacă există efectiv un acord de securitate socială cu statul respectiv și fără certificatul care atestă asigurarea în celălalt stat.
- Se încearcă declararea salariatului doar cu CNP, deși un cetățean din afara UE, nou-venit, poate avea alocat inițial doar un NIF — declarația trebuie completată cu identificatorul disponibil la momentul respectiv, nu blocată în așteptarea unui CNP.
- Se ignoră faptul că regimul de contribuții pentru un salariat din afara UE poate diferi de la o lună la alta, dacă în cursul relației de muncă apare sau expiră un document de detașare/atestare din statul de origine.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează D112 din datele de salarizare introduse pentru fiecare angajat, dar aplicația **nu are o logică dedicată** pentru verificarea existenței unui acord de securitate socială aplicabil sau pentru gestionarea distinctă a salariaților cu NIF în locul CNP — încadrarea corectă a regimului de contribuții pentru un angajat din afara UE rămâne o verificare manuală a contabilului.

[iConta.eu](/)
