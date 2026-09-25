---
title: "Termene fiscale pentru firmele care depășesc plafonul de TVA"
description: "Ce termen legal are o firmă neplătitoare de TVA atunci când cifra de afaceri depășește plafonul de scutire de 395.000 lei, și de când se aplică regimul normal de taxare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Termene fiscale pentru firmele care depășesc plafonul de TVA

O firmă neînregistrată în scopuri de TVA nu are voie să treacă pur și simplu peste plafonul de scutire fără nicio consecință: din momentul depășirii, legea îi impune obligația de a solicita înregistrarea, iar termenul nu e generos — e practic imediat, nu la finalul lunii sau al trimestrului.

## Temeiul legal

::: ghid-temei
„Persoana impozabilă stabilită în România [...], a cărei cifră de afaceri anuală, declarată sau realizată, nu depășește plafonul de 395.000 lei, poate aplica scutirea de taxă, denumită în continuare regim special de scutire [...]"
— Legea 227/2015, art. 310 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Persoana impozabilă [...] trebuie să solicite înregistrarea în scopuri de TVA la organul fiscal competent, după cum urmează: [...] b) dacă în cursul unui an calendaristic depășește plafonul de scutire prevăzut la art. 310 alin. (1), cel târziu la data depășirii plafonului."
— Legea 227/2015, art. 316 alin. (1) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din aceste texte rezultă mecanismul concret:

- **Plafonul** este 395.000 lei cifră de afaceri anuală, declarată sau realizată — nu 300.000 lei, cifră care a fost valabilă doar până la 31 august 2025, când OG 22/2025 a majorat-o.
- **Termenul de solicitare a înregistrării** nu e un număr de zile de la depășire, ci „cel târziu la data depășirii plafonului" — practic, obligația se naște chiar în ziua/tranzacția care duce la depășire, nu ulterior.
- Pentru cei care aplicau deja regimul special de scutire și îl depășesc în cursul anului, art. 310 alin. (6) confirmă aceeași logică: „trebuie să solicite înregistrarea în scopuri de TVA [...] cel târziu la data depășirii plafonului", regimul normal de taxare aplicându-se „începând cu tranzacția care conduce la depășirea plafonului", nu de la începutul lunii sau de la data înregistrării efective.

## Ce se greșește în practică

- Se aplică vechiul reflex al unui termen de „10 zile de la depășire" (valabil în alte contexte de înregistrare fiscală), în loc de termenul real — care e chiar data depășirii.
- Se calculează greșit momentul depășirii, considerând finalul lunii sau al trimestrului, în loc de tranzacția exactă care duce cifra de afaceri peste 395.000 lei.
- Se emit facturi fără TVA și după data depășirii, deși regimul normal de taxare se aplică deja de la tranzacția care a produs depășirea — riscul e recalificarea facturilor ca TVA neaplicată, deși ar fi trebuit colectată.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu calculează și nu monitorizează automat** cifra de afaceri cumulată a firmei față de plafonul de 395.000 lei de scutire TVA. Aplicația urmărește intern doar un alt plafon, cel al TVA la încasare (`plafon_tva_incasare`, folosit de motorul din `core/tva_incasare.py`), care este un prag diferit, cu regim fiscal diferit. Verificarea depășirii plafonului de scutire pentru întreprinderile mici și inițierea la timp a înregistrării în scopuri de TVA rămân, la acest moment, responsabilitatea contabilului.

[iConta.eu](/)
