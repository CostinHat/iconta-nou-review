---
title: "Contabilitatea unui lanț de magazine: gestiune pe puncte de lucru"
description: Legea nu obligă un cost mediu separat pentru fiecare magazin dintr-un lanț - dar nici nu interzice ținerea unei evidențe cantitative distincte pe fiecare punct de lucru. De unde vine, concret, limita între ce oferă și ce nu oferă un sistem cu cost mediu unic.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Contabilitatea unui lanț de magazine: gestiune pe puncte de lucru

Un lanț de magazine ridică exact întrebarea pe care standardul o tratează explicit: are sens un cost mediu diferit pentru fiecare magazin, sau costul rămâne unul singur la nivelul firmei, cu evidența cantitativă separată pe fiecare punct de lucru?

## Temeiul legal

::: ghid-temei
„O diferență în localizarea geografică nu este suficientă pentru a justifica alegerea de metode diferite [de determinare a costului]."

— OMFP 1802/2014, Anexa 1 (Reglementări contabile), pct. 287 alin. (4)

„Contabilitatea stocurilor se ține cantitativ și valoric sau numai valoric prin folosirea inventarului permanent sau a inventarului intermitent."

— OMFP 1802/2014, Anexa 1 (Reglementări contabile), pct. 289
:::

Primul text răspunde direct: faptul că fiecare magazin al lanțului e la o adresă diferită nu justifică, de la sine, o metodă de cost diferită de la un magazin la altul. Al doilea text arată însă că evidența poate fi ținută cantitativ și valoric — deci nimic nu împiedică o firmă să urmărească separat, pe fiecare magazin, câtă marfă are, chiar dacă metoda de cost rămâne unică la nivelul întregii firme. Cele două lucruri — „câte gestiuni cu evidență cantitativă distinctă" și „câte costuri medii distincte" — nu trebuie confundate.

## Ce se greșește în practică

- Se cere sau se așteaptă un cost mediu ponderat separat pentru fiecare magazin din lanț, ca și cum ar fi entități complet independente — regula de la pct. 287 alin. (4) nu susține automat această așteptare; costul poate rămâne unic.
- Se ignoră evidența pe locație complet, tratând tot lanțul ca o singură gestiune, ceea ce face imposibilă cunoașterea stocului faptic real din fiecare magazin, la un moment dat.
- Se schimbă denumirea magazinelor inconsecvent în timp (redenumiri, renumerotări), fragmentând silențios istoricul de stoc al aceluiași punct de lucru în mai multe „locații" aparent distincte.

## Ce face iConta.eu

Pentru un lanț de magazine, iConta.eu oferă, la nivelul actual (Tier 1), evidența cantitativă descriptivă pe locație: stocul fiecărui articol poate fi urmărit separat pe fiecare magazin, iar mutările de marfă între magazine se fac prin funcția de transfer (F138) — ieșire dintr-un magazin, intrare în altul, fără notă contabilă. Costul mediu ponderat (CMP) rămâne însă **unul singur la nivelul întregii firme**, nu separat pe fiecare magazin — un transfer între magazine nu modifică deloc costul, doar mută cantitatea.

De precizat clar limita: dacă aveți nevoie de un cost mediu propriu fiecărui magazin (de exemplu pentru a compara marja reală magazin cu magazin, cu costuri de achiziție diferite pe fiecare gestiune), acest nivel de detaliu (gestiune cantitativ-valorică separată per depozit/magazin) e un pas mai avansat, momentan amânat în dezvoltarea aplicației — nu e disponibil ca funcționalitate completă în starea curentă. Ce e disponibil acum e eticheta de locație pe cantitate, cu un CMP global pentru toată firma.

[iConta.eu](/)
