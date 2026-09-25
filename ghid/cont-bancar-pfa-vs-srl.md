---
title: "Cont bancar pentru PFA vs SRL: diferențe"
description: "De ce regimul contabil diferit dintre PFA și SRL explică nevoia practică a unui cont bancar dedicat activității, deși legea nu impune explicit un cont separat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cont bancar pentru PFA vs SRL: diferențe

Întrebarea "trebuie neapărat un cont bancar separat?" primește răspunsuri diferite pentru SRL și pentru PFA, dar nu pentru că vreo lege ar impune explicit un cont bancar dedicat — ci pentru că regimul lor contabil e fundamental diferit. Sursele disponibile nu conțin o normă care să oblige expres un cont bancar separat pentru PFA; ce se poate afirma cu temei e diferența de regim contabil, care explică practic de ce, la SRL, separarea patrimonială impune și separarea fluxurilor bancare.

## Temeiul legal

::: ghid-temei
„(1) Societățile comerciale, societățile/companiile naționale, regiile autonome, institutele naționale de cercetare-dezvoltare, societățile cooperatiste și celelalte persoane juridice au obligația să organizeze și să conducă contabilitatea financiară, potrivit prezentei legi. [...]
(5) Persoanele fizice care desfășoară activități producătoare de venit, definite de Codul fiscal, și ale căror venituri sunt determinate în sistem real au obligația să conducă evidența contabilă pe baza regulilor contabilității în partidă simplă sau, la opțiunea acestora, pe baza regulilor contabilității în partidă dublă, potrivit reglementărilor contabile emise în acest sens, cu excepția situației în care în legislația fiscală se prevede altfel."
— Legea contabilității nr. 82/1991, art. 1 alin. (1) și alin. (5) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

- **SRL-ul are personalitate juridică proprie, distinctă de asociați**, cu patrimoniu separat și contabilitate în partidă dublă obligatorie — orice mișcare de bani a firmei trebuie să treacă prin conturile ei, nu prin conturile personale ale asociaților.
- **PFA-ul nu are personalitate juridică distinctă de persoana fizică titulară** și conduce, de regulă, contabilitate în partidă simplă — de aceea legea nu impune, în sursele verificate, un cont bancar separat obligatoriu; titularul poate opta pentru un cont dedicat activității din motive practice (trasabilitate, evidență mai clară), nu dintr-o obligație legală expresă găsită în aceste surse.
- **Consecința practică**: la SRL, amestecul fondurilor firmei cu cele personale ale asociaților ridică probleme de opozabilitate a patrimoniului social; la PFA, distincția e mai degrabă administrativă (mai ușor de urmărit veniturile activității), nu una impusă structural de personalitate juridică separată.

## Ce se greșește în practică

- Se presupune, fără verificare la sursă, că există o obligație legală explicită de cont bancar separat pentru PFA — afirmație pe care sursele disponibile nu o confirmă; ce impune legea e regimul contabil (partidă simplă/dublă), nu instrumentul bancar în sine.
- La SRL, se folosește contul bancar al firmei pentru cheltuieli personale ale asociatului, ceea ce nu încalcă direct legea contabilă, dar generează operațiuni greu de justificat ca fiind în interesul societății și poate ridica probleme la o inspecție fiscală.
- Se confundă absența unei obligații legale explicite cu absența oricărui risc practic — chiar și la PFA, amestecul fondurilor personale cu cele ale activității îngreunează serios ținerea evidenței în partidă simplă.

## Ce face iConta.eu

Modulele de bancă ale iConta.eu (`core/banca.py`, `core/banca_parser.py`) tratează la fel din punct de vedere tehnic orice cont bancar adăugat, indiferent dacă utilizatorul e SRL sau PFA — aplicația nu impune și nu verifică dacă titularul folosește un cont dedicat exclusiv activității economice; separarea rămâne o decizie și o disciplină a utilizatorului.

[iConta.eu](/)
