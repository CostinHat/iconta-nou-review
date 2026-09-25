---
title: "De ce diferă D394 de jurnalul de cumpărări?"
description: "Regulile structurale prin care D394 exclude sau reformulează operațiuni față de un simplu jurnal de cumpărări — și de ce diferența e, de cele mai multe ori, normală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# De ce diferă D394 de jurnalul de cumpărări?

Un jurnal de cumpărări clasic înregistrează, în ordine cronologică, toate achizițiile firmei. D394 nu e o copie a acestui jurnal — e o selecție filtrată, cu reguli precise despre ce intră și ce nu, moștenite direct din textul ordinului ANAF.

## Temeiul legal

::: ghid-temei
„Persoanele impozabile stabilite în România trebuie să țină evidențe corecte și complete ale tuturor operațiunilor efectuate în desfășurarea activității lor economice."
— Codul fiscal, art. 321 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt:21609-21612)

„Nu se înscriu achiziţiile intracomunitare de bunuri şi servicii pentru care există obligativitatea înscrierii în declaraţia 390."
— OPANAF 2194/2025, Anexa 2 pct.1 lit.b) (sursă: anaf_surse/opanaf_2194_2025_d394.txt:741-742)
:::

Legea îți cere să ții evidențe complete ale operațiunilor (art.321) — dar D394, ca declarație, nu preia mecanic acea evidență, ci aplică filtre proprii:

- **Achizițiile intracomunitare lipsesc din D394** — se declară separat, în D390. Un jurnal de cumpărări care le include pe toate va avea, structural, mai multe rânduri decât D394.
- **Bonurile fiscale intră doar condiționat.** Un bon fiscal (de exemplu, de combustibil) e echivalat unei facturi simplificate și e raportabil în D394 doar dacă are înscris codul de înregistrare în scopuri de TVA al firmei cumpărătoare — un jurnal de cumpărări poate conține și bonuri fără această mențiune, care nu au corespondent în D394.
- **Documentele care nu sunt facturi valide** (proforme, avize de însoțire) nu intră niciodată în D394, chiar dacă apar în evidența internă a firmei.

## Ce se greșește în practică

- Se compară totalul jurnalului de cumpărări, linie cu linie, cu totalul din D394, fără să se scadă întâi achizițiile intracomunitare — care nu au ce căuta în D394.
- Se introduc în jurnal bonuri fiscale fără CUI-ul firmei și apoi se așteaptă ca acestea să apară automat în D394 — condiția legală a codului de înregistrare pe bon nu e opțională.
- Se ignoră faptul că o factură anulată sau stornată, deși poate apărea încă în jurnalul intern, nu ar trebui să mai apară în D394.

## Ce face iConta.eu

D394 se generează în iConta.eu direct din tabelele de facturi ale aplicației (`facturi` + `factura_linii`), cu filtre explicite în cod: sunt excluse documentele de tip proformă/aviz, precum și facturile anulate sau stornate (filtru adăugat explicit în `core/repo_d394.py`). Achizițiile intracomunitare sunt excluse programatic din generare, cu un comentariu explicit în cod care trimite la D390.

Aplicația nu are un „jurnal de cumpărări" ca document separat de registrul de facturi — orice diferență între o evidență ținută paralel (de exemplu, într-un tabel Excel) și D394 trebuie verificată pornind de la aceleași reguli de excludere de mai sus, nu tratată automat ca eroare de generare.

[iConta.eu](/)
