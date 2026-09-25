---
title: "TVA 2026: cine este obligat să se înregistreze în scopuri de TVA"
description: "Plafonul de scutire pentru întreprinderile mici, valabil în 2026, și momentul în care înregistrarea în scopuri de TVA devine obligatorie, conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# TVA 2026: cine este obligat să se înregistreze în scopuri de TVA

Plafonul de scutire de TVA pentru întreprinderile mici s-a schimbat în 2025 și rămâne valabil și în 2026 — dar mulți contribuabili încă lucrează cu vechea valoare.

## Temeiul legal

::: ghid-temei
„Persoana impozabilă stabilită în România conform art. 266 alin. (2) lit. a), a cărei cifră de afaceri anuală, declarată sau realizată, nu depășește plafonul de 395.000 lei, poate aplica scutirea de taxă, denumită în continuare regim special de scutire, pentru operațiunile prevăzute la art. 268 alin. (1) [...]."
— Legea 227/2015 (Codul fiscal), art. 310 alin. (1), modificat prin OG 22/2025 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Concret, în 2026, obligația de înregistrare în scopuri de TVA se declanșează astfel:

- Plafonul de scutire pentru întreprinderile mici este **395.000 lei cifră de afaceri anuală** — nu 300.000 lei, cum era valabil până la 1 septembrie 2025.
- Persoana impozabilă care depășește acest plafon **trebuie să solicite înregistrarea în scopuri de TVA**, aplicând regimul normal de taxare de la data depășirii.
- Dacă organul fiscal constată că înregistrarea nu a fost solicitată sau a fost solicitată cu întârziere, poate înregistra din oficiu persoana impozabilă, cu data înregistrării stabilită retroactiv, la data depășirii plafonului.
- Pentru firmele nou-înființate, plafonul de scutire se aplică integral pentru primul an de activitate, calculat proporțional cu perioada rămasă din anul calendaristic de la înființare.
- Există și o regulă tranzitorie: firmele care au depășit în august 2025 vechiul plafon de 300.000 lei nu au fost obligate să se înregistreze decât la depășirea noului plafon de 395.000 lei, dacă la acel moment nu îl depășiseră deja.

## Ce se greșește în practică

- Se folosește în continuare pragul vechi de 300.000 lei pentru a decide dacă e nevoie de înregistrare, deși plafonul curent este de 395.000 lei.
- Se calculează cifra de afaceri incluzând operațiuni excluse expres de lege din baza de calcul a plafonului (de exemplu, anumite livrări intracomunitare de mijloace de transport noi).
- Se așteaptă notificarea din partea ANAF pentru a solicita înregistrarea, deși obligația este a contribuabilului de a o solicita din proprie inițiativă, la depășirea plafonului.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu monitorizează automat apropierea sau depășirea plafonului de 395.000 lei** — nu am găsit în cod (`core/`) o funcție care să urmărească cifra de afaceri cumulată a unei firme neplătitoare de TVA și să semnaleze depășirea plafonului de scutire. Odată ce o firmă este înregistrată în scopuri de TVA, aplicația generează corect declarațiile aferente (D300 și altele), dar decizia și momentul înregistrării rămân în sarcina contabilului.

[iConta.eu](/)
