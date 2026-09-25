---
title: "Ce se întâmplă dacă depun D394 cu întârziere?"
description: "Termenul de depunere D394 e ziua 30 a lunii următoare (excepție ianuarie), iar nedepunerea la termen e contravenție sancționată cu amendă între 500 și 5.000 lei, în funcție de mărimea firmei."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce se întâmplă dacă depun D394 cu întârziere?

Depunerea cu întârziere a D394 e o contravenție — cu amendă între 500 și 5.000 lei, în funcție de categoria contribuabilului — indiferent dacă declarația e „pe zero" sau conține operațiuni.

## Temeiul legal

::: ghid-temei
„Declaraţia se depune la organul fiscal competent până în data de 30 inclusiv a lunii următoare încheierii perioadei de raportare, declarate pentru depunerea decontului (luna, trimestrul etc.) [...] În cazul în care perioada de raportare este luna calendaristică, termenul de depunere a declaraţiei pentru luna ianuarie este până la data de 28, respectiv 29 februarie."
— OPANAF 2194/2025, Anexa 2 pct. 2 (sursă: anaf_surse/opanaf_2194_2025_d394.txt)

„neîndeplinirea de către contribuabil/plătitor la termen a obligaţiilor de declarare prevăzute de lege [...] precum şi orice informaţii în legătură cu impozitele, taxele, contribuţiile, bunurile şi veniturile impozabile, dacă legea prevede declararea acestora"
— Legea 207/2015 (Codul de procedură fiscală), art. 336 alin. (1) lit. b) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„cu amendă de la 1.000 lei la 5.000 lei pentru persoanele juridice încadrate în categoria contribuabililor mijlocii şi mari şi cu amendă de la 500 lei la 1.000 lei, pentru celelalte persoane juridice, precum şi pentru persoanele fizice, în cazul săvârşirii faptei prevăzute la alin. (1) lit. a), b) şi i) - m)"
— Legea 207/2015, art. 336 alin. (2) lit. d) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Din aceste texte rezultă:

- Termenul normal e **ziua 30** a lunii următoare perioadei de raportare (lunar, trimestrial etc., aliniat cu periodicitatea decontului de TVA), cu excepția lunii ianuarie, unde termenul e **28, respectiv 29 februarie**.
- Depunerea peste acest termen se încadrează la art. 336 alin. (1) lit. b) din Codul de procedură fiscală, ca „neîndeplinire la termen a obligațiilor de declarare" — D394 fiind o declarație informativă creată prin ordin ANAF, sub temeiul CPF art. 59.
- Amenda: **1.000–5.000 lei** pentru persoanele juridice încadrate la contribuabili mijlocii/mari, respectiv **500–1.000 lei** pentru celelalte persoane juridice și pentru persoanele fizice.
- Declarația se depune inclusiv dacă în perioada de raportare nu au existat operațiuni de natura celor din D394 — deci întârzierea unei declarații „pe zero" e sancționabilă la fel ca a uneia cu operațiuni.

## Ce se greșește în practică

- Se presupune că termenul D394 e identic cu cel de la decontul de TVA (D300, ziua 25) — de fapt D394 are termen propriu, ziua 30 (cu excepția lunii ianuarie).
- Se amână depunerea declarației „pe zero", crezând că lipsa operațiunilor scutește de obligație — textul spune explicit contrariul.
- Se ignoră faptul că amenda diferă după categoria contribuabilului (mijlociu/mare vs. restul), nu e o sumă fixă unică.

## Ce face iConta.eu

Termenul de depunere D394 e urmărit intern la ziua 30 a lunii următoare (`core/scadente.py`), aliniat cu textul citat mai sus, și cu excepția lunii ianuarie tratată separat pentru februarie. Semaforul de conformare fiscală din aplicație verifică declarațiile datorate față de vectorul fiscal al firmei și le compară cu cele depuse, pentru a semnala termenele apropiate sau depășite.

Dincolo de această urmărire a termenului, **iConta.eu nu depune automat D394 la ANAF** — fișierul e validat local prin validatorul oficial (DUK) înainte de a fi considerat gata, dar transmiterea efectivă, cu respectarea sau nu a termenului, rămâne manuală, prin portalul SPV.

[iConta.eu](/)
