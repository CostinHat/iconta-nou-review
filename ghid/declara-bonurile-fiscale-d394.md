---
title: "Se declară bonurile fiscale în D394?"
description: "Când un bon fiscal trebuie inclus în declarația 394 conform OPANAF 2194/2025 și ce acoperă azi generatorul D394 din iConta.eu pentru bonuri fiscale/facturi simplificate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Se declară bonurile fiscale în D394?

Da, dar nu ca operațiune obișnuită: bonurile fiscale intră în D394 doar dacă îndeplinesc condițiile unei facturi simplificate, și apar ca valoare totală, nu ca linie individuală de operațiune.

## Temeiul legal

::: ghid-temei
„De asemenea, în declarație se înscrie valoarea totală a facturilor simplificate şi a bonurilor fiscale care îndeplinesc condiţiile unei facturi simplificate conform prevederilor art. 319 alin. (12), (13) şi (21) din Codul fiscal, dacă au înscris codul de înregistrare în scopuri de TVA al beneficiarului."
— OPANAF 2194/2025, Anexa 2 (sursă: anaf_surse/opanaf_2194_2025_d394.txt)
:::

Structura oficială a declarației, confirmată și de codul validatorului instalat, tratează separat mai multe situații:

- **Livrări/prestări cu factură simplificată, cu CUI-ul beneficiarului înscris** — valoare totală pe cotă (câmp distinct, „FSLcod").
- **Livrări/prestări cu factură simplificată, fără CUI-ul beneficiarului, dar fără bon fiscal emis** — alt câmp totalizator („FSL").
- **Achiziții cu bon fiscal care îndeplinește condițiile unei facturi simplificate, cu CUI-ul beneficiarului înscris** — câmp propriu („BFAI").
- Pentru achizițiile fără CUI înscris, textul precizează explicit: „valoarea totală a bonurilor fiscale, inclusiv facturile simplificate şi bonurile fiscale care îndeplinesc condiţiile unei facturi simplificate ... indiferent dacă au/nu au înscris codul de înregistrare în scopuri de TVA al beneficiarului."

Un bon fiscal obișnuit, care nu îndeplinește condițiile unei facturi simplificate (de regulă: fără CUI/CNP al cumpărătorului și fără elementele minime cerute de art. 319), nu se raportează individual în D394.

## Ce se greșește în practică

- Se presupune că „bon fiscal" înseamnă automat „nu intră în D394" — de fapt intră, dar agregat pe totalul perioadei, nu ca operațiune cu partener identificat.
- Se confundă bonul fiscal obișnuit cu bonul fiscal care îndeplinește condițiile unei facturi simplificate (are, de regulă, CUI-ul cumpărătorului sau alte elemente din art. 319) — doar al doilea tip intră sub această regulă.
- Se așteaptă ca aplicația de contabilitate să extragă automat totalul bonurilor fiscale dintr-un flux de casă de marcat (AMEF), fără să se verifice dacă acel flux e conectat efectiv la evidență.

## Ce face iConta.eu

Generatorul D394 (`core/d394.py`) include în structura declarației toate câmpurile pentru facturi simplificate și bonuri fiscale (FSLcod, FSL, FSA, FSAI, BFAI) — validatorul oficial le cere prezente chiar și pe 0, așa că aplicația le populează întotdeauna. La data acestui ghid însă, **iConta.eu nu are încă funcționalitate de facturi simplificate sau conectare la case de marcat (AMEF)**: aceste câmpuri se transmit mereu cu valoarea 0, indiferent câte bonuri fiscale a emis sau primit firma în perioadă (comentariu explicit în cod: „iConta nu are inca facturi simplificate si AMEF -> raman 0 pana se construiesc").

Practic, dacă firma ta emite sau primește bonuri fiscale care îndeplinesc condițiile unei facturi simplificate, valoarea lor totală nu ajunge azi automat în D394 prin iConta.eu — trebuie calculată și urmărită separat, până la extinderea aplicației pe acest flux.

[iConta.eu](/)
